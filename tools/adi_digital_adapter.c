#define _GNU_SOURCE

/* Own bounded byte-frame ADI model for the explicitly supported digital
 * profiles. This is neither byte-identical DAL behavior nor a hardware/backend.
 */
#include "adi_digital_adapter.h"
#ifdef VIRTUALWAGO_ENABLE_MODEL_BRIDGE
#include "adi_model_bridge.h"
#endif

#include <limits.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <time.h>
#include <libpackbus.h>
#include "adi_catalog_profiles.h"
#include "adi_virtual_integration_profiles.h"

#define VIRTUAL_DEVICE_ID ((tDeviceId)1)
#define VIRTUAL_DEVICE_NAME "libpackbus"
#if (defined(VIRTUALWAGO_DEFAULT_PROFILE8) + \
     defined(VIRTUALWAGO_DEFAULT_ANALOG466_AO550) + \
     defined(VIRTUALWAGO_DEFAULT_PWM677)) > 1
#error "Select at most one non-DI16 default ADI profile"
#endif
#if defined(VIRTUALWAGO_DEFAULT_PROFILE8)
static const virtual_adi_profile default_profile =
    VIRTUAL_ADI_PROFILE_DIGITAL8_DI8_DO8;
#elif defined(VIRTUALWAGO_DEFAULT_ANALOG466_AO550)
static const virtual_adi_profile default_profile =
    VIRTUAL_ADI_PROFILE_ANALOG466_AO550;
#elif defined(VIRTUALWAGO_DEFAULT_PWM677)
static const virtual_adi_profile default_profile = VIRTUAL_ADI_PROFILE_PWM677;
#else
static const virtual_adi_profile default_profile = VIRTUAL_ADI_PROFILE_DIGITAL16;
#endif
#ifdef VIRTUALWAGO_DEFAULT_CLOCK_MONOTONIC
static const virtual_adi_clock_mode default_clock_mode =
    VIRTUAL_ADI_CLOCK_MONOTONIC;
#else
static const virtual_adi_clock_mode default_clock_mode =
    VIRTUAL_ADI_CLOCK_LOGICAL;
#endif
typedef struct {
  virtual_adi_profile profile;
  const char *name;
  uint32_t input_bytes;
  uint32_t output_bytes;
  uint32_t input_bits;
  uint32_t output_bits;
  uint16_t input_mask;
  uint16_t output_mask;
  uint32_t terminal_count;
  uint16_t module_ids[2];
  uint32_t input_offsets_bits[2];
  uint32_t output_offsets_bits[2];
  uint32_t terminal_input_bits[2];
  uint32_t terminal_output_bits[2];
  uint16_t register16;
  uint16_t register29;
  uint16_t register30;
  bool supports_legacy_word;
  bool integration_profile;
} virtual_profile_view;

static virtual_profile_view selected_profile;
static bool selected_profile_valid;
#ifdef VIRTUALWAGO_TEST_PROFILE_EXTENTS
static virtual_profile_view test_profile;
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
  uint8_t input_signals[VIRTUAL_ADI_MAX_FRAME_BYTES];
  uint8_t read_latch[VIRTUAL_ADI_MAX_FRAME_BYTES];
  uint8_t requested_outputs[VIRTUAL_ADI_MAX_FRAME_BYTES];
  uint8_t staged_outputs[VIRTUAL_ADI_MAX_FRAME_BYTES];
  uint8_t staged_coverage[VIRTUAL_ADI_MAX_FRAME_BYTES];
  uint8_t effective_outputs[VIRTUAL_ADI_MAX_FRAME_BYTES];
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

