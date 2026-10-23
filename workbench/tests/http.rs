use axum::{
    body::{Body, to_bytes},
    http::{Request, StatusCode},
};
use std::{
    path::PathBuf,
    sync::{Arc, Mutex},
};
use tower::ServiceExt;
use virtualwago_workbench::{
    api::{self, AppState},
    engine::Simulation,
    model::*,
};

fn app() -> axum::Router {
    api::router(
        AppState {
            simulation: Arc::new(Mutex::new(Simulation::new(demo_project()).unwrap())),
            state_dir: None,
            authority: "127.0.0.1:8787".into(),
            slots: Arc::new(tokio::sync::Semaphore::new(32)),
            viewers: Arc::new(tokio::sync::Semaphore::new(8)),
            evaluators: Arc::new(tokio::sync::Semaphore::new(1)),
        },
        PathBuf::from("web/dist"),
    )
}
fn request(method: &str, path: &str, body: serde_json::Value) -> Request<Body> {
    Request::builder()
        .method(method)
        .uri(path)
        .header("host", "127.0.0.1:8787")
        .header("content-type", "application/json")
        .header("x-virtualwago-client", "workbench")
        .header(
            "x-virtualwago-instance",
            virtualwago_workbench::engine::process_instance(),
        )
        .body(Body::from(serde_json::to_vec(&body).unwrap()))
        .unwrap()
}
#[tokio::test]
async fn command_contract_runs_and_rejects_old_project_generation() {
    let app = app();
    let response = app
        .clone()
        .oneshot(request(
            "POST",
            "/api/command",
            serde_json::json!({"generation":1,"command":{"action":"step"}}),
        ))
        .await
        .unwrap();
    assert_eq!(response.status(), StatusCode::OK);
    let body: serde_json::Value =
        serde_json::from_slice(&to_bytes(response.into_body(), 1024 * 1024).await.unwrap())
            .unwrap();
    assert_eq!(body["tick"], "1");
    let response = app
        .oneshot(request(
            "POST",
            "/api/command",
            serde_json::json!({"generation":99,"command":{"action":"run"}}),
        ))
        .await
        .unwrap();
    assert_eq!(response.status(), StatusCode::CONFLICT);
}

