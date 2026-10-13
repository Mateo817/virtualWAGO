/* Actual own adapter + bridge, using genuine private ADI types.
 * This is an own-client test, not an original WAGO consumer test.
 */
#define _GNU_SOURCE
#include "adi_digital_adapter.h"
#include "adi_model_bridge.h"
#include <assert.h>
#include <errno.h>
#include <stddef.h>
#include <pthread.h>
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

static void command(int fd, const char *request, const char *prefix) {
  size_t length = strlen(request);
  assert(send(fd, request, length, MSG_NOSIGNAL) == (ssize_t)length);
  char reply[513];
  ssize_t size = recv(fd, reply, sizeof(reply) - 1u, 0);
  assert(size > 0); reply[size] = '\0';
  assert(strncmp(reply, prefix, strlen(prefix)) == 0);
}

typedef struct {
  tApplicationDeviceInterface *adi;
  pthread_barrier_t *barrier;
  int32_t result;
  bool do_init;
} lifecycle_call;

static void *call_lifecycle(void *opaque) {
  lifecycle_call *call = opaque;
  int barrier_result = pthread_barrier_wait(call->barrier);
  assert(barrier_result == 0 || barrier_result == PTHREAD_BARRIER_SERIAL_THREAD);
  call->result = call->do_init ? call->adi->Init() : call->adi->Exit();
  return NULL;
}

static void assert_status_socket(const char *path) {
  int fd = socket(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0);
  assert(fd >= 0);
  struct timeval timeout = {2, 0};
  assert(setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)) == 0);
  struct sockaddr_un address = {.sun_family = AF_UNIX};
  strcpy(address.sun_path, path);
  assert(connect(fd, (struct sockaddr *)&address,
                 (socklen_t)(offsetof(struct sockaddr_un, sun_path) + strlen(path) + 1u)) == 0);
  command(fd, "STATUS", "STATUS input=");
  close(fd);
}

static void test_concurrent_init_exit(tApplicationDeviceInterface *adi,
                                      const char *path) {
  for (unsigned iteration = 0; iteration < 64u; ++iteration) {
    pthread_barrier_t barrier;
    assert(pthread_barrier_init(&barrier, NULL, 3u) == 0);
    lifecycle_call init_call = {.adi = adi, .barrier = &barrier, .do_init = true};
    lifecycle_call exit_call = {.adi = adi, .barrier = &barrier, .do_init = false};
    pthread_t init_thread, exit_thread;
    assert(pthread_create(&init_thread, NULL, call_lifecycle, &init_call) == 0);
    assert(pthread_create(&exit_thread, NULL, call_lifecycle, &exit_call) == 0);
    int barrier_result = pthread_barrier_wait(&barrier);
    assert(barrier_result == 0 || barrier_result == PTHREAD_BARRIER_SERIAL_THREAD);
    assert(pthread_join(init_thread, NULL) == 0);
    assert(pthread_join(exit_thread, NULL) == 0);
    assert(pthread_barrier_destroy(&barrier) == 0);

    if (init_call.result == DAL_FAILURE) {
      /* Init serialized before Exit and correctly observed the active adapter. */
      assert(exit_call.result == DAL_SUCCESS);
      assert(adi->Init() == DAL_SUCCESS);
    } else {
      /* Exit serialized first; its completed join must not stop this Init. */
      assert(init_call.result == DAL_SUCCESS);
      assert(exit_call.result == DAL_SUCCESS);
    }
    assert_status_socket(path);
  }
}

