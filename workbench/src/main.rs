use std::{
    net::{Ipv4Addr, SocketAddrV4},
    path::PathBuf,
    sync::{
        Arc, Mutex,
        atomic::{AtomicBool, Ordering},
    },
    time::Duration,
};
use virtualwago_workbench::{
    api::{self, AppState},
    engine::Simulation,
    model::demo_project,
};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let mut state_dir = root.join("state");
    let mut assets = root.join("web/dist");
    let mut port = 8787_u16;
    let mut args = std::env::args().skip(1);
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--port" => port = args.next().ok_or("Port fehlt")?.parse()?,
            "--state-dir" => {
                state_dir = PathBuf::from(args.next().ok_or("Projektverzeichnis fehlt")?)
            }
            "--assets" => assets = PathBuf::from(args.next().ok_or("Webverzeichnis fehlt")?),
            "--help" => {
                println!(
                    "virtualwago-workbench [--port 8787] [--state-dir PATH] [--assets PATH]\nLocal offline signal models. Binds only 127.0.0.1; no PLC, CODESYS or hardware adapter."
                );
                return Ok(());
            }
            _ => return Err(format!("Unbekanntes Argument: {arg}").into()),
        }
    }
    if !assets.join("index.html").is_file() {
        return Err(
            "Weboberfläche fehlt: zuerst in workbench/web npm ci und npm run build ausführen"
                .into(),
        );
    }
    let project = api::load_project(&state_dir)?.unwrap_or_else(demo_project);
    let simulation = Arc::new(Mutex::new(Simulation::new(project)?));
    let listener =
        tokio::net::TcpListener::bind(SocketAddrV4::new(Ipv4Addr::LOCALHOST, port)).await?;
    let address = listener.local_addr()?;
    let state = AppState {
        simulation: simulation.clone(),
        state_dir: Some(state_dir),
        authority: address.to_string(),
        slots: Arc::new(tokio::sync::Semaphore::new(32)),
        viewers: Arc::new(tokio::sync::Semaphore::new(8)),
    };
    let stop = Arc::new(AtomicBool::new(false));
    let worker_stop = stop.clone();
    let worker = std::thread::spawn(move || {
        while !worker_stop.load(Ordering::Relaxed) {
            let delay = {
                let Ok(mut sim) = simulation.lock() else {
                    break;
                };
                let delay = sim.project().tick_ms;
                if sim.running {
                    for _ in 0..sim.speed() {
                        if sim.step().is_err() {
                            break;
                        }
                    }
                }
                delay
            };
            // Best-effort host pacing. Logical ticks never catch up after a stall.
            std::thread::sleep(Duration::from_millis(delay as u64));
        }
    });
    println!("virtualWAGO: http://{address}\nOffline-Signalmodell · kein Gerätezugriff");
    let result = axum::serve(listener, api::router(state, assets))
        .with_graceful_shutdown(async {
            let _ = tokio::signal::ctrl_c().await;
        })
        .await;
    stop.store(true, Ordering::Relaxed);
    let _ = worker.join();
    result?;
    Ok(())
}
