#include "nrf24_driver.h"
#include "joystick.hpp"

#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "pico/binary_info.h"
#include "hardware/adc.h"
#include "hardware/spi.h"
#include <iostream>

const uint LED_PIN = 25;

int main()
{   
    stdio_init_all();

    spi_pin_config_t spi_pin_config = {
        .hspi = spi0,
        .sck = 2,
        .tx = 3,
        .rx = 4, 
        .csn = 5,
        .ce = 6
    };

    spi_config_t config;

    NRF24L01 nrf(&spi_pin_config);
    uint8_t data[5] = {0x11, 0x22, 0x33, 0x44, 0x55};

    sleep_ms(5000);
    nrf.print_reg_values();

    nrf.configure(&config);

    char my_data[32];

    nrf.open_reading_pipe(1, data, 5);

    nrf.start_listening();

    printf("\nValue after init");
    nrf.print_reg_values();
    while (true) {
        if(nrf.any()) {
            if(nrf.recv_msg(my_data)) {
                my_data[32] = '\n';
                printf("Message received: %s\n", my_data);
            }
        }
    }
    return 0;
}