#define _GNU_SOURCE

/* Own in-memory ADI model for an explicitly selected virtual digital profile.
 * This is neither byte-identical DAL behavior nor a hardware/device backend.
 */
#include "adi_digital_adapter.h"
#ifdef VIRTUALWAGO_ENABLE_MODEL_BRIDGE
#include "adi_model_bridge.h"
#endif

#include <limits.h>
#include <pthread.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <time.h>
#include <libpackbus.h>

#define VIRTUAL_DEVICE_ID ((tDeviceId)1)
#define VIRTUAL_DEVICE_NAME "libpackbus"

typedef struct {
  virtual_adi_profile profile;
  uint32_t input_bytes;
  uint32_t output_bytes;
  uint32_t input_bits;
  uint32_t output_bits;
  uint16_t input_mask;
  uint16_t output_mask;
  uint32_t terminal_count;
  uint16_t module_ids[2];
  const char *parameter10[2];
  const char *process_field_type;
} virtual_profile_data;

/* These are own model metadata. Parameter strings came from the supplied
 * device descriptions; no physical identity or runtime selection is implied.
 */
static const virtual_profile_data profile_digital16 = {
    VIRTUAL_ADI_PROFILE_DIGITAL16, 2u, 2u, 16u, 16u, 0xffffu, 0xffffu, 2u,
    {0x9001u, 0x9002u}, {NULL, NULL}, NULL};
static const virtual_profile_data profile_digital8 = {
    VIRTUAL_ADI_PROFILE_DIGITAL8_DI8_DO8, 1u, 1u, 8u, 8u, 0x00ffu, 0x00ffu,
    2u, {0x8801u, 0x8802u}, {"UUUU8801UUUUUUUU", "UUUU8802UUUUUUUU"},
    "stdBYTE8bools"};
#ifdef VIRTUALWAGO_DEFAULT_PROFILE8
static const virtual_profile_data *default_profile = &profile_digital8;
#else
static const virtual_profile_data *default_profile = &profile_digital16;
#endif
#ifdef VIRTUALWAGO_DEFAULT_CLOCK_MONOTONIC
static const virtual_adi_clock_mode default_clock_mode =
    VIRTUAL_ADI_CLOCK_MONOTONIC;
#else
static const virtual_adi_clock_mode default_clock_mode =
    VIRTUAL_ADI_CLOCK_LOGICAL;
#endif
#ifdef VIRTUALWAGO_DEFAULT_PROFILE8
static const virtual_profile_data *selected_profile = &profile_digital8;
#else
static const virtual_profile_data *selected_profile = &profile_digital16;
#endif
static virtual_adi_clock_mode selected_clock_mode = default_clock_mode;

typedef struct {
  bool initialized;
  bool opened;
  bool configured;
  bool app_running;
  bool permit;
  bool watchdog_healthy;
  bool fault_latched;
  bool read_active;
  bool write_active;
  bool write_failed;
  bool watchdog_started;
  bool watchdog_configured;
  bool read_owner_valid;
  bool write_owner_valid;
  uint32_t read_task;
  uint32_t write_task;
  pthread_t read_owner;
  pthread_t write_owner;
  uint64_t read_generation;
  uint64_t write_generation;
  uint64_t model_time_us;
  uint64_t watchdog_period_us;
  uint64_t watchdog_deadline_us;
  uint16_t input_signals;
  uint16_t read_latch;
  uint16_t requested_outputs;
  uint16_t staged_outputs;
  uint16_t staged_touched_bits;
  uint16_t effective_outputs;
  uint64_t frame_count;
} virtual_state;

static virtual_state state;
static pthread_mutex_t state_mutex = PTHREAD_MUTEX_INITIALIZER;
#ifdef VIRTUALWAGO_ENABLE_MODEL_BRIDGE
/* Serialize the full Init/Exit lifecycle, including bridge join after releasing
 * state_mutex. The worker never takes this mutex.
 */
static pthread_mutex_t lifecycle_mutex = PTHREAD_MUTEX_INITIALIZER;
#endif
static uint64_t lifecycle_generation;

