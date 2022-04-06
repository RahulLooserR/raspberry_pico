add_executable(transmitter
transmitter.cpp)

target_link_libraries(transmitter 
    PRIVATE 
      nrf24_driver 
      mpu6050_driver
      joystick
      pico_stdlib
)

pico_enable_stdio_usb(transmitter 1)
pico_enable_stdio_uart(transmitter 0)

# create map/bin/hex file etc.
pico_add_extra_outputs(transmitter)