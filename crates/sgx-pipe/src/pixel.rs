// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The pixel side of a render job (12.3): the ISP over the objects the TA wrote (`objects`,
//! `isp`), the pixel programs of the winning object and of the background object through `sgx-sim`
//! (the PDS primary and secondary programs, then the USSE task of each pixel), the pixel-event
//! program and the end-of-tile task of each tile, and the PBE (`pbe`): the image, and the depth
//! where the job stores it. The library's scenes only: every command word the model does not read
//! is checked against what the library writes and refused (Q231, Q085) when it differs; what the
//! iterators would deliver is refused (a pixel program that reads a pa register no one wrote stops
//! the simulator: Q180).

use crate::Outcome;
use crate::isp::{self, Listed, Mode};
use crate::mem::Mem;
use crate::objects::{self, Object};
use crate::pbe::{self, Emit};
use crate::scene::Scene;
use crate::ta;
use crate::xfer::{PIXEVENT_CODE_FNV, PIXEVENT_CODE_LEN, SENTINEL, fnv, run_pds, run_task, words};
use sgx_sim::pds::Pds;
use sgx_sim::{Machine, Program};
use usse_isa::Core;

type R<T> = Result<T, Outcome>;

fn open(why: impl AsRef<str>, ids: &[&str]) -> Outcome {
    Outcome::unsupported(why.as_ref(), ids)
}

// the render command's words (`drm_sgxfive_render_cmd` order)
const C_MTE_MS: usize = 10;
const C_PIXELBE: usize = 11;
const C_CTL: usize = 12;
const C_AA3D: usize = 13;
const C_BGDEPTH: usize = 14;
const C_BGOBJ: usize = 15;
const C_ISP_MS: usize = 16;
const C_TSP: usize = 17;
const C_EV_EXEC: usize = 18;
const C_EV_ROWS: usize = 19;
const C_EV_INFO: usize = 20;
const C_FPU: usize = 21;
const C_DEPTHSORT: usize = 22;
const C_BG: usize = 23;
/// The command words this side reads, checks or runs: 10 to 25 (the background object's three
/// pixel PDS words are 23 to 25). `render` refuses the words of that range that no one reads, so
/// it leaves these to `check_cmd` and the shader runs.
pub const READS: std::ops::Range<usize> = C_MTE_MS..C_BG + 3;

/// Where the library puts its programs, as offsets inside the pixel PDS and USSE pages
/// (sgxfive_render.h): the pixel-event program, and the end-of-tile and end-of-render tasks.
const PP_PIXEV: u32 = 0x80;
const UP_EOT: u32 = 0x40;
const UP_EOR: u32 = 0x80;

/// A task word U0 for the code at `off` bytes into the page with `temps` temporaries
/// (sgxfive_tri_doutu).
fn doutu(off: u32, temps: u32) -> u32 {
    ((off << 1) & 0xffff0) | temps.div_ceil(4) << 24
}

/// CR_ZLS control: what a depth store through E465's layout needs (3d.md 11.5): the stores on,
/// the depth stored as float32, the stencil not; the pitch G in bits 11:3 is free.
const ZLS_BASE_PATTERN: u32 = 0x0017_1004;
pub const REG_ZLSCTL: u32 = 0x0480;
pub const REG_ZSTORE: u32 = 0x0488;

/// What a job's pixel side produced.
#[derive(Debug, Clone, PartialEq)]
pub struct Image {
    pub pixels: Vec<u32>,
    /// dwords of the target's buffer outside the rectangle that the job changed
    pub outside: u64,
    pub depth: Option<Result<Depth, Outcome>>,
}

/// The depth of every pixel of the target as the model has it: the plane's value and the
/// tolerance in units of 2^-23 (E606), or None where no tolerance is known.
#[derive(Debug, Clone, PartialEq)]
pub struct Depth {
    pub w: u32,
    pub h: u32,
    pub g: u32,
    pub value: Vec<f64>,
    pub tol: Vec<Option<u32>>,
}

