/* Standalone contract harness for the own virtual model; no vendor code. */
#include "adi_digital_adapter.h"

#include <assert.h>
#include <pthread.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <libpackbus.h>

typedef struct {
  tApplicationDeviceInterface *adi;
  tDeviceId device_id;
  uint8_t *data;
  int32_t result;
} cross_thread_call;

/* Own variadic wrapper exercising the genuine slot-29 va_list signature.
 * This does not execute or emulate the original IoDrvDal wrapper.
 */
static int32_t call_through_vcall(tApplicationDeviceInterface *adi,
                                 const char *name, void *return_value, ...) {
  va_list arguments;
  va_start(arguments, return_value);
  int32_t result = adi->VCallDeviceSpecificFunction(name, return_value,
                                                    arguments);
  va_end(arguments);
  return result;
}

static void *cross_thread_write(void *argument) {
  cross_thread_call *call = (cross_thread_call *)argument;
  call->result = call->adi->WriteBytes(call->device_id, 0u, 0u, 1u,
                                       call->data);
  return NULL;
}

static void *cross_thread_watchdog_trigger(void *argument) {
  cross_thread_call *call = (cross_thread_call *)argument;
  call->result = call->adi->WatchdogTrigger();
  return NULL;
}

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
  uint16_t requested = 1u, effective = 1u;
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0u && effective == 0u);
  tCONFIGURE_DEVICE config = {0};
  config.eStructType = TCF_SSC_CONF_STRUCT_3;
  assert(adi->ConfigureDevice(id, &config) == DAL_SUCCESS); /* model recovery */
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

  /* A rejected transfer preserves requested data and latches effective off. */
  assert(adi->WriteStart(id, 0u) == DAL_SUCCESS);
  uint8_t partial = 0xffu;
  assert(adi->WriteBytes(id, 0u, 0u, 1u, &partial) == DAL_SUCCESS);
  assert(adi->WriteBytes(id, 0u, UINT32_MAX, 1u, &partial) == DAL_FAILURE);
  assert(adi->WriteEnd(id, 0u) == DAL_FAILURE);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x1234u && effective == 0u);

  uint8_t recovered_frame[2] = {0x34u, 0x12u};
  tCONFIGURE_DEVICE recovery_config = {0};
  recovery_config.eStructType = TCF_SSC_CONF_STRUCT_3;
  assert(adi->ConfigureDevice(id, &recovery_config) == DAL_SUCCESS);
  assert(adi->WriteStart(id, 0u) == DAL_SUCCESS);
  assert(adi->WriteBytes(id, 0u, 0u, 2u, recovered_frame) == DAL_SUCCESS);
  assert(adi->WriteEnd(id, 0u) == DAL_SUCCESS);
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

  assert(adi->ConfigureDevice(id, &recovery_config) == DAL_SUCCESS);
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

  int32_t inner = -99;
  assert(adi->CallDeviceSpecificFunction("unknown", &inner) == DAL_NOTUSED);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x9234u && effective == 0u);
  uint8_t recovery_frame[2] = {0x34u, 0x92u};
  assert(adi->WriteStart(id, 0u) == DAL_SUCCESS);
  assert(adi->WriteBytes(id, 0u, 0u, 2u, recovery_frame) == DAL_SUCCESS);
  assert(adi->WriteEnd(id, 0u) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x9234u && effective == 0u);
  assert(virtual_adi_set_permit(false) == DAL_SUCCESS);
  assert(virtual_adi_set_permit(true) == DAL_SUCCESS);
  assert(adi->WatchdogTrigger() == DAL_SUCCESS);
  assert(adi->WriteStart(id, 0u) == DAL_SUCCESS);
  assert(adi->WriteBytes(id, 0u, 0u, 2u, recovery_frame) == DAL_SUCCESS);
  assert(adi->WriteEnd(id, 0u) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x9234u && effective == 0u);
  assert(adi->ConfigureDevice(id, &recovery_config) == DAL_SUCCESS);
  assert(adi->WriteStart(id, 0u) == DAL_SUCCESS);
  assert(adi->WriteBytes(id, 0u, 0u, 2u, recovery_frame) == DAL_SUCCESS);
  assert(adi->WriteEnd(id, 0u) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x9234u && effective == 0x9234u);

  uint16_t module_id = 0u;
  assert(adi->CallDeviceSpecificFunction(LIBPACKBUS_DAL_FUNC_GET_UID, &inner,
                                         1, &module_id) == DAL_SUCCESS);
  assert(inner == -1);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x9234u && effective == 0u);
  assert(adi->WriteStart(id, 0u) == DAL_SUCCESS);
  assert(adi->WriteBytes(id, 0u, 0u, 2u, recovery_frame) == DAL_SUCCESS);
  assert(adi->WriteEnd(id, 0u) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x9234u && effective == 0u);
  assert(adi->ConfigureDevice(id, &recovery_config) == DAL_SUCCESS);
  assert(adi->WriteStart(id, 0u) == DAL_SUCCESS);
  assert(adi->WriteBytes(id, 0u, 0u, 2u, recovery_frame) == DAL_SUCCESS);
  assert(adi->WriteEnd(id, 0u) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x9234u && effective == 0x9234u);

  assert(virtual_adi_set_permit(false) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x9234u && effective == 0u);
}

