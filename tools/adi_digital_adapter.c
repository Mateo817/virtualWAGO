/* Own in-memory ADI model for an explicitly virtual 1405/1504 digital slice.
 * This is neither byte-identical DAL behavior nor a hardware/device backend.
 */
#include "adi_digital_adapter.h"

#include <limits.h>
#include <stdarg.h>
#include <string.h>
#include <libpackbus.h>

#define VIRTUAL_DEVICE_ID ((tDeviceId)1)
#define VIRTUAL_DEVICE_NAME "libpackbus"
#define PROCESS_BYTES 2u
#define PROCESS_BITS 16u
#define VIRTUAL_TERMINALS 2u

typedef struct {
  bool initialized;
  bool opened;
  bool configured;
  bool app_running;
  bool permit;
  bool watchdog_healthy;
  bool read_active;
  bool write_active;
  bool write_failed;
  bool watchdog_started;
  bool watchdog_configured;
  uint32_t read_task;
  uint32_t write_task;
  uint64_t model_time_us;
  uint64_t watchdog_period_us;
  uint64_t watchdog_deadline_us;
  uint16_t input_signals;
  uint16_t read_latch;
  uint16_t requested_outputs;
  uint16_t staged_outputs;
  uint16_t staged_touched_bits;
  uint16_t effective_outputs;
} virtual_state;

static virtual_state state;

static bool valid_device(tDeviceId id) { return id == VIRTUAL_DEVICE_ID; }
static bool ready_device(tDeviceId id) {
  return valid_device(id) && state.initialized && state.opened &&
         state.configured;
}
static uint16_t read_le16(const uint8_t *data, uint32_t offset) {
  return (uint16_t)((uint16_t)data[offset] |
                    ((uint16_t)data[offset + 1u] << 8));
}
static void write_le16(uint8_t *data, uint16_t value) {
  data[0] = (uint8_t)(value & 0xffu);
  data[1] = (uint8_t)(value >> 8);
}
static bool effective_permit(void) {
  return state.app_running && state.permit && state.watchdog_healthy;
}

void virtual_adi_reset(void) { memset(&state, 0, sizeof(state)); }

int32_t virtual_adi_set_inputs(uint16_t input_bits) {
  if (!state.initialized) return DAL_FAILURE;
  state.input_signals = input_bits;
  return DAL_SUCCESS;
}

int32_t virtual_adi_set_permit(bool permit) {
  if (!state.initialized) return DAL_FAILURE;
  if (state.write_active && state.permit != permit) state.write_failed = true;
  state.permit = permit;
  if (!effective_permit()) state.effective_outputs = 0;
  if (!effective_permit() && state.write_active) state.write_failed = true;
  return DAL_SUCCESS;
}

int32_t virtual_adi_set_application_state(tApplicationState app_state) {
  if (!state.initialized || app_state < ApplicationState_BASE ||
      app_state >= ApplicationState_TOP)
    return DAL_FAILURE;
  bool running = app_state == ApplicationState_Running;
  if (state.write_active && state.app_running != running)
    state.write_failed = true;
  state.app_running = running;
  if (!effective_permit()) state.effective_outputs = 0;
  if (!effective_permit() && state.write_active) state.write_failed = true;
  return DAL_SUCCESS;
}

int32_t virtual_adi_advance_time_us(uint64_t elapsed_us) {
  if (!state.initialized || elapsed_us > UINT64_MAX - state.model_time_us)
    return DAL_FAILURE;
  state.model_time_us += elapsed_us;
  if (state.watchdog_started && state.model_time_us >= state.watchdog_deadline_us) {
    state.watchdog_healthy = false;
    state.effective_outputs = 0;
    if (state.write_active) state.write_failed = true;
  }
  return DAL_SUCCESS;
}

int32_t virtual_adi_get_outputs(uint16_t *requested, uint16_t *effective) {
  if (requested == NULL || effective == NULL) return DAL_FAILURE;
  *requested = state.requested_outputs;
  *effective = state.effective_outputs;
  return DAL_SUCCESS;
}

static int32_t adapter_init(void) {
  if (state.initialized) return DAL_FAILURE;
  memset(&state, 0, sizeof(state));
  state.initialized = true;
  /* Fail-closed model defaults; not claimed as vendor policy. */
  state.watchdog_healthy = false;
  return DAL_SUCCESS;
}

