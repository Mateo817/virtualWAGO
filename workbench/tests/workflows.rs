use virtualwago_workbench::{
    engine::{Command, Simulation, validate_script},
    model::*,
    scenario::*,
};
fn sig(module: &str, channel: &str) -> SignalRef {
    SignalRef {
        module: module.into(),
        channel: channel.into(),
    }
}
fn stateful() -> Project {
    let mut p = demo_project();
    let r = &mut p.reactions[0];
    r.stateful = true;
    r.sources = vec![sig("do-bank", "ch2")];
    r.code=r#"fn react_state(outputs, previous, state, dt_s, time_s) {
   if !state.contains("elapsed") { state.elapsed=0.0; }
   if outputs["do-bank/ch1"] > 0.5 && outputs["do-bank/ch2"] > 0.5 { state.elapsed+=dt_s; } else { state.elapsed=0.0; }
   #{value: if state.elapsed >= 0.06 {1.0} else {0.0}, state:state}
 }"#.into();
    p
}
fn input(sim: &Simulation) -> f64 {
    sim.snapshot()
        .signals
        .iter()
        .find(|s| s.signal == sig("di-bank", "ch1"))
        .unwrap()
        .value
}
#[test]
fn multiple_effective_outputs_and_state_obey_gate_reset_and_atomicity() {
    let mut sim = Simulation::new(stateful()).unwrap();
    for c in ["ch1", "ch2"] {
        sim.command(Command::SetSignal {
            signal: sig("do-bank", c),
            value: 1.,
        })
        .unwrap();
    }
    for _ in 0..5 {
        sim.step().unwrap();
    }
    assert_eq!(input(&sim), 0.);
    sim.command(Command::Permit { enabled: true }).unwrap();
    sim.step().unwrap();
    sim.step().unwrap();
    assert_eq!(input(&sim), 0.);
    sim.step().unwrap();
    assert_eq!(input(&sim), 1.);
    sim.command(Command::Reset).unwrap();
    assert_eq!(input(&sim), 0.);
    for c in ["ch1", "ch2"] {
        sim.command(Command::SetSignal {
            signal: sig("do-bank", c),
            value: 1.,
        })
        .unwrap();
    }
    sim.command(Command::Permit { enabled: true }).unwrap();
    sim.step().unwrap();
    assert_eq!(input(&sim), 0.);
    let mut bad = stateful();
    bad.reactions[0].code =
        "fn react_state(o,p,s,dt,t) { #{value:1.0,state:#{bad: [1,2]}} }".into();
    sim.apply(bad).unwrap();
    assert!(sim.step().is_err());
    assert_eq!(input(&sim), 0.);
    assert_eq!(sim.snapshot().time_ms, 0);
    assert!(!sim.snapshot().permit);
}
#[test]
fn state_is_bounded_and_multi_source_contracts_reject_bad_bindings() {
    for code in [
        "fn react_state(o,p,s,dt,t) { #{value:1.0,state:#{large: 1000000001.0}} }",
        "fn react_state(o,p,s,dt,t) { #{value:1.0,state:#{}} } fn extra(a,b) { 0 }",
        "fn react_state(o,p,s,dt,t) { loop {} }",
    ] {
        let mut p = stateful();
        p.reactions[0].code = code.into();
        let mut sim = Simulation::new(p).unwrap();
        let result = sim.step();
        if code.contains("extra") {
            assert!(result.is_ok());
        } else {
            assert!(result.is_err());
        }
    }
    let mut p = stateful();
    p.reactions[0].sources.push(sig("di-bank", "ch1"));
    assert!(Simulation::new(p).is_err());
    let mut p = stateful();
    p.reactions[0].sources.push(sig("do-bank", "ch1"));
    assert!(Simulation::new(p).is_err());
}
fn with_scenario() -> Project {
    let mut p = stateful();
    p.scenarios = vec![Scenario {
        id: "delay".into(),
        name: "Delayed feedback".into(),
        steps: vec![ScenarioStep {
            at_ms: 0,
            permit: Some(true),
            set: vec![
                Stimulus {
                    signal: sig("do-bank", "ch1"),
                    value: 1.,
                },
                Stimulus {
                    signal: sig("do-bank", "ch2"),
                    value: 1.,
                },
            ],
            expect: vec![Expectation {
                signal: sig("di-bank", "ch1"),
                min: 1.,
                max: 1.,
                within_ms: 60,
            }],
        }],
    }];
    p
}
#[test]
fn scenario_deadline_is_inclusive_and_live_session_is_unchanged() {
    let p = with_scenario();
    let sim = Simulation::new(p.clone()).unwrap();
    let report = run(p.clone(), "delay").unwrap();
    assert!(report.passed);
    assert_eq!(report.assertions[0].passed_at_ms, Some(60));
    assert_eq!(report.samples.len(), 4);
    assert_eq!(sim.snapshot().time_ms, 0);
    assert!(!sim.snapshot().permit);
    let mut p = p;
    p.scenarios[0].steps[0].expect[0].within_ms = 40;
    let report = run(p, "delay").unwrap();
    assert!(!report.passed);
    assert_eq!(report.assertions[0].passed_at_ms, None);
    assert_eq!(report.assertions[0].actual, 0.);
}
#[test]
fn scenario_gate_changes_and_faults_are_not_successes() {
    let mut p = with_scenario();
    p.scenarios[0].steps.push(ScenarioStep {
        at_ms: 80,
        permit: Some(false),
        set: vec![],
        expect: vec![Expectation {
            signal: sig("di-bank", "ch1"),
            min: 0.,
            max: 0.,
            within_ms: 20,
        }],
    });
    assert!(run(p.clone(), "delay").unwrap().passed);
    p.reactions[0].code = "fn react_state(o,p,s,dt,t) { #{value:99.0,state:#{}} }".into();
    let r = run(p, "delay").unwrap();
    assert!(!r.passed);
    assert!(r.fault.is_some());
    assert_eq!(r.elapsed_ms, 0);
}
#[test]
fn invalid_timing_empty_assertions_and_script_owned_stimuli_are_rejected() {
    let p = with_scenario();
    let mut q = p.clone();
    q.scenarios[0].steps[0].expect[0].within_ms = 1;
    assert!(q.validate().is_err());
    let mut q = p.clone();
    q.scenarios[0].steps[0].expect.clear();
    assert!(q.validate().is_err());
    let mut q = p.clone();
    q.scenarios[0].steps[0].set[0].signal = sig("di-bank", "ch1");
    assert!(q.validate().is_err());
    let mut q = p;
    q.scenarios[0].steps[0].expect[0].within_ms = 20020;
    assert!(q.validate().is_err());
}
#[test]
fn script_diagnostic_locates_parse_error_and_legacy_project_is_compatible() {
    let d = validate_script("fn react(o,p,dt,t) {\n let x = ;\n}", false).unwrap();
    assert_eq!(d.line, Some(2));
    assert!(d.column.is_some());
    assert!(validate_script("fn react_state(o,p,s,dt,t) { #{value:p,state:s} }", true).is_none());
    let mut old = serde_json::to_value(demo_project()).unwrap();
    old.as_object_mut().unwrap().remove("scenarios");
    for r in old["reactions"].as_array_mut().unwrap() {
        r.as_object_mut().unwrap().remove("sources");
        r.as_object_mut().unwrap().remove("stateful");
    }
    let p: Project = serde_json::from_value(old).unwrap();
    Simulation::new(p).unwrap();
}

#[test]
fn scenario_reports_are_identical_on_repeated_runs() {
    let p = with_scenario();
    assert_eq!(
        serde_json::to_string(&run(p.clone(), "delay").unwrap()).unwrap(),
        serde_json::to_string(&run(p, "delay").unwrap()).unwrap()
    );
}