fn layout(sc: &Scene, k: &str) -> R<u32> {
    sc.layout
        .iter()
        .find(|(n, _)| n == k)
        .map(|p| p.1)
        .ok_or_else(|| open(format!("{}: the scene's layout has no `{k}`", sc.id), &["Q206"]))
}

/// The pixel side's command words are the library's or refused.
fn check_cmd(sc: &Scene, pdsp: u32) -> R<()> {
    let c = &sc.cmd;
    if c.len() < 26 {
        return Err(open(format!("{}: a render scene needs its 26 command words", sc.id), &["Q206"]));
    }
    let want = [
        (C_MTE_MS, 0x88, "Q202"),
        (C_ISP_MS, 0x88, "Q202"),
        (C_PIXELBE, 0x80, "Q231"),
        (C_AA3D, 0x8000_0000, "Q202"),
        (C_BGOBJ, 0x300, "Q066"),
        (C_TSP, 0x30, "Q231"),
        (C_FPU, 1, "Q231"),
        (C_DEPTHSORT, 0x100, "Q231"),
        (C_EV_ROWS, 5, "Q206"),
        (C_EV_INFO, 1, "Q206"),
    ];
    for (i, v, q) in want {
        if c[i] != v {
            return Err(open(
                format!(
                    "command word {i} is {:#x}, the library's {v:#x}: no record says what else it does",
                    c[i]
                ),
                &[q],
            ));
        }
    }
    // CR_ISP_CTL: bit 8 (process empty tiles) and bits 19:16 as the library sets them, bits 5:0 free (E232)
    if c[C_CTL] & !0x3f != 0x000f_0100 {
        return Err(open(
            format!("CR_ISP_CTL {:#x}: only the library's bits are modelled", c[C_CTL]),
            &["Q085"],
        ));
    }
    if c[C_EV_EXEC] != (pdsp + PP_PIXEV) & !0xf {
        return Err(open("the pixel-event program is not at the library's place", &["Q206"]));
    }
    let d = f32::from_bits(c[C_BGDEPTH]);
    if !d.is_finite() || !(0.0..=1.0).contains(&d) {
        return Err(open("the background object's depth is not a float in [0, 1]", &["Q066"]));
    }
    Ok(())
}

/// A pixel PDS program pair (secondary, primary) from the three words of a pixel object
/// (E306): run once, giving the task the primary starts for every pixel.
struct Shader {
    u0: u32,
}

struct Ctx {
    mem: Mem,
    code: Program,
    /// the code page's instructions, as the decoder reads them
    words: Vec<u64>,
    pds_base: u32,
}

/// Whether a pixel program from instruction `pc` writes a pixel output, stores or emits with an
/// instruction that lacks `.skipinv` (E104, E111, E113): such an instruction also runs for the
/// helper instances of a partly covered quad, and whether their o0 lands varies from run to run
/// (Q052). The scan runs through the program's phases up to the `.end` of the last one (a `phas`
/// whose next-phase mode is `end`). A branch refuses: in a quad whose instances disagree the
/// branch is taken as one instance, chosen by the phase mode (E112), and the per-pixel run
/// cannot say which (Q050).
fn helper_sensitive(words: &[u64], pc: usize) -> Result<bool, Outcome> {
    let (mut sensitive, mut last_phase) = (false, false);
    for &w in words.iter().skip(pc).take(0x200) {
        let text = usse_isa::decode(w, Core::Sgx545).text;
        let mut toks = text.split_whitespace();
        let mut mnem = toks.next().unwrap_or("");
        if mnem.starts_with('p') && mnem.len() == 2 || mnem.starts_with("!p") {
            mnem = toks.next().unwrap_or("");
        }
        let base = mnem.split('.').next().unwrap_or("");
        if base == "phas" {
            // "phas #t, #n, pixel, <next>, <mode>": the fourth operand names the next phase
            last_phase = text.split(',').nth(3).is_some_and(|t| t.trim() == "end");
        }
        let dest = toks.next().unwrap_or("").trim_end_matches(',');
        if base == "br" || base == "bra" || base == "lapc" {
            return Err(open(
                "a pixel program with a branch: in a quad whose instances disagree it is taken as one instance, picked by the phase mode (E112); not modelled",
                &["Q050"],
            ));
        }
        let outputs =
            dest.starts_with('o') && dest.len() > 1 && dest[1..].chars().all(|c| c.is_ascii_digit());
        let side = base.starts_with("st") || base.starts_with("emit") || base == "ldad";
        if (outputs || side) && !mnem.split('.').any(|m| m == "skipinv") {
            sensitive = true;
        }
        if mnem.split('.').any(|m| m == "end") && last_phase {
            return Ok(sensitive);
        }
    }
    Err(open("a pixel program with no last .end within 512 instructions", &["Q052"]))
}

