// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The transfer job (12.1): a fill or a copy, as the EDM starts it and the units run it.
//!
//! What the model does, from what a record states: the 17 register words of the command (doc/
//! specs/transfer.md 3.2) give the render box in 32 x 16 tiles, the background object and the
//! pixel-event program; each tile of the box runs the pixel-event PDS program with ir0 =
//! tile_y << 10 | tile_x in the units E130 records (16 pixels across, 16 rows: the second 32-pixel
//! column of the box is tile_x 2) and ir1 = 2, or 6 on the last tile (E130, E265), which starts
//! the end-of-tile task (or the end-of-render task, E265), which stores the tile at the place its
//! U1's tile fields name in half-tile units (E876, E884); the shader of the background object's
//! primary PDS program runs for every pixel of the tile (the ISP covers whole tiles of the box:
//! the vertices do not clip, E069, E590; the PBE's rectangle does, E267), a copy's texel
//! coming from `tex::sample` at the iterated coordinates; the end-of-tile task's emit words
//! reach the PBE (`pbe`).
//!
//! Everything a record does not explain refuses, naming a question that depends only on the
//! scene's words, never on what the hardware did: a command word or task word with no record
//! (Q206), a PDS program or input the simulator
//! does not know (Q207), the iterator word (Q180), background object words (Q066), a copy's tag
//! (Q011), an access to memory the scene does not map or a job that cannot complete (Q076 and
//! Q003).
//!
//! Assumptions, none a fitted rule of a record. The programs' code is pinned by hash and any
//! program that is not a template the records ran refuses under Q207, so the assumptions are
//! confined to those three programs:
//! - `alu_specials_in_movs`: a `movs` reads `ir1.l` and `tim.l` as the ALU reads `ir1` and
//!   `tim`. Measured in a fill's secondary program and in the pixel-event program (pds_isa 8.9
//!   item 9, E263); assumed for the primary program, where only the baselines' image hashes
//!   support it (without it 24 of 13679 scenes match).
//! - `ifs` and `ir2` are not assumed: they are unknown inputs (if0 and if1 are open on SGX,
//!   pds_isa 3.2, and ir2 is measured only in `movs`), so a program that reads one refuses under
//!   Q207. None of the three template programs does (the replay is unchanged with them unknown).
//! - The builder's addresses (the target, a copy's source, the pages of the programs and the
//!   background object) are the mock's: the fill and copy sweeps print no layout line.
//!
//! One fitted rule: the place of a moved tile (`u1_place`, `rules::XFER_U1_PLACE`; E876 states
//! the fit, E884 held it out), so a scene whose tile moved is reported fitted.

pub mod population;

use crate::Outcome;
use crate::mem::Mem;
use crate::pbe::{self, Emit};
use crate::scene::{Scene, SceneResult};
use sgx_sim::pds::{self, Pds, Port};
use sgx_sim::{Bus, Error, Machine, Program, tex};
use usse_isa::Core;

/// What the harness fills the target with before a job.
pub const SENTINEL: u32 = 0xdead_beef;

/// The questions the model refuses under (the transfer's own; the units' are in their modules).
pub const OPEN: &[&str] = &["Q206", "Q207", "Q074", "Q011", "Q180", "Q066", "Q200", "Q300", "Q076", "Q003"];

/// The EOT and EOR task entries of the builder's use page (the transfer templates, 4 instructions
/// and 12 instructions in, with 4 and 1 temporaries: fw_format.md 9.2) as a PDS data word U0.
const U0_EOT: u32 = 0x0100_0040;
const U0_EOR: u32 = 0x0100_00c0;
/// The secondary program's task (a transfer has no per-tile secondary work).
const U0_SEC: u32 = 0x20;
/// Tiles of a render box the model runs at most (the words are 8 bits wide in the sweeps).
const MAX_TILES_PER_SIDE: u32 = 0x100;
pub(crate) const STEPS: usize = 100_000;
/// The pixel-event program's 29 instruction words (the transfer template, asm/transfer/
/// pds_pixevent.s) by FNV-1a 64: a program that moved, so that its data segment or code shifted,
/// is not the one the records ran.
pub(crate) const PIXEVENT_CODE_FNV: u64 = 0x39de_3648_7c33_127c;
pub(crate) const PIXEVENT_CODE_LEN: usize = 29;
/// The code of the secondary program (and of a fill's primary program): two words; a copy's
/// primary program has four (the transfer templates, asm/transfer). The assumptions listed in the
/// header hold for these programs only.
const SEC_CODE_FNV: u64 = 0x6a88_01ce_6437_f7a9;
const SEC_CODE_LEN: usize = 2;
const COPY_PRIMARY_CODE_FNV: u64 = 0x19f7_4eee_ce22_2fb4;
const COPY_PRIMARY_CODE_LEN: usize = 4;

