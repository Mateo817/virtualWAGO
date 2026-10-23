use crate::{
    engine::{Command, Simulation, process_instance},
    model::*,
};
use axum::{
    Json, Router,
    extract::ws::Message,
    extract::{DefaultBodyLimit, Request, State, WebSocketUpgrade},
    http::{StatusCode, header},
    middleware::{self, Next},
    response::{IntoResponse, Response},
    routing::{get, post, put},
};
use futures_util::{SinkExt, StreamExt};
use serde::Deserialize;
use serde_json::json;
use std::{
    fs,
    io::Write,
    os::unix::fs::OpenOptionsExt,
    path::{Path, PathBuf},
    sync::{Arc, Mutex},
    time::Duration,
};
use tokio::sync::Semaphore;
use tower_http::{services::ServeDir, set_header::SetResponseHeaderLayer};

#[derive(Clone)]
pub struct AppState {
    pub simulation: Arc<Mutex<Simulation>>,
    pub state_dir: Option<PathBuf>,
    pub authority: String,
    pub slots: Arc<Semaphore>,
    pub viewers: Arc<Semaphore>,
}
type ApiResult<T> = std::result::Result<Json<T>, ApiError>;
pub struct ApiError(pub StatusCode, pub String);
impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        (self.0, Json(json!({"error":self.1}))).into_response()
    }
}
fn bad(error: String) -> ApiError {
    ApiError(StatusCode::UNPROCESSABLE_ENTITY, error)
}
fn lock_error() -> ApiError {
    ApiError(
        StatusCode::INTERNAL_SERVER_ERROR,
        "Simulationszustand nicht verfügbar".into(),
    )
}

pub fn router(state: AppState, assets: PathBuf) -> Router {
    Router::new()
        .route("/api/bootstrap",get(bootstrap))
        .route("/api/project",put(apply))
        .route("/api/project/validate",post(validate_project))
        .route("/api/command",post(command))
        .route("/api/packages/validate",post(validate_package))
        .route("/api/stream",get(stream))
        .fallback_service(ServeDir::new(assets))
        .layer(DefaultBodyLimit::max(MAX_DOCUMENT))
        .layer(SetResponseHeaderLayer::overriding(header::CACHE_CONTROL,header::HeaderValue::from_static("no-store")))
        .layer(SetResponseHeaderLayer::overriding(header::X_CONTENT_TYPE_OPTIONS,header::HeaderValue::from_static("nosniff")))
        .layer(SetResponseHeaderLayer::overriding(header::CONTENT_SECURITY_POLICY,header::HeaderValue::from_static("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")))
        .layer(middleware::from_fn_with_state(state.clone(), local_request))
        .with_state(state)
}

async fn local_request(State(state): State<AppState>, request: Request, next: Next) -> Response {
    let host = request
        .headers()
        .get(header::HOST)
        .and_then(|v| v.to_str().ok());
    let port = state.authority.rsplit(':').next().unwrap();
    let localhost = format!("localhost:{port}");
    if host != Some(state.authority.as_str()) && host != Some(localhost.as_str()) {
        return (StatusCode::FORBIDDEN, "Unbekannter lokaler Host").into_response();
    }
    if let Some(origin) = request.headers().get(header::ORIGIN) {
        let allowed = host.map(|h| format!("http://{h}"));
        if origin.to_str().ok() != allowed.as_deref() {
            return (StatusCode::FORBIDDEN, "Fremder Browserursprung").into_response();
        }
    }
    if request
        .headers()
        .get("sec-fetch-site")
        .and_then(|v| v.to_str().ok())
        == Some("cross-site")
    {
        return (StatusCode::FORBIDDEN, "Fremder Browserursprung").into_response();
    }
    if request.method() != axum::http::Method::GET
        && request
            .headers()
            .get("x-virtualwago-client")
            .and_then(|v| v.to_str().ok())
            != Some("workbench")
    {
        return (StatusCode::FORBIDDEN, "Workbench-Clientkennung fehlt").into_response();
    }
    if request.method() != axum::http::Method::GET
        && request
            .headers()
            .get("x-virtualwago-instance")
            .and_then(|v| v.to_str().ok())
            != Some(process_instance())
    {
        return (
            StatusCode::CONFLICT,
            Json(json!({"error":"Dienst wurde neu gestartet; aktuellen Stand neu laden"})),
        )
            .into_response();
    }
    next.run(request).await
}

