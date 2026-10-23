import { lazy, Suspense, useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  ArrowDownToLine,
  ArrowLeft,
  ArrowRight,
  Check,
  ChevronDown,
  ChevronRight,
  CircleHelp,
  Code2,
  Copy,
  Download,
  FileUp,
  GripVertical,
  Layers3,
  Pause,
  Play,
  Plus,
  RotateCcw,
  Search,
  Settings2,
  ShieldCheck,
  SkipForward,
  Square,
  Terminal,
  Trash2,
  Undo2,
  Unplug,
  X,
} from "lucide-react";
import type {
  Bootstrap,
  ModulePackage,
  Project,
  SignalRef,
  Snapshot,
  Diagnostic,
} from "./types";
import { clone, key, same } from "./types";
import "./styles.css";
import { ThemeControl } from "./Theme";
const ScriptEditor = lazy(() =>
  import("./ScriptEditor").then((m) => ({ default: m.ScriptEditor })),
);
import { ScenarioPanel } from "./ScenarioPanel";
import { SignalRow } from "./SignalViews";
import { TracePanel } from "./TracePanel";

const stamp = (ms: number) =>
  `${Math.floor(ms / 60000)
    .toString()
    .padStart(
      2,
      "0",
    )}:${(Math.floor((ms % 60000) / 10) / 100).toFixed(2).padStart(5, "0")}`;
const familyName: Record<string, string> = {
  di: "Digital Input",
  do: "Digital Output",
  ai: "Analog Input",
  ao: "Analog Output",
  passive: "Abschluss",
};
const feedback =
  "// Wirksamer Ausgang → Sensorsignal\nfn react(output, previous, dt_s, time_s) {\n    if output > 0.5 { 1.0 } else { 0.0 }\n}";
const lag =
  "// Einfaches träges Reaktionsmodell (eigene Annahme)\nfn react(output, previous, dt_s, time_s) {\n    let target = 4.0 + output * 1.6;\n    let alpha = dt_s / (1.0 + dt_s);\n    previous + (target - previous) * alpha\n}";

function statefulExample(sources: SignalRef[]) {
  const active = sources.length
    ? sources.map((s) => `outputs["${key(s)}"] > 0.5`).join(" && ")
    : "true";
  return `// Eigene Annahme: digitale Rückmeldung nach 200 ms.\nfn react_state(outputs, previous, state, dt_s, time_s) {\n    if !state.contains("elapsed") { state.elapsed = 0.0; }\n    if ${active} { state.elapsed += dt_s; } else { state.elapsed = 0.0; }\n    #{value: if state.elapsed >= 0.2 { 1.0 } else { 0.0 }, state: state}\n}`;
}

