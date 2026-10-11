/* Offline compile-only probe against genuine, version-pinned WAGO headers.
 * This is not a shim and makes no runtime or hardware calls.
 * Evidence scope: public FW30-V04.08.09 SDK headers only; not FW31 ABI proof.
 */
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <dal/adi_application_interface.h>

#ifdef RESEARCH_RUNTIME_LAYOUT_PROBE
#include <stdio.h>
#endif

#if !defined(__arm__) || !defined(__ARM_EABI__) || !defined(__ARM_PCS_VFP)
#error "Compile with an ARM EABI hard-float compiler"
#endif

_Static_assert(sizeof(void *) == 4, "Use ARM32, not a 64-bit host ABI");
_Static_assert(sizeof(size_t) == 4, "Expected ARM32 size_t");
_Static_assert(sizeof(tDeviceId) == 4, "Header tDeviceId width changed");

typedef int32_t (*research_get_device_list_fn)(size_t, tDeviceInfo *, size_t *);
typedef int32_t (*research_read_bytes_fn)(tDeviceId, uint32_t, uint32_t,
                                          uint32_t, uint8_t *);
typedef int32_t (*research_write_bytes_fn)(tDeviceId, uint32_t, uint32_t,
                                           uint32_t, uint8_t *);
_Static_assert(__builtin_types_compatible_p(
                   __typeof__(((tApplicationDeviceInterface *)0)->GetDeviceList),
                   research_get_device_list_fn),
               "GetDeviceList header signature changed");
_Static_assert(__builtin_types_compatible_p(
                   __typeof__(((tApplicationDeviceInterface *)0)->ReadBytes),
                   research_read_bytes_fn),
               "ReadBytes header signature changed");
_Static_assert(__builtin_types_compatible_p(
                   __typeof__(((tApplicationDeviceInterface *)0)->WriteBytes),
                   research_write_bytes_fn),
               "WriteBytes header signature changed");

#define LAYOUT_SIZE(type) const uint32_t research_size_##type = sizeof(type)
#define LAYOUT_OFFSET(field) \
  const uint32_t research_offset_##field = \
      offsetof(tApplicationDeviceInterface, field)

const uint32_t research_pointer_bytes = sizeof(void *);
const uint32_t research_size_t_bytes = sizeof(size_t);
const uint32_t research_bool_bytes = sizeof(bool);
const uint32_t research_function_pointer_bytes =
    sizeof(((tApplicationDeviceInterface *)0)->Init);

LAYOUT_SIZE(tApplicationDeviceInterface);
LAYOUT_SIZE(tDeviceInfo);
LAYOUT_SIZE(tDeviceId);
LAYOUT_SIZE(tApplicationStateChangedEvent);
LAYOUT_SIZE(tApplicationState);
LAYOUT_SIZE(tBusState);
LAYOUT_SIZE(tDiagnoseState);
LAYOUT_SIZE(tError);
LAYOUT_SIZE(tCommonEvent_IoSizeChanged);

const uint32_t research_offset_device_info_DeviceId =
    offsetof(tDeviceInfo, DeviceId);
const uint32_t research_offset_device_info_DeviceName =
    offsetof(tDeviceInfo, DeviceName);
const uint32_t research_offset_state_event_State =
    offsetof(tApplicationStateChangedEvent, State);
const uint32_t research_offset_iowidths_OldInputSize =
    offsetof(tCommonEvent_IoSizeChanged, OldInputSize);
const uint32_t research_offset_iowidths_OldOutputSize =
    offsetof(tCommonEvent_IoSizeChanged, OldOutputSize);
const uint32_t research_offset_iowidths_NewInputSize =
    offsetof(tCommonEvent_IoSizeChanged, NewInputSize);
const uint32_t research_offset_iowidths_NewOutputSize =
    offsetof(tCommonEvent_IoSizeChanged, NewOutputSize);

