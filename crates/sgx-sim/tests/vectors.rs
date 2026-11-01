// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The simulator against the hardware: every recorded instruction vector in
//! the data repository's vectors/ directory (doc/specs/vectors.md; `$RESGX545_DATA` or
//! `resgx545-data` beside this tree; the tests skip without it). Each runs as one
//! instance, the scratch dwords and o0 equal to the readback; a vector that
//! reports every pixel runs as the fill's 2x2 quads, every pixel's o0 equal.

use sgx_sim::json;
use sgx_sim::vectors::{
    Kind, SKIP, data, kind, probe_files, reason, run_pds, run_pixels, run_scalar as run, skipped,
};
use std::collections::BTreeMap;
use std::path::PathBuf;

/// The vectors directory, or None when the data repository is absent: the test then does
/// nothing and says so ("SKIPPED"), and with `RESGX545_REQUIRE_DATA` set (the release gate)
/// it fails instead of passing without having run.
fn vectors() -> Option<PathBuf> {
    let d = data();
    if d.is_none() {
        let msg = "no resgx545-data/vectors (set RESGX545_DATA or place it beside the tree)";
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "{msg}");
        eprintln!("SKIPPED: {msg}");
    }
    d
}

/// The USSE probe vectors: every one the simulator models must match; the
/// summary says how many it models.
#[test]
fn probe_vectors_match_where_modelled() {
    let Some(dir) = vectors() else { return };
    let rd = probe_files(&dir);
    assert!(!rd.is_empty(), "no vectors in {}", dir.display());
    let (mut pass, mut unsup, mut fail) = (0, 0, Vec::new());
    let mut whys = BTreeMap::<String, usize>::new();
    // SGX_SIM_SHOW=<text>: list the unsupported cases whose reason contains it
    let show = std::env::var("SGX_SIM_SHOW").ok();
    for e in rd {
        let d = json::parse(&std::fs::read_to_string(e).unwrap());
        for v in d.get("vectors").arr() {
            let rb = v.get("readback");
            if rb.get("failed").str().is_some() || v.get("program").get("isa").str() != Some("usse") {
                continue;
            }
            let probe = v.get("provenance").get("probe").str().unwrap_or("");
            let raw = d.get("run").get("raw").str().unwrap_or("");
            if skipped(raw, probe, v.get("id").str().unwrap_or("")).is_some() {
                continue;
            }
            // pixels other than the uniform o0, and coordinates, need every instance; a
            // triangle-host readback is the scene's, not the shader's (kind)
            if kind(v) != Kind::Scalar {
                continue;
            }
            match run(v) {
                Ok(_) => pass += 1,
                Err(e) if e.starts_with("unsupported") => {
                    unsup += 1;
                    if show.as_deref().is_some_and(|t| e.contains(t)) {
                        eprintln!("{} [{raw}]: {e}", v.get("id").str().unwrap());
                    }
                    // "unsupported: <pc>: <text>: <why>": group by why, and the
                    // forms without semantics by mnemonic
                    let parts: Vec<&str> = e.splitn(4, ": ").collect();
                    let why = parts.last().unwrap();
                    let w: String = if why.starts_with("no semantics") {
                        let text = parts.get(2).unwrap_or(&"");
                        let m = text
                            .split_whitespace()
                            .find(|t| !t.starts_with('p') && !t.starts_with('!') || t.len() > 3);
                        format!("no semantics: {}", m.unwrap_or("").split('.').next().unwrap())
                    } else if why.starts_with("test") {
                        why.to_string()
                    } else {
                        why.split(|c: char| c.is_ascii_digit()).next().unwrap().to_string()
                    };
                    *whys.entry(w).or_default() += 1;
                }
                Err(e) => fail.push(format!(
                    "{} [{}]: {e}",
                    v.get("id").str().unwrap(),
                    d.get("run").get("raw").str().unwrap_or("")
                )),
            }
        }
    }
    eprintln!("probes: {pass} pass, {unsup} unsupported, {} fail", fail.len());
    // a regression that turns the passes into unsupported vectors must not stay green
    assert!(pass > 5000, "only {pass} probe vectors pass");
    let mut top: Vec<_> = whys.into_iter().collect();
    top.sort_by_key(|x| std::cmp::Reverse(x.1));
    for (w, n) in top.iter().take(60) {
        eprintln!("  unsupported x{n}  {w}");
    }
    assert!(fail.is_empty(), "{} mismatches:\n{}", fail.len(), fail[..fail.len().min(200)].join("\n"));
}

