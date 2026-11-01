// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! Print what the model gives for one scene of a scene-vector directory: the outcome, the pixel
//! side's refusal and the image as value counts and its first rows.
//!
//!     RESGX545_SCENE_VECTORS=DIR cargo run --release -p sgx-pipe --example scene_image -- ID-SUFFIX

use sgx_pipe::data::{Ctx, files};
use sgx_pipe::job;
use sgx_pipe::scene::{Scene, fnv64};
use sgx_sim::json::parse;
use std::collections::BTreeMap;

fn main() {
    let want = std::env::args().nth(1).expect("a scene id suffix");
    let dir = Ctx::from_env().scenes.expect("no scene vectors");
    for f in files(&dir, ".scene.json") {
        let doc = parse(&std::fs::read_to_string(&f).unwrap());
        for sc in Scene::load_file(&doc).into_iter().flatten() {
            if !sc.id.ends_with(&want) {
                continue;
            }
            let r = job::run(&sc);
            println!("{}: outcome {:?}\npixel refusal {:?}", sc.id, r.outcome, r.pixel_refusal);
            if std::env::args().any(|a| a == "--code")
                && let Some(seg) = sc.memory.iter().find(|m| m.role == "usep")
            {
                let d = seg.dwords.as_ref().unwrap();
                for (i, w) in d.chunks(2).enumerate().take(80) {
                    let v = w[0] as u64 | (w.get(1).copied().unwrap_or(0) as u64) << 32;
                    if v != 0 {
                        println!("  {:#05x} {}", i, usse_isa::decode(v, usse_isa::Core::Sgx545).text);
                    }
                }
            }
            if let Some(img) = &r.image {
                let mut h: BTreeMap<u32, u32> = BTreeMap::new();
                for &p in img {
                    *h.entry(p).or_default() += 1;
                }
                println!("hash {:#x} mixed {:x?}", fnv64(img), h);
                for y in 0..(sc.target.h.min(8)) {
                    let row: Vec<String> = (0..sc.target.w.min(16))
                        .map(|x| format!("{:08x}", img[(y * sc.target.w + x) as usize]))
                        .collect();
                    println!("row {y}: {}", row.join(" "));
                }
            }
            println!(
                "expect {:?}",
                doc.get("scenes")
                    .arr()
                    .iter()
                    .find(|s| s.get("id").str() == Some(sc.id.as_str()))
                    .map(|s| s.get("expect").clone())
            );
        }
    }
}
