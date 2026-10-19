/* Own adapter/bridge integration profiles only; never an original consumer. */
#define _GNU_SOURCE
#include "adi_digital_adapter.h"
#include "adi_model_bridge.h"

#include <assert.h>
#include <errno.h>
#include <stddef.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/un.h>
#include <time.h>
#include <unistd.h>
#include <libpackbus.h>

static void command(int fd, const char *request, const char *expected_prefix) {
  size_t length = strlen(request);
  assert(send(fd, request, length, MSG_NOSIGNAL) == (ssize_t)length);
  char reply[4097];
  ssize_t received = recv(fd, reply, sizeof(reply) - 1u, 0);
  assert(received > 0);
  reply[received] = '\0';
  assert(strncmp(reply, expected_prefix, strlen(expected_prefix)) == 0);
}

static int connect_bridge(const char *path) {
  int fd = socket(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0);
  assert(fd >= 0);
  struct timeval timeout = {2, 0};
  assert(setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)) == 0);
  struct sockaddr_un address = {.sun_family = AF_UNIX};
  assert(strlen(path) < sizeof(address.sun_path));
  strcpy(address.sun_path, path);
  assert(connect(fd, (struct sockaddr *)&address,
                 (socklen_t)(offsetof(struct sockaddr_un, sun_path) +
                             strlen(path) + 1u)) == 0);
  return fd;
}

static void call_register(tApplicationDeviceInterface *adi, int slot,
                          int register_id, uint16_t *value,
                          int32_t expected_inner) {
  int32_t inner = 99;
  assert(adi->CallDeviceSpecificFunction(LIBPACKBUS_DAL_FUNC_READ_CONF_REG,
                                         &inner, slot, register_id, value) ==
         DAL_SUCCESS);
  assert(inner == expected_inner);
}

static int32_t call_register_v(tApplicationDeviceInterface *adi, int32_t *inner,
                               ...) {
  va_list arguments;
  va_start(arguments, inner);
  int32_t outer = adi->VCallDeviceSpecificFunction(
      LIBPACKBUS_DAL_FUNC_READ_CONF_REG, inner, arguments);
  va_end(arguments);
  return outer;
}

