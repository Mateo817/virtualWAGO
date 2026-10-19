/*
 * Native transport-only test for adi_model_bridge.c.
 * The setter/snapshot hooks below are a test double for this IPC scope only;
 * this does not exercise the ADI adapter, CODESYS, Runtime, or hardware.
 * Build: cc -std=gnu11 -Wall -Wextra -Werror -pthread \
 *   -DVIRTUALWAGO_ENABLE_MODEL_BRIDGE -DADI_MODEL_BRIDGE_STANDALONE_TEST \
 *   tools/adi_model_bridge.c tools/adi_model_bridge_test.c -o bridge-test
 */
#define _GNU_SOURCE

#include "adi_model_bridge.h"

typedef enum {
  VIRTUAL_ADI_PROFILE_DIGITAL16 = 0,
  VIRTUAL_ADI_PROFILE_DIGITAL8_DI8_DO8 = 1
} virtual_adi_profile;

#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <pthread.h>
#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/time.h>
#include <sys/un.h>
#include <time.h>
#include <unistd.h>

#define TEST_ENV "VIRTUALWAGO_MODEL_SOCKET"

static pthread_mutex_t test_mutex = PTHREAD_MUTEX_INITIALIZER;
static virtual_model_snapshot test_state;
static unsigned appstate_setter_calls;

static void check(bool condition, const char *message) {
  if (!condition) {
    fprintf(stderr, "FAIL: %s\n", message);
    exit(1);
  }
}

int32_t virtual_adi_set_inputs(uint16_t input_bits) {
  pthread_mutex_lock(&test_mutex);
  if (!test_state.initialized) {
    pthread_mutex_unlock(&test_mutex);
    return -1;
  }
  test_state.input_bytes = 2u;
  test_state.input_bits = 16u;
  test_state.profile_id = 0u;
  test_state.input_signals[0] = (uint8_t)input_bits;
  test_state.input_signals[1] = (uint8_t)(input_bits >> 8u);
  pthread_mutex_unlock(&test_mutex);
  return 0;
}

int32_t virtual_adi_set_input_frame(virtual_adi_profile profile,
                                    uint64_t generation, uint32_t length,
                                    const uint8_t *bytes) {
  pthread_mutex_lock(&test_mutex);
  if (!test_state.initialized) { pthread_mutex_unlock(&test_mutex); return 1; }
  if (profile != (virtual_adi_profile)test_state.profile_id) {
    pthread_mutex_unlock(&test_mutex); return 2;
  }
  if (generation != test_state.generation) {
    pthread_mutex_unlock(&test_mutex); return 3;
  }
  if (length != test_state.input_bytes || (length != 0u && bytes == NULL)) {
    pthread_mutex_unlock(&test_mutex); return 4;
  }
  memcpy(test_state.input_signals, bytes, length);
  pthread_mutex_unlock(&test_mutex);
  return 0;
}

const char *virtual_adi_profile_name(virtual_adi_profile profile) {
  if (profile == VIRTUAL_ADI_PROFILE_DIGITAL8_DI8_DO8) return "DI8";
  if (profile == VIRTUAL_ADI_PROFILE_DIGITAL16) return "DI16";
  return NULL;
}

int32_t virtual_adi_set_permit(bool permit) {
  pthread_mutex_lock(&test_mutex);
  if (!test_state.initialized) {
    pthread_mutex_unlock(&test_mutex);
    return -1;
  }
  test_state.permit = permit;
  if (!permit || test_state.fault_latched || !test_state.app_running ||
      !test_state.watchdog_healthy)
    memset(test_state.effective_outputs, 0, sizeof(test_state.effective_outputs));
  pthread_mutex_unlock(&test_mutex);
  return 0;
}

int32_t virtual_adi_model_snapshot(virtual_model_snapshot *snapshot) {
  if (snapshot == NULL) return -1;
  pthread_mutex_lock(&test_mutex);
  *snapshot = test_state;
  pthread_mutex_unlock(&test_mutex);
  return 0;
}

