/* Own opt-in experiment: no vendor hardware or module-readiness claim. */
#include "adi_digital_adapter.h"
#include <libpackbus.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdarg.h>

static int32_t call_v(tApplicationDeviceInterface *adi, const char *name,
                      int32_t *inner, ...) {
  va_list args;
  va_start(args, inner);
  int32_t result = adi->VCallDeviceSpecificFunction(name, inner, args);
  va_end(args);
  return result;
}

int main(void) {
  tApplicationDeviceInterface *adi = adi_GetApplicationInterface();
  virtual_adi_reset();
  assert(virtual_adi_select_profile(VIRTUAL_ADI_PROFILE_PWM677) == DAL_SUCCESS);
  int32_t inner = 99;
  uint32_t uid = 0xabcdef01u;
  assert(adi->Init() == DAL_SUCCESS);
  assert(adi->CallDeviceSpecificFunction(LIBPACKBUS_DAL_FUNC_GET_UID,
                                       &inner, 1, &uid) == DAL_SUCCESS);
#ifndef VIRTUALWAGO_PWM_ASYNC_EXPLORATION
  assert(inner == -1 && uid == 0xabcdef01u);
  uint32_t token = 123u;
  assert(call_v(adi, LIBPACKBUS_DAL_FUNC_ASYNC_COM_OPEN, &inner, &token) == DAL_NOTUSED);
  assert(token == 123u);
#else
  assert(inner == 0 && uid == 750677u);
  uid = 0xabcdef01u;
  assert(adi->CallDeviceSpecificFunction(LIBPACKBUS_DAL_FUNC_GET_UID,
                                       &inner, 2, &uid) == DAL_SUCCESS);
  assert(inner == -1 && uid == 0xabcdef01u);
  assert(virtual_adi_set_permit(true) == DAL_FAILURE);
  assert(virtual_adi_set_permit(false) == DAL_SUCCESS);
  uint32_t tokens[4];
  for (unsigned i = 0; i < 4; ++i) {
    struct { uint32_t before, token, after; } b = {0x12345678u, 999u, 0x87654321u};
    assert(call_v(adi, LIBPACKBUS_DAL_FUNC_ASYNC_COM_OPEN, &inner, &b.token) == DAL_SUCCESS);
    assert(inner == 0 && b.token != 0 && b.before == 0x12345678u && b.after == 0x87654321u);
    tokens[i] = b.token;
    for (unsigned j = 0; j < i; ++j) assert(tokens[i] != tokens[j]);
  }
  uint32_t extra = 0xabcdef01u;
  assert(call_v(adi, LIBPACKBUS_DAL_FUNC_ASYNC_COM_OPEN, &inner, &extra) == DAL_FAILURE);
  assert(extra == 0xabcdef01u);
  assert(call_v(adi, LIBPACKBUS_DAL_FUNC_ASYNC_COM_OPEN, &inner, (uint32_t *)0) == DAL_FAILURE);
  assert(call_v(adi, LIBPACKBUS_DAL_FUNC_ASYNC_COM_OPEN, (int32_t *)0, &extra) == DAL_FAILURE);
  void *handle = (void *)(uintptr_t)tokens[0];
  struct { uint16_t before, value, after; } word = {0x1234u, 0xabcdu, 0x5678u};
  assert(call_v(adi, LIBPACKBUS_DAL_FUNC_ASYNC_COM_START_RD_REG,
                &inner, handle, 1, 0, 16) == DAL_SUCCESS && inner == 0);
  assert(call_v(adi, LIBPACKBUS_DAL_FUNC_ASYNC_COM_START_RD_REG,
                &inner, handle, 1, 0, 29) == DAL_FAILURE);
  assert(call_v(adi, LIBPACKBUS_DAL_FUNC_ASYNC_COM_POLL_RD_REG,
                &inner, handle, 1, 0, 16, (uint16_t *)0) == DAL_SUCCESS && inner == 16);
  assert(call_v(adi, LIBPACKBUS_DAL_FUNC_ASYNC_COM_POLL_RD_REG,
                &inner, handle, 1, 0, 29, &word.value) == DAL_SUCCESS && inner == 22);
  assert(word.value == 0xabcdu);
  assert(call_v(adi, LIBPACKBUS_DAL_FUNC_ASYNC_COM_POLL_RD_REG,
                &inner, handle, 1, 0, 16, &word.value) == DAL_FAILURE);
  assert(call_v(adi, LIBPACKBUS_DAL_FUNC_ASYNC_COM_START_RD_REG,
                &inner, handle, 1, 0, 16) == DAL_SUCCESS && inner == 0);
  assert(call_v(adi, LIBPACKBUS_DAL_FUNC_ASYNC_COM_POLL_RD_REG,
                &inner, handle, 1, 0, 16, &word.value) == DAL_SUCCESS && inner == 0);
  assert(word.value == 0 && word.before == 0x1234u && word.after == 0x5678u);
  for (unsigned i = 0; i < 4; ++i) {
    assert(call_v(adi, LIBPACKBUS_DAL_FUNC_ASYNC_COM_CLOSE, &inner,
                  (void *)(uintptr_t)tokens[i]) == DAL_SUCCESS);
    assert(inner == 0);
  }
  assert(call_v(adi, LIBPACKBUS_DAL_FUNC_ASYNC_COM_CLOSE, &inner,
                (void *)(uintptr_t)tokens[0]) == DAL_SUCCESS && inner == 15);
  assert(adi->Exit() == DAL_SUCCESS);
  assert(adi->Init() == DAL_SUCCESS);
  assert(call_v(adi, LIBPACKBUS_DAL_FUNC_ASYNC_COM_OPEN, &inner, &extra) == DAL_SUCCESS);
  for (unsigned i = 0; i < 4; ++i) assert(extra != tokens[i]);
  virtual_adi_reset();
  assert(adi->Init() == DAL_SUCCESS);
  assert(call_v(adi, LIBPACKBUS_DAL_FUNC_ASYNC_COM_CLOSE, &inner,
                (void *)(uintptr_t)extra) == DAL_SUCCESS && inner == 15);
  /* Device close cancels our pending read and invalidates its token. */
  assert(adi->OpenDevice(1) == DAL_SUCCESS);
  assert(call_v(adi, LIBPACKBUS_DAL_FUNC_ASYNC_COM_OPEN, &inner, &extra) == DAL_SUCCESS);
  handle = (void *)(uintptr_t)extra;
  assert(call_v(adi, LIBPACKBUS_DAL_FUNC_ASYNC_COM_START_RD_REG,
                &inner, handle, 1, 0, 29) == DAL_SUCCESS && inner == 0);
  assert(adi->CloseDevice(1) == DAL_SUCCESS);
  assert(adi->OpenDevice(1) == DAL_SUCCESS);
  word.value = 0xabcdu;
  assert(call_v(adi, LIBPACKBUS_DAL_FUNC_ASYNC_COM_POLL_RD_REG,
                &inner, handle, 1, 0, 29, &word.value) == DAL_SUCCESS && inner == 15);
  assert(word.value == 0xabcdu);
  assert(call_v(adi, LIBPACKBUS_DAL_FUNC_ASYNC_COM_OPEN, &inner, &extra) == DAL_SUCCESS);
  assert((void *)(uintptr_t)extra != handle);
  assert(adi->CloseDevice(1) == DAL_SUCCESS);
  assert(adi->Exit() == DAL_SUCCESS);
  /* Enabling exploration does not grant async services to other profiles. */
  assert(virtual_adi_select_profile(VIRTUAL_ADI_PROFILE_DIGITAL16) == DAL_SUCCESS);
  assert(adi->Init() == DAL_SUCCESS);
  extra = 0xabcdef01u;
  assert(call_v(adi, LIBPACKBUS_DAL_FUNC_ASYNC_COM_OPEN, &inner, &extra) == DAL_NOTUSED);
  assert(extra == 0xabcdef01u);
#endif
  assert(adi->Exit() == DAL_SUCCESS);
  puts("PWM_ASYNC_EXPLORATION_TEST_PASS");
}