static void test_profile(tApplicationDeviceInterface *adi,
                         virtual_adi_profile profile, const char *name,
                         uint32_t input_bytes, uint32_t output_bytes,
                         uint32_t terminal_count, const uint16_t *module_ids,
                         const uint32_t *terminal_input_bits,
                         const uint32_t *terminal_output_bits) {
  char directory[] = "/tmp/adi-native-profile-XXXXXX";
  assert(mkdtemp(directory) != NULL && chmod(directory, 0700) == 0);
  char path[108];
  assert(snprintf(path, sizeof(path), "%s/model.sock", directory) > 0);
  assert(setenv("VIRTUALWAGO_MODEL_SOCKET", path, 1) == 0);

  virtual_adi_reset();
  assert(virtual_adi_select_profile(profile) == DAL_SUCCESS);
  assert(virtual_adi_select_profile((virtual_adi_profile)99) == DAL_FAILURE);
  assert(adi->Init() == DAL_SUCCESS);
  assert(adi->OpenDevice(1) == DAL_SUCCESS);
  tCONFIGURE_DEVICE config = {0};
  config.eStructType = TCF_SSC_CONF_STRUCT_3;
  assert(adi->ConfigureDevice(1, &config) == DAL_SUCCESS);

  uint32_t input_size = 0, output_size = 0;
  assert(adi->GetIoSizes(1, &input_size, &output_size) == DAL_SUCCESS);
  assert(input_size == input_bytes && output_size == output_bytes);

  int32_t inner = 99;
  uint32_t count = 0;
  tKBUS_TERMINAL_INFO_32 records[2];
  memset(records, 0xa5, sizeof(records));
  assert(adi->CallDeviceSpecificFunction(
             LIBPACKBUS_DAL_FUNC_GET_TERMINAL_INFO_32, &inner,
             (uint32_t)(terminal_count * sizeof(records[0])), records,
             &count) == DAL_SUCCESS);
  assert(inner == 0 && count == terminal_count);
  for (uint32_t i = 0; i < terminal_count; ++i) {
    assert(records[i].ulOffsetInput_bits == 0u);
    assert(records[i].ulOffsetOutput_bits == 0u);
    assert(records[i].ulSizeInput_bits == terminal_input_bits[i]);
    assert(records[i].ulSizeOutput_bits == terminal_output_bits[i]);
  }
  memset(records, 0xa5, sizeof(records));
  inner = 99;
  assert(adi->CallDeviceSpecificFunction(
             LIBPACKBUS_DAL_FUNC_GET_TERMINAL_INFO_32, &inner, 0u, records,
             &count) == DAL_SUCCESS);
  assert(inner == 2 && count == terminal_count &&
         ((const uint8_t *)records)[0] == 0xa5u);

  uint16_t module_id = 0u;
  for (uint32_t i = 0; i < terminal_count; ++i) {
    inner = 99;
    assert(adi->CallDeviceSpecificFunction(LIBPACKBUS_DAL_FUNC_READ_TAB_9,
                                           &inner, (int)(i + 1u),
                                           &module_id) == DAL_SUCCESS);
    assert(inner == 0 && module_id == module_ids[i]);
  }
  inner = 99;
  assert(adi->CallDeviceSpecificFunction(LIBPACKBUS_DAL_FUNC_READ_TAB_9,
                                         &inner, 0, &module_id) == DAL_SUCCESS);
  assert(inner == -1);
  inner = 99;
  assert(adi->CallDeviceSpecificFunction(LIBPACKBUS_DAL_FUNC_READ_TAB_9,
                                         &inner, 1, (uint16_t *)NULL) ==
         DAL_SUCCESS);
  assert(inner == -2); /* Bound FW31 Table9 NULL result. */

  uint16_t register_value = 0xffffu;
  call_register(adi, 0, 16, &register_value, -1);
  call_register(adi, (int)terminal_count + 1, 16, &register_value, -1);
  call_register(adi, 1, 28, &register_value, -2);
  call_register(adi, 1, 16, NULL, -3);
  for (uint32_t slot = 1u; slot <= terminal_count; ++slot) {
    for (int register_id = 16; register_id <= 30; ++register_id) {
      if (register_id != 16 && register_id != 29 && register_id != 30) continue;
      register_value = 0xffffu;
      call_register(adi, (int)slot, register_id, &register_value, 0);
      assert(register_value == 0u); /* Explicit own virtual policy. */
    }
  }
  register_value = 0xffffu;
  inner = 99;
  assert(call_register_v(adi, &inner, 1, 16, &register_value) == DAL_SUCCESS);
  assert(inner == 0 && register_value == 0u);
  uint16_t uid = 0xbeefu;
  inner = 99;
  assert(adi->CallDeviceSpecificFunction(LIBPACKBUS_DAL_FUNC_GET_UID, &inner,
                                         1, &uid) == DAL_SUCCESS);
  assert(inner == -1 && uid == 0xbeefu);
  inner = 99;
  assert(adi->CallDeviceSpecificFunction("UNSUPPORTED_PRIVATE_OP", &inner) ==
         DAL_NOTUSED);
  assert(adi->ConfigureDevice(1, &config) == DAL_SUCCESS);
  assert(virtual_adi_set_inputs(0xffffu) == DAL_FAILURE);
  assert(virtual_adi_get_outputs(&register_value, &register_value) ==
         DAL_FAILURE);
  inner = 0x1234;
  assert(adi->CallDeviceSpecificFunction("DAL_capabilityProbe7", &inner) ==
         DAL_NOTUSED);
  assert(inner == 0x1234);
  inner = 0x5678;
  assert(adi->CallDeviceSpecificFunction("UNSUPPORTED PRIVATE_OP", &inner) ==
         DAL_NOTUSED);
  assert(inner == 0x5678);

  virtual_model_snapshot snapshot;
  assert(virtual_adi_model_snapshot(&snapshot) == DAL_SUCCESS);
  assert(snapshot.profile_id == (uint32_t)profile);
  int fd = connect_bridge(path);
  command(fd, "STATUS", "ERR PROFILE");
  command(fd, "INPUT 65535", "ERR PROFILE");
  char request[600];
  snprintf(request, sizeof(request), "V2 STATUS %s", name);
  command(fd, "V2 STATUS", request);
  uint8_t input[input_bytes], output[output_bytes];
  char frame_hex[VIRTUAL_ADI_MAX_FRAME_BYTES * 2u + 1u];
  static const char hex[] = "0123456789abcdef";
  for (uint32_t i = 0u; i < input_bytes; ++i) {
    input[i] = (uint8_t)(0x31u + i);
    frame_hex[i * 2u] = hex[input[i] >> 4u];
    frame_hex[i * 2u + 1u] = hex[input[i] & 0x0fu];
  }
  frame_hex[input_bytes * 2u] = '\0';
  assert(snprintf(request, sizeof(request), "V2 INPUT %s %llu %u %s", name,
                  (unsigned long long)snapshot.generation, input_bytes,
                  frame_hex) > 0);
  command(fd, request, "OK FRAME");
  snprintf(request, sizeof(request), "V2 INPUT %s %llu %u %s", name,
           (unsigned long long)(snapshot.generation - 1u), input_bytes,
           frame_hex);
  command(fd, request, "ERR GENERATION");
  snprintf(request, sizeof(request), "V2 INPUT %s %llu %u %s", name,
           (unsigned long long)snapshot.generation, input_bytes - 1u,
           frame_hex);
  command(fd, request, "ERR FRAME");
  assert(virtual_adi_model_snapshot(&snapshot) == DAL_SUCCESS);
  assert(memcmp(snapshot.input_signals, input, input_bytes) == 0);

  assert(adi->ReadStart(1, 0u) == DAL_SUCCESS);
  assert(virtual_adi_set_input_frame(profile, snapshot.generation,
                                     input_bytes, input) ==
         VIRTUAL_ADI_FRAME_ACCEPTED);
  memset(output, 0, sizeof(output));
  assert(adi->ReadBytes(1, 0u, 0u, input_bytes, output) == DAL_SUCCESS);
  assert(memcmp(output, input, input_bytes) == 0);
  assert(adi->ReadEnd(1, 0u) == DAL_SUCCESS);
  uint8_t replacement[input_bytes];
  memset(replacement, 0xe7, sizeof(replacement));
  assert(virtual_adi_set_input_frame(profile, snapshot.generation,
                                     input_bytes - 1u, replacement) ==
         VIRTUAL_ADI_FRAME_LENGTH_MISMATCH);
  assert(virtual_adi_set_input_frame(VIRTUAL_ADI_PROFILE_DIGITAL16,
                                     snapshot.generation, input_bytes, input) ==
         VIRTUAL_ADI_FRAME_PROFILE_MISMATCH);
  assert(virtual_adi_set_input_frame(profile, snapshot.generation,
                                     input_bytes, NULL) ==
         VIRTUAL_ADI_FRAME_NULL_DATA);
  assert(virtual_adi_model_snapshot(&snapshot) == DAL_SUCCESS);
  assert(memcmp(snapshot.input_signals, input, input_bytes) == 0);

  for (uint32_t i = 0u; i < output_bytes; ++i) output[i] = (uint8_t)(0xc0u + i);
  assert(adi->WriteStart(1, 0u) == DAL_SUCCESS);
  uint32_t byte_prefix = output_bytes / 2u;
  assert(adi->WriteBytes(1, 0u, 0u, byte_prefix, output) == DAL_SUCCESS);
  for (uint32_t byte = byte_prefix; byte < output_bytes; ++byte) {
    for (uint32_t bit = 0u; bit < 8u; ++bit) {
      uint32_t bit_offset = byte * 8u + bit;
      uint8_t bit_value = (uint8_t)((output[byte] >> bit) & 1u);
      if ((bit_offset & 1u) == 0u)
        assert(adi->WriteBit(1, 0u, bit_offset, &bit_value) == DAL_SUCCESS);
      else
        assert(adi->WriteBool(1, 0u, bit_offset, bit_value != 0u) == DAL_SUCCESS);
    }
  }
  assert(adi->WriteEnd(1, 0u) == DAL_SUCCESS);
  assert(virtual_adi_model_snapshot(&snapshot) == DAL_SUCCESS);
  assert(memcmp(snapshot.requested_outputs, output, output_bytes) == 0);
  for (uint32_t i = 0u; i < output_bytes; ++i)
    assert(snapshot.effective_outputs[i] == 0u);
  close(fd);
  assert(adi->CloseDevice(1) == DAL_SUCCESS);
  assert(adi->Exit() == DAL_SUCCESS);
  assert(access(path, F_OK) != 0);
  assert(rmdir(directory) == 0);
}

int main(void) {
  tApplicationDeviceInterface *adi = adi_GetApplicationInterface();
  assert(adi != NULL);
  static const uint16_t analog_ids[] = {0x01d2u, 0x0226u};
  static const uint32_t analog_input[] = {32u, 0u};
  static const uint32_t analog_output[] = {0u, 32u};
  static const uint16_t pwm_ids[] = {0x02a5u};
  static const uint32_t pwm_input[] = {128u};
  static const uint32_t pwm_output[] = {128u};
  test_profile(adi, VIRTUAL_ADI_PROFILE_ANALOG466_AO550, "AI466_AO550",
               4u, 4u, 2u, analog_ids, analog_input, analog_output);
  test_profile(adi, VIRTUAL_ADI_PROFILE_PWM677, "PWM677", 16u, 16u, 1u,
               pwm_ids, pwm_input, pwm_output);
  puts("ADI_NATIVE_INTEGRATION_PROFILE_TEST: PASS (own adapter/bridge only)");
  return 0;
}
