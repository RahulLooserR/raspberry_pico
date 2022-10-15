#include "receiver_util.h"
#include "utility.h"

/* function for drone stablization
 * this will run on core 1 of pico
 */
void receiver_core1()
{
}

void send_data_rx()
{
  uint8_t pipe;
  bool report = false;

  if (radio.available(&pipe))
  {                                                        // is there a payload? get the pipe number that recieved it
    radio.read(&control_payload, sizeof(control_payload)); // get incoming payload

    if (control_payload.send_ack)
    {
      // transmit response & save result to `report`
      radio.stopListening();                                          // put in TX mode
      radio.writeFast(&telemetry_payload, sizeof(telemetry_payload)); // load response to TX FIFO
      report = radio.txStandBy(300);                             // keep retrying for 150 ms
      radio.startListening();                                         // put back in RX mode
    }

    // print summary of transactions, starting with details about incoming payload
    // printf("Received %d bytes on pipe %d:\n pitch: %d, roll: %d, throttle:%d, yaw: %d, is_ack: %d\n",
    //        radio.getPayloadSize(),
    //        pipe,
    //        control_payload.pitch, control_payload.roll, control_payload.throttle,
    //        control_payload.yaw, control_payload.send_ack);

    if (report)
    {
      // print outgoing payload and its counter
      // printf(" Sent: %f %f\n", telemetry_payload.latitude, telemetry_payload.longitude);
      telemetry_payload.latitude += 1.5;
      telemetry_payload.longitude += 2.5;
    }
    else if (!control_payload.send_ack)
    {
      // printf(" Response failed.\n"); // failed to send response
    }
  }
} // loop