fn refuse(why: impl AsRef<str>, ids: &[&str]) -> Outcome {
    Outcome::unsupported(why.as_ref(), ids)
}

type R<T> = Result<T, Outcome>;

/// The words of the command the model understands, read and checked.
#[derive(Debug, Clone, PartialEq)]
struct Cmd {
    bg: u32,
    layers: u32,
    pix_exec: u32,
    pix_rows: u32,
    pds_base: u32,
    box_min: (u32, u32),
    box_max: (u32, u32),
    reg0400: u32,
}

/// Fixed words of a fill and a copy (fw_format.md 9.5): index, value.
const FIXED: &[(usize, u32)] = &[
    (1, 0x200),
    (2, 0x3f80_0000),
    (3, 3),
    (4, 0),
    (5, 0x100),
    (7, 0x8000_0000),
    (8, 0x88),
    (10, 5),
    (11, 1),
    (16, 0),
];

fn layout(sc: &Scene, name: &str) -> R<u32> {
    sc.layout
        .iter()
        .find(|(k, _)| k == name)
        .map(|(_, a)| *a)
        .ok_or_else(|| refuse(format!("the scene's layout names no `{name}`"), &["Q206"]))
}

fn read_cmd(sc: &Scene) -> R<Cmd> {
    let w = &sc.xfer;
    if w.len() < 17 {
        return Err(refuse("a transfer scene without the 17 register words", &["Q206"]));
    }
    for &(i, v) in FIXED {
        if w[i] != v {
            return Err(refuse(
                format!(
                    "command word {i} (+{:#x}) is {:#x}, the fixed {v:#x}: no record says what it does",
                    4 * i,
                    w[i]
                ),
                &["Q206"],
            ));
        }
    }
    if let Some(i) = (17..w.len()).find(|&i| w[i] != 0) {
        return Err(refuse(format!("command word {i} (a coefficient group) is set"), &["Q206"]));
    }
    // the tag: the object's offset from the request base in 16-byte units [23:0] and the layer
    // count [30:25]; bits 24 and 30 read the source's last texel (E272, Q011)
    let hi = w[0] >> 24;
    if hi & 0x41 != 0 {
        return Err(refuse("tag bit 24 or 30: every pixel is the source's last texel (E272)", &["Q011"]));
    }
    if hi >> 1 > 1 || hi & 0x80 != 0 {
        return Err(refuse(format!("tag {:#x}: more than one layer or bit 31", w[0]), &["Q206"]));
    }
    let bg = w[6].wrapping_add(16 * (w[0] & 0xff_ffff));
    if bg != layout(sc, "bg")? {
        return Err(refuse("the tag and the request base do not name the builder's object", &["Q206"]));
    }
    let pds_base = w[15];
    if pds_base != layout(sc, "pds_page")? {
        return Err(refuse("the PDS execution base is not the page the programs were placed at", &["Q206"]));
    }
    let tiles = |v: u32| (v >> 16, v & 0xffff);
    let (box_min, box_max) = (tiles(w[12]), tiles(w[13]));
    for (a, b) in [(box_min.0, box_max.0), (box_min.1, box_max.1)] {
        if b < a || b >= MAX_TILES_PER_SIDE {
            return Err(refuse(
                format!(
                    "the render box {:#x}..{:#x} is empty or wider than {MAX_TILES_PER_SIDE} tiles",
                    w[12], w[13]
                ),
                &["Q206"],
            ));
        }
    }
    Ok(Cmd {
        bg,
        layers: hi >> 1,
        pix_exec: w[9],
        pix_rows: w[10],
        pds_base,
        box_min,
        box_max,
        reg0400: w[14],
    })
}

/// What a task and the PDS programs did on the bus, in order.
#[derive(Default)]
pub(crate) struct Events {
    pub(crate) tasks: Vec<[u32; 3]>,
    pub(crate) attrs: Vec<(usize, u32)>,
    pub(crate) iter: Vec<[u32; 2]>,
    pub(crate) tex: Vec<[u32; 4]>,
    pub(crate) emits: Vec<(String, [u32; 3])>,
}

struct MemBus<'a> {
    mem: &'a mut Mem,
    ev: Events,
}

fn unmapped(addr: u32) -> Error {
    Error::Fault(addr)
}

