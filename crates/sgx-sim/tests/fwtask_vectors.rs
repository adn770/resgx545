// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The simulator against the hardware for a firmware (EDM) task of our own: the 9b runs of phase
//! 11.29 (str then ldr on 0x0814 and 0x0a78) and the runs of phase 11.30 (state between tasks, the
//! event word, a slow task, the temporaries), vectors/nokernel/usse/fwtask-* of the data
//! repository (`$RESGX545_DATA`; skipped without it). Each vector runs our wrapper to its tail call
//! over the results page and the register file of `sgx_sim::fwtask::FwBus`.

/// The vectors of each set, as the conversions made them (E534, E536, E538, E539, E540): a set that
/// is present must have all of them, so a lost file is a failure and not a smaller count.
const SETS: [(&str, usize); 5] =
    [("fwtask-9b", 318), ("fwtask-state", 14), ("fwtask-events", 6), ("fwtask-slow", 10), ("fwtask-trc", 1)];

use sgx_sim::vectors::{Kind, Outcome, data, kind, load, probe_files, run};

#[test]
fn firmware_task_vectors_match() {
    let Some(dir) = data() else {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no resgx545-data/vectors");
        eprintln!("SKIPPED: no resgx545-data/vectors");
        return;
    };
    let usse = dir.join("nokernel/usse");
    let mut dirs: Vec<_> = std::fs::read_dir(&usse)
        .map(|rd| rd.filter_map(|e| e.ok()).map(|e| e.path()).filter(|p| p.is_dir()).collect())
        .unwrap_or_default();
    dirs.retain(|p| p.file_name().and_then(|n| n.to_str()).is_some_and(|n| n.starts_with("fwtask-")));
    dirs.sort();
    if dirs.is_empty() {
        eprintln!("SKIPPED: no vectors/nokernel/usse/fwtask-* in the data repository");
        return;
    }
    let (mut n, mut bad) = (0, Vec::new());
    for dir in &dirs {
        let name = dir.file_name().and_then(|n| n.to_str()).unwrap_or("");
        let mut in_set = 0;
        for e in probe_files(dir) {
            let d = load(&e);
            for v in d.get("vectors").arr() {
                assert_eq!(kind(v), Kind::Firmware);
                in_set += 1;
                match run(v) {
                    Some(Ok(Outcome::Exact)) => {}
                    other => bad.push(format!("{}: {:?}", v.get("id").str().unwrap_or("?"), other)),
                }
            }
        }
        match SETS.iter().find(|(s, _)| *s == name) {
            Some((_, want)) => assert_eq!(in_set, *want, "{name} has {want} vectors"),
            None => assert!(in_set > 0, "{name} holds no vector"),
        }
        n += in_set;
    }
    assert!(n > 0, "no firmware task vectors");
    assert!(bad.is_empty(), "{} of {} firmware vectors differ: {:?}", bad.len(), n, &bad[..bad.len().min(5)]);
    eprintln!("firmware task vectors: {n} match");
}
