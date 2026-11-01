// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! List what the simulator does with every USSE vector of the data repository: one tab-separated
//! line per vector, `status` (pass, fitted, unsupported, mismatch or skipped; excluded with the
//! reason the replay leaves the vector out; hang-predicted or hang-not-predicted for a job that
//! hung on the hardware, where the simulator does or does not stop at a hanging phas request), the
//! kind (scalar, pixels or firmware), the run's raw file, the vector's id and the reason or the mismatch.
//! The counts before and after a change to the model show what it changed.
//!
//!     RESGX545_DATA=... cargo run --release -p sgx-sim --example replay > replay.tsv
use sgx_sim::vectors::{self, Kind, Outcome};

fn main() {
    let dir = vectors::data().expect("no resgx545-data/vectors: set RESGX545_DATA");
    for path in vectors::probe_files(&dir) {
        let d = vectors::load(&path);
        let raw = d.get("run").get("raw").str().unwrap_or("").to_string();
        for v in d.get("vectors").arr() {
            if v.get("program").get("isa").str() != Some("usse") {
                continue;
            }
            let id = v.get("id").str().unwrap_or("");
            let probe = v.get("provenance").get("probe").str().unwrap_or("");
            let k = vectors::kind(v);
            if k == Kind::None {
                // a job that hung: does the simulator stop on a phas request that hangs (E519)?
                if v.get("readback").get("failed").str().is_some_and(|f| f.starts_with("job hung")) {
                    let status = match vectors::run_scalar(v) {
                        Err(e) if e.contains("hangs the job") => "hang-predicted",
                        _ => "hang-not-predicted",
                    };
                    println!("{status}\tscalar\t{raw}\t{id}\t");
                    continue;
                }
                // every other vector the replay leaves out, with why
                let rb = v.get("readback");
                let tri = v.get("provenance").get("options").arr().iter().any(|o| o.str() == Some("--tri"));
                let why = if let Some(f) = rb.get("failed").str() {
                    format!("the job failed: {f}")
                } else if tri {
                    "a triangle-host readback is the scene's, not the shader's".to_string()
                } else if v.get("init").get("pa0").str() == Some("coords") {
                    "coordinates without every pixel's o0".to_string()
                } else {
                    "the pixels differ and are not reported (a mixture, no single o0)".to_string()
                };
                println!("excluded\t-\t{raw}\t{id}\t{why}");
                continue;
            }
            let (status, why) = match vectors::skipped(&raw, probe, id) {
                Some(w) => ("skipped", w.to_string()),
                None => match vectors::run(v).unwrap() {
                    Ok(Outcome::Fitted) => ("fitted", String::new()),
                    Ok(_) => ("pass", String::new()),
                    Err(e) if e.starts_with("unsupported") => ("unsupported", vectors::reason(&e)),
                    Err(e) => ("mismatch", e),
                },
            };
            let kind = match k {
                Kind::Pixels => "pixels",
                Kind::Firmware => "firmware",
                _ => "scalar",
            };
            println!("{status}\t{kind}\t{raw}\t{id}\t{why}");
        }
    }
}