static int32_t adapter_exit(void) {
  if (!state.initialized) return DAL_FAILURE;
  memset(&state, 0, sizeof(state));
  return DAL_SUCCESS;
}

static int32_t adapter_scan(void) {
  return state.initialized ? DAL_SUCCESS : DAL_FAILURE;
}

static int32_t adapter_list(size_t capacity, tDeviceInfo *list,
                            size_t *device_count) {
  if (!state.initialized || device_count == NULL ||
      (capacity != 0u && list == NULL))
    return DAL_FAILURE;
  *device_count = 1u;
  if (capacity != 0u) {
    list[0].DeviceId = VIRTUAL_DEVICE_ID;
    list[0].DeviceName = VIRTUAL_DEVICE_NAME;
  }
  return DAL_SUCCESS;
}

static int32_t adapter_open(tDeviceId id) {
  if (!state.initialized || !valid_device(id) || state.opened)
    return DAL_FAILURE;
  state.opened = true;
  return DAL_SUCCESS;
}

static int32_t adapter_close(tDeviceId id) {
  if (!valid_device(id) || !state.opened || state.read_active ||
      state.write_active)
    return DAL_FAILURE;
  state.opened = false;
  state.configured = false;
  state.app_running = false;
  state.permit = false;
  state.watchdog_started = false;
  state.watchdog_healthy = false;
  state.watchdog_configured = false;
  state.watchdog_period_us = 0u;
  state.watchdog_deadline_us = 0u;
  state.requested_outputs = 0u;
  state.staged_outputs = 0u;
  state.effective_outputs = 0;
  return DAL_SUCCESS;
}

static bool adapter_is_open(tDeviceId id) {
  return valid_device(id) && state.initialized && state.opened;
}

static int32_t adapter_name(tDeviceId id, size_t capacity, char *buffer,
                            size_t *length) {
  const size_t name_length = sizeof(VIRTUAL_DEVICE_NAME) - 1u;
  if (!valid_device(id) || !state.initialized || buffer == NULL ||
      length == NULL || capacity == 0u)
    return DAL_FAILURE;
  size_t copied = name_length < capacity ? name_length : capacity - 1u;
  memcpy(buffer, VIRTUAL_DEVICE_NAME, copied);
  buffer[copied] = '\0';
  *length = copied;
  return copied == 0u ? DAL_FAILURE : DAL_SUCCESS;
}

static int32_t adapter_flags(tDeviceId id, uint32_t *flags) {
  if (!valid_device(id) || !state.initialized || flags == NULL)
    return DAL_FAILURE;
  *flags = 0u;
  return DAL_SUCCESS;
}

static int32_t adapter_sizes(tDeviceId id, uint32_t *input, uint32_t *output) {
  if (!valid_device(id) || !state.initialized || input == NULL ||
      output == NULL)
    return DAL_FAILURE;
  *input = PROCESS_BYTES;
  *output = PROCESS_BYTES;
  return DAL_SUCCESS;
}

static int32_t adapter_configure_subdevice(tDeviceId id, int32_t subdevice,
                                            void *config) {
  (void)id;
  (void)subdevice;
  (void)config;
  return DAL_FAILURE;
}

static int32_t adapter_configure(tDeviceId id, void *config_data) {
  if (!valid_device(id) || !state.opened || config_data == NULL ||
      state.read_active || state.write_active)
    return DAL_FAILURE;
  const tCONFIGURE_DEVICE *config = (const tCONFIGURE_DEVICE *)config_data;
  if (config->eStructType != TCF_SSC_CONF_STRUCT_3) return DAL_FAILURE;
  const tSSC_CONF_STRUCT_III *type_iii =
      &config->uConfStru.rSSC_ConfStruct_III;
  if (type_iii->ulTcmControl != 0u ||
      type_iii->boSSC_NewProcessImag)
    return DAL_FAILURE;
  state.configured = true;
  return DAL_SUCCESS;
}

static int32_t adapter_write_start(tDeviceId id, uint32_t task) {
  if (!ready_device(id) || task != 0u || state.write_active) return DAL_FAILURE;
  state.staged_outputs = state.requested_outputs;
  state.staged_touched_bits = 0u;
  state.write_task = task;
  state.write_active = true;
  return DAL_SUCCESS;
}