impl Bus for MemBus<'_> {
    fn load32(&mut self, addr: u32) -> Result<u32, Error> {
        self.mem.read32(addr).map_err(|_| unmapped(addr))
    }

    fn store32(&mut self, addr: u32, v: u32) -> Result<(), Error> {
        self.mem.write32(addr, v).map_err(|_| unmapped(addr))
    }

    fn emit(&mut self, text: &str, srcs: [u32; 3]) -> Result<(), Error> {
        self.ev.emits.push((text.to_string(), srcs));
        Ok(())
    }

    fn port(&mut self, port: Port, w: [u32; 4]) -> Result<(), Error> {
        let open = |why: String| Error::Unsupported { pc: 0, text: String::new(), why };
        match port {
            Port::Doutu => self.ev.tasks.push([w[0], w[1], w[2]]),
            Port::Douta => self.ev.attrs.push(((w[1] >> 8 & 0xfff) as usize, w[0])),
            Port::Douti => self.ev.iter.push([w[0], w[1]]),
            Port::Doutt => self.ev.tex.push(w),
            p => return Err(open(format!("a PDS program writes the {p:?} port"))),
        }
        Ok(())
    }
}

/// A simulator error as the refusal it is, by what the error says and never by what the hardware
/// did with the words: an access outside the scene's memory is the flat memory's (Q076, Q003); a
/// program that does not end or leaves its code is a job that cannot complete (Q003); what the
/// PDS simulator does not support is a PDS input or instruction no record measured (Q207); what
/// the USSE simulator does not support is a task word no record explains (Q206).
pub(crate) fn refusal(e: Error, what: &str, pds: bool) -> Outcome {
    match e {
        Error::Fault(a) => refuse(
            format!("{what}: access to unmapped address {a:#010x} (flat memory: no MMU model yet)"),
            &["Q076", "Q003"],
        ),
        Error::Unsupported { why, .. } => {
            refuse(format!("{what}: {why}"), if pds { &["Q207"] } else { &["Q206"] })
        }
        e => refuse(format!("{what}: {e}: the job's completion is not known"), &["Q003"]),
    }
}

/// The dwords from `addr` to the end of its mapped pages, at most `max`.
pub(crate) fn words(mem: &Mem, addr: u32, max: usize) -> Vec<u32> {
    (0..max as u32).map_while(|i| mem.read32(addr.wrapping_add(4 * i)).ok()).collect()
}

/// Whether the `len` code dwords after a program's `data` dwords hash to `want`.
fn code_is(mem: &Mem, prog: (u32, usize), len: usize, want: u64) -> bool {
    let w = words(mem, prog.0, prog.1 + len);
    w.len() == prog.1 + len && fnv(&w[prog.1..]) == want
}

/// The program is one of the templates the records ran: the assumptions of the header hold for
/// those and for no other program, so any other refuses (Q207).
fn pin_code(mem: &Mem, prog: (u32, usize), fits: &[(usize, u64)], what: &str) -> R<()> {
    if fits.iter().any(|&(len, want)| code_is(mem, prog, len, want)) {
        return Ok(());
    }
    Err(refuse(
        format!("{what}'s code is not a template the records ran: the PDS inputs are assumed for those only"),
        &["Q207"],
    ))
}

/// Run a PDS program at `addr` with `data` dwords of data.
pub(crate) fn run_pds(mem: &mut Mem, addr: u32, data: usize, pds: &mut Pds, what: &str) -> R<Events> {
    let w = words(mem, addr, data + 256);
    if w.len() < data {
        return Err(refusal(Error::Fault(addr), what, true));
    }
    let prog = pds::Program::new(&w, data);
    let mut bus = MemBus { mem, ev: Events::default() };
    pds.run(&prog, &mut bus, STEPS).map_err(|e| refusal(e, what, true))?;
    Ok(bus.ev)
}

/// Run the USSE task `u0` of the program decoded from the code base for one instance.
pub(crate) fn run_task(
    mem: &mut Mem,
    prog: &Program,
    u0: u32,
    mut m: Machine,
    what: &str,
) -> R<(Machine, Events)> {
    if u0 & 0xf != 0 {
        return Err(refuse(format!("{what}: code base register {} is not modelled", u0 & 0xf), &["Q206"]));
    }
    m.temps = (u0 >> 24) as usize * 4;
    m.pc = (u0 >> 4 & 0xffff) as usize;
    let mut bus = MemBus { mem, ev: Events::default() };
    m.run(prog, &mut bus, STEPS).map_err(|e| refusal(e, what, false))?;
    Ok((m, bus.ev))
}

