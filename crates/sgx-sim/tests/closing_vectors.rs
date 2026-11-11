// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The loop proofs of the closing pass (round 4, sim item 4b): the pixel loops of R3-pixel's q-f0, q-f1a, q-f1b and
//! q-t jobs (`vectors/closing/r3-pixel/loops/`, `tools/usse-asm/closing_vectors.py`). Each program proves itself: it
//! leaves MARK = 0xC0DE0000 | N in o0 where its counter reached zero (0 for E431's `ba` loop), and the hardware read
//! that value in every pixel the job drew (`readback.proof`). The simulator runs the program as one instance, from the
//! code index of its host (0 in a fill, 0x20 in a `--tri pixel` slot), and must leave the same o0; the files of
//! timings (`timings/`) are measurements the simulator has no clock for and are only checked to be there.
//!
//! The vectors are in the data repository (`$RESGX545_DATA`, or `$SGX_SIM_OVERLAY` while only in a working copy: a
//! `vectors/` directory laid out as the data repository's); without them the tests do nothing and say so
//! ("SKIPPED"), and with `RESGX545_REQUIRE_DATA` set they fail instead. A vector the simulator stops on as
//! unsupported is counted and named, never counted as a pass.

use sgx_sim::json::{Json, parse};
use sgx_sim::vectors::{SCRATCH_BASE, SCRATCH_DWORDS, data, patch_scratch};
use sgx_sim::{Error, Machine, Memory, Program, run_quad};
use std::path::PathBuf;
use usse_isa::Core;

const STEPS: usize = 2_000_000;
/// Why the vertex loops are refused today (the vector files are kept; the replay says so instead of passing).
const REFUSED: &str = "phas wait vcull in a pixel task hangs the job (E121)";
const STAGES: [(&str, usize); 4] = [("q-f0", 10), ("q-f1a", 54), ("q-f1b", 54), ("q-t", 86)];
const TIMINGS: [(&str, usize); 5] = [("q-f0", 10), ("q-f1a", 54), ("q-f1b", 54), ("q-t", 93), ("q-v", 74)];

fn dir() -> Option<PathBuf> {
    let overlay = std::env::var_os("SGX_SIM_OVERLAY").map(|p| PathBuf::from(p).join("vectors"));
    let d = overlay.into_iter().chain(data()).map(|v| v.join("closing/r3-pixel")).find(|d| d.is_dir());
    if d.is_none() {
        let msg = "no vectors/closing/r3-pixel (set RESGX545_DATA or SGX_SIM_OVERLAY)";
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "{msg}");
        eprintln!("SKIPPED: {msg}");
    }
    d
}

fn file(d: &std::path::Path, rel: &str) -> Json {
    parse(&std::fs::read_to_string(d.join(rel)).unwrap_or_else(|e| panic!("{rel}: {e}")))
}

/// What the simulator leaves in o0 for one instance of the vector's program, or why not.
fn run(v: &Json) -> Result<u32, String> {
    let words: Vec<u64> =
        v.get("program").get("words").arr().iter().map(|w| patch_scratch(w.hex().unwrap())).collect();
    let prog = Program::new(&words, Core::Sgx545);
    let init = v.get("init");
    let mut mem =
        Memory { base: SCRATCH_BASE, words: (0..SCRATCH_DWORDS as u32).map(|i| 0xD000_0000 | i).collect() };
    let mut m = Machine {
        temps: init.get("temps").num().map_or(124, |t| t as usize),
        code_index: init.get("code_index").num().unwrap_or(0.0) as u32,
        uniform: true,
        ..Machine::default()
    };
    match m.run(&prog, &mut mem, STEPS) {
        Ok(()) => Ok(m.o[0]),
        Err(e @ Error::Unsupported { .. }) => Err(format!("unsupported: {e}")),
        Err(e) => Err(format!("error: {e}")),
    }
}

#[test]
fn every_loop_proves_itself_in_the_simulator() {
    let Some(d) = dir() else { return };
    let (mut pass, mut unsup, mut bad) = (0, vec![], vec![]);
    for (stage, n) in STAGES {
        let doc = file(&d, &format!("loops/{stage}.vec.json"));
        let vs = doc.get("vectors").arr();
        assert_eq!(vs.len(), n, "{stage}");
        for v in vs {
            let id = v.get("id").str().unwrap_or("?");
            assert_eq!(v.get("init").get("task").str(), Some("loop-proof"), "{id}");
            let want = v.get("readback").get("proof").get("o0").hex().expect("a proof value") as u32;
            match run(v) {
                Ok(o0) if o0 == want => pass += 1,
                Ok(o0) => bad.push(format!("{stage}/{id}: model {o0:#x}, hardware {want:#x}")),
                Err(e) if e.starts_with("unsupported") => unsup.push(format!("{stage}/{id}: {e}")),
                Err(e) => bad.push(format!("{stage}/{id}: {e}")),
            }
        }
    }
    eprintln!("loop proofs: {pass} pass, {} unsupported, {} fail", unsup.len(), bad.len());
    for u in &unsup {
        eprintln!("  {u}");
    }
    assert!(bad.is_empty(), "{} mismatches:\n{}", bad.len(), bad.join("\n"));
    assert_eq!(pass + unsup.len(), 204, "every loop vector is run or named");
    assert!(pass >= 200, "only {pass} loop proofs pass");
}

