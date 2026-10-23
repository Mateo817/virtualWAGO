use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::{HashMap, HashSet};

pub type Result<T> = std::result::Result<T, String>;
pub const MAX_DOCUMENT: usize = 512 * 1024;

#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum Direction {
    Input,
    Output,
}

#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum Kind {
    Digital,
    Analog,
}

/// Own signal codecs. They never define a native ADI layout or bus identity.
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(tag = "codec", rename_all = "snake_case", deny_unknown_fields)]
pub enum Encoding {
    Bit,
    Ai466Standard,
    Ao550Standard,
    Linear {
        scale: f64,
        offset: f64,
        max_raw: u32,
    },
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Channel {
    pub id: String,
    pub label: String,
    pub direction: Direction,
    pub kind: Kind,
    pub unit: String,
    pub min: f64,
    pub max: f64,
    pub initial: f64,
    pub encoding: Encoding,
}

impl Channel {
    pub fn check(&self, value: f64) -> Result<f64> {
        if !value.is_finite() || value < self.min || value > self.max {
            return Err(format!(
                "{}: Wert außerhalb [{}, {}]",
                self.label, self.min, self.max
            ));
        }
        if self.kind == Kind::Digital && value != 0.0 && value != 1.0 {
            return Err(format!("{}: Digitalsignal muss 0 oder 1 sein", self.label));
        }
        Ok(value)
    }
    pub fn raw(&self, value: f64) -> u32 {
        match self.encoding {
            Encoding::Bit => value as u32,
            Encoding::Ai466Standard => encode_ai466((value * 1000.0).round() as u32),
            // Nearest code, with the same piecewise normal-range table as Python.
            // This inverse quantization is an own model assumption.
            Encoding::Ao550Standard => {
                let mv = value * 1000.0;
                let anchors = [
                    (0., 0.),
                    (1250., 4096.),
                    (2500., 8192.),
                    (3750., 12288.),
                    (5000., 16384.),
                    (6250., 20480.),
                    (7500., 24576.),
                    (8750., 28672.),
                    (10000., 32760.),
                ];
                let pair = anchors.windows(2).find(|a| mv <= a[1].0).unwrap();
                let code = pair[0].1
                    + (mv - pair[0].0) * (pair[1].1 - pair[0].1) / (pair[1].0 - pair[0].0);
                ((code / 8.0).round() as u32 * 8).min(32760)
            }
            Encoding::Linear {
                scale,
                offset,
                max_raw,
            } => ((value * scale + offset).round().clamp(0.0, max_raw as f64)) as u32,
        }
    }
}

pub fn encode_ai466(current_ua: u32) -> u32 {
    (((current_ua.saturating_sub(4000) as u64 * 4096 / 16000).min(4095)) << 3) as u32
}

pub fn decode_ao550(word: u32) -> u32 {
    let code = word & 0x7ff8;
    let anchors = [
        (0, 0),
        (4096, 1250),
        (8192, 2500),
        (12288, 3750),
        (16384, 5000),
        (20480, 6250),
        (24576, 7500),
        (28672, 8750),
        (32760, 10000),
    ];
    for pair in anchors.windows(2) {
        let [(lo, lv), (hi, hv)] = [pair[0], pair[1]];
        if code <= hi {
            return lv + ((code - lo) * (hv - lv) + (hi - lo) / 2) / (hi - lo);
        }
    }
    10000
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ModulePackage {
    pub schema: u32,
    pub id: String,
    pub version: String,
    pub article: String,
    pub title: String,
    pub family: String,
    pub description: String,
    pub evidence: String,
    pub assumptions: String,
    pub channels: Vec<Channel>,
}

pub fn text(value: &str, limit: usize, name: &str) -> Result<()> {
    if value.is_empty() || value.len() > limit || value.chars().any(|c| c.is_control()) {
        return Err(format!("{name}: ungültiger oder zu langer Text"));
    }
    Ok(())
}
pub fn identifier(value: &str) -> Result<()> {
    if value.is_empty()
        || value.len() > 80
        || !value
            .bytes()
            .all(|b| b.is_ascii_alphanumeric() || b"_.-".contains(&b))
    {
        return Err("Ungültige stabile Kennung".into());
    }
    Ok(())
}
impl ModulePackage {
    pub fn digest(&self) -> String {
        format!(
            "{:x}",
            Sha256::digest(serde_json::to_vec(self).expect("validated package"))
        )
    }
    pub fn validate(&self) -> Result<()> {
        if self.schema != 1 || self.channels.len() > 64 {
            return Err("Modulpaket: Schema 1 und höchstens 64 Kanäle erforderlich".into());
        }
        identifier(&self.id)?;
        for (value, limit) in [
            (&self.version, 40),
            (&self.article, 40),
            (&self.title, 100),
            (&self.description, 1500),
            (&self.evidence, 500),
            (&self.assumptions, 3000),
        ] {
            text(value, limit, "Modulpaket")?;
        }
        if !["di", "do", "ai", "ao", "passive"].contains(&self.family.as_str()) {
            return Err("Unbekannte Modulfamilie".into());
        }
        if self.channels.is_empty() != (self.family == "passive") {
            return Err("Nur passive Module dürfen ohne Kanäle sein".into());
        }
        let mut ids = HashSet::new();
        for c in &self.channels {
            identifier(&c.id)?;
            text(&c.label, 80, "Kanalname")?;
            if c.unit.len() > 20 || c.unit.chars().any(|v| v.is_control()) {
                return Err("Ungültige Einheit".into());
            }
            if !ids.insert(&c.id)
                || !c.min.is_finite()
                || !c.max.is_finite()
                || c.min >= c.max
                || c.min.abs() > 1e9
                || c.max.abs() > 1e9
            {
                return Err("Ungültige Kanalgrenzen oder doppelte Kennung".into());
            }
            c.check(c.initial)?;
            if c.direction == Direction::Output && (c.min > 0. || c.max < 0. || c.initial != 0.) {
                return Err("Ausgänge benötigen 0 als sicheren Startwert".into());
            }
            match (&c.encoding, c.kind, c.direction) {
                (Encoding::Bit, Kind::Digital, _) if c.min == 0. && c.max == 1. => {}
                (Encoding::Ai466Standard, Kind::Analog, Direction::Input)
                    if c.min == 4. && c.max == 20. => {}
                (Encoding::Ao550Standard, Kind::Analog, Direction::Output)
                    if c.min == 0. && c.max == 10. => {}
                (
                    Encoding::Linear {
                        scale,
                        offset,
                        max_raw,
                    },
                    Kind::Analog,
                    _,
                ) if scale.is_finite()
                    && *scale != 0.0
                    && offset.is_finite()
                    && scale.abs() <= 1e9
                    && offset.abs() <= 1e12
                    && *max_raw > 0 => {}
                _ => return Err("Kanaltyp, Bereich und Signalcodec passen nicht zusammen".into()),
            }
            if c.direction
                != if self.family.ends_with('i') {
                    Direction::Input
                } else {
                    Direction::Output
                }
            {
                return Err("Kanalrichtung passt nicht zur Modulfamilie".into());
            }
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq, Eq, Hash)]
#[serde(deny_unknown_fields)]
pub struct SignalRef {
    pub module: String,
    pub channel: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Instance {
    pub id: String,
    pub package: String,
    pub package_sha256: String,
    pub label: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Reaction {
    pub id: String,
    pub name: String,
    pub enabled: bool,
    pub source: Option<SignalRef>,
    #[serde(default)]
    pub sources: Vec<SignalRef>,
    #[serde(default)]
    pub stateful: bool,
    pub target: SignalRef,
    pub code: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Project {
    pub schema: u32,
    pub name: String,
    pub tick_ms: u32,
    pub packages: Vec<ModulePackage>,
    pub modules: Vec<Instance>,
    pub reactions: Vec<Reaction>,
    #[serde(default)]
    pub scenarios: Vec<crate::scenario::Scenario>,
}
impl Project {
    pub fn channel(&self, signal: &SignalRef) -> Result<&Channel> {
        let module = self
            .modules
            .iter()
            .find(|m| m.id == signal.module)
            .ok_or("Modulinstanz fehlt")?;
        let package = self
            .packages
            .iter()
            .find(|p| p.id == module.package)
            .ok_or("Modulpaket fehlt")?;
        package
            .channels
            .iter()
            .find(|c| c.id == signal.channel)
            .ok_or("Kanal fehlt".into())
    }
    pub fn validate(&self) -> Result<()> {
        if self.schema != 1
            || !(1..=1000).contains(&self.tick_ms)
            || self.packages.is_empty()
            || self.packages.len() > 64
            || self.modules.len() > 64
            || self.reactions.len() > 32
        {
            return Err(
                "Projektgrenzen verletzt (Schema 1, 1–1000 ms, 64 Pakete/Module, 32 Skripte)"
                    .into(),
            );
        }
        text(&self.name, 100, "Projektname")?;
        if serde_json::to_vec(self).map_err(|e| e.to_string())?.len() > MAX_DOCUMENT {
            return Err("Projekt zu groß".into());
        }
        let mut packages = HashMap::new();
        for p in &self.packages {
            p.validate()?;
            if packages.insert(&p.id, p).is_some() {
                return Err("Doppeltes Modulpaket".into());
            }
        }
        let mut ids = HashSet::new();
        let mut count = 0;
        for m in &self.modules {
            identifier(&m.id)?;
            text(&m.label, 100, "Instanzname")?;
            if !ids.insert(&m.id) {
                return Err("Doppelte Modulinstanz".into());
            }
            let p = packages.get(&m.package).ok_or("Modulpaket fehlt")?;
            if m.package_sha256 != p.digest() {
                return Err("Modulpaket wurde geändert: Hashbindung prüfen".into());
            }
            count += p.channels.len();
        }
        if count > 1024 {
            return Err("Höchstens 1024 Kanäle".into());
        }
        crate::scenario::validate_scenarios(self)?;
        let mut writers = HashSet::new();
        ids.clear();
        for r in &self.reactions {
            identifier(&r.id)?;
            text(&r.name, 100, "Skriptname")?;
            if !ids.insert(&r.id) || r.code.is_empty() || r.code.len() > 8192 {
                return Err("Doppelte Skriptkennung oder Skript zu groß".into());
            }
            if self.channel(&r.target)?.direction != Direction::Input {
                return Err("Reaktionsskripte dürfen nur Eingänge liefern".into());
            }
            if let Some(source) = &r.source
                && self.channel(source)?.direction != Direction::Output
            {
                return Err("Reaktionsquelle muss ein Ausgang sein".into());
            }
            if r.sources.len() + usize::from(r.source.is_some()) > 16
                || (!r.stateful && !r.sources.is_empty())
            {
                return Err(
                    "Zusätzliche Quellen: höchstens 16, nur für zustandsbehaftete Modelle".into(),
                );
            }
            let mut sources = HashSet::new();
            for source in r.sources.iter().chain(r.source.iter()) {
                if self.channel(source)?.direction != Direction::Output || !sources.insert(source) {
                    return Err("Reaktionsquellen müssen verschiedene Ausgänge sein".into());
                }
            }
            if r.enabled && !writers.insert(&r.target) {
                return Err("Mehrere aktive Skripte schreiben denselben Eingang".into());
            }
        }
        Ok(())
    }
}

pub fn bundled_packages() -> Result<Vec<ModulePackage>> {
    [
        include_str!("../module-packs/750-430.json"),
        include_str!("../module-packs/750-530.json"),
        include_str!("../module-packs/750-1405.json"),
        include_str!("../module-packs/750-1504.json"),
        include_str!("../module-packs/750-466.json"),
        include_str!("../module-packs/750-550.json"),
        include_str!("../module-packs/750-600.json"),
    ]
    .into_iter()
    .map(|s| {
        let p: ModulePackage = serde_json::from_str(s).map_err(|e| e.to_string())?;
        p.validate()?;
        Ok(p)
    })
    .collect()
}

pub fn demo_project() -> Project {
    let packages = bundled_packages().expect("bundled packages validated in tests");
    let modules = [
        ("di-bank", "750-430", "Digitale Rückmeldungen"),
        ("do-bank", "750-530", "Digitale Testausgänge"),
        ("ai-bank", "750-466", "Stromsignale"),
        ("ao-bank", "750-550", "Spannungsausgänge"),
        ("end", "750-600", "Busabschluss"),
    ]
    .into_iter()
    .map(|(id, article, label)| {
        let p = packages.iter().find(|p| p.article == article).unwrap();
        Instance {
            id: id.into(),
            package: p.id.clone(),
            package_sha256: p.digest(),
            label: label.into(),
        }
    })
    .collect();
    Project { schema:1, name:"Meine erste Simulation".into(), tick_ms:20, packages, modules,
        scenarios:vec![], reactions:vec![Reaction { id:"valve-feedback".into(), name:"Ventilrückmeldung".into(), enabled:true,
            sources:vec![], stateful:false, source:Some(SignalRef { module:"do-bank".into(), channel:"ch1".into() }),
            target:SignalRef { module:"di-bank".into(), channel:"ch1".into() },
            code:"// Wirksamer Ausgang → Rückmeldung am Eingang\nfn react(output, previous, dt_s, time_s) {\n    if output > 0.5 { 1.0 } else { 0.0 }\n}".into() }] }
}
