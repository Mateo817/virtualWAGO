PROGRAM PLC_PRG
VAR
    // Dedicated virtual-only cyclic probe; model permit starts false.
    // Physical bus endpoints must remain absent; never deploy to physical I/O.
    InputByte : BYTE := BYTE#0;
    OutputByte : BYTE := BYTE#0;
    OutputPermit : BOOL := TRUE;
    CycleCounter : UDINT := UDINT#0;
END_VAR

// Default the requested output to zero on every scan.
OutputByte := BYTE#0;
IF OutputPermit THEN
    OutputByte := InputByte XOR BYTE#16#96;
END_IF;

// Saturate at the UDINT maximum so behavior does not depend on wrap settings.
IF CycleCounter < UDINT#16#FFFFFFFF THEN
    CycleCounter := CycleCounter + UDINT#1;
END_IF;
