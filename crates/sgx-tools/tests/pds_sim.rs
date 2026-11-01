// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! PDS programs on the simulator (sgx_sim::pds), run to their halt with the
//! port writes they are known to make: our transfer templates from asm/, and
//! the microkernel's five (harness/ukernel-extract/extracted, gitignored;
//! skipped without it). The data words a driver patches get distinct markers,
//! so each check also says which data dword reached which port word.

use sgx_sim::pds::{Pds, Port, Program};
use sgx_sim::{Bus, Error};
use sgx_tools::asm::{PDS, assemble};
use std::path::PathBuf;
use usse_isa::Core;

#[derive(Default)]
struct Ports(Vec<(Port, [u32; 4])>);

impl Bus for Ports {
    fn load32(&mut self, a: u32) -> Result<u32, Error> {
        Err(Error::Fault(a))
    }
    fn store32(&mut self, a: u32, _: u32) -> Result<(), Error> {
        Err(Error::Fault(a))
    }
    fn port(&mut self, port: Port, words: [u32; 4]) -> Result<(), Error> {
        self.0.push((port, words));
        Ok(())
    }
}

fn root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..")
}

/// asm/<path> assembled: its words and data dwords; `marked` data dwords get
/// the marker 0xD0 + their index.
fn ours(path: &str, marked: &[usize]) -> (Vec<u32>, usize) {
    let text = std::fs::read(root().join("asm").join(path)).unwrap();
    let a = assemble(&PDS, &text, path, Core::Sgx545);
    assert_eq!(a.errors, 0, "{}", String::from_utf8_lossy(&a.messages));
    let mut w: Vec<u32> = a.words.iter().map(|&x| x as u32).collect();
    for &i in marked {
        w[i] = 0xD0 + i as u32;
    }
    (w, a.ndata)
}

fn run(words: &[u32], data: usize, ir: [Option<u32>; 3]) -> Result<Vec<(Port, [u32; 4])>, Error> {
    let (mut m, mut bus) = (Pds { ir, ..Pds::default() }, Ports::default());
    m.run(&Program::new(words, data), &mut bus, 1000)?;
    Ok(bus.0)
}

/// The data dword that holds dsB[n] (rows of ds0[2r], ds0[2r+1], ds1[2r], ds1[2r+1]).
fn ds(words: &[u32], b: usize, n: usize) -> u32 {
    words[n / 2 * 4 + b * 2 + (n & 1)]
}

fn stops_on_an_open_special(r: Result<Vec<(Port, [u32; 4])>, Error>) {
    match r {
        Err(Error::Unsupported { why, .. }) => assert!(why.contains("as a movs source is open"), "{why}"),
        r => panic!("{r:?}"),
    }
}

#[test]
fn primary_and_secondary_templates_kick_their_task() {
    for t in ["transfer/pds_prim.s", "transfer/pds_sec.s"] {
        let (w, n) = ours(t, &[0, 1, 2]);
        assert_eq!(run(&w, n, [None; 3]).unwrap(), vec![(Port::Doutu, [0xD0, 0xD1, 0xD2, 0xD0])], "{t}");
    }
}

#[test]
fn the_copy_primary_issues_the_task_the_fetch_and_the_texture_state() {
    let (w, n) = ours("transfer/pds_prim_1src.s", &(0..10).collect::<Vec<_>>());
    assert_eq!(
        run(&w, n, [None; 3]).unwrap(),
        vec![
            (Port::Doutu, [0xD0, 0xD1, 0xD2, 0xD0]),
            (Port::Douti, [0xD4, 0xD5, 0xD4, 0xD4]),
            (Port::Doutt, [0xD8, 0xD9, 0xD6, 0xD7]),
        ]
    );
}

#[test]
fn the_pixel_event_program_picks_the_task_by_event() {
    let (w, n) = ours("transfer/pds_pixevent.s", &[0, 1, 2, 3, 4, 5, 12]);
    let ev = |ir1: u32| run(&w, n, [Some(0x0001_0203), Some(ir1), None]);
    let eor = vec![(Port::Doutu, [0xD4, 0xD5, 0xD4, 0xD4])];
    assert_eq!(ev(0x8).unwrap(), vec![(Port::Doutu, [0xD0, 0xD1, 0xD0, 0xD0])]); // PTOFF
    assert_eq!(ev(0x4).unwrap(), eor); // end of render
    assert_eq!(ev(0x102).unwrap(), eor); // end of tile with bit 8: end of render instead
    assert_eq!(ev(0).unwrap(), vec![]);
    // end of tile passes ir1.l on with douta: open (ir0.l is all of ir0)
    stops_on_an_open_special(ev(0x2));
}

/// The microkernel's PDS programs as srvinit leaves them, with their data
/// sizes (tools/fwcutter/facts.py BUFFERS, in rows of four dwords).
fn aux(n: u32) -> Option<(Vec<u32>, usize)> {
    let p = root().join(format!("harness/ukernel-extract/extracted/sgx545_pds{n}_runtime.bin"));
    let b = std::fs::read(p).ok()?;
    let rows = [1, 2, 1, 6, 3][n as usize - 10];
    Some((b.chunks_exact(4).map(|c| u32::from_le_bytes(c.try_into().unwrap())).collect(), rows * 4))
}

#[test]
fn the_microkernel_pds_programs() {
    let Some((p10, d10)) = aux(10) else {
        eprintln!("skip: no extracted microkernel PDS programs");
        return;
    };
    // #10 and #12 start the boot and init-done tasks (hw_spec 11.2)
    assert_eq!(run(&p10, d10, [None; 3]).unwrap(), vec![(Port::Doutu, [p10[0], p10[1], p10[2], p10[0]])]);
    let (p12, d12) = aux(12).unwrap();
    assert_eq!(run(&p12, d12, [None; 3]).unwrap(), vec![(Port::Doutu, [p12[0], p12[1], p12[2], p12[0]])]);
    // #11 DMAs TA3DCtl into the secondary attributes when ir0 is 0, then
    // starts edm.task.pds11 either way
    let (p11, d11) = aux(11).unwrap();
    let task = (Port::Doutu, [ds(&p11, 0, 2), ds(&p11, 0, 3), ds(&p11, 1, 0), ds(&p11, 0, 2)]);
    assert_eq!(
        run(&p11, d11, [Some(0), None, None]).unwrap(),
        vec![(Port::Doutd, [p11[0], p11[1], p11[0], p11[0]]), task]
    );
    assert_eq!(run(&p11, d11, [Some(1), None, None]).unwrap(), vec![task]);
    // #13 (events) and #14 (deferred work) first pass their inputs on with
    // douta of ir0.l (all of ir0), ir1.l, tim.l: the last two open
    for n in [13, 14] {
        let (p, d) = aux(n).unwrap();
        stops_on_an_open_special(run(&p, d, [Some(0); 3]));
    }
}
