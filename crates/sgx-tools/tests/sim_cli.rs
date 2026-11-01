// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The sgx-sim command: runs a USSE program (source or binary) on the
//! simulator and prints what it wrote, with a trace on request; runs the
//! hardware vectors against the hardware readbacks.

use std::io::Write as _;
use std::path::PathBuf;
use std::process::{Command, Output, Stdio};

fn sim(args: &[&str], stdin: &str) -> Output {
    let mut c = Command::new(env!("CARGO_BIN_EXE_sgx-sim"))
        .args(args)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    c.stdin.take().unwrap().write_all(stdin.as_bytes()).unwrap();
    c.wait_with_output().unwrap()
}

/// A file of the public data repository: $RESGX545_DATA or a sibling ../resgx545-data. None
/// when absent: the tests that need it skip.
fn data(rel: &str) -> Option<PathBuf> {
    let root = std::env::var_os("RESGX545_DATA")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../../resgx545-data"));
    let p = root.join(rel);
    p.is_file().then_some(p)
}

fn out(o: &Output) -> String {
    String::from_utf8_lossy(&o.stdout).into_owned()
}

const SHL: &str = "mov r1, #0x00000002\nshl r2, r1, #3\nmov.end o0, r2\n";

#[test]
fn runs_a_source_and_prints_what_it_wrote() {
    let o = sim(&["-"], SHL);
    assert!(o.status.success(), "{o:?}");
    let s = out(&o);
    assert!(s.contains("ended after 3 steps"), "{s}");
    for l in ["r1 = 0x00000002", "r2 = 0x00000010", "o0 = 0x00000010"] {
        assert!(s.lines().any(|x| x == l), "{l} in {s}");
    }
}

#[test]
fn traces_each_instruction_and_its_writes() {
    let s = out(&sim(&["--trace", "-"], SHL));
    assert!(s.contains("0: mov r1, #0x00000002"), "{s}");
    assert!(s.contains("    r1 = 0x00000002"), "{s}");
    assert!(s.contains("1: shl r2, r1, #0x00000003"), "{s}");
}

#[test]
fn presets_registers() {
    let s = out(&sim(&["--set", "r1=0x10", "--set", "pa0=5", "-"], "or r2, r1, pa0\nmov.end o0, r2\n"));
    assert!(s.lines().any(|x| x == "o0 = 0x00000015"), "{s}");
}

#[test]
fn stops_where_the_model_stops() {
    let o = sim(&["-"], "mov.end o0, r5\n");
    assert_eq!(o.status.code(), Some(1));
    assert!(String::from_utf8_lossy(&o.stderr).contains("unsupported"), "{o:?}");
}

#[test]
fn runs_a_quad() {
    // i3 is the next instance's i0: TR's pa0 for TL at (0, 0)
    let s = out(&sim(&["--quad", "0,0", "-"], "mov i0, pa0\nmov.end o0, i3\n"));
    assert!(s.lines().any(|x| x == "o0 = 0x00000001"), "{s}");
}

#[test]
fn checks_the_hardware_vectors() {
    let Some(v) = data("vectors/vec1.vec.json") else {
        eprintln!("skip: no data repository (set RESGX545_DATA)");
        return;
    };
    let s = out(&sim(&["--vectors", v.to_str().unwrap()], ""));
    assert!(s.contains("533 match, 4 unsupported, 0 mismatch"), "{s}");
}

#[test]
fn lists_the_emits() {
    let s =
        out(&sim(&["-"], "mov r0, #0x00000011\nemitpix2.end.freep #0 /* incp */, r0, #0, r0, #0x00000200\n"));
    assert!(s.lines().any(|x| x == "emit emitpix2 0x00000011, 0x00000000, 0x00000011"), "{s}");
}

#[test]
fn near_values_carry_their_bound() {
    // frcp of 3 is within one ulp on the hardware: only with --near
    let src = "mov r1, #0x40400000\nfrcp r2, r1\nmov.end o0, r2\n";
    assert_eq!(sim(&["-"], src).status.code(), Some(1));
    let s = out(&sim(&["--near", "-"], src));
    assert!(s.lines().any(|x| x == "r2 = 0x3eaaaaab ~ within 1 ulp"), "{s}");
    assert!(s.lines().any(|x| x == "o0 = 0x3eaaaaab ~ within 1 ulp"), "{s}");
    assert!(s.lines().any(|x| x == "r1 = 0x40400000"), "{s}");
}

const PDS_SRC: &str = ".word 5, 0, 7, 0x100\nadd ds0[48], ds0[0], ds1[0]\nmovs douta, ds0[48], ds1[1], ds0[48], ds0[48]\nhalt\n";

#[test]
fn runs_a_pds_program_and_lists_its_port_writes() {
    let o = sim(&["--pds", "-"], PDS_SRC);
    assert!(o.status.success(), "{o:?}");
    let s = out(&o);
    assert!(s.contains("halted after 3 steps"), "{s}");
    for l in ["ds0[48] = 0x0000000c", "movs douta 0x0000000c, 0x00000100, 0x0000000c, 0x0000000c"] {
        assert!(s.lines().any(|x| x == l), "{l} in {s}");
    }
    let t = out(&sim(&["--pds", "--trace", "-"], PDS_SRC));
    assert!(t.contains("0: add ds0[48], ds0[0], ds1[0]\n    ds0[48] = 0x0000000c\n"), "{t}");
}

#[test]
fn a_pds_program_stops_on_what_is_open() {
    let o = sim(&["--pds", "-"], "mov32 ds0[48], ir0.0\nhalt\n");
    assert_eq!(o.status.code(), Some(1), "{o:?}");
    assert!(String::from_utf8_lossy(&o.stderr).contains("ir0 is not known"), "{o:?}");
    let o = sim(&["--pds", "--set", "ir0=0x402", "-"], "mov32 ds0[48], ir0.0\nhalt\n");
    assert!(out(&o).lines().any(|l| l == "ds0[48] = 0x00000402"), "{o:?}");
}

#[test]
fn runs_the_pds_vectors() {
    let Some(f) = data("vectors/pds1/runs_probes_pds1_ab.vec.json") else {
        eprintln!("skip: no data repository (set RESGX545_DATA)");
        return;
    };
    let o = sim(&["--vectors", f.to_str().unwrap()], "");
    assert!(o.status.success(), "{o:?}");
    assert!(out(&o).contains("101 match, 2 unsupported, 0 mismatch, 0 skipped"), "{}", out(&o));
}

#[test]
fn a_preset_predicate_or_pclink_counts_as_set() {
    // 11.28: p0-p3 and pclink read before the program sets them stop it (they are left over from
    // the job before), so a host preset must mark them set
    let o = sim(&["--set", "p0=1", "-"], "p0 mov.end o0, #5\n");
    assert!(out(&o).contains("o0 = 0x00000005"), "{} {}", out(&o), String::from_utf8_lossy(&o.stderr));
    let o = sim(&["--set", "pclink=7", "-"], "mov r1, pclink\nmov.end o0, r1\n");
    assert!(out(&o).contains("o0 = 0x00000007"), "{} {}", out(&o), String::from_utf8_lossy(&o.stderr));
}

#[test]
fn a_vcull_phas_runs_only_as_a_vertex_task() {
    let src = "phas #2, #8, pixel, vcull, parallel\nmov.end o0, #5\nmov.end o0, #7\n";
    assert_eq!(sim(&["-"], src).status.code(), Some(1));
    let o = sim(&["--task", "vertex", "-"], src);
    assert!(out(&o).contains("o0 = 0x00000005"), "{}", out(&o));
}
