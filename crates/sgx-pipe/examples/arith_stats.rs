// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The ISP model against the recorded images of E606 and E607 (isp/arith-1138): coverage of the
//! colour image and the stored depth of every depth job, per set and class; the refusals by
//! question; every mismatch. Reads `$RESGX545_DATA`.
//!
//!     cargo run --release -p sgx-pipe --example arith_stats

use sgx_pipe::arith::*;
use sgx_pipe::data::{Ctx, dwords};
use sgx_pipe::{Outcome, isp};
use std::collections::BTreeMap;

fn main() {
    let ctx = Ctx::from_env();
    let root = ctx.root.expect("no data repository");
    let base = root.join("isp/arith-1138");
    let mut grand: BTreeMap<String, u64> = BTreeMap::new();
    let mut verdicts: BTreeMap<String, u64> = BTreeMap::new();
    let mut grand_it: BTreeMap<String, [u64; 5]> = BTreeMap::new();
    for (cases, dir) in [("cases.tsv", "main"), ("cases-fine.tsv", "fine"), ("cases-fine2.tsv", "fine2")] {
        let text = std::fs::read_to_string(base.join(cases)).unwrap();
        let mut by: BTreeMap<String, [u64; 9]> = BTreeMap::new();
        for c in parse_cases(&text) {
            if !c.jobs.contains('D') {
                continue;
            }
            let key = format!("{dir}/{}/{}", c.set, c.class);
            let e = by.entry(key).or_default();
            let t = match tri_of(&c) {
                Ok(t) => t,
                Err(Outcome::Unsupported { ids, .. }) => {
                    *grand.entry(format!("refused {}", ids.join("+"))).or_default() += 1;
                    e[0] += 1;
                    continue;
                }
                Err(o) => panic!("{o:?}"),
            };
            let txt = std::fs::read(base.join(dir).join("D").join(format!("{}.txt.gz", c.id)));
            let dep = std::fs::read(base.join(dir).join("D").join(format!("{}.depth.gz", c.id)));
            let (Ok(txt), Ok(dep)) = (txt, dep) else {
                e[1] += 1;
                continue;
            };
            let txt = String::from_utf8_lossy(&sgx_pipe::gz::gunzip(&txt).unwrap()).to_string();
            let img = parse_image(&txt, c.w, c.h).expect("image rows");
            let raw = dwords(&sgx_pipe::gz::gunzip(&dep).unwrap());
            let d = depth_image(&raw, c.w, c.h, pitch_g(c.w)).expect("depth dump");
            let r = check_case(&t, &c, &img, &d);
            e[2] += 1;
            let covered = r.depth_checked + r.depth_refused;
            let dv = if covered == 0 {
                "depth matched (nothing covered: the background 1.0 exactly)"
            } else if t.gradient() < isp::DEPTH_GRADIENT_LIMIT {
                "depth near"
            } else {
                "depth refused Q200"
            };
            *verdicts.entry(format!("{dir}: image fitted, {dv}")).or_default() += 1;
            e[3] += r.pixels;
            e[4] += r.colour_wrong;
            e[5] += r.depth_checked;
            e[6] += r.depth_within;
            e[7] += r.depth_refused;
            e[8] += r.background_wrong;
            if c.jobs.contains('I') && dir == "main" {
                for k in 0..2u32 {
                    let p = base.join(dir).join(format!("I{k}")).join(format!("{}.txt.gz", c.id));
                    let Ok(b) = std::fs::read(p) else { continue };
                    let txt = String::from_utf8_lossy(&sgx_pipe::gz::gunzip(&b).unwrap()).to_string();
                    let img = parse_image(&txt, c.w, c.h).expect("iteration image rows");
                    let r = check_iteration(&t, &c, k, &img);
                    let g = grand_it.entry(format!("{dir}/{}/pa{k}", c.set)).or_default();
                    g[0] += 1;
                    g[1] += r.coverage_wrong;
                    g[2] += r.checked;
                    g[3] += r.within;
                    g[4] += r.refused;
                    if r.coverage_wrong > 0 || r.within < r.checked {
                        println!(
                            "ITER {} pa{k} {} {}: coverage-wrong {} out-of-tolerance {} max {:.1}",
                            c.id,
                            c.class,
                            c.set,
                            r.coverage_wrong,
                            r.checked - r.within,
                            r.max_units
                        );
                    }
                }
            }
            if r.colour_wrong > 0 || r.background_wrong > 0 {
                println!(
                    "MISMATCH {dir} {} {} {}: colour {} background {}",
                    c.id, c.class, c.set, r.colour_wrong, r.background_wrong
                );
            }
            if t.gradient() < isp::DEPTH_GRADIENT_LIMIT && r.depth_within < r.depth_checked {
                println!(
                    "DEPTH {dir} {} {}: {} of {} within, max {:.2}",
                    c.id,
                    c.class,
                    r.depth_checked - r.depth_within,
                    r.depth_checked,
                    r.depth_max_units
                );
            }
        }
        println!(
            "{dir}: refused/nodata/cases/pixels/colour-wrong/depth-checked/within/depth-refused/bg-wrong"
        );
        for (k, e) in &by {
            println!("  {k:<28} {e:?}");
        }
    }
    println!("{grand:?}");
    for (k, n) in &verdicts {
        println!("  {n:>5} {k}");
    }
    println!("iteration (images, coverage-wrong, checked, within, refused): {grand_it:?}");
}