async fn bootstrap(State(state): State<AppState>) -> ApiResult<serde_json::Value> {
    let sim = state.simulation.lock().map_err(|_| lock_error())?;
    Ok(Json(
        json!({"project":sim.project(),"state":sim.snapshot()}),
    ))
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct CommandRequest {
    generation: u64,
    command: Command,
}
async fn command(
    State(state): State<AppState>,
    Json(input): Json<CommandRequest>,
) -> ApiResult<serde_json::Value> {
    let slot = state.slots.clone().try_acquire_owned().map_err(|_| {
        ApiError(
            StatusCode::SERVICE_UNAVAILABLE,
            "Auftragsgrenze erreicht".into(),
        )
    })?;
    tokio::task::spawn_blocking(move || {
        let _slot = slot;
        let mut sim = state.simulation.lock().map_err(|_| lock_error())?;
        sim.check_generation(input.generation)
            .map_err(|e| ApiError(StatusCode::CONFLICT, e))?;
        sim.command(input.command).map_err(bad)?;
        Ok(Json(json!(sim.snapshot())))
    })
    .await
    .map_err(|_| lock_error())?
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct ApplyRequest {
    generation: u64,
    project: Project,
}
async fn apply(
    State(state): State<AppState>,
    Json(input): Json<ApplyRequest>,
) -> ApiResult<serde_json::Value> {
    let slot = state.slots.clone().try_acquire_owned().map_err(|_| {
        ApiError(
            StatusCode::SERVICE_UNAVAILABLE,
            "Auftragsgrenze erreicht".into(),
        )
    })?;
    tokio::task::spawn_blocking(move || {
        let _slot = slot;
        let mut sim = state.simulation.lock().map_err(|_| lock_error())?;
        sim.check_generation(input.generation)
            .map_err(|e| ApiError(StatusCode::CONFLICT, e))?;
        let prepared = sim.prepare(input.project).map_err(bad)?;
        let synced = if let Some(dir) = &state.state_dir {
            save_project(dir, &prepared.project).map_err(bad)?
        } else {
            true
        };
        sim.activate(prepared);
        if !synced {
            sim.storage_warning();
        }
        Ok(Json(
            json!({"project":sim.project(),"state":sim.snapshot()}),
        ))
    })
    .await
    .map_err(|_| lock_error())?
}
async fn validate_package(
    State(state): State<AppState>,
    Json(package): Json<ModulePackage>,
) -> ApiResult<serde_json::Value> {
    let slot = state.slots.clone().try_acquire_owned().map_err(|_| {
        ApiError(
            StatusCode::SERVICE_UNAVAILABLE,
            "Auftragsgrenze erreicht".into(),
        )
    })?;
    tokio::task::spawn_blocking(move || {
        let _slot = slot;
        package.validate().map_err(bad)?;
        Ok(Json(json!({"sha256":package.digest(),"package":package})))
    })
    .await
    .map_err(|_| lock_error())?
}
async fn validate_project(
    State(state): State<AppState>,
    Json(project): Json<Project>,
) -> ApiResult<serde_json::Value> {
    let slot = state.slots.clone().try_acquire_owned().map_err(|_| {
        ApiError(
            StatusCode::SERVICE_UNAVAILABLE,
            "Auftragsgrenze erreicht".into(),
        )
    })?;
    tokio::task::spawn_blocking(move || {
        let _slot = slot;
        let sim = Simulation::new(project).map_err(bad)?;
        Ok(Json(json!(sim.project())))
    })
    .await
    .map_err(|_| lock_error())?
}
async fn stream(State(state): State<AppState>, upgrade: WebSocketUpgrade) -> Response {
    let Ok(slot) = state.viewers.clone().try_acquire_owned() else {
        return (StatusCode::SERVICE_UNAVAILABLE, "Browsergrenze erreicht").into_response();
    };
    upgrade.max_message_size(1024).max_frame_size(1024).on_upgrade(move |socket|async move {
        let _slot=slot;
        let (mut sender,mut receiver)=socket.split();
        let mut timer=tokio::time::interval(Duration::from_millis(100));
        timer.set_missed_tick_behavior(tokio::time::MissedTickBehavior::Skip);
        loop {
            tokio::select! {
                message=receiver.next()=>match message {
                    Some(Ok(Message::Close(_)))|None|Some(Err(_))=>break,
                    Some(Ok(Message::Ping(bytes)))=> {
                        if !matches!(tokio::time::timeout(Duration::from_secs(2),sender.send(Message::Pong(bytes))).await,Ok(Ok(()))) {break;}
                    },
                    // WebSocket is observation only; commands use validated HTTP.
                    _=>{},
                },
                _=timer.tick()=> {
                    let payload={
                        let Ok(sim)=state.simulation.lock() else {break;};
                        serde_json::to_string(&sim.snapshot()).unwrap()
                    };
                    if !matches!(tokio::time::timeout(Duration::from_secs(2),sender.send(Message::Text(payload.into()))).await,Ok(Ok(()))) {break;}
                }
            }
        }
    })
}

/// Success means rename committed. False reports a subsequent directory fsync
/// failure; the caller must still activate the committed configuration.
pub fn save_project(dir: &Path, project: &Project) -> Result<bool> {
    fs::create_dir_all(dir).map_err(|e| format!("Projektverzeichnis: {e}"))?;
    let target = dir.join("project.json");
    for path in [dir.to_path_buf(), target.clone()] {
        if fs::symlink_metadata(&path).is_ok_and(|m| m.file_type().is_symlink()) {
            return Err("Projektpfad darf kein symbolischer Link sein".into());
        }
    }
    let temp = dir.join(format!(".project.{}.next", process_instance()));
    let mut file = fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .mode(0o600)
        .open(&temp)
        .map_err(|e| format!("Projekt konnte nicht vorbereitet werden: {e}"))?;
    let result = (|| {
        let bytes = serde_json::to_vec_pretty(project).map_err(|e| e.to_string())?;
        file.write_all(&bytes).map_err(|e| e.to_string())?;
        file.sync_all().map_err(|e| e.to_string())?;
        fs::rename(&temp, &target).map_err(|e| e.to_string())?;
        Ok(fs::File::open(dir).and_then(|f| f.sync_all()).is_ok())
    })();
    if result.is_err() {
        let _ = fs::remove_file(&temp);
    }
    result
}

pub fn load_project(dir: &Path) -> Result<Option<Project>> {
    let path = dir.join("project.json");
    let metadata = match fs::symlink_metadata(&path) {
        Ok(v) => v,
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => return Ok(None),
        Err(e) => return Err(e.to_string()),
    };
    if !metadata.is_file()
        || metadata.file_type().is_symlink()
        || metadata.len() > MAX_DOCUMENT as u64
    {
        return Err("Ungültige gespeicherte Projektdatei".into());
    }
    let project: Project = serde_json::from_slice(&fs::read(&path).map_err(|e| e.to_string())?)
        .map_err(|e| e.to_string())?;
    project.validate()?;
    Ok(Some(project))
}
