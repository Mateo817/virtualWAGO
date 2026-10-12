/*
 * Own, in-memory ADI model. Compile against the genuine private ADI and
 * libpackbus headers supplied by the caller; no vendor declarations are copied.
 */
#ifndef VIRTUALWAGO_ADI_DIGITAL_ADAPTER_H
#define VIRTUALWAGO_ADI_DIGITAL_ADAPTER_H

#include <stdint.h>
#include <dal/adi_application_interface.h>

/* Own extension API; these are not WAGO ADI functions. */
int32_t virtual_adi_set_inputs(uint16_t input_bits);
int32_t virtual_adi_set_permit(bool permit);
int32_t virtual_adi_set_application_state(tApplicationState state);
/* Advances the model-only monotonic clock; no wall clock is consulted. */
int32_t virtual_adi_advance_time_us(uint64_t elapsed_us);
int32_t virtual_adi_get_outputs(uint16_t *requested, uint16_t *effective);
void virtual_adi_reset(void);

#endif
