/* Offline compile-only probe against genuine, version-pinned WAGO headers.
 * This is not a shim and makes no runtime or hardware calls.
 * Evidence scope: public FW30-V04.08.09 SDK headers only; not FW31 ABI proof.
 */
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <dal/adi_application_interface.h>
#include <libpackbus.h>

#ifdef RESEARCH_RUNTIME_LAYOUT_PROBE
#include <stdio.h>
#endif

#if !defined(__arm__) || !defined(__ARM_EABI__) || !defined(__ARM_PCS_VFP)
#error "Compile with an ARM EABI hard-float compiler"
#endif

_Static_assert(sizeof(void *) == 4, "Use ARM32, not a 64-bit host ABI");
_Static_assert(sizeof(size_t) == 4, "Expected ARM32 size_t");
_Static_assert(sizeof(tDeviceId) == 4, "Header tDeviceId width changed");

typedef int32_t (*research_adi_slot_00_fn)(void);
typedef int32_t (*research_adi_slot_01_fn)(void);
typedef int32_t (*research_adi_slot_02_fn)(void);
typedef int32_t (*research_adi_slot_03_fn)(size_t, tDeviceInfo *, size_t *);
typedef int32_t (*research_adi_slot_04_fn)(tDeviceId);
typedef int32_t (*research_adi_slot_05_fn)(tDeviceId);
typedef bool (*research_adi_slot_06_fn)(tDeviceId);
typedef int32_t (*research_adi_slot_07_fn)(tDeviceId, size_t, char *, size_t *);
typedef int32_t (*research_adi_slot_08_fn)(tDeviceId, uint32_t *);
typedef int32_t (*research_adi_slot_09_fn)(tDeviceId, uint32_t *, uint32_t *);
typedef int32_t (*research_adi_slot_10_fn)(tDeviceId, int32_t, void *);
typedef int32_t (*research_adi_slot_11_fn)(tDeviceId, void *);
typedef int32_t (*research_adi_slot_12_fn)(tDeviceId, uint32_t);
typedef int32_t (*research_adi_slot_13_fn)(tDeviceId, uint32_t, uint32_t,
                                           uint8_t *);
typedef int32_t (*research_adi_slot_14_fn)(tDeviceId, uint32_t, uint32_t, bool);
typedef int32_t (*research_adi_slot_15_fn)(tDeviceId, uint32_t, uint32_t,
                                           uint32_t, uint8_t *);
typedef int32_t (*research_adi_slot_16_fn)(tDeviceId, uint32_t);
typedef int32_t (*research_adi_slot_17_fn)(tDeviceId, uint32_t);
typedef int32_t (*research_adi_slot_18_fn)(tDeviceId, uint32_t, uint32_t,
                                           uint8_t *);
typedef int32_t (*research_adi_slot_19_fn)(tDeviceId, uint32_t, uint32_t, bool *);
typedef int32_t (*research_adi_slot_20_fn)(tDeviceId, uint32_t, uint32_t,
                                           uint32_t, uint8_t *);
typedef int32_t (*research_adi_slot_21_fn)(tDeviceId, uint32_t);
typedef int32_t (*research_adi_slot_22_fn)(tDeviceId, uint32_t, uint8_t *,
                                           tBusState *);
typedef int32_t (*research_adi_slot_23_fn)(tDeviceId, int32_t, size_t, uint8_t *,
                                           tDiagnoseState *);
typedef int32_t (*research_adi_slot_24_fn)(tDeviceId, tEventHandler, void *);
typedef int32_t (*research_adi_slot_25_fn)(tDeviceId, tEventHandler);
typedef int32_t (*research_adi_slot_26_fn)(tDeviceId, tError *);
typedef int32_t (*research_adi_slot_27_fn)(tApplicationStateChangedEvent);
typedef int32_t (*research_adi_slot_28_fn)(const char *, void *, ...);
typedef int32_t (*research_adi_slot_29_fn)(const char *, void *, va_list);
typedef int32_t (*research_adi_slot_30_fn)(uint32_t, uint32_t);
typedef int32_t (*research_adi_slot_31_fn)(void);
typedef int32_t (*research_adi_slot_32_fn)(void);
typedef int32_t (*research_adi_slot_33_fn)(void);

