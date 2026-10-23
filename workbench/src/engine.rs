use crate::model::*;
use rhai::{AST, Dynamic, Engine as ScriptEngine, Scope};
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
fn compile(project: &Project) -> Result<HashMap<String, AST>> {
    project.validate()?;
    let e = scripting();
    let mut compiled = HashMap::new();
    for r in &project.reactions {
        let ast = e.compile(&r.code).map_err(|v| format!("{}: {v}", r.name))?;
        if !ast
            .iter_functions()
            .any(|f| f.name == "react" && f.params.len() == 4)
        {
            return Err(format!(
                "{}: fn react(output, previous, dt_s, time_s) fehlt",
                r.name
            ));
        }
        // Global statements are never evaluated: only the explicitly called function runs.
        compiled.insert(r.id.clone(), ast.clone_functions_only());
    }
    Ok(compiled)
}

pub struct Simulation {
    project: Project,
    compiled: HashMap<String, AST>,
    values: HashMap<SignalRef, f64>,
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
                let value: Dynamic = e
                    .call_fn(
                        &mut Scope::new(),
                        &self.compiled[&r.id],
                        "react",
                        (
                            output,
                            previous,
                            self.project.tick_ms as f64 / 1000.0,
                            self.time_ms as f64 / 1000.0,
                        ),
                    )
                    .map_err(|err| format!("{}: {err}", r.name))?;
                let value = if let Some(v) = value.clone().try_cast::<f64>() {
                    v
                } else if let Some(v) = value.try_cast::<i64>() {
                    v as f64
                } else {
                    return Err(format!("{}: Rückgabe muss eine Zahl sein", r.name));
                };
                self.project
                    .channel(&r.target)?
                    .check(value)
                    .map_err(|err| format!("{}: {err}", r.name))?;
                changes.push((r.target.clone(), value));
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
        for (signal, value) in changes {
            self.values.insert(signal, value);
        }
        self.time_ms = next;
        self.tick += 1;
        self.sequence += 1;
        Ok(())
    }
}
