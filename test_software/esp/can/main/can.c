#include "esp_err.h"
#include "esp_twai.h"
#include "esp_twai_onchip.h"
#include "esp_twai_types.h"
#include "freertos/idf_additions.h"
#include "hal/gpio_types.h"
#include "soc/gpio_num.h"
#include "driver/gpio.h"
#include <stdio.h>

#define LED_PIN GPIO_NUM_2
#define RX_PIN GPIO_NUM_12
#define TX_PIN GPIO_NUM_13

#define NODE_ID 0b111111

#define CMD_MASK 0b11111
#define CMD_HB 1
#define CMD_LED 2

typedef void (*can_cb)(uint8_t* buf, size_t buf_len);

void can_led(uint8_t* buf, size_t buf_len) {
    static int led_state = 0;
    led_state = !led_state;
    gpio_set_level(LED_PIN, led_state);
}

void heartbeat(void* arg) {
    uint8_t buf[8] = {0};
    twai_frame_t msg = {
        .header.id = (NODE_ID << 5) | CMD_HB,
        .header.dlc = 1,
        .buffer = buf,
    };

    for(;;) {
        ESP_ERROR_CHECK(twai_node_transmit(arg, &msg, 0));
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

can_cb can_callbacks[3] = {
    NULL,
    NULL,
    can_led,
};
static bool twai_rx(twai_node_handle_t handle, const twai_rx_done_event_data_t *edata, void *user_ctx) {
    uint8_t buf[8];
    twai_frame_t frame = {
        .buffer = buf,
        .buffer_len = 8,
    };
    if (ESP_OK == twai_node_receive_from_isr(handle, &frame)) {
        if (frame.header.id >> 5 == NODE_ID) {
            can_cb cb = can_callbacks[frame.header.id & CMD_MASK];
            if (cb != NULL) cb(frame.buffer, frame.buffer_len);
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

    gpio_reset_pin(LED_PIN);
    gpio_set_direction(LED_PIN, GPIO_MODE_OUTPUT);

    ESP_ERROR_CHECK(twai_node_enable(node_hdl));

    xTaskCreate(heartbeat, "heartbeat", 1<<12, node_hdl, 5, NULL);
}
