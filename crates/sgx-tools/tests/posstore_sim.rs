// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The position-store pixel program (probes/pds/templates/pix_posstore.s, E898, run in E904) on the
//! simulator: assembled from the template, run as a triangle's pixel instance (g23, g24 and g25
//! as E808 measured) at every pixel of a 64 x 32 area with E437's position pair (pa0 = x + 0.5,
//! pa1 = y + 0.5 as floats). Every instance stores at the scratch slot of its place in its tile,
//! 16 bytes at 16 x (y mod 16 << 5 | x mod 32): pa0, pa0, pa1 and 0x7E570000 | lane, and leaves
//! o0 = pa0. The round 7 plan's scratch harness (closing7/a/q291/simcheck) made the same check.

use sgx_sim::{Bus, Error, Machine, Memory, Program};
use sgx_tools::asm::{USSE, assemble};
use std::path::PathBuf;
use usse_isa::Core;

const SCRATCH: u32 = 0x5CAF_0000;

struct Scratch {
    mem: Memory,
    stores: Vec<(u32, u32)>,
}

impl Bus for Scratch {
    fn load32(&mut self, addr: u32) -> Result<u32, Error> {
        self.mem.load32(addr)
    }
    fn store32(&mut self, addr: u32, v: u32) -> Result<(), Error> {
        self.stores.push((addr, v));
        self.mem.store32(addr, v)
    }
}

fn words() -> Vec<u64> {
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../probes/pds/templates/pix_posstore.s");
    let text = std::fs::read(&path).unwrap_or_else(|e| panic!("{}: {e}", path.display()));
    let a = assemble(&USSE, &text, "pix_posstore.s", Core::Sgx545);
    assert_eq!(a.errors, 0, "{}", String::from_utf8_lossy(&a.messages));
    a.words
}

/// The (address, value) stores of one instance and its o0, if written.
type Outcome = (Vec<(u32, u32)>, Option<u32>);

/// What one instance at (x, y) leaves, or the simulator's error.
fn run(prog: &Program, x: u32, y: u32) -> Result<Outcome, Error> {
    let mut m = Machine { core: Core::Sgx545, temps: 4, tri_pixel: true, ..Machine::default() };
    m.pixel = Some((x, y));
    m.pa[0] = (x as f32 + 0.5).to_bits();
    m.pa[1] = (y as f32 + 0.5).to_bits();
    m.written.pa |= 3;
    let mut bus = Scratch {
        mem: Memory { base: SCRATCH, words: (0..0x4000u32).map(|i| 0xD000_0000 | i).collect() },
        stores: Vec::new(),
    };
    m.run(prog, &mut bus, 1000)?;
    Ok((bus.stores, (m.written.o & 1 != 0).then_some(m.o[0])))
}

#[test]
fn the_template_is_the_plans_seventeen_instructions() {
    let w = words();
    let prog = Program::new(&w, Core::Sgx545);
    let texts: Vec<&str> = (0..).map_while(|pc| Machine::text(&prog, pc)).collect();
    assert_eq!(texts.len(), 17, "{texts:#?}");
    assert_eq!(texts[1], "shl r1, g24, #0x00000005");
    assert_eq!(texts[2], "or r1, r1, g23");
    assert_eq!(texts[5], "or r2, g25, #0x7E570000");
    assert_eq!(texts[16], "mov.skipinv.end o0, pa0");
    // the only global registers it reads are the three a triangle's pixel task has (E808)
    let globals: Vec<&str> =
        texts.iter().flat_map(|t| t.split([' ', ','])).filter(|s| s.starts_with('g')).collect();
    assert_eq!(globals, ["g24", "g23", "g25"]);
}

#[test]
fn every_pixel_of_a_64_x_32_area_stores_its_own_slot() {
    let w = words();
    let prog = Program::new(&w, Core::Sgx545);
    let mut bad = Vec::new();
    for y in 0..32 {
        for x in 0..64 {
            let (px, py) = ((x as f32 + 0.5).to_bits(), (y as f32 + 0.5).to_bits());
            let base = SCRATCH + 16 * ((y % 16) << 5 | (x % 32));
            let lane = 0x7E57_0000 | (x & 1) | (y & 1) << 1;
            let want = vec![(base, px), (base + 4, px), (base + 8, py), (base + 12, lane)];
            match run(&prog, x, y) {
                Ok((stores, o0)) if stores == want && o0 == Some(px) => {}
                r => bad.push(format!("({x}, {y}): {r:x?}")),
            }
        }
    }
    assert!(bad.is_empty(), "{} of 2048 pixels wrong: {:#?}", bad.len(), &bad[..bad.len().min(4)]);
}