int32_t virtual_adi_latch_fault(void) {
  pthread_mutex_lock(&test_mutex);
  if (!test_state.initialized) {
    pthread_mutex_unlock(&test_mutex);
    return -1;
  }
  test_state.fault_latched = true;
  memset(test_state.effective_outputs, 0, sizeof(test_state.effective_outputs));
  pthread_mutex_unlock(&test_mutex);
  return 0;
}

static void set_initialized(bool value) {
  pthread_mutex_lock(&test_mutex);
  test_state.initialized = value;
  if (value) {
    test_state.profile_id = 0u;
    test_state.input_bytes = test_state.output_bytes = 2u;
    test_state.input_bits = test_state.output_bits = 16u;
    test_state.generation = 17u;
  }
  pthread_mutex_unlock(&test_mutex);
}

static virtual_model_snapshot get_test_state(void) {
  virtual_model_snapshot result;
  pthread_mutex_lock(&test_mutex);
  result = test_state;
  pthread_mutex_unlock(&test_mutex);
  return result;
}

static int64_t now_ms(void) {
  struct timespec now;
  check(clock_gettime(CLOCK_MONOTONIC, &now) == 0, "clock_gettime failed");
  return (int64_t)now.tv_sec * 1000 + (int64_t)now.tv_nsec / 1000000;
}

static int connect_client(const char *path) {
  int fd = socket(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0);
  check(fd >= 0, "socket client creation failed");
  struct timeval timeout = {2, 0};
  check(setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)) == 0,
        "setting test receive timeout failed");
  struct sockaddr_un address;
  memset(&address, 0, sizeof(address));
  address.sun_family = AF_UNIX;
  check(strlen(path) < sizeof(address.sun_path), "test socket path too long");
  strcpy(address.sun_path, path);
  check(connect(fd, (struct sockaddr *)&address,
                (socklen_t)(offsetof(struct sockaddr_un, sun_path) + strlen(path) + 1u)) == 0,
        "client connect failed");
  return fd;
}

static void command(int fd, const char *request, const char *expected_prefix) {
  size_t length = strlen(request);
  check(send(fd, request, length, MSG_NOSIGNAL) == (ssize_t)length,
        "sending test packet failed");
  char response[1024];
  ssize_t received = recv(fd, response, sizeof(response) - 1u, 0);
  check(received > 0, "receiving test response failed");
  response[received] = '\0';
  check(strncmp(response, expected_prefix, strlen(expected_prefix)) == 0,
        response);
}

static void wait_permit_false(void) {
  int64_t deadline = now_ms() + 1000;
  while (now_ms() < deadline) {
    if (!get_test_state().permit) return;
    struct timespec pause = {0, 10000000L};
    nanosleep(&pause, NULL);
  }
  check(false, "connection loss did not revoke permit within bound");
}

static void make_private_dir(char *path, size_t capacity, const char *root) {
  check(strlen(root) + sizeof("/bridge-XXXXXX") < capacity,
        "test directory buffer too small");
  strcpy(path, root);
  strcat(path, "/bridge-XXXXXX");
  check(mkdtemp(path) != NULL, "mkdtemp failed");
  check(chmod(path, 0700) == 0, "chmod private test directory failed");
}