static void test_digital8_profile(tApplicationDeviceInterface *adi) {
  assert(virtual_adi_select_profile(VIRTUAL_ADI_PROFILE_DIGITAL8_DI8_DO8) ==
         DAL_FAILURE); /* profile changes are frozen after Init */
  assert(virtual_adi_select_clock_mode(VIRTUAL_ADI_CLOCK_MONOTONIC) ==
         DAL_FAILURE);

  tDeviceInfo entry = {0};
  size_t count = 0u;
  assert(adi->GetDeviceList(1u, &entry, &count) == DAL_SUCCESS);
  uint32_t input_size = 0u, output_size = 0u;
  assert(adi->GetIoSizes(entry.DeviceId, &input_size, &output_size) ==
         DAL_SUCCESS);
  assert(input_size == 1u && output_size == 1u);
  assert(adi->OpenDevice(entry.DeviceId) == DAL_SUCCESS);
  tCONFIGURE_DEVICE config = {0};
  config.eStructType = TCF_SSC_CONF_STRUCT_3;
  assert(adi->ConfigureDevice(entry.DeviceId, &config) == DAL_SUCCESS);

  tKBUS_TERMINAL_INFO_32 records[2] = {{0}};
  int32_t inner = -1;
  count = 0u;
  assert(adi->CallDeviceSpecificFunction(
             LIBPACKBUS_DAL_FUNC_GET_TERMINAL_INFO_32, &inner,
             (uint32_t)sizeof(records), records, &count) == DAL_SUCCESS);
  assert(inner == 0 && count == 2u);
  assert(records[0].ulOffsetInput_bits == 0u &&
         records[0].ulOffsetOutput_bits == 0u &&
         records[0].ulSizeInput_bits == 8u &&
         records[0].ulSizeOutput_bits == 0u);
  assert(records[1].ulOffsetInput_bits == 0u &&
         records[1].ulOffsetOutput_bits == 0u &&
         records[1].ulSizeInput_bits == 0u &&
         records[1].ulSizeOutput_bits == 8u);

  uint16_t module_id = 0u;
  assert(adi->CallDeviceSpecificFunction(LIBPACKBUS_DAL_FUNC_READ_TAB_9,
                                         &inner, 1, &module_id) == DAL_SUCCESS);
  assert(inner == 0 && module_id == 0x8801u);
  assert(adi->CallDeviceSpecificFunction(LIBPACKBUS_DAL_FUNC_READ_TAB_9,
                                         &inner, 2, &module_id) == DAL_SUCCESS);
  assert(inner == 0 && module_id == 0x8802u);

  /* The original async wrapper reaches VCall, including promoted terminal id. */
  uint32_t terminal_count = 0u;
  assert(call_through_vcall(
             adi, LIBPACKBUS_DAL_FUNC_GET_TERMINAL_INFO_32, &inner,
             (uint32_t)0u, records, &terminal_count) == DAL_SUCCESS);
  assert(inner == 2 && terminal_count == 2u);
  assert(call_through_vcall(
             adi, LIBPACKBUS_DAL_FUNC_GET_TERMINAL_INFO_32, &inner,
             (uint32_t)sizeof(records), records, &terminal_count) == DAL_SUCCESS);
  assert(inner == 0 && records[0].ulSizeInput_bits == 8u &&
         records[1].ulSizeOutput_bits == 8u);
  assert(call_through_vcall(adi, LIBPACKBUS_DAL_FUNC_READ_TAB_9, &inner,
                            (int)1, &module_id) == DAL_SUCCESS);
  assert(inner == 0 && module_id == 0x8801u);
  assert(call_through_vcall(adi, LIBPACKBUS_DAL_FUNCTION_PUSH, &inner) ==
         DAL_SUCCESS);
  assert(inner == 0);

  assert(virtual_adi_set_inputs(0x01ffu) == DAL_SUCCESS); /* masked to 8 bits */
  assert(adi->ReadStart(entry.DeviceId, 0u) == DAL_SUCCESS);
  uint8_t input = 0u;
  assert(adi->ReadBytes(entry.DeviceId, 0u, 0u, 1u, &input) == DAL_SUCCESS);
  assert(input == 0xffu);
  uint8_t bit = 0u;
  assert(adi->ReadBit(entry.DeviceId, 0u, 7u, &bit) == DAL_SUCCESS && bit == 1u);
  assert(adi->ReadEnd(entry.DeviceId, 0u) == DAL_SUCCESS);

  assert(virtual_adi_set_application_state(ApplicationState_Running) ==
         DAL_SUCCESS);
  assert(virtual_adi_set_permit(true) == DAL_SUCCESS);
  assert(adi->WatchdogSetTime(1u, 10u) == DAL_SUCCESS);
  assert(adi->WatchdogStart() == DAL_SUCCESS);
  assert(adi->WatchdogStart() == DAL_FAILURE);
  assert(adi->WatchdogTrigger() == DAL_SUCCESS);
  assert(adi->WriteStart(entry.DeviceId, 0u) == DAL_SUCCESS);
  uint8_t output = 0xffu;
  assert(adi->WriteBytes(entry.DeviceId, 0u, 0u, 1u, &output) == DAL_SUCCESS);
  assert(adi->WriteEnd(entry.DeviceId, 0u) == DAL_SUCCESS);
  uint16_t requested = 0u, effective = 0u;
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x00ffu && effective == 0x00ffu);

  /* Task id zero does not transfer transaction ownership between threads. */
  assert(adi->WriteStart(entry.DeviceId, 0u) == DAL_SUCCESS);
  output = 0x5au;
  assert(adi->WriteBytes(entry.DeviceId, 0u, 0u, 1u, &output) == DAL_SUCCESS);
  cross_thread_call cross = {adi, entry.DeviceId, &output, DAL_FAILURE};
  pthread_t thread;
  assert(pthread_create(&thread, NULL, cross_thread_write, &cross) == 0);
  assert(pthread_join(thread, NULL) == 0);
  assert(cross.result == DAL_FAILURE);
  cross.result = DAL_FAILURE;
  assert(pthread_create(&thread, NULL, cross_thread_watchdog_trigger, &cross) ==
         0);
  assert(pthread_join(thread, NULL) == 0);
  assert(cross.result == DAL_SUCCESS);
  assert(adi->WriteEnd(entry.DeviceId, 0u) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x005au && effective == 0x005au);

  /* Rejected reconfiguration shuts down an already effective output. */
  config.uConfStru.rSSC_ConfStruct_III.ulTcmControl = 0x01000000u;
  assert(adi->ConfigureDevice(entry.DeviceId, &config) == DAL_FAILURE);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x005au && effective == 0u);
  tBusState fault_bus_state = BusState_BusOk;
  assert(adi->DiagnoseGetDeviceState(entry.DeviceId, 0u, NULL,
                                     &fault_bus_state) == DAL_SUCCESS);
  assert(fault_bus_state == BusState_BusFault);
  assert(call_through_vcall(adi, LIBPACKBUS_DAL_FUNCTION_PUSH, &inner) ==
         DAL_SUCCESS);
  assert(inner == DAL_FAILURE); /* own policy, original-shaped visible result */
  assert(adi->WatchdogTrigger() == DAL_SUCCESS);
  assert(adi->WriteStart(entry.DeviceId, 0u) == DAL_SUCCESS);
  assert(adi->WriteBytes(entry.DeviceId, 0u, 0u, 1u, &output) == DAL_SUCCESS);
  assert(adi->WriteEnd(entry.DeviceId, 0u) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x005au && effective == 0u);
  config.uConfStru.rSSC_ConfStruct_III.ulTcmControl = 0u;
  assert(adi->ConfigureDevice(entry.DeviceId, &config) == DAL_SUCCESS);
  assert(adi->DiagnoseGetDeviceState(entry.DeviceId, 0u, NULL,
                                     &fault_bus_state) == DAL_SUCCESS);
  assert(fault_bus_state == BusState_BusOk);
  assert(call_through_vcall(adi, LIBPACKBUS_DAL_FUNCTION_PUSH, &inner) ==
         DAL_SUCCESS);
  assert(inner == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(effective == 0u); /* recovery alone cannot publish retained data */
  assert(adi->WriteStart(entry.DeviceId, 0u) == DAL_SUCCESS);
  assert(adi->WriteBytes(entry.DeviceId, 0u, 0u, 1u, &output) == DAL_SUCCESS);
  assert(adi->WriteEnd(entry.DeviceId, 0u) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x005au && effective == 0x005au);

  /* An out-of-range bit rejects and aborts the entire staged frame. */
  assert(adi->WriteStart(entry.DeviceId, 0u) == DAL_SUCCESS);
  output = 0x12u;
  assert(adi->WriteBytes(entry.DeviceId, 0u, 0u, 1u, &output) == DAL_SUCCESS);
  bit = 1u;
  assert(adi->WriteBit(entry.DeviceId, 0u, 8u, &bit) == DAL_FAILURE);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x005au && effective == 0u);
  assert(adi->WriteEnd(entry.DeviceId, 0u) == DAL_FAILURE);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x005au && effective == 0u);

  /* A healthy full frame still cannot clear an operation fault implicitly. */
  uint8_t blocked_recovery = 0x33u;
  assert(adi->WriteStart(entry.DeviceId, 0u) == DAL_SUCCESS);
  assert(adi->WriteBytes(entry.DeviceId, 0u, 0u, 1u, &blocked_recovery) ==
         DAL_SUCCESS);
  assert(adi->WriteEnd(entry.DeviceId, 0u) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x0033u && effective == 0u);

  assert(virtual_adi_set_permit(false) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x0033u && effective == 0u);
  assert(virtual_adi_set_permit(true) == DAL_SUCCESS);
  assert(adi->WatchdogTrigger() == DAL_SUCCESS);
  assert(virtual_adi_advance_time_us(10u) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x0033u && effective == 0u);
  assert(adi->WatchdogTrigger() == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x0033u && effective == 0u);
  assert(adi->WriteStart(entry.DeviceId, 0u) == DAL_SUCCESS);
  assert(adi->WriteBytes(entry.DeviceId, 0u, 0u, 1u, &blocked_recovery) ==
         DAL_SUCCESS);
  assert(adi->WriteEnd(entry.DeviceId, 0u) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x0033u && effective == 0u);
  assert(adi->WatchdogStop() == DAL_SUCCESS);
  assert(adi->WatchdogTrigger() == DAL_FAILURE);

  assert(adi->CloseDevice(entry.DeviceId) == DAL_SUCCESS);
  assert(adi->OpenDevice(entry.DeviceId) == DAL_SUCCESS);
  assert(adi->ConfigureDevice(entry.DeviceId, &config) == DAL_SUCCESS);
  assert(adi->WriteStart(entry.DeviceId, 0u) == DAL_SUCCESS);
  assert(adi->WriteBytes(entry.DeviceId, 0u, 0u, 1u, &output) == DAL_SUCCESS);
  assert(adi->WriteEnd(entry.DeviceId, 0u) == DAL_SUCCESS);
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x0012u && effective == 0u);
  assert(adi->CloseDevice(entry.DeviceId) == DAL_SUCCESS);
}