/// What the primary PDS program started for each pixel: the shader's attributes (the texel of a
/// copy comes with each pixel) and the texture state.
struct Primary {
    tex: Option<[u32; 4]>,
}

pub(crate) fn fnv(w: &[u32]) -> u64 {
    crate::scene::fnv64(w)
}

fn f32_of(w: u32) -> f64 {
    f32::from_bits(w) as f64
}

/// The 80-bit vertices of the background object from dword 15 of a copy: Y then X, 24 bits each
/// (8 fraction bits, offset 4096), then 32 zero bits (transfer.md 4.2).
pub(crate) fn vertices(bg: &[u32], at: usize) -> Option<[(f64, f64); 3]> {
    let bit = |pos: usize, n: usize| -> Option<u64> {
        let mut v = 0u64;
        for i in 0..n {
            let b = pos + i;
            v |= ((*bg.get(at + b / 32)? as u64 >> (b % 32)) & 1) << i;
        }
        Some(v)
    };
    let mut out = [(0.0, 0.0); 3];
    for (k, o) in out.iter_mut().enumerate() {
        let (y, x) = (bit(80 * k, 24)?, bit(80 * k + 24, 24)?);
        *o = (x as f64 / 256.0 - 4096.0, y as f64 / 256.0 - 4096.0);
    }
    Some(out)
}

/// A copy's iterated (u, v) at the centre of pixel (x, y): the plane through the three
/// vertices' normalised coordinates, evaluated exactly (E048: the iterators agree with the exact
/// iteration to 1.2e-7); a degenerate triangle has no plane (Q200, the iterators' arithmetic).
pub(crate) fn uv(bg: &[u32], x: u32, y: u32) -> R<(f32, f32)> {
    let v = vertices(bg, 15).ok_or_else(|| refuse("the background object is too short", &["Q066"]))?;
    let (u0, u1, u2) =
        ((f32_of(bg[3]), f32_of(bg[4])), (f32_of(bg[5]), f32_of(bg[6])), (f32_of(bg[7]), f32_of(bg[8])));
    let det = (v[1].0 - v[0].0) * (v[2].1 - v[0].1) - (v[2].0 - v[0].0) * (v[1].1 - v[0].1);
    if det == 0.0 {
        return Err(refuse("the background object's triangle has no area", &["Q200"]));
    }
    let (px, py) = (x as f64 + 0.5, y as f64 + 0.5);
    let l1 = ((px - v[0].0) * (v[2].1 - v[0].1) - (v[2].0 - v[0].0) * (py - v[0].1)) / det;
    let l2 = ((v[1].0 - v[0].0) * (py - v[0].1) - (px - v[0].0) * (v[1].1 - v[0].1)) / det;
    Ok((
        (u0.0 + l1 * (u1.0 - u0.0) + l2 * (u2.0 - u0.0)) as f32,
        (u0.1 + l1 * (u1.1 - u0.1) + l2 * (u2.1 - u0.1)) as f32,
    ))
}

/// The LOD of a copy's texel fetch. No record gives the pixel side's LOD; on the identity plane
/// (the unit square over the target's rectangle, one texel a pixel) it is level 0, as the 1:1
/// copies are. On any other plane it is open: the texture unit then reads level 0 only where the
/// texture's state does not depend on it (stride textures) and refuses otherwise.
pub(crate) fn lod_of(bg: &[u32]) -> tex::Lod {
    let unit = [0.0f32, 0.0, 1.0, 0.0, 0.0, 1.0];
    if bg[3..9].iter().zip(unit).all(|(&c, u)| c == u.to_bits()) {
        tex::Lod::Value(0.0)
    } else {
        tex::Lod::Open("a copy off the identity plane: the pixel side's LOD is not recorded")
    }
}

struct Job {
    mem: Mem,
    cmd: Cmd,
    code: Program,
    bg: Vec<u32>,
    /// the address ranges the scene's memory holds (what the builder placed, not the target)
    segments: Vec<(u32, u32)>,
    prim: Primary,
    /// a tile was stored at another place than its own (`u1_place`, a fitted rule)
    moved: bool,
}