#[tokio::test]
async fn service_restart_epoch_rejects_old_client_even_at_generation_one() {
    let mut r = request(
        "POST",
        "/api/command",
        serde_json::json!({"generation":1,"command":{"action":"run"}}),
    );
    r.headers_mut().insert(
        "x-virtualwago-instance",
        "previous-process".parse().unwrap(),
    );
    assert_eq!(
        app().oneshot(r).await.unwrap().status(),
        StatusCode::CONFLICT
    );
}
#[tokio::test]
async fn host_origin_and_browser_client_boundary_are_enforced() {
    for (host, origin, client, status) in [
        ("attacker.example:8787", None, true, 403),
        (
            "127.0.0.1:8787",
            Some("https://attacker.example"),
            true,
            403,
        ),
        ("127.0.0.1:8787", None, false, 403),
        ("127.0.0.1:8787", Some("http://127.0.0.1:8787"), true, 200),
    ] {
        let mut r = request(
            "POST",
            "/api/command",
            serde_json::json!({"generation":1,"command":{"action":"pause"}}),
        );
        r.headers_mut().insert("host", host.parse().unwrap());
        if let Some(origin) = origin {
            r.headers_mut().insert("origin", origin.parse().unwrap());
        }
        if !client {
            r.headers_mut().remove("x-virtualwago-client");
        }
        assert_eq!(app().oneshot(r).await.unwrap().status().as_u16(), status);
    }
}
#[tokio::test]
async fn invalid_project_apply_is_rejected_and_preserves_generation() {
    let app = app();
    let mut p = demo_project();
    p.reactions[0].code = "broken code".into();
    let response = app
        .clone()
        .oneshot(request(
            "PUT",
            "/api/project",
            serde_json::json!({"generation":1,"project":p}),
        ))
        .await
        .unwrap();
    assert_eq!(response.status(), StatusCode::UNPROCESSABLE_ENTITY);
    let response = app
        .oneshot(request("GET", "/api/bootstrap", serde_json::Value::Null))
        .await
        .unwrap();
    let body: serde_json::Value =
        serde_json::from_slice(&to_bytes(response.into_body(), 1024 * 1024).await.unwrap())
            .unwrap();
    assert_eq!(body["state"]["generation"], 1);
    assert_eq!(body["project"]["reactions"][0]["name"], "Ventilrückmeldung");
}
#[tokio::test]
async fn config_apply_resets_live_state_and_emits_csp() {
    let app = app();
    let mut p = demo_project();
    p.name = "Neues Projekt".into();
    let response = app
        .oneshot(request(
            "PUT",
            "/api/project",
            serde_json::json!({"generation":1,"project":p}),
        ))
        .await
        .unwrap();
    assert_eq!(response.status(), StatusCode::OK);
    assert!(response.headers().contains_key("content-security-policy"));
    let body: serde_json::Value =
        serde_json::from_slice(&to_bytes(response.into_body(), 1024 * 1024).await.unwrap())
            .unwrap();
    assert_eq!(body["state"]["generation"], 2);
    assert_eq!(body["state"]["permit"], false);
    assert_eq!(body["project"]["name"], "Neues Projekt");
}
#[test]
fn project_storage_round_trip_and_symlink_refusal() {
    let path = std::env::temp_dir().join(format!("virtualwago-storage-{}", std::process::id()));
    std::fs::create_dir(&path).unwrap();
    api::save_project(&path, &demo_project()).unwrap();
    assert_eq!(api::load_project(&path).unwrap().unwrap().modules.len(), 5);
    std::fs::remove_file(path.join("project.json")).unwrap();
    std::os::unix::fs::symlink("/dev/null", path.join("project.json")).unwrap();
    assert!(api::save_project(&path, &demo_project()).is_err());
    assert!(api::load_project(&path).is_err());
    std::fs::remove_file(path.join("project.json")).unwrap();
    std::fs::remove_dir(path).unwrap();
}

#[tokio::test]
async fn failed_persistence_keeps_the_active_configuration() {
    let dir = std::env::temp_dir().join(format!("virtualwago-unwritable-{}", std::process::id()));
    std::fs::write(&dir, b"not a directory").unwrap();
    let sim = Arc::new(Mutex::new(Simulation::new(demo_project()).unwrap()));
    let app = api::router(
        AppState {
            simulation: sim.clone(),
            state_dir: Some(dir.clone()),
            authority: "127.0.0.1:8787".into(),
            slots: Arc::new(tokio::sync::Semaphore::new(32)),
            viewers: Arc::new(tokio::sync::Semaphore::new(8)),
            evaluators: Arc::new(tokio::sync::Semaphore::new(1)),
        },
        PathBuf::from("web/dist"),
    );
    let mut p = demo_project();
    p.name = "Must not commit".into();
    let response = app
        .oneshot(request(
            "PUT",
            "/api/project",
            serde_json::json!({"generation":1,"project":p}),
        ))
        .await
        .unwrap();
    assert_eq!(response.status(), StatusCode::UNPROCESSABLE_ENTITY);
    assert_eq!(sim.lock().unwrap().generation(), 1);
    assert_eq!(sim.lock().unwrap().project().name, "Meine erste Simulation");
    std::fs::remove_file(dir).unwrap();
}