int main(void) {
  char directory[] = "/tmp/adi-integrated-XXXXXX";
  assert(mkdtemp(directory) != NULL && chmod(directory, 0700) == 0);
  char path[108];
  assert(snprintf(path, sizeof(path), "%s/model.sock", directory) > 0);
  assert(setenv("VIRTUALWAGO_MODEL_SOCKET", path, 1) == 0);
  tApplicationDeviceInterface *adi = adi_GetApplicationInterface();
  assert(adi != NULL);
  assert(virtual_adi_select_profile(VIRTUAL_ADI_PROFILE_DIGITAL8_DI8_DO8) == DAL_SUCCESS);
  assert(adi->Init() == DAL_SUCCESS);
  assert(adi->OpenDevice(1) == DAL_SUCCESS);
  tCONFIGURE_DEVICE config = {0};
  config.eStructType = TCF_SSC_CONF_STRUCT_3;
  assert(adi->ConfigureDevice(1, &config) == DAL_SUCCESS);
  int fd = socket(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0);
  assert(fd >= 0);
  struct timeval timeout = {2, 0};
  assert(setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)) == 0);
  struct sockaddr_un address = {.sun_family = AF_UNIX};
  strcpy(address.sun_path, path);
  assert(connect(fd, (struct sockaddr *)&address,
                 (socklen_t)(offsetof(struct sockaddr_un, sun_path) + strlen(path) + 1u)) == 0);
  command(fd, "INPUT 128", "OK INPUT");
  /* The active eight-channel profile keeps its existing low-byte mask. */
  command(fd, "INPUT 32896", "OK INPUT");
  command(fd, "STATUS", "STATUS input=128 permit=0 ");
  assert(adi->ReadStart(1, 0) == DAL_SUCCESS);
  uint8_t input = 0;
  assert(adi->ReadBytes(1, 0, 0, 1, &input) == DAL_SUCCESS && input == 128);
  assert(adi->ReadEnd(1, 0) == DAL_SUCCESS);
  assert(virtual_adi_set_application_state(ApplicationState_Running) == DAL_SUCCESS);
  assert(adi->WatchdogSetTime(1, 1000000) == DAL_SUCCESS);
  assert(adi->WatchdogStart() == DAL_SUCCESS && adi->WatchdogTrigger() == DAL_SUCCESS);
  command(fd, "PERMIT 1", "OK PERMIT");
  assert(adi->WriteStart(1, 0) == DAL_SUCCESS);
  assert(adi->WriteBytes(1, 0, 0, 1, &input) == DAL_SUCCESS);
  assert(adi->WriteEnd(1, 0) == DAL_SUCCESS);
  command(fd, "STATUS", "STATUS input=128 permit=1 requested=128 effective=128");
  command(fd, "FAULT", "OK FAULT LATCHED");
  command(fd, "STATUS", "STATUS input=128 permit=1 requested=128 effective=0");
  int32_t inner = 0;
  assert(adi->CallDeviceSpecificFunction(LIBPACKBUS_DAL_FUNCTION_PUSH, &inner) == DAL_SUCCESS);
  assert(inner == DAL_FAILURE);
  assert(adi->ConfigureDevice(1, &config) == DAL_SUCCESS);
  assert(adi->WriteStart(1, 0) == DAL_SUCCESS);
  assert(adi->WriteBytes(1, 0, 0, 1, &input) == DAL_SUCCESS);
  assert(adi->WriteEnd(1, 0) == DAL_SUCCESS);
  command(fd, "STATUS", "STATUS input=128 permit=1 requested=128 effective=128");
  close(fd);
  struct timespec delay = {0, 150000000L};
  while (nanosleep(&delay, &delay) != 0) assert(errno == EINTR);
  virtual_model_snapshot snapshot;
  assert(virtual_adi_model_snapshot(&snapshot) == DAL_SUCCESS);
  assert(!snapshot.permit && snapshot.requested_outputs == 128 && snapshot.effective_outputs == 0);
  assert(snapshot.frame_count == 2);
  assert(adi->CloseDevice(1) == DAL_SUCCESS && adi->Exit() == DAL_SUCCESS);
  assert(adi->Init() == DAL_SUCCESS);
  test_concurrent_init_exit(adi, path);
  assert(adi->Exit() == DAL_SUCCESS);
  assert(virtual_adi_select_profile(VIRTUAL_ADI_PROFILE_DIGITAL16) == DAL_SUCCESS);
  assert(adi->Init() == DAL_SUCCESS && adi->OpenDevice(1) == DAL_SUCCESS);
  assert(adi->ConfigureDevice(1, &config) == DAL_SUCCESS);
  fd = socket(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0);
  assert(fd >= 0);
  assert(setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)) == 0);
  assert(connect(fd, (struct sockaddr *)&address,
                 (socklen_t)(offsetof(struct sockaddr_un, sun_path) + strlen(path) + 1u)) == 0);
  command(fd, "PERMIT 0", "OK PERMIT");
  const unsigned word_values[] = {0u, 255u, 256u, 32768u, 42390u, 65535u};
  for (size_t index = 0; index < sizeof(word_values) / sizeof(word_values[0]); ++index) {
    char request[32], expected[80];
    snprintf(request, sizeof(request), "INPUT %u", word_values[index]);
    snprintf(expected, sizeof(expected), "STATUS input=%u permit=0 ", word_values[index]);
    command(fd, request, "OK INPUT");
    command(fd, "STATUS", expected);
    uint8_t input_word[2] = {0u, 0u};
    assert(adi->ReadStart(1, 0u) == DAL_SUCCESS);
    assert(adi->ReadBytes(1, 0u, 0u, 2u, input_word) == DAL_SUCCESS);
    assert(input_word[0] == (word_values[index] & 0xffu));
    assert(input_word[1] == (word_values[index] >> 8));
    assert(adi->ReadEnd(1, 0u) == DAL_SUCCESS);
  }
  command(fd, "INPUT 65536", "ERR COMMAND");
  close(fd);
  assert(virtual_adi_model_snapshot(&snapshot) == DAL_SUCCESS);
  assert(snapshot.inputs == 65535u && !snapshot.permit && snapshot.effective_outputs == 0u);
  assert(adi->CloseDevice(1) == DAL_SUCCESS && adi->Exit() == DAL_SUCCESS);
  assert(access(path, F_OK) != 0 && rmdir(directory) == 0);
  puts("ADI_MODEL_BRIDGE_INTEGRATION_TEST: PASS (own adapter only)");
  return 0;
}
