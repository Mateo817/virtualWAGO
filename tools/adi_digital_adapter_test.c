/* Standalone contract harness for the own virtual model; no vendor code. */
#include "adi_digital_adapter.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <libpackbus.h>

static void test_enumeration(tApplicationDeviceInterface *adi) {
  tDeviceInfo entry = {0};
  size_t count = 0;
  assert(adi->GetDeviceList(0u, NULL, &count) == DAL_SUCCESS);
  assert(count == 1u);
  assert(adi->GetDeviceList(1u, NULL, &count) == DAL_FAILURE);
  assert(adi->GetDeviceList(1u, &entry, &count) == DAL_SUCCESS);
  assert(count == 1u && entry.DeviceId == 1);
  assert(strcmp(entry.DeviceName, "libpackbus") == 0);
  char name[16];
  size_t length = 0;
  assert(adi->GetDeviceName(entry.DeviceId, sizeof(name), name, &length) ==
         DAL_SUCCESS);
  assert(strcmp(name, "libpackbus") == 0 && length == strlen(name));
  uint32_t input_size = 0, output_size = 0;
  assert(adi->GetIoSizes(entry.DeviceId, &input_size, &output_size) ==
         DAL_SUCCESS);
  assert(input_size == 2u && output_size == 2u);
  assert(adi->OpenDevice(entry.DeviceId) == DAL_SUCCESS);
  assert(adi->OpenDevice(99) == DAL_FAILURE);
  tCONFIGURE_DEVICE config = {0};
  config.eStructType = TCF_SSC_CONF_STRUCT_3;
  config.uConfStru.rSSC_ConfStruct_III.ulTcmControl = 0x01000000u;
  assert(adi->ConfigureDevice(entry.DeviceId, &config) == DAL_FAILURE);
  config.uConfStru.rSSC_ConfStruct_III.ulTcmControl = 0u;
  assert(adi->ConfigureDevice(entry.DeviceId, &config) == DAL_SUCCESS);
}

static void test_terminal_metadata(tApplicationDeviceInterface *adi) {
  int32_t inner = -99;
  uint32_t count = 0;
  tKBUS_TERMINAL_INFO_32 records[2];
  memset(records, 0xa5, sizeof(records));
  assert(adi->CallDeviceSpecificFunction(
             LIBPACKBUS_DAL_FUNC_GET_TERMINAL_INFO_32, &inner, 0u, records,
             &count) == DAL_SUCCESS);
  assert(inner == 2 && count == 2u);
  assert(((uint8_t *)records)[0] == 0xa5); /* insufficient leaves buffer */
  assert(adi->CallDeviceSpecificFunction(
             LIBPACKBUS_DAL_FUNC_GET_TERMINAL_INFO_32, &inner,
             (uint32_t)sizeof(records), records, &count) == DAL_SUCCESS);
  assert(inner == 0 && count == 2u);
  assert(records[0].ulOffsetInput_bits == 0u &&
         records[0].ulSizeInput_bits == 16u &&
         records[0].ulSizeOutput_bits == 0u);
  assert(records[1].ulOffsetInput_bits == 16u &&
         records[1].ulSizeInput_bits == 0u &&
         records[1].ulOffsetOutput_bits == 0u &&
         records[1].ulSizeOutput_bits == 16u);
  memset(records, 0xa5, sizeof(records));
  assert(adi->CallDeviceSpecificFunction(
             LIBPACKBUS_DAL_FUNC_GET_TERMINAL_INFO_32, &inner, 31u, records,
             &count) == DAL_SUCCESS);
  assert(inner == 2 && count == 2u && ((uint8_t *)records)[0] == 0xa5u);
  count = 0u;
  assert(adi->CallDeviceSpecificFunction(
             LIBPACKBUS_DAL_FUNC_GET_TERMINAL_INFO_32, &inner, 32u, NULL,
             &count) == DAL_SUCCESS);
  assert(inner == 1 && count == 0u);
  uint8_t large[4004];
  memset(large, 0xa5, sizeof(large));
  assert(adi->CallDeviceSpecificFunction(
             LIBPACKBUS_DAL_FUNC_GET_TERMINAL_INFO_32, &inner, 4000u, large,
             &count) == DAL_SUCCESS);
  assert(inner == 0 && count == 2u);
  memcpy(records, large, sizeof(records));
  assert(records[0].ulSizeInput_bits == 16u);
  for (size_t i = 32u; i < 4000u; ++i) assert(large[i] == 0u);
  for (size_t i = 4000u; i < sizeof(large); ++i) assert(large[i] == 0xa5u);
  uint16_t id = 0;
  assert(adi->CallDeviceSpecificFunction(LIBPACKBUS_DAL_FUNC_READ_TAB_9, &inner,
                                         1, &id) == DAL_SUCCESS);
  assert(inner == 0 && id == 0x9001u);
  assert(adi->CallDeviceSpecificFunction(LIBPACKBUS_DAL_FUNC_READ_TAB_9, &inner,
                                         2, &id) == DAL_SUCCESS);
  assert(inner == 0 && id == 0x9002u);
  assert(adi->CallDeviceSpecificFunction("unknown", &inner) == DAL_NOTUSED);
  assert(adi->CallDeviceSpecificFunction(LIBPACKBUS_DAL_FUNC_GET_UID, &inner,
                                         1, &id) == DAL_SUCCESS);
  assert(inner == -1);
}

