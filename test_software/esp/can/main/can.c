#include "can.h"

#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali_scheme.h"
#include "esp_err.h"
#include "esp_twai.h"
#include "esp_twai_onchip.h"
#include "esp_twai_types.h"
#include "esp_err.h"

#include "freertos/idf_additions.h"
#include "freertos/projdefs.h"
#include "freertos/queue.h"

#include "portmacro.h"

#include "soc/gpio_num.h"

#include "driver/gpio.h"

#include <stdio.h>
#include <string.h>
#include <inttypes.h>

// DEFINES

#define LED_PIN                 GPIO_NUM_2

#define CAN_RX_PIN              GPIO_NUM_12
#define CAN_TX_PIN              GPIO_NUM_13

#define AXE_0_IN_PIN            GPIO_NUM_32
#define AXE_0_ADC_CHAN          ADC_CHANNEL_4
#define AXE_1_IN_PIN            GPIO_NUM_33
#define AXE_1_ADC_CHAN          ADC_CHANNEL_5

#define AXE_0_EXTEND_PIN        GPIO_NUM_16
#define AXE_0_RETRACT_PIN       GPIO_NUM_17
#define AXE_1_EXTEND_PIN        GPIO_NUM_18
#define AXE_1_RETRACT_PIN       GPIO_NUM_19
#define GRIPPERS_EXTEND_PIN     GPIO_NUM_22
#define GRIPPERS_RETRACT_PIN    GPIO_NUM_23

#define NODE_ID                 0b111111
#define ADC_BITWIDTH            ADC_BITWIDTH_12

#define MIN(a, b)               (a) < (b) ? (a) : (b)
#define MAX(a, b)               (a) > (b) ? (a) : (b)
#define BETWEEN(mid, min, max)  ((mid) > (min) && (mid) < (max))

// DEFINES
//
// TYPEDEFS

typedef CanErr (*can_callback_t)(const twai_frame_t *frame);
typedef struct {
    adc_channel_t chan;
    uint16_t samples;
    QueueHandle_t reply;
} adc_req_t;

// TYPEDEFS
//
// GLOBAL_VARS

static QueueHandle_t can_queue;
static QueueHandle_t adc_queue;
static QueueHandle_t pos_queue;

static twai_node_handle_t node_hdl;

static adc_oneshot_unit_handle_t adc1_unit_handle;
static adc_cali_handle_t adc1_cali_handle;

// GLOBAL_VARS
// 
// HELPER_FUNCTIONS

void print_twai_frame(const twai_frame_t *frame) {
    const twai_frame_header_t *h = &frame->header;

    printf("TWAI Frame:\n");
    printf("  ID: 0x%" PRIu32 "\n", h->id);
    printf("  DLC: %" PRIu16 "\n", h->dlc);
    printf("  Flags:\n");
    printf("    IDE: %d\n", h->ide);
    printf("    RTR: %d\n", h->rtr);
    printf("    FDF: %d\n", h->fdf);
    printf("    BRS: %d\n", h->brs);
    printf("    ESI: %d\n", h->esi);
    printf("  Timestamp / Trigger Time: %" PRIu64 "\n", h->timestamp);

    printf("  Data (%zu bytes):", h->dlc);
    for (size_t i = 0; i < h->dlc; i++) {
        if (i % 16 == 0) printf("\n    ");
        printf("%02X ", frame->buffer[i]);
    }
    printf("\n");
}

float mV_to_mm(float mV) {
    // standard: range from 1V-10V, 1V = 0mm and 10V = 100mm -> 90 mV/mm
    // adjusted: range from 230-2360 mV -> ~21.3 mV/mm
    return ((mV - 230) / 21.3);
}

float read_adc_q(QueueHandle_t reply, adc_channel_t chan, uint16_t samples) {
    adc_req_t req = { .chan = chan, .samples = samples, .reply = reply };

    xQueueSend(adc_queue, &req, portMAX_DELAY);

    float val;
    xQueueReceive(reply, &val, portMAX_DELAY);

    return val;
}

