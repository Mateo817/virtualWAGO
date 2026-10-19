#include "adi_digital_adapter.h"
#include <libpackbus.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
int main(void) {
 tApplicationDeviceInterface *a=adi_GetApplicationInterface();
 virtual_adi_reset(); assert(virtual_adi_select_profile(VIRTUAL_ADI_PROFILE_PWM677)==DAL_SUCCESS);
 assert(a->Init()==DAL_SUCCESS);
 struct {uint32_t before,uid,after;} b={0x12345678,0xabcdef01,0x87654321};
 int32_t inner=99;
 assert(a->CallDeviceSpecificFunction(LIBPACKBUS_DAL_FUNC_GET_UID,&inner,1,&b.uid)==DAL_SUCCESS);
 assert(inner==0 && b.uid==SYNTHETIC_TEST_UID && b.before==0x12345678 && b.after==0x87654321);
 b.uid=0xabcdef01;
 assert(a->CallDeviceSpecificFunction(LIBPACKBUS_DAL_FUNC_GET_UID,&inner,0,&b.uid)==DAL_SUCCESS);
 assert(inner==-1 && b.uid==0xabcdef01);
 assert(a->Exit()==DAL_SUCCESS); puts("SYNTHETIC_UID_BUFFER_TEST_PASS");
}
