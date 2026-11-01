// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The vertex side's tasks (12.2): a state block's PDS program and USSE task, and a vertex's, run
//! on `sgx-sim` unchanged. The PDS program's `doutd` DMAs memory into the task's primary
//! attributes (here: the pipe's bus does the copy, from the fields pds_isa 3 states), its `doutu`
//! starts the USSE task from the vertex heap's code base; the task runs on `Machine` until it hands
//! its outputs to the vertex cache (`emitvcbst`, `emitvcbvtx`): what the MTE takes is the outputs
//! `o0..` at that point (an assumption: the library's programs hand the same outputs on in the
//! phase after, E351).

use crate::Outcome;
use crate::mem::Mem;
use sgx_sim::pds::{self, Pds, Port};
use sgx_sim::{Bus, Error, Machine, Program};
use usse_isa::Core;

pub const OPEN: &[&str] = &["Q050", "Q076", "Q003", "Q231"];

/// The vertex heap's code base the library's vertex programs run from (DOUTU U0 bits 3:0 = 10).
pub const VERTEX_CODE_BASE: u32 = 10;

/// What a PDS program did: the DMAs (address, control word) in order and the task it started.
#[derive(Debug, Default, Clone, PartialEq)]
pub struct PdsRun {
    pub dma: Vec<(u32, u32)>,
    pub task: Option<[u32; 3]>,
}

const STEPS: usize = 100_000;

fn refusal(e: Error, what: &str) -> Outcome {
    match e {
        Error::Fault(a) => Outcome::unsupported(
            &format!("{what}: access to unmapped address {a:#010x} (flat memory: no MMU model yet)"),
            &["Q076", "Q003"],
        ),
        Error::Unsupported { why, .. } => Outcome::unsupported(&format!("{what}: {why}"), &["Q050"]),
        e => Outcome::unsupported(&format!("{what}: {e}"), &["Q050"]),
    }
}

/// The scene's memory as the bus of both units: reads only (a vertex program stores nothing).
struct ReadBus<'a>(&'a Mem);

impl Bus for ReadBus<'_> {
    fn load32(&mut self, addr: u32) -> Result<u32, Error> {
        self.0.read32(addr).map_err(|_| Error::Fault(addr))
    }
    fn store32(&mut self, addr: u32, _v: u32) -> Result<(), Error> {
        Err(Error::Unsupported {
            pc: 0,
            text: String::new(),
            why: format!("a store to {addr:#x} in a vertex-side task"),
        })
    }
}

/// The PDS side: `doutd` and `doutu` are recorded for the caller (the DMA and the task start);
/// any other port is a program no record explains.
struct PdsBus<'a> {
    mem: &'a Mem,
    run: PdsRun,
}

impl Bus for PdsBus<'_> {
    fn load32(&mut self, addr: u32) -> Result<u32, Error> {
        self.mem.read32(addr).map_err(|_| Error::Fault(addr))
    }
    fn store32(&mut self, addr: u32, _v: u32) -> Result<(), Error> {
        Err(Error::Unsupported {
            pc: 0,
            text: String::new(),
            why: format!("a store to {addr:#x} in a vertex-side PDS program"),
        })
    }
    fn port(&mut self, port: Port, w: [u32; 4]) -> Result<(), Error> {
        match port {
            Port::Doutd => self.run.dma.push((w[0], w[1])),
            Port::Doutu => {
                if self.run.task.is_some() {
                    return Err(Error::Unsupported {
                        pc: 0,
                        text: String::new(),
                        why: "a vertex PDS program starts two tasks".into(),
                    });
                }
                self.run.task = Some([w[0], w[1], w[2]]);
            }
            p => {
                return Err(Error::Unsupported {
                    pc: 0,
                    text: String::new(),
                    why: format!("a vertex-side PDS program writes the {p:?} port"),
                });
            }
        }
        Ok(())
    }
}

/// Run the PDS program of a state block or vertex at `pds` (`data` data dwords) with `ir0`; `if0`
/// is whether the program's `(if0)` tests true (the last vertex of a task: pds_isa 8.11).
pub fn run_pds(mem: &Mem, pds: u32, data: u32, ir0: u32, if0: bool) -> Result<PdsRun, Outcome> {
    let what = format!("the PDS program at {pds:#010x}");
    let w: Vec<u32> = (0..data + 256).map_while(|i| mem.read32(pds.wrapping_add(4 * i)).ok()).collect();
    if (w.len() as u32) < data {
        return Err(refusal(Error::Fault(pds), &what));
    }
    let prog = pds::Program::new(&w, data as usize);
    let mut p = Pds { ir: [Some(ir0), None, None], ifs: [Some(if0), Some(false)], ..Pds::default() };
    let mut bus = PdsBus { mem, run: PdsRun::default() };
    p.run(&prog, &mut bus, STEPS).map_err(|e| refusal(e, &what))?;
    Ok(bus.run)
}

