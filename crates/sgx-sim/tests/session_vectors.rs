// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The probe jobs of round 25's sessions replayed (round 26 P1), from the data repository's
//! `vectors/closing/r25-sa64/pds/` (E1104) and `vectors/closing/r25-csc/texture/` (E1103), made by
//! `tools/usse-asm/closing_vectors.py --probes`. The vectors are in the data repository
//! (`$RESGX545_DATA`, or `$SGX_SIM_OVERLAY` while only in a working copy); without them the tests do
//! nothing and say so ("SKIPPED"), and with `RESGX545_REQUIRE_DATA` set they fail instead.

use sgx_sim::json::{Json, parse};
use sgx_sim::vectors::{Outcome, data, run_pds, run_pixels};
use std::path::PathBuf;

/// A vector file by its path in the data repository (`vectors/...`).
fn file(path: &str) -> Option<Json> {
    let rel = path.trim_start_matches("vectors/");
    let overlay = std::env::var_os("SGX_SIM_OVERLAY").map(|p| PathBuf::from(p).join("vectors"));
    let found = overlay.into_iter().chain(data()).map(|v| v.join(rel)).find(|p| p.is_file());
    let Some(found) = found else {
        let msg = format!("no {path} (set RESGX545_DATA or SGX_SIM_OVERLAY)");
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "{msg}");
        eprintln!("SKIPPED: {msg}");
        return None;
    };
    Some(parse(&std::fs::read_to_string(&found).unwrap()))
}

/// The vector with one readback scratch dword (`off`, "0x0c0") set to `val`, and another field
/// of init replaced.
fn with(v: &Json, off: Option<(&str, &str)>, init: Option<(&str, Json)>) -> Json {
    let mut v = v.clone();
    let Json::Obj(top) = &mut v else { panic!() };
    for (k, x) in top.iter_mut() {
        match (k.as_str(), x) {
            ("readback", Json::Obj(rb)) => {
                for (k, s) in rb.iter_mut() {
                    if let (Some((o, val)), "scratch", Json::Obj(sc)) = (off, k.as_str(), s) {
                        sc.retain(|(k, _)| k != o);
                        sc.push((o.to_string(), Json::Str(val.to_string())));
                    }
                }
            }
            ("init", Json::Obj(i)) => {
                if let Some((name, val)) = &init {
                    i.retain(|(k, _)| k != name);
                    i.push((name.to_string(), val.clone()));
                }
            }
            _ => {}
        }
    }
    v
}

/// E1104: every job of pk64 and q019 replays, each set's sixteen markers checked exactly at their own
/// sa (sa0-sa63; the other attributes hold what earlier jobs left, AnyValue); a marker changed in the
/// readback fails (the control), and the vector cut back to 16 attributes stops at sa16.
#[test]
fn r25_sa64_jobs_replay_with_64_attributes() {
    let mut n = 0;
    for stage in ["pk64", "q019"] {
        let Some(doc) = file(&format!("vectors/closing/r25-sa64/pds/{stage}.vec.json")) else { return };
        for v in doc.get("vectors").arr() {
            let id = v.get("id").str().unwrap();
            assert_eq!(v.get("init").get("attrs").num(), Some(64.0), "{id}");
            let got = run_pds(v);
            assert!(matches!(got, Ok(Outcome::Exact | Outcome::AnyValue)), "{id}: {got:?}");
            // the job's first attribute: 0, 16, 32 or 48 (q019-R-rN-aAA; pk64's are sets 0-15)
            let a: usize = id.rsplit("-a").next().and_then(|s| s.parse().ok()).unwrap_or(0);
            let off = format!("0x{:03x}", 4 * a);
            let bad = with(v, Some((&off, "0x00000bad")), None);
            assert!(run_pds(&bad).is_err(), "{id}: a changed marker at sa{a} must fail");
            let cut = run_pds(&with(v, None, Some(("attrs", Json::Num(16.0)))));
            if a >= 16 {
                assert!(cut.as_ref().is_err_and(|e| e.contains("past the 16")), "{id}: {cut:?}");
            }
            n += 1;
        }
    }
    assert_eq!(n, 58, "pk64's 2 and q019's 56");
}

/// E1103: the twelve fills of r25-csc replay exactly (2048 pixels each) with the colour-space set the
/// batch left (init.job.csc): E037's conversion after a BT.601 load, opaque black after a zeros load.
/// Without the batch's set (the field taken out) a fill with a load of its own stops, as before, and
/// an unpoked fill falls back on the old reading (no pokes: unloaded, black), which E1103's c and d
/// (unpoked after a BT.601 load) contradict: the control that the kept set is what matches.
#[test]
fn r25_csc_fills_replay_with_the_set_the_batch_left() {
    let Some(doc) = file("vectors/closing/r25-csc/texture/csc.vec.json") else { return };
    let vs = doc.get("vectors").arr();
    assert_eq!(vs.len(), 12);
    for v in vs {
        let id = v.get("id").str().unwrap();
        assert_eq!(run_pixels(v), Ok(Outcome::Exact), "{id}");
        let mut job = v.get("init").get("job").clone();
        if let Json::Obj(j) = &mut job {
            j.retain(|(k, _)| k != "csc");
        }
        let bare = with(v, None, Some(("job", job)));
        let r = run_pixels(&bare);
        let poked = !v.get("init").get("job").get("pokes").arr().is_empty();
        if poked {
            assert!(
                r.as_ref().is_err_and(|e| e.contains("colour-space")),
                "{id} without the batch's set: {r:?}"
            );
        } else if id.ends_with("-c") || id.ends_with("-d") {
            assert!(
                r.as_ref().is_err_and(|e| e.contains("want 0xff")),
                "{id}: the old reading is black: {r:?}"
            );
        } else {
            assert_eq!(r, Ok(Outcome::Exact), "{id}: black after a zeros load, as the old reading");
        }
    }
}
