use crate::model::*;
use rhai::{AST, Dynamic, Engine as ScriptEngine, Map, Scope};
use serde::{Deserialize, Serialize};
use std::{
    collections::{HashMap, VecDeque},
    sync::OnceLock,
    time::{SystemTime, UNIX_EPOCH},
};

/// An epoch, not an authentication secret. A new service process invalidates
/// previous command and draft revisions even when its generation restarts at 1.
pub fn process_instance() -> &'static str {
    static INSTANCE: OnceLock<String> = OnceLock::new();
    INSTANCE.get_or_init(|| {
        format!(
            "{}-{}",
            std::process::id(),
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap_or_default()
                .as_nanos()
        )
    })
}

#[derive(Clone, Debug, Serialize)]
pub struct SignalState {
    pub signal: SignalRef,
    pub value: f64,
    pub requested: Option<f64>,
    pub effective: Option<f64>,
    pub raw: u32,
    pub requested_raw: Option<u32>,
    pub source: String,
}
#[derive(Clone, Debug, Serialize)]
pub struct Event {
    pub time_ms: u64,
    pub level: String,
    pub message: String,
}

#[derive(Clone, Debug, Serialize)]
pub struct Snapshot {
    pub instance: &'static str,
    pub generation: u64,
    pub sequence: String,
    pub tick: String,
    pub time_ms: u64,
    pub running: bool,
    pub permit: bool,
    pub speed: u32,
    pub fault: Option<String>,
    pub signals: Vec<SignalState>,
    pub events: Vec<Event>,
    pub scope: &'static str,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(tag = "action", rename_all = "snake_case", deny_unknown_fields)]
pub enum Command {
    Run,
    Pause,
    Stop,
    Step,
    Reset,
    Permit { enabled: bool },
    Speed { factor: u32 },
    SetSignal { signal: SignalRef, value: f64 },
}

fn scripting() -> ScriptEngine {
    let mut e = ScriptEngine::new();
    e.set_max_operations(20_000);
    e.set_max_call_levels(16);
    e.set_max_expr_depths(32, 16);
    e.set_max_variables(64);
    e.set_max_functions(16);
    e.set_max_string_size(4096);
    e.set_max_array_size(128);
    e.set_max_map_size(64);
    e.disable_symbol("eval");
    // No file/network/process APIs, module loading, console, or host callbacks.
    e.on_print(|_| {});
    e.on_debug(|_, _, _| {});
    e
}
#[derive(Debug, Serialize)]
pub struct ScriptDiagnostic {
    pub message: String,
    pub line: Option<usize>,
    pub column: Option<usize>,
}
fn compile_script(code: &str, stateful: bool) -> std::result::Result<AST, ScriptDiagnostic> {
    if code.is_empty() || code.len() > 8192 {
        return Err(ScriptDiagnostic {
            message: "Skript benötigt 1–8192 Byte".into(),
            line: None,
            column: None,
        });
    }
    let ast = scripting().compile(code).map_err(|e| ScriptDiagnostic {
        line: e.position().line(),
        column: e.position().position(),
        message: e.to_string(),
    })?;
    let (name, count) = if stateful {
        ("react_state", 5)
    } else {
        ("react", 4)
    };
    if !ast
        .iter_functions()
        .any(|f| f.name == name && f.params.len() == count)
    {
        return Err(ScriptDiagnostic {
            message: format!("fn {name} mit {count} Parametern fehlt"),
            line: None,
            column: None,
        });
    }
    Ok(ast.clone_functions_only())
}
pub fn validate_script(code: &str, stateful: bool) -> Option<ScriptDiagnostic> {
    compile_script(code, stateful).err()
}
fn compile(project: &Project) -> Result<HashMap<String, AST>> {
    project.validate()?;
    project
        .reactions
        .iter()
        .map(|r| {
            compile_script(&r.code, r.stateful)
                .map(|ast| (r.id.clone(), ast))
                .map_err(|e| format!("{}: {}", r.name, e.message))
        })
        .collect()
}
fn numeric(value: Dynamic) -> Result<f64> {
    value
        .clone()
        .try_cast::<f64>()
        .or_else(|| value.try_cast::<i64>().map(|v| v as f64))
        .filter(|v| v.is_finite())
        .ok_or("Rückgabe muss eine endliche Zahl sein".into())
}
fn checked_state(value: Dynamic) -> Result<Map> {
    let map = value.try_cast::<Map>().ok_or("state muss eine Map sein")?;
    if map.len() > 16 {
        return Err("Höchstens 16 numerische Zustandswerte".into());
    }
    for (key, value) in &map {
        identifier(key)?;
        if numeric(value.clone())?.abs() > 1e9 {
            return Err("Zustandswert außerhalb ±1e9".into());
        }
    }
    Ok(map)
}

pub struct Simulation {
    project: Project,
    compiled: HashMap<String, AST>,
    values: HashMap<SignalRef, f64>,
    reaction_states: HashMap<String, Map>,
    requested: HashMap<SignalRef, f64>,
    generation: u64,
    sequence: u64,
    tick: u64,
    time_ms: u64,
    pub running: bool,
    permit: bool,
    speed: u32,
    fault: Option<String>,
    events: VecDeque<Event>,
}
pub(crate) struct PreparedProject {
    pub project: Project,
    compiled: HashMap<String, AST>,
}
impl Simulation {
    pub fn new(project: Project) -> Result<Self> {
        let compiled = compile(&project)?;
        let mut sim = Self {
            project,
            compiled,
            values: HashMap::new(),
            reaction_states: HashMap::new(),
            requested: HashMap::new(),
            generation: 1,
            sequence: 0,
            tick: 0,
            time_ms: 0,
            running: false,
            permit: false,
            speed: 1,
            fault: None,
            events: VecDeque::new(),
        };
        sim.initialize();
        sim.event("info", "Projekt geladen · ausschließlich Offline-Signale");
        Ok(sim)
    }
    fn initialize(&mut self) {
        self.values.clear();
        self.reaction_states.clear();
        self.requested.clear();
        for m in &self.project.modules {
            let p = self
                .project
                .packages
                .iter()
                .find(|p| p.id == m.package)
                .unwrap();
            for c in &p.channels {
                let signal = SignalRef {
                    module: m.id.clone(),
                    channel: c.id.clone(),
                };
                self.values.insert(signal.clone(), c.initial);
                if c.direction == Direction::Output {
                    self.requested.insert(signal, 0.0);
                }
            }
        }
    }
    fn event(&mut self, level: &str, message: &str) {
        if self.events.len() == 100 {
            self.events.pop_front();
        }
        self.events.push_back(Event {
            time_ms: self.time_ms,
            level: level.into(),
            message: message.chars().take(1500).collect(),
        });
        self.sequence += 1;
    }
    pub fn project(&self) -> &Project {
        &self.project
    }
    pub fn speed(&self) -> u32 {
        self.speed
    }
    pub fn generation(&self) -> u64 {
        self.generation
    }
    pub fn check_generation(&self, generation: u64) -> Result<()> {
        if self.generation != generation {
            return Err("Projektversion geändert; aktuellen Stand neu laden".into());
        }
        Ok(())
    }
    pub(crate) fn prepare(&self, project: Project) -> Result<PreparedProject> {
        if self.running {
            return Err("Simulation vor einer Projektänderung pausieren".into());
        }
        let compiled = compile(&project)?;
        Ok(PreparedProject { project, compiled })
    }
    pub fn apply(&mut self, project: Project) -> Result<()> {
        let prepared = self.prepare(project)?;
        self.activate(prepared);
        Ok(())
    }
    pub(crate) fn activate(&mut self, prepared: PreparedProject) {
        self.project = prepared.project;
        self.compiled = prepared.compiled;
        self.generation += 1;
        self.time_ms = 0;
        self.tick = 0;
        self.running = false;
        self.permit = false;
        self.fault = None;
        self.initialize();
        self.event(
            "info",
            "Projekt aktiviert · Modellzeit und Freigabe zurückgesetzt",
        );
    }
    pub(crate) fn storage_warning(&mut self) {
        self.event("warning","Projekt aktiviert, aber Verzeichnis-Synchronisierung fehlgeschlagen; Dauerhaftigkeit bei Stromausfall unbestätigt");
    }
    fn effective(&self, signal: &SignalRef) -> f64 {
        if self.permit && self.fault.is_none() {
            *self.requested.get(signal).unwrap_or(&0.0)
        } else {
            0.0
        }
    }
    pub fn snapshot(&self) -> Snapshot {
        let mut signals = Vec::new();
        for m in &self.project.modules {
            let p = self
                .project
                .packages
                .iter()
                .find(|p| p.id == m.package)
                .unwrap();
            for c in &p.channels {
                let signal = SignalRef {
                    module: m.id.clone(),
                    channel: c.id.clone(),
                };
                let output = c.direction == Direction::Output;
                let value = if output {
                    self.effective(&signal)
                } else {
                    self.values[&signal]
                };
                let requested = output.then(|| self.requested[&signal]);
                let source = if output {
                    "test".into()
                } else {
                    self.project
                        .reactions
                        .iter()
                        .find(|r| r.enabled && r.target == signal)
                        .map(|r| format!("reaction:{}", r.id))
                        .unwrap_or_else(|| "manual".into())
                };
                signals.push(SignalState {
                    signal,
                    value,
                    requested,
                    effective: output.then_some(value),
                    raw: c.raw(value),
                    requested_raw: requested.map(|v| c.raw(v)),
                    source,
                });
            }
        }
        Snapshot {
            instance: process_instance(),
            generation: self.generation,
            sequence: self.sequence.to_string(),
            tick: self.tick.to_string(),
            time_ms: self.time_ms,
            running: self.running,
            permit: self.permit,
            speed: self.speed,
            fault: self.fault.clone(),
            signals,
            events: self.events.iter().cloned().collect(),
            scope: "OFFLINE_SIGNAL_MODEL_NO_PLC_NO_NATIVE_ADI",
        }
    }
    pub fn command(&mut self, command: Command) -> Result<()> {
        if self.fault.is_some()
            && !matches!(
                command,
                Command::Reset
                    | Command::Stop
                    | Command::Pause
                    | Command::Permit { enabled: false }
            )
        {
            return Err("Modellfehler: Skript korrigieren oder zurücksetzen".into());
        }
        match command {
            Command::Run => {
                self.running = true;
                self.event("info", "Simulation gestartet");
            }
            Command::Pause => {
                self.running = false;
                self.event("info", "Pause · Modellzeit und Reaktionen eingefroren");
            }
            Command::Stop => {
                self.running = false;
                self.permit = false;
                self.event("info", "Gestoppt · wirksame Ausgänge auf 0");
            }
            Command::Step => {
                if self.running {
                    return Err("Einzelschritt benötigt Pause".into());
                }
                self.step()?;
            }
            Command::Reset => {
                self.running = false;
                self.permit = false;
                self.fault = None;
                self.time_ms = 0;
                self.tick = 0;
                self.initialize();
                self.event("info", "Simulation zurückgesetzt");
            }
            Command::Permit { enabled } => {
                self.permit = enabled;
                self.event(
                    "info",
                    if enabled {
                        "Modellfreigabe aktiv"
                    } else {
                        "Modellfreigabe entzogen"
                    },
                );
            }
            Command::Speed { factor } => {
                if !(1..=10).contains(&factor) {
                    return Err("Geschwindigkeit muss zwischen 1 und 10 liegen".into());
                }
                self.speed = factor;
                self.sequence += 1;
            }
            Command::SetSignal { signal, value } => {
                let channel = self.project.channel(&signal)?;
                channel.check(value)?;
                if channel.direction == Direction::Output {
                    self.requested.insert(signal, value);
                } else {
                    if self
                        .project
                        .reactions
                        .iter()
                        .any(|r| r.enabled && r.target == signal)
                    {
                        return Err("Eingang wird von einem Reaktionsskript geführt".into());
                    }
                    self.values.insert(signal, value);
                }
                self.sequence += 1;
            }
        }
        Ok(())
    }
    pub fn step(&mut self) -> Result<()> {
        if self.fault.is_some() {
            return Err("Modellfehler ist verriegelt".into());
        }
        let next = self
            .time_ms
            .checked_add(self.project.tick_ms as u64)
            .filter(|v| *v <= 9_007_199_254_740_991)
            .ok_or("Grenze der Modellzeit erreicht")?;
        let e = scripting();
        let mut changes = Vec::new();
        let result: Result<()> = (|| {
            for r in self.project.reactions.iter().filter(|r| r.enabled) {
                let output = r.source.as_ref().map(|s| self.effective(s)).unwrap_or(0.0);
                let previous = self.values[&r.target];
                let result: Dynamic = if r.stateful {
                    let mut outputs = Map::new();
                    for source in r.source.iter().chain(r.sources.iter()) {
                        outputs.insert(
                            format!("{}/{}", source.module, source.channel).into(),
                            Dynamic::from(self.effective(source)),
                        );
                    }
                    let state = self.reaction_states.get(&r.id).cloned().unwrap_or_default();
                    e.call_fn(
                        &mut Scope::new(),
                        &self.compiled[&r.id],
                        "react_state",
                        (
                            outputs,
                            previous,
                            state,
                            self.project.tick_ms as f64 / 1000.,
                            self.time_ms as f64 / 1000.,
                        ),
                    )
                } else {
                    e.call_fn(
                        &mut Scope::new(),
                        &self.compiled[&r.id],
                        "react",
                        (
                            output,
                            previous,
                            self.project.tick_ms as f64 / 1000.,
                            self.time_ms as f64 / 1000.,
                        ),
                    )
                }
                .map_err(|err| format!("{}: {err}", r.name))?;
                let (value, state) = if r.stateful {
                    let mut result = result.try_cast::<Map>().ok_or_else(|| {
                        format!("{}: Rückgabe muss #{{value, state}} sein", r.name)
                    })?;
                    if result.len() != 2 {
                        return Err(format!("{}: Genau value und state erforderlich", r.name));
                    }
                    let value = numeric(result.remove("value").ok_or("value fehlt")?)?;
                    let state = checked_state(result.remove("state").ok_or("state fehlt")?)?;
                    (value, Some(state))
                } else {
                    (numeric(result)?, None)
                };
                self.project
                    .channel(&r.target)?
                    .check(value)
                    .map_err(|err| format!("{}: {err}", r.name))?;
                changes.push((r.target.clone(), value, r.id.clone(), state));
            }
            Ok(())
        })();
        if let Err(err) = result {
            self.running = false;
            self.permit = false;
            self.fault = Some(err.clone());
            self.event("error", &err);
            return Err(err);
        }
        for (signal, value, id, state) in changes {
            self.values.insert(signal, value);
            if let Some(state) = state {
                self.reaction_states.insert(id, state);
            }
        }
        self.time_ms = next;
        self.tick += 1;
        self.sequence += 1;
        Ok(())
    }
}