impl Job {
    /// The 32 x 16 colours the shader writes for tile (tx, ty), one instance a pixel.
    fn shade(&mut self, tile: (u32, u32)) -> R<Vec<u32>> {
        let mut out = Vec::with_capacity(512);
        for j in 0..16 {
            for i in 0..32 {
                let (x, y) = (32 * tile.0 + i, 16 * tile.1 + j);
                let mut m = Machine { pixel: Some((x, y)), ..Machine::default() };
                if let Some(state) = self.prim.tex {
                    let lod = lod_of(&self.bg);
                    let (u, v) = uv(&self.bg, x, y)?;
                    let s = tex::Sample { state, u, v, one_d: false, srd: tex::Srd::None, pcf: None, lod };
                    let (mem, segs) = (&self.mem, &self.segments);
                    let r = tex::sample(&s, &mut |a| {
                        // the target's pages hold the sentinel the harness wrote and whatever the
                        // tiles stored so far: a read there depends on the hardware's order
                        if !segs.iter().any(|&(b, e)| a >= b && a < e) {
                            return Err(Error::Fault(a));
                        }
                        mem.read32(a).map_err(|_| Error::Fault(a))
                    })
                    .map_err(|f| match f {
                        tex::Fail::Open(w) => refuse(format!("texture sample: {w}"), &["Q300"]),
                        tex::Fail::Load(e) => refusal(e, "texture read", false),
                    })?;
                    m.pa[0] = *r.first().ok_or_else(|| refuse("an empty texture sample", &["Q300"]))?;
                    m.written.pa |= 1;
                }
                let (m, _) = run_task(&mut self.mem, &self.code, 0, m, "the pixel shader")?;
                if m.written.o & 1 == 0 {
                    return Err(refuse("the pixel shader did not write o0", &["Q206"]));
                }
                out.push(m.o[0]);
            }
        }
        Ok(out)
    }
}

/// ir0 of the pixel-event program for the tile (column, row) of the box: tile_y << 10 | tile_x,
/// in the units of E130 (16 pixels across, 16 rows): a 32-pixel column is two tile_x.
fn ir0_of(tile: (u32, u32)) -> u32 {
    tile.1 << 10 | (tile.0 << 1)
}

/// The tile fields of the end-of-tile task's U1 that the pixel-event program builds from ir0 with
/// the masks 0xff8 and 0x3ff000 of its data (dwords 9 and 13) after `ir0 << 3`: x in bits 11:3
/// (2 for the second 32-pixel column, the fact of E620 and E130's unit) and y in bits 21:12; the
/// place they name is the tile itself (`u1_place`).
#[cfg(test)]
fn u1_tile_fields(tile: (u32, u32)) -> u32 {
    let ir0 = ir0_of(tile);
    (ir0 << 3 & 0xff8) | (ir0 << 3 & 0x3f_f000)
}

/// The place, in 32 x 16 tiles, where the end-of-tile task with this U1 stores its tile: the x field
/// (bits 11:3) and the y field (bits 21:12) read in half-tile units (16 pixels, 8 rows), so a
/// field's bit 0 changes nothing. Read on the kept sweeps of the fill (E876, post hoc) and held
/// out at 128 x 64 and 256 x 32 (E884: OR of the poked word into the tile's own field, which is
/// the pixel-event program's own arithmetic here, 20 of 20); E126's XOR into the fields on a
/// 128 x 128 render moves whole tiles the same way. A place past the target is cut by the PBE's
/// rectangle (`pbe::store_tile`), so nothing is stored there, as every one of those jobs showed.
/// With both fields moved at once each axis is placed by its own field, independently (E909, held
/// out at 128 x 64, 8 of 8; only one field acting was refuted).
fn u1_place(u1: u32) -> (u32, u32) {
    ((u1 >> 3 & 0x1ff) >> 1, (u1 >> 12 & 0x3ff) >> 1)
}

/// Run a transfer scene.
pub fn run(sc: &Scene) -> SceneResult {
    match run_inner(sc) {
        Ok(r) => r,
        Err(o) => SceneResult::refusing(o),
    }
}