static int32_t adapter_write_bytes(tDeviceId id, uint32_t task,
                                   uint32_t offset, uint32_t size,
                                   uint8_t *data) {
  if (!ready_device(id) || !state.write_active || task != state.write_task ||
      (size != 0u && data == NULL) || offset > PROCESS_BYTES ||
      size > PROCESS_BYTES - offset) {
    if (valid_device(id) && state.write_active) state.write_failed = true;
    return DAL_FAILURE;
  }
  if (size == 0u) return DAL_SUCCESS;
  uint8_t frame[PROCESS_BYTES];
  write_le16(frame, state.staged_outputs);
  memcpy(frame + offset, data, size);
  state.staged_outputs = read_le16(frame, 0u);
  if (offset == 0u) state.staged_touched_bits |= 0x00ffu;
  if (offset == 1u) state.staged_touched_bits |= 0xff00u;
  if (size == 2u) state.staged_touched_bits = 0xffffu;
  return DAL_SUCCESS;
}

static int32_t adapter_write_bit(tDeviceId id, uint32_t task,
                                 uint32_t bit_offset, uint8_t *data) {
  if (!ready_device(id) || !state.write_active || task != state.write_task ||
      bit_offset >= PROCESS_BITS || data == NULL) {
    if (valid_device(id) && state.write_active) state.write_failed = true;
    return DAL_FAILURE;
  }
  const uint16_t mask = (uint16_t)(1u << bit_offset);
  if ((*data & 1u) != 0u)
    state.staged_outputs = (uint16_t)(state.staged_outputs | mask);
  else
    state.staged_outputs = (uint16_t)(state.staged_outputs & (uint16_t)~mask);
  state.staged_touched_bits |= mask;
  return DAL_SUCCESS;
}

static int32_t adapter_write_bool(tDeviceId id, uint32_t task,
                                 uint32_t bit_offset, bool value) {
  uint8_t byte_value = value ? 1u : 0u;
  return adapter_write_bit(id, task, bit_offset, &byte_value);
}

static int32_t adapter_write_end(tDeviceId id, uint32_t task) {
  if (!ready_device(id) || !state.write_active || task != state.write_task)
    return DAL_FAILURE;
  if (state.write_failed || state.staged_touched_bits != 0xffffu) {
    state.write_active = false;
    state.write_failed = false;
    state.staged_outputs = state.requested_outputs;
    state.staged_touched_bits = 0u;
    return DAL_FAILURE;
  }
  state.requested_outputs = state.staged_outputs;
  state.effective_outputs = effective_permit() ? state.staged_outputs : 0u;
  state.write_active = false;
  state.write_failed = false;
  state.staged_touched_bits = 0u;
  return DAL_SUCCESS;
}

static int32_t adapter_read_start(tDeviceId id, uint32_t task) {
  if (!ready_device(id) || task != 0u || state.read_active) return DAL_FAILURE;
  state.read_latch = state.input_signals;
  state.read_task = task;
  state.read_active = true;
  return DAL_SUCCESS;
}

static int32_t adapter_read_bytes(tDeviceId id, uint32_t task,
                                  uint32_t offset, uint32_t size,
                                  uint8_t *data) {
  if (!ready_device(id) || !state.read_active || task != state.read_task ||
      (size != 0u && data == NULL) || offset > PROCESS_BYTES ||
      size > PROCESS_BYTES - offset)
    return DAL_FAILURE;
  if (size == 0u) return DAL_SUCCESS;
  uint8_t frame[PROCESS_BYTES];
  write_le16(frame, state.read_latch);
  memcpy(data, frame + offset, size);
  return DAL_SUCCESS;
}

static int32_t adapter_read_bit(tDeviceId id, uint32_t task,
                                uint32_t bit_offset, uint8_t *data) {
  if (!ready_device(id) || !state.read_active || task != state.read_task ||
      bit_offset >= PROCESS_BITS || data == NULL)
    return DAL_FAILURE;
  *data = (uint8_t)((state.read_latch >> bit_offset) & 1u);
  return DAL_SUCCESS;
}

static int32_t adapter_read_bool(tDeviceId id, uint32_t task,
                                uint32_t bit_offset, bool *value) {
  if (value == NULL || bit_offset >= PROCESS_BITS) return DAL_FAILURE;
  uint8_t bit = 0u;
  int32_t result = adapter_read_bit(id, task, bit_offset, &bit);
  if (result == DAL_SUCCESS) *value = bit != 0u;
  return result;
}