#ifdef VIRTUALWAGO_ADI_TRACE
static unsigned trace_init_count, trace_sizes_count, trace_terminal_count;
static unsigned trace_table9_count, trace_confreg_count, trace_unknown_count;
static unsigned trace_uid_count;
static unsigned trace_read_count, trace_write_count;
#define TRACE_UNKNOWN_NAME_MAX 96u
static bool trace_safe_unknown_name(const char *name) {
  if (name == NULL) return false;
  size_t length = strnlen(name, TRACE_UNKNOWN_NAME_MAX + 1u);
  if (length == 0u || length > TRACE_UNKNOWN_NAME_MAX) return false;
  for (size_t i = 0u; i < length; ++i) {
    unsigned char byte = (unsigned char)name[i];
    bool alpha = (byte >= 'A' && byte <= 'Z') ||
                 (byte >= 'a' && byte <= 'z');
    if (i == 0u) {
      if (!alpha && byte != '_') return false;
    } else if (!alpha && !(byte >= '0' && byte <= '9') && byte != '_') {
      return false;
    }
  }
  return true;
}
static void trace_unknown_call(const char *name) {
  if (trace_unknown_count >= 8u) return;
  ++trace_unknown_count;
  fprintf(stderr,
          "VIRTUAL_ADI_TRACE unknown_op profile=%s outer=%d "
          "inner=not_written "
          "a=0 b=0 name=%s\n",
          selected_profile_valid ? selected_profile.name : "unselected",
          DAL_NOTUSED,
          trace_safe_unknown_name(name) ? name : "<redacted>");
}
static void trace_event(unsigned *count, const char *event, const char *profile,
                        int32_t outer, int32_t inner, uint32_t first,
                        uint32_t second) {
  if (*count >= 8u) return;
  ++*count;
  fprintf(stderr, "VIRTUAL_ADI_TRACE %s profile=%s outer=%d inner=%d a=%u b=%u\n",
          event, profile != NULL ? profile : "unselected", outer, inner,
          first, second);
}
#define TRACE_EVENT(counter, event, outer, inner, first, second) \
  trace_event(&(counter), (event), selected_profile_valid ? \
              selected_profile.name : NULL, (outer), (inner), (first), (second))
#define TRACE_UNKNOWN_CALL(name) trace_unknown_call(name)
#else
#define TRACE_EVENT(counter, event, outer, inner, first, second) \
  ((void)0)
#define TRACE_UNKNOWN_CALL(name) ((void)0)
#endif

static void clear_frame(uint8_t frame[VIRTUAL_ADI_MAX_FRAME_BYTES]);
static void clear_effective_outputs(void);

static const virtual_adi_integration_profile *integration_profile_for(
    virtual_adi_profile profile) {
  switch (profile) {
    case VIRTUAL_ADI_PROFILE_ANALOG466_AO550: return &profile_analog466_550;
    case VIRTUAL_ADI_PROFILE_PWM677: return &profile_pwm677;
    default: return NULL;
  }
}

static void activate_profile(virtual_adi_profile profile) {
  memset(&selected_profile, 0, sizeof(selected_profile));
  selected_profile.profile = profile;
  const virtual_profile_data *digital = NULL;
  if (profile == VIRTUAL_ADI_PROFILE_DIGITAL16)
    digital = &profile_digital16;
  else if (profile == VIRTUAL_ADI_PROFILE_DIGITAL8_DI8_DO8)
    digital = &profile_digital8;
  if (digital != NULL) {
    selected_profile.name = profile == VIRTUAL_ADI_PROFILE_DIGITAL16
                                ? "DI16" : "DI8";
    selected_profile.input_bytes = digital->input_bytes;
    selected_profile.output_bytes = digital->output_bytes;
    selected_profile.input_bits = digital->input_bits;
    selected_profile.output_bits = digital->output_bits;
    selected_profile.input_mask = digital->input_mask;
    selected_profile.output_mask = digital->output_mask;
    selected_profile.terminal_count = digital->terminal_count;
    memcpy(selected_profile.module_ids, digital->module_ids,
           sizeof(selected_profile.module_ids));
    memcpy(selected_profile.input_offsets_bits, digital->input_offsets_bits,
           sizeof(selected_profile.input_offsets_bits));
    memcpy(selected_profile.output_offsets_bits, digital->output_offsets_bits,
           sizeof(selected_profile.output_offsets_bits));
    selected_profile.terminal_input_bits[0] = digital->input_bits;
    selected_profile.terminal_output_bits[1] = digital->output_bits;
    selected_profile.supports_legacy_word = true;
    selected_profile_valid = true;
    return;
  }
  const virtual_adi_integration_profile *integration =
      integration_profile_for(profile);
  if (integration == NULL) {
    selected_profile_valid = false;
    return;
  }
  selected_profile.name = integration->name;
  selected_profile.input_bytes = integration->input_bytes;
  selected_profile.output_bytes = integration->output_bytes;
  selected_profile.input_bits = integration->input_bits;
  selected_profile.output_bits = integration->output_bits;
  selected_profile.terminal_count = integration->terminal_count;
  memcpy(selected_profile.module_ids, integration->module_ids,
         sizeof(selected_profile.module_ids));
  memcpy(selected_profile.input_offsets_bits,
         integration->input_offsets_bits,
         sizeof(selected_profile.input_offsets_bits));
  memcpy(selected_profile.output_offsets_bits,
         integration->output_offsets_bits,
         sizeof(selected_profile.output_offsets_bits));
  memcpy(selected_profile.terminal_input_bits,
         integration->terminal_input_bits,
         sizeof(selected_profile.terminal_input_bits));
  memcpy(selected_profile.terminal_output_bits,
         integration->terminal_output_bits,
         sizeof(selected_profile.terminal_output_bits));
  selected_profile.register16 = integration->register16;
  selected_profile.register29 = integration->register29;
  selected_profile.register30 = integration->register30;
  selected_profile.integration_profile = true;
  selected_profile_valid = true;
}

