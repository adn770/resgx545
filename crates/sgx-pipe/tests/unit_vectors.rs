// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The unit models against the hardware: every unit vector of the data repository's
//! `unit-vectors/` (doc/specs/vectors.md section 5; `$RESGX545_DATA`, or `$RESGX545_UNIT_VECTORS`
//! for a set not yet landed). Skips, saying so, without them; with `RESGX545_REQUIRE_DATA`
//! set (the release gate) it fails instead. The gate is zero mismatches (D5): refusals are
//! counted by question, fitted results apart, predicted hangs as matches.

use sgx_pipe::data::{Ctx, files};
use sgx_pipe::report::Report;
use sgx_pipe::unitvec::replay;
use sgx_sim::json::parse;

fn replay_all() -> Option<Report> {
    let ctx = Ctx::from_env();
    let Some(dir) = ctx.units.clone() else {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no unit-vectors (RESGX545_DATA)");
        eprintln!("SKIPPED: no unit-vectors (set RESGX545_DATA or RESGX545_UNIT_VECTORS)");
        return None;
    };
    let mut rep = Report::default();
    for f in files(&dir, ".vec.json") {
        let d = parse(&std::fs::read_to_string(&f).unwrap());
        assert_eq!(d.get("format").str(), Some("sgx545-vectors"), "{}", f.display());
        for v in d.get("vectors").arr() {
            match replay(v, &ctx) {
                Ok(r) => rep.add(&r),
                Err(e) => rep.skip(v.get("id").str().unwrap_or("?"), &e),
            }
        }
    }
    Some(rep)
}

#[test]
fn unit_vectors_replay_with_no_mismatch() {
    let Some(rep) = replay_all() else { return };
    eprintln!("{}", rep.render());
    for (id, why) in &rep.mismatches {
        eprintln!("MISMATCH {id}: {why}");
    }
    for (id, why) in &rep.skipped {
        eprintln!("SKIPPED {id}: {why}");
    }
    assert!(rep.gate(), "{} mismatches", rep.mismatches.len());
    assert!(rep.skipped.is_empty(), "vectors that could not be replayed: {:?}", rep.skipped);
}

/// D6: the four rules of 12.0 are fitted as their records state, so none of their vectors is
/// reported matched; a hang the record states is predicted.
#[test]
fn fitted_rules_are_never_reported_matched() {
    let Some(rep) = replay_all() else { return };
    for unit in ["zls", "ta", "isp"] {
        let c = &rep.units[unit];
        assert_eq!(c.matched, 0, "{unit}: a fitted rule reported matched");
        assert!(c.fitted > 0, "{unit}");
    }
    let ta = &rep.units["ta"];
    assert_eq!((ta.hang, ta.fault), (0, 0), "no hang or fault is predicted: E541's three are recalled");
    assert_eq!(ta.refused["Q165"], 3);
}

#[test]
fn the_counts_of_the_records_hold() {
    let Some(rep) = replay_all() else { return };
    // E489 (18 cases), E542 (35 jobs) and E541 (56 completed + 3 failed), E503 (48 runs)
    assert_eq!(rep.units["zls"].fitted, 18);
    assert_eq!(rep.units["ta"].fitted, 35 + 56);
    assert_eq!(rep.units["isp"].fitted, 48);
    // D6: every item rests on a fitted rule, so none is "matched"
    for u in ["zls", "ta", "isp"] {
        assert_eq!(rep.items_matched.get(u).copied().unwrap_or(0), 0, "{u}");
    }
    assert_eq!(
        rep.items_fitted["zls"], 3_225_000,
        "3279132 at the rule, less 54132 for pixels past the target"
    );
    assert_eq!(rep.items_refused["zls"]["Q107"], 128_640 + 6_656);
    assert_eq!(rep.items_refused["zls"]["Q122"], 54_132 + 1_124);
    assert_eq!(rep.items_fitted["isp"], 773);
    assert_eq!(rep.items_refused["isp"]["Q141"], 13);
    // 14656 (primitive, tile) pairs of E542 and 56 of E541's jobs
    assert_eq!(rep.items_fitted["ta"], 14_656 + 56);
}