/// The proof the hardware read is MARK of the program's own counter: the file says nothing the program name
/// does not (guards the converter against a mislabelled job), and a triangle host runs from index 0x20.
#[test]
fn the_proofs_name_their_counters_and_hosts() {
    let Some(d) = dir() else { return };
    for (stage, _) in STAGES {
        for v in file(&d, &format!("loops/{stage}.vec.json")).get("vectors").arr() {
            let id = v.get("id").str().unwrap_or("?");
            let probe = v.get("provenance").get("probe").str().unwrap();
            let n: u32 = probe.rsplit("-i").next().unwrap().parse().unwrap();
            let o0 = v.get("readback").get("proof").get("o0").hex().unwrap() as u32;
            assert_eq!(o0, if probe.starts_with("loop-abs") { 0 } else { 0xC0DE_0000 | n }, "{id}");
            let tri = v.get("init").get("host").str() == Some("tri");
            assert_eq!(v.get("init").get("code_index").num(), Some(if tri { 32.0 } else { 0.0 }), "{id}");
            let (count, of) = (
                v.get("readback").get("proof").get("count").num().unwrap(),
                v.get("readback").get("proof").get("of").num().unwrap(),
            );
            assert!(0.0 < count && count <= of, "{id}");
        }
    }
}

/// A vertex loop (q-v): the stored depth word of the hardware's object is the float32 0.5 + 0.5 z of the z the
/// program leaves in o2 (z = 0.25 + 4 N ulp, so the word is 0x3f200000 + N); the vertex runs as one of the draw.
fn run_vertex_z(v: &Json, i: u32) -> Result<u32, String> {
    let words: Vec<u64> = v.get("program").get("words").arr().iter().map(|w| w.hex().unwrap()).collect();
    let prog = Program::new(&words, Core::Sgx545);
    let init = v.get("init");
    let n = init.get("instances").num().unwrap() as u32;
    let per = init.get("per").num().unwrap() as u32;
    let mut mem = Memory { base: SCRATCH_BASE, words: vec![] };
    let mut m = Machine {
        temps: init.get("temps").num().map_or(124, |t| t as usize),
        vertex: Some((i, per, n)),
        ..Machine::default()
    };
    match m.run(&prog, &mut mem, STEPS) {
        Ok(()) => Ok((0.5f32 + 0.5f32 * f32::from_bits(m.o[2])).to_bits()),
        Err(e @ Error::Unsupported { .. }) => Err(format!("unsupported: {e}")),
        Err(e) => Err(format!("error: {e}")),
    }
}

#[test]
fn the_vertex_loops_store_the_depth_word_of_their_counter() {
    let Some(d) = dir() else { return };
    let doc = file(&d, "loops/q-v.vec.json");
    let vs = doc.get("vectors").arr();
    assert_eq!(vs.len(), 73);
    let (mut pass, mut unsup, mut bad) = (0, vec![], vec![]);
    for v in vs {
        let id = v.get("id").str().unwrap_or("?");
        let want: Vec<u32> =
            v.get("readback").get("depth_words").arr().iter().map(|w| w.hex().unwrap() as u32).collect();
        assert_eq!(want.len() as f64, v.get("init").get("instances").num().unwrap(), "{id}");
        let mut ok = true;
        for (i, w) in want.iter().enumerate() {
            match run_vertex_z(v, i as u32) {
                Ok(got) if got == *w => {}
                Ok(got) => {
                    bad.push(format!("{id} vertex {i}: model {got:#x}, hardware {w:#x}"));
                    ok = false;
                    break;
                }
                Err(e) if e.starts_with("unsupported") => {
                    unsup.push(format!("{id}: {e}"));
                    ok = false;
                    break;
                }
                Err(e) => {
                    bad.push(format!("{id}: {e}"));
                    ok = false;
                    break;
                }
            }
        }
        pass += ok as usize;
    }
    eprintln!("vertex loops: {pass} pass, {} unsupported, {} fail", unsup.len(), bad.len());
    for u in unsup.iter().take(3) {
        eprintln!("  {u}");
    }
    // refused, not passing: the loop's first instruction is the vertex program's `phas ... vcull`, which the model
    // stops on as a pixel task's hang (E121); the vertex role of that phas is not modelled. Any other reason, or a
    // pass, is news: the list below is the whole of what is refused and why.
    let refused = unsup.iter().filter(|u| u.contains(REFUSED)).count();
    assert_eq!(refused, unsup.len(), "unsupported for another reason: {unsup:?}");
    assert_eq!(pass + unsup.len(), 73, "every vertex loop is run or named");
    assert!(bad.is_empty(), "{} mismatches:\n{}", bad.len(), bad.join("\n"));
}

