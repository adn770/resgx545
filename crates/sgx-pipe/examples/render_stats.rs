// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! Count what the vertex side and the TA do with every render scene of a scene-vector directory:
//! per file the verdicts, the refusals by question with the reason, the mismatches with the first
//! differing words, how many distinct expected buffers there are (a baseline is not evidence: per
//! file and over all the files, where a set one file repeats from another counts once), the
//! dwords compared and the dwords of the dumps the model does not cover.
//!
//!     RESGX545_SCENE_VECTORS=DIR cargo run --release -p sgx-pipe --example render_stats

use sgx_pipe::data::{Ctx, files};
use sgx_pipe::scene::{Kind, Scene, compare};
use sgx_pipe::{Outcome, Verdict, job};
use sgx_sim::json::parse;
use std::collections::{BTreeMap, BTreeSet};

fn main() {
    let ctx = Ctx::from_env();
    let dir = ctx.scenes.expect("no scene-vectors");
    let mut total: BTreeMap<String, u64> = BTreeMap::new();
    let mut all_distinct = BTreeSet::new();
    for f in files(&dir, ".scene.json") {
        let d = parse(&std::fs::read_to_string(&f).unwrap());
        let name = f.strip_prefix(&dir).unwrap().to_string_lossy().replace(".scene.json", "");
        let (mut by, mut distinct, mut items, mut outside) =
            (BTreeMap::<String, u64>::new(), BTreeSet::new(), 0u64, 0u64);
        let mut sets: BTreeMap<String, BTreeMap<String, u64>> = BTreeMap::new();
        for (sc, j) in Scene::load_file(&d).into_iter().zip(d.get("scenes").arr()) {
            let sc = sc.unwrap();
            if sc.kind != Kind::Render {
                continue;
            }
            let r = job::run(&sc);
            let v = compare(j.get("expect"), &r);
            let key = match (&r.outcome, &v) {
                (Outcome::Unsupported { ids, why }, _) => {
                    println!(
                        "  refused {} {}: {}",
                        sc.id,
                        ids.join("+"),
                        why.chars().take(150).collect::<String>()
                    );
                    format!("refused {}", ids.join("+"))
                }
                (_, Verdict::Mismatch(m)) => {
                    println!("  MISMATCH {}: {}", sc.id, m.chars().take(200).collect::<String>());
                    "mismatch".to_string()
                }
                (_, v) => format!("{v:?}"),
            };
            if matches!(v, Verdict::Fitted | Verdict::Matched) {
                let e = j.get("expect").get("buffers");
                let mut sig = String::new();
                for (nm, b) in e.obj() {
                    for (a, x) in b.get("sparse").obj() {
                        sig.push_str(&format!("{nm}{a}={}", x.str().unwrap_or("")));
                        items += 1;
                    }
                }
                distinct.insert(sig.clone());
                all_distinct.insert(sig);
                let o = j.get("provenance").get("outside_window_nonzero");
                outside +=
                    (o.get("param").num().unwrap_or(0.0) + o.get("tadata").num().unwrap_or(0.0)) as u64;
                let set = j.get("provenance").get("set").str().unwrap_or("").to_string();
                *sets.entry(set).or_default().entry(key.clone()).or_default() += 1;
            }
            *by.entry(key.clone()).or_default() += 1;
            *total.entry(key).or_default() += 1;
        }
        println!("{name}: {by:?}");
        println!(
            "    {} distinct expected buffer sets among the fitted/matched; {items} non-zero dwords compared; {outside} dump dwords outside the windows not modelled (the DPM state and the like, 12.7)",
            distinct.len()
        );
        println!("    by the table's own set (fit / heldout of E542): {sets:?}");
    }
    println!("TOTAL {total:?}");
    println!("{} distinct expected buffer sets over all the files", all_distinct.len());
}
