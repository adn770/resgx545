// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The 4x contexts' region-header arrays and H-COV, replayed on the kept rows (`$RESGX545_DATA`;
//! the tests skip, saying so, without it and fail with `RESGX545_REQUIRE_DATA`):
//! - E729 (texture/p1141 msaa-c-q140, module B21FDA82, one array): each job's completion and the
//!   page of its first BIF fault after its marker against `ta::header_layout_ending`;
//! - E788 (render/closing-r2-pixel, stages r2-a-safe and r2-a-fault, the same module): each job's
//!   class, its kept TA data's size against `ta::tadata_layout`, the non-zero dwords of each slot
//!   of the target's `rgn_size` against `ta::array_dwords` (nothing past the last array), and a6's
//!   fault page;
//! - E886 and E908 (render/closing-r6-misc and closing-r7-rp, stage q086): every row's ending
//!   against `dpm::poked_4x_ending` (H-COV), the rule's words where a row poked none.

use sgx_pipe::data::{Ctx, dwords};
use sgx_pipe::dpm::{Ending4x, PB_PAGES_DEFAULT, TailRoom, poked_4x_ending};
use sgx_pipe::ta::{HeaderEnding, array_dwords, header_layout_ending, rgn_size, tadata_layout, tiling};

const P1141: &str = "texture/p1141/out-hw/p1141tex-dumps/msaa-c-q140";
const R2: &str = "render/closing-r2-pixel/out/20261110-105258";
const R6: &str = "render/closing-r6-misc/out/20261112-144153/q086";
const R7: &str = "render/closing-r7-rp/out/20261112-205431/q086";
const TADATA_PAGE: u32 = 0x20000;

fn ctx(dir: &str) -> Option<Ctx> {
    let c = Ctx::from_env();
    if c.root.as_ref().is_some_and(|r| r.join(dir).is_dir()) {
        return Some(c);
    }
    assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no {dir} (RESGX545_DATA)");
    eprintln!("SKIPPED: no {dir} (set RESGX545_DATA)");
    None
}

fn read(c: &Ctx, rel: &str) -> String {
    let root = c.root.as_ref().unwrap();
    std::fs::read_to_string(root.join(rel)).unwrap()
}

fn text_gz(c: &Ctx, rel: &str) -> String {
    String::from_utf8(c.read_gz(rel, "").unwrap()).unwrap()
}

/// The rows of a cases.tsv as maps of column to value.
fn rows(tsv: &str) -> Vec<std::collections::BTreeMap<String, String>> {
    let mut lines = tsv.lines();
    let head: Vec<&str> = lines.next().unwrap().split('\t').collect();
    lines
        .filter(|l| !l.is_empty())
        .map(|l| head.iter().zip(l.split('\t')).map(|(k, v)| (k.to_string(), v.to_string())).collect())
        .collect()
}

/// The value of an option of a tool command line (`--width 320`).
fn opt(args: &str, name: &str) -> Option<u32> {
    let mut it = args.split_whitespace();
    while let Some(a) = it.next() {
        if a == name {
            return it.next().and_then(|v| v.parse().ok());
        }
    }
    None
}

fn hex(v: &str) -> u32 {
    u32::from_str_radix(v.trim_start_matches("0x"), 16).unwrap()
}

/// The `CR_TE_AA` word a row poked (`--poke cmd:1=...`).
fn te_aa(args: &str) -> u32 {
    let a = args.split_whitespace().find_map(|a| a.strip_prefix("cmd:1=")).unwrap();
    hex(a)
}

/// The page of a kernel log line's BIF fault address (`BIF fault 0x90004 at 0x20006062`).
fn fault_page(line: &str) -> Option<u32> {
    let (_, rest) = line.split_once("BIF fault ")?;
    let addr = rest.split_whitespace().nth(2)?;
    Some(hex(addr) >> 12)
}

#[test]
fn e729s_jobs_end_as_the_one_array_layout_says() {
    let Some(c) = ctx(P1141) else { return };
    let journal = text_gz(&c, &format!("{P1141}/journal-k.txt.gz"));
    let mut n = 0;
    for r in rows(&read(&c, &format!("{P1141}/cases.tsv"))) {
        let (name, a) = (&r["name"], &r["options"]);
        let (w, h) = (opt(a, "--width").unwrap(), opt(a, "--height").unwrap());
        let (mw, mh) = (opt(a, "--max-width").unwrap(), opt(a, "--max-height").unwrap());
        let model = header_layout_ending(w, h, mw, mh, te_aa(a), 1).unwrap();
        // the first BIF fault after the job's marker and before the next marker
        let first = journal
            .lines()
            .skip_while(|l| !l.contains(&format!("case {name} ")))
            .skip(1)
            .take_while(|l| !l.contains("p1141tex case "))
            .find_map(fault_page);
        let out = text_gz(&c, &format!("{P1141}/{name}.txt.gz"));
        let complete = out.contains(&format!("diff: 0 of {}", w * h));
        match model {
            HeaderEnding::Complete => assert!(complete && first.is_none(), "{name}: {first:?}"),
            HeaderEnding::Fault { page } => {
                assert!(!complete, "{name}");
                assert_eq!(first, Some(TADATA_PAGE + page), "{name}");
            }
        }
        n += 1;
    }
    assert_eq!(n, 5);
}

