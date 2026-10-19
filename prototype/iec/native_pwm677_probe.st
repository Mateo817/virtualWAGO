PROGRAM PLC_PRG
VAR
    PwmStatus1 : BYTE := BYTE#0;
    PwmReservedInput1 : BYTE := BYTE#0;
    PwmInputValue1 : WORD := WORD#0;
    PwmStatus2 : BYTE := BYTE#0;
    PwmReservedInput2 : BYTE := BYTE#0;
    PwmInputValue2 : WORD := WORD#0;
    PwmStatus3 : BYTE := BYTE#0;
    PwmReservedInput3 : BYTE := BYTE#0;
    PwmInputValue3 : WORD := WORD#0;
    PwmStatus4 : BYTE := BYTE#0;
    PwmReservedInput4 : BYTE := BYTE#0;
    PwmInputValue4 : WORD := WORD#0;
    PwmControl1 : BYTE := BYTE#0;
    PwmReservedOutput1 : BYTE := BYTE#0;
    PwmOutputValue1 : WORD := WORD#0;
    PwmControl2 : BYTE := BYTE#0;
    PwmReservedOutput2 : BYTE := BYTE#0;
    PwmOutputValue2 : WORD := WORD#0;
    PwmControl3 : BYTE := BYTE#0;
    PwmReservedOutput3 : BYTE := BYTE#0;
    PwmOutputValue3 : WORD := WORD#0;
    PwmControl4 : BYTE := BYTE#0;
    PwmReservedOutput4 : BYTE := BYTE#0;
    PwmOutputValue4 : WORD := WORD#0;
END_VAR

// Raw WORD integration probe only: no physical PWM behavior or input meaning is claimed.
PwmControl1 := BYTE#0;
PwmReservedOutput1 := BYTE#0;
PwmOutputValue1 := PwmInputValue1;
PwmControl2 := BYTE#0;
PwmReservedOutput2 := BYTE#0;
PwmOutputValue2 := PwmInputValue2;
PwmControl3 := BYTE#0;
PwmReservedOutput3 := BYTE#0;
PwmOutputValue3 := PwmInputValue3;
PwmControl4 := BYTE#0;
PwmReservedOutput4 := BYTE#0;
PwmOutputValue4 := PwmInputValue4;