float read_adc(adc_channel_t chan, uint16_t samples) {
    QueueHandle_t reply = xQueueCreate(1, sizeof(float));
    return read_adc_q(reply, chan, samples);
}

// HELPER_FUNCTIONS
//
// CAN_CALLBACKS

CanErr setPosAxe(const twai_frame_t *frame) {
    if (frame->header.dlc != 4) return IncorrectDLC;

    float pos = *(float*) frame->buffer;
    xQueueSend(pos_queue, &pos, portMAX_DELAY);

    return OK;
}

CanErr setGripState(const twai_frame_t *frame) {
    if (frame->header.dlc != 1) return IncorrectDLC;

    bool active = *frame->buffer;
    gpio_set_level(!active ? GRIPPERS_EXTEND_PIN : GRIPPERS_RETRACT_PIN, 0);
    gpio_set_level(active ? GRIPPERS_EXTEND_PIN : GRIPPERS_RETRACT_PIN, 1);

    return OK;
}

CanErr getPosAxe(const twai_frame_t *frame) {
    if (!frame->header.rtr) return NoRTR;

    float mV_0 = read_adc(AXE_0_ADC_CHAN, 48);
    float pos_0 = mV_to_mm(mV_0);

    float mV_1 = read_adc(AXE_1_ADC_CHAN, 48);
    float pos_1 = mV_to_mm(mV_1);

    uint8_t buf[8];

    ((float *)buf)[0] = pos_0;
    ((float *)buf)[1] = pos_1;

    twai_frame_t rtr = *frame;
    rtr.header.rtr = 0;
    rtr.header.dlc = 8;
    rtr.buffer_len = 8;
    rtr.buffer = buf;

    if (twai_node_transmit(node_hdl, &rtr, 0) < 0) {
        return UnknownErr;
    };

    return OK;
}

CanErr getGripState(const twai_frame_t *frame) {
    if (!frame->header.rtr) return NoRTR;

    bool extend = gpio_get_level(GRIPPERS_EXTEND_PIN);
    bool retract = gpio_get_level(GRIPPERS_EXTEND_PIN);
    uint8_t state = extend ? 1 : retract ? -1 : 0;

    twai_frame_t rtr = *frame;
    rtr.header.rtr = 0;
    rtr.header.dlc = 1;
    rtr.buffer_len = 1;
    rtr.buffer = &state;

    ESP_ERROR_CHECK(twai_node_transmit(node_hdl, &rtr, 0));

    return OK;
}

// CAN_CALLBACKS
//
// ADC_LOOP

void adc_loop(void* arg) {
    adc_req_t req;
    int raw, cali_mV;
    float acc, val;

    for (;;) {
        if (!xQueueReceive(adc_queue, &req, portMAX_DELAY)) { continue; }

        acc = 0;
        for (uint16_t i = 0; i < req.samples; i++) {
            adc_oneshot_read(adc1_unit_handle, req.chan, &raw);
            adc_cali_raw_to_voltage(adc1_cali_handle, acc/req.samples, &cali_mV);
            acc += cali_mV;
        }
        val = acc / req.samples;

        xQueueSend(req.reply, &val, 0);
    }
}

// ADC_LOOP
//
// CAN_LOOP

static bool twai_rx(twai_node_handle_t handle, const twai_rx_done_event_data_t *edata, void *user_ctx) {
    twai_frame_t *frame = calloc(1, sizeof(twai_frame_t));
    frame->buffer = calloc(8, 1);
    frame->buffer_len = 8;

    if (ESP_OK == twai_node_receive_from_isr(handle, frame)) {
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;

        if (frame->header.id >> 5 == NODE_ID) {
            xQueueSendFromISR(can_queue, &frame, &xHigherPriorityTaskWoken);
            return xHigherPriorityTaskWoken == pdTRUE;
        }
    }

    return false;
}

can_callback_t callbacks[NUM_CAN_CMD] = {
    NULL,               // RESERVED
    NULL,               // HEARTBEAT
    setPosAxe,          // SET POS AXE
    setGripState,       // SET GRIPPER STATE
    getPosAxe,          // GET POS AXE
    getGripState,       // GET GRIPPER STATE
    NULL,               // GRIPPER DONE
};

