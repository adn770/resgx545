// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! Count what the model does with every scene of a scene-vector directory, per file: the verdict
//! with the vectors' own `refuse` lists, and, for the scenes the model refuses, the questions it
//! names and what the hardware recorded (image, hang, fault); the figures E620 states:
//!
//! - the scenes by kind of job (fill, copy) and unpoked or poked;
//! - the matched scenes by population (unpoked baselines, poked and model-inert, poked and
//!   model-live: `sgx_pipe::xfer::population`) and by the recorded result (baseline image, an
//!   image the poke changed);
//! - the images the pokes changed: scenes, distinct images and the scenes of the largest ones;
//! - the refusals by question and by poked space, against the hardware's recorded outcome (the
//!   model never reads it).
//!
//!     RESGX545_SCENE_VECTORS=DIR cargo run --release -p sgx-pipe --example scene_stats

use sgx_pipe::data::{Ctx, files};
use sgx_pipe::job;
use sgx_pipe::scene::{Scene, compare, fnv64};
use sgx_pipe::xfer::population::{Population, Word, base_of, classify};
use sgx_pipe::{Outcome, Verdict};
use sgx_sim::json::parse;
use std::collections::{BTreeMap, HashMap};

type Count = BTreeMap<String, u64>;

fn bump(m: &mut Count, k: impl Into<String>) {
    *m.entry(k.into()).or_default() += 1;
}

fn main() {
    let ctx = Ctx::from_env();
    let dir = ctx.scenes.expect("no scene-vectors");
    let mut by_file: BTreeMap<String, Count> = BTreeMap::new();
    let mut total = Count::new();
    let mut spaces: BTreeMap<String, Count> = BTreeMap::new();
    let mut kinds = Count::new();
    let mut matched = Count::new();
    // a changed image: its hash -> the (file, scenes) it came from
    let mut changed: BTreeMap<String, BTreeMap<String, u64>> = BTreeMap::new();
    let mut changed_spaces = Count::new();
    let mut changed_words = Count::new();
    let mut inert_spaces = Count::new();
    for f in files(&dir, ".scene.json") {
        let d = parse(&std::fs::read_to_string(&f).unwrap());
        let name = f.strip_prefix(&dir).unwrap().to_string_lossy().replace(".scene.json", "");
        // per base of this file: the unpoked scene, its result and the words probed so far
        let mut bases: HashMap<usize, (Scene, sgx_pipe::scene::SceneResult, HashMap<Word, bool>)> =
            HashMap::new();
        for (sc, j) in Scene::load_file(&d).into_iter().zip(d.get("scenes").arr()) {
            let sc = sc.unwrap();
            let r = job::run(&sc);
            let rec = match j.get("expect").get("outcome").str() {
                Some(o) => o.to_string(),
                None => "image".to_string(),
            };
            let pokes: Vec<&str> =
                j.get("provenance").get("poke").arr().iter().filter_map(|p| p.str()).collect();
            let bi = j.get("base").num().map(|b| b as usize).unwrap_or(usize::MAX);
            let kind = d.get("bases").arr().get(bi).and_then(|b| b.get("kind").str()).unwrap_or("full");
            bump(&mut kinds, format!("{kind} {}", if pokes.is_empty() { "unpoked" } else { "poked" }));
            let key = match &r.outcome {
                Outcome::Unsupported { ids, .. } => format!("refused {} vs {rec}", ids.join("+")),
                _ => match compare(j.get("expect"), &r) {
                    Verdict::Matched => {
                        let (base, base_r, cache) = bases.entry(bi).or_insert_with(|| {
                            let b = base_of(&d, j).expect("a scene of a base");
                            let br = job::run(&b);
                            (b, br, HashMap::new())
                        });
                        let pop = classify(base, base_r, &sc, cache);
                        bump(
                            &mut matched,
                            match pop {
                                Population::Unpoked if pokes.is_empty() => "unpoked baseline",
                                Population::Unpoked => "poke leaves every word as built",
                                Population::ModelInert => "poked, model-inert",
                                Population::ModelLive => "poked, model-live",
                            },
                        );
                        if pop == Population::ModelInert {
                            let sp: Vec<&str> = pokes
                                .iter()
                                .map(|p| {
                                    let n = if p.starts_with("pds") { 2 } else { 1 };
                                    let end = p.match_indices(':').nth(n - 1).map_or(p.len(), |(i, _)| i);
                                    &p[..end]
                                })
                                .collect();
                            bump(&mut inert_spaces, sp.join("+"));
                        }
                        let h = fnv64(r.image.as_deref().unwrap_or(&[]));
                        if base_r.image.as_deref().map(fnv64) == Some(h) {
                            "matched (the baseline's image)".to_string()
                        } else {
                            *changed
                                .entry(format!("{h:#018x}"))
                                .or_default()
                                .entry(name.clone())
                                .or_default() += 1;
                            for p in &pokes {
                                let sp = p
                                    .split(':')
                                    .take(if p.starts_with("pds") { 2 } else { 1 })
                                    .collect::<Vec<_>>();
                                bump(&mut changed_spaces, sp.join(":"));
                                let word = p.split(['^', '=', '|', '&', '+']).next().unwrap_or(p);
                                bump(&mut changed_words, word);
                            }
                            "matched (an image the poke changed)".to_string()
                        }
                    }
                    v => format!("{v:?}").chars().take(60).collect(),
                },
            };
            let space = pokes
                .iter()
                .map(|p| {
                    p.split(':').take(if p.starts_with("pds") { 2 } else { 1 }).collect::<Vec<_>>().join(":")
                })
                .collect::<Vec<_>>()
                .join("+");
            if let Outcome::Unsupported { ids, .. } = &r.outcome {
                bump(spaces.entry(space).or_default(), ids.join("+"));
            }
            bump(by_file.entry(name.clone()).or_default(), key.clone());
            bump(&mut total, key);
        }
    }
    for (f, m) in &by_file {
        println!("{f}");
        for (k, n) in m {
            println!("    {n:>5} {k}");
        }
    }
    println!("REFUSED BY POKED SPACE");
    for (sp, m) in &spaces {
        println!("  {sp}: {m:?}");
    }
    println!("SCENES BY KIND");
    for (k, n) in &kinds {
        println!("    {n:>5} {k}");
    }
    println!("MATCHED BY POPULATION (the model alone, 34 probe values a poked word)");
    for (k, n) in &matched {
        println!("    {n:>5} {k}");
    }
    println!("  of which model-inert, by poked space:");
    for (k, n) in &inert_spaces {
        println!("    {n:>5} {k}");
    }
    let scenes: u64 = changed.values().flat_map(|m| m.values()).sum();
    println!("IMAGES THE POKES CHANGED: {scenes} scenes, {} distinct images", changed.len());
    let mut groups: Vec<(u64, &String, String)> = changed
        .iter()
        .map(|(h, m)| (m.values().sum(), h, m.keys().cloned().collect::<Vec<_>>().join(", ")))
        .collect();
    groups.sort_by(|a, b| b.cmp(a));
    for (n, h, files) in groups.iter().take(5) {
        println!("    {n:>5} scenes of {h} ({files})");
    }
    println!("  by poked space (pokes, a scene with several counts in each):");
    for (k, n) in &changed_spaces {
        println!("    {n:>5} {k}");
    }
    println!("  by poked word (the address words among them corroborate the builder's addresses):");
    for (k, n) in &changed_words {
        println!("    {n:>5} {k}");
    }
    println!("TOTAL");
    for (k, n) in &total {
        println!("    {n:>5} {k}");
    }
}
