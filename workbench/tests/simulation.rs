use virtualwago_workbench::{
    engine::{Command, Simulation},
    model::*,
};

fn signal(module: &str, channel: &str) -> SignalRef {
    SignalRef {
        module: module.into(),
        channel: channel.into(),
    }
}
fn set(sim: &mut Simulation, module: &str, channel: &str, value: f64) {
    sim.command(Command::SetSignal {
        signal: signal(module, channel),
        value,
    })
    .unwrap();
}
fn value(sim: &Simulation, module: &str, channel: &str) -> f64 {
    sim.snapshot()
        .signals
        .into_iter()
        .find(|s| s.signal == signal(module, channel))
        .unwrap()
        .value
}

#[test]
fn output_reactions_observe_effective_values_and_cannot_write_commands() {
    let mut sim = Simulation::new(demo_project()).unwrap();
    set(&mut sim, "do-bank", "ch1", 1.0);
    sim.step().unwrap();
    assert_eq!(value(&sim, "di-bank", "ch1"), 0.0);
    assert!(
        sim.command(Command::SetSignal {
            signal: signal("di-bank", "ch1"),
            value: 1.
        })
        .is_err()
    );
    sim.command(Command::Permit { enabled: true }).unwrap();
    sim.step().unwrap();
    assert_eq!(value(&sim, "di-bank", "ch1"), 1.0);
    let output = sim
        .snapshot()
        .signals
        .into_iter()
        .find(|s| s.signal == signal("do-bank", "ch1"))
        .unwrap();
    assert_eq!((output.requested, output.effective), (Some(1.0), Some(1.0)));
    sim.command(Command::Stop).unwrap();
    let output = sim
        .snapshot()
        .signals
        .into_iter()
        .find(|s| s.signal == signal("do-bank", "ch1"))
        .unwrap();
    assert_eq!((output.requested, output.effective), (Some(1.0), Some(0.0)));
    sim.step().unwrap();
    assert_eq!(value(&sim, "di-bank", "ch1"), 0.0);
}

#[test]
fn rejected_reaction_frame_is_atomic_and_latches_fault() {
    let mut project = demo_project();
    project.reactions.push(Reaction {
        id: "bad".into(),
        name: "Bereichsfehler".into(),
        enabled: true,
        source: None,
        sources: vec![],
        stateful: false,
        target: signal("ai-bank", "ch1"),
        code: "fn react(output, previous, dt_s, time_s) { 99.0 }".into(),
    });
    let mut sim = Simulation::new(project).unwrap();
    set(&mut sim, "do-bank", "ch1", 1.);
    sim.command(Command::Permit { enabled: true }).unwrap();
    assert!(sim.step().is_err());
    assert_eq!(
        value(&sim, "di-bank", "ch1"),
        0.0,
        "earlier reaction must not partially commit"
    );
    assert_eq!(sim.snapshot().tick, "0");
    assert_eq!(sim.snapshot().time_ms, 0);
    assert!(!sim.snapshot().permit);
    assert!(!sim.running);
    assert!(sim.snapshot().fault.is_some());
    assert!(sim.command(Command::Permit { enabled: true }).is_err());
    sim.command(Command::Reset).unwrap();
    assert!(sim.snapshot().fault.is_none());
}

#[test]
fn script_loop_is_bounded_and_external_functions_are_absent() {
    for code in [
        "fn react(output, previous, dt_s, time_s) { loop {} 0.0 }",
        "fn react(output, previous, dt_s, time_s) { read_file(\"/etc/passwd\"); 0.0 }",
        "fn react(output, previous, dt_s, time_s) { timestamp(); 0.0 }",
        "fn react(output, previous, dt_s, time_s) { let a = []; for i in 0..1000 { a.push(i); } 0.0 }",
    ] {
        let mut project = demo_project();
        project.reactions[0].code = code.into();
        let mut sim = Simulation::new(project).unwrap();
        assert!(
            sim.step().is_err(),
            "unbounded or external script must fail: {code}"
        );
        assert_eq!(sim.snapshot().time_ms, 0);
        assert!(!sim.snapshot().permit);
    }
}

#[test]
fn global_statements_are_not_executed_or_imported_into_reaction_scope() {
    let mut project = demo_project();
    project.reactions[0].code = "loop {} fn react(output, previous, dt_s, time_s) { 0.0 }".into();
    let mut sim = Simulation::new(project).unwrap();
    sim.step().unwrap();
    assert_eq!(sim.snapshot().tick, "1");
}

#[test]
fn duplicate_writers_wrong_directions_and_changed_package_pins_are_rejected() {
    let original = demo_project();
    let mut duplicate = original.clone();
    let mut r = duplicate.reactions[0].clone();
    r.id = "second".into();
    duplicate.reactions.push(r);
    assert!(Simulation::new(duplicate).is_err());
    let mut wrong = original.clone();
    wrong.reactions[0].target = signal("do-bank", "ch1");
    assert!(Simulation::new(wrong).is_err());
    let mut wrong_source = original.clone();
    wrong_source.reactions[0].source = Some(signal("di-bank", "ch2"));
    assert!(Simulation::new(wrong_source).is_err());
    let mut changed = original;
    changed.packages[0].channels[0].label = "Neue Erkenntnis".into();
    assert!(Simulation::new(changed).is_err());
}