static bool ensure_profile_selected(void) {
  if (!selected_profile_valid) activate_profile(default_profile);
  return selected_profile_valid;
}

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
    clear_effective_outputs();
    if (state.write_active) state.write_failed = true;
  }
}

static bool valid_device(tDeviceId id) { return id == VIRTUAL_DEVICE_ID; }
static bool ready_device(tDeviceId id) {
  return valid_device(id) && state.initialized && state.opened &&
         state.configured;
}
static void clear_frame(uint8_t frame[VIRTUAL_ADI_MAX_FRAME_BYTES]) {
  memset(frame, 0, VIRTUAL_ADI_MAX_FRAME_BYTES);
}
static uint16_t frame_to_u16(const uint8_t *frame, uint32_t length) {
  uint16_t value = 0u;
  if (length > 0u) value = frame[0];
  if (length > 1u) value |= (uint16_t)((uint16_t)frame[1] << 8u);
  return value;
}
static void u16_to_frame(uint8_t *frame, uint32_t length, uint16_t value) {
  if (length > 0u) frame[0] = (uint8_t)value;
  if (length > 1u) frame[1] = (uint8_t)(value >> 8u);
}
static bool frame_is_fully_covered(const uint8_t *coverage, uint32_t bytes,
                                   uint32_t bits) {
  for (uint32_t i = 0u; i < bytes; ++i) {
    uint32_t remaining = bits > i * 8u ? bits - i * 8u : 0u;
    uint8_t expected = remaining >= 8u
                           ? UINT8_MAX
                           : (uint8_t)((1u << remaining) - 1u);
    if ((coverage[i] & expected) != expected) return false;
  }
  return true;
}
static bool profile_extent_valid(const virtual_profile_view *profile) {
  if (profile == NULL || profile->input_bytes == 0u ||
      profile->output_bytes == 0u || profile->input_bits == 0u ||
      profile->output_bits == 0u ||
      profile->input_bytes > VIRTUAL_ADI_MAX_FRAME_BYTES ||
      profile->output_bytes > VIRTUAL_ADI_MAX_FRAME_BYTES ||
      profile->input_bits != profile->input_bytes * 8u ||
      profile->output_bits != profile->output_bytes * 8u ||
      profile->terminal_count == 0u || profile->terminal_count > 2u)
    return false;
  uint32_t input_covered = 0u, output_covered = 0u;
  for (uint32_t i = 0u; i < profile->terminal_count; ++i) {
    if (profile->input_offsets_bits[i] > profile->input_bits ||
        profile->terminal_input_bits[i] >
            profile->input_bits - profile->input_offsets_bits[i] ||
        profile->output_offsets_bits[i] > profile->output_bits ||
        profile->terminal_output_bits[i] >
            profile->output_bits - profile->output_offsets_bits[i])
      return false;
    input_covered += profile->terminal_input_bits[i];
    output_covered += profile->terminal_output_bits[i];
  }
  return input_covered == profile->input_bits &&
         output_covered == profile->output_bits;
}
static void clear_effective_outputs(void) {
  clear_frame(state.effective_outputs);
}
static bool effective_permit(void) {
  return state.app_running && state.permit && state.watchdog_healthy &&
         !state.fault_latched;
}