#[test]
fn e788s_jobs_ta_data_and_endings_are_the_models() {
    let Some(c) = ctx(R2) else { return };
    let mut n = 0;
    for stage in ["r2-a-safe", "r2-a-fault"] {
        for r in rows(&read(&c, &format!("{R2}/{stage}/cases.tsv"))) {
            let (name, a) = (&r["name"], &r["args"]);
            let (w, h) = (opt(a, "--width").unwrap(), opt(a, "--height").unwrap());
            let (mw, mh) = (opt(a, "--max-width").unwrap(), opt(a, "--max-height").unwrap());
            let te = te_aa(a);
            let model = header_layout_ending(w, h, mw, mh, te, 1).unwrap();
            match model {
                HeaderEnding::Complete => {
                    assert_eq!(r["class"], "ok", "{name}");
                    let td =
                        dwords(&c.read_gz(&format!("{R2}/{stage}/{name}.tri.tadata.bin.gz"), "").unwrap());
                    let layout = tadata_layout(mw, mh, 1).unwrap();
                    assert_eq!(4 * td.len() as u32, layout.size, "{name}");
                    // nothing below the headers
                    assert!(td[..(layout.rgn / 4) as usize].iter().all(|&v| v == 0), "{name}");
                    let per = (rgn_size(w, h) / 4) as usize;
                    let slots: Vec<u32> = td[(layout.rgn / 4) as usize..]
                        .chunks(per)
                        .map(|s| s.iter().filter(|&&v| v != 0).count() as u32)
                        .collect();
                    let want = array_dwords(w, h, te).unwrap();
                    assert_eq!(&slots[..want.len()], &want[..], "{name}");
                    assert!(slots[want.len()..].iter().all(|&k| k == 0), "{name}: {slots:?}");
                }
                HeaderEnding::Fault { page } => {
                    assert_eq!(r["class"], "fault", "{name}");
                    let log = text_gz(&c, &format!("{R2}/{stage}/{name}.dmesg.gz"));
                    assert_eq!(log.lines().find_map(fault_page), Some(TADATA_PAGE + page), "{name}");
                }
            }
            n += 1;
        }
    }
    assert_eq!(n, 6);
}

/// The q086 rows of a stage: (name, ending observed, ending modelled).
fn q086(c: &Ctx, dir: &str, room: TailRoom) -> Vec<(String, Ending4x, Option<Ending4x>)> {
    rows(&read(c, &format!("{dir}/cases.tsv")))
        .into_iter()
        .map(|r| {
            let a = &r["args"];
            let (w, h) = (opt(a, "--width").unwrap(), opt(a, "--height").unwrap());
            let (mw, mh) = (opt(a, "--max-width").unwrap(), opt(a, "--max-height").unwrap());
            assert_eq!(te_aa(a), 0xe000_0000, "{}", r["name"]);
            let t = tiling(w, h);
            let (mut m1, mut m2, mut stride) = (t.mtile1, t.mtile2, t.stride);
            for p in a.split_whitespace().filter_map(|p| p.strip_prefix("1:ta:")) {
                let (i, v) = p.split_once('=').unwrap();
                match i {
                    "143" => m1 = hex(v),
                    "144" => m2 = hex(v),
                    "146" => stride = hex(v),
                    _ => panic!("{}: poke {p}", r["name"]),
                }
            }
            let seen = match (r["class"].as_str(), r["fault_req"].as_str(), r["fault_word"].as_str()) {
                ("ok", ..) => Ending4x::Complete,
                ("fault", "256", "0x10000011") => Ending4x::Fault,
                k => panic!("{}: {k:?}", r["name"]),
            };
            let model = poked_4x_ending(w, h, mw, mh, PB_PAGES_DEFAULT, room, m1, m2, stride);
            (r["name"].clone(), seen, model)
        })
        .collect()
}

#[test]
fn e886s_and_e908s_q086_rows_end_as_h_cov_says() {
    for (dir, room, count) in [(R6, TailRoom::Rgn4, 10), (R7, TailRoom::Quad, 11)] {
        let Some(c) = ctx(dir) else { return };
        let rs = q086(&c, dir, room);
        assert_eq!(rs.len(), count, "{dir}");
        for (name, seen, model) in rs {
            assert_eq!(model, Some(seen), "{name}");
        }
    }
}