LAYOUT_OFFSET(Init);
LAYOUT_OFFSET(Exit);
LAYOUT_OFFSET(ScanDevices);
LAYOUT_OFFSET(GetDeviceList);
LAYOUT_OFFSET(OpenDevice);
LAYOUT_OFFSET(CloseDevice);
LAYOUT_OFFSET(IsDeviceOpen);
LAYOUT_OFFSET(GetDeviceName);
LAYOUT_OFFSET(GetDeviceFlags);
LAYOUT_OFFSET(GetIoSizes);
LAYOUT_OFFSET(ConfigureSubdevice);
LAYOUT_OFFSET(ConfigureDevice);
LAYOUT_OFFSET(WriteStart);
LAYOUT_OFFSET(WriteBit);
LAYOUT_OFFSET(WriteBool);
LAYOUT_OFFSET(WriteBytes);
LAYOUT_OFFSET(WriteEnd);
LAYOUT_OFFSET(ReadStart);
LAYOUT_OFFSET(ReadBit);
LAYOUT_OFFSET(ReadBool);
LAYOUT_OFFSET(ReadBytes);
LAYOUT_OFFSET(ReadEnd);
LAYOUT_OFFSET(DiagnoseGetDeviceState);
LAYOUT_OFFSET(DiagnoseGetSubdeviceState);
LAYOUT_OFFSET(RegisterEventHandler);
LAYOUT_OFFSET(UnregisterEventHandler);
LAYOUT_OFFSET(GetLastError);
LAYOUT_OFFSET(ApplicationStateChanged);
LAYOUT_OFFSET(CallDeviceSpecificFunction);
LAYOUT_OFFSET(VCallDeviceSpecificFunction);
LAYOUT_OFFSET(WatchdogSetTime);
LAYOUT_OFFSET(WatchdogStart);
LAYOUT_OFFSET(WatchdogStop);
LAYOUT_OFFSET(WatchdogTrigger);

const int32_t research_enum_DAL_FAILURE = DAL_FAILURE;
const int32_t research_enum_DAL_SUCCESS = DAL_SUCCESS;
const int32_t research_enum_DAL_NOTUSED = DAL_NOTUSED;
const int32_t research_enum_ApplicationState_BASE = ApplicationState_BASE;
const int32_t research_enum_ApplicationState_Running = ApplicationState_Running;
const int32_t research_enum_ApplicationState_Stopped = ApplicationState_Stopped;
const int32_t research_enum_ApplicationState_Unconfigured =
    ApplicationState_Unconfigured;
const int32_t research_enum_BusState_NotEnabled = BusState_NotEnabled;
const int32_t research_enum_BusState_BusOk = BusState_BusOk;
const int32_t research_enum_BusState_BusFault = BusState_BusFault;
const int32_t research_enum_BusState_BusNotCommunicating =
    BusState_BusNotCommunicating;
const int32_t research_enum_BusState_BusStopped = BusState_BusStopped;
const int32_t research_enum_DiagnoseState_InvalidInputParameter =
    DiagnoseState_InvalidInputParameter;
const int32_t research_enum_DiagnoseState_NotEnabled = DiagnoseState_NotEnabled;
const int32_t research_enum_DiagnoseState_GetDiagInfo = DiagnoseState_GetDiagInfo;
const int32_t research_enum_DiagnoseState_DiagInfoAvailable =
    DiagnoseState_DiagInfoAvailable;
const int32_t research_enum_DiagnoseState_DiagInfoNotAvailable =
    DiagnoseState_DiagInfoNotAvailable;
const uint32_t research_enum_BusMemberState_Configured =
    BusMemberState_Configured;
const uint32_t research_enum_BusMemberState_Alive = BusMemberState_Alive;
const uint32_t research_enum_BusMemberState_Faulted = BusMemberState_Faulted;

#ifdef RESEARCH_RUNTIME_LAYOUT_PROBE
/* Optional own executable: header layout only. No DAL or driver functions are
 * linked/called. A run qualifies the ARM carrier, never an original consumer. */
int main(void)
{
    printf("{\"scope\":\"own ARM probe; FW30 headers; no DAL calls\","
           "\"pointer_bytes\":%u,\"size_t_bytes\":%u,\"bool_bytes\":%u,"
           "\"interface_bytes\":%u,\"device_info_bytes\":%u,"
           "\"device_id_bytes\":%u,\"event_bytes\":%u,"
           "\"get_device_list_offset\":%u,\"read_bytes_offset\":%u,"
           "\"write_bytes_offset\":%u,\"success\":%d,\"failure\":%d}\n",
           research_pointer_bytes, research_size_t_bytes, research_bool_bytes,
           research_size_tApplicationDeviceInterface, research_size_tDeviceInfo,
           research_size_tDeviceId, research_size_tApplicationStateChangedEvent,
           research_offset_GetDeviceList, research_offset_ReadBytes,
           research_offset_WriteBytes, research_enum_DAL_SUCCESS,
           research_enum_DAL_FAILURE);
    return 0;
}
#endif