static void test_diagnosis(tApplicationDeviceInterface *adi, tDeviceId id) {
  uint8_t details[8];
  memset(details, 0xa5, sizeof(details));
  tBusState bus_state = BusState_BusFault;
  assert(adi->DiagnoseGetDeviceState(id, sizeof(details), details, &bus_state) ==
         DAL_SUCCESS);
  assert(bus_state == BusState_BusOk);
  for (size_t i = 0; i < sizeof(details); ++i) assert(details[i] == 0u);
  assert(adi->DiagnoseGetDeviceState(id, 0u, NULL, NULL) == DAL_FAILURE);
}

static void test_read_latch_and_bounds(tApplicationDeviceInterface *adi,
                                       tDeviceId id) {
  assert(virtual_adi_set_inputs(0xa55au) == DAL_SUCCESS);
  assert(adi->ReadStart(id, 0u) == DAL_SUCCESS);
  assert(virtual_adi_set_inputs(0x5aa5u) == DAL_SUCCESS);
  uint8_t bytes[2] = {0};
  assert(adi->ReadBytes(id, 0u, 0u, 2u, bytes) == DAL_SUCCESS);
  assert(bytes[0] == 0x5au && bytes[1] == 0xa5u);
  uint8_t bit = 9u;
  assert(adi->ReadBit(id, 0u, 0u, &bit) == DAL_SUCCESS && bit == 0u);
  assert(adi->ReadBytes(id, 0u, UINT32_MAX, 2u, bytes) == DAL_FAILURE);
  assert(adi->ReadBytes(id, 1u, 0u, 1u, bytes) == DAL_FAILURE);
  assert(adi->ReadEnd(id, 0u) == DAL_SUCCESS);
  assert(adi->ReadEnd(id, 0u) == DAL_FAILURE);
}

