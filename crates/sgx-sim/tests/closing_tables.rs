// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The data statements of the closing pass the simulator does not replay (round 4, sim item 4 of R3-P11):
//! `vectors/closing/{r3-geo,r3k-pixel,r3-geo-c}/` of the data repository, made by
//! `tools/usse-asm/closing_tables.py`. The TA's depth words, the DPM abort sequence, the parameter buffer pages and
//! the ZLS store are not modelled by sgx-sim, so every table says `replay.status` `refused` with its reason; this
//! test holds the files to that: a table with rows and no refusal would be a claim without a check, and it prints
//! what it refuses instead of passing it. Without the data the test does nothing and says so ("SKIPPED"); with
//! `RESGX545_REQUIRE_DATA` set it fails instead.

use sgx_sim::json::parse;
use sgx_sim::vectors::data;
use std::path::{Path, PathBuf};

fn tables(d: &Path, out: &mut Vec<PathBuf>) {
    let Ok(rd) = std::fs::read_dir(d) else { return };
    let mut es: Vec<_> = rd.flatten().map(|e| e.path()).collect();
    es.sort();
    for p in es {
        if p.is_dir() {
            tables(&p, out);
        } else if p.to_string_lossy().ends_with(".table.json") {
            out.push(p);
        }
    }
}

#[test]
fn every_table_of_the_closing_pass_is_refused_with_a_reason() {
    let root = std::env::var_os("SGX_SIM_OVERLAY")
        .map(|p| PathBuf::from(p).join("vectors"))
        .into_iter()
        .chain(data())
        .map(|v| v.join("closing"))
        .find(|d| d.is_dir());
    let Some(root) = root else {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no vectors/closing");
        eprintln!("SKIPPED: no vectors/closing (set RESGX545_DATA or SGX_SIM_OVERLAY)");
        return;
    };
    let mut files = Vec::new();
    tables(&root, &mut files);
    let mut rows = 0;
    for f in &files {
        let j = parse(&std::fs::read_to_string(f).unwrap());
        let name = f.strip_prefix(&root).unwrap().display().to_string();
        assert_eq!(j.get("format").str(), Some("sgx545-tables"), "{name}");
        let r = j.get("replay");
        assert_eq!(r.get("status").str(), Some("refused"), "{name}: a table no simulator replays is refused, not passed");
        assert!(!r.get("reason").str().unwrap_or("").is_empty(), "{name}: no reason");
        let n = j.get("rows").arr().len();
        assert!(n > 0, "{name}: no rows");
        rows += n;
        eprintln!("REFUSED {name}: {n} rows ({})", r.get("reason").str().unwrap());
    }
    eprintln!("{} tables, {rows} rows refused", files.len());
}
