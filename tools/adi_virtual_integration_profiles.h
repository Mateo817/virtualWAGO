/* Own, explicitly pinned virtual integration profiles.  These descriptors are
 * not vendor structs, physical inventories, or hardware defaults. */
#ifndef VIRTUALWAGO_ADI_VIRTUAL_INTEGRATION_PROFILES_H
#define VIRTUALWAGO_ADI_VIRTUAL_INTEGRATION_PROFILES_H

#include "adi_digital_adapter.h"

typedef struct {
  virtual_adi_profile profile;
  const char *name;
  const char *descriptor_id;
  const char *descriptor_version;
  const char *descriptor_sha256;
  const char *parameter10;
  uint32_t input_bytes;
  uint32_t output_bytes;
  uint32_t input_bits;
  uint32_t output_bits;
  uint32_t terminal_count;
  uint16_t module_ids[2];
  uint32_t input_offsets_bits[2];
  uint32_t output_offsets_bits[2];
  uint32_t terminal_input_bits[2];
  uint32_t terminal_output_bits[2];
  uint16_t register16;
  uint16_t register29;
  uint16_t register30;
} virtual_adi_integration_profile;

/* The register values are this project's explicit virtual settings chosen to
 * satisfy the statically reviewed FW31 consumer predicates. They are not
 * observed factory defaults or a complete hardware register model. */
static const virtual_adi_integration_profile profile_analog466_550 = {
    .profile = VIRTUAL_ADI_PROFILE_ANALOG466_AO550,
    .name = "AI466_AO550",
    .descriptor_id = "07500466000000000400+07500550000000000004",
    .descriptor_version = "2.0.0.9+2.0.0.9",
    .descriptor_sha256 =
        "aa9bb802e2d2656ec9e101f1537aebc23f79487437513bdc9588f0d283ecca51+"
        "8edb68d2b02370398251890035552779fb1edce5e6d039c2d7312d26f6927105",
    .parameter10 = "000001D200000000+0000022600000000",
    .input_bytes = 4u,
    .output_bytes = 4u,
    .input_bits = 32u,
    .output_bits = 32u,
    .terminal_count = 2u,
    .module_ids = {0x01d2u, 0x0226u},
    .input_offsets_bits = {0u, 0u},
    .output_offsets_bits = {0u, 0u},
    .terminal_input_bits = {32u, 0u},
    .terminal_output_bits = {0u, 32u},
    .register16 = 0u,
    .register29 = 0u,
    .register30 = 0u,
};

static const virtual_adi_integration_profile profile_pwm677 = {
    .profile = VIRTUAL_ADI_PROFILE_PWM677,
    .name = "PWM677",
    .descriptor_id = "07500677000000001616",
    .descriptor_version = "2.0.0.3",
    .descriptor_sha256 =
        "15dcba17a7186fc3dd91fc2b47c806bf7016e6e0ebc949b352c9549f5124c780",
    .parameter10 = "000002A500000000",
    .input_bytes = 16u,
    .output_bytes = 16u,
    .input_bits = 128u,
    .output_bits = 128u,
    .terminal_count = 1u,
    .module_ids = {0x02a5u, 0u},
    .input_offsets_bits = {0u, 0u},
    .output_offsets_bits = {0u, 0u},
    .terminal_input_bits = {128u, 0u},
    .terminal_output_bits = {128u, 0u},
    .register16 = 0u,
    .register29 = 0u,
    .register30 = 0u,
};

#endif