static void latch_fault_locked(void) {
  state.fault_latched = true;
  clear_effective_outputs();
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
  if (snapshot == NULL || !ensure_profile_selected() ||
      !profile_extent_valid(&selected_profile)) return DAL_FAILURE;
  memset(snapshot, 0, sizeof(*snapshot));
  snapshot->initialized = state.initialized;
  snapshot->opened = state.opened;
  snapshot->configured = state.configured;
  snapshot->app_running = state.app_running;
  snapshot->permit = state.permit;
  snapshot->watchdog_healthy = state.watchdog_healthy;
  snapshot->fault_latched = state.fault_latched;
  snapshot->read_active = state.read_active;
  snapshot->write_active = state.write_active;
  snapshot->write_failed = state.write_failed;
  snapshot->profile_id = (uint32_t)selected_profile.profile;
  snapshot->input_bytes = selected_profile.input_bytes;
  snapshot->output_bytes = selected_profile.output_bytes;
  snapshot->input_bits = selected_profile.input_bits;
  snapshot->output_bits = selected_profile.output_bits;
  memcpy(snapshot->input_signals, state.input_signals,
         selected_profile.input_bytes);
  memcpy(snapshot->read_latch, state.read_latch,
         selected_profile.input_bytes);
  memcpy(snapshot->requested_outputs, state.requested_outputs,
         selected_profile.output_bytes);
  memcpy(snapshot->staged_outputs, state.staged_outputs,
         selected_profile.output_bytes);
  memcpy(snapshot->staged_coverage, state.staged_coverage,
         selected_profile.output_bytes);
  memcpy(snapshot->effective_outputs, state.effective_outputs,
         selected_profile.output_bytes);
  snapshot->generation = lifecycle_generation;
  snapshot->frame_count = state.frame_count;
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
  activate_profile(default_profile);
  selected_clock_mode = default_clock_mode;
}

#ifdef VIRTUALWAGO_TEST_PROFILE_EXTENTS
int32_t virtual_adi_test_select_extents(uint32_t input_bytes,
                                        uint32_t output_bytes) {
  STATE_GUARD;
  if (state.initialized || input_bytes == 0u || output_bytes == 0u ||
      input_bytes > VIRTUAL_ADI_MAX_FRAME_BYTES ||
      output_bytes > VIRTUAL_ADI_MAX_FRAME_BYTES) return DAL_FAILURE;
  activate_profile(VIRTUAL_ADI_PROFILE_DIGITAL16);
  test_profile = selected_profile;
  test_profile.input_bytes = input_bytes;
  test_profile.output_bytes = output_bytes;
  test_profile.input_bits = input_bytes * 8u;
  test_profile.output_bits = output_bytes * 8u;
  test_profile.input_offsets_bits[0] = 0u;
  test_profile.input_offsets_bits[1] = 0u;
  test_profile.output_offsets_bits[0] = 0u;
  test_profile.output_offsets_bits[1] = 0u;
  test_profile.terminal_input_bits[0] = test_profile.input_bits;
  test_profile.terminal_output_bits[1] = test_profile.output_bits;
  selected_profile = test_profile;
  selected_profile_valid = true;
  return DAL_SUCCESS;
}
#endif

int32_t virtual_adi_select_profile(virtual_adi_profile profile) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (state.initialized) return DAL_FAILURE;
  if (profile != VIRTUAL_ADI_PROFILE_DIGITAL16 &&
      profile != VIRTUAL_ADI_PROFILE_DIGITAL8_DI8_DO8 &&
      integration_profile_for(profile) == NULL)
    return DAL_FAILURE;
  activate_profile(profile);
  if (!selected_profile_valid || !profile_extent_valid(&selected_profile))
    return DAL_FAILURE;
  return DAL_SUCCESS;
}

int32_t virtual_adi_select_clock_mode(virtual_adi_clock_mode mode) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (state.initialized) return DAL_FAILURE;
  if (!ensure_profile_selected() ||
      !profile_extent_valid(&selected_profile)) return DAL_FAILURE;
  if (mode != VIRTUAL_ADI_CLOCK_LOGICAL &&
      mode != VIRTUAL_ADI_CLOCK_MONOTONIC)
    return DAL_FAILURE;
  selected_clock_mode = mode;
  return DAL_SUCCESS;
}

