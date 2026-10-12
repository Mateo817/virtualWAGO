PROGRAM PLC_PRG
VAR
    // Internal candidate signals only; native project mapping is separate.
    InputByte : BYTE := BYTE#0;
    OutputByte : BYTE := BYTE#0;
    OutputPermit : BOOL := FALSE;
    CycleCounter : UDINT := UDINT#0;
END_VAR

// Default the requested output to zero on every scan.
OutputByte := BYTE#0;
IF OutputPermit THEN
    OutputByte := InputByte;
END_IF;

// Saturate at the UDINT maximum so behavior does not depend on wrap settings.
IF CycleCounter < UDINT#16#FFFFFFFF THEN
    CycleCounter := CycleCounter + UDINT#1;
END_IF;
