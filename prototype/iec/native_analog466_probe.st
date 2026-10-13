PROGRAM PLC_PRG
VAR
    InputWord1 : WORD := WORD#0;
    InputWord2 : WORD := WORD#0;
    SampleSignature : WORD := WORD#0;
    CycleCounter : UDINT := UDINT#0;
END_VAR

// Observe two mapped native WORDs. No outputs or diagnostic values are synthesized.
SampleSignature := InputWord1 XOR InputWord2;
IF CycleCounter < UDINT#16#FFFFFFFF THEN
    CycleCounter := CycleCounter + UDINT#1;
END_IF;