static int lock_state(void) {
  if (pthread_mutex_lock(&state_mutex) != 0) abort();
  return 1;
}

static void unlock_state(int *locked) {
  if (locked != NULL && *locked && pthread_mutex_unlock(&state_mutex) != 0)
    abort();
}

/* GNU cleanup keeps every public ABI entry serialized across all return paths. */
#define STATE_GUARD \
  int state_guard __attribute__((cleanup(unlock_state))) = lock_state(); \
  (void)state_guard

#ifdef VIRTUALWAGO_ENABLE_MODEL_BRIDGE
static void unlock_lifecycle(int *locked) {
  if (locked != NULL && *locked && pthread_mutex_unlock(&lifecycle_mutex) != 0)
    abort();
}

#define LIFECYCLE_GUARD \
  int lifecycle_guard __attribute__((cleanup(unlock_lifecycle))) = \
      (pthread_mutex_lock(&lifecycle_mutex) == 0 ? 1 : (abort(), 0)); \
  (void)lifecycle_guard
#endif

static void bump_lifecycle_generation(void) {
  ++lifecycle_generation;
  if (lifecycle_generation == 0u) ++lifecycle_generation;
}

static uint64_t current_time_us(void) {
  if (selected_clock_mode == VIRTUAL_ADI_CLOCK_LOGICAL)
    return state.model_time_us;
  struct timespec now;
  if (clock_gettime(CLOCK_MONOTONIC, &now) != 0 || now.tv_sec < 0)
    return UINT64_MAX;
  uint64_t seconds = (uint64_t)now.tv_sec;
  if (seconds > (UINT64_MAX - (uint64_t)now.tv_nsec / 1000u) / 1000000u)
    return UINT64_MAX;
  return seconds * 1000000u + (uint64_t)now.tv_nsec / 1000u;
}

static void refresh_watchdog_locked(void) {
  if (state.watchdog_started && state.watchdog_healthy &&
      current_time_us() >= state.watchdog_deadline_us) {
    state.watchdog_healthy = false;
    state.effective_outputs = 0u;
    if (state.write_active) state.write_failed = true;
  }
}

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
  return state.app_running && state.permit && state.watchdog_healthy &&
         !state.fault_latched;
}

static void latch_fault_locked(void) {
  state.fault_latched = true;
  state.effective_outputs = 0u;
  if (state.write_active) state.write_failed = true;
}

static bool owns_read(uint32_t task) {
  return state.read_active && task == state.read_task &&
         state.read_owner_valid &&
         pthread_equal(state.read_owner, pthread_self()) != 0 &&
         state.read_generation == lifecycle_generation;
}

static bool owns_write(uint32_t task) {
  return state.write_active && task == state.write_task &&
         state.write_owner_valid &&
         pthread_equal(state.write_owner, pthread_self()) != 0 &&
         state.write_generation == lifecycle_generation;
}

#ifdef VIRTUALWAGO_ENABLE_MODEL_BRIDGE
/* Own IPC metadata only. These are not added WAGO ABI slots. */
int32_t virtual_adi_model_snapshot(virtual_model_snapshot *snapshot) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (snapshot == NULL) return DAL_FAILURE;
  *snapshot = (virtual_model_snapshot){
      .initialized = state.initialized, .opened = state.opened,
      .configured = state.configured, .app_running = state.app_running,
      .permit = state.permit, .watchdog_healthy = state.watchdog_healthy,
      .fault_latched = state.fault_latched, .inputs = state.input_signals,
      .requested_outputs = state.requested_outputs,
      .effective_outputs = state.effective_outputs,
      .generation = lifecycle_generation, .frame_count = state.frame_count};
  return DAL_SUCCESS;
}

int32_t virtual_adi_latch_fault(void) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!state.initialized) return DAL_FAILURE;
  latch_fault_locked();
  return DAL_SUCCESS;
}
#endif

void virtual_adi_reset(void) {
  STATE_GUARD;
  refresh_watchdog_locked();
  bump_lifecycle_generation();
  memset(&state, 0, sizeof(state));
  selected_profile = default_profile;
  selected_clock_mode = default_clock_mode;
}

