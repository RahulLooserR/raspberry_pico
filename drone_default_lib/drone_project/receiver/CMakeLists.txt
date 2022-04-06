add_executable(receiver
receiver.cpp)

target_link_libraries(receiver 
    PRIVATE 
      nrf24_driver 
      mpu6050_driver
      joystick
      pico_stdlib
)

pico_enable_stdio_usb(receiver 1)
pico_enable_stdio_uart(receiver 0)

# create map/bin/hex file etc.
pico_add_extra_outputs(receiver)