/// The library's colour write (probes/isp pix_green.s): one phase, then `mov.end o0, #0xFF00FF00`
/// with or without `.skipinv` (the plain form is the helper-instance probe's). E065 ran the pass
/// types 1, 2, 4, 5 and 6 with this shader only.
pub const COLOUR_PHASE: u64 = 0xfa44_0700_0000_0000;
pub const COLOUR_WRITE: [u64; 2] = [0xfca7_f181_0000_ff00, 0xfc27_f181_0000_ff00];

fn is_colour_write(words: &[u64], pc: usize) -> bool {
    matches!(words.get(pc..pc + 2), Some([p, w]) if *p == COLOUR_PHASE && COLOUR_WRITE.contains(w))
}

impl Ctx {
    fn prog_at(&self, w: u32) -> (u32, usize) {
        (self.pds_base.wrapping_add(16 * (w & 0x03ff_ffff)), (w >> 26) as usize * 4)
    }

    /// Run the secondary and primary programs of an object's three pixel PDS words.
    fn shader(&mut self, w: [u32; 3], what: &str) -> R<Shader> {
        if w[1] >> 16 != 3 {
            return Err(open(format!("{what}: size word {:#x} is not the library's", w[1]), &["Q066"]));
        }
        let pds = |ir: [u32; 2]| Pds {
            ir: [Some(ir[0]), Some(ir[1]), Some(0)],
            ifs: [Some(false); 2],
            alu_specials_in_movs: true,
            ..Pds::default()
        };
        let (sec, pri) = (self.prog_at(w[0]), self.prog_at(w[2]));
        let ev = run_pds(
            &mut self.mem,
            sec.0,
            sec.1,
            &mut pds([0, 0]),
            &format!("{what}: the secondary program"),
        )?;
        if ev.tasks.len() != 1 || !ev.attrs.is_empty() {
            return Err(open(format!("{what}: the secondary program does not start one task"), &["Q206"]));
        }
        run_task(&mut self.mem, &self.code, ev.tasks[0][0], Machine::default(), "the secondary task")?;
        let ev =
            run_pds(&mut self.mem, pri.0, pri.1, &mut pds([0, 0]), &format!("{what}: the primary program"))?;
        if ev.tasks.len() != 1 || !ev.attrs.is_empty() || !ev.tex.is_empty() {
            return Err(open(
                format!(
                    "{what}: the primary program starts {} tasks, {} attributes, {} texture fetches",
                    ev.tasks.len(),
                    ev.attrs.len(),
                    ev.tex.len()
                ),
                &["Q180"],
            ));
        }
        Ok(Shader { u0: ev.tasks[0][0] })
    }

