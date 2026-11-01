// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The triangle-host vectors of the data repository, rebuilt as render scenes by
//! `tools/usse-asm/isp_scenes.py inventory`, run through the whole pipeline and judged against the
//! image each vector recorded. A refusal the vector did not declare (the census declares none) is
//! counted by the questions the model names; a mismatch is listed in full.
//!
//!     RESGX545_SCENE_VECTORS=DIR cargo run --release -p sgx-pipe --example inventory_stats [-- -v]

use sgx_pipe::data::{Ctx, files};
use sgx_pipe::scene::{Scene, compare};
use sgx_pipe::{Outcome, Verdict, job};
use sgx_sim::json::parse;
use std::collections::BTreeMap;

fn main() {
    let verbose = std::env::args().any(|a| a == "-v");
    let dir = Ctx::from_env().scenes.expect("no scene vectors");
    let mut by: BTreeMap<String, u64> = BTreeMap::new();
    let mut why: BTreeMap<String, u64> = BTreeMap::new();
    let mut total = 0;
    let mut fam: BTreeMap<String, BTreeMap<String, u64>> = BTreeMap::new();
    for f in files(&dir, ".scene.json") {
        let doc = parse(&std::fs::read_to_string(&f).unwrap());
        for (sc, j) in Scene::load_file(&doc).into_iter().zip(doc.get("scenes").arr()) {
            let sc = sc.unwrap();
            total += 1;
            let r = job::run(&sc);
            let v = compare(j.get("expect"), &r);
            let refusal = match (&r.pixel_refusal, &r.outcome) {
                (Some(o @ Outcome::Unsupported { .. }), Outcome::Ok)
                | (None, o @ Outcome::Unsupported { .. }) => Some(o),
                _ => None,
            };
            let key = match (&v, refusal) {
                (Verdict::Mismatch(m), _) => {
                    println!("MISMATCH {}: {}", sc.id, m.chars().take(300).collect::<String>());
                    "mismatch".to_string()
                }
                (Verdict::Unsupported(_), Some(Outcome::Unsupported { ids, why: w })) => {
                    *why.entry(format!("{} | {}", ids.join("+"), w.chars().take(110).collect::<String>()))
                        .or_default() += 1;
                    if verbose {
                        println!("refused {} {}: {w}", sc.id, ids.join("+"));
                    }
                    format!("refused {}", ids.join("+"))
                }
                (v, _) => {
                    if verbose {
                        println!("{v:?} {}", sc.id);
                    }
                    format!("{v:?}")
                }
            };
            let family = sc.id.split('/').skip(1).take(2).collect::<Vec<_>>().join("/");
            let short = key.split_whitespace().take(2).collect::<Vec<_>>().join(" ");
            *fam.entry(family).or_default().entry(short).or_default() += 1;
            *by.entry(key).or_default() += 1;
        }
    }
    println!("scenes: {total}");
    for (k, n) in &by {
        println!("  {n:>5} {k}");
    }
    println!("by family:");
    for (f, m) in &fam {
        println!("  {f:<40} {m:?}");
    }
    println!("by reason:");
    let mut w: Vec<_> = why.into_iter().collect();
    w.sort_by_key(|x| std::cmp::Reverse(x.1));
    for (k, n) in w.iter().take(60) {
        println!("  {n:>5} {k}");
    }
}