int main(void) {
  char root_template[] = "/tmp/adi-model-bridge-test-XXXXXX";
  char *test_root = mkdtemp(root_template);
  check(test_root != NULL, "mkdtemp root failed");
  check(chmod(test_root, 0700) == 0, "chmod root failed");

  unsetenv(TEST_ENV);
  check(virtual_model_bridge_start() == 0,
        "absent optional endpoint must leave bridge disabled");
  virtual_model_bridge_stop();

  char private_dir[sizeof(((struct sockaddr_un *)0)->sun_path)];
  make_private_dir(private_dir, sizeof(private_dir), test_root);
  char socket_path[sizeof(((struct sockaddr_un *)0)->sun_path)];
  check(snprintf(socket_path, sizeof(socket_path), "%s/model.sock", private_dir) > 0,
        "socket path formatting failed");

  char public_dir[sizeof(((struct sockaddr_un *)0)->sun_path)];
  make_private_dir(public_dir, sizeof(public_dir), test_root);
  check(chmod(public_dir, 0755) == 0, "chmod public test directory failed");
  char invalid_path[sizeof(((struct sockaddr_un *)0)->sun_path)];
  check(snprintf(invalid_path, sizeof(invalid_path), "%s/model.sock", public_dir) > 0,
        "invalid socket path formatting failed");
  check(setenv(TEST_ENV, invalid_path, 1) == 0, "setting invalid endpoint failed");
  check(virtual_model_bridge_start() != 0,
        "non-private containing directory must be rejected");
  check(access(invalid_path, F_OK) != 0 && errno == ENOENT,
        "failed setup unexpectedly created a socket");
  virtual_model_bridge_stop();

  char existing_path[sizeof(((struct sockaddr_un *)0)->sun_path)];
  check(snprintf(existing_path, sizeof(existing_path), "%s/existing.sock", private_dir) > 0,
        "existing path formatting failed");
  int existing_fd = open(existing_path, O_CREAT | O_EXCL | O_WRONLY | O_CLOEXEC, 0600);
  check(existing_fd >= 0, "creating existing-path sentinel failed");
  check(write(existing_fd, "preserve", 8u) == 8, "writing sentinel failed");
  close(existing_fd);
  check(setenv(TEST_ENV, existing_path, 1) == 0, "setting existing endpoint failed");
  check(virtual_model_bridge_start() != 0, "existing endpoint must be rejected");
  char sentinel[9] = {0};
  existing_fd = open(existing_path, O_RDONLY | O_CLOEXEC);
  check(existing_fd >= 0 && read(existing_fd, sentinel, 8u) == 8,
        "existing endpoint was removed or changed");
  close(existing_fd);
  check(strcmp(sentinel, "preserve") == 0, "existing endpoint bytes changed");
  virtual_model_bridge_stop();

  check(setenv(TEST_ENV, socket_path, 1) == 0, "setting valid endpoint failed");
  memset(&test_state, 0, sizeof(test_state));
  check(virtual_model_bridge_start() == 0, "private endpoint did not start");
  check(virtual_model_bridge_start() == 0, "start should be idempotent");
  struct stat socket_info;
  check(lstat(socket_path, &socket_info) == 0 && S_ISSOCK(socket_info.st_mode),
        "listener socket was not created");
  check(socket_info.st_uid == geteuid() && (socket_info.st_mode & 0777u) == 0600u,
        "listener ownership/mode is incorrect");

  int client = connect_client(socket_path);
  command(client, "INPUT 17", "NOT_READY");
  check(get_test_state().input_signals[0] == 0u, "pre-init command altered model inputs");
  close(client);

  set_initialized(true);
  pthread_mutex_lock(&test_mutex);
  test_state.opened = true;
  test_state.configured = true;
  test_state.app_running = true;
  test_state.watchdog_healthy = true;
  test_state.effective_outputs[0] = 12u;
  pthread_mutex_unlock(&test_mutex);

  client = connect_client(socket_path);
  command(client, "APPSTATE 3", "ERR COMMAND");
  check(appstate_setter_calls == 0u, "application-state setter was reachable");
  close(client);
  wait_permit_false();

  client = connect_client(socket_path);
  command(client, "INPUT 255", "OK INPUT");
  command(client, "PERMIT 1", "OK PERMIT");
  command(client, "STATUS", "STATUS input=255 permit=1");
  virtual_model_snapshot snapshot = get_test_state();
  check(snapshot.input_signals[0] == 255u && snapshot.permit,
        "valid input/permit commands did not update the model");
  command(client, "V2 STATUS", "V2 STATUS DI16 generation=17 input_bytes=2");
  command(client, "V2 INPUT DI16 17 2 a55a", "OK FRAME");
  check(get_test_state().input_signals[0] == 0xa5u &&
        get_test_state().input_signals[1] == 0x5au,
        "complete V2 byte frame was not applied");
  command(client, "V2 INPUT DI16 16 2 0102", "ERR GENERATION");
  command(client, "V2 INPUT DI16 17 1 ff", "ERR LENGTH");
  command(client, "V2 INPUT DI16 17 2 a55A", "ERR FRAME");
  command(client, "V2 INPUT DI8 17 2 0102", "ERR PROFILE");
  check(get_test_state().input_signals[0] == 0xa5u &&
        get_test_state().input_signals[1] == 0x5au,
        "rejected V2 frame changed input signals");
  command(client, "FAULT", "OK FAULT LATCHED");
  snapshot = get_test_state();
  check(snapshot.fault_latched && snapshot.effective_outputs[0] == 0u,
        "fault command did not latch fault/fail closed");
  command(client, "PERMIT 2", "ERR COMMAND");
  close(client);
  wait_permit_false();

  pthread_mutex_lock(&test_mutex);
  test_state.fault_latched = false;
  memset(test_state.effective_outputs, 0, sizeof(test_state.effective_outputs));
  pthread_mutex_unlock(&test_mutex);
  client = connect_client(socket_path);
  command(client, "PERMIT 1", "OK PERMIT");
  close(client); /* Client close must synchronously revoke permit in the worker. */
  wait_permit_false();

  client = connect_client(socket_path);
  command(client, "PERMIT 1", "OK PERMIT");
  struct timespec pause = {0, 700000000L};
  nanosleep(&pause, NULL);
  wait_permit_false();
  close(client);

  client = connect_client(socket_path);
  const unsigned word_values[] = {0u, 255u, 256u, 32768u, 42390u, 65535u};
  for (size_t index = 0; index < sizeof(word_values) / sizeof(word_values[0]); ++index) {
    char request[32], expected[80];
    snprintf(request, sizeof(request), "INPUT %u", word_values[index]);
    snprintf(expected, sizeof(expected), "STATUS input=%u permit=0 ", word_values[index]);
    command(client, request, "OK INPUT");
    command(client, "STATUS", expected);
    check((unsigned)get_test_state().input_signals[0] + ((unsigned)get_test_state().input_signals[1] << 8u) == word_values[index], "word input was truncated");
  }
  close(client);
  wait_permit_false();
  const char *invalid_inputs[] = {
      "INPUT 65536", "INPUT -1", "INPUT +1", "INPUT 00", "INPUT 0255",
      "INPUT 100000", "INPUT 4294967296", "INPUT 1x", "INPUT 65535\n", "INPUT "};
  for (size_t index = 0; index < sizeof(invalid_inputs) / sizeof(invalid_inputs[0]); ++index) {
    client = connect_client(socket_path);
    command(client, "PERMIT 1", "OK PERMIT");
    command(client, invalid_inputs[index], "ERR COMMAND");
    close(client);
    wait_permit_false();
    snapshot = get_test_state();
    check(snapshot.input_signals[0] == 255u && snapshot.input_signals[1] == 255u && snapshot.effective_outputs[0] == 0u,
          "invalid input changed signals or left outputs enabled");
  }

  virtual_model_bridge_stop();
  check(access(socket_path, F_OK) != 0 && errno == ENOENT,
        "stop did not remove its own socket");
  virtual_model_bridge_stop();

  unlink(existing_path);
  rmdir(public_dir);
  rmdir(private_dir);
  rmdir(test_root);
  puts("ADI_MODEL_BRIDGE_TRANSPORT_TEST: PASS (own-only IPC test double)");
  return 0;
}
