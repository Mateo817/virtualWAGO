import { useEffect, useRef, useState } from "react";
import type { Channel, Sample } from "./types";
type TraceChannel = { key: string; label: string; channel: Channel };
type Recording = {
  schema: 1;
  scope: "offline_observation";
  revision: string;
  channels: TraceChannel[];
  samples: Sample[];
};
const colors = ["#299e91", "#cb8d22", "#6b8fe0", "#d978a2"];
export function parseRecording(text: string): Recording {
  if (text.length > 2 * 1024 * 1024)
    throw new Error("Aufzeichnung darf höchstens 2 MiB groß sein.");
  const value = JSON.parse(text) as Recording;
  if (
    value.schema !== 1 ||
    value.scope !== "offline_observation" ||
    typeof value.revision !== "string" ||
    !Array.isArray(value.channels) ||
    value.channels.length < 1 ||
    value.channels.length > 4 ||
    !Array.isArray(value.samples) ||
    value.samples.length < 1 ||
    value.samples.length > 5000
  )
    throw new Error("Ungültige Aufzeichnung.");
  const keys = new Set<string>();
  for (const c of value.channels) {
    if (
      typeof c.key !== "string" ||
      c.key.length > 162 ||
      keys.has(c.key) ||
      typeof c.label !== "string" ||
      c.label.length > 200 ||
      !c.channel ||
      !Number.isFinite(c.channel.min) ||
      !Number.isFinite(c.channel.max) ||
      c.channel.min >= c.channel.max ||
      Math.abs(c.channel.min) > 1e9 ||
      Math.abs(c.channel.max) > 1e9 ||
      typeof c.channel.unit !== "string" ||
      c.channel.unit.length > 20
    )
      throw new Error("Ungültiger Aufzeichnungskanal.");
    keys.add(c.key);
  }
  let last = -1;
  for (const s of value.samples) {
    if (
      !Number.isSafeInteger(s.time) ||
      s.time < 0 ||
      s.time <= last ||
      !s.values ||
      typeof s.values !== "object" ||
      Object.keys(s.values).length !== keys.size
    )
      throw new Error("Ungültige Zeitfolge.");
    for (const c of value.channels) {
      const v = s.values[c.key];
      if (!Number.isFinite(v) || v < c.channel.min || v > c.channel.max)
        throw new Error("Ungültiger Signalwert.");
    }
    last = s.time;
  }
  return value;
}
export function TracePanel({
  history,
  channels,
  watched,
  onWatch,
  revision,
  connected,
}: {
  history: Sample[];
  channels: TraceChannel[];
  watched: string;
  onWatch: (v: string) => void;
  revision: string;
  connected: boolean;
}) {
  const [extra, setExtra] = useState<string[]>([]);
  const [recording, setRecording] = useState(false);
  const [trace, setTrace] = useState<Recording | null>(null);
  const [replay, setReplay] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [cursor, setCursor] = useState(0);
  const [error, setError] = useState("");
  const file = useRef<HTMLInputElement>(null);
  const previousRevision = useRef(revision);
  const watchedChannels = channels
    .filter((c) => [watched, ...extra].includes(c.key))
    .slice(0, 4);
  useEffect(() => {
    setExtra((old) =>
      old.filter((k) => k !== watched && channels.some((c) => c.key === k)),
    );
  }, [channels.map((c) => c.key).join("|"), watched]);
  useEffect(() => {
    if (previousRevision.current !== revision) {
      setRecording(false);
      setPlaying(false);
      previousRevision.current = revision;
    }
  }, [revision]);
  useEffect(() => {
    if (!recording || !connected) return;
    const sample = history.at(-1);
    if (!sample) return;
    setTrace((old) => {
      if (!old) return old;
      const last = old.samples.at(-1)?.time ?? -1;
      if (sample.time < last) {
        setRecording(false);
        return old;
      }
      if (sample.time === last) return old;
      if (old.samples.length >= 5000) {
        setRecording(false);
        return old;
      }
      const values = Object.fromEntries(
        old.channels.map((c) => [c.key, sample.values[c.key]]),
      );
      if (Object.values(values).some((v) => !Number.isFinite(v))) return old;
      return {
        ...old,
        samples: [...old.samples, { time: sample.time, values }],
      };
    });
  }, [history, recording, connected]);
  useEffect(() => {
    if (!connected) setRecording(false);
  }, [connected]);
  useEffect(() => {
    if (!playing || !replay || !trace) return;
    const next = trace.samples[cursor + 1];
    if (!next) {
      setPlaying(false);
      return;
    }
    const delay = Math.max(
      10,
      Math.min(1000, next.time - trace.samples[cursor].time),
    );
    const timer = setTimeout(() => setCursor((c) => c + 1), delay);
    return () => clearTimeout(timer);
  }, [playing, replay, trace, cursor]);
  const samples = replay
    ? (trace?.samples.slice(0, cursor + 1) ?? [])
    : history;
  const displayChannels = replay ? (trace?.channels ?? []) : watchedChannels;
  const last = samples.at(-1)?.time ?? 0;
  const start = Math.max(samples[0]?.time ?? 0, last - 10000);
  const span = Math.max(1000, last - start);
  const exportFile = (csv = false) => {
    if (!trace?.samples.length) return;
    const content = csv
      ? [
          "time_ms," +
            trace.channels.map((c) => JSON.stringify(c.key)).join(","),
          ...trace.samples.map((s) =>
            [s.time, ...trace.channels.map((c) => s.values[c.key])].join(","),
          ),
        ].join("\n")
      : JSON.stringify(trace, null, 2);
    const url = URL.createObjectURL(
      new Blob([content], { type: csv ? "text/csv" : "application/json" }),
    );
    const link = document.createElement("a");
    link.href = url;
    link.download = `virtualwago-recording.${csv ? "csv" : "json"}`;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };
  return (
    <div className="trend trace-panel">
      <div className="trend-title">
        <span>
          {replay ? "Aufzeichnung · Wiedergabe" : "Signalverlauf · Live"}
        </span>
        <select
          aria-label="Signal für Verlauf"
          value={watched}
          disabled={replay || recording}
          onChange={(e) => onWatch(e.target.value)}
        >
          {channels.map((c) => (
            <option key={c.key} value={c.key}>
              {c.label}
            </option>
          ))}
        </select>
      </div>
      <details>
        <summary>Weitere Signale vergleichen (max. 4)</summary>
        <div className="source-picker">
          {channels
            .filter((c) => c.key !== watched)
            .map((c) => (
              <label key={c.key}>
                <input
                  type="checkbox"
                  disabled={
                    recording ||
                    replay ||
                    (!extra.includes(c.key) && extra.length >= 3)
                  }
                  checked={extra.includes(c.key)}
                  onChange={(e) =>
                    setExtra((old) =>
                      e.target.checked
                        ? [...old, c.key]
                        : old.filter((k) => k !== c.key),
                    )
                  }
                />
                {c.label}
              </label>
            ))}
        </div>
      </details>
      <svg
        className="trend-svg"
        viewBox="0 0 460 140"
        role="img"
        aria-label="Mehrere Signalverläufe, je Kanal auf den Messbereich normiert"
      >
        {[22, 67, 112].map((y) => (
          <line
            key={y}
            x1="30"
            x2="440"
            y1={y}
            y2={y}
            className="chart-grid"
            strokeDasharray="3 4"
          />
        ))}
        <text x="0" y="26">
          100%
        </text>
        <text x="4" y="115">
          0%
        </text>
        {displayChannels.map((c, i) => {
          const points = samples
            .filter((s) => s.time >= start && s.values[c.key] !== undefined)
            .map(
              (s) =>
                `${30 + ((s.time - start) / span) * 410},${112 - ((s.values[c.key] - c.channel.min) / (c.channel.max - c.channel.min)) * 90}`,
            )
            .join(" ");
          return (
            <polyline
              key={c.key}
              data-signal={c.key}
              points={points}
              fill="none"
              stroke={colors[i]}
              strokeWidth="2"
            />
          );
        })}
        {!samples.length && (
          <text x="230" y="72" textAnchor="middle">
            Starte die Simulation für einen Verlauf.
          </text>
        )}
      </svg>
      <div className="trace-legend">
        {displayChannels.map((c, i) => (
          <span key={c.key}>
            <i style={{ background: colors[i] }} />
            {c.label}: {samples.at(-1)?.values[c.key] ?? "—"} {c.channel.unit}{" "}
            <small>
              ({c.channel.min}–{c.channel.max})
            </small>
          </span>
        ))}
      </div>
      <div className="trace-actions">
        <button
          className="button compact"
          disabled={!connected || !watchedChannels.length || replay}
          onClick={() => {
            if (recording) setRecording(false);
            else {
              setTrace({
                schema: 1,
                scope: "offline_observation",
                revision,
                channels: structuredClone(watchedChannels),
                samples: [],
              });
              setRecording(true);
              setError("");
            }
          }}
        >
          {recording ? "Aufnahme stoppen" : "Aufzeichnen"}
        </button>
        <button
          className="button compact"
          disabled={!trace?.samples.length || recording}
          onClick={() => {
            setReplay((v) => !v);
            setPlaying(false);
            setCursor(0);
          }}
        >
          {replay ? "Zur Live-Ansicht" : "Wiedergabe"}
        </button>
        <button
          className="button compact"
          disabled={!trace?.samples.length || recording}
          onClick={() => exportFile()}
        >
          JSON exportieren
        </button>
        <button
          className="button compact"
          disabled={!trace?.samples.length || recording}
          onClick={() => exportFile(true)}
        >
          CSV exportieren
        </button>
        <button
          className="button compact"
          disabled={recording}
          onClick={() => file.current?.click()}
        >
          Aufzeichnung laden
        </button>
        <input
          ref={file}
          className="visually-hidden"
          type="file"
          accept=".json"
          aria-label="Aufzeichnung importieren"
          onChange={async (e) => {
            const f = e.target.files?.[0];
            e.target.value = "";
            if (!f) return;
            try {
              if (f.size > 2 * 1024 * 1024)
                throw new Error("Aufzeichnung zu groß.");
              const next = parseRecording(await f.text());
              setTrace(next);
              setReplay(true);
              setCursor(0);
              setPlaying(false);
              setError("");
            } catch (e) {
              setError(String(e));
            }
          }}
        />
      </div>
      {replay && trace && (
        <div className="trace-replay">
          <button
            className="button compact"
            onClick={() => {
              if (cursor === trace.samples.length - 1) setCursor(0);
              setPlaying((v) => !v);
            }}
          >
            {playing ? "Wiedergabe pausieren" : "Wiedergabe starten"}
          </button>
          <input
            type="range"
            aria-label="Wiedergabeposition"
            min={0}
            max={trace.samples.length - 1}
            value={cursor}
            onChange={(e) => {
              setPlaying(false);
              setCursor(Number(e.target.value));
            }}
          />
          <span>
            {trace.samples[cursor]?.time} ms · {cursor + 1}/
            {trace.samples.length}
          </span>
          <p>
            Aufzeichnung aus {trace.revision}. Reine Anzeige, keine Testbefehle.
          </p>
        </div>
      )}
      {error && (
        <p role="status" className="validation-error">
          {error}
        </p>
      )}
      <div className="trend-footer">
        <span>
          {recording
            ? `Aufnahme · ${trace?.samples.length ?? 0}/5000 Samples`
            : replay
              ? `${last} ms Modellzeit`
              : "Letzte 10 s Modellzeit"}
        </span>
        <span>Anzeigeabtastung ≈ 100 ms · kein Zyklusrekorder</span>
      </div>
    </div>
  );
}