    /// o0 of the shader for pixel (x, y). `tri`: the pixel is the triangle object's, whose task
    /// reads only g23, g24 and g25 of the global bank as measured (E808); the background object's
    /// task keeps the fill's readings (E086).
    fn colour(&mut self, s: &Shader, x: u32, y: u32, tri: bool) -> R<u32> {
        let m = Machine { pixel: Some((x, y)), tri_pixel: tri, ..Machine::default() };
        let (m, _) = run_task(&mut self.mem, &self.code, s.u0, m, "the pixel shader")?;
        if m.written.o & 1 == 0 {
            return Err(open("the pixel shader did not write o0", &["Q206"]));
        }
        Ok(m.o[0])
    }
}

/// The image of a render scene from the TA's output.
pub fn image(sc: &Scene, out: &ta::Written) -> R<Image> {
    let (w, h) = (sc.target.w, sc.target.h);
    isp::target_in_envelope(w, h)?;
    let (pdsp, usep, ubase) = (layout(sc, "pdsp")?, layout(sc, "usep")?, layout(sc, "usep_base")?);
    check_cmd(sc, pdsp)?;
    if usep != ubase {
        return Err(open("the pixel code page is not at its code base", &["Q206"]));
    }
    let pds_base = layout(sc, "pds_exec_base")?;
    let mut mem = sc.load_mem()?;
    let fb = sc.target.base;
    let pages = (w as u64 * h as u64 * 4 + 2 * 4096 - 1) / 4096;
    mem.map(fb, (pages * 4096) as u32);
    for i in 0..pages * 1024 {
        mem.write32(fb + 4 * i as u32, SENTINEL)?;
    }
    let code = Program::new(
        &words(&mem, usep, 0x400)
            .chunks_exact(2)
            .map(|d| d[0] as u64 | (d[1] as u64) << 32)
            .collect::<Vec<_>>(),
        Core::Sgx545,
    );
    let words_page = words(&mem, usep, 0x400);
    let wide: Vec<u64> = words_page.chunks_exact(2).map(|d| d[0] as u64 | (d[1] as u64) << 32).collect();
    let mut cx = Ctx { mem, code, words: wide, pds_base };
    let t = ta::tiling(w, h);
    let (tw, th) = (w.div_ceil(32), h.div_ceil(16));

    // the objects of the tiles: one object (12.2's TA writes one), read once
    let mut listings = vec![];
    let mut obj: Option<(Object, u32, u32)> = None;
    for ty in 0..th {
        for tx in 0..tw {
            let l = objects::listing(&out.param, &out.tadata, &t, (tx, ty))?;
            if let Some(l) = l {
                match &obj {
                    None => {
                        obj = Some((
                            objects::read_object(&out.param, l.isp_addr, l.nprims)?,
                            l.isp_addr,
                            l.nprims,
                        ))
                    }
                    Some((_, a, n)) if (*a, *n) != (l.isp_addr, l.nprims) => {
                        return Err(open("tiles that list different objects", &["Q231"]));
                    }
                    _ => {}
                }
            }
            listings.push(l);
        }
    }
    let ctl = sc.cmd[C_CTL];
    let mode: Option<Mode> =
        obj.as_ref().map(|(o, _, _)| isp::decode_words(o.isp, ctl, o.prims.len())).transpose()?;
    let tris: Vec<isp::Tri> =
        obj.as_ref().map(|(o, _, _)| o.prims.iter().map(|p| p.tri).collect()).unwrap_or_default();
    if let Some((o, _, _)) = &obj {
        for p in &o.prims {
            if p.rhw != [1.0; 3] {
                return Err(open(
                    "a vertex with 1/w other than 1: perspective is not shown (E606)",
                    &["Q202"],
                ));
            }
            isp::vertices_in_envelope(w, h, &p.tri)?;
            if p.negative != (p.tri.area2() < 0) {
                return Err(open("the TA's winding mark and the grid vertices' area disagree", &["Q230"]));
            }
        }
    }
    let objshader = match &obj {
        Some((o, _, _)) => Some(cx.shader(o.pds, "the triangle")?),
        None => None,
    };
    if let (Some(m), Some(sh)) = (&mode, &objshader)
        && matches!(m.pass, 1 | 2 | 4 | 5 | 6)
        && !is_colour_write(&cx.words, (sh.u0 >> 4 & 0xffff) as usize)
    {
        return Err(open(
            format!(
                "pass type {} with a pixel shader other than the library's colour write: E065 ran those pass types with that shader only, so a translucent or punch-through object that writes alpha would be drawn unblended",
                m.pass
            ),
            &["Q241"],
        ));
    }
    let bg = cx.shader([sc.cmd[C_BG], sc.cmd[C_BG + 1], sc.cmd[C_BG + 2]], "the background object")?;

    // the depth store
    let store = match sc.regs.iter().find(|(o, _)| *o == REG_ZLSCTL).map(|p| p.1) {
        None => None,
        Some(ctl) if ctl & !(0x1ff << 3) == ZLS_BASE_PATTERN => {
            let base = sc.regs.iter().find(|(o, _)| *o == REG_ZSTORE).map(|p| p.1);
            Some((ctl >> 3 & 0x1ff, base.ok_or_else(|| open("a depth store without its base", &["Q071"]))?))
        }
        Some(ctl) => {
            return Err(open(
                format!("CR_ISP_ZLSCTL {ctl:#x}: only the depth store of E465 is modelled"),
                &["Q071"],
            ));
        }
    };

    let bgdepth = f32::from_bits(sc.cmd[C_BGDEPTH]);
    let mut depth = store.map(|(g, _)| Depth {
        w,
        h,
        g,
        value: vec![bgdepth as f64; (w * h) as usize],
        tol: vec![Some(0); (w * h) as usize],
    });
    // helper instances: a shader whose writes lack .skipinv also runs for the uncovered pixels of the
    // quads the triangle covers in part (E104): which land varies from run to run (E111, E113: Q052)
    let helpers = match &objshader {
        Some(sh) => helper_sensitive(&cx.words, (sh.u0 >> 4 & 0xffff) as usize)?,
        None => false,
    };
    let mut tile_colours: Vec<Vec<u32>> = vec![];
    for ty in 0..th {
        for tx in 0..tw {
            let l = listings[(ty * tw + tx) as usize];
            let objs: Vec<Listed> = match (&l, &mode) {
                (Some(l), Some(m)) => vec![Listed { mode: *m, prims: &tris, left: l.left, right: l.right }],
                _ => vec![],
            };
            let px = isp::resolve_tile((tx, ty), bgdepth, &objs)?;
            if helpers {
                for q in 0..128usize {
                    let (qx, qy) = (q % 16 * 2, q / 16 * 2);
                    let n = [(0, 0), (1, 0), (0, 1), (1, 1)]
                        .iter()
                        .filter(|&&(dx, dy)| px[(qy + dy) * 32 + qx + dx].tag.is_some())
                        .count();
                    if (1..4).contains(&n) {
                        return Err(open(
                            format!(
                                "a pixel program whose writes lack .skipinv over a quad the triangle covers in part (tile ({tx}, {ty})): the helper instances' o0 lands in some runs only (E104, E111, E113)"
                            ),
                            &["Q052"],
                        ));
                    }
                }
            }
            let mut cols = Vec::with_capacity(512);
            for (k, p) in px.iter().enumerate() {
                let (x, y) = (32 * tx + k as u32 % 32, 16 * ty + k as u32 / 32);
                let c = match (p.tag, &objshader) {
                    (Some(_), Some(s)) => cx.colour(s, x, y, true)?,
                    _ => cx.colour(&bg, x, y, false)?,
                };
                cols.push(c);
                if x < w
                    && y < h
                    && let Some(d) = depth.as_mut()
                {
                    d.value[(y * w + x) as usize] = p.depth;
                    d.tol[(y * w + x) as usize] = p.tol;
                }
            }
            tile_colours.push(cols);
        }
    }

    // the pixel-event program and the end-of-tile task of each tile, and the PBE
    let (rows, ev_exec) = (sc.cmd[C_EV_ROWS] as usize * 4, sc.cmd[C_EV_EXEC]);
    let pw = words(&cx.mem, ev_exec, rows + PIXEVENT_CODE_LEN);
    if pw.len() < rows + PIXEVENT_CODE_LEN || fnv(&pw[rows..rows + PIXEVENT_CODE_LEN]) != PIXEVENT_CODE_FNV {
        return Err(open("the pixel-event program's code is not the template's", &["Q206"]));
    }
    if pw[9] != 0xff8 || pw[13] != 0x3f_f000 {
        return Err(open("the pixel-event program's tile masks are not the template's", &["Q206"]));
    }
    let (eot, eor) = (doutu(UP_EOT, 4), doutu(UP_EOR, 1));
    let pds = |ir: [u32; 2]| Pds {
        ir: [Some(ir[0]), Some(ir[1]), Some(0)],
        ifs: [Some(false); 2],
        alu_specials_in_movs: true,
        ..Pds::default()
    };
    let last = (tw * th - 1) as usize;
    for (n, colours) in tile_colours.iter().enumerate() {
        let (tx, ty) = (n as u32 % tw, n as u32 / tw);
        let (ir0, ir1) = (ty << 10 | tx, if n == last { 6 } else { 2 });
        let ev = run_pds(&mut cx.mem, ev_exec, rows, &mut pds([ir0, ir1]), "the pixel-event program")?;
        if ev.tasks.len() != 1 {
            return Err(open(
                format!("the pixel-event program started {} tasks for tile ({tx}, {ty})", ev.tasks.len()),
                &["Q206"],
            ));
        }
        let [u0, u1, _] = ev.tasks[0];
        if u0 == eor {
            run_task(&mut cx.mem, &cx.code, u0, Machine::default(), "the end-of-render task")?;
        } else if u0 == eot {
            let own = (ir0 << 3 & 0xff8) | (ir0 << 3 & 0x3f_f000);
            if u1 & 0x3f_fff8 != own
                || (n == last && u1 & 0x40_0000 == 0)
                || u1 & !(0x3f_fff8 | 0x40_0000) != 0x80_0000
            {
                return Err(open(
                    format!("the end-of-tile task's U1 {u1:#x} is not the template's for tile ({tx}, {ty})"),
                    &["Q206"],
                ));
            }
            let mut m = Machine::default();
            for &(a, v) in &ev.attrs {
                if a >= 128 {
                    return Err(open("a PDS attribute past 127", &["Q206"]));
                }
                m.pa[a] = v;
                m.written.pa |= 1 << a;
            }
            let (_, e) = run_task(&mut cx.mem, &cx.code, eot, m, "the end-of-tile task")?;
            let side = |t: &str| t.rsplit("#0x").next().and_then(|h| u32::from_str_radix(h.trim(), 16).ok());
            let [(a, s1), (b, s2)] = &e.emits[..] else {
                return Err(open("the end-of-tile task does not emit once as the template does", &["Q054"]));
            };
            if !a.starts_with("emitpix1") || !b.starts_with("emitpix2") {
                return Err(open("the end-of-tile task does not emit once as the template does", &["Q054"]));
            }
            let sideband =
                side(b).ok_or_else(|| open("the emit's sideband is not an immediate", &["Q054"]))?;
            let emit = Emit { words: [s1[0], s1[1], s2[0], s2[1]], sideband };
            pbe::store_tile(&emit, sc.cmd[C_PIXELBE], (tx, ty), colours, &mut cx.mem)?;
        } else {
            return Err(open(format!("the pixel-event program starts a task {u0:#x}"), &["Q206"]));
        }
    }
    let mut image = Vec::with_capacity((w * h) as usize);
    for y in 0..h {
        for x in 0..w {
            image.push(cx.mem.read32(fb + 4 * (y * w + x))?);
        }
    }
    // the target's buffer past its last row: the guard page and the rounding of the allocation
    let mut outside = 0u64;
    for i in w as u64 * h as u64..pages * 1024 {
        if cx.mem.read32(fb + 4 * i as u32)? != SENTINEL {
            outside += 1;
        }
    }
    let depth = depth.map(|d| {
        if d.tol.iter().any(Option::is_none) {
            Err(open(
                "a depth stored by a plane of gradient 0.03 or more: its error reaches 145 units (E606)",
                &["Q200"],
            ))
        } else {
            Ok(d)
        }
    });
    Ok(Image { pixels: image, outside, depth })
}