int32_t virtual_adi_set_inputs(uint16_t input_bits) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!state.initialized || !ensure_profile_selected() ||
      !selected_profile.supports_legacy_word) return DAL_FAILURE;
  clear_frame(state.input_signals);
  u16_to_frame(state.input_signals, selected_profile.input_bytes,
               (uint16_t)(input_bits & selected_profile.input_mask));
  return DAL_SUCCESS;
}

int32_t virtual_adi_set_input_frame(virtual_adi_profile profile,
                                    uint64_t generation, uint32_t length,
                                    const uint8_t *bytes) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!state.initialized || !ensure_profile_selected())
    return VIRTUAL_ADI_FRAME_NOT_READY;
  if (profile != selected_profile.profile)
    return VIRTUAL_ADI_FRAME_PROFILE_MISMATCH;
  if (generation != lifecycle_generation)
    return VIRTUAL_ADI_FRAME_GENERATION_MISMATCH;
  if (length != selected_profile.input_bytes)
    return VIRTUAL_ADI_FRAME_LENGTH_MISMATCH;
  if (length != 0u && bytes == NULL) return VIRTUAL_ADI_FRAME_NULL_DATA;
  clear_frame(state.input_signals);
  memcpy(state.input_signals, bytes, length);
  return VIRTUAL_ADI_FRAME_ACCEPTED;
}

const char *virtual_adi_profile_name(virtual_adi_profile profile) {
  switch (profile) {
    case VIRTUAL_ADI_PROFILE_DIGITAL8_DI8_DO8: return "DI8";
    case VIRTUAL_ADI_PROFILE_DIGITAL16: return "DI16";
    case VIRTUAL_ADI_PROFILE_ANALOG466_AO550: return "AI466_AO550";
    case VIRTUAL_ADI_PROFILE_PWM677: return "PWM677";
    default: return NULL;
  }
}

int32_t virtual_adi_set_permit(bool permit) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!state.initialized) return DAL_FAILURE;
  if (state.write_active && state.permit != permit) state.write_failed = true;
  state.permit = permit;
  if (!effective_permit()) clear_effective_outputs();
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
  if (!effective_permit()) clear_effective_outputs();
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
  if (requested == NULL || effective == NULL || !ensure_profile_selected() ||
      !selected_profile.supports_legacy_word) return DAL_FAILURE;
  *requested = frame_to_u16(state.requested_outputs,
                            selected_profile.output_bytes);
  *effective = frame_to_u16(state.effective_outputs,
                            selected_profile.output_bytes);
  return DAL_SUCCESS;
}

static int32_t adapter_init(void) {
#ifdef VIRTUALWAGO_ENABLE_MODEL_BRIDGE
  LIFECYCLE_GUARD;
#endif
  STATE_GUARD;
  refresh_watchdog_locked();
  if (state.initialized) {
    TRACE_EVENT(trace_init_count, "init", DAL_FAILURE, DAL_FAILURE, 0u, 0u);
    return DAL_FAILURE;
  }
  if (!ensure_profile_selected() ||
      !profile_extent_valid(&selected_profile)) {
    TRACE_EVENT(trace_init_count, "init", DAL_FAILURE, DAL_FAILURE, 0u, 0u);
    return DAL_FAILURE;
  }
#ifdef VIRTUALWAGO_ENABLE_MODEL_BRIDGE
  if (virtual_model_bridge_start() != 0) {
    TRACE_EVENT(trace_init_count, "init", DAL_FAILURE, DAL_FAILURE, 0u, 0u);
    return DAL_FAILURE;
  }
#endif
  memset(&state, 0, sizeof(state));
  bump_lifecycle_generation();
  state.initialized = true;
  /* Fail-closed model defaults; not claimed as vendor policy. */
  state.watchdog_healthy = false;
  TRACE_EVENT(trace_init_count, "init", DAL_SUCCESS, DAL_SUCCESS,
              selected_profile.input_bytes, selected_profile.output_bytes);
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
  clear_frame(state.input_signals);
  clear_frame(state.read_latch);
  clear_frame(state.requested_outputs);
  clear_frame(state.staged_outputs);
  clear_frame(state.staged_coverage);
  clear_effective_outputs();
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
  if (!ensure_profile_selected() || !valid_device(id) || !state.initialized || input == NULL ||
      output == NULL)
    { TRACE_EVENT(trace_sizes_count, "get_iosizes", DAL_FAILURE, DAL_FAILURE,
                  0u, 0u); return DAL_FAILURE; }
  *input = selected_profile.input_bytes;
  *output = selected_profile.output_bytes;
  TRACE_EVENT(trace_sizes_count, "get_iosizes", DAL_SUCCESS, DAL_SUCCESS,
              *input, *output);
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
  memcpy(state.staged_outputs, state.requested_outputs,
         selected_profile.output_bytes);
  memset(state.staged_coverage, 0, sizeof(state.staged_coverage));
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
  if (!ready_device(id) || !owns_write(task)) {
    TRACE_EVENT(trace_write_count, "write_bytes", DAL_FAILURE, DAL_FAILURE,
                offset, size); return DAL_FAILURE;
  }
  if ((size != 0u && data == NULL) ||
      offset > selected_profile.output_bytes ||
      size > selected_profile.output_bytes - offset) {
    latch_fault_locked();
    TRACE_EVENT(trace_write_count, "write_bytes", DAL_FAILURE, DAL_FAILURE,
                offset, size);
    return DAL_FAILURE;
  }
  if (size == 0u) {
    TRACE_EVENT(trace_write_count, "write_bytes", DAL_SUCCESS, DAL_SUCCESS,
                offset, size); return DAL_SUCCESS;
  }
  memcpy(state.staged_outputs + offset, data, size);
  memset(state.staged_coverage + offset, UINT8_MAX, size);
  TRACE_EVENT(trace_write_count, "write_bytes", DAL_SUCCESS, DAL_SUCCESS,
              offset, size);
  return DAL_SUCCESS;
}