#[test]
fn module_order_changes_keep_script_binding_and_require_pause() {
    let mut sim = Simulation::new(demo_project()).unwrap();
    let mut project = sim.project().clone();
    project.modules.reverse();
    sim.command(Command::Run).unwrap();
    assert!(sim.apply(project.clone()).is_err());
    sim.command(Command::Pause).unwrap();
    sim.apply(project).unwrap();
    assert_eq!(sim.generation(), 2);
    assert!(sim.check_generation(1).is_err());
    set(&mut sim, "do-bank", "ch1", 1.);
    sim.command(Command::Permit { enabled: true }).unwrap();
    sim.step().unwrap();
    assert_eq!(value(&sim, "di-bank", "ch1"), 1.0);
}

#[test]
fn saved_projects_restore_configuration_but_never_live_outputs_or_permits() {
    let mut sim = Simulation::new(demo_project()).unwrap();
    set(&mut sim, "do-bank", "ch1", 1.);
    sim.command(Command::Permit { enabled: true }).unwrap();
    sim.step().unwrap();
    let json = serde_json::to_vec(sim.project()).unwrap();
    let restored = Simulation::new(serde_json::from_slice(&json).unwrap()).unwrap();
    assert!(!restored.snapshot().permit);
    assert!(!restored.running);
    assert_eq!(restored.snapshot().time_ms, 0);
    assert_eq!(value(&restored, "do-bank", "ch1"), 0.0);
}

#[test]
fn custom_data_only_package_and_time_source_run_without_a_new_binary() {
    let mut project = demo_project();
    let mut p = project
        .packages
        .iter()
        .find(|p| p.article == "750-466")
        .unwrap()
        .clone();
    p.id = "own.temperature".into();
    p.article = "SYNTHETIC".into();
    p.version = "0.2.0".into();
    p.channels.truncate(1);
    let c = &mut p.channels[0];
    c.min = -10.;
    c.max = 60.;
    c.initial = 20.;
    c.unit = "°C".into();
    c.encoding = Encoding::Linear {
        scale: 10.,
        offset: 100.,
        max_raw: 700,
    };
    project.modules.push(Instance {
        id: "temperature".into(),
        package: p.id.clone(),
        package_sha256: p.digest(),
        label: "Eigener Temperatursensor".into(),
    });
    project.packages.push(p);
    project.reactions.push(Reaction {
        id: "ramp".into(),
        name: "Temperaturrampe".into(),
        enabled: true,
        source: None,
        sources: vec![],
        stateful: false,
        target: signal("temperature", "ch1"),
        code: "fn react(output, previous, dt_s, time_s) { previous + dt_s }".into(),
    });
    let mut sim = Simulation::new(project).unwrap();
    for _ in 0..50 {
        sim.step().unwrap();
    }
    assert!((value(&sim, "temperature", "ch1") - 21.).abs() < 1e-10);
    let ch = sim
        .snapshot()
        .signals
        .into_iter()
        .find(|s| s.signal.module == "temperature")
        .unwrap();
    assert_eq!(ch.raw, 310);
}

#[test]
fn analog_quantization_matches_all_public_python_reference_vectors() {
    let vectors: serde_json::Value =
        serde_json::from_str(include_str!("fixtures/python-codecs.json")).unwrap();
    for v in vectors["ai466"].as_array().unwrap() {
        assert_eq!(
            encode_ai466(v[0].as_u64().unwrap() as u32),
            v[1].as_u64().unwrap() as u32
        );
    }
    for v in vectors["ao550"].as_array().unwrap() {
        assert_eq!(
            decode_ao550(v[0].as_u64().unwrap() as u32),
            v[1].as_u64().unwrap() as u32
        );
    }
}

#[test]
fn malformed_or_unsafe_signal_packages_are_rejected() {
    let original = demo_project();
    for change in 0..4 {
        let mut p = original
            .packages
            .iter()
            .find(|p| p.family == "do")
            .unwrap()
            .clone();
        match change {
            0 => p.channels[0].initial = 1.,
            1 => p.channels[0].min = 1.,
            2 => p.channels.push(p.channels[0].clone()),
            _ => p.channels[0].encoding = Encoding::Ai466Standard,
        }
        assert!(p.validate().is_err());
    }
    let mut project = original;
    project.reactions[0].code = "fn missing(x) { x }".into();
    assert!(Simulation::new(project).is_err());
}

#[test]
fn analog_reaction_is_deterministic_and_pause_does_not_advance_time() {
    let mut project = demo_project();
    project.reactions=vec![Reaction{sources:vec![],stateful:false,id:"lag".into(),name:"Trägheit".into(),enabled:true,
        source:Some(signal("ao-bank","ch1")),target:signal("ai-bank","ch1"),
        code:"fn react(output, previous, dt_s, time_s) { let target = 4.0 + output * 1.6; previous + (target - previous) * dt_s / (1.0 + dt_s) }".into()}];
    let mut a = Simulation::new(project.clone()).unwrap();
    let mut b = Simulation::new(project).unwrap();
    for s in [&mut a, &mut b] {
        set(s, "ao-bank", "ch1", 10.);
        s.command(Command::Permit { enabled: true }).unwrap();
        for _ in 0..100 {
            s.step().unwrap();
        }
    }
    assert_eq!(value(&a, "ai-bank", "ch1"), value(&b, "ai-bank", "ch1"));
    assert!(value(&a, "ai-bank", "ch1") > 17.);
    assert!(value(&a, "ai-bank", "ch1") < 20.);
    let before = a.snapshot().time_ms;
    a.command(Command::Pause).unwrap();
    assert_eq!(a.snapshot().time_ms, before);
}