#[cfg(test)]
mod tests {
    use super::*;

    const FIXTURE: &str = include_str!("../tests/fixtures/first-triangle.scene.json");

    fn usep_words() -> Vec<u64> {
        let sc = Scene::from_fixture(FIXTURE, "first-triangle/64x64");
        let seg = sc.memory.iter().find(|m| m.role == "usep").unwrap();
        let mut d = seg.dwords.clone().unwrap();
        d.resize(1024, 0);
        d.chunks(2).map(|w| w[0] as u64 | (w[1] as u64) << 32).collect()
    }

    fn text(w: u64) -> String {
        usse_isa::decode(w, Core::Sgx545).text
    }

    /// The word with `.skipinv` removed: the one bit whose flip does that and nothing else.
    fn without_skipinv(w: u64) -> u64 {
        let t = text(w);
        let plain = t.replace(".skipinv", "");
        (0..64)
            .map(|b| w ^ 1 << b)
            .find(|&v| text(v) == plain)
            .unwrap_or_else(|| panic!("no bit takes .skipinv off {t}"))
    }

    #[test]
    fn the_librarys_fill_shader_writes_with_skipinv_and_has_no_helper_dependence() {
        let w = usep_words();
        assert_eq!(text(w[0]), "phas #0, #0, pixel, end, parallel");
        assert!(text(w[1]).starts_with("mov.skipinv.end o0"));
        assert!(!helper_sensitive(&w, 0).unwrap());
    }