static void test_staged_outputs(tApplicationDeviceInterface *adi,
                                tDeviceId id) {
  uint16_t requested = 0xffffu, effective = 0xffffu;
  assert(virtual_adi_set_application_state(ApplicationState_Running) ==
         DAL_SUCCESS);
  assert(virtual_adi_set_permit(true) == DAL_SUCCESS);
  assert(adi->WatchdogSetTime(1u, 100u) == DAL_SUCCESS);
  assert(adi->WatchdogStart() == DAL_SUCCESS);
  assert(adi->WatchdogTrigger() == DAL_SUCCESS);
  assert(adi->WriteStart(id, 0u) == DAL_SUCCESS);
  uint8_t frame[2] = {0x34u, 0x12u};
  assert(adi->WriteBytes(id, 0u, 0u, 2u, frame) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0u && effective == 0u); /* no partial publication */
  assert(adi->WriteEnd(id, 0u) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x1234u && effective == 0x1234u);

  /* A rejected transfer poisons the transaction and leaves the last frame. */
  assert(adi->WriteStart(id, 0u) == DAL_SUCCESS);
  uint8_t partial = 0xffu;
  assert(adi->WriteBytes(id, 0u, 0u, 1u, &partial) == DAL_SUCCESS);
  assert(adi->WriteBytes(id, 0u, UINT32_MAX, 1u, &partial) == DAL_FAILURE);
  assert(adi->WriteEnd(id, 0u) == DAL_FAILURE);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x1234u && effective == 0x1234u);

  /* Gate loss during a complete staged frame poisons it, even after trigger. */
  assert(adi->WriteStart(id, 0u) == DAL_SUCCESS);
  uint8_t candidate[2] = {0x78u, 0x56u};
  assert(adi->WriteBytes(id, 0u, 0u, 2u, candidate) == DAL_SUCCESS);
  assert(virtual_adi_advance_time_us(99u) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(effective == 0x1234u);
  assert(virtual_adi_advance_time_us(1u) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x1234u && effective == 0u);
  assert(adi->WatchdogTrigger() == DAL_SUCCESS);
  assert(adi->WriteEnd(id, 0u) == DAL_FAILURE);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(effective == 0u);
  assert(adi->WriteStart(id, 0u) == DAL_SUCCESS);
  assert(adi->WriteEnd(id, 0u) == DAL_FAILURE); /* no empty-frame publish */

  /* ADI state stop/start poisons the current frame through the real slot. */
  assert(adi->WriteStart(id, 0u) == DAL_SUCCESS);
  uint8_t state_candidate[2] = {0x78u, 0x56u};
  assert(adi->WriteBytes(id, 0u, 0u, 2u, state_candidate) == DAL_SUCCESS);
  tApplicationStateChangedEvent stopped = {ApplicationState_Stopped};
  tApplicationStateChangedEvent running = {ApplicationState_Running};
  assert(adi->ApplicationStateChanged(stopped) == DAL_SUCCESS);
  assert(adi->ApplicationStateChanged(running) == DAL_SUCCESS);
  assert(adi->WriteEnd(id, 0u) == DAL_FAILURE);

  /* Permit loss and restoration cannot make a staged frame eligible again. */
  assert(adi->WriteStart(id, 0u) == DAL_SUCCESS);
  assert(adi->WriteBytes(id, 0u, 0u, 2u, state_candidate) == DAL_SUCCESS);
  assert(virtual_adi_set_permit(false) == DAL_SUCCESS);
  assert(virtual_adi_set_permit(true) == DAL_SUCCESS);
  assert(adi->WriteEnd(id, 0u) == DAL_FAILURE);

  assert(adi->WriteStart(id, 0u) == DAL_SUCCESS);
  uint8_t full_frame[2] = {0x34u, 0x12u};
  assert(adi->WriteBytes(id, 0u, 0u, 2u, full_frame) == DAL_SUCCESS);
  assert(adi->WriteEnd(id, 0u) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(effective == 0x1234u);

  assert(adi->WriteStart(id, 0u) == DAL_SUCCESS);
  assert(adi->WriteBytes(id, 0u, 0u, 2u, full_frame) == DAL_SUCCESS);
  uint8_t bit = 1u;
  assert(adi->WriteBit(id, 0u, 15u, &bit) == DAL_SUCCESS);
  assert(adi->WriteEnd(id, 0u) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x9234u && effective == 0x9234u);
  assert(virtual_adi_set_permit(false) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x9234u && effective == 0u);
}

int main(void) {
  virtual_adi_reset();
  tApplicationDeviceInterface *adi = adi_GetApplicationInterface();
  assert(adi != NULL);
  assert(adi->Init() == DAL_SUCCESS);
  assert(adi->ScanDevices() == DAL_SUCCESS);
  test_enumeration(adi);
  test_terminal_metadata(adi);
  test_diagnosis(adi, 1);
  test_read_latch_and_bounds(adi, 1);
  test_staged_outputs(adi, 1);
  assert(adi->CloseDevice(1) == DAL_SUCCESS);
  assert(adi->OpenDevice(1) == DAL_SUCCESS);
  tCONFIGURE_DEVICE config = {0};
  config.eStructType = TCF_SSC_CONF_STRUCT_3;
  assert(adi->ConfigureDevice(1, &config) == DAL_SUCCESS);
  assert(adi->WriteStart(1, 0u) == DAL_SUCCESS);
  uint8_t nonzero_frame[2] = {0xcdu, 0xabu};
  assert(adi->WriteBytes(1, 0u, 0u, 2u, nonzero_frame) == DAL_SUCCESS);
  assert(adi->WriteEnd(1, 0u) == DAL_SUCCESS);
  uint16_t requested = 1u, effective = 1u;
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0xabcdU && effective == 0u);
  assert(adi->CloseDevice(1) == DAL_SUCCESS);
  assert(adi->Exit() == DAL_SUCCESS);
  puts("ADI digital model contract tests: PASS");
  return 0;
}
