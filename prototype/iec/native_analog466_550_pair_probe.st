PROGRAM PLC_PRG
VAR
    InputWord1 : WORD := WORD#0;
    InputWord2 : WORD := WORD#0;
    OutputWord1 : WORD := WORD#0;
    OutputWord2 : WORD := WORD#0;
END_VAR

// Probe-only controller logic: pass each native input WORD to one output WORD.
// This mapping test does not model either terminal or scale the values.
OutputWord1 := InputWord1;
OutputWord2 := InputWord2;