int32_t virtual_adi_select_profile(virtual_adi_profile profile) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (state.initialized) return DAL_FAILURE;
  if (profile == VIRTUAL_ADI_PROFILE_DIGITAL16)
    selected_profile = &profile_digital16;
  else if (profile == VIRTUAL_ADI_PROFILE_DIGITAL8_DI8_DO8)
    selected_profile = &profile_digital8;
  else
    return DAL_FAILURE;
  return DAL_SUCCESS;
}

int32_t virtual_adi_select_clock_mode(virtual_adi_clock_mode mode) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (state.initialized) return DAL_FAILURE;
  if (mode != VIRTUAL_ADI_CLOCK_LOGICAL &&
      mode != VIRTUAL_ADI_CLOCK_MONOTONIC)
    return DAL_FAILURE;
  selected_clock_mode = mode;
  return DAL_SUCCESS;
}

int32_t virtual_adi_set_inputs(uint16_t input_bits) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!state.initialized) return DAL_FAILURE;
  state.input_signals = (uint16_t)(input_bits & selected_profile->input_mask);
  return DAL_SUCCESS;
}

int32_t virtual_adi_set_permit(bool permit) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!state.initialized) return DAL_FAILURE;
  if (state.write_active && state.permit != permit) state.write_failed = true;
  state.permit = permit;
  if (!effective_permit()) state.effective_outputs = 0;
  if (!effective_permit() && state.write_active) state.write_failed = true;
  return DAL_SUCCESS;
}

int32_t virtual_adi_set_application_state(tApplicationState app_state) {
  STATE_GUARD;
  refresh_watchdog_locked();
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
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!state.initialized ||
      selected_clock_mode != VIRTUAL_ADI_CLOCK_LOGICAL ||
      elapsed_us > UINT64_MAX - state.model_time_us)
    return DAL_FAILURE;
  state.model_time_us += elapsed_us;
  refresh_watchdog_locked();
  return DAL_SUCCESS;
}

int32_t virtual_adi_get_outputs(uint16_t *requested, uint16_t *effective) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (requested == NULL || effective == NULL) return DAL_FAILURE;
  *requested = state.requested_outputs;
  *effective = state.effective_outputs;
  return DAL_SUCCESS;
}

static int32_t adapter_init(void) {
#ifdef VIRTUALWAGO_ENABLE_MODEL_BRIDGE
  LIFECYCLE_GUARD;
#endif
  STATE_GUARD;
  refresh_watchdog_locked();
  if (state.initialized) return DAL_FAILURE;
#ifdef VIRTUALWAGO_ENABLE_MODEL_BRIDGE
  if (virtual_model_bridge_start() != 0) return DAL_FAILURE;
#endif
  memset(&state, 0, sizeof(state));
  bump_lifecycle_generation();
  state.initialized = true;
  /* Fail-closed model defaults; not claimed as vendor policy. */
  state.watchdog_healthy = false;
  return DAL_SUCCESS;
}

static int32_t adapter_exit(void) {
#ifdef VIRTUALWAGO_ENABLE_MODEL_BRIDGE
  LIFECYCLE_GUARD;
#endif
  {
    STATE_GUARD;
    refresh_watchdog_locked();
    if (!state.initialized) return DAL_FAILURE;
    bump_lifecycle_generation();
    memset(&state, 0, sizeof(state));
  }
#ifdef VIRTUALWAGO_ENABLE_MODEL_BRIDGE
  /* The worker may wait for state_mutex; never join while holding it. */
  virtual_model_bridge_stop();
#endif
  return DAL_SUCCESS;
}

static int32_t adapter_scan(void) {
  STATE_GUARD;
  refresh_watchdog_locked();
  return state.initialized ? DAL_SUCCESS : DAL_FAILURE;
}

static int32_t adapter_list(size_t capacity, tDeviceInfo *list,
                            size_t *device_count) {
  STATE_GUARD;
  refresh_watchdog_locked();
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
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!state.initialized || !valid_device(id) || state.opened)
    return DAL_FAILURE;
  state.opened = true;
  state.fault_latched = false;
  return DAL_SUCCESS;
}

