// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The vertex-task global-register vectors of phase 11.33 (q053-vtx, q053-vtx2: 12 hardware jobs of 126 vertices):
//! each vertex of each job runs the job's movs as the vertex of the draw (Machine::vertex) and its outputs equal the
//! hardware's stored vertex words. The vectors are in the data repository's
//! `vectors/nokernel/usse/globals-vertex/` (`$RESGX545_DATA`, or `$SGX_SIM_OVERLAY` while they are only in a
//! working copy: a `vectors/` directory laid out as the data repository's); without them the test does nothing and
//! says so ("SKIPPED"), and with `RESGX545_REQUIRE_DATA` set it fails instead.

use sgx_sim::json::parse;
use sgx_sim::vectors::{data, run_vertex};
use std::path::PathBuf;

/// The directory of the vectors, the overlay's first, or None (with the reason said).
fn dir() -> Option<PathBuf> {
    let overlay = std::env::var_os("SGX_SIM_OVERLAY").map(|p| PathBuf::from(p).join("vectors"));
    let d = overlay.into_iter().chain(data()).map(|v| v.join("nokernel/usse/globals-vertex")).find(|d| d.is_dir());
    if d.is_none() {
        let msg = "no vectors/nokernel/usse/globals-vertex (set RESGX545_DATA or SGX_SIM_OVERLAY)";
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "{msg}");
        eprintln!("SKIPPED: {msg}");
    }
    d
}

#[test]
fn the_vertex_task_globals_match_the_hardware() {
    let Some(d) = dir() else { return };
    let mut n = 0;
    for f in ["q053-vtx.vec.json", "q053-vtx2.vec.json"] {
        let doc = parse(&std::fs::read_to_string(d.join(f)).expect("a vertex vector file"));
        for v in doc.get("vectors").arr() {
            let r = run_vertex(v);
            assert!(r.is_ok(), "{}: {:?}", v.get("id").str().unwrap_or("?"), r);
            n += 1;
        }
    }
    assert_eq!(n, 12);
}

/// Every raw file a vector file names exists in the data repository and has its sha256 recorded (the
/// digests themselves are checked by tools/usse-asm/test_make_vertex_vectors.py: the crate has no hash).
#[test]
fn the_vertex_vectors_name_their_raw_files() {
    let Some(d) = dir() else { return };
    let Some(root) = data().and_then(|v| v.parent().map(PathBuf::from)) else {
        eprintln!("SKIPPED: no data repository to resolve the raw files in");
        return;
    };
    for f in ["q053-vtx.vec.json", "q053-vtx2.vec.json"] {
        let doc = parse(&std::fs::read_to_string(d.join(f)).expect("a vertex vector file"));
        let (raws, shas) = (doc.get("run").get("raw").arr(), doc.get("run").get("raw_sha256").arr());
        assert_eq!(raws.len(), 6, "{f}");
        assert_eq!(raws.len(), shas.len(), "{f}");
        for (r, s) in raws.iter().zip(shas) {
            let p = r.str().expect("a raw path");
            assert!(root.join(p).is_file(), "{f}: {p} does not resolve in the data repository");
            let h = s.str().expect("a sha256");
            assert!(h.len() == 64 && h.bytes().all(|c| c.is_ascii_digit() || (b'a'..=b'f').contains(&c)), "{f}: {h}");
        }
    }
}
