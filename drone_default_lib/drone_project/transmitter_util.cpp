#include "transmitter_util.h"
#include "pins.h"
#include "pico/multicore.h"

#define THORTTLE_SPEED 2

/* function running on core 1
 * oled display
 */
void core1_function()
{
  using namespace pico_ssd1306;
  char buffer[50];
  /* oled pin setup */
  i2c_init(OLED_PORT, _1MHZ); // Use i2c port with baud rate of 1Mhz
  gpio_set_function(OLED_SDA_PIN, GPIO_FUNC_I2C);
  gpio_set_function(OLED_SCL_PIN, GPIO_FUNC_I2C);
  gpio_pull_up(OLED_SDA_PIN);
  gpio_pull_up(OLED_SCL_PIN);
  sleep_ms(250);

  SSD1306 display = SSD1306(OLED_PORT, SCREEN_ADDR, Size::W128xH64);

  // Here we rotate the display by 180 degrees, so that it's not upside down from my perspective
  // If your screen is upside down try setting it to 1 or 0
  display.setOrientation(1);
  display.setContrast(255);

  drawText(&display, font_5x8, "Test", 0, 0);
  display.sendBuffer();

  while (true)
  {
    if (multicore_fifo_rvalid())
    {
      uint32_t flag = multicore_fifo_pop_blocking();
      if (flag)
      {
        // display.clear();
        // sprintf(buffer, "lat: %f", telemetry_payload.latitude);
        // drawText(&display, font_8x8, buffer, 0, 0);
        // display.sendBuffer();

        // sprintf(buffer, "long: %f", telemetry_payload.longitude);
        // drawText(&display, font_8x8, buffer, 0, 18);
        // display.sendBuffer();

        // float ping_ms = ping / 1000.0f;
        // sprintf(buffer, "ping %.2fms", ping_ms);
        // drawText(&display, font_5x8, buffer, 60, 50);
        // display.sendBuffer();
        display.clear();
        sprintf(buffer, "throttle %d", control_payload.throttle);
        drawText(&display, font_5x8, buffer, 60, 50);
        display.sendBuffer();
      }
    }
  }
}

void send_data_tx()
{
  uint64_t end_timer;
  uint64_t start_timer = to_us_since_boot(get_absolute_time());         // start the timer
  bool report = radio.write(&control_payload, sizeof(control_payload)); // transmit & save the report
  multicore_fifo_push_blocking(1);
  if (report)
  {
    // transmission successful; wait for response and print results

    if (control_payload.send_ack)
    {
      radio.startListening();                                         // put in RX mode
      uint64_t start_timeout = to_ms_since_boot(get_absolute_time()); // timer to detect timeout
      while (!radio.available())
      { // wait for response
        if (to_ms_since_boot(get_absolute_time()) - start_timeout > 200)
        {
          printf("Timed out\n");
          break;
        } // only wait 200 ms
      }
      end_timer = to_us_since_boot(get_absolute_time()); // end the timer
      radio.stopListening();                                      // put back in TX mode
    }

    // print summary of transactions
    printf("Transmission successful!"); // payload was delivered
    uint8_t pipe;
    if (control_payload.send_ack)
    {
      if (radio.available(&pipe))
      { // is there a payload received
        // print details about outgoing payload
        ping = end_timer - start_timer;
        printf(" Round-trip delay: %llu us. Sent\n",
               ping);

        radio.read(&telemetry_payload, sizeof(telemetry_payload)); // get payload from RX FIFO
        // multicore_fifo_push_blocking(1);
        // print details about incoming payload
        printf(" Received %d bytes on pipe %d: %f %f\n",
               radio.getPayloadSize(),
               pipe,
               telemetry_payload.latitude,
               telemetry_payload.longitude);
      }
      else
      {
        printf(" Recieved no response.\n"); // no response received
      }
    }
  }
  else
  {
    printf("Transmission failed or timed out\n"); // payload was not delivered
  }                                               // report

  // to make this example readable in the serial terminal
  // sleep_ms(1000); // slow transmissions down by 1 second

} // loop

void pin_setup_tx()
{
  /* gp0 and gp1 is for throttle
   */
  gpio_init(UP_PIN);
  gpio_init(DOWN_PIN);
  gpio_set_dir(UP_PIN, GPIO_IN);
  gpio_set_dir(DOWN_PIN, GPIO_IN);

  /* setting adc input (26, 27, 28)
   * for pitch, roll and throttle
   * is set for yaw, clockwise and ccw
   */

  adc_init();
  // Make sure GPIO is high-impedance, no pullups etc
  adc_gpio_init(26);
  adc_gpio_init(27);
  adc_gpio_init(28);
}

void read_input(control_data_t *control_payload)
{
  int value_read;

  adc_select_input(0);

  value_read = adc_read();
  control_payload->roll = map(value_read, 0, 4060, -10, 10); // 4095 default range

  adc_select_input(1);
  value_read = adc_read();
  control_payload->pitch = map(value_read, 0, 4060, -10, 10);

  adc_select_input(2);
  value_read = adc_read();
  control_payload->yaw = map(value_read, 0, 4060, -1, 1);

  if (gpio_get(UP_PIN) > 0)
  {
    if (control_payload->throttle < MAX_THROTTLE)
      control_payload->throttle += THORTTLE_SPEED;
  }
  if (gpio_get(DOWN_PIN) > 0)
  {
    if (control_payload->throttle > MIN_THROTTLE)
      control_payload->throttle -= THORTTLE_SPEED;
  }

}

void print_input_value(const control_data_t *control_payload)
{
  printf("value of roll: %d \'c\n", control_payload->roll);
  printf("value of pitch: %d \'c\n", control_payload->pitch);
  printf("value of throttle: %d\n", control_payload->throttle);

  printf("Value of yaw: ");
  if (control_payload->yaw > 0)
  {
    printf("clockwise\n");
  }
  else if (control_payload->yaw == 0)
  {
    printf("No rotation\n");
  }
  else
  {
    printf("counter-clockwise\n");
  }

  printf("Value of send_ack: %s\n", (control_payload->send_ack > 0) ? "True" : "False");
}