static int32_t adapter_close(tDeviceId id) {
  STATE_GUARD;
  refresh_watchdog_locked();
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
  state.fault_latched = false;
  bump_lifecycle_generation();
  return DAL_SUCCESS;
}

static bool adapter_is_open(tDeviceId id) {
  STATE_GUARD;
  refresh_watchdog_locked();
  return valid_device(id) && state.initialized && state.opened;
}

static int32_t adapter_name(tDeviceId id, size_t capacity, char *buffer,
                            size_t *length) {
  STATE_GUARD;
  refresh_watchdog_locked();
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
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!valid_device(id) || !state.initialized || flags == NULL)
    return DAL_FAILURE;
  *flags = 0u;
  return DAL_SUCCESS;
}

static int32_t adapter_sizes(tDeviceId id, uint32_t *input, uint32_t *output) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!valid_device(id) || !state.initialized || input == NULL ||
      output == NULL)
    return DAL_FAILURE;
  *input = selected_profile->input_bytes;
  *output = selected_profile->output_bytes;
  return DAL_SUCCESS;
}

static int32_t adapter_configure_subdevice(tDeviceId id, int32_t subdevice,
                                            void *config) {
  STATE_GUARD;
  refresh_watchdog_locked();
  (void)id;
  (void)subdevice;
  (void)config;
  return DAL_FAILURE;
}

static int32_t adapter_configure(tDeviceId id, void *config_data) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!valid_device(id) || !state.opened)
    return DAL_FAILURE;
  if (config_data == NULL || state.read_active || state.write_active) {
    latch_fault_locked();
    return DAL_FAILURE;
  }
  const tCONFIGURE_DEVICE *config = (const tCONFIGURE_DEVICE *)config_data;
  if (config->eStructType != TCF_SSC_CONF_STRUCT_3) {
    latch_fault_locked();
    return DAL_FAILURE;
  }
  const tSSC_CONF_STRUCT_III *type_iii =
      &config->uConfStru.rSSC_ConfStruct_III;
  if (type_iii->ulTcmControl != 0u ||
      type_iii->boSSC_NewProcessImag) {
    latch_fault_locked();
    return DAL_FAILURE;
  }
  state.configured = true;
  state.fault_latched = false;
  return DAL_SUCCESS;
}

static int32_t adapter_write_start(tDeviceId id, uint32_t task) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!ready_device(id) || task != 0u || state.write_active) return DAL_FAILURE;
  state.staged_outputs = state.requested_outputs;
  state.staged_touched_bits = 0u;
  state.write_task = task;
  state.write_owner = pthread_self();
  state.write_owner_valid = true;
  state.write_generation = lifecycle_generation;
  state.write_active = true;
  return DAL_SUCCESS;
}

static int32_t adapter_write_bytes(tDeviceId id, uint32_t task,
                                   uint32_t offset, uint32_t size,
                                   uint8_t *data) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!ready_device(id) || !owns_write(task)) return DAL_FAILURE;
  if ((size != 0u && data == NULL) ||
      offset > selected_profile->output_bytes ||
      size > selected_profile->output_bytes - offset) {
    latch_fault_locked();
    return DAL_FAILURE;
  }
  if (size == 0u) return DAL_SUCCESS;
  uint8_t frame[2];
  write_le16(frame, state.staged_outputs);
  memcpy(frame + offset, data, size);
  state.staged_outputs = (uint16_t)(read_le16(frame, 0u) &
                                    selected_profile->output_mask);
  for (uint32_t i = 0u; i < size; ++i) {
    uint32_t bit = (offset + i) * 8u;
    state.staged_touched_bits |= (uint16_t)(0x00ffu << bit);
  }
  state.staged_touched_bits &= selected_profile->output_mask;
  return DAL_SUCCESS;
}

