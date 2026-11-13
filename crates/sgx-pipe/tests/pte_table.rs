// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The r9-faults PTE tables (`vectors/closing/r9-faults/pte/xf2.table.json`, E964, and
//! `tri2.table.json`, E965) replayed with `bif::pte_access`: each knob row's access is named from
//! its arguments and the knob's address (a fill's destination and a 64 x 64 triangle's colour
//! target: the pixel write; a copy's source: the texture read; the GENERAL page: the stream read;
//! the depth store's buffer of `tri --depth --depth-store`: the ZLS store), its flags from the
//! kernel's `vm_map ... PTE flags` line, and the model's end is compared with the row's: the
//! fault word, the page it names (the mapping's first, or the last page the access wrote: the
//! fill's last row, the target's last page, the ZLS store window's last page, 8 tiles of 512
//! dwords at 64 x 64, E465) and `SB`, and, for the pixel accesses, whether the image is exact.
//! A row the model has no access for (the depth buffer, which the clearing control does not
//! load; the tool's isolation) is refused, never a pass. Each table's `replay` names
//! `the_model_replays_every_modelled_row_of_the_pte_tables`. Skips without the data, and fails
//! with `RESGX545_REQUIRE_DATA` set.

use sgx_pipe::bif::{FaultPage, PteAccess, PteEnd, pte_access};
use sgx_pipe::data::Ctx;
use sgx_sim::json::{Json, parse};

/// Each table and its count of rows the model replays (every row but the refused ones).
const TABLES: &[(&str, usize, usize)] = &[
    ("vectors/closing/r9-faults/pte/xf2.table.json", 12, 11),
    ("vectors/closing/r9-faults/pte/tri2.table.json", 7, 6),
];
const NAME: &str = "the_model_replays_every_modelled_row_of_the_pte_tables";
const PAGE: u64 = 0x1000;

#[derive(Debug, PartialEq)]
enum Row {
    Matched,
    Refused(&'static str),
    Mismatched(String),
}

fn load(table: &str) -> Option<Json> {
    let ctx = Ctx::from_env();
    let Some(root) = ctx.root.as_ref().filter(|r| r.join(table).is_file()) else {
        assert!(std::env::var_os("RESGX545_REQUIRE_DATA").is_none(), "no {table}");
        eprintln!("SKIPPED: no {table}");
        return None;
    };
    Some(parse(&std::fs::read_to_string(root.join(table)).unwrap()))
}

fn opt(args: &str, name: &str, default: u64) -> u64 {
    args.split_whitespace().skip_while(|w| *w != name).nth(1).map(|v| v.parse().unwrap()).unwrap_or(default)
}

/// The access a knob at `addr` meets in a job of `args`, and the last page that access writes.
fn access(args: &str, addr: u64) -> Result<(PteAccess, Option<u64>), &'static str> {
    let cmd = args.split_whitespace().next().unwrap_or("");
    match (cmd, addr, args.contains("--depth")) {
        ("fill", 0x3e00_1000, _) => {
            let (w, h, y) = (opt(args, "--width", 64), opt(args, "--height", 32), opt(args, "--y", 0));
            Ok((PteAccess::PixelWrite, Some(addr + ((y + h - 1) * 256 + w * 4 - 1) / PAGE * PAGE)))
        }
        ("copy", 0x3e00_1000, _) => Ok((PteAccess::TextureRead, None)),
        ("tri", 0x3e00_1000, false) => Ok((PteAccess::PixelWrite, Some(addr + 3 * PAGE))),
        ("tri", 0x3e00_0000, _) => Ok((PteAccess::StreamRead, None)),
        ("tri", 0x3e01_5000, true) => Ok((PteAccess::ZlsStore, Some(addr + 4096 * 4 - PAGE))),
        ("tri", 0x3e00_1000, true) => Err("the depth buffer: the clearing control 0x0017100c loads nothing"),
        _ => Err("no PTE knob access the model names"),
    }
}