fn run_inner(sc: &Scene) -> R<SceneResult> {
    let cmd = read_cmd(sc)?;
    let mut mem = Mem::new();
    for s in &sc.memory {
        let d = s
            .dwords
            .as_ref()
            .ok_or_else(|| refuse("a memory segment held as a file is not loaded yet", &["Q206"]))?;
        mem.load(s.base, d)?;
    }
    let t = &sc.target;
    if t.stride == 0 || t.pages == 0 {
        return Err(refuse("the scene's target has no stride or pages", &["Q206"]));
    }
    mem.map(t.base, t.pages * 4096);
    for i in 0..t.pages * 1024 {
        mem.write32(t.base + 4 * i, SENTINEL)?;
    }
    let use_page = layout(sc, "use_page")?;
    let code = Program::new(
        &words(&mem, use_page, 0x8000)
            .chunks_exact(2)
            .map(|d| d[0] as u64 | (d[1] as u64) << 32)
            .collect::<Vec<_>>(),
        Core::Sgx545,
    );
    // the background object's first three words and the two PDS programs it names
    let bg = words(&mem, cmd.bg, 23);
    if bg.len() < 23 {
        return Err(refusal(Error::Fault(cmd.bg), "the background object", false));
    }
    let prog_at = |w: u32| (cmd.pds_base.wrapping_add(16 * (w & 0x03ff_ffff)), (w >> 26) as usize * 4);
    let (sec, pri) = (prog_at(bg[0]), prog_at(bg[2]));
    let pds = |ir: [u32; 2]| Pds {
        ir: [Some(ir[0]), Some(ir[1]), None],
        ifs: [None; 2],
        alu_specials_in_movs: true,
        ..Pds::default()
    };
    pin_code(&mem, sec, &[(SEC_CODE_LEN, SEC_CODE_FNV)], "the secondary program")?;
    pin_code(
        &mem,
        pri,
        &[(SEC_CODE_LEN, SEC_CODE_FNV), (COPY_PRIMARY_CODE_LEN, COPY_PRIMARY_CODE_FNV)],
        "the primary program",
    )?;
    // the secondary program starts the one task that ends
    let ev = run_pds(&mut mem, sec.0, sec.1, &mut pds([0, 0]), "the secondary program")?;
    if ev.tasks.len() != 1 || ev.tasks[0] != [U0_SEC, 4, 0] || !ev.attrs.is_empty() {
        return Err(refuse("the secondary program does not start the template's one task", &["Q207"]));
    }
    run_task(&mut mem, &code, U0_SEC, Machine::default(), "the secondary task")?;
    // the primary: the shader, and for a copy the iterator word and the texture's four words
    let ev = run_pds(&mut mem, pri.0, pri.1, &mut pds([0, 0]), "the primary program")?;
    let tex = ev.tex.first().copied();
    let expect_u1 = if tex.is_some() { 0x0200_0004 } else { 4 };
    if ev.tasks.len() != 1
        || ev.tasks[0] != [0, expect_u1, 0]
        || ev.tex.len() != tex.is_some() as usize
        || !ev.attrs.is_empty()
    {
        return Err(refuse("the primary program is not the template's shader start", &["Q207"]));
    }
    if tex.is_some() && ev.iter != [[0x4001_2001, 0]] || tex.is_none() && !ev.iter.is_empty() {
        return Err(refuse("the iterator word is not the template's one fetch of layer 0", &["Q180"]));
    }
    // the object's remaining words: the attribute count follows the texture, word 10 changes
    // nothing (E069), a fill's words 3 to 16 change nothing (E069), a copy's coordinates and
    // vertices are read
    let layers = tex.is_some() as u32;
    if cmd.layers != layers {
        return Err(refuse("the tag's layer count is not the primary program's", &["Q011"]));
    }
    if bg[1] != 0x3_0000 | layers {
        return Err(refuse("background object word 1 is not the template's", &["Q066"]));
    }
    if layers == 1 && [9, 11, 12, 13, 14].iter().any(|&i| bg[i] != 0) {
        return Err(refuse("a copy's background object words 9, 11 to 14 are set", &["Q066"]));
    }
    // E069 swept the two low bytes of word 10: the high half is not known to change nothing
    if layers == 1 && bg[10] >> 16 != 0 {
        return Err(refuse("a copy's background object word 10 has bits 31:16 set", &["Q066"]));
    }
    // the iterated coordinates are modelled for the plane of the whole-target rectangle with
    // finite coordinates; any other triangle is the iterators' arithmetic (Q200)
    if layers == 1 {
        let (w, h) = (sc.target.w as f64, sc.target.h as f64);
        let v = vertices(&bg, 15);
        let rect = v.is_some_and(|v| v == [(0.0, 0.0), (w, 0.0), (0.0, h)]);
        if !rect || bg[3..9].iter().any(|&c| !f32::from_bits(c).is_finite()) {
            return Err(refuse(
                "a copy's vertices are not the target's rectangle or a coordinate is not finite",
                &["Q200"],
            ));
        }
    }
    let segments = sc
        .memory
        .iter()
        .map(|s| (s.base, s.base + 4 * s.dwords.as_ref().map_or(0, |d| d.len() as u32)))
        .collect();
    let mut job = Job { mem, cmd, code, bg, segments, prim: Primary { tex }, moved: false };
    let mut tiles = vec![];
    for ty in job.cmd.box_min.1..=job.cmd.box_max.1 {
        for tx in job.cmd.box_min.0..=job.cmd.box_max.0 {
            tiles.push((tx, ty));
        }
    }
    let last = tiles.len() - 1;
    {
        // the program the records ran, from the address the command names
        let w = words(&job.mem, job.cmd.pix_exec, job.cmd.pix_rows as usize * 4 + PIXEVENT_CODE_LEN);
        let data = job.cmd.pix_rows as usize * 4;
        if w.len() < data + PIXEVENT_CODE_LEN || fnv(&w[data..data + PIXEVENT_CODE_LEN]) != PIXEVENT_CODE_FNV
        {
            return Err(refuse("the pixel-event program's code is not the template's", &["Q207"]));
        }
        // the masks that build U1's tile fields from ir0 (data dwords 9 and 13) are data the
        // program runs on: what U1 they give is the program's, where it stores is `u1_place`
    }
    for (n, &(tx, ty)) in tiles.iter().enumerate() {
        let ir0 = ir0_of((tx, ty));
        let ir1 = if n == last { 6 } else { 2 };
        let ev = run_pds(
            &mut job.mem,
            job.cmd.pix_exec,
            job.cmd.pix_rows as usize * 4,
            &mut pds([ir0, ir1]),
            "the pixel-event program",
        )?;
        // every tile event starts one task: whether a job completes when a tile starts none (or
        // two) is not in the records, so the job's completion is refused (Q003)
        if ev.tasks.len() != 1 {
            return Err(refuse(
                format!(
                    "the pixel-event program started {} tasks for tile ({tx}, {ty}): the job's completion is not known",
                    ev.tasks.len()
                ),
                &["Q003"],
            ));
        }
        for &[u0, u1, _u2] in &ev.tasks {
            match u0 {
                U0_EOR => {
                    run_task(&mut job.mem, &job.code, u0, Machine::default(), "the end-of-render task")?;
                }
                U0_EOT => job.end_of_tile((tx, ty), n == last, u1, &ev.attrs)?,
                _ => return Err(refuse(format!("the pixel-event program starts a task {u0:#x}"), &["Q206"])),
            }
        }
    }
    let mut res = SceneResult::refusing(Outcome::Ok);
    if job.moved {
        res.use_rule(crate::rules::XFER_U1_PLACE);
    }
    let mut image = Vec::with_capacity((t.w * t.h) as usize);
    for y in 0..t.h {
        for x in 0..t.w {
            image.push(job.mem.read32(t.base + y * t.stride + 4 * x)?);
        }
    }
    let mut outside = 0u64;
    for i in 0..t.pages * 1024 {
        let (row, col) = (i / (t.stride / 4), i % (t.stride / 4));
        let inside = row < t.h && col < t.w;
        if !inside && job.mem.read32(t.base + 4 * i)? != SENTINEL {
            outside += 1;
        }
    }
    res.image = Some(image);
    res.outside = Some(outside);
    Ok(res)
}

