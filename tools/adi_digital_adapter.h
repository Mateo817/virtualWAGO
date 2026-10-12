/*
 * Own, in-memory ADI model. Compile against the genuine private ADI and
 * libpackbus headers supplied by the caller; no vendor declarations are copied.
 */
#ifndef VIRTUALWAGO_ADI_DIGITAL_ADAPTER_H
#define VIRTUALWAGO_ADI_DIGITAL_ADAPTER_H

#include <stdint.h>
#include <dal/adi_application_interface.h>

/* Own model profiles; neither value identifies a physical terminal. */
typedef enum {
  VIRTUAL_ADI_PROFILE_DIGITAL16 = 0,
  VIRTUAL_ADI_PROFILE_DIGITAL8_DI8_DO8 = 1
} virtual_adi_profile;

typedef enum {
  VIRTUAL_ADI_CLOCK_LOGICAL = 0,
  VIRTUAL_ADI_CLOCK_MONOTONIC = 1
} virtual_adi_clock_mode;

/* Own extension API; these are not WAGO ADI functions. */
/* Profile selection is accepted only before Init. Runtime builds may select a
 * reviewed default with VIRTUALWAGO_DEFAULT_PROFILE8; unset means DIGITAL16.
 */
int32_t virtual_adi_select_profile(virtual_adi_profile profile);
/* Clock mode can also be selected only before Init. Logical time is the
 * default unless VIRTUALWAGO_DEFAULT_CLOCK_MONOTONIC is explicitly compiled.
 */
int32_t virtual_adi_select_clock_mode(virtual_adi_clock_mode mode);
int32_t virtual_adi_set_inputs(uint16_t input_bits);
int32_t virtual_adi_set_permit(bool permit);
int32_t virtual_adi_set_application_state(tApplicationState state);
/* Advances the model-only monotonic clock; no wall clock is consulted. */
int32_t virtual_adi_advance_time_us(uint64_t elapsed_us);
int32_t virtual_adi_get_outputs(uint16_t *requested, uint16_t *effective);
void virtual_adi_reset(void);

#endif
