// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The first triangle through the whole pipeline (12.3): the vertex side, the TA, the ISP, the pixel
//! programs on `sgx-sim` and the PBE, from the words the library's builder puts in its pages, against
//! the image hashes the records kept (E023, E148, E174; the fixture `first-triangle.scene.json` holds
//! the sizes of E148 that E606's envelope contains and three it does not) and, with the data
//! repository, against every scene of `scene-vectors/isp/` and the stored depth of the E606 depth
//! jobs. The image rests on the coverage rule E606 fitted, so it is reported fitted, never matched;
//! the depth is `near` within E606's tolerance; the gate is zero mismatches.

use sgx_pipe::data::{Ctx, dwords, files};
use sgx_pipe::scene::{Scene, compare, depth_verdict, fnv64};
use sgx_pipe::{Outcome, Verdict, job};
use sgx_sim::json::{Json, parse};
use std::collections::BTreeMap;

fn fixture() -> Json {
    parse(include_str!("fixtures/first-triangle.scene.json"))
}

fn scene(id: &str) -> (Scene, Json) {
    let f = fixture();
    let i = f.get("scenes").arr().iter().position(|s| s.get("id").str().unwrap().ends_with(id)).unwrap();
    let sc = Scene::load_file(&f).remove(i).unwrap();
    (sc, f.get("scenes").arr()[i].get("expect").clone())
}

fn refusal_ids(sc: &Scene) -> Vec<String> {
    let r = job::run(sc);
    match (&r.pixel_refusal, &r.outcome) {
        (Some(Outcome::Unsupported { ids, .. }), _) | (None, Outcome::Unsupported { ids, .. }) => ids.clone(),
        o => panic!("{o:?}"),
    }
}

#[test]
fn the_three_sizes_e606_ran_draw_the_recorded_image_and_are_fitted() {
    for size in ["64x64", "128x128", "256x128"] {
        let (sc, expect) = scene(size);
        let r = job::run(&sc);
        assert!(r.pixel_refusal.is_none(), "{size}: {:?}", r.pixel_refusal);
        assert_eq!(r.outside, Some(0), "{size}: the guard page stays untouched (E023: guard 0)");
        assert_eq!(
            compare(&expect, &r),
            Verdict::Fitted,
            "{size}: the coverage rule is a fit, never matched"
        );
    }
}

#[test]
fn e023s_counts_come_out_of_the_image_1062_triangle_pixels_and_3034_background() {
    let (sc, _) = scene("64x64");
    let img = job::run(&sc).image.unwrap();
    let green = img.iter().filter(|&&p| p == 0xff00_ff00).count();
    let bg = img.iter().filter(|&&p| p == 0xff20_3040).count();
    assert_eq!((green, bg, green + bg), (1062, 3034, 4096));
}

#[test]
fn sizes_outside_e606s_are_refused_by_question_and_never_given_an_image_that_could_be_wrong() {
    // the family around E606's three sizes was not run: E148 ran it with the library's triangle
    // only, which is no record of the rule there (r123 item 3)
    for size in ["64x128", "128x64", "256x64", "128x144", "128x96"] {
        let (sc, expect) = scene(size);
        let r = job::run(&sc);
        assert!(r.image.is_none());
        assert_eq!(compare(&expect, &r), Verdict::Refused(vec!["Q240".into()]), "{size}");
    }
    // four macrotiles a row: the TA's own refusal comes first (E506), and Q240 is open as well
    let (sc, expect) = scene("1024x768");
    assert_eq!(refusal_ids(&sc), ["Q139", "Q100", "Q086"]);
    assert!(matches!(compare(&expect, &job::run(&sc)), Verdict::Refused(_)));
}