/// The primary attributes the DMAs of a PDS run fill, as (attribute, value): each DMA copies
/// `lines` bursts of `burst` dwords, a burst every `stride` dwords from the address, to the
/// destination attribute on (control word: burst - 1 in 3:0, lines - 1 in 7:4, destination 19:8,
/// stride - 1 in 29:22; pds_isa 3, [CAP/HW]).
pub fn dma_to_pa(mem: &Mem, run: &PdsRun) -> Result<Vec<(usize, u32)>, Outcome> {
    let mut pa = vec![];
    for &(addr, ctl) in &run.dma {
        let (burst, lines, dst, stride) =
            ((ctl & 15) + 1, (ctl >> 4 & 15) + 1, (ctl >> 8 & 0xfff) as usize, (ctl >> 22 & 0xff) + 1);
        if ctl >> 20 & 3 != 0 || ctl >> 30 != 0 {
            return Err(Outcome::unsupported(
                &format!("doutd control word {ctl:#010x} has bits no record reads"),
                &["Q050"],
            ));
        }
        for l in 0..lines {
            for b in 0..burst {
                let a = addr.wrapping_add(4 * (l * stride + b));
                let v = mem.read32(a)?;
                let at = dst + (l * burst + b) as usize;
                if at >= 128 {
                    return Err(Outcome::unsupported("a doutd past the 128 primary attributes", &["Q050"]));
                }
                pa.push((at, v));
            }
        }
    }
    Ok(pa)
}

/// Run the task a PDS run started on a machine whose attributes it filled, until the task hands its
/// outputs to the vertex cache; returns the machine (its `o`).
fn run_task(
    mem: &Mem,
    run: &PdsRun,
    pa: &[(usize, u32)],
    usev_base: u32,
    vertex: Option<(u32, u32, u32)>,
    what: &str,
) -> Result<Machine, Outcome> {
    let u0 = run
        .task
        .ok_or_else(|| Outcome::unsupported(&format!("{what}: the PDS program starts no task"), &["Q050"]))?
        [0];
    if u0 & 0xf != VERTEX_CODE_BASE {
        return Err(Outcome::unsupported(
            &format!(
                "{what}: the task starts from code base {} and the model knows the vertex heap's {VERTEX_CODE_BASE}",
                u0 & 0xf
            ),
            &["Q050"],
        ));
    }
    let words: Vec<u64> = (0..0x1000u32 / 4)
        .map_while(|i| Some((mem.read32(usev_base + 8 * i).ok()?, mem.read32(usev_base + 8 * i + 4).ok()?)))
        .map(|(lo, hi)| lo as u64 | (hi as u64) << 32)
        .collect();
    let prog = Program::new(&words, Core::Sgx545);
    let mut m = Machine {
        vertex,
        vertex_task: true,
        temps: (u0 >> 24) as usize * 4,
        pc: (u0 >> 4 & 0xffff) as usize,
        ..Machine::default()
    };
    for &(n, v) in pa {
        m.pa[n] = v;
        m.written.pa |= 1 << n;
    }
    match m.run(&prog, &mut ReadBus(mem), STEPS) {
        // the vertex cache emits end the part the model runs
        Err(Error::Unsupported { text, .. })
            if text.starts_with("emitvcbst") || text.starts_with("emitvcbvtx") =>
        {
            Ok(m)
        }
        Ok(()) => Err(Outcome::unsupported(
            &format!("{what}: the task ended without handing its outputs on"),
            &["Q050"],
        )),
        Err(e) => Err(refusal(e, what)),
    }
}

/// The outputs `o0..o17` of a state block's task: its PDS program DMAs the block into the
/// attributes and the USSE task copies them out.
pub fn state_outputs(mem: &Mem, pds: u32, data: u32, usev_base: u32) -> Result<Vec<u32>, Outcome> {
    let what = format!("the state block's task at {pds:#010x}");
    let run = run_pds(mem, pds, data, 0, true)?;
    let pa = dma_to_pa(mem, &run)?;
    let m = run_task(mem, &run, &pa, usev_base, None, &what)?;
    let n = pa.iter().map(|p| p.0 + 1).max().unwrap_or(0);
    Ok(m.o[..n].to_vec())
}

