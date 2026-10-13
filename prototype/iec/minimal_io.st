PROGRAM PLC_PRG
VAR
    // Internal candidate signals only; no physical I/O mapping is supplied.
    InputWord : WORD := WORD#0;
    OutputWord : WORD := WORD#0;
    OutputPermit : BOOL := FALSE;
    CycleCounter : UDINT := UDINT#0;
END_VAR

// Default the requested output to zero on every scan.
OutputWord := WORD#0;
IF OutputPermit THEN
    OutputWord := InputWord;
END_IF;

// Saturate at the UDINT maximum so behavior does not depend on wrap settings.
IF CycleCounter < UDINT#16#FFFFFFFF THEN
    CycleCounter := CycleCounter + UDINT#1;
END_IF;