static int32_t adapter_write_bit(tDeviceId id, uint32_t task,
                                 uint32_t bit_offset, uint8_t *data) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!ready_device(id) || !owns_write(task)) return DAL_FAILURE;
  if (bit_offset >= selected_profile->output_bits || data == NULL) {
    latch_fault_locked();
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
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!ready_device(id) || !owns_write(task)) return DAL_FAILURE;
  if (bit_offset >= selected_profile->output_bits) {
    latch_fault_locked();
    return DAL_FAILURE;
  }
  const uint16_t mask = (uint16_t)(1u << bit_offset);
  if (value)
    state.staged_outputs = (uint16_t)(state.staged_outputs | mask);
  else
    state.staged_outputs = (uint16_t)(state.staged_outputs & (uint16_t)~mask);
  state.staged_touched_bits |= mask;
  return DAL_SUCCESS;
}

static int32_t adapter_write_end(tDeviceId id, uint32_t task) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!ready_device(id) || !owns_write(task))
    return DAL_FAILURE;
  if (state.write_failed ||
      state.staged_touched_bits != selected_profile->output_mask) {
    if (!state.write_failed) latch_fault_locked();
    state.write_active = false;
    state.write_owner_valid = false;
    state.write_failed = false;
    state.staged_outputs = state.requested_outputs;
    state.staged_touched_bits = 0u;
    return DAL_FAILURE;
  }
  state.requested_outputs = state.staged_outputs;
  if (state.frame_count != UINT64_MAX) ++state.frame_count;
  state.effective_outputs = effective_permit() ? state.staged_outputs : 0u;
  state.write_active = false;
  state.write_owner_valid = false;
  state.write_failed = false;
  state.staged_touched_bits = 0u;
  return DAL_SUCCESS;
}

static int32_t adapter_read_start(tDeviceId id, uint32_t task) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!ready_device(id) || task != 0u || state.read_active) return DAL_FAILURE;
  state.read_latch = state.input_signals;
  state.read_task = task;
  state.read_owner = pthread_self();
  state.read_owner_valid = true;
  state.read_generation = lifecycle_generation;
  state.read_active = true;
  return DAL_SUCCESS;
}

static int32_t adapter_read_bytes(tDeviceId id, uint32_t task,
                                  uint32_t offset, uint32_t size,
                                  uint8_t *data) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!ready_device(id) || !owns_read(task))
    return DAL_FAILURE;
  if ((size != 0u && data == NULL) || offset > selected_profile->input_bytes ||
      size > selected_profile->input_bytes - offset) {
    latch_fault_locked();
    return DAL_FAILURE;
  }
  if (size == 0u) return DAL_SUCCESS;
  uint8_t frame[2];
  write_le16(frame, state.read_latch);
  memcpy(data, frame + offset, size);
  return DAL_SUCCESS;
}

static int32_t adapter_read_bit(tDeviceId id, uint32_t task,
                                uint32_t bit_offset, uint8_t *data) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!ready_device(id) || !owns_read(task)) return DAL_FAILURE;
  if (bit_offset >= selected_profile->input_bits || data == NULL) {
    latch_fault_locked();
    return DAL_FAILURE;
  }
  *data = (uint8_t)((state.read_latch >> bit_offset) & 1u);
  return DAL_SUCCESS;
}

static int32_t adapter_read_bool(tDeviceId id, uint32_t task,
                                uint32_t bit_offset, bool *value) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!ready_device(id) || !owns_read(task)) return DAL_FAILURE;
  if (value == NULL || bit_offset >= selected_profile->input_bits) {
    latch_fault_locked();
    return DAL_FAILURE;
  }
  *value = ((state.read_latch >> bit_offset) & 1u) != 0u;
  return DAL_SUCCESS;
}

static int32_t adapter_read_end(tDeviceId id, uint32_t task) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!ready_device(id) || !owns_read(task))
    return DAL_FAILURE;
  state.read_active = false;
  state.read_owner_valid = false;
  return DAL_SUCCESS;
}

static int32_t adapter_diagnose(tDeviceId id, uint32_t buffer_size,
                                uint8_t *buffer, tBusState *bus_state) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!valid_device(id) || !state.initialized || bus_state == NULL ||
      (buffer_size != 0u && buffer == NULL))
    return DAL_FAILURE;
  if (buffer_size != 0u) memset(buffer, 0, buffer_size);
  /* Own model fault visibility; not claimed as original-provider behavior. */
  *bus_state = state.fault_latched ? BusState_BusFault
                 : state.opened && state.configured ? BusState_BusOk
                                                    : BusState_NotEnabled;
  return DAL_SUCCESS;
}