static int32_t adapter_read_end(tDeviceId id, uint32_t task) {
  if (!ready_device(id) || !state.read_active || task != state.read_task)
    return DAL_FAILURE;
  state.read_active = false;
  return DAL_SUCCESS;
}

static int32_t adapter_diagnose(tDeviceId id, uint32_t buffer_size,
                                uint8_t *buffer, tBusState *bus_state) {
  if (!valid_device(id) || !state.initialized || bus_state == NULL ||
      (buffer_size != 0u && buffer == NULL))
    return DAL_FAILURE;
  if (buffer_size != 0u) memset(buffer, 0, buffer_size);
  *bus_state = state.opened && state.configured ? BusState_BusOk
                                                : BusState_NotEnabled;
  return DAL_SUCCESS;
}

static int32_t adapter_diagnose_subdevice(tDeviceId id, int32_t subdevice,
                                          size_t buffer_size, uint8_t *buffer,
                                          tDiagnoseState *diagnose_state) {
  (void)id;
  (void)subdevice;
  (void)buffer_size;
  (void)buffer;
  (void)diagnose_state;
  return DAL_FAILURE;
}

static int32_t adapter_register_event(tDeviceId id, tEventHandler handler,
                                      void *user_data) {
  (void)id;
  (void)handler;
  (void)user_data;
  return DAL_FAILURE;
}

static int32_t adapter_unregister_event(tDeviceId id, tEventHandler handler) {
  (void)id;
  (void)handler;
  return DAL_FAILURE;
}

static int32_t adapter_last_error(tDeviceId id, tError *error) {
  (void)id;
  (void)error;
  return DAL_FAILURE;
}

static int32_t adapter_app_state(tApplicationStateChangedEvent event) {
  return virtual_adi_set_application_state(event.State);
}

static int32_t inner_terminal_info(uint32_t capacity, void *records,
                                   void *count_out) {
  if (records == NULL || count_out == NULL) return 1;
  const uint32_t count = VIRTUAL_TERMINALS;
  const uint32_t needed = count * (uint32_t)sizeof(tKBUS_TERMINAL_INFO_32);
  *(uint32_t *)count_out = count;
  if (capacity < needed) return 2;
  tKBUS_TERMINAL_INFO_32 model[VIRTUAL_TERMINALS] = {
      {0u, 0u, 16u, 0u},
      {16u, 0u, 0u, 16u},
  };
  memcpy(records, model, needed);
  if (capacity > needed) memset((uint8_t *)records + needed, 0, capacity - needed);
  return 0;
}

static int32_t device_specific(const char *name, void *return_value,
                               va_list args) {
  if (name == NULL) return DAL_NOTUSED;
  if (strcmp(name, LIBPACKBUS_DAL_FUNCTION_PUSH) == 0) {
    if (return_value == NULL || !state.initialized) return DAL_FAILURE;
    *(int32_t *)return_value = 0;
    return DAL_SUCCESS;
  }
  if (strcmp(name, LIBPACKBUS_DAL_FUNC_GET_TERMINAL_INFO_32) == 0) {
    if (return_value == NULL || !state.initialized) return DAL_FAILURE;
    uint32_t capacity = va_arg(args, uint32_t);
    void *records = va_arg(args, void *);
    void *count = va_arg(args, void *);
    *(int32_t *)return_value = inner_terminal_info(capacity, records, count);
    return DAL_SUCCESS;
  }
  if (strcmp(name, LIBPACKBUS_DAL_FUNC_READ_TAB_9) == 0) {
    if (return_value == NULL || !state.initialized) return DAL_FAILURE;
    int terminal = va_arg(args, int); /* uint8_t is promoted to int */
    uint16_t *module_id = va_arg(args, uint16_t *);
    int32_t result = -1;
    if (terminal >= 1 && terminal <= (int)VIRTUAL_TERMINALS) {
      if (module_id == NULL) {
        result = -2;
      } else {
        *module_id = terminal == 1 ? 0x9001u : 0x9002u;
        result = 0;
      }
    }
    *(int32_t *)return_value = result;
    return DAL_SUCCESS;
  }
  if (strcmp(name, LIBPACKBUS_DAL_FUNC_GET_UID) == 0 ||
      strcmp(name, LIBPACKBUS_DAL_FUNC_READ_CONF_REG) == 0) {
    if (return_value == NULL || !state.initialized) return DAL_FAILURE;
    *(int32_t *)return_value = -1; /* Explicitly unsupported by this model. */
    return DAL_SUCCESS;
  }
  return DAL_NOTUSED;
}

