// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! Write doc/isa/sim-coverage.json: what the simulator models of each form,
//! against the vectors of the data repository (sgx_sim::vectors).
//!
//! `-- --check` writes nothing and exits 1 when the committed file differs (tools/regen_generated.py);
//! without the vectors, nothing is written or compared.

fn main() {
    let out = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../doc/isa/sim-coverage.json");
    let check = std::env::args().any(|a| a == "--check");
    let Some(dir) = sgx_sim::vectors::data() else {
        eprintln!("no resgx545-data/vectors (set RESGX545_DATA): {} left alone", out.display());
        return;
    };
    let now = sgx_sim::vectors::coverage_json(&dir);
    if check {
        if std::fs::read_to_string(&out).unwrap_or_default() != now {
            eprintln!("{} differs from its regeneration", out.display());
            std::process::exit(1);
        }
        return;
    }
    std::fs::write(&out, now).unwrap();
    eprintln!("wrote {}", out.display());
}
