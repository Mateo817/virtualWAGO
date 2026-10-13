#ifndef VIRTUALWAGO_ADI_MODEL_BRIDGE_H
#define VIRTUALWAGO_ADI_MODEL_BRIDGE_H

#include <stdbool.h>
#include <stdint.h>

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
  uint16_t inputs;
  uint16_t requested_outputs;
  uint16_t effective_outputs;
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
