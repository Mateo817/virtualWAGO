import { useEffect, useRef, useState } from "react";
import type { Project, ScenarioReport, SignalRef } from "./types";
import { key } from "./types";
export function ScenarioPanel({
  project,
  editing,
  connected,
  edit,
  run,
}: {
  project: Project;
  editing: boolean;
  connected: boolean;
  edit: (change: (p: Project) => void) => void;
  run: (id: string) => Promise<ScenarioReport>;
}) {
  const [selected, setSelected] = useState("");
  const [report, setReport] = useState<ScenarioReport | null>(null);
  const [error, setError] = useState("");
  const [running, setRunning] = useState(false);
  const currentSelection = useRef(selected);
  currentSelection.current = selected;
  const currentProject = useRef("");
  currentProject.current = JSON.stringify(project);
  const scenarios = project.scenarios ?? [];
  const scenario = scenarios.find((s) => s.id === selected);
  const channels = project.modules.flatMap((m) =>
    (project.packages.find((p) => p.id === m.package)?.channels ?? []).map(
      (c) => ({
        ref: { module: m.id, channel: c.id },
        c,
        label: `${m.label} · ${c.label}`,
      }),
    ),
  );
  useEffect(() => {
    setSelected((old) =>
      scenarios.some((s) => s.id === old) ? old : (scenarios[0]?.id ?? ""),
    );
    setReport(null);
    setError("");
  }, [project]);
  const signalSelect = (
    ref: SignalRef,
    inputOnly: boolean,
    change: (s: SignalRef) => void,
  ) => (
    <select
      aria-label={inputOnly ? "Prüfsignal" : "Testsignal"}
      disabled={!editing}
      value={key(ref)}
      onChange={(e) => {
        const v = channels.find((c) => key(c.ref) === e.target.value);
        if (v) change(v.ref);
      }}
    >
      {channels
        .filter((v) => !inputOnly || v.c.direction === "input")
        .map((v) => (
          <option value={key(v.ref)} key={key(v.ref)}>
            {v.label}
          </option>
        ))}
    </select>
  );
  return (
    <div className="scenario-panel">
      <div className="panel-heading">
        <h2>Reaktionen prüfen</h2>
        <button
          className="button compact"
          disabled={!editing || scenarios.length >= 16}
          onClick={() => {
            const target = channels.find((v) => v.c.direction === "input");
            if (!target) {
              setError("Ein Szenario benötigt einen Eingang.");
              return;
            }
            const source = channels.find((v) => v.c.direction === "output");
            const id = `s-${crypto.randomUUID()}`;
            edit((p) => {
              p.scenarios = [
                ...(p.scenarios ?? []),
                {
                  id,
                  name: "Neue Reaktionsprüfung",
                  steps: [
                    {
                      at_ms: 0,
                      permit: true,
                      set: source
                        ? [{ signal: source.ref, value: source.c.max }]
                        : [],
                      expect: [
                        {
                          signal: target.ref,
                          min: target.c.max,
                          max: target.c.max,
                          within_ms: project.tick_ms * 10,
                        },
                      ],
                    },
                  ],
                },
              ];
            });
            setSelected(id);
          }}
        >
          Szenario hinzufügen
        </button>
      </div>
      <p>
        Testvorgaben laufen in einer eigenen Modellinstanz. Der aktive Lauf
        bleibt unverändert. Eine Prüfung besteht, sobald der Eingang innerhalb
        der Frist im erwarteten Bereich liegt.
      </p>
      <div className="scenario-toolbar">
        <select
          aria-label="Szenario auswählen"
          value={selected}
          onChange={(e) => {
            setSelected(e.target.value);
            setReport(null);
          }}
        >
          {scenarios.map((s) => (
            <option value={s.id} key={s.id}>
              {s.name}
            </option>
          ))}
        </select>
        <button
          className="button primary"
          disabled={!scenario || !connected || running}
          onClick={async () => {
            if (!scenario) return;
            setRunning(true);
            setError("");
            setReport(null);
            try {
              const revision = currentProject.current;
              const next = await run(scenario.id);
              if (
                revision === currentProject.current &&
                currentSelection.current === next.id
              )
                setReport(next);
            } catch (e) {
              setError(String(e));
            } finally {
              setRunning(false);
            }
          }}
        >
          {running ? "Prüfung läuft …" : "Szenario prüfen"}
        </button>
        <button
          className="button danger"
          disabled={!editing || !scenario || running}
          onClick={() =>
            edit((p) => {
              p.scenarios = (p.scenarios ?? []).filter(
                (s) => s.id !== selected,
              );
            })
          }
        >
          Entfernen
        </button>
      </div>
      {scenario && (
        <fieldset disabled={!editing || running}>
          <legend>Szenariokonfiguration · {project.tick_ms} ms Raster</legend>
          <label>
            Name{" "}
            <input
              aria-label="Szenarioname"
              maxLength={100}
              value={scenario.name}
              onChange={(e) =>
                edit((p) => {
                  p.scenarios!.find((s) => s.id === selected)!.name =
                    e.target.value;
                })
              }
            />
          </label>
          {scenario.steps.map((step, i) => (
            <div className="scenario-step" key={i}>
              <div className="scenario-toolbar">
                <strong>Schritt {i + 1}</strong>
                <label>
                  Zeit (ms)
                  <input
                    aria-label={`Schritt ${i + 1} Zeit`}
                    type="number"
                    min={0}
                    step={project.tick_ms}
                    value={step.at_ms}
                    onChange={(e) =>
                      edit((p) => {
                        p.scenarios!.find((s) => s.id === selected)!.steps[
                          i
                        ].at_ms = Number(e.target.value);
                      })
                    }
                  />
                </label>
                <label>
                  Freigabe
                  <select
                    aria-label={`Schritt ${i + 1} Freigabe`}
                    value={step.permit === null ? "keep" : String(step.permit)}
                    onChange={(e) =>
                      edit((p) => {
                        p.scenarios!.find((s) => s.id === selected)!.steps[
                          i
                        ].permit =
                          e.target.value === "keep"
                            ? null
                            : e.target.value === "true";
                      })
                    }
                  >
                    <option value="keep">Unverändert</option>
                    <option value="true">Ein</option>
                    <option value="false">Aus</option>
                  </select>
                </label>
                <button
                  className="button compact"
                  onClick={() =>
                    edit((p) => {
                      p.scenarios!.find((s) => s.id === selected)!.steps.splice(
                        i,
                        1,
                      );
                    })
                  }
                >
                  Schritt entfernen
                </button>
              </div>
              {step.set.map((v, j) => (
                <div className="scenario-toolbar" key={j}>
                  <span>Testvorgabe</span>
                  {signalSelect(v.signal, false, (ref) =>
                    edit((p) => {
                      p.scenarios!.find((s) => s.id === selected)!.steps[i].set[
                        j
                      ].signal = ref;
                    }),
                  )}
                  <input
                    aria-label="Testwert"
                    type="number"
                    step="any"
                    value={v.value}
                    onChange={(e) =>
                      edit((p) => {
                        p.scenarios!.find((s) => s.id === selected)!.steps[
                          i
                        ].set[j].value = Number(e.target.value);
                      })
                    }
                  />
                  <button
                    className="button compact"
                    onClick={() =>
                      edit((p) => {
                        p.scenarios!.find((s) => s.id === selected)!.steps[
                          i
                        ].set.splice(j, 1);
                      })
                    }
                  >
                    Vorgabe entfernen
                  </button>
                </div>
              ))}
              {step.expect.map((v, j) => (
                <div className="scenario-toolbar expectation" key={j}>
                  <span>Erwartung</span>
                  {signalSelect(v.signal, true, (ref) =>
                    edit((p) => {
                      p.scenarios!.find((s) => s.id === selected)!.steps[
                        i
                      ].expect[j].signal = ref;
                    }),
                  )}
                  {(
                    [
                      ["min", "Minimum"],
                      ["max", "Maximum"],
                      ["within_ms", "Frist (ms)"],
                    ] as const
                  ).map(([field, label]) => (
                    <label key={field}>
                      {label}
                      <input
                        aria-label={label}
                        type="number"
                        step={field === "within_ms" ? project.tick_ms : "any"}
                        value={v[field]}
                        onChange={(e) =>
                          edit((p) => {
                            p.scenarios!.find((s) => s.id === selected)!.steps[
                              i
                            ].expect[j][field] = Number(e.target.value);
                          })
                        }
                      />
                    </label>
                  ))}
                  <button
                    className="button compact"
                    onClick={() =>
                      edit((p) => {
                        p.scenarios!.find((s) => s.id === selected)!.steps[
                          i
                        ].expect.splice(j, 1);
                      })
                    }
                  >
                    Prüfung entfernen
                  </button>
                </div>
              ))}
              <div className="scenario-toolbar">
                <button
                  className="button compact"
                  disabled={step.set.length >= 16}
                  onClick={() => {
                    const v = channels.find((v) => v.c.direction === "output");
                    if (v)
                      edit((p) => {
                        p.scenarios!.find((s) => s.id === selected)!.steps[
                          i
                        ].set.push({ signal: v.ref, value: 0 });
                      });
                  }}
                >
                  Vorgabe hinzufügen
                </button>
                <button
                  className="button compact"
                  disabled={step.expect.length >= 16}
                  onClick={() => {
                    const v = channels.find((v) => v.c.direction === "input");
                    if (v)
                      edit((p) => {
                        p.scenarios!.find((s) => s.id === selected)!.steps[
                          i
                        ].expect.push({
                          signal: v.ref,
                          min: v.c.min,
                          max: v.c.max,
                          within_ms: project.tick_ms * 10,
                        });
                      });
                  }}
                >
                  Prüfung hinzufügen
                </button>
              </div>
            </div>
          ))}
          <button
            className="button"
            disabled={scenario.steps.length >= 64}
            onClick={() =>
              edit((p) => {
                const s = p.scenarios!.find((s) => s.id === selected)!;
                s.steps.push({
                  at_ms: (s.steps.at(-1)?.at_ms ?? 0) + project.tick_ms * 10,
                  permit: null,
                  set: [],
                  expect: [],
                });
              })
            }
          >
            Schritt hinzufügen
          </button>
        </fieldset>
      )}
      {error && (
        <p role="status" className="validation-error">
          {error}
        </p>
      )}
      {report && (
        <div
          className={`scenario-result ${report.passed ? "pass" : "fail"}`}
          role="status"
        >
          <strong>
            {report.passed ? "PASS" : "FAIL"} · {report.elapsed_ms} ms
            Modellzeit
          </strong>
          {report.fault && <p>{report.fault}</p>}
          <ul>
            {report.assertions.map((a, i) => (
              <li key={i}>
                {a.passed_at_ms === null ? "FAIL" : "PASS"} · Schritt{" "}
                {a.step + 1} · {key(a.signal)}: [{a.min}, {a.max}] ·{" "}
                {a.passed_at_ms === null
                  ? `Wert ${a.actual} bis ${a.deadline_ms} ms`
                  : `erreicht bei ${a.passed_at_ms} ms`}
              </li>
            ))}
          </ul>
          <button
            className="button compact"
            onClick={() => {
              const url = URL.createObjectURL(
                new Blob([JSON.stringify({ project, report }, null, 2)], {
                  type: "application/json",
                }),
              );
              const a = document.createElement("a");
              a.href = url;
              a.download = "virtualwago-scenario-report.json";
              a.click();
              setTimeout(() => URL.revokeObjectURL(url), 1000);
            }}
          >
            Bericht exportieren
          </button>
        </div>
      )}
    </div>
  );
}
