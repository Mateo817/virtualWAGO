/*
 * Own, in-memory ADI model. Compile against the genuine private ADI and
 * libpackbus headers supplied by the caller; no vendor declarations are copied.
 */
#ifndef VIRTUALWAGO_ADI_DIGITAL_ADAPTER_H
#define VIRTUALWAGO_ADI_DIGITAL_ADAPTER_H

#include <stdint.h>
#include <dal/adi_application_interface.h>

#define VIRTUAL_ADI_MAX_FRAME_BYTES 256u

/* Own model profiles; neither value identifies a physical terminal. */
typedef enum {
  VIRTUAL_ADI_PROFILE_DIGITAL16 = 0,
  VIRTUAL_ADI_PROFILE_DIGITAL8_DI8_DO8 = 1,
  VIRTUAL_ADI_PROFILE_ANALOG466_AO550 = 2,
  VIRTUAL_ADI_PROFILE_PWM677 = 3
} virtual_adi_profile;

typedef enum {
  VIRTUAL_ADI_CLOCK_LOGICAL = 0,
  VIRTUAL_ADI_CLOCK_MONOTONIC = 1
} virtual_adi_clock_mode;

/* Own extension API; these are not WAGO ADI functions. */
/* Profile selection is accepted only before Init. Runtime builds may select a
 * reviewed default with exactly one of VIRTUALWAGO_DEFAULT_PROFILE8,
 * VIRTUALWAGO_DEFAULT_ANALOG466_AO550, or VIRTUALWAGO_DEFAULT_PWM677; unset
 * means DIGITAL16.
 */
int32_t virtual_adi_select_profile(virtual_adi_profile profile);
/* Clock mode can also be selected only before Init. Logical time is the
 * default unless VIRTUALWAGO_DEFAULT_CLOCK_MONOTONIC is explicitly compiled.
 */
int32_t virtual_adi_select_clock_mode(virtual_adi_clock_mode mode);
int32_t virtual_adi_set_inputs(uint16_t input_bits);
/* Own model IPC hook: accepts one complete frame for the exact current
 * profile and lifecycle generation. Result codes are model-local, not DAL ABI.
 */
typedef enum {
  VIRTUAL_ADI_FRAME_ACCEPTED = 0,
  VIRTUAL_ADI_FRAME_NOT_READY = 1,
  VIRTUAL_ADI_FRAME_PROFILE_MISMATCH = 2,
  VIRTUAL_ADI_FRAME_GENERATION_MISMATCH = 3,
  VIRTUAL_ADI_FRAME_LENGTH_MISMATCH = 4,
  VIRTUAL_ADI_FRAME_NULL_DATA = 5
} virtual_adi_frame_result;
int32_t virtual_adi_set_input_frame(virtual_adi_profile profile,
                                    uint64_t generation, uint32_t length,
                                    const uint8_t *bytes);
const char *virtual_adi_profile_name(virtual_adi_profile profile);
int32_t virtual_adi_set_permit(bool permit);
int32_t virtual_adi_set_application_state(tApplicationState state);
/* Advances the model-only monotonic clock; no wall clock is consulted. */
int32_t virtual_adi_advance_time_us(uint64_t elapsed_us);
int32_t virtual_adi_get_outputs(uint16_t *requested, uint16_t *effective);
void virtual_adi_reset(void);

#ifdef VIRTUALWAGO_TEST_PROFILE_EXTENTS
/* Compiled only in dedicated native test builds; absent from runtime builds. */
int32_t virtual_adi_test_select_extents(uint32_t input_bytes,
                                        uint32_t output_bytes);
#endif

#endif