    #[test]
    fn an_o0_write_without_skipinv_depends_on_the_helper_instances() {
        // E104: the plain write also reaches uncovered pixels of the quads the triangle covers
        let mut w = usep_words();
        w[1] = without_skipinv(w[1]);
        assert!(text(w[1]).starts_with("mov.end o0"), "{}", text(w[1]));
        assert!(helper_sensitive(&w, 0).unwrap());
    }

    // words of E112's phase probe (pix_phas_br.s), from its rebuilt scene: phas with a next phase,
    // a nop that ends the phase, a predicated branch, the last phas
    const PHAS_NONE: u64 = 0xfa44_0002_0000_0026;
    const NOP_END: u64 = 0xf804_0140_0000_0000;
    const BR: u64 = 0xf900_0040_0000_0003;
    const PHAS_END: u64 = 0xfa4c_0700_0000_0000;

    #[test]
    fn a_branch_in_a_later_phase_refuses_naming_q050_the_scan_goes_through_the_phases() {
        assert!(text(PHAS_NONE).starts_with("phas #38, #8, pixel, none"), "{}", text(PHAS_NONE));
        assert!(text(BR).contains("br"), "{}", text(BR));
        // phase 0 ends with its .end, but its phas names a next phase: the scan continues
        let w = [PHAS_NONE, NOP_END, BR, PHAS_END];
        match helper_sensitive(&w, 0) {
            Err(Outcome::Unsupported { ids, why }) => {
                assert_eq!(ids, ["Q050"]);
                assert!(why.contains("E112"));
            }
            o => panic!("{o:?}"),
        }
        // without the branch the same two phases are straight-line and not helper dependent
        let w = [PHAS_NONE, NOP_END, PHAS_END, NOP_END];
        assert!(!helper_sensitive(&w, 0).unwrap());
    }

