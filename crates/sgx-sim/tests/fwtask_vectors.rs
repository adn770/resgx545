// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The simulator against the hardware for a firmware (EDM) task of our own: the 9b runs of phase
//! 11.29 (str then ldr on 0x0814 and 0x0a78), vectors/nokernel/usse/fwtask-9b of the data
//! repository (`$RESGX545_DATA`; skipped without it). Each vector runs our wrapper to its tail call
//! over the results page and the register file of `sgx_sim::fwtask::FwBus`.

use sgx_sim::vectors::{Kind, Outcome, data, kind, load, probe_files, run};

#[test]
fn firmware_task_vectors_match() {
    let Some(dir) = data() else {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no resgx545-data/vectors");
        eprintln!("SKIPPED: no resgx545-data/vectors");
        return;
    };
    let vecs = dir.join("nokernel/usse/fwtask-9b");
    if !vecs.is_dir() {
        eprintln!("SKIPPED: no vectors/nokernel/usse/fwtask-9b in the data repository");
        return;
    }
    let (mut n, mut bad) = (0, Vec::new());
    for e in probe_files(&vecs) {
        let d = load(&e);
        for v in d.get("vectors").arr() {
            assert_eq!(kind(v), Kind::Firmware);
            n += 1;
            match run(v) {
                Some(Ok(Outcome::Exact)) => {}
                other => bad.push(format!("{}: {:?}", v.get("id").str().unwrap_or("?"), other)),
            }
        }
    }
    assert_eq!(n, 318, "the 9b runs of 11.29 are 318 vectors (E534)");
    assert!(bad.is_empty(), "{} of {} firmware vectors differ: {:?}", bad.len(), n, &bad[..bad.len().min(5)]);
    eprintln!("firmware task vectors: {n} match");
}