let serverInstance = "";
async function api<T>(
  path: string,
  method = "GET",
  body?: unknown,
  instance = serverInstance,
): Promise<T> {
  const response = await fetch(`/api/${path}`, {
    method,
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      "X-VirtualWago-Client": "workbench",
      "X-VirtualWago-Instance": instance,
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    signal: AbortSignal.timeout(15000),
  });
  if (!response.ok) {
    const text = await response.text();
    try {
      throw new Error(JSON.parse(text).error ?? text);
    } catch (error) {
      if (error instanceof SyntaxError)
        throw new Error(text || `HTTP ${response.status}`);
      throw error;
    }
  }
  return response.json();
}
function download(name: string, content: unknown) {
  const url = URL.createObjectURL(
    new Blob(
      [
        typeof content === "string"
          ? content
          : JSON.stringify(content, null, 2) + "\n",
      ],
      {
        type: typeof content === "string" ? "text/plain" : "application/json",
      },
    ),
  );
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  link.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function App() {
  const [project, setProject] = useState<Project | null>(null);
  const [active, setActive] = useState<Project | null>(null);
  const [state, setState] = useState<Snapshot | null>(null);
  const [baseGeneration, setBaseGeneration] = useState(0);
  const [baseInstance, setBaseInstance] = useState("");
  const [selected, setSelected] = useState("do-bank");
  const [tab, setTab] = useState<
    "signals" | "reactions" | "events" | "scenarios"
  >("signals");
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all");
  const [connected, setConnected] = useState(false);
  const lastMessage = useRef(0);
  const [diagnostic, setDiagnostic] = useState<Diagnostic | null>(null);
  const [validatedCode, setValidatedCode] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [scriptId, setScriptId] = useState("valve-feedback");
  const [undo, setUndo] = useState<Project[]>([]);
  const [dragged, setDragged] = useState<string | null>(null);
  const [history, setHistory] = useState<
    { time: number; values: Record<string, number> }[]
  >([]);
  const [watched, setWatched] = useState("di-bank/ch1");
  const dirty =
    project !== null &&
    active !== null &&
    JSON.stringify(project) !== JSON.stringify(active);
  const dirtyRef = useRef(dirty);
  dirtyRef.current = dirty;
  const projectFile = useRef<HTMLInputElement>(null);
  const packageFile = useRef<HTMLInputElement>(null);
  const help = useRef<HTMLDialogElement>(null);
  const scriptFile = useRef<HTMLInputElement>(null);
  const historyRevision = useRef("");

  function observe(next: Snapshot) {
    if (next.instance !== serverInstance) return;
    setState((previous) =>
      !previous ||
      previous.instance !== next.instance ||
      next.generation > previous.generation ||
      (next.generation === previous.generation &&
        BigInt(next.sequence) >= BigInt(previous.sequence))
        ? next
        : previous,
    );
  }
  function accept(data: Bootstrap, keepDraft = false) {
    serverInstance = data.state.instance;
    setActive(data.project);
    observe(data.state);
    if (!keepDraft) {
      setProject(clone(data.project));
      setBaseGeneration(data.state.generation);
      setBaseInstance(data.state.instance);
      setUndo([]);
    }
  }
  useEffect(() => {
    if (!project) return;
    setSelected((old) =>
      project.modules.some((m) => m.id === old)
        ? old
        : (project.modules[0]?.id ?? ""),
    );
    setScriptId((old) =>
      project.reactions.some((r) => r.id === old)
        ? old
        : (project.reactions[0]?.id ?? ""),
    );
    const keys = project.modules.flatMap(
      (m) =>
        project.packages
          .find((p) => p.id === m.package)
          ?.channels.map((c) => `${m.id}/${c.id}`) ?? [],
    );
    setWatched((old) => (keys.includes(old) ? old : (keys[0] ?? "")));
  }, [project]);
  useEffect(() => {
    setDiagnostic(null);
    setValidatedCode("");
  }, [project?.reactions, scriptId]);
  useEffect(() => {
    let disposed = false;
    let socket: WebSocket | undefined;
    let timer: ReturnType<typeof setTimeout>;
    let generation = -1;
    async function connect() {
      try {
        const data = await api<Bootstrap>("bootstrap");
        if (disposed) return;
        accept(data, dirtyRef.current);
        generation = data.state.generation;
        socket = new WebSocket(
          `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/api/stream`,
        );
        socket.onopen = () => {
          lastMessage.current = performance.now();
        };
        socket.onmessage = (event) => {
          if (disposed) return;
          const next = JSON.parse(event.data) as Snapshot;
          if (next.instance !== serverInstance) {
            socket?.close();
            return;
          }
          lastMessage.current = performance.now();
          setConnected(true);
          observe(next);
          if (next.generation !== generation) {
            generation = next.generation;
            void api<Bootstrap>("bootstrap")
              .then((data) => {
                if (!disposed) accept(data, dirtyRef.current);
              })
              .catch((e) => setError(String(e)));
          }
        };
        socket.onclose = () => {
          if (!disposed) {
            lastMessage.current = 0;
            setConnected(false);
            timer = setTimeout(connect, 1500);
          }
        };
        socket.onerror = () => socket?.close();
      } catch (e) {
        if (!disposed) {
          setError(String(e));
          lastMessage.current = 0;
          setConnected(false);
          timer = setTimeout(connect, 2000);
        }
      }
    }
    const watchdog = setInterval(() => {
      if (
        lastMessage.current &&
        performance.now() - lastMessage.current > 1500
      ) {
        setConnected(false);
        // Recover an open but silent transport as well as a dead one.
        if (performance.now() - lastMessage.current > 5000) {
          lastMessage.current = 0;
          if (socket) {
            socket.onmessage = null;
            socket.onclose = null;
            socket.onerror = null;
            socket.close();
          }
          timer = setTimeout(connect, 250);
        }
      }
    }, 250);
    void connect();
    return () => {
      clearInterval(watchdog);
      disposed = true;
      clearTimeout(timer);
      socket?.close();
    };
  }, []);
  useEffect(() => {
    const warn = (event: BeforeUnloadEvent) => {
      if (dirtyRef.current) event.preventDefault();
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, []);
  useEffect(() => {
    if (!state) return;
    const revision = `${state.instance}/${state.generation}`;
    const changed = historyRevision.current !== revision;
    historyRevision.current = revision;
    setHistory((previous) => {
      if (changed) previous = [];
      if (previous.at(-1)?.time === state.time_ms) return previous;
      const retained =
        previous.at(-1) && previous.at(-1)!.time > state.time_ms
          ? []
          : previous;
      return [
        ...retained,
        {
          time: state.time_ms,
          values: Object.fromEntries(
            state.signals.map((s) => [key(s.signal), s.value]),
          ),
        },
      ].slice(-150);
    });
  }, [state?.tick, state?.generation, state?.instance]);

  async function work(task: () => Promise<void>) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await task();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }
  async function command(action: string, fields: Record<string, unknown> = {}) {
    if (!state || !connected) return;
    await work(async () =>
      observe(
        await api<Snapshot>("command", "POST", {
          generation: state.generation,
          command: { action, ...fields },
        }),
      ),
    );
  }
  function edit(change: (draft: Project) => void) {
    if (!project || state?.running) return;
    const next = clone(project);
    change(next);
    setUndo((previous) => [...previous, clone(project)].slice(-40));
    setProject(next);
    setNotice("");
  }
  async function apply() {
    if (!project) return;
    await work(async () => {
      accept(
        await api<Bootstrap>(
          "project",
          "PUT",
          {
            generation: baseGeneration,
            project,
          },
          baseInstance,
        ),
      );
      setNotice(
        "Projekt gespeichert. Modellzeit zurückgesetzt; Freigabe bleibt aus.",
      );
    });
  }
  function add(p: ModulePackage) {
    const id = `m-${crypto.randomUUID()}`;
    void work(async () => {
      const checked = await api<{ sha256: string }>(
        "packages/validate",
        "POST",
        p,
      );
      edit((draft) =>
        draft.modules.push({
          id,
          package: p.id,
          package_sha256: checked.sha256,
          label: p.title,
        }),
      );
      setSelected(id);
    });
  }
  function move(id: string, offset: number) {
    edit((draft) => {
      const index = draft.modules.findIndex((m) => m.id === id);
      const target = index + offset;
      if (index < 0 || target < 0 || target >= draft.modules.length) return;
      const [module] = draft.modules.splice(index, 1);
      draft.modules.splice(target, 0, module);
    });
  }
  async function importFile(
    file: File | undefined,
    kind: "project" | "package",
  ) {
    if (!file) return;
    await work(async () => {
      if (file.size > 512 * 1024)
        throw new Error("Die Datei darf höchstens 512 KiB groß sein.");
      const content: unknown = JSON.parse(await file.text());
      if (kind === "project") {
        const next = await api<Project>("project/validate", "POST", content);
        edit((draft) => Object.assign(draft, next));
        setNotice("Projekt als Entwurf geladen. Mit „Übernehmen“ aktivieren.");
      } else {
        const next = await api<{ package: ModulePackage; sha256: string }>(
          "packages/validate",
          "POST",
          content,
        );
        edit((draft) => {
          draft.packages = [
            ...draft.packages.filter((p) => p.id !== next.package.id),
            next.package,
          ];
          for (const m of draft.modules.filter(
            (m) => m.package === next.package.id,
          ))
            m.package_sha256 = next.sha256;
        });
        setNotice(
          `Modulpaket ${next.package.article} v${next.package.version} im Entwurf. Mit „Übernehmen“ prüfen und aktivieren.`,
        );
      }
    });
  }
  if (!project || !state)
    return (
      <div className="loading">
        <Layers3 size={40} />
        <h1>Simulationswerkstatt</h1>
        <p>{error || "Lokalen Simulationskern verbinden …"}</p>
      </div>
    );
  const editing = !state.running && connected && !busy;
  const controls = connected && !busy && !dirty && !state.fault;
  const instance = project.modules.find((m) => m.id === selected);
  const pack = project.packages.find((p) => p.id === instance?.package);
  const signals = new Map(state.signals.map((s) => [key(s.signal), s]));
  const names = (ref: SignalRef) =>
    `${project.modules.find((m) => m.id === ref.module)?.label ?? ref.module} · ${ref.channel}`;
  const allChannels = project.modules.flatMap((m) =>
    project.packages
      .find((p) => p.id === m.package)!
      .channels.map((c) => ({ m, c, ref: { module: m.id, channel: c.id } })),
  );
  const script = project.reactions.find((r) => r.id === scriptId);

  const packages = project.packages.filter(
    (p) =>
      (filter === "all" ||
        (filter === "digital"
          ? ["di", "do"].includes(p.family)
          : filter === "analog"
            ? ["ai", "ao"].includes(p.family)
            : p.family === "passive")) &&
      `${p.article} ${p.title}`.toLowerCase().includes(query.toLowerCase()),
  );

  return (
    <div className="app">
      <a className="skip" href="#rail">
        Zur Klemmenleiste
      </a>
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">
            <Layers3 size={24} />
          </span>
          <span>
            virtual<span className="brand-wago">WAGO</span>
            <small>SIMULATIONSWERKSTATT</small>
          </span>
        </div>
        <div className="top-context">
          <span className="breadcrumb">Projekte</span>
          <ChevronRight size={14} />
          <strong>{active?.name}</strong>
          <span className="tag subtle">Lokal</span>
        </div>
        <ThemeControl />
        <button
          className="icon-button help-button"
          aria-label="Hilfe öffnen"
          onClick={() => help.current?.showModal()}
        >
          <CircleHelp size={19} />
        </button>
        <span className={`connection ${connected ? "" : "lost"}`}>
          <i />
          {connected ? "Kern verbunden" : "Live-Daten veraltet"}
        </span>
      </header>
      <div className="workspace-heading">
        <div>
          <div className="eyebrow">VIRTUELLER K-BUS</div>
          <h1>Deine Anlage. Im Modell.</h1>
          <p>
            Module zusammenstellen, Signale beobachten, Reaktionen simulieren.
          </p>
        </div>
        <div className="offline-label">
          <Unplug size={15} />
          Offline-Simulation<span>Kein Gerätezugriff</span>
        </div>
      </div>
      <div className="projectbar">
        <div className="project-title">
          <Layers3 size={18} />
          <input
            aria-label="Projektname"
            value={project.name}
            maxLength={100}
            disabled={!editing}
            onChange={(e) =>
              edit((d) => {
                d.name = e.target.value;
              })
            }
          />
          <ChevronDown size={14} />
        </div>
        <div className="project-actions">
          <span className={`save-state ${dirty ? "unsaved" : ""}`}>
            {dirty ? (
              "Entwurf geändert"
            ) : (
              <>
                <Check size={13} />
                Gespeichert
              </>
            )}
          </span>
          <button
            className="button compact"
            disabled={!editing || !undo.length}
            onClick={() => {
              const previous = undo.at(-1);
              if (previous) {
                setProject(previous);
                setUndo(undo.slice(0, -1));
              }
            }}
          >
            <Undo2 size={15} />
            Rückgängig
          </button>
          {dirty && (
            <button
              className="button compact"
              disabled={!editing}
              onClick={() => {
                setProject(clone(active!));
                setBaseGeneration(state.generation);
                setBaseInstance(state.instance);
                setUndo([]);
              }}
            >
              Verwerfen
            </button>
          )}
          <button
            className="button compact"
            onClick={() => download("virtualwago-project.json", project)}
          >
            <Download size={15} />
            Export
          </button>
          <button
            className="button compact"
            disabled={!editing}
            onClick={() => projectFile.current?.click()}
          >
            <FileUp size={15} />
            Import
          </button>
          <button
            className="button primary compact"
            disabled={!editing || !dirty}
            onClick={() => void apply()}
          >
            <Check size={15} />
            Übernehmen
          </button>
        </div>
        <input
          className="visually-hidden"
          ref={projectFile}
          type="file"
          accept=".json,application/json"
          aria-label="Projektdatei importieren"
          onChange={(e) => {
            void importFile(e.target.files?.[0], "project");
            e.target.value = "";
          }}
        />
        <input
          className="visually-hidden"
          ref={packageFile}
          type="file"
          accept=".json,application/json"
          aria-label="Modulpaket importieren"
          onChange={(e) => {
            void importFile(e.target.files?.[0], "package");
            e.target.value = "";
          }}
        />
      </div>
      {(error || notice || !connected || state.fault) && (
        <div
          className={`message ${error || state.fault || !connected ? "error" : ""}`}
          role="status"
        >
          {!connected
            ? "Live-Verbindung unterbrochen. Werte sind möglicherweise veraltet; Bedienung bleibt gesperrt."
            : error || state.fault || notice}
          <button
            aria-label="Hinweis schließen"
            className="icon-button"
            onClick={() => {
              setError("");
              setNotice("");
            }}
          >
            <X size={15} />
          </button>
        </div>
      )}
      <div className="workbench">
        <aside className="catalog" aria-label="Modulkatalog">
          <div className="panel-heading">
            <h2>Modulkatalog</h2>
            <span className="count">{project.packages.length}</span>
          </div>
          <label className="search">
            <Search size={16} />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Artikel oder Modul suchen"
              aria-label="Module suchen"
            />
          </label>
          <div className="filter-tabs" aria-label="Modulfamilie">
            {[
              ["all", "Alle"],
              ["digital", "Digital"],
              ["analog", "Analog"],
            ].map(([id, label]) => (
              <button
                key={id}
                className={filter === id ? "active" : ""}
                aria-pressed={filter === id}
                onClick={() => setFilter(id)}
              >
                {label}
              </button>
            ))}
          </div>
          <div className="catalog-list">
            {packages.map((p) => (
              <div className={`catalog-item family-${p.family}`} key={p.id}>
                <div className="mini-module">
                  <span />
                  <span />
                  <span />
                  <span />
                </div>
                <div className="catalog-info">
                  <strong>{p.article}</strong>
                  <span>{p.title}</span>
                  <small>{familyName[p.family]}</small>
                </div>
                <button
                  className="add-module"
                  disabled={!editing}
                  aria-label={`${p.article} hinzufügen`}
                  onClick={() => add(p)}
                >
                  <Plus size={17} />
                </button>
              </div>
            ))}
            {!packages.length && (
              <p className="empty-small">Kein passendes Modul gefunden.</p>
            )}
          </div>
          <div className="catalog-footer">
            <span className="tag">SIGNALMODELLE</span>
            <p>
              Versionierte Pakete. Erkenntnisse und Grenzen bleiben je Modul
              sichtbar.
            </p>
            <button
              className="button"
              disabled={!editing}
              onClick={() => packageFile.current?.click()}
            >
              <Plus size={15} />
              Modulpaket laden
            </button>
          </div>
        </aside>
        <main className="main-panel" id="rail" tabIndex={-1}>
          <div className="rail-heading">
            <div>
              <h2>
                Klemmenleiste{" "}
                <span className="count">{project.modules.length} Module</span>
              </h2>
              <p>Module auswählen und in die gewünschte Reihenfolge ziehen.</p>
            </div>
            <span className="scope-tag">
              <ShieldCheck size={13} />
              Eigene Signalmodelle
            </span>
          </div>
          <div className="rail-viewport">
            <div className="din-rail" />
            <div
              className="rail-modules"
              role="list"
              aria-label="Virtuelle Klemmenleiste"
            >
              <div className="controller">
                <div className="controller-top">
                  <span className="controller-logo">virtualWAGO</span>
                  <span className="controller-type">OFFLINE CONTROLLER</span>
                </div>
                <div className="controller-leds">
                  <span>
                    <i className={state.running ? "on" : "amber"} />
                    {state.running ? "RUN" : "PAUSE"}
                  </span>
                  <span>
                    <i className={state.permit ? "on" : ""} />
                    MODEL I/O
                  </span>
                  <span>
                    <i className={state.fault ? "fault" : ""} />
                    FAULT
                  </span>
                </div>
                <div className="ethernet">
                  <div />
                  <div />
                </div>
                <div className="controller-bottom">
                  SIMULATION CORE<small>Rust · eigene Modellzeit</small>
                </div>
              </div>
              {project.modules.map((m, index) => {
                const p = project.packages.find((p) => p.id === m.package)!;
                const input = p.channels.filter(
                  (c) => c.direction === "input",
                ).length;
                const output = p.channels.length - input;
                return (
                  <div
                    key={m.id}
                    role="listitem"
                    className="rail-item"
                    onDragOver={(e) => {
                      if (editing) e.preventDefault();
                    }}
                    onDrop={(e) => {
                      e.preventDefault();
                      if (dragged && dragged !== m.id) {
                        const from = project.modules.findIndex(
                          (m) => m.id === dragged,
                        );
                        move(dragged, index - from);
                      }
                      setDragged(null);
                    }}
                  >
                    <button
                      className={`module-card family-${p.family} ${selected === m.id ? "selected" : ""} ${p.family === "passive" ? "passive" : ""}`}
                      aria-label={`${p.article} · ${m.label}`}
                      aria-pressed={selected === m.id}
                      draggable={editing}
                      onDragStart={() => setDragged(m.id)}
                      onDragEnd={() => setDragged(null)}
                      onClick={() => setSelected(m.id)}
                    >
                      <div className="module-cap">
                        <span>{p.family === "passive" ? "" : "WAGO"}</span>
                        <GripVertical size={12} />
                      </div>
                      <div className="module-label">
                        <strong>{p.article}</strong>
                        <small>{familyName[p.family]}</small>
                      </div>
                      <div className="terminal-grid">
                        {p.channels.map((c, n) => {
                          const v = signals.get(`${m.id}/${c.id}`);
                          return (
                            <span
                              className={`terminal ${v && v.value > c.min ? "lit" : ""}`}
                              key={c.id}
                            >
                              <small>{n + 1}</small>
                              <i />
                              <em>{c.kind === "analog" ? c.unit : ""}</em>
                            </span>
                          );
                        })}
                      </div>
                      {p.family === "passive" ? (
                        <div className="end-lines">
                          <i />
                          <i />
                          <i />
                        </div>
                      ) : (
                        <div className="module-foot">
                          <span>
                            {input || output} {p.family.toUpperCase()}
                            {p.family.startsWith("a") ? " · Analog" : ""}
                          </span>
                          <span className="module-screw" />
                        </div>
                      )}
                    </button>
                    <span className="slot-number">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                  </div>
                );
              })}
              {project.modules.length === 0 && (
                <div className="rail-empty">
                  <Plus size={28} />
                  <strong>Deine Klemmenleiste beginnt hier</strong>
                  <span>Füge links das erste Modul hinzu.</span>
                </div>
              )}
              <button
                className="rail-add"
                disabled={!editing}
                aria-label="Zum Modulkatalog"
                onClick={() =>
                  document
                    .querySelector<HTMLInputElement>(".search input")
                    ?.focus()
                }
              >
                <Plus size={23} />
                <span>
                  Modul
                  <br />
                  hinzufügen
                </span>
              </button>
            </div>
          </div>
          <div className="rail-caption">
            <span>
              <i className="legend-dot input" />
              Eingänge
            </span>
            <span>
              <i className="legend-dot output" />
              Ausgänge
            </span>
            <span>
              <i className="legend-dot analog" />
              Analogsignale
            </span>
            <span className="rail-hint">
              Stabile Instanz-IDs erhalten Skriptzuordnungen beim Verschieben.
            </span>
          </div>
          <div className="runbar">
            <div className="run-controls">
              <button
                className={`button ${state.running ? "" : "primary"}`}
                disabled={!controls}
                onClick={() => void command(state.running ? "pause" : "run")}
              >
                {state.running ? <Pause size={15} /> : <Play size={15} />}
                {state.running ? "Pause" : "Start"}
              </button>
              <button
                className="icon-button bordered"
                aria-label="Einzelschritt"
                disabled={!controls || state.running}
                onClick={() => void command("step")}
              >
                <SkipForward size={17} />
              </button>
              <button
                className="icon-button bordered"
                aria-label="Simulation stoppen"
                disabled={!connected || busy}
                onClick={() => void command("stop")}
              >
                <Square size={14} />
              </button>
              <button
                className="icon-button bordered"
                aria-label="Simulation zurücksetzen"
                disabled={!connected || busy}
                onClick={() => void command("reset")}
              >
                <RotateCcw size={16} />
              </button>
              <span className="divider" />
              <label className="speed">
                <select
                  aria-label="Simulationsgeschwindigkeit"
                  value={state.speed}
                  disabled={!controls}
                  onChange={(e) =>
                    void command("speed", { factor: Number(e.target.value) })
                  }
                >
                  {[1, 2, 5, 10].map((v) => (
                    <option key={v} value={v}>
                      {v}× Tempo
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <div className="run-clock">
              <span className={`status-dot ${state.running ? "on" : ""}`} />
              <span>
                {state.fault ? "Fehler" : state.running ? "Läuft" : "Pausiert"}
              </span>
              <strong>{stamp(state.time_ms)}</strong>
              <small>{state.tick} Zyklen</small>
            </div>
            <button
              className={`permit ${state.permit ? "enabled" : ""}`}
              disabled={!controls}
              role="switch"
              aria-checked={state.permit}
              aria-label="Modellfreigabe"
              onClick={() => void command("permit", { enabled: !state.permit })}
            >
              <span className="switch-track">
                <i />
              </span>
              <span>
                Modellfreigabe
                <small>
                  {state.permit
                    ? "Wirksame Ausgänge aktiv"
                    : "Wirksame Ausgänge bleiben 0"}
                </small>
              </span>
            </button>
          </div>
          <section className="data-panel">
            <div
              className="data-tabs"
              role="tablist"
              aria-label="Simulationsdaten"
            >
              {[
                ["signals", Activity, "Live-I/O"],
                ["reactions", Code2, "Reaktionsskripte"],
                ["events", Terminal, "Ereignisse"],
                ["scenarios", Check, "Szenarien"],
              ].map(([id, Icon, label]) => {
                const I = Icon as typeof Activity;
                return (
                  <button
                    key={id as string}
                    role="tab"
                    aria-selected={tab === id}
                    onClick={() => setTab(id as typeof tab)}
                    className={tab === id ? "active" : ""}
                  >
                    <I size={16} />
                    {label as string}
                    {id === "reactions" && (
                      <span className="count">{project.reactions.length}</span>
                    )}
                  </button>
                );
              })}
              <span className="data-meta">
                {state.signals.length} Kanäle · {project.tick_ms} ms
                Modellzyklus
              </span>
            </div>
            <div className="live-content" hidden={tab !== "signals"}>
              <div className="signal-table-wrap">
                <table className="signal-table">
                  <thead>
                    <tr>
                      <th>Signal</th>
                      <th>Richtung</th>
                      <th>Wert / Anforderung</th>
                      <th>Wirksam</th>
                      <th>Quelle</th>
                    </tr>
                  </thead>
                  <tbody>
                    {allChannels
                      .filter((v) => v.m.id === selected)
                      .map(({ m, c, ref }) => (
                        <SignalRow
                          key={key(ref)}
                          channel={c}
                          signal={signals.get(key(ref))}
                          name={m.label}
                          disabled={!controls}
                          onValue={(value) =>
                            void command("set_signal", { signal: ref, value })
                          }
                          onWatch={() => setWatched(key(ref))}
                        />
                      ))}
                  </tbody>
                </table>
                {!pack?.channels.length && (
                  <div className="empty-small">
                    Dieses Modul besitzt keine I/O-Kanäle. Wähle ein
                    Signalmodul.
                  </div>
                )}
              </div>
              <TracePanel
                history={history}
                watched={watched}
                onWatch={setWatched}
                connected={connected}
                revision={`${state.instance}/${state.generation}`}
                channels={allChannels.map((v) => ({
                  key: key(v.ref),
                  label: names(v.ref),
                  channel: v.c,
                }))}
              />
            </div>
            {tab === "reactions" && (
              <div className="reaction-content">
                <div className="script-list">
                  <div className="script-list-heading">
                    Reaktionsmodelle
                    <button
                      className="icon-button"
                      aria-label="Reaktionsskript hinzufügen"
                      disabled={!editing}
                      onClick={() => {
                        const target = allChannels.find(
                          (v) =>
                            v.c.direction === "input" &&
                            !project.reactions.some(
                              (r) => r.enabled && same(r.target, v.ref),
                            ),
                        );
                        if (!target) {
                          setError(
                            "Füge einen freien Eingang hinzu oder deaktiviere dessen bestehendes Skript.",
                          );
                          return;
                        }
                        const source = allChannels.find(
                          (v) => v.c.direction === "output",
                        );
                        const id = `r-${crypto.randomUUID()}`;
                        edit((d) =>
                          d.reactions.push({
                            id,
                            name: "Neue Reaktion",
                            enabled: false,
                            source: source?.ref ?? null,
                            target: target.ref,
                            code:
                              target.c.kind === "digital"
                                ? feedback
                                : `fn react(output, previous, dt_s, time_s) {\n    previous\n}`,
                          }),
                        );
                        setScriptId(id);
                      }}
                    >
                      <Plus size={16} />
                    </button>
                  </div>
                  {project.reactions.map((r) => (
                    <button
                      key={r.id}
                      className={`script-item ${scriptId === r.id ? "active" : ""}`}
                      onClick={() => setScriptId(r.id)}
                    >
                      <Code2 size={16} />
                      <span>
                        {r.name}
                        <small>{r.enabled ? "Aktiviert" : "Deaktiviert"}</small>
                      </span>
                      <i className={r.enabled ? "on" : ""} />
                    </button>
                  ))}
                </div>
                {script ? (
                  <div className="script-editor">
                    <div className="script-editor-heading">
                      <input
                        aria-label="Skriptname"
                        value={script.name}
                        disabled={!editing}
                        maxLength={100}
                        onChange={(e) =>
                          edit((d) => {
                            d.reactions.find((r) => r.id === scriptId)!.name =
                              e.target.value;
                          })
                        }
                      />
                      <label className="checkbox">
                        <input
                          type="checkbox"
                          checked={script.enabled}
                          disabled={!editing}
                          onChange={(e) =>
                            edit((d) => {
                              d.reactions.find(
                                (r) => r.id === scriptId,
                              )!.enabled = e.target.checked;
                            })
                          }
                        />
                        Aktiv
                      </label>
                      <button
                        className="icon-button"
                        aria-label="Reaktionsskript entfernen"
                        disabled={!editing}
                        onClick={() =>
                          edit((d) => {
                            d.reactions = d.reactions.filter(
                              (r) => r.id !== scriptId,
                            );
                          })
                        }
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                    <div className="script-bindings">
                      <label>
                        Ausgang lesen
                        <select
                          aria-label="Reaktionsquelle"
                          disabled={!editing}
                          value={script.source ? key(script.source) : ""}
                          onChange={(e) =>
                            edit((d) => {
                              const r = d.reactions.find(
                                (r) => r.id === scriptId,
                              )!;
                              r.sources = (r.sources ?? []).filter(
                                (s) => key(s) !== e.target.value,
                              );
                              r.source =
                                allChannels.find(
                                  (v) => key(v.ref) === e.target.value,
                                )?.ref ?? null;
                            })
                          }
                        >
                          <option value="">Nur Modellzeit</option>
                          {allChannels
                            .filter((v) => v.c.direction === "output")
                            .map((v) => (
                              <option key={key(v.ref)} value={key(v.ref)}>
                                {names(v.ref)}
                              </option>
                            ))}
                        </select>
                      </label>
                      <ChevronRight size={15} />
                      <label>
                        Eingang liefern
                        <select
                          aria-label="Reaktionsziel"
                          disabled={!editing}
                          value={key(script.target)}
                          onChange={(e) =>
                            edit((d) => {
                              const ref = allChannels.find(
                                (v) => key(v.ref) === e.target.value,
                              )!.ref;
                              d.reactions.find(
                                (r) => r.id === scriptId,
                              )!.target = ref;
                            })
                          }
                        >
                          {allChannels
                            .filter((v) => v.c.direction === "input")
                            .map((v) => (
                              <option key={key(v.ref)} value={key(v.ref)}>
                                {names(v.ref)}
                              </option>
                            ))}
                        </select>
                      </label>
                      <select
                        className="example-select"
                        aria-label="Skriptbeispiel auswählen"
                        value=""
                        disabled={!editing}
                        onChange={(e) =>
                          edit((d) => {
                            const r = d.reactions.find(
                              (r) => r.id === scriptId,
                            )!;
                            r.code = r.stateful
                              ? statefulExample([
                                  ...(r.source ? [r.source] : []),
                                  ...(r.sources ?? []),
                                ])
                              : e.target.value === "lag"
                                ? lag
                                : feedback;
                          })
                        }
                      >
                        <option value="" disabled>
                          Beispiel laden
                        </option>
                        {script.stateful ? (
                          <option value="state">
                            Verzögerte digitale Rückmeldung
                          </option>
                        ) : (
                          <>
                            <option value="digital">
                              Digitale Rückmeldung
                            </option>
                            <option value="lag">Träges Analogmodell</option>
                          </>
                        )}
                      </select>
                    </div>
                    <div className="script-file-actions">
                      <button
                        className="button compact"
                        disabled={!editing}
                        onClick={() => scriptFile.current?.click()}
                      >
                        <FileUp size={14} />
                        Skript laden
                      </button>
                      <button
                        className="button compact"
                        onClick={() =>
                          download(`${script.id}.rhai`, script.code)
                        }
                      >
                        <Download size={14} />
                        Skript exportieren
                      </button>
                      <input
                        className="visually-hidden"
                        ref={scriptFile}
                        type="file"
                        accept=".rhai,.txt,text/plain"
                        aria-label="Reaktionsskript importieren"
                        onChange={(event) => {
                          const file = event.target.files?.[0];
                          event.target.value = "";
                          if (file)
                            void work(async () => {
                              if (file.size > 8192)
                                throw new Error(
                                  "Ein Skript darf höchstens 8192 Byte groß sein.",
                                );
                              const code = await file.text();
                              edit((d) => {
                                d.reactions.find(
                                  (r) => r.id === script.id,
                                )!.code = code;
                              });
                            });
                        }}
                      />
                    </div>
                    <div className="script-file-actions">
                      <label>
                        <input
                          type="checkbox"
                          aria-label="Zustandsbehaftetes Modell"
                          checked={script.stateful ?? false}
                          disabled={!editing}
                          onChange={(e) =>
                            edit((d) => {
                              const r = d.reactions.find(
                                (r) => r.id === scriptId,
                              )!;
                              r.stateful = e.target.checked;
                              r.sources = [];
                              r.code = e.target.checked
                                ? statefulExample(r.source ? [r.source] : [])
                                : feedback;
                            })
                          }
                        />{" "}
                        Mehrere Quellen / Zustand
                      </label>
                      <button
                        className="button compact"
                        disabled={!editing}
                        onClick={() =>
                          void work(async () => {
                            const result = await api<{
                              valid: boolean;
                              diagnostic: Diagnostic | null;
                            }>("scripts/validate", "POST", {
                              code: script.code,
                              stateful: script.stateful ?? false,
                            });
                            setDiagnostic(result.diagnostic);
                            setValidatedCode(result.valid ? script.code : "");
                          })
                        }
                      >
                        Syntax prüfen
                      </button>
                    </div>
                    {script.stateful && (
                      <fieldset className="source-picker">
                        <legend>
                          Weitere wirksame Ausgänge (Map-Schlüssel =
                          Instanz/Kanal)
                        </legend>
                        {allChannels
                          .filter(
                            (v) =>
                              v.c.direction === "output" &&
                              (!script.source || !same(v.ref, script.source)),
                          )
                          .map((v) => (
                            <label key={key(v.ref)}>
                              <input
                                type="checkbox"
                                disabled={!editing}
                                checked={(script.sources ?? []).some((s) =>
                                  same(s, v.ref),
                                )}
                                onChange={(e) =>
                                  edit((d) => {
                                    const r = d.reactions.find(
                                      (r) => r.id === scriptId,
                                    )!;
                                    r.sources = e.target.checked
                                      ? [...(r.sources ?? []), v.ref]
                                      : (r.sources ?? []).filter(
                                          (s) => !same(s, v.ref),
                                        );
                                  })
                                }
                              />
                              {names(v.ref)} <code>{key(v.ref)}</code>
                            </label>
                          ))}
                      </fieldset>
                    )}
                    {diagnostic && (
                      <p className="validation-error" role="status">
                        {diagnostic.line
                          ? `Zeile ${diagnostic.line}, Spalte ${diagnostic.column ?? 1}: `
                          : ""}
                        {diagnostic.message}
                      </p>
                    )}
                    {validatedCode === script.code && (
                      <p role="status">
                        Syntax gültig. Laufzeit und Reaktion mit einem Szenario
                        prüfen.
                      </p>
                    )}
                    <Suspense fallback={<p>Editor laden …</p>}>
                      <ScriptEditor
                        code={script.code}
                        disabled={!editing}
                        diagnostic={diagnostic}
                        onChange={(code) =>
                          edit((d) => {
                            d.reactions.find((r) => r.id === scriptId)!.code =
                              code;
                          })
                        }
                      />
                    </Suspense>
                    <div className="code-footer">
                      <span>
                        {script.stateful
                          ? "Rhai · Ergebnis = #{value, state} · outputs = wirksame Ausgänge"
                          : "Rhai · Ergebnis = neuer Eingangswert · output = wirksamer Ausgang"}
                      </span>
                      <span>20.000 Operationen / Aufruf</span>
                    </div>
                  </div>
                ) : (
                  <div className="empty-small">
                    Wähle ein Reaktionsskript oder füge eines hinzu.
                  </div>
                )}
              </div>
            )}
            {tab === "scenarios" && (
              <ScenarioPanel
                project={project}
                editing={editing}
                connected={connected}
                edit={edit}
                run={(id) => api("scenarios/run", "POST", { project, id })}
              />
            )}
            {tab === "events" && (
              <div className="event-list">
                {state.events
                  .slice()
                  .reverse()
                  .map((e, i) => (
                    <div
                      className={`event ${e.level}`}
                      key={`${state.sequence}-${i}`}
                    >
                      <time>{stamp(e.time_ms)}</time>
                      <span>
                        {e.level === "error"
                          ? "Fehler"
                          : e.level === "warning"
                            ? "Warnung"
                            : "Info"}
                      </span>
                      <p>{e.message}</p>
                    </div>
                  ))}
              </div>
            )}
          </section>
        </main>
        <aside className="inspector" aria-label="Moduleigenschaften">
          <div className="panel-heading">
            <h2>Moduleigenschaften</h2>
            <Settings2 size={16} />
          </div>
          {instance && pack ? (
            <>
              <div className={`inspector-summary family-${pack.family}`}>
                <div className="mini-module large">
                  <span />
                  <span />
                  <span />
                  <span />
                </div>
                <span>
                  <strong>{pack.article}</strong>
                  <small>{pack.title}</small>
                </span>
              </div>
              <label className="field">
                Bezeichnung
                <input
                  value={instance.label}
                  disabled={!editing}
                  maxLength={100}
                  onChange={(e) =>
                    edit((d) => {
                      d.modules.find((m) => m.id === selected)!.label =
                        e.target.value;
                    })
                  }
                />
              </label>
              <dl className="properties">
                <div>
                  <dt>Position</dt>
                  <dd>
                    {project.modules.findIndex((m) => m.id === selected) + 1}{" "}
                    von {project.modules.length}
                  </dd>
                </div>
                <div>
                  <dt>Modellversion</dt>
                  <dd>{pack.version}</dd>
                </div>
                <div>
                  <dt>Kanäle</dt>
                  <dd>{pack.channels.length}</dd>
                </div>
                <div>
                  <dt>Familie</dt>
                  <dd>{familyName[pack.family]}</dd>
                </div>
              </dl>
              <div className="inspector-actions">
                <button
                  className="button"
                  aria-label="Modul nach links"
                  disabled={!editing || project.modules[0]?.id === selected}
                  onClick={() => move(selected, -1)}
                >
                  <ArrowLeft size={15} />
                </button>
                <button
                  className="button"
                  aria-label="Modul nach rechts"
                  disabled={!editing || project.modules.at(-1)?.id === selected}
                  onClick={() => move(selected, 1)}
                >
                  <ArrowRight size={15} />
                </button>
                <button
                  className="button"
                  aria-label="Modul duplizieren"
                  disabled={!editing}
                  onClick={() => {
                    const id = `m-${crypto.randomUUID()}`;
                    edit((d) => {
                      const n = d.modules.findIndex((m) => m.id === selected);
                      d.modules.splice(n + 1, 0, {
                        ...clone(instance),
                        id,
                        label: `${instance.label.slice(0, 85)} (Kopie)`,
                      });
                    });
                    setSelected(id);
                  }}
                >
                  <Copy size={15} />
                </button>
                <button
                  className="button danger"
                  aria-label="Modul entfernen"
                  disabled={!editing}
                  onClick={() => {
                    edit((d) => {
                      d.modules = d.modules.filter((m) => m.id !== selected);
                      d.reactions = d.reactions.filter(
                        (r) =>
                          r.target.module !== selected &&
                          r.source?.module !== selected &&
                          !(r.sources ?? []).some((s) => s.module === selected),
                      );
                    });
                    setSelected(
                      project.modules.find((m) => m.id !== selected)?.id ?? "",
                    );
                  }}
                >
                  <Trash2 size={15} />
                </button>
              </div>
              <div className="inspector-section">
                <h3>Modellumfang</h3>
                <p>{pack.description}</p>
                <span className="tag model-tag">
                  <ShieldCheck size={12} />
                  Offline-Signalmodell
                </span>
                <p className="assumptions">{pack.assumptions}</p>
              </div>
              <div className="inspector-section">
                <h3>Quellenbindung</h3>
                <code className="source-path">{pack.evidence}</code>
                <small className="digest">
                  SHA-256 {instance.package_sha256.slice(0, 12)}…
                </small>
                <button
                  className="text-button"
                  onClick={() => download(`${pack.article}-module.json`, pack)}
                >
                  <ArrowDownToLine size={14} />
                  Modulpaket exportieren
                </button>
              </div>
              <div className="instance-id">
                <span>Stabile Instanz-ID</span>
                <code>{instance.id}</code>
              </div>
            </>
          ) : (
            <div className="empty-small">
              Wähle ein Modul in der Klemmenleiste.
            </div>
          )}
        </aside>
      </div>
      <footer className="statusbar">
        <span>
          <ShieldCheck size={13} />
          Simulation ohne WAGO / CODESYS
        </span>
        <span>
          Projekt v{state.generation} · Lokale Modellzeit · keine
          Echtzeitgarantie
        </span>
        <span>
          virtualWAGO <strong>Workbench 0.1</strong>
        </span>
      </footer>
      <dialog ref={help} className="help-dialog">
        <button
          className="icon-button close-dialog"
          aria-label="Hilfe schließen"
          onClick={() => help.current?.close()}
        >
          <X size={20} />
        </button>
        <div className="eyebrow">ERSTE SCHRITTE</div>
        <h2>Von der Klemme zur Reaktion</h2>
        <ol>
          <li>
            Module links hinzufügen oder in der Leiste auswählen. Änderungen
            bleiben zunächst im Entwurf.
          </li>
          <li>
            Mit „Übernehmen“ prüfen, speichern und aktivieren. Dabei werden
            Modellzeit und Freigabe zurückgesetzt.
          </li>
          <li>
            Am Ausgang einen Testwert vorgeben und die Modellfreigabe
            einschalten.
          </li>
          <li>
            „Start“ oder „Einzelschritt“ ausführen. Reaktionsskripte lesen
            wirksame Ausgänge und liefern Eingänge zurück.
          </li>
        </ol>
        <p>
          <strong>Pause</strong> friert Zeit und Reaktionen ein.{" "}
          <strong>Stopp</strong> entzieht zusätzlich die Freigabe und setzt
          wirksame Ausgänge auf null.
        </p>
        <p>
          Modulpakete enthalten Kanäle, Signalcodecs, Version und
          Quellenbindung. Ein Import benötigt keinen neuen Rust-Build, solange
          die verwendeten Codecs unterstützt sind. Skripte haben keinen Datei-,
          Netzwerk- oder Gerätezugriff.
        </p>
      </dialog>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