void can_dispatch_cb(void* arg) {
    twai_frame_t *frame;

    for (;;) {
        if (xQueueReceive(can_queue, &frame, portMAX_DELAY) == pdTRUE) {
            CanCmd cmd = frame->header.id & CMD_MASK;
            if (cmd > NUM_CAN_CMD) goto cleanup;

            can_callback_t cb = callbacks[cmd];
            if (cb) {
                CanErr err = cb(frame);
                if (err) {
                    fprintf(stderr, "ERROR: %d\b", err);
                }
            }

            cleanup:
            free(frame->buffer);
            free(frame);
        }
        vTaskDelay(1);
    }
}

void heartbeat(void* arg) {
    // TODO: encode error message into buf
    uint8_t buf = 0;

    twai_frame_t msg = {
        .header.id = (NODE_ID << 5) | HeartBeat,
        .header.dlc = 1,
        .buffer = &buf,
    };

    for(;;) {
        ESP_ERROR_CHECK(twai_node_transmit(node_hdl, &msg, 0));
        vTaskDelay(10);
    }
}

// CAN_LOOP
//
// POSITION_LOOP

/*void position_single(QueueHandle_t replies, adc_channel_t chan, float pos) {*/
/*    for (;;) {*/
/*        if (!xQueueIsQueueEmptyFromISR(pos_queue)) return;*/
/*        if (BETWEEN(mV_to_mm(read_adc_q(replies, chan, 48)), pos-1, pos+1)) return;*/
/*        vTaskDelay(1);*/
/*    }*/
/*}*/

void position(void* arg) {
    float pos;
    QueueHandle_t replies = xQueueCreate(1, sizeof(float));

    for (;;) {
        // wait for new pos and grab newest
        while (xQueueIsQueueEmptyFromISR(pos_queue)) { vTaskDelay(1); }
        while (xQueueReceive(pos_queue, &pos, 0) == pdTRUE) { }

        float pos_0 = mV_to_mm(read_adc_q(replies, AXE_0_ADC_CHAN, 48));
        float pos_1 = mV_to_mm(read_adc_q(replies, AXE_1_ADC_CHAN, 48));

        if (BETWEEN(pos_0, pos-0.5, pos+0.5) && BETWEEN(pos_1, pos-0.5, pos+0.5)) continue;

        int axe_0_pin = pos_0 - pos > 0 ? AXE_0_RETRACT_PIN : AXE_0_EXTEND_PIN;
        int axe_1_pin = pos_1 - pos > 0 ? AXE_1_RETRACT_PIN : AXE_1_EXTEND_PIN;

        gpio_set_level(axe_0_pin, 1);
        gpio_set_level(axe_1_pin, 1);
        for (;;) {
            // new position needed
            if (!xQueueIsQueueEmptyFromISR(pos_queue)) {
                gpio_set_level(axe_0_pin, 0);
                gpio_set_level(axe_1_pin, 0);
                break;
            }

            // axe 0 reached position
            if (BETWEEN(mV_to_mm(read_adc_q(replies, AXE_0_ADC_CHAN, 48)), pos-1, pos+1)) {
                gpio_set_level(axe_0_pin, 0);
                /*position_single(replies, AXE_1_ADC_CHAN, pos);*/
                gpio_set_level(axe_1_pin, 0);
                xQueueSend(pos_queue, &pos, 0);
                break;
            }

            // axe 1 reached position
            if (BETWEEN(mV_to_mm(read_adc_q(replies, AXE_1_ADC_CHAN, 48)), pos-1, pos+1)) {
                gpio_set_level(axe_1_pin, 0);
                /*position_single(replies, AXE_0_ADC_CHAN, pos);*/
                gpio_set_level(axe_0_pin, 0);
                xQueueSend(pos_queue, &pos, 0);
                break;
            }

            vTaskDelay(1);
        }
    }
}

// POSITION_LOOP
//
// SETUP