impl Job {
    fn end_of_tile(&mut self, tile: (u32, u32), last: bool, u1: u32, attrs: &[(usize, u32)]) -> R<()> {
        // U1 = base | tile_x | tile_y | end-of-render: the tile is stored at the place its fields
        // name (E876, E884: the loop's own tile unless the program's words moved it); each axis by
        // its own field, also when both move at once (E909)
        let place = u1_place(u1);
        self.moved |= place != tile;
        // the last tile (ir1 bit 2) ends the render: without bit 22 in its U1 no record says
        // whether the job completes (Q003)
        if last && u1 & 0x40_0000 == 0 {
            return Err(refuse(
                "the last tile's end-of-tile task does not end the render: the job's completion is not known",
                &["Q003"],
            ));
        }
        if u1 & !(0x3f_fff8 | 0x40_0000) != 0x80_0000 {
            return Err(refuse(
                format!("the end-of-tile task's U1 {u1:#x} has bits no record explains"),
                &["Q206"],
            ));
        }
        let mut m = Machine::default();
        for &(n, v) in attrs {
            if n >= 128 {
                return Err(refuse("a PDS attribute past 127", &["Q206"]));
            }
            m.pa[n] = v;
            m.written.pa |= 1 << n;
        }
        let (_, ev) = run_task(&mut self.mem, &self.code, U0_EOT, m, "the end-of-tile task")?;
        let side = |t: &str| t.rsplit("#0x").next().and_then(|h| u32::from_str_radix(h.trim(), 16).ok());
        match &ev.emits[..] {
            [(a, s1), (b, s2)] if a.starts_with("emitpix1") && b.starts_with("emitpix2") => {
                let sideband =
                    side(b).ok_or_else(|| refuse("the emit's sideband is not an immediate", &["Q054"]))?;
                let e = Emit { words: [s1[0], s1[1], s2[0], s2[1]], sideband };
                let colours = self.shade(tile)?;
                pbe::store_tile(&e, self.cmd.reg0400, place, &colours, &mut self.mem)
            }
            _ => Err(refuse("the end-of-tile task does not emit once as the template does", &["Q054"])),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_lod_is_level_0_on_the_identity_plane_only_and_open_elsewhere() {
        let mut bg = vec![0u32; 23];
        bg[5] = 1.0f32.to_bits();
        bg[8] = 1.0f32.to_bits();
        assert_eq!(lod_of(&bg), tex::Lod::Value(0.0));
        bg[5] = 2.0f32.to_bits();
        assert!(matches!(lod_of(&bg), tex::Lod::Open(_)));
        bg[5] = 1.0f32.to_bits();
        bg[3] = 0.5f32.to_bits();
        assert!(matches!(lod_of(&bg), tex::Lod::Open(_)), "an offset plane is not the identity");
    }

    #[test]
    fn a_pds_program_is_accepted_only_if_its_code_hashes_to_a_template_the_records_ran() {
        // 4 data dwords and the secondary template's two code words, then the same with one code
        // bit changed: whatever the simulator would do with it, the program is not the assumed one
        let mut m = Mem::new();
        m.load(0x1000, &[0, 4, 0, 0, 0x0700_0305, 0xaf00_0000]).unwrap();
        m.load(0x2000, &[0, 4, 0, 0, 0x0700_0304, 0xaf00_0000]).unwrap();
        let fits = [(SEC_CODE_LEN, SEC_CODE_FNV)];
        assert!(pin_code(&m, (0x1000, 4), &fits, "p").is_ok());
        let Err(Outcome::Unsupported { ids, .. }) = pin_code(&m, (0x2000, 4), &fits, "p") else {
            panic!("a changed code word was accepted")
        };
        assert_eq!(ids, ["Q207"]);
        // a program that ends before its code is not one either
        m.load(0x3000, &[0, 4]).unwrap();
        assert!(pin_code(&m, (0x3000, 2), &fits, "p").is_err());
    }

    #[test]
    fn ir0_counts_tile_x_in_16_pixels_as_e130_records() {
        // E130: tile_y << 10 | tile_x, tile_x 0 or 1 on a 32-pixel-wide render and tile_y up to 255 on
        // 4096 rows: a 32 x 16 tile of the box is two tile_x wide and one tile_y high
        assert_eq!(ir0_of((0, 0)), 0);
        assert_eq!(ir0_of((1, 0)), 2);
        assert_eq!(ir0_of((0, 1)), 1 << 10);
        assert_eq!(ir0_of((3, 255)), 255 << 10 | 6);
    }

    #[test]
    fn the_second_column_has_bit_4_of_the_x_field_as_the_e620_fact() {
        // E620: with bit 4 of the x mask cleared the second column of the 64x32 fill is
        // unwritten, so that column's U1 carries bit 4 (x field 2 in bits 11:3)
        assert_eq!(u1_tile_fields((0, 0)), 0);
        assert_eq!(u1_tile_fields((1, 0)), 0x10);
        assert_eq!(u1_tile_fields((0, 1)), 2 << 12);
    }

    #[test]
    fn a_u1_names_its_place_in_half_tile_units_and_the_programs_own_fields_name_the_tile() {
        // E876, E884: field bit 0 is half a tile; the template's fields name the loop's tile
        for t in [(0, 0), (1, 0), (0, 1), (3, 255), (255, 7)] {
            assert_eq!(u1_place(0x80_0000 | u1_tile_fields(t)), t);
        }
        // the 64 x 32 fill's second column with x ^ 0x10 (field 3) stores at column 1 under OR,
        // the first column with x | 0x10 (field 2) too, and field 1 changes nothing
        assert_eq!(u1_place(0x10 | 0x10), (1, 0));
        assert_eq!(u1_place(0x08), (0, 0));
        assert_eq!(u1_place(0x18), (1, 0));
        // E884's 128 x 64 x ^ 0x20 (field 4 = two tiles): column 1 stores at place 3
        assert_eq!(u1_place(0x10 | 0x20), (3, 0));
        assert_eq!(u1_place(0x3_f000 | 0x2000), (0, 31));
    }
}
