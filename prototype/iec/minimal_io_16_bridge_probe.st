PROGRAM PLC_PRG
VAR
    // Dedicated isolated probe only; requested output is distinct from model-effective output.
    InputWord : WORD := WORD#0;
    OutputWord : WORD := WORD#0;
    OutputPermit : BOOL := TRUE;
    CycleCounter : UDINT := UDINT#0;
END_VAR

// Deterministic signature exposes all sixteen input bits in the requested frame.
OutputWord := WORD#0;
IF OutputPermit THEN
    OutputWord := InputWord XOR WORD#16#A596;
END_IF;

// Saturate at the UDINT maximum so behavior does not depend on wrap settings.
IF CycleCounter < UDINT#16#FFFFFFFF THEN
    CycleCounter := CycleCounter + UDINT#1;
END_IF;