void setup_can() {
    twai_onchip_node_config_t node_config = {
        .io_cfg.tx = CAN_TX_PIN,
        .io_cfg.rx = CAN_RX_PIN,
        .bit_timing.bitrate = 250000,
        .tx_queue_depth = 4,
        .fail_retry_cnt = 3,
    };
    twai_event_callbacks_t user_cbs = {
        .on_rx_done = twai_rx,
    };
    ESP_ERROR_CHECK(twai_new_node_onchip(&node_config, &node_hdl));
    ESP_ERROR_CHECK(twai_node_register_event_callbacks(node_hdl, &user_cbs, NULL));

    can_queue = xQueueCreate(10, sizeof(twai_frame_t *));
    ESP_ERROR_CHECK(twai_node_enable(node_hdl));
}

void setup_adc() {
    // setup oneshot ADC unit
    adc_oneshot_unit_init_cfg_t adc_unit_cfg = {
        .unit_id = ADC_UNIT_1,
        .ulp_mode = ADC_ULP_MODE_DISABLE,
    };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&adc_unit_cfg, &adc1_unit_handle));

    // setup oneshot ADC channel
    adc_oneshot_chan_cfg_t adc_chan_cfg = {
        .atten = ADC_ATTEN_DB_12,
        .bitwidth = ADC_BITWIDTH,
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1_unit_handle, AXE_0_ADC_CHAN, &adc_chan_cfg));
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1_unit_handle, AXE_1_ADC_CHAN, &adc_chan_cfg));

    // setup adc calibration
    adc_cali_line_fitting_config_t adc_cal_config = {
        .unit_id = ADC_UNIT_1,
        .bitwidth = ADC_BITWIDTH,
        .atten = ADC_ATTEN_DB_12,
        .default_vref = 0,
    };
    ESP_ERROR_CHECK(adc_cali_create_scheme_line_fitting(&adc_cal_config, &adc1_cali_handle));

    adc_queue = xQueueCreate(8, sizeof(adc_req_t));
}

void setup_pins() {
    gpio_reset_pin(AXE_0_EXTEND_PIN);
    gpio_set_direction(AXE_0_EXTEND_PIN, GPIO_MODE_OUTPUT);
    gpio_set_level(AXE_0_EXTEND_PIN, 0);

    gpio_reset_pin(AXE_0_RETRACT_PIN);
    gpio_set_direction(AXE_0_RETRACT_PIN, GPIO_MODE_OUTPUT);
    gpio_set_level(AXE_0_RETRACT_PIN, 0);

    gpio_reset_pin(AXE_1_EXTEND_PIN);
    gpio_set_direction(AXE_1_EXTEND_PIN, GPIO_MODE_OUTPUT);
    gpio_set_level(AXE_1_EXTEND_PIN, 0);
    
    gpio_reset_pin(AXE_1_RETRACT_PIN);
    gpio_set_direction(AXE_1_RETRACT_PIN, GPIO_MODE_OUTPUT);
    gpio_set_level(AXE_1_RETRACT_PIN, 0);

    gpio_reset_pin(GRIPPERS_EXTEND_PIN);
    gpio_set_direction(GRIPPERS_EXTEND_PIN, GPIO_MODE_OUTPUT);
    gpio_set_level(GRIPPERS_EXTEND_PIN, 0);

    gpio_reset_pin(GRIPPERS_RETRACT_PIN);
    gpio_set_direction(GRIPPERS_RETRACT_PIN, GPIO_MODE_OUTPUT);
    gpio_set_level(GRIPPERS_RETRACT_PIN, 0);
}

// SETUP
//
// MAIN

void app_main(void) {
    setup_can();
    setup_adc();
    setup_pins();
    pos_queue = xQueueCreate(4, sizeof(float));

    xTaskCreate(adc_loop, "ADC reader", 2048, NULL, 8, NULL);
    xTaskCreate(position, "axe position loop", 2048, NULL, 7, NULL);
    xTaskCreate(can_dispatch_cb, "CAN dispatch", 2048, NULL, 6, NULL);
    xTaskCreate(heartbeat, "heartbeat", 1028, NULL, 5, NULL);
}

// MAIN
