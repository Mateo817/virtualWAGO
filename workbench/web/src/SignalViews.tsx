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
export function Trend({
  history,
  watched,
  channel,
}: {
  history: { time: number; values: Record<string, number> }[];
  watched: string;
  channel?: Channel;
}) {
  const last = history.at(-1)?.time ?? 0;
  const start = Math.max(0, last - 10000);
  const span = Math.max(1000, last - start);
  const data = history.filter(
    (p) => p.time >= start && p.values[watched] !== undefined,
  );
  const lo = channel?.min ?? 0;
  const hi = channel?.max ?? 1;
  const points = data
    .map(
      (p) =>
        `${30 + ((p.time - start) / span) * 410},${112 - ((p.values[watched] - lo) / (hi - lo)) * 90}`,
    )
    .join(" ");
  return (
    <svg
      className="trend-svg"
      viewBox="0 0 460 140"
      role="img"
      aria-label={`Verlauf ${channel?.label ?? "Signal"}, ${lo} bis ${hi} ${channel?.unit ?? ""}`}
    >
      <defs>
        <linearGradient id="area" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#238b82" stopOpacity=".15" />
          <stop offset="100%" stopColor="#238b82" stopOpacity="0" />
        </linearGradient>
      </defs>
      {[22, 67, 112].map((y) => (
        <line
          key={y}
          x1="30"
          x2="440"
          y1={y}
          y2={y}
          stroke="#e2e9e8"
          strokeDasharray="3 4"
        />
      ))}
      <text x="2" y="26">
        {hi}
      </text>
      <text x="2" y="115">
        {lo}
      </text>
      {points && (
        <>
          <polygon
            points={`30,112 ${points} ${data.length ? 30 + ((data.at(-1)!.time - start) / span) * 410 : 30},112`}
            fill="url(#area)"
          />
          <polyline
            points={points}
            fill="none"
            stroke="#238b82"
            strokeWidth="2"
            strokeLinejoin="round"
          />
        </>
      )}
      {!data.length && (
        <text className="chart-empty" x="230" y="72" textAnchor="middle">
          Starte die Simulation für einen Verlauf.
        </text>
      )}
    </svg>
  );
}