/// The direct reads of E808 (p-c3: g23, g24 or g25 written to o0 in a triangle's pixel program): every written pixel
/// the premise control confirms (`readback.undecoded` lists the others) reads what the model gives its quad's lane,
/// run as the aligned 2x2 quads the hardware ran (g25 is the lane).
#[test]
fn the_direct_reads_match_the_model_where_the_premise_holds() {
    let Some(d) = dir() else { return };
    let doc = file(&d, "direct-reads/p-c3.vec.json");
    let vs = doc.get("vectors").arr();
    assert_eq!(vs.len(), 8);
    let (mut compared, mut bad) = (0usize, vec![]);
    for v in vs {
        let id = v.get("id").str().unwrap_or("?");
        let init = v.get("init");
        let (w, h) = (init.get("width").num().unwrap() as usize, init.get("height").num().unwrap() as usize);
        let bg = init.get("background").hex().unwrap() as u32;
        let img: Vec<u32> =
            v.get("readback").get("image").arr().iter().map(|p| p.hex().unwrap() as u32).collect();
        assert_eq!(img.len(), w * h, "{id}");
        let skip: std::collections::HashSet<usize> =
            v.get("readback").get("undecoded").arr().iter().map(|i| i.num().unwrap() as usize).collect();
        let words: Vec<u64> = v.get("program").get("words").arr().iter().map(|x| x.hex().unwrap()).collect();
        let prog = Program::new(&words, Core::Sgx545);
        let temps = init.get("temps").num().unwrap() as usize;
        for y0 in (0..h).step_by(2) {
            for x0 in (0..w).step_by(2) {
                let at = [(x0, y0), (x0 + 1, y0), (x0, y0 + 1), (x0 + 1, y0 + 1)];
                if !at.iter().any(|&(x, y)| img[y * w + x] != bg && !skip.contains(&(y * w + x))) {
                    continue;
                }
                let mut quad: [Machine; 4] = Default::default();
                for (m, &(x, y)) in quad.iter_mut().zip(&at) {
                    m.temps = temps;
                    m.pa[0] = (y as u32) << 16 | x as u32;
                    m.pixel = Some((x as u32, y as u32));
                    m.written.pa |= 1;
                }
                let mut mem = Memory { base: SCRATCH_BASE, words: vec![] };
                if let Err(e) = run_quad(&mut quad, &prog, &mut mem, 10_000) {
                    bad.push(format!("{id} quad ({x0}, {y0}): {e}"));
                    continue;
                }
                for (m, &(x, y)) in quad.iter().zip(&at) {
                    let i = y * w + x;
                    if img[i] == bg || skip.contains(&i) {
                        continue;
                    }
                    compared += 1;
                    if m.o[0] != img[i] {
                        bad.push(format!(
                            "{id} pixel ({x}, {y}): model {:#x}, hardware {:#x}",
                            m.o[0], img[i]
                        ));
                    }
                }
            }
        }
    }
    eprintln!("direct reads: {compared} pixels compared, {} mismatches", bad.len());
    assert!(compared > 40_000, "only {compared} pixels compared");
    assert!(bad.is_empty(), "{} mismatches:\n{}", bad.len(), bad[..bad.len().min(20)].join("\n"));
}

#[test]
fn the_timing_files_are_there_with_a_row_a_job() {
    let Some(d) = dir() else { return };
    for (stage, n) in TIMINGS {
        let doc = file(&d, &format!("timings/{stage}.timing.json"));
        assert_eq!(doc.get("format").str(), Some("sgx545-timings"), "{stage}");
        let rows = doc.get("jobs").arr();
        assert_eq!(rows.len(), n, "{stage}");
        for r in rows {
            let id = r.get("id").str().unwrap_or("?");
            assert!(r.get("ta_run_us").num().is_some(), "{stage}/{id}: no ta_run_us");
            assert!(
                matches!(r.get("bit6"), Json::Bool(_)) && matches!(r.get("bit7"), Json::Bool(_)),
                "{stage}/{id}"
            );
        }
    }
}