    #[test]
    fn eot_and_eor_tasks_sit_where_the_librarys_page_puts_them() {
        // the U0 words the pixel-event program starts: code at 0x40 and 0x80 bytes into the page
        assert_eq!((doutu(UP_EOT, 4), doutu(UP_EOR, 1)), (0x0100_0080, 0x0100_0100));
        let w = usep_words();
        assert!(text(w[(UP_EOT / 8 + 1) as usize]).starts_with("mov.skipinv r0"));
    }

    /// The fixture's scene with its pixel program replaced by `src` (the library's phase word,
    /// then the instructions: the last must end the program) and rendered through `render::run`.
    fn render_with(at: usize, src: &[&str]) -> crate::scene::SceneResult {
        let mut sc = Scene::from_fixture(FIXTURE, "first-triangle/64x64");
        let mut w = usep_words();
        for (i, t) in src.iter().enumerate() {
            w[at + i] = usse_isa::encode(t, Core::Sgx545).unwrap_or_else(|| panic!("{t}"));
        }
        let seg = sc.memory.iter_mut().find(|m| m.role == "usep").unwrap();
        let mut d: Vec<u32> = w.iter().flat_map(|x| [*x as u32, (*x >> 32) as u32]).collect();
        let n = seg.dwords.as_ref().unwrap().len();
        d.truncate(n);
        seg.dwords = Some(d);
        crate::render::run(&sc).unwrap()
    }

