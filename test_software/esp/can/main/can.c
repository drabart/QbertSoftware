#include "can.h"
#include "esp_err.h"
#include "esp_twai.h"
#include "esp_twai_onchip.h"
#include "esp_twai_types.h"
#include "freertos/idf_additions.h"
#include "freertos/queue.h"
#include "hal/gpio_types.h"
#include "driver/gpio.h"
#include "portmacro.h"
#include "soc/gpio_num.h"
#include <stdio.h>
#include <string.h>

#define LED_PIN GPIO_NUM_2
#define RX_PIN GPIO_NUM_12
#define TX_PIN GPIO_NUM_13

#define NODE_ID 0b111111

QueueHandle_t queue;
typedef CanErr (*can_callback_t)(const twai_node_handle_t node_hdl, const twai_frame_t *frame);

CanErr setPosAxe(const twai_node_handle_t node_hdl, const twai_frame_t *frame) {
    if (frame->header.dlc != 4) return IncorrectBufLen;

    // ESP reads LE
    float pos = *(float*) frame->buffer;
    printf("pos = %f\n", pos);

    return None;
}

CanErr setGripState(const twai_node_handle_t node_hdl, const twai_frame_t *frame) {
    if (frame->header.dlc != 1) return IncorrectBufLen;

    uint8_t active = *frame->buffer;
    printf("active = %d\n", active);

    return None;
}

CanErr getPosAxe(const twai_node_handle_t node_hdl, const twai_frame_t *frame) {
    if (!frame->header.rtr) return NoRTR;

    // ESP sends LE
    float pos = 5051.334;
    uint8_t buf[4];

    *(float *)buf = pos;

    twai_frame_t rtr = *frame;
    rtr.header.rtr = 0;
    rtr.header.dlc = 4;
    rtr.buffer_len = 4;
    rtr.buffer = buf;

    ESP_ERROR_CHECK(twai_node_transmit(node_hdl, &rtr, 0));

    return None;
}

CanErr getGripState(const twai_node_handle_t node_hdl, const twai_frame_t *frame) {
    if (!frame->header.rtr) return NoRTR;

    uint8_t state = false;

    twai_frame_t rtr = *frame;
    rtr.header.rtr = 0;
    rtr.header.dlc = 1;
    rtr.buffer_len = 1;
    rtr.buffer = &state;

    ESP_ERROR_CHECK(twai_node_transmit(node_hdl, &rtr, 0));

    return None;
}

CanErr getError(const twai_node_handle_t node_hdl, const twai_frame_t *frame) {
    return None;
}

can_callback_t callbacks[NUM_CAN_CMD] = {
    NULL, // RESERVED
    NULL, // HEARTBEAT
    setPosAxe, // SET POS AXE
    setGripState, // SET GRIPPER STATE
    getPosAxe, // GET POS AXE
    getGripState, // GET GRIPPER STATE
    getError, // GET ERROR
    NULL, // GRIPPER DONE
};

void heartbeat(void* arg) {
    twai_node_handle_t node_hdl = arg;

    uint8_t buf = 0;
    twai_frame_t msg = {
        .header.id = (NODE_ID << 5) | HeartBeat,
        .header.dlc = 1,
        .buffer = &buf,
    };

    for(;;) {
        ESP_ERROR_CHECK(twai_node_transmit(node_hdl, &msg, 0));
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void can_dispatch_cb(void* arg) {
    twai_node_handle_t node_hdl = arg;
    twai_frame_t frame;

    for (;;) {
        if (xQueueReceive(queue, &frame, portMAX_DELAY) == pdTRUE) {
            uint8_t cmd = frame.header.id & CMD_MASK;
            printf("received CAN frame with cmd: %d\n", cmd);
            can_callback_t cb = callbacks[cmd];
            if (cb) {
                CanErr err = cb(node_hdl, &frame);
                printf("err: %d\n", err);
            }
        }
    }
}

static bool twai_rx(twai_node_handle_t handle, const twai_rx_done_event_data_t *edata, void *user_ctx) {
    uint8_t buf[8];
    twai_frame_t frame = {
        .buffer = buf,
        .buffer_len = 8,
    };

    if (ESP_OK == twai_node_receive_from_isr(handle, &frame)) {
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;

        if (frame.header.id >> 5 == NODE_ID) {
            xQueueSendFromISR(queue, &frame, &xHigherPriorityTaskWoken);
            return xHigherPriorityTaskWoken == pdTRUE;
        }
    }

    return false;
}

void app_main(void) {
    twai_node_handle_t node_hdl = NULL;
    twai_onchip_node_config_t node_config = {
        .io_cfg.tx = TX_PIN,
        .io_cfg.rx = RX_PIN,
        .bit_timing.bitrate = 250000,
        .tx_queue_depth = 4,
        .fail_retry_cnt = 3,
    };
    twai_event_callbacks_t user_cbs = {
        .on_rx_done = twai_rx,
    };
    ESP_ERROR_CHECK(twai_new_node_onchip(&node_config, &node_hdl));
    ESP_ERROR_CHECK(twai_node_register_event_callbacks(node_hdl, &user_cbs, NULL));

    queue = xQueueCreate(10, sizeof(twai_frame_t));

    gpio_reset_pin(LED_PIN);
    gpio_set_direction(LED_PIN, GPIO_MODE_OUTPUT);

    ESP_ERROR_CHECK(twai_node_enable(node_hdl));

    xTaskCreate(heartbeat, "heartbeat", 1<<12, node_hdl, 5, NULL);
    xTaskCreate(can_dispatch_cb, "CAN dispatch", 1<<12, node_hdl, 7, NULL);
}