static int32_t adapter_write_bit(tDeviceId id, uint32_t task,
                                 uint32_t bit_offset, uint8_t *data) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!ready_device(id) || !owns_write(task)) {
    TRACE_EVENT(trace_write_count, "write_bit", DAL_FAILURE, DAL_FAILURE,
                bit_offset, 1u); return DAL_FAILURE;
  }
  if (bit_offset >= selected_profile.output_bits || data == NULL) {
    latch_fault_locked();
    TRACE_EVENT(trace_write_count, "write_bit", DAL_FAILURE, DAL_FAILURE,
                bit_offset, 1u);
    return DAL_FAILURE;
  }
  const uint32_t byte_index = bit_offset / 8u;
  const uint8_t mask = (uint8_t)(1u << (bit_offset % 8u));
  if ((*data & 1u) != 0u)
    state.staged_outputs[byte_index] |= mask;
  else
    state.staged_outputs[byte_index] &= (uint8_t)~mask;
  state.staged_coverage[byte_index] |= mask;
  TRACE_EVENT(trace_write_count, "write_bit", DAL_SUCCESS, DAL_SUCCESS,
              bit_offset, 1u);
  return DAL_SUCCESS;
}

static int32_t adapter_write_bool(tDeviceId id, uint32_t task,
                                 uint32_t bit_offset, bool value) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!ready_device(id) || !owns_write(task)) {
    TRACE_EVENT(trace_write_count, "write_bool", DAL_FAILURE, DAL_FAILURE,
                bit_offset, 1u); return DAL_FAILURE;
  }
  if (bit_offset >= selected_profile.output_bits) {
    latch_fault_locked();
    TRACE_EVENT(trace_write_count, "write_bool", DAL_FAILURE, DAL_FAILURE,
                bit_offset, 1u);
    return DAL_FAILURE;
  }
  const uint32_t byte_index = bit_offset / 8u;
  const uint8_t mask = (uint8_t)(1u << (bit_offset % 8u));
  if (value)
    state.staged_outputs[byte_index] |= mask;
  else
    state.staged_outputs[byte_index] &= (uint8_t)~mask;
  state.staged_coverage[byte_index] |= mask;
  TRACE_EVENT(trace_write_count, "write_bool", DAL_SUCCESS, DAL_SUCCESS,
              bit_offset, 1u);
  return DAL_SUCCESS;
}

