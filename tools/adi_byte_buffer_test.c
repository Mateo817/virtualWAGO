/* Own generalized byte-buffer harness. It is built only with the test-only
 * extent selector and the authentic private ADI headers. This is not a vendor
 * consumer, original runtime, backend, or hardware test.
 */
#include "adi_digital_adapter.h"
#include "adi_model_bridge.h"
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
#include <libpackbus.h>

static void run_extent(tApplicationDeviceInterface *adi, uint32_t bytes) {
  uint8_t source[VIRTUAL_ADI_MAX_FRAME_BYTES];
  uint8_t replacement[VIRTUAL_ADI_MAX_FRAME_BYTES];
  uint8_t observed[VIRTUAL_ADI_MAX_FRAME_BYTES];
  uint8_t outputs[VIRTUAL_ADI_MAX_FRAME_BYTES];
  for (uint32_t i = 0; i < bytes; ++i) {
    source[i] = (uint8_t)(i * 37u + 11u);
    replacement[i] = (uint8_t)~source[i];
    outputs[i] = (uint8_t)(i * 19u + 3u);
  }
  assert(virtual_adi_test_select_extents(bytes, bytes) == DAL_SUCCESS);
  assert(adi->Init() == DAL_SUCCESS);
  assert(adi->OpenDevice(1) == DAL_SUCCESS);
  tCONFIGURE_DEVICE config = {0};
  config.eStructType = TCF_SSC_CONF_STRUCT_3;
  assert(adi->ConfigureDevice(1, &config) == DAL_SUCCESS);
  virtual_model_snapshot snapshot;
  assert(virtual_adi_model_snapshot(&snapshot) == DAL_SUCCESS);
  assert(snapshot.input_bytes == bytes && snapshot.output_bytes == bytes);
  assert(virtual_adi_set_input_frame(VIRTUAL_ADI_PROFILE_DIGITAL16,
                                     snapshot.generation, bytes - 1u, source) ==
         VIRTUAL_ADI_FRAME_LENGTH_MISMATCH);
  assert(virtual_adi_set_input_frame(VIRTUAL_ADI_PROFILE_DIGITAL8_DI8_DO8,
                                     snapshot.generation, bytes, source) ==
         VIRTUAL_ADI_FRAME_PROFILE_MISMATCH);
  assert(virtual_adi_set_input_frame(VIRTUAL_ADI_PROFILE_DIGITAL16,
                                     snapshot.generation - 1u, bytes, source) ==
         VIRTUAL_ADI_FRAME_GENERATION_MISMATCH);
  assert(virtual_adi_set_input_frame(VIRTUAL_ADI_PROFILE_DIGITAL16,
                                     snapshot.generation, bytes, NULL) ==
         VIRTUAL_ADI_FRAME_NULL_DATA);
  assert(virtual_adi_set_input_frame(VIRTUAL_ADI_PROFILE_DIGITAL16,
                                     snapshot.generation, bytes, source) ==
         VIRTUAL_ADI_FRAME_ACCEPTED);

  assert(adi->ReadStart(1, 0) == DAL_SUCCESS);
  assert(virtual_adi_set_input_frame(VIRTUAL_ADI_PROFILE_DIGITAL16,
                                     snapshot.generation, bytes, replacement) ==
         VIRTUAL_ADI_FRAME_ACCEPTED);
  memset(observed, 0, sizeof(observed));
  uint32_t split = bytes / 2u;
  assert(adi->ReadBytes(1, 0, 0, split, observed) == DAL_SUCCESS);
  assert(adi->ReadBytes(1, 0, split, bytes - split, observed + split) == DAL_SUCCESS);
  assert(memcmp(source, observed, bytes) == 0);
  uint8_t bit = 0xffu;
  assert(adi->ReadBit(1, 0, 0, &bit) == DAL_SUCCESS);
  assert(bit == (uint8_t)(source[0] & 1u));
  assert(adi->ReadBit(1, 0, bytes * 8u - 1u, &bit) == DAL_SUCCESS);
  assert(bit == (uint8_t)((source[bytes - 1u] >> 7u) & 1u));
  assert(adi->ReadBytes(1, 0, bytes, 0, NULL) == DAL_SUCCESS);
  assert(adi->ReadEnd(1, 0) == DAL_SUCCESS);

  assert(adi->WriteStart(1, 0) == DAL_SUCCESS);
  assert(adi->WriteBytes(1, 0, 0, split, outputs) == DAL_SUCCESS);
  assert(adi->WriteBytes(1, 0, split, bytes - split, outputs + split) == DAL_SUCCESS);
  assert(adi->WriteBytes(1, 0, bytes, 0, NULL) == DAL_SUCCESS);
  assert(adi->WriteEnd(1, 0) == DAL_SUCCESS);
  assert(virtual_adi_model_snapshot(&snapshot) == DAL_SUCCESS);
  assert(memcmp(snapshot.requested_outputs, outputs, bytes) == 0);
  assert(snapshot.frame_count == 1u);

  /* A complete mixed WriteBit/WriteBool transaction covers every bit. */
  assert(adi->WriteStart(1, 0) == DAL_SUCCESS);
  for (uint32_t bit_index = 0u; bit_index < bytes * 8u; ++bit_index) {
    uint8_t value = (uint8_t)((outputs[bit_index / 8u] >> (bit_index % 8u)) & 1u);
    if ((bit_index & 1u) == 0u)
      assert(adi->WriteBit(1, 0, bit_index, &value) == DAL_SUCCESS);
    else
      assert(adi->WriteBool(1, 0, bit_index, value != 0u) == DAL_SUCCESS);
  }
  assert(virtual_adi_model_snapshot(&snapshot) == DAL_SUCCESS);
  for (uint32_t i = 0u; i < bytes; ++i)
    assert(snapshot.staged_coverage[i] == UINT8_MAX);
  assert(adi->WriteEnd(1, 0) == DAL_SUCCESS);
  assert(virtual_adi_model_snapshot(&snapshot) == DAL_SUCCESS);
  assert(snapshot.frame_count == 2u);
  assert(memcmp(snapshot.requested_outputs, outputs, bytes) == 0);

  assert(adi->WriteStart(1, 0) == DAL_SUCCESS);
  /* Leave exactly the final output bit uncovered. */
  for (uint32_t bit_index = 0u; bit_index < bytes * 8u - 1u; ++bit_index) {
    uint8_t value = (uint8_t)((source[bit_index / 8u] >> (bit_index % 8u)) & 1u);
    if ((bit_index & 1u) == 0u)
      assert(adi->WriteBit(1, 0, bit_index, &value) == DAL_SUCCESS);
    else
      assert(adi->WriteBool(1, 0, bit_index, value != 0u) == DAL_SUCCESS);
  }
  assert(virtual_adi_model_snapshot(&snapshot) == DAL_SUCCESS);
  for (uint32_t i = 0u; i + 1u < bytes; ++i)
    assert(snapshot.staged_coverage[i] == UINT8_MAX);
  assert(snapshot.staged_coverage[bytes - 1u] == 0x7fu);
  assert(adi->WriteEnd(1, 0) == DAL_FAILURE);
  assert(virtual_adi_model_snapshot(&snapshot) == DAL_SUCCESS);
  assert(snapshot.fault_latched);
  assert(snapshot.frame_count == 2u);
  assert(memcmp(snapshot.requested_outputs, outputs, bytes) == 0);
  assert(adi->ConfigureDevice(1, &config) == DAL_SUCCESS);

  assert(adi->WriteStart(1, 0) == DAL_SUCCESS);
  assert(adi->WriteBytes(1, 0, UINT32_MAX, 1, source) == DAL_FAILURE);
  assert(adi->WriteEnd(1, 0) == DAL_FAILURE);
  assert(adi->ConfigureDevice(1, &config) == DAL_SUCCESS);
  assert(adi->WriteStart(1, 0) == DAL_SUCCESS);
  assert(adi->WriteBytes(1, 0, bytes + 1u, 0, NULL) == DAL_FAILURE);
  assert(adi->WriteEnd(1, 0) == DAL_FAILURE);
  assert(adi->ConfigureDevice(1, &config) == DAL_SUCCESS);
  assert(adi->CloseDevice(1) == DAL_SUCCESS);
  assert(adi->Exit() == DAL_SUCCESS);
}

int main(void) {
  tApplicationDeviceInterface *adi = adi_GetApplicationInterface();
  const uint32_t extents[] = {1u, 2u, 4u, 16u, 256u};
  for (size_t i = 0; i < sizeof(extents) / sizeof(extents[0]); ++i) {
    virtual_adi_reset();
    run_extent(adi, extents[i]);
  }
  virtual_adi_reset();
  assert(virtual_adi_test_select_extents(257u, 1u) == DAL_FAILURE);
  puts("ADI byte buffer harness: PASS (own test-profile adapter only)");
  return 0;
}