/// The clip-space position `o0..o3` of each vertex of a vertex task (vertex numbers `v` of a draw of
/// `total`, `per` a task): the PDS program per vertex, the USSE task per vertex.
pub fn vertex_outputs(
    mem: &Mem,
    pds: u32,
    data: u32,
    usev_base: u32,
    v: &[u32],
    per: u32,
    total: u32,
) -> Result<Vec<[u32; 4]>, Outcome> {
    let mut out = vec![];
    for (k, &i) in v.iter().enumerate() {
        let what = format!("vertex {i}");
        // (if0) starts the task once, on the task's last vertex
        let run = run_pds(mem, pds, data, i, k + 1 == v.len())?;
        let run = if k + 1 == v.len() { run } else { PdsRun { task: None, ..run } };
        let pa = dma_to_pa(mem, &run)?;
        // the task is shared by the vertices of the task: its u0 is the last vertex's
        let last = run_pds(mem, pds, data, *v.last().unwrap(), true)?;
        let m = run_task(
            mem,
            &PdsRun { dma: run.dma.clone(), task: last.task },
            &pa,
            usev_base,
            Some((i, per, total)),
            &what,
        )?;
        out.push([m.o[0], m.o[1], m.o[2], m.o[3]]);
    }
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::scene::Scene;

    const FIXTURE: &str = include_str!("../tests/fixtures/tri-baselines.scene.json");

    fn scene() -> (Scene, Mem) {
        let sc = Scene::from_fixture(FIXTURE, "tb-w128-k0-16-16");
        let mem = sc.load_mem().unwrap();
        (sc, mem)
    }

    fn layout(sc: &Scene, k: &str) -> u32 {
        sc.layout.iter().find(|(n, _)| n == k).unwrap().1
    }

    #[test]
    fn a_state_blocks_pds_program_dmas_the_block_and_the_task_copies_it_to_the_outputs() {
        let (sc, mem) = scene();
        let pdsv = layout(&sc, "pdsv");
        let o = state_outputs(&mem, pdsv + 0x40, 8, layout(&sc, "usev_base")).unwrap();
        let blk: Vec<u32> = (0..18).map(|i| mem.read32(pdsv + 0x100 + 4 * i).unwrap()).collect();
        assert_eq!(o, blk);
        assert_eq!(o[0], 0xdf43);
    }

    #[test]
    fn the_outputs_follow_the_memory_so_the_pipe_really_runs_the_programs() {
        let (sc, mut mem) = scene();
        let pdsv = layout(&sc, "pdsv");
        mem.write32(pdsv + 0x100 + 4 * 6, 0x1234_5678).unwrap();
        let o = state_outputs(&mem, pdsv + 0x40, 8, layout(&sc, "usev_base")).unwrap();
        assert_eq!(o[6], 0x1234_5678);
    }

    #[test]
    fn a_vertex_task_gives_each_vertex_its_four_dwords_by_its_index_times_the_stride() {
        let (sc, mut mem) = scene();
        let (gen_, pdsv) = (layout(&sc, "gen"), layout(&sc, "pdsv"));
        let v: Vec<u32> = (0..15).collect();
        let out = vertex_outputs(&mem, pdsv, 8, layout(&sc, "usev_base"), &v, 16, 15).unwrap();
        assert_eq!(out.len(), 15);
        for (i, o) in out.iter().enumerate() {
            let at = gen_ + 0x100 + 16 * i as u32;
            let want: Vec<u32> = (0..4).map(|k| mem.read32(at + 4 * k).unwrap()).collect();
            assert_eq!(&o[..], &want[..], "vertex {i}");
        }
        // the first vertex is (-0.75, -0.75, 0, 1) in clip space for the 128 x 128 job's (16, 16)
        assert_eq!(f32::from_bits(out[0][0]), -0.75);
        mem.write32(gen_ + 0x100 + 16 * 4 + 8, 0x3f00_0000).unwrap();
        let out = vertex_outputs(&mem, pdsv, 8, layout(&sc, "usev_base"), &v, 16, 15).unwrap();
        assert_eq!(out[4][2], 0x3f00_0000);
    }

    #[test]
    fn a_program_that_starts_a_task_from_another_code_base_is_refused() {
        let (sc, mut mem) = scene();
        let pdsv = layout(&sc, "pdsv");
        // the DOUTU word of the state block's PDS program is data dword 4: code base 10 -> 9
        let u0 = mem.read32(pdsv + 0x40 + 16).unwrap();
        mem.write32(pdsv + 0x40 + 16, u0 & !0xf | 9).unwrap();
        match state_outputs(&mem, pdsv + 0x40, 8, layout(&sc, "usev_base")) {
            Err(Outcome::Unsupported { why, .. }) => assert!(why.contains("code base"), "{why}"),
            r => panic!("{r:?}"),
        }
    }

    #[test]
    fn an_access_outside_the_scene_is_refused_under_the_flat_memory_questions() {
        let (sc, mem) = scene();
        match state_outputs(&mem, 0x1000_0000, 8, layout(&sc, "usev_base")) {
            Err(Outcome::Unsupported { ids, .. }) => assert!(ids.iter().any(|i| i == "Q076")),
            r => panic!("{r:?}"),
        }
    }
}