#define ASSERT_SLOT_SIGNATURE(field, signature) \
  _Static_assert(__builtin_types_compatible_p( \
                     __typeof__(((tApplicationDeviceInterface *)0)->field), \
                     signature), \
                 #field " header signature changed")
ASSERT_SLOT_SIGNATURE(Init, research_adi_slot_00_fn);
ASSERT_SLOT_SIGNATURE(Exit, research_adi_slot_01_fn);
ASSERT_SLOT_SIGNATURE(ScanDevices, research_adi_slot_02_fn);
ASSERT_SLOT_SIGNATURE(GetDeviceList, research_adi_slot_03_fn);
ASSERT_SLOT_SIGNATURE(OpenDevice, research_adi_slot_04_fn);
ASSERT_SLOT_SIGNATURE(CloseDevice, research_adi_slot_05_fn);
ASSERT_SLOT_SIGNATURE(IsDeviceOpen, research_adi_slot_06_fn);
ASSERT_SLOT_SIGNATURE(GetDeviceName, research_adi_slot_07_fn);
ASSERT_SLOT_SIGNATURE(GetDeviceFlags, research_adi_slot_08_fn);
ASSERT_SLOT_SIGNATURE(GetIoSizes, research_adi_slot_09_fn);
ASSERT_SLOT_SIGNATURE(ConfigureSubdevice, research_adi_slot_10_fn);
ASSERT_SLOT_SIGNATURE(ConfigureDevice, research_adi_slot_11_fn);
ASSERT_SLOT_SIGNATURE(WriteStart, research_adi_slot_12_fn);
ASSERT_SLOT_SIGNATURE(WriteBit, research_adi_slot_13_fn);
ASSERT_SLOT_SIGNATURE(WriteBool, research_adi_slot_14_fn);
ASSERT_SLOT_SIGNATURE(WriteBytes, research_adi_slot_15_fn);
ASSERT_SLOT_SIGNATURE(WriteEnd, research_adi_slot_16_fn);
ASSERT_SLOT_SIGNATURE(ReadStart, research_adi_slot_17_fn);
ASSERT_SLOT_SIGNATURE(ReadBit, research_adi_slot_18_fn);
ASSERT_SLOT_SIGNATURE(ReadBool, research_adi_slot_19_fn);
ASSERT_SLOT_SIGNATURE(ReadBytes, research_adi_slot_20_fn);
ASSERT_SLOT_SIGNATURE(ReadEnd, research_adi_slot_21_fn);
ASSERT_SLOT_SIGNATURE(DiagnoseGetDeviceState, research_adi_slot_22_fn);
ASSERT_SLOT_SIGNATURE(DiagnoseGetSubdeviceState, research_adi_slot_23_fn);
ASSERT_SLOT_SIGNATURE(RegisterEventHandler, research_adi_slot_24_fn);
ASSERT_SLOT_SIGNATURE(UnregisterEventHandler, research_adi_slot_25_fn);
ASSERT_SLOT_SIGNATURE(GetLastError, research_adi_slot_26_fn);
ASSERT_SLOT_SIGNATURE(ApplicationStateChanged, research_adi_slot_27_fn);
ASSERT_SLOT_SIGNATURE(CallDeviceSpecificFunction, research_adi_slot_28_fn);
ASSERT_SLOT_SIGNATURE(VCallDeviceSpecificFunction, research_adi_slot_29_fn);
ASSERT_SLOT_SIGNATURE(WatchdogSetTime, research_adi_slot_30_fn);
ASSERT_SLOT_SIGNATURE(WatchdogStart, research_adi_slot_31_fn);
ASSERT_SLOT_SIGNATURE(WatchdogStop, research_adi_slot_32_fn);
ASSERT_SLOT_SIGNATURE(WatchdogTrigger, research_adi_slot_33_fn);

#define ASSERT_SLOT_OFFSET(field, index) \
  _Static_assert(offsetof(tApplicationDeviceInterface, field) == (index) * 4, \
                 #field " slot offset changed")
ASSERT_SLOT_OFFSET(Init, 0);
ASSERT_SLOT_OFFSET(Exit, 1);
ASSERT_SLOT_OFFSET(ScanDevices, 2);
ASSERT_SLOT_OFFSET(GetDeviceList, 3);
ASSERT_SLOT_OFFSET(OpenDevice, 4);
ASSERT_SLOT_OFFSET(CloseDevice, 5);
ASSERT_SLOT_OFFSET(IsDeviceOpen, 6);
ASSERT_SLOT_OFFSET(GetDeviceName, 7);
ASSERT_SLOT_OFFSET(GetDeviceFlags, 8);
ASSERT_SLOT_OFFSET(GetIoSizes, 9);
ASSERT_SLOT_OFFSET(ConfigureSubdevice, 10);
ASSERT_SLOT_OFFSET(ConfigureDevice, 11);
ASSERT_SLOT_OFFSET(WriteStart, 12);
ASSERT_SLOT_OFFSET(WriteBit, 13);
ASSERT_SLOT_OFFSET(WriteBool, 14);
ASSERT_SLOT_OFFSET(WriteBytes, 15);
ASSERT_SLOT_OFFSET(WriteEnd, 16);
ASSERT_SLOT_OFFSET(ReadStart, 17);
ASSERT_SLOT_OFFSET(ReadBit, 18);
ASSERT_SLOT_OFFSET(ReadBool, 19);
ASSERT_SLOT_OFFSET(ReadBytes, 20);
ASSERT_SLOT_OFFSET(ReadEnd, 21);
ASSERT_SLOT_OFFSET(DiagnoseGetDeviceState, 22);
ASSERT_SLOT_OFFSET(DiagnoseGetSubdeviceState, 23);
ASSERT_SLOT_OFFSET(RegisterEventHandler, 24);
ASSERT_SLOT_OFFSET(UnregisterEventHandler, 25);
ASSERT_SLOT_OFFSET(GetLastError, 26);
ASSERT_SLOT_OFFSET(ApplicationStateChanged, 27);
ASSERT_SLOT_OFFSET(CallDeviceSpecificFunction, 28);
ASSERT_SLOT_OFFSET(VCallDeviceSpecificFunction, 29);
ASSERT_SLOT_OFFSET(WatchdogSetTime, 30);
ASSERT_SLOT_OFFSET(WatchdogStart, 31);
ASSERT_SLOT_OFFSET(WatchdogStop, 32);
ASSERT_SLOT_OFFSET(WatchdogTrigger, 33);
_Static_assert(sizeof(tApplicationDeviceInterface) == 34 * 4,
               "ADI table size changed");

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
LAYOUT_SIZE(tCONFIGURE_DEVICE);
LAYOUT_SIZE(tKBUS_TERMINAL_INFO_32);

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
const uint32_t research_offset_configure_device_uConfStru =
      offsetof(tCONFIGURE_DEVICE, uConfStru);
const uint32_t research_offset_terminal_info_input_bits =
      offsetof(tKBUS_TERMINAL_INFO_32, ulOffsetInput_bits);
const uint32_t research_offset_terminal_info_output_bits =
      offsetof(tKBUS_TERMINAL_INFO_32, ulOffsetOutput_bits);
const uint32_t research_offset_terminal_info_size_input_bits =
      offsetof(tKBUS_TERMINAL_INFO_32, ulSizeInput_bits);
const uint32_t research_offset_terminal_info_size_output_bits =
      offsetof(tKBUS_TERMINAL_INFO_32, ulSizeOutput_bits);

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