/// The PDS vectors: every one matches or stops unsupported (a program or an input whose
/// meaning is open), and none may mismatch.
#[test]
fn pds_vectors_match_the_hardware() {
    let Some(dir) = vectors() else { return };
    let (mut pass, mut unsup, mut fail) = (0, BTreeMap::<String, usize>::new(), Vec::new());
    for path in probe_files(&dir) {
        let d = json::parse(&std::fs::read_to_string(&path).unwrap());
        for v in d.get("vectors").arr() {
            if kind(v) != Kind::Pds {
                continue;
            }
            let (id, pv) = (v.get("id").str().unwrap(), v.get("provenance"));
            let raw = d.get("run").get("raw").str().unwrap_or("");
            if skipped(raw, pv.get("probe").str().unwrap_or(""), id).is_some() {
                continue;
            }
            match run_pds(v) {
                Ok(_) => pass += 1,
                Err(e) if e.starts_with("unsupported") => {
                    *unsup
                        .entry(format!("{}: {}", pv.get("probe").str().unwrap(), reason(&e)))
                        .or_default() += 1;
                }
                Err(e) => fail.push(format!("{id}: {e}")),
            }
        }
    }
    eprintln!("pds: {pass} pass, {} unsupported, {} fail", unsup.values().sum::<usize>(), fail.len());
    let mut top: Vec<_> = unsup.iter().collect();
    top.sort_by_key(|x| std::cmp::Reverse(*x.1));
    for (k, n) in top.iter().take(40) {
        eprintln!("  unsupported x{n}  {k}");
    }
    assert!(pass > 0, "no PDS vectors in {}", dir.display());
    assert!(fail.is_empty(), "{} mismatches:\n{}", fail.len(), fail[..fail.len().min(200)].join("\n"));
}

/// The vectors that report every pixel, run as quads.
#[test]
fn pixel_vectors_match_where_modelled() {
    let Some(dir) = vectors() else { return };
    let (mut pass, mut unsup, mut fail) = (0, 0, Vec::new());
    let mut whys = BTreeMap::<String, usize>::new();
    for e in probe_files(&dir) {
        let d = json::parse(&std::fs::read_to_string(e).unwrap());
        let raw = d.get("run").get("raw").str().unwrap_or("").to_string();
        for v in d.get("vectors").arr() {
            let rb = v.get("readback");
            if rb.get("failed").str().is_some()
                || rb.get("pixels").arr().is_empty()
                || v.get("init").get("pa0").str() != Some("coords")
            {
                continue;
            }
            let probe = v.get("provenance").get("probe").str().unwrap_or("");
            if skipped(&raw, probe, v.get("id").str().unwrap_or("")).is_some() {
                continue;
            }
            match run_pixels(v) {
                Ok(_) => pass += 1,
                Err(e) if e.starts_with("unsupported") => {
                    unsup += 1;
                    let why = e.rsplit(": ").next().unwrap();
                    *whys
                        .entry(why.split(|c: char| c.is_ascii_digit()).next().unwrap().to_string())
                        .or_default() += 1;
                }
                Err(e) => fail.push(format!("{} [{raw}]: {e}", v.get("id").str().unwrap())),
            }
        }
    }
    eprintln!("pixel vectors: {pass} pass, {unsup} unsupported, {} fail", fail.len());
    assert!(pass > 100, "only {pass} pixel vectors pass");
    let mut top: Vec<_> = whys.into_iter().collect();
    top.sort_by_key(|x| std::cmp::Reverse(x.1));
    for (w, n) in top.iter().take(20) {
        eprintln!("  unsupported x{n}  {w}");
    }
    assert!(fail.is_empty(), "{} mismatches:\n{}", fail.len(), fail[..fail.len().min(40)].join("\n"));
}

/// Every row of the skip list matches at least one vector (a typo in an id or a renamed probe
/// would otherwise hide nothing and go unnoticed), and the count of each is reported.
#[test]
fn every_skip_row_matches_a_vector() {
    let Some(dir) = vectors() else { return };
    let mut hits = vec![0usize; SKIP.len()];
    for path in probe_files(&dir) {
        let d = json::parse(&std::fs::read_to_string(&path).unwrap());
        let raw = d.get("run").get("raw").str().unwrap_or("");
        for v in d.get("vectors").arr() {
            let probe = v.get("provenance").get("probe").str().unwrap_or("");
            let id = v.get("id").str().unwrap_or("");
            for (i, (r, p, _)) in SKIP.iter().enumerate() {
                if (p.is_empty() || *p == probe || *p == id) && raw.starts_with(r) {
                    hits[i] += 1;
                }
            }
        }
    }
    for ((r, p, why), n) in SKIP.iter().zip(&hits) {
        eprintln!("skipped {n:4}  [{r}] {p}: {why}");
    }
    let dead: Vec<_> = SKIP.iter().zip(&hits).filter(|(_, n)| **n == 0).map(|(s, _)| s.1).collect();
    assert!(dead.is_empty(), "skip rows that match no vector: {dead:?}");
}

/// doc/isa/sim-coverage.json, which the ISA documents render per group, says
/// what the simulator does with the vectors; RESGX545_WRITE_COVERAGE=1 rewrites it.
#[test]
fn the_coverage_report_is_fresh() {
    let Some(dir) = vectors() else { return };
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../doc/isa/sim-coverage.json");
    let now = sgx_sim::vectors::coverage_json(&dir);
    if std::env::var_os("RESGX545_WRITE_COVERAGE").is_some() {
        std::fs::write(&path, &now).unwrap();
        return;
    }
    let committed = std::fs::read_to_string(&path).unwrap_or_default();
    assert!(
        committed == now,
        "doc/isa/sim-coverage.json is stale: RESGX545_WRITE_COVERAGE=1 cargo test --release -p sgx-sim, then \
         python3 doc/isa/build.py"
    );
}