static int32_t adapter_diagnose_subdevice(tDeviceId id, int32_t subdevice,
                                          size_t buffer_size, uint8_t *buffer,
                                          tDiagnoseState *diagnose_state) {
  STATE_GUARD;
  refresh_watchdog_locked();
  (void)id;
  (void)subdevice;
  (void)buffer_size;
  (void)buffer;
  (void)diagnose_state;
  return DAL_FAILURE;
}

static int32_t adapter_register_event(tDeviceId id, tEventHandler handler,
                                      void *user_data) {
  STATE_GUARD;
  refresh_watchdog_locked();
  (void)id;
  (void)handler;
  (void)user_data;
  return DAL_FAILURE;
}

static int32_t adapter_unregister_event(tDeviceId id, tEventHandler handler) {
  STATE_GUARD;
  refresh_watchdog_locked();
  (void)id;
  (void)handler;
  return DAL_FAILURE;
}

static int32_t adapter_last_error(tDeviceId id, tError *error) {
  STATE_GUARD;
  refresh_watchdog_locked();
  (void)id;
  (void)error;
  return DAL_FAILURE;
}

static int32_t adapter_app_state(tApplicationStateChangedEvent event) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!state.initialized || event.State < ApplicationState_BASE ||
      event.State >= ApplicationState_TOP)
    return DAL_FAILURE;
  bool running = event.State == ApplicationState_Running;
  if (state.write_active && state.app_running != running)
    state.write_failed = true;
  state.app_running = running;
  if (!effective_permit()) state.effective_outputs = 0u;
  if (!effective_permit() && state.write_active) state.write_failed = true;
  return DAL_SUCCESS;
}

static int32_t inner_terminal_info(uint32_t capacity, void *records,
                                   void *count_out) {
  if (records == NULL || count_out == NULL) return 1;
  const uint32_t count = selected_profile->terminal_count;
  const uint32_t needed = count * (uint32_t)sizeof(tKBUS_TERMINAL_INFO_32);
  *(uint32_t *)count_out = count;
  if (capacity < needed) return 2;
  tKBUS_TERMINAL_INFO_32 model[2];
  model[0].ulOffsetInput_bits = 0u;
  model[0].ulOffsetOutput_bits = 0u;
  model[0].ulSizeInput_bits = selected_profile->input_bits;
  model[0].ulSizeOutput_bits = 0u;
  model[1].ulOffsetInput_bits = selected_profile->profile ==
                                        VIRTUAL_ADI_PROFILE_DIGITAL8_DI8_DO8
                                    ? 0u
                                    : selected_profile->input_bits;
  model[1].ulOffsetOutput_bits = 0u;
  model[1].ulSizeInput_bits = 0u;
  model[1].ulSizeOutput_bits = selected_profile->output_bits;
  memcpy(records, model, needed);
  if (capacity > needed) memset((uint8_t *)records + needed, 0, capacity - needed);
  return 0;
}

