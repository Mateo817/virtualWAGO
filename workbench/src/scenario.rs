//! Deterministic offline test stimuli. These never execute in the live session.
use crate::{
    engine::{Command, Simulation},
    model::*,
};
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, HashMap, HashSet};

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Expectation {
    pub signal: SignalRef,
    pub min: f64,
    pub max: f64,
    pub within_ms: u32,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Stimulus {
    pub signal: SignalRef,
    pub value: f64,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ScenarioStep {
    pub at_ms: u32,
    #[serde(default)]
    pub permit: Option<bool>,
    #[serde(default)]
    pub set: Vec<Stimulus>,
    #[serde(default)]
    pub expect: Vec<Expectation>,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Scenario {
    pub id: String,
    pub name: String,
    pub steps: Vec<ScenarioStep>,
}
#[derive(Clone, Debug, Serialize)]
pub struct AssertionResult {
    pub step: usize,
    pub signal: SignalRef,
    pub min: f64,
    pub max: f64,
    pub deadline_ms: u64,
    pub passed_at_ms: Option<u64>,
    pub actual: f64,
}
#[derive(Clone, Debug, Serialize)]
pub struct ScenarioSample {
    pub time: u64,
    pub values: BTreeMap<String, f64>,
}
#[derive(Clone, Debug, Serialize)]
pub struct ScenarioReport {
    pub id: String,
    pub passed: bool,
    pub elapsed_ms: u64,
    pub assertions: Vec<AssertionResult>,
    pub fault: Option<String>,
    pub samples: Vec<ScenarioSample>,
}

pub fn validate_scenarios(project: &Project) -> Result<()> {
    if project.scenarios.len() > 16 {
        return Err("Höchstens 16 Szenarien".into());
    }
    let mut ids = HashSet::new();
    for s in &project.scenarios {
        identifier(&s.id)?;
        text(&s.name, 100, "Szenarioname")?;
        if !ids.insert(&s.id) || s.steps.is_empty() || s.steps.len() > 64 {
            return Err("Szenario: eindeutige Kennung und 1–64 Schritte erforderlich".into());
        }
        let mut last = None;
        let mut assertions = 0;
        for step in &s.steps {
            if !step.at_ms.is_multiple_of(project.tick_ms)
                || last.is_some_and(|v| step.at_ms <= v)
                || step.set.len() > 16
                || step.expect.len() > 16
            {
                return Err("Szenariozeiten müssen aufsteigend auf dem Modellraster liegen; höchstens 16 Vorgaben/Prüfungen je Schritt".into());
            }
            last = Some(step.at_ms);
            let mut writes = HashSet::new();
            for set in &step.set {
                project.channel(&set.signal)?.check(set.value)?;
                if !writes.insert(&set.signal) {
                    return Err("Doppelte Szenariovorgabe".into());
                }
                if project
                    .reactions
                    .iter()
                    .any(|r| r.enabled && r.target == set.signal)
                {
                    return Err("Szenario darf skriptgeführte Eingänge nicht überschreiben".into());
                }
            }
            for e in &step.expect {
                let c = project.channel(&e.signal)?;
                if c.direction != Direction::Input
                    || !e.min.is_finite()
                    || !e.max.is_finite()
                    || e.min > e.max
                    || e.min < c.min
                    || e.max > c.max
                    || !e.within_ms.is_multiple_of(project.tick_ms)
                {
                    return Err("Prüfung benötigt einen Eingangsbereich und eine Frist auf dem Modellraster".into());
                }
                let end = step.at_ms as u64 + e.within_ms as u64;
                if end / project.tick_ms as u64 > 1000 {
                    return Err("Szenario darf höchstens 1000 Modellschritte dauern".into());
                }
            }
            if step.at_ms / project.tick_ms > 1000 {
                return Err("Szenario darf höchstens 1000 Modellschritte dauern".into());
            }
            assertions += step.expect.len();
        }
        if assertions == 0 || assertions > 64 {
            return Err("Szenario benötigt 1–64 Prüfungen".into());
        }
    }
    Ok(())
}

pub fn run(project: Project, id: &str) -> Result<ScenarioReport> {
    project.validate()?;
    let scenario = project
        .scenarios
        .iter()
        .find(|s| s.id == id)
        .ok_or("Szenario fehlt")?
        .clone();
    let mut sim = Simulation::new(project)?;
    let mut report = ScenarioReport {
        id: scenario.id,
        passed: false,
        elapsed_ms: 0,
        assertions: vec![],
        fault: None,
        samples: vec![],
    };
    let end = scenario
        .steps
        .iter()
        .map(|s| {
            s.expect
                .iter()
                .map(|e| s.at_ms as u64 + e.within_ms as u64)
                .max()
                .unwrap_or(s.at_ms as u64)
        })
        .max()
        .unwrap();
    let mut seen = HashSet::new();
    let traces: Vec<_> = scenario
        .steps
        .iter()
        .flat_map(|s| s.expect.iter().map(|e| e.signal.clone()))
        .filter(|signal| seen.insert(signal.clone()))
        .take(8)
        .collect();
    let mut next = 0;
    loop {
        let now = sim.snapshot().time_ms;
        if let Some(step) = scenario.steps.get(next).filter(|s| s.at_ms as u64 == now) {
            if let Some(enabled) = step.permit {
                sim.command(Command::Permit { enabled })?;
            }
            for set in &step.set {
                sim.command(Command::SetSignal {
                    signal: set.signal.clone(),
                    value: set.value,
                })?;
            }
            for e in &step.expect {
                report.assertions.push(AssertionResult {
                    step: next,
                    signal: e.signal.clone(),
                    min: e.min,
                    max: e.max,
                    deadline_ms: now + e.within_ms as u64,
                    passed_at_ms: None,
                    actual: 0.,
                });
            }
            next += 1;
        }
        let snapshot = sim.snapshot();
        let values: HashMap<_, _> = snapshot
            .signals
            .iter()
            .map(|s| (s.signal.clone(), s.value))
            .collect();
        for a in &mut report.assertions {
            if a.passed_at_ms.is_none() && now <= a.deadline_ms {
                a.actual = values[&a.signal];
                if (a.min..=a.max).contains(&a.actual) {
                    a.passed_at_ms = Some(now);
                }
            }
        }
        report.samples.push(ScenarioSample {
            time: now,
            values: traces
                .iter()
                .map(|s| (format!("{}/{}", s.module, s.channel), values[s]))
                .collect(),
        });
        report.elapsed_ms = now;
        if now >= end {
            break;
        }
        if let Err(e) = sim.step() {
            report.fault = Some(e);
            break;
        }
    }
    report.passed =
        report.fault.is_none() && report.assertions.iter().all(|a| a.passed_at_ms.is_some());
    Ok(report)
}