#[test]
fn a_different_recorded_hash_is_a_mismatch_so_the_comparison_is_not_vacuous() {
    let (sc, _) = scene("64x64");
    let wrong = parse(r#"{"image": {"hash": "0x99385a04ee01c586"}, "outside": 0}"#);
    assert!(matches!(compare(&wrong, &job::run(&sc)), Verdict::Mismatch(_)));
    let fnv = fnv64(&job::run(&sc).image.unwrap());
    assert_eq!(fnv, 0x99385a04ee01c585, "E148's first 64 x 64 render");
}

fn poke_cmd(i: usize, v: u32) -> Vec<String> {
    let (mut sc, _) = scene("64x64");
    sc.cmd[i] = v;
    refusal_ids(&sc)
}

#[test]
fn command_words_the_library_never_changes_are_refused_by_question() {
    assert_eq!(poke_cmd(16, 0x98), ["Q202"], "ISP_MULTISAMPLECTL places the sample (E278)");
    assert_eq!(poke_cmd(10, 0x98), ["Q202"]);
    assert_eq!(poke_cmd(13, 0x8000_0001), ["Q202"]);
    assert_eq!(poke_cmd(12, 0x000f_0100 | 1 << 9), ["Q085"]);
    assert_eq!(poke_cmd(14, 0x4000_0000), ["Q066"], "a background depth of 2.0");
    assert_eq!(poke_cmd(15, 0x100), ["Q066"]);
    assert_eq!(poke_cmd(11, 0x80 | 1 << 25), ["Q231"]);
    assert_eq!(poke_cmd(18, 0x2e00_0090), ["Q206"], "the pixel-event program moved");
    assert_eq!(poke_cmd(19, 6), ["Q206"]);
}

fn poke_isp(word: usize, v: u32) -> Scene {
    let (mut sc, _) = scene("64x64");
    // the triangle's state block is at pdsv + 0x100: presence, ISP0, ISP1, ...
    let seg = sc.memory.iter_mut().find(|s| s.role == "pdsv").unwrap();
    seg.dwords.as_mut().unwrap()[0x100 / 4 + word] = v;
    sc
}

#[test]
fn isp_words_no_record_settles_are_refused_by_question() {
    for (w0, q) in [
        (0x01d0_0300u32, "Q071"),
        (0x01d0_0200 | 1 << 28, "Q202"),
        (0x01d0_0200 | 1 << 17, "Q241"),
        (2 << 22 | 0x0010_0200, "Q241"),
    ] {
        assert_eq!(refusal_ids(&poke_isp(1, w0)), [q], "{w0:#x}");
    }
    assert_eq!(refusal_ids(&poke_isp(2, 0x10f8)), ["Q241"], "a visibility test");
}

#[test]
fn the_depth_compare_and_write_bits_change_the_image_as_the_records_say() {
    // the triangle at depth 0.5 over a background at 1.0: less draws it, greater and never do not
    let hash = |w0: u32| fnv64(&job::run(&poke_isp(1, w0)).image.unwrap());
    let drawn = hash(0x01d0_0200);
    assert_eq!(hash(0x0040_0200), drawn, "less, depth written (the E606 depth jobs' word)");
    assert_eq!(hash(0x0010_0200 | 1 << 22), drawn, "less, depth write disabled");
    assert_ne!(hash(0x0100_0200), drawn, "greater: the background wins");
    let bg_only = |w0: u32| job::run(&poke_isp(1, w0)).image.unwrap().iter().all(|&p| p == 0xff20_3040);
    assert!(bg_only(0x0100_0200) && bg_only(0x0000_0200), "greater and never draw nothing at 0.5 < 1.0");
    assert!(bg_only(0x01d0_0200 | 3 << 25), "pass type 3 removes the object (E065)");
    // tagwrite disabled: depth written, no colour (E282)
    assert!(bg_only(0x0060_0200));
}

#[test]
fn the_fitted_rules_a_result_used_are_named_with_the_depth_store_only_where_depth_is_stored() {
    let (mut sc, _) = scene("64x64");
    let r = job::run(&sc);
    assert_eq!(r.fitted.iter().filter(|f| ["E606", "E607"].contains(&f.as_str())).count(), 2);
    assert!(!r.fitted.contains(&"E465".to_string()), "no depth store, no E465: {:?}", r.fitted);
    // the depth store of E465 (CR_ISP_ZLSCTL with G = 1, the store base)
    sc.regs.push((0x0480, 0x0017_1004 | 1 << 3));
    sc.regs.push((0x0488, 0x3e00_1000));
    let r = job::run(&sc);
    assert!(r.depth.is_some());
    for rule in ["E606", "E607", "E465"] {
        assert!(r.fitted.contains(&rule.to_string()), "{rule}: {:?}", r.fitted);
    }
}

fn drawn(sc: &Scene) -> bool {
    let img = job::run(sc).image.unwrap_or_else(|| panic!("{:?}", refusal_ids(sc)));
    if img.contains(&0xff00_ff00) {
        return true;
    }
    assert!(img.iter().all(|&p| p == 0xff20_3040));
    false
}

#[test]
fn a_gate_in_isp_word_1_under_cr_isp_ctl_removes_an_opaque_object_for_the_pairs_measured() {
    // E232 (gate 0, thresholds 0 to 8, 16, 32, 63) and E235 (gate 0 and 63, thresholds 1 and 63): the
    // object is drawn when ISP1 bits 31:26 reach CR_ISP_CTL bits 5:0, else removed
    for (gate, thr, want) in
        [(0, 0, true), (0, 1, false), (0, 63, false), (63, 1, true), (63, 63, true), (0, 16, false)]
    {
        let mut sc = poke_isp(2, 0x10f0 | gate << 26);
        sc.cmd[12] = 0x000f_0100 | thr;
        assert_eq!(drawn(&sc), want, "gate {gate}, threshold {thr}");
    }
}

#[test]
fn a_gate_pair_no_record_measured_is_refused_not_decided_by_the_comparison() {
    for (gate, thr) in [(2, 3), (2, 2), (3, 5), (63, 0), (63, 62), (0, 9)] {
        let mut sc = poke_isp(2, 0x10f0 | gate << 26);
        sc.cmd[12] = 0x000f_0100 | thr;
        assert_eq!(refusal_ids(&sc), ["Q241"], "gate {gate}, threshold {thr}");
    }
}

/// The library's colour write replaced by another constant: not the shader E065 ran.
fn poke_shader() -> Scene {
    let (mut sc, _) = scene("64x64");
    let seg = sc.memory.iter_mut().find(|s| s.role == "usep").unwrap();
    let d = seg.dwords.as_mut().unwrap();
    let text = |v: u64| usse_isa::decode(v, usse_isa::Core::Sgx545).text;
    let mut poked = 0;
    for i in 0..d.len() / 2 {
        if text(d[2 * i] as u64 | (d[2 * i + 1] as u64) << 32).starts_with("mov.skipinv.end o0, #0xFF00FF00")
        {
            d[2 * i] = 0x0000_fe00;
            poked += 1;
        }
    }
    assert!(poked >= 1);
    sc
}

#[test]
fn pass_types_1_2_4_5_6_draw_only_with_the_library_colour_write_and_refuse_another_shader() {
    for pass in [1u32, 2, 4, 5, 6] {
        let w0 = 0x01d0_0200 | pass << 25;
        let mut sc = poke_isp(1, w0);
        assert!(drawn(&sc), "pass {pass}: E065's shader draws as opaque");
        sc = poke_shader();
        let seg = sc.memory.iter_mut().find(|s| s.role == "pdsv").unwrap();
        seg.dwords.as_mut().unwrap()[0x100 / 4 + 1] = w0;
        assert_eq!(refusal_ids(&sc), ["Q241"], "pass {pass} with another shader");
    }
    // pass type 0 is E606's, whatever the colour the shader writes: it still draws
    assert!(job::run(&poke_shader()).image.is_some());
}

fn dir() -> Option<std::path::PathBuf> {
    let ctx = Ctx::from_env();
    let d = ctx.scenes.map(|d| d.join("isp")).filter(|d| d.is_dir());
    if d.is_none() {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no scene-vectors/isp (RESGX545_DATA)");
        eprintln!("SKIPPED: no scene-vectors/isp (set RESGX545_DATA or RESGX545_SCENE_VECTORS)");
    }
    d
}

#[test]
fn every_scene_of_the_isp_tables_is_fitted_or_refused_by_question_and_none_mismatches() {
    let Some(d) = dir() else { return };
    let ctx = Ctx::from_env();
    let mut counts: BTreeMap<String, u64> = BTreeMap::new();
    for f in files(&d, ".scene.json") {
        let doc = parse(&std::fs::read_to_string(&f).unwrap());
        for (sc, j) in Scene::load_file(&doc).into_iter().zip(doc.get("scenes").arr()) {
            let sc = sc.unwrap();
            let r = job::run(&sc);
            let mut v = compare(j.get("expect"), &r);
            // a fitted image whose depth is only `near` is counted apart: the combined verdict is
            // Fitted either way, and the tolerance must stay visible in the per-scene result
            let mut near = false;
            if let Some(dep) = j.get("provenance").get("depth").get("file").str() {
                let refuse: Vec<String> = j
                    .get("expect")
                    .get("refuse")
                    .arr()
                    .iter()
                    .filter_map(|s| s.str().map(String::from))
                    .collect();
                if r.pixel_refusal.is_none() && !matches!(v, Verdict::Refused(_)) {
                    let dump = dwords(&ctx.read_gz(dep, "").unwrap());
                    let dv = depth_verdict(&r, &dump, &refuse);
                    assert!(!matches!(dv, Verdict::Mismatch(_)), "{}: {dv:?}", sc.id);
                    *counts.entry(format!("depth {dv:?}")).or_default() += 1;
                    near = matches!(dv, Verdict::Near);
                    v = v.combine(dv);
                }
            }
            let key = match &v {
                Verdict::Mismatch(m) => panic!("MISMATCH {}: {m}", sc.id),
                Verdict::Refused(ids) => format!("refused {}", ids.join("+")),
                Verdict::Fitted if near => "Fitted (depth near)".to_string(),
                v => format!("{v:?}"),
            };
            *counts.entry(key).or_default() += 1;
        }
    }
    eprintln!("{counts:?}");
    let fitted =
        counts.get("Fitted").copied().unwrap_or(0) + counts.get("Fitted (depth near)").copied().unwrap_or(0);
    assert!(fitted >= 6, "{counts:?}");
    let near = counts.get("depth Near").copied().unwrap_or(0);
    assert_eq!(
        near,
        counts.get("Fitted (depth near)").copied().unwrap_or(0),
        "every near depth is seen per scene"
    );
    assert!(!counts.contains_key("Matched"), "the image rests on a fitted rule");
    assert!(!counts.keys().any(|k| k.starts_with("Unsupported")), "{counts:?}");
}

#[test]
fn a_pixel_shader_that_writes_without_skipinv_is_refused_where_the_triangle_covers_a_quad_in_part() {
    // E104, E111, E113: the plain write also runs for helper instances and lands in some runs only
    let (mut sc, _) = scene("64x64");
    let seg = sc.memory.iter_mut().find(|s| s.role == "usep").unwrap();
    let d = seg.dwords.as_mut().unwrap();
    let text = |v: u64| usse_isa::decode(v, usse_isa::Core::Sgx545).text;
    let mut poked = 0;
    for i in 0..d.len() / 2 {
        let w = d[2 * i] as u64 | (d[2 * i + 1] as u64) << 32;
        // the triangle's colour write (the probe's green program), wherever the builder put it
        if text(w).starts_with("mov.skipinv.end o0, #0xFF00FF00") {
            let plain =
                (0..64).map(|b| w ^ 1 << b).find(|&v| text(v) == text(w).replace(".skipinv", "")).unwrap();
            d[2 * i] = plain as u32;
            d[2 * i + 1] = (plain >> 32) as u32;
            poked += 1;
        }
    }
    assert!(poked >= 1);
    assert_eq!(refusal_ids(&sc), ["Q052"]);
}
