// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! Write doc/isa/sim-coverage.json: what the simulator models of each form,
//! against the vectors of the data repository (sgx_sim::vectors).
//!
//! `-- --out FILE` names the file (required: no path is compiled in, so a binary shared between
//! worktrees never writes into another one's tree).
//!
//! `-- --check` writes nothing and exits 1 when the committed file differs (tools/regen_generated.py);
//! without the vectors, nothing is written or compared.

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let Some(out) = args.iter().position(|a| a == "--out").and_then(|i| args.get(i + 1)) else {
        eprintln!("usage: coverage [--check] --out FILE (the doc/isa/sim-coverage.json of the tree)");
        std::process::exit(2);
    };
    let out = std::path::PathBuf::from(out);
    let check = args.iter().any(|a| a == "--check");
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