static int32_t device_specific(const char *name, void *return_value,
                               va_list args) {
  if (name == NULL) {
    if (state.initialized) latch_fault_locked();
    return DAL_NOTUSED;
  }
  if (strcmp(name, LIBPACKBUS_DAL_FUNCTION_PUSH) == 0) {
    if (!state.initialized) return DAL_FAILURE;
    if (return_value == NULL) {
      latch_fault_locked();
      return DAL_FAILURE;
    }
    /* Original Kbus checks Push's outer and inner results. Make an own latched
     * operation fault observable there even when it discarded WriteEnd status.
     */
    *(int32_t *)return_value = state.fault_latched ? DAL_FAILURE : DAL_SUCCESS;
    return DAL_SUCCESS;
  }
  if (strcmp(name, LIBPACKBUS_DAL_FUNC_GET_TERMINAL_INFO_32) == 0) {
    if (!state.initialized) return DAL_FAILURE;
    if (return_value == NULL) {
      latch_fault_locked();
      return DAL_FAILURE;
    }
    uint32_t capacity = va_arg(args, uint32_t);
    void *records = va_arg(args, void *);
    void *count = va_arg(args, void *);
    int32_t result = inner_terminal_info(capacity, records, count);
    if (result == 1) latch_fault_locked();
    *(int32_t *)return_value = result;
    return DAL_SUCCESS;
  }
  if (strcmp(name, LIBPACKBUS_DAL_FUNC_READ_TAB_9) == 0) {
    if (!state.initialized) return DAL_FAILURE;
    if (return_value == NULL) {
      latch_fault_locked();
      return DAL_FAILURE;
    }
    int terminal = va_arg(args, int); /* uint8_t is promoted to int */
    uint16_t *module_id = va_arg(args, uint16_t *);
    int32_t result = -1;
    if (terminal >= 1 &&
        terminal <= (int)selected_profile->terminal_count) {
      if (module_id == NULL) {
        result = -2;
      } else {
        *module_id = selected_profile->module_ids[terminal - 1];
        result = 0;
      }
    }
    if (result != 0) latch_fault_locked();
    *(int32_t *)return_value = result;
    return DAL_SUCCESS;
  }
  if (strcmp(name, LIBPACKBUS_DAL_FUNC_GET_UID) == 0 ||
      strcmp(name, LIBPACKBUS_DAL_FUNC_READ_CONF_REG) == 0) {
    if (!state.initialized) return DAL_FAILURE;
    if (return_value == NULL) {
      latch_fault_locked();
      return DAL_FAILURE;
    }
    latch_fault_locked();
    *(int32_t *)return_value = -1; /* Explicitly unsupported by this model. */
    return DAL_SUCCESS;
  }
  if (state.initialized) latch_fault_locked();
  return DAL_NOTUSED;
}

static int32_t adapter_call_device_specific(const char *name, void *ret,
                                           ...) {
  STATE_GUARD;
  refresh_watchdog_locked();
  va_list args;
  va_start(args, ret);
  int32_t result = device_specific(name, ret, args);
  va_end(args);
  return result;
}

static int32_t adapter_vcall_device_specific(const char *name, void *ret,
                                             va_list args) {
  STATE_GUARD;
  refresh_watchdog_locked();
  return device_specific(name, ret, args);
}

static int32_t adapter_watchdog_set_time(uint32_t factor, uint32_t timeout_us) {
  STATE_GUARD;
  refresh_watchdog_locked();
  uint64_t period = (uint64_t)factor * (uint64_t)timeout_us;
  if (!state.initialized || factor == 0u || timeout_us == 0u ||
      period > 0x3fffffffu)
    return DAL_FAILURE;
  state.watchdog_period_us = period;
  state.watchdog_configured = true;
  return DAL_SUCCESS;
}

static int32_t adapter_watchdog_start(void) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!state.initialized || !state.watchdog_configured ||
      state.watchdog_started)
    return DAL_FAILURE;
  uint64_t now = current_time_us();
  if (now == UINT64_MAX) return DAL_FAILURE;
  state.watchdog_started = true;
  state.watchdog_healthy = false;
  state.watchdog_deadline_us = now;
  state.effective_outputs = 0;
  if (state.write_active) state.write_failed = true;
  return DAL_SUCCESS;
}

static int32_t adapter_watchdog_stop(void) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!state.initialized) return DAL_FAILURE;
  state.watchdog_started = false;
  state.watchdog_healthy = false;
  state.effective_outputs = 0;
  if (state.write_active) state.write_failed = true;
  return DAL_SUCCESS;
}

static int32_t adapter_watchdog_trigger(void) {
  STATE_GUARD;
  refresh_watchdog_locked();
  uint64_t now = current_time_us();
  if (!state.initialized || !state.watchdog_started ||
      !state.watchdog_configured ||
      state.watchdog_period_us > UINT64_MAX - now)
    return DAL_FAILURE;
  state.watchdog_healthy = true;
  state.watchdog_deadline_us = now + state.watchdog_period_us;
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