#[test]
fn state_directory_lock_rejects_second_owner_and_releases_without_unlink() {
    let dir = std::env::temp_dir().join(format!("virtualwago-lock-{}", std::process::id()));
    let first = api::StateDirectoryLock::acquire(&dir).unwrap();
    assert!(api::StateDirectoryLock::acquire(&dir).is_err());
    drop(first);
    let second = api::StateDirectoryLock::acquire(&dir).unwrap();
    drop(second);
    assert!(dir.join(".workbench.lock").is_file());
    std::fs::remove_dir_all(dir).unwrap();
}
#[tokio::test]
async fn script_validation_returns_line_and_scenario_run_does_not_mutate_live_state() {
    let app = app();
    let response = app
        .clone()
        .oneshot(request(
            "POST",
            "/api/scripts/validate",
            serde_json::json!({"code":"fn react(o,p,dt,t) {\nlet x = ;\n}","stateful":false}),
        ))
        .await
        .unwrap();
    assert_eq!(response.status(), StatusCode::OK);
    let body: serde_json::Value =
        serde_json::from_slice(&to_bytes(response.into_body(), 1024 * 1024).await.unwrap())
            .unwrap();
    assert_eq!(body["valid"], false);
    assert_eq!(body["diagnostic"]["line"], 2);
    let mut p = demo_project();
    p.scenarios=serde_json::from_value(serde_json::json!([{"id":"feedback","name":"Feedback","steps":[{"at_ms":0,"permit":true,"set":[{"signal":{"module":"do-bank","channel":"ch1"},"value":1}],"expect":[{"signal":{"module":"di-bank","channel":"ch1"},"min":1,"max":1,"within_ms":20}]}]}])).unwrap();
    let response = app
        .clone()
        .oneshot(request(
            "POST",
            "/api/scenarios/run",
            serde_json::json!({"project":p,"id":"feedback"}),
        ))
        .await
        .unwrap();
    assert_eq!(response.status(), StatusCode::OK);
    let body: serde_json::Value =
        serde_json::from_slice(&to_bytes(response.into_body(), 1024 * 1024).await.unwrap())
            .unwrap();
    assert_eq!(body["passed"], true);
    let response = app
        .oneshot(request("GET", "/api/bootstrap", serde_json::Value::Null))
        .await
        .unwrap();
    let body: serde_json::Value =
        serde_json::from_slice(&to_bytes(response.into_body(), 1024 * 1024).await.unwrap())
            .unwrap();
    assert_eq!(body["state"]["time_ms"], 0);
    assert_eq!(body["state"]["permit"], false);
}

#[test]
fn real_services_cannot_share_a_state_directory_and_restart_releases_lock() {
    use std::{
        io::{BufRead, BufReader},
        process::{Child, Command, Stdio},
        time::{Duration, Instant},
    };
    struct Service(Child);
    impl Drop for Service {
        fn drop(&mut self) {
            let _ = self.0.kill();
            let _ = self.0.wait();
        }
    }
    let dir = std::env::temp_dir().join(format!("virtualwago-process-lock-{}", std::process::id()));
    std::fs::create_dir(&dir).unwrap();
    std::fs::write(dir.join("index.html"), "offline test").unwrap();
    let start = || {
        Command::new(env!("CARGO_BIN_EXE_virtualwago-workbench"))
            .args(["--port", "0", "--state-dir"])
            .arg(&dir)
            .arg("--assets")
            .arg(&dir)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .unwrap()
    };
    let mut first = Service(start());
    let mut line = String::new();
    BufReader::new(first.0.stdout.take().unwrap())
        .read_line(&mut line)
        .unwrap();
    assert!(line.contains("http://127.0.0.1:"));
    let mut second = Service(start());
    let deadline = Instant::now() + Duration::from_secs(3);
    loop {
        if let Some(status) = second.0.try_wait().unwrap() {
            assert!(!status.success());
            break;
        }
        assert!(
            Instant::now() < deadline,
            "second service must reject the occupied state directory"
        );
        std::thread::sleep(Duration::from_millis(10));
    }
    let mut error = String::new();
    std::io::Read::read_to_string(&mut second.0.stderr.take().unwrap(), &mut error).unwrap();
    assert!(error.contains("bereits belegt"));
    drop(first);
    let mut third = Service(start());
    line.clear();
    BufReader::new(third.0.stdout.take().unwrap())
        .read_line(&mut line)
        .unwrap();
    assert!(line.contains("http://127.0.0.1:"));
    drop(third);
    drop(second);
    std::fs::remove_dir_all(dir).unwrap();
}