static int32_t adapter_write_end(tDeviceId id, uint32_t task) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!ready_device(id) || !owns_write(task))
    return DAL_FAILURE;
  if (state.write_failed ||
      !frame_is_fully_covered(state.staged_coverage,
                              selected_profile.output_bytes,
                              selected_profile.output_bits)) {
    if (!state.write_failed) latch_fault_locked();
    state.write_active = false;
    state.write_owner_valid = false;
    state.write_failed = false;
    memcpy(state.staged_outputs, state.requested_outputs,
           selected_profile.output_bytes);
    memset(state.staged_coverage, 0, sizeof(state.staged_coverage));
    return DAL_FAILURE;
  }
  memcpy(state.requested_outputs, state.staged_outputs,
         selected_profile.output_bytes);
  if (state.frame_count != UINT64_MAX) ++state.frame_count;
  if (effective_permit())
    memcpy(state.effective_outputs, state.staged_outputs,
           selected_profile.output_bytes);
  else
    clear_effective_outputs();
  state.write_active = false;
  state.write_owner_valid = false;
  state.write_failed = false;
  memset(state.staged_coverage, 0, sizeof(state.staged_coverage));
  return DAL_SUCCESS;
}

static int32_t adapter_read_start(tDeviceId id, uint32_t task) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!ready_device(id) || task != 0u || state.read_active) return DAL_FAILURE;
  memcpy(state.read_latch, state.input_signals,
         selected_profile.input_bytes);
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
  if (!ready_device(id) || !owns_read(task)) {
    TRACE_EVENT(trace_read_count, "read_bytes", DAL_FAILURE, DAL_FAILURE,
                offset, size); return DAL_FAILURE;
  }
  if ((size != 0u && data == NULL) || offset > selected_profile.input_bytes ||
      size > selected_profile.input_bytes - offset) {
    latch_fault_locked();
    TRACE_EVENT(trace_read_count, "read_bytes", DAL_FAILURE, DAL_FAILURE,
                offset, size);
    return DAL_FAILURE;
  }
  if (size == 0u) {
    TRACE_EVENT(trace_read_count, "read_bytes", DAL_SUCCESS, DAL_SUCCESS,
                offset, size); return DAL_SUCCESS;
  }
  memcpy(data, state.read_latch + offset, size);
  TRACE_EVENT(trace_read_count, "read_bytes", DAL_SUCCESS, DAL_SUCCESS,
              offset, size);
  return DAL_SUCCESS;
}

static int32_t adapter_read_bit(tDeviceId id, uint32_t task,
                                uint32_t bit_offset, uint8_t *data) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!ready_device(id) || !owns_read(task)) {
    TRACE_EVENT(trace_read_count, "read_bit", DAL_FAILURE, DAL_FAILURE,
                bit_offset, 1u); return DAL_FAILURE;
  }
  if (bit_offset >= selected_profile.input_bits || data == NULL) {
    latch_fault_locked();
    TRACE_EVENT(trace_read_count, "read_bit", DAL_FAILURE, DAL_FAILURE,
                bit_offset, 1u);
    return DAL_FAILURE;
  }
  *data = (uint8_t)((state.read_latch[bit_offset / 8u] >>
                     (bit_offset % 8u)) & 1u);
  TRACE_EVENT(trace_read_count, "read_bit", DAL_SUCCESS, DAL_SUCCESS,
              bit_offset, 1u);
  return DAL_SUCCESS;
}

static int32_t adapter_read_bool(tDeviceId id, uint32_t task,
                                uint32_t bit_offset, bool *value) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!ready_device(id) || !owns_read(task)) {
    TRACE_EVENT(trace_read_count, "read_bool", DAL_FAILURE, DAL_FAILURE,
                bit_offset, 1u); return DAL_FAILURE;
  }
  if (value == NULL || bit_offset >= selected_profile.input_bits) {
    latch_fault_locked();
    TRACE_EVENT(trace_read_count, "read_bool", DAL_FAILURE, DAL_FAILURE,
                bit_offset, 1u);
    return DAL_FAILURE;
  }
  *value = ((state.read_latch[bit_offset / 8u] >>
             (bit_offset % 8u)) & 1u) != 0u;
  TRACE_EVENT(trace_read_count, "read_bool", DAL_SUCCESS, DAL_SUCCESS,
              bit_offset, 1u);
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
  if (!effective_permit()) clear_effective_outputs();
  if (!effective_permit() && state.write_active) state.write_failed = true;
  return DAL_SUCCESS;
}

