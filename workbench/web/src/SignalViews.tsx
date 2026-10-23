import { useEffect, useRef, useState } from "react";
import { Code2, Zap } from "lucide-react";
import type { Channel, Signal } from "./types";
const number = new Intl.NumberFormat("de-DE", { maximumFractionDigits: 3 });

export function SignalRow({
  channel: c,
  signal: s,
  disabled,
  onValue,
  onWatch,
}: {
  channel: Channel;
  signal?: Signal;
  name: string;
  disabled: boolean;
  onValue: (value: number) => void;
  onWatch: () => void;
}) {
  const value = s?.requested ?? s?.value ?? c.initial;
  const [draft, setDraft] = useState(String(value));
  const focused = useRef(false);
  useEffect(() => {
    if (!focused.current) setDraft(String(value));
  }, [value]);
  const scripted = s?.source.startsWith("reaction:");
  const blocked = disabled || !s || (c.direction === "input" && scripted);
  return (
    <tr>
      <td>
        <button className="signal-name" onClick={onWatch}>
          <span className={`io-dot ${s && s.value > c.min ? "lit" : ""}`} />
          {c.label}
        </button>
        <small>
          {s ? `0x${s.raw.toString(16).padStart(4, "0")}` : "Entwurf"}
        </small>
      </td>
      <td>
        <span className={`direction ${c.direction}`}>
          {c.direction === "input" ? "IN" : "OUT"}
        </span>
      </td>
      <td>
        {c.kind === "digital" ? (
          <button
            className={`bit-button ${value ? "high" : ""}`}
            disabled={blocked}
            aria-label={`${c.label} ${c.direction === "output" ? "Testvorgabe" : "Eingang"} ${value ? "ausschalten" : "einschalten"}`}
            onClick={() => onValue(value ? 0 : 1)}
          >
            {value ? "1 · HIGH" : "0 · LOW"}
          </button>
        ) : (
          <label className="numeric">
            <input
              type="number"
              aria-label={`${c.label} ${c.direction === "output" ? "Testvorgabe" : "Eingang"}`}
              min={c.min}
              max={c.max}
              step="0.001"
              value={draft}
              disabled={blocked}
              onFocus={() => {
                focused.current = true;
              }}
              onChange={(e) => setDraft(e.target.value)}
              onBlur={() => {
                focused.current = false;
                const v = Number(draft);
                if (draft.trim() && Number.isFinite(v) && v !== value)
                  onValue(v);
                setDraft(String(value));
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter") e.currentTarget.blur();
              }}
            />
            {c.unit}
          </label>
        )}
      </td>
      <td className="effective">
        {s ? `${number.format(s.value)} ${c.unit}` : "—"}
      </td>
      <td>
        <span className={`source ${scripted ? "scripted" : ""}`}>
          {scripted ? (
            <Code2 size={12} />
          ) : c.direction === "output" ? (
            <Zap size={12} />
          ) : null}
          {scripted
            ? "Reaktion"
            : c.direction === "output"
              ? "Testvorgabe"
              : "Manuell"}
        </span>
      </td>
    </tr>
  );
}