static int32_t adapter_call_device_specific(const char *name, void *ret,
                                           ...) {
  va_list args;
  va_start(args, ret);
  int32_t result = device_specific(name, ret, args);
  va_end(args);
  return result;
}

static int32_t adapter_vcall_device_specific(const char *name, void *ret,
                                             va_list args) {
  return device_specific(name, ret, args);
}

static int32_t adapter_watchdog_set_time(uint32_t factor, uint32_t timeout_us) {
  if (!state.initialized || factor == 0u || timeout_us == 0u ||
      factor > UINT32_MAX / timeout_us)
    return DAL_FAILURE;
  state.watchdog_period_us = (uint64_t)factor * (uint64_t)timeout_us;
  state.watchdog_configured = true;
  return DAL_SUCCESS;
}

static int32_t adapter_watchdog_start(void) {
  if (!state.initialized || !state.watchdog_configured) return DAL_FAILURE;
  state.watchdog_started = true;
  state.watchdog_healthy = false;
  state.watchdog_deadline_us = state.model_time_us;
  state.effective_outputs = 0;
  if (state.write_active) state.write_failed = true;
  return DAL_SUCCESS;
}

static int32_t adapter_watchdog_stop(void) {
  if (!state.initialized) return DAL_FAILURE;
  state.watchdog_started = false;
  state.watchdog_healthy = false;
  state.effective_outputs = 0;
  if (state.write_active) state.write_failed = true;
  return DAL_SUCCESS;
}

static int32_t adapter_watchdog_trigger(void) {
  if (!state.initialized || !state.watchdog_started ||
      !state.watchdog_configured ||
      state.watchdog_period_us > UINT64_MAX - state.model_time_us)
    return DAL_FAILURE;
  state.watchdog_healthy = true;
  state.watchdog_deadline_us = state.model_time_us + state.watchdog_period_us;
  if (state.write_active) state.write_failed = true;
  return DAL_SUCCESS;
}

static tApplicationDeviceInterface interface_table = {
    .Init = adapter_init,
    .Exit = adapter_exit,
    .ScanDevices = adapter_scan,
    .GetDeviceList = adapter_list,
    .OpenDevice = adapter_open,
    .CloseDevice = adapter_close,
    .IsDeviceOpen = adapter_is_open,
    .GetDeviceName = adapter_name,
    .GetDeviceFlags = adapter_flags,
    .GetIoSizes = adapter_sizes,
    .ConfigureSubdevice = adapter_configure_subdevice,
    .ConfigureDevice = adapter_configure,
    .WriteStart = adapter_write_start,
    .WriteBit = adapter_write_bit,
    .WriteBool = adapter_write_bool,
    .WriteBytes = adapter_write_bytes,
    .WriteEnd = adapter_write_end,
    .ReadStart = adapter_read_start,
    .ReadBit = adapter_read_bit,
    .ReadBool = adapter_read_bool,
    .ReadBytes = adapter_read_bytes,
    .ReadEnd = adapter_read_end,
    .DiagnoseGetDeviceState = adapter_diagnose,
    .DiagnoseGetSubdeviceState = adapter_diagnose_subdevice,
    .RegisterEventHandler = adapter_register_event,
    .UnregisterEventHandler = adapter_unregister_event,
    .GetLastError = adapter_last_error,
    .ApplicationStateChanged = adapter_app_state,
    .CallDeviceSpecificFunction = adapter_call_device_specific,
    .VCallDeviceSpecificFunction = adapter_vcall_device_specific,
    .WatchdogSetTime = adapter_watchdog_set_time,
    .WatchdogStart = adapter_watchdog_start,
    .WatchdogStop = adapter_watchdog_stop,
    .WatchdogTrigger = adapter_watchdog_trigger,
};

tApplicationDeviceInterface *adi_GetApplicationInterface(void) {
  return &interface_table;
}