static void test_monotonic_clock(tApplicationDeviceInterface *adi) {
  assert(virtual_adi_select_clock_mode(VIRTUAL_ADI_CLOCK_MONOTONIC) ==
         DAL_SUCCESS);
  assert(adi->Init() == DAL_SUCCESS);
  tDeviceInfo entry = {0};
  size_t count = 0u;
  assert(adi->GetDeviceList(1u, &entry, &count) == DAL_SUCCESS);
  assert(adi->OpenDevice(entry.DeviceId) == DAL_SUCCESS);
  tCONFIGURE_DEVICE config = {0};
  config.eStructType = TCF_SSC_CONF_STRUCT_3;
  assert(adi->ConfigureDevice(entry.DeviceId, &config) == DAL_SUCCESS);
  assert(virtual_adi_set_application_state(ApplicationState_Running) ==
         DAL_SUCCESS);
  assert(virtual_adi_set_permit(true) == DAL_SUCCESS);
  assert(adi->WatchdogSetTime(1u, 1000u) == DAL_SUCCESS);
  assert(adi->WatchdogSetTime(UINT32_MAX, UINT32_MAX) == DAL_FAILURE);
  assert(adi->WatchdogStart() == DAL_SUCCESS);
  assert(adi->WatchdogTrigger() == DAL_SUCCESS);
  uint8_t output[2] = {0x34u, 0x12u};
  assert(adi->WriteStart(entry.DeviceId, 0u) == DAL_SUCCESS);
  assert(adi->WriteBytes(entry.DeviceId, 0u, 0u, 2u, output) == DAL_SUCCESS);
  assert(adi->WriteEnd(entry.DeviceId, 0u) == DAL_SUCCESS);
  assert(virtual_adi_advance_time_us(1u) == DAL_FAILURE);

  struct timespec delay = {0, 2000000L};
  assert(nanosleep(&delay, NULL) == 0);
  uint16_t requested = 0u, effective = 0u;
  assert(virtual_adi_get_outputs(&requested, &effective) == DAL_SUCCESS);
  assert(requested == 0x1234u && effective == 0u);
  assert(adi->CloseDevice(entry.DeviceId) == DAL_SUCCESS);
  assert(adi->Exit() == DAL_SUCCESS);
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

  assert(virtual_adi_select_profile(VIRTUAL_ADI_PROFILE_DIGITAL8_DI8_DO8) ==
         DAL_SUCCESS);
  assert(adi->Init() == DAL_SUCCESS);
  assert(adi->ScanDevices() == DAL_SUCCESS);
  test_digital8_profile(adi);
  assert(adi->Exit() == DAL_SUCCESS);
  virtual_adi_reset();
  test_monotonic_clock(adi);
  virtual_adi_reset();
  assert(adi->Init() == DAL_SUCCESS);
  uint32_t reset_input_size = 0u, reset_output_size = 0u;
  assert(adi->GetIoSizes(1, &reset_input_size, &reset_output_size) ==
         DAL_SUCCESS);
  assert(reset_input_size == 2u && reset_output_size == 2u);
  assert(adi->Exit() == DAL_SUCCESS);
  puts("ADI digital model contract tests: PASS");
  return 0;
}