    /// Word indices (in 64-bit words) of the colour write after the phase word, in the fixture's
    /// pixel page: the triangle's primary program (u0 0x8000200, phase at 32) and the background
    /// object's (u0 0x20, phase at 2, the fill 0xFF203040).
    const TRI_PROGRAM: usize = 33;
    const BG_FILL: u32 = 0xff20_3040;

    #[test]
    fn a_triangles_pixels_read_g23_g24_and_g25_and_the_background_keeps_its_own_shader() {
        // E808: in the triangle's task g23 = x mod 32, g24 = y mod 16, g25 = the lane of the quad
        type Want = fn(u32, u32) -> u32;
        let cases: [(&str, Want); 3] =
            [("g23", |x, _| x % 32), ("g24", |_, y| y % 16), ("g25", |x, y| (x & 1) | (y & 1) << 1)];
        for (g, want) in cases {
            let src = format!("mov.skipinv.end o0, {g}");
            let r = render_with(TRI_PROGRAM, &[&src]);
            assert!(r.pixel_refusal.is_none(), "{g}: {:?}", r.pixel_refusal);
            let img = r.image.unwrap();
            let (mut tri, mut bg) = (0, 0);
            for (i, &v) in img.iter().enumerate() {
                let (x, y) = (i as u32 % 64, i as u32 / 64);
                if v == BG_FILL {
                    bg += 1;
                } else {
                    // a triangle pixel: o0 is the value the program read (the PBE stores it as is)
                    assert_eq!(v & 0xff, want(x, y), "{g} at ({x}, {y}): {v:#x}");
                    tri += 1;
                }
            }
            assert!(tri > 100 && bg > 100, "{g}: triangle pixels {tri}, background {bg}");
        }
    }

    #[test]
    fn a_triangles_pixel_program_reading_another_global_is_refused_by_the_open_question() {
        // the background object's shader may read g17 (a fill, E086): the triangle's may not (E808)
        let r = render_with(TRI_PROGRAM, &["mov.skipinv.end o0, g17"]);
        match r.pixel_refusal {
            Some(Outcome::Unsupported { why, ids }) => {
                assert!(why.contains("g17") && why.contains("triangle"), "{why}");
                assert!(!ids.is_empty(), "{why}");
            }
            o => panic!("{o:?}"),
        }
        // the same read in the background's own program still renders: it is a fill's task
        let r = render_with(3, &["mov.skipinv.end o0, g17"]);
        assert!(r.pixel_refusal.is_none(), "{:?}", r.pixel_refusal);
    }
}