fn replay(row: &Json) -> Row {
    let args = row.get("args").str().unwrap_or("");
    let lines = row.get("pte_lines").arr();
    if args.starts_with("isolation") {
        return Row::Refused("the tool's isolation: no PTE knob");
    }
    let exact = row.get("diff").arr().first().and_then(Json::num) == Some(0.0);
    let id = row.get("id").str().unwrap_or("?");
    let Some(l) = lines.first() else {
        // a knob-free control (or the address alone): no flags, the model's clean end
        return if exact && row.get("faults").arr().is_empty() {
            Row::Matched
        } else {
            Row::Mismatched(format!("{id}: no PTE flags, yet not exact"))
        };
    };
    let (addr, pte) = (l.arr()[0].hex().unwrap(), l.arr()[2].hex().unwrap() as u32);
    let (acc, last) = match access(args, addr) {
        Ok(a) => a,
        Err(why) => return Row::Refused(why),
    };
    let Ok(PteEnd { written, fault }) = pte_access(pte, acc) else {
        return Row::Refused("flags and access the model refuses");
    };
    let faults = row.get("faults").arr();
    match (fault, faults.first()) {
        (None, None) if exact || acc == PteAccess::ZlsStore => Row::Matched,
        (Some(f), Some(got)) => {
            let (int, at) = (got.arr()[0].hex().unwrap() as u32, got.arr()[1].hex().unwrap());
            let page = match f.page {
                FaultPage::First => addr,
                FaultPage::LastWritten => last.unwrap(),
            };
            let pixels_ok = acc == PteAccess::ZlsStore || written == exact;
            if int == f.int_stat && at & !0xfff == page && (at >> 4 & 0x1f) as u32 == f.sb && pixels_ok {
                Row::Matched
            } else {
                Row::Mismatched(format!(
                    "{id}: model {f:?} written {written}, row {int:#x} at {at:#x} exact {exact}"
                ))
            }
        }
        (m, g) => Row::Mismatched(format!(
            "{id}: model {m:?}, row faults {:?} exact {exact}",
            g.map(|_| faults.len())
        )),
    }
}

#[test]
fn the_model_replays_every_modelled_row_of_the_pte_tables() {
    for (table, rows, modelled) in TABLES {
        let Some(t) = load(table) else { continue };
        let all = t.get("rows").arr();
        assert_eq!(all.len(), *rows, "{table}");
        let out: Vec<Row> = all.iter().map(replay).collect();
        let bad: Vec<&Row> = out.iter().filter(|r| matches!(r, Row::Mismatched(_))).collect();
        assert!(bad.is_empty(), "{table}: {bad:?}");
        assert_eq!(out.iter().filter(|r| **r == Row::Matched).count(), *modelled, "{table}: {out:?}");
    }
}

#[test]
fn a_wrong_fault_page_or_word_is_a_mismatch() {
    let row = |faults: &str, diff: &str| {
        parse(&format!(
            r#"{{"id": "x", "args": "fill --width 64 --height 64", "pte_lines": [["0x3e001000", "0x5000", "0x2"]],
               "faults": {faults}, "diff": {diff}}}"#
        ))
    };
    assert_eq!(replay(&row(r#"[["0x80020", "0x3e0041f1"]]"#, "[0, 4096]")), Row::Matched);
    assert!(matches!(replay(&row(r#"[["0x80020", "0x3e0051f1"]]"#, "[0, 4096]")), Row::Mismatched(_)));
    assert!(matches!(replay(&row(r#"[["0xa0020", "0x3e0041f1"]]"#, "[0, 4096]")), Row::Mismatched(_)));
    assert!(matches!(replay(&row("[]", "[0, 4096]")), Row::Mismatched(_)));
    assert!(matches!(replay(&row(r#"[["0x80020", "0x3e0041f1"]]"#, "[4096, 4096]")), Row::Mismatched(_)));
}

#[test]
fn each_table_names_this_test_as_its_replay() {
    for (table, _, _) in TABLES {
        let Some(t) = load(table) else { continue };
        let r = t.get("replay");
        assert_eq!(r.get("status").str(), Some("replayed"), "{table}");
        assert!(r.get("test").str().unwrap().ends_with(NAME), "{:?}", r.get("test").str());
    }
}
