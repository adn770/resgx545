// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! Write doc/isa/sim-coverage.json: what the simulator models of each form,
//! against the vectors of the data repository (sgx_sim::vectors).

fn main() {
    let out = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../doc/isa/sim-coverage.json");
    let dir = sgx_sim::vectors::data().expect("no resgx545-data/vectors: set RESGX545_DATA");
    std::fs::write(&out, sgx_sim::vectors::coverage_json(&dir)).unwrap();
    eprintln!("wrote {}", out.display());
}
