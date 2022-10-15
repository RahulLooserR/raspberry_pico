
#include "utility.h"
#include "pins.h"
#include "receiver_util.h"

#include <tusb.h> // TinyUSB tud_cdc_connected()

// instantiate an object for the nRF24L01 transceiver
RF24 radio(CE_PIN, CSN_PIN);
control_data_t control_payload;
telemetry_data_t telemetry_payload;

int main()
{
  stdio_init_all(); // init necessary IO for the RP2040
  led_setup();
  telemetry_payload.latitude = 10.1;
  telemetry_payload.longitude = 20.1;

  MPU_6050 mpu(PICO_DEFAULT_I2C_SDA_PIN, PICO_DEFAULT_I2C_SCL_PIN, 400 * 1000);
  mpu.set_low_pass_filter(DLPF_CFG);
  mpu.set_sensitivity(GYRO_FS_SEL);
  mpu.calibrate();
  // wait here until the CDC ACM (serial port emulation) is connected
#ifdef SERIAL_COM
  while (!tud_cdc_connected())
  {
    sleep_ms(10);
  }
#endif

  while (!nrf_setup(false))
  { // if radio.begin() failed
    // hold program in infinite attempts to initialize radio
  }

  esc bldc_FL(10);
  esc bldc_FR(11);
  bldc_FL.set_frequency(50);
  bldc_FR.set_frequency(50);
  sleep_ms(2000);

  /* this is used to run the loop in specifc frequency
   * im considering 250 iterations per secreflist 
   */
  int counter = 0;
  absolute_time_t t1;
  absolute_time_t t2 = get_absolute_time();

  while (true)
  {
    t1 = get_absolute_time();
    send_data_rx();
    bldc_FL.set_level_ms(control_payload.throttle);
    bldc_FR.set_level_ms(control_payload.throttle);
    // printf("current milis: %u\n", control_payload.throttle);
    
    counter += 1;
    if(absolute_time_diff_us(t2, get_absolute_time()) >= 1000000) {
      printf("counter: %d\n", counter);
      printf("current milis: %u\n", control_payload.throttle);
      mpu.read_calibrated();
      mpu.print();
      t2 = get_absolute_time();
    }

    /* stricts loop to run 250 times / sec */
    while(absolute_time_diff_us(t1, get_absolute_time()) < 4000) {
    }
  }
  return 0; // we will never reach this
}