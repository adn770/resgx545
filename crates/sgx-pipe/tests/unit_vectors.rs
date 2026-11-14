// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The unit models against the hardware: every unit vector of the data repository's
//! `unit-vectors/` (doc/specs/vectors.md section 5; `$RESGX545_DATA`, or `$RESGX545_UNIT_VECTORS`
//! for a set not yet landed). Skips, saying so, without them; with `RESGX545_REQUIRE_DATA`
//! set (the release gate) it fails instead. The gate is zero mismatches (D5): refusals are
//! counted by question, fitted results apart, predicted hangs as matches. The model records these
//! replays hold: E615 (zls::store_dword over E489's 18 cases), E616 (ta::tile_lists, E542's 35
//! jobs), E617 (ta::object_layout, E541's 59 jobs), E618 (isp::msaa_source, E503's 48 runs),
//! E664 (the zls load and pass, E467's 30 cases) and E665 (the zls control word, 47 vectors).

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
    for unit in ["ta", "isp"] {
        let c = &rep.units[unit];
        assert_eq!(c.matched, 0, "{unit}: a fitted rule reported matched");
        assert!(c.fitted > 0, "{unit}");
    }
    // zls (12.4): the control words that read as the records state with no address, format or
    // inferred load match (15); the two empty stores compare nothing and are counted empty, not
    // matched; every vector that stores through E465 is fitted (tests/zls_vectors.rs)
    let z = &rep.units["zls"];
    assert_eq!((z.matched, z.empty, z.fitted), (15, 2, 18 + 6 + 30 + 24));
    let ta = &rep.units["ta"];
    assert_eq!((ta.hang, ta.fault), (0, 0), "no hang or fault is predicted: E541's three are recalled");
    assert_eq!(ta.refused["Q165"], 3);
}

/// E031, E268: pack modes 0 to 3 store the two colours of the triangle jobs as the dumps show
/// (4 modes, 2 colours) and mode 0 the ten shader colours unchanged; E383, E999: modes 7, 8, 15,
/// 18, 20, 24, 25, 27 and 28 store the channels their field picks, and each dword of E031's
/// histogram is made of the two colours' packed values (9 modes, 23 dword values; every pixel in
/// tests/pbe_pack_images.rs); the other 51 modes refuse. Measured rules: nothing here is fitted.
#[test]
fn the_pack_modes_of_e031_replay_matched_and_the_rest_are_refused_by_question() {
    let Some(rep) = replay_all() else { return };
    let Some(c) = rep.units.get("pbe") else {
        // the pack-mode vectors are not landed in this data revision
        eprintln!("SKIPPED: no pbe vectors in the set");
        return;
    };
    assert_eq!((c.matched, c.fitted, c.mismatch), (14 + 9, 0, 0));
    assert_eq!(rep.items_matched["pbe"], 4 * 2 + 10 + 23);
    assert_eq!((c.refused["Q012"], c.refused["Q044"]), (2, 49));
    assert_eq!(c.refused_vectors, 51);
}

#[test]
fn the_counts_of_the_records_hold() {
    let Some(rep) = replay_all() else { return };
    // E489 (18 cases), E542 (35 jobs) and E541 (56 completed + 3 failed), E503 (48 runs)
    // 18 layouts, 6 format buffers (f0, f1, f2, b19_0 to b19_2) and 30 loads (12.4)
    // the control words: 24 fitted since E977 admits the 16-bit format at G = 1 (flip-25)
    assert_eq!(rep.units["zls"].fitted, 18 + 6 + 30 + 24);
    assert_eq!(rep.units["ta"].fitted, 35 + 56);
    assert_eq!(rep.units["isp"].fitted, 48);
    // D6: every item rests on a fitted rule, so none is "matched"
    for u in ["ta", "isp"] {
        assert_eq!(rep.items_matched.get(u).copied().unwrap_or(0), 0, "{u}");
    }
    // 3279132 at the rule and 1124 of background past the band (E831); the format buffers' 7864320
    // dwords and the loads' 983040 (8 x 40960 + 20 x 32768)
    // and the 24 fitted control vectors' items: E411's stored pages in dwords and the fields read
    // (103709, counted by the replay, checked by hand for flip 3: 3200 + 6; and 3072 of flip 25,
    // the 16-bit format at G = 1, admitted since E977)
    assert_eq!(rep.items_fitted["zls"], 3_225_000 + 54_132 + 1_124 + 7_864_320 + 983_040 + 103_709 + 3_072);
    assert_eq!(rep.items_refused["zls"]["Q107"], 128_640 + 6_656);
    // E411's seven faulted flips are predicted faults at their pages (E1070); format 4 refuses
    assert_eq!((rep.units["zls"].fault, rep.units["zls"].refused["Q120"]), (7, 3 + 1));
    assert_eq!(rep.items_refused["zls"].len(), 1, "Q107's tiles only: E489's cases are even sizes");
    assert_eq!(rep.items_fitted["isp"], 773);
    assert_eq!(rep.items_refused["isp"]["Q141"], 13);
    // 14656 (primitive, tile) pairs of E542 and 56 of E541's jobs
    assert_eq!(rep.items_fitted["ta"], 14_656 + 56);
}
