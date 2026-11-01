// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! Every PDS vector's outcome on the simulator, one line each: the vector file, its id and
//! "ok Exact", "ok Near" or "ok AnyValue" with the fill tile whose run matched,
//! "unsupported: ..." or the mismatch (sgx_sim::vectors::run_pds_tile_match). The coverage
//! report counts these; this lists them, for finding what a model change moves.
//!
//!     RESGX545_DATA=DIR cargo run --release -p sgx-sim --example pds_outcomes

use sgx_sim::vectors::{self, Kind};

fn main() {
    let dir = vectors::data().expect("no resgx545-data/vectors: set RESGX545_DATA");
    for path in vectors::probe_files(&dir) {
        let d = sgx_sim::json::parse(&std::fs::read_to_string(&path).unwrap());
        let raw = d.get("run").get("raw").str().unwrap_or("").to_string();
        for v in d.get("vectors").arr() {
            if vectors::kind(v) != Kind::Pds {
                continue;
            }
            let id = v.get("id").str().unwrap_or("?");
            let probe = v.get("provenance").get("probe").str().unwrap_or("");
            if vectors::skipped(&raw, probe, id).is_some() {
                continue;
            }
            let outcome = match vectors::run_pds_tile_match(v) {
                Ok((o, (x, y))) => format!("ok {o:?} tile ({x}, {y})"),
                Err(e) => e,
            };
            println!("{}\t{id}\t{outcome}", path.strip_prefix(&dir).unwrap().display());
        }
    }
}