static int32_t inner_terminal_info(uint32_t capacity, void *records,
                                   void *count_out) {
  if (records == NULL || count_out == NULL) return 1;
  const uint32_t count = selected_profile.terminal_count;
  const uint32_t needed = count * (uint32_t)sizeof(tKBUS_TERMINAL_INFO_32);
  *(uint32_t *)count_out = count;
  if (capacity < needed) return 2;
  tKBUS_TERMINAL_INFO_32 model[2];
  memset(model, 0, sizeof(model));
  for (uint32_t i = 0u; i < count; ++i) {
    model[i].ulOffsetInput_bits = selected_profile.input_offsets_bits[i];
    model[i].ulOffsetOutput_bits = selected_profile.output_offsets_bits[i];
    model[i].ulSizeInput_bits = selected_profile.terminal_input_bits[i];
    model[i].ulSizeOutput_bits = selected_profile.terminal_output_bits[i];
  }
  memcpy(records, model, needed);
  if (capacity > needed) memset((uint8_t *)records + needed, 0, capacity - needed);
  return 0;
}

static int32_t device_specific(const char *name, void *return_value,
                               va_list args) {
  if (name == NULL) {
    if (state.initialized) latch_fault_locked();
    TRACE_UNKNOWN_CALL(name);
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
    TRACE_EVENT(trace_terminal_count, "terminal_info", DAL_SUCCESS, result,
                selected_profile.terminal_count, capacity);
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
        terminal <= (int)selected_profile.terminal_count) {
      if (module_id == NULL) {
        result = -2; /* FW31 read_table_9 inner NULL result. */
      } else {
        *module_id = selected_profile.module_ids[terminal - 1];
        result = 0;
      }
    }
    if (result != 0) latch_fault_locked();
    *(int32_t *)return_value = result;
    TRACE_EVENT(trace_table9_count, "table9", DAL_SUCCESS, result,
                terminal < 0 ? 0u : (uint32_t)terminal,
                selected_profile.terminal_count);
    return DAL_SUCCESS;
  }
  if (strcmp(name, LIBPACKBUS_DAL_FUNC_READ_CONF_REG) == 0) {
    if (!state.initialized) return DAL_FAILURE;
    if (return_value == NULL) {
      latch_fault_locked();
      return DAL_FAILURE;
    }
    int terminal = va_arg(args, int); /* uint8_t is promoted to int */
    int register_id = va_arg(args, int); /* uint8_t is promoted to int */
    uint16_t *value = va_arg(args, uint16_t *);
    int32_t result;
    if (terminal < 1 || terminal > (int)selected_profile.terminal_count)
      result = -1;
    else if (value == NULL)
      result = -3;
    else if (!selected_profile.integration_profile ||
             (register_id != 16 && register_id != 29 && register_id != 30))
      result = -2;
    else {
      *value = register_id == 16 ? selected_profile.register16
               : register_id == 29 ? selected_profile.register29
                                   : selected_profile.register30;
      result = 0;
    }
    if (result != 0) latch_fault_locked();
    *(int32_t *)return_value = result;
    TRACE_EVENT(trace_confreg_count, "read_conf_reg", DAL_SUCCESS, result,
                terminal < 0 ? 0u : (uint32_t)terminal,
                register_id < 0 ? 0u : (uint32_t)register_id);
    return DAL_SUCCESS;
  }
  if (strcmp(name, LIBPACKBUS_DAL_FUNC_GET_UID) == 0) {
    if (!state.initialized) return DAL_FAILURE;
    if (return_value == NULL) {
      latch_fault_locked();
      return DAL_FAILURE;
    }
    latch_fault_locked();
    *(int32_t *)return_value = -1; /* Own explicit unsupported UID response. */
    TRACE_EVENT(trace_uid_count, "get_uid", DAL_SUCCESS,
                *(int32_t *)return_value, 0u, 0u);
    return DAL_SUCCESS;
  }
  if (state.initialized) latch_fault_locked();
  TRACE_UNKNOWN_CALL(name);
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
  clear_effective_outputs();
  if (state.write_active) state.write_failed = true;
  return DAL_SUCCESS;
}

static int32_t adapter_watchdog_stop(void) {
  STATE_GUARD;
  refresh_watchdog_locked();
  if (!state.initialized) return DAL_FAILURE;
  state.watchdog_started = false;
  state.watchdog_healthy = false;
  clear_effective_outputs();
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
