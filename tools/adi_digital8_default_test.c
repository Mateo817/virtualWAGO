/* Own-client check of the explicit DIGITAL8/MONOTONIC build defaults.
 * No original WAGO consumer, runtime, or hardware is executed.
 */
#include "adi_digital_adapter.h"
#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <time.h>
#include <libpackbus.h>

int main(void) {
  /* Deliberately never select a profile or clock through our extension API. */
  tApplicationDeviceInterface *adi = adi_GetApplicationInterface();
  assert(adi != NULL && adi->Init() == DAL_SUCCESS);
  uint32_t inputs = 0u, outputs = 0u;
  assert(adi->GetIoSizes(1, &inputs, &outputs) == DAL_SUCCESS);
  assert(inputs == 1u && outputs == 1u);
  assert(virtual_adi_advance_time_us(1u) == DAL_FAILURE);
  int32_t inner = -99;
  uint16_t identifier = 0u;
  assert(adi->CallDeviceSpecificFunction(LIBPACKBUS_DAL_FUNC_READ_TAB_9,
             &inner, 1, &identifier) == DAL_SUCCESS);
  assert(inner == 0 && identifier == 0x8801u);
  assert(adi->CallDeviceSpecificFunction(LIBPACKBUS_DAL_FUNC_READ_TAB_9,
             &inner, 2, &identifier) == DAL_SUCCESS);
  assert(inner == 0 && identifier == 0x8802u);
  assert(adi->OpenDevice(1) == DAL_SUCCESS);
  tCONFIGURE_DEVICE config = {0};
  config.eStructType = TCF_SSC_CONF_STRUCT_3;
  assert(adi->ConfigureDevice(1, &config) == DAL_SUCCESS);
  assert(virtual_adi_set_application_state(ApplicationState_Running) == DAL_SUCCESS);
  assert(virtual_adi_set_permit(true) == DAL_SUCCESS);
  assert(adi->WatchdogSetTime(1u, 10000u) == DAL_SUCCESS);
  assert(adi->WatchdogStart() == DAL_SUCCESS);
  assert(adi->WatchdogTrigger() == DAL_SUCCESS);
  uint8_t frame = 0xa5u;
  assert(adi->WriteStart(1, 0u) == DAL_SUCCESS);
  assert(adi->WriteBytes(1, 0u, 0u, 1u, &frame) == DAL_SUCCESS);
  assert(adi->WriteEnd(1, 0u) == DAL_SUCCESS);
  uint16_t requested = 0u, effective = 0u;
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0xa5u); /* no scheduler-dependent healthy-time assertion */
  struct timespec delay = {0, 30000000L};
  while (nanosleep(&delay, &delay) != 0) assert(errno == EINTR);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0xa5u && effective == 0u);
  assert(adi->CloseDevice(1) == DAL_SUCCESS);
  assert(adi->Exit() == DAL_SUCCESS);
  puts("ADI digital8 default model tests: PASS");
  return 0;
}
