/* Own-client check of the default DIGITAL16/MONOTONIC model build.
 * This exercises our in-memory ADI client contract, not an original WAGO
 * consumer, runtime, or hardware.
 */
#include "adi_digital_adapter.h"

#include <assert.h>
#include <stdio.h>
#include <libpackbus.h>

int main(void) {
  /* Deliberately do not select the profile or clock through the extension API. */
  tApplicationDeviceInterface *adi = adi_GetApplicationInterface();
  assert(adi != NULL && adi->Init() == DAL_SUCCESS);

  uint32_t input_size = 0u, output_size = 0u;
  assert(adi->GetIoSizes(1, &input_size, &output_size) == DAL_SUCCESS);
  assert(input_size == 2u && output_size == 2u);

  int32_t inner = -99;
  uint16_t identifier = 0u;
  assert(adi->CallDeviceSpecificFunction(LIBPACKBUS_DAL_FUNC_READ_TAB_9,
                                         &inner, 1, &identifier) == DAL_SUCCESS);
  assert(inner == 0 && identifier == 0x9001u);
  assert(adi->CallDeviceSpecificFunction(LIBPACKBUS_DAL_FUNC_READ_TAB_9,
                                         &inner, 2, &identifier) == DAL_SUCCESS);
  assert(inner == 0 && identifier == 0x9002u);

  assert(adi->OpenDevice(1) == DAL_SUCCESS);
  tCONFIGURE_DEVICE config = {0};
  config.eStructType = TCF_SSC_CONF_STRUCT_3;
  assert(adi->ConfigureDevice(1, &config) == DAL_SUCCESS);

  assert(virtual_adi_set_inputs(0xa596u) == DAL_SUCCESS);
  assert(adi->ReadStart(1, 0u) == DAL_SUCCESS);
  uint8_t input_frame[2] = {0u, 0u};
  assert(adi->ReadBytes(1, 0u, 0u, 2u, input_frame) == DAL_SUCCESS);
  assert(input_frame[0] == 0x96u && input_frame[1] == 0xa5u);
  assert(adi->ReadEnd(1, 0u) == DAL_SUCCESS);

  assert(virtual_adi_set_application_state(ApplicationState_Running) ==
         DAL_SUCCESS);
  assert(virtual_adi_set_permit(false) == DAL_SUCCESS);
  /* Longer than the bounded 15s runner so the immediate gate check does not
   * depend on scheduler latency. This is an own-client test setting. */
  assert(adi->WatchdogSetTime(1u, 60000000u) == DAL_SUCCESS);
  assert(adi->WatchdogStart() == DAL_SUCCESS);
  assert(adi->WatchdogTrigger() == DAL_SUCCESS);

  uint8_t output_frame[2] = {0x69u, 0x5au};
  uint16_t requested = 0u, effective = 0xffffu;
  assert(adi->WriteStart(1, 0u) == DAL_SUCCESS);
  assert(adi->WriteBytes(1, 0u, 0u, 2u, output_frame) == DAL_SUCCESS);
  assert(adi->WriteEnd(1, 0u) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x5a69u && effective == 0u);

  assert(virtual_adi_set_permit(true) == DAL_SUCCESS);
  assert(adi->WatchdogTrigger() == DAL_SUCCESS);
  assert(adi->WriteStart(1, 0u) == DAL_SUCCESS);
  assert(adi->WriteBytes(1, 0u, 0u, 2u, output_frame) == DAL_SUCCESS);
  assert(adi->WriteEnd(1, 0u) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x5a69u && effective == 0x5a69u);

  assert(virtual_adi_set_permit(false) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x5a69u && effective == 0u);

  /* The default clock is MONOTONIC; only the explicit logical mode advances. */
  assert(virtual_adi_advance_time_us(1u) == DAL_FAILURE);

  assert(adi->CloseDevice(1) == DAL_SUCCESS);
  assert(adi->Exit() == DAL_SUCCESS);
  puts("ADI digital16 default model tests: PASS");
  return 0;
}
