#ifndef VIRTUALWAGO_ADI_MODEL_BRIDGE_H
#define VIRTUALWAGO_ADI_MODEL_BRIDGE_H

#include <stdbool.h>
#include <stdint.h>

#ifndef VIRTUAL_ADI_MAX_FRAME_BYTES
#define VIRTUAL_ADI_MAX_FRAME_BYTES 256u
#endif

/* Private model snapshot shared by this bridge and the owning adapter.
 * This is an own extension, not a DAL/CODESYS structure or ABI declaration.
 */
typedef struct virtual_model_snapshot {
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
  uint32_t profile_id;
  uint32_t input_bytes;
  uint32_t output_bytes;
  uint32_t input_bits;
  uint32_t output_bits;
  uint8_t input_signals[VIRTUAL_ADI_MAX_FRAME_BYTES];
  uint8_t read_latch[VIRTUAL_ADI_MAX_FRAME_BYTES];
  uint8_t requested_outputs[VIRTUAL_ADI_MAX_FRAME_BYTES];
  uint8_t staged_outputs[VIRTUAL_ADI_MAX_FRAME_BYTES];
  uint8_t staged_coverage[VIRTUAL_ADI_MAX_FRAME_BYTES];
  uint8_t effective_outputs[VIRTUAL_ADI_MAX_FRAME_BYTES];
  uint64_t generation;
  uint64_t frame_count;
} virtual_model_snapshot;

/* Owner-adapter hooks. The adapter implements these under its own state lock. */
int32_t virtual_adi_model_snapshot(virtual_model_snapshot *snapshot);
int32_t virtual_adi_latch_fault(void);

/* Start is idempotent. With no VIRTUALWAGO_MODEL_SOCKET environment variable,
 * it returns success without creating a worker. When compiled without
 * VIRTUALWAGO_ENABLE_MODEL_BRIDGE these functions are inert stubs.
 */
int virtual_model_bridge_start(void);
void virtual_model_bridge_stop(void);

#endif
