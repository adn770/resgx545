// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! DPM: parameter buffer pool, state page, overflow and partial render (12.7).

use crate::Outcome;
use std::collections::BTreeMap;

/// Open questions that block the unit.
pub const OPEN: &[&str] = &["Q045", "Q036", "Q038", "Q081", "Q191", "Q192", "Q210", "Q211"];

/// A refusing stub until the unit's sub-phase lands: the model never guesses.
pub fn refuse() -> Outcome {
    Outcome::unsupported("the DPM is not modelled (12.7)", OPEN)
}

/// The limit C on the raised threshold (E774): at 4096x4096, with 1350 or 1500 vertices of the
/// tool's triangle, the TA's threshold was raised by 0x20 after the first abort at every cell of the
/// ladder with a first threshold thr0 from 0x33e to 0x351 and at none from 0x352 to 0x35e (23 jobs,
/// one flip, 1350 as 1500). The limit is on the threshold the TA runs, not on the knob P: with P
/// at 0x422 and the threshold poked, the flip was at 0x351 / 0x352 (E786, 7 of 7). It is not the
/// same at other targets (E799, E801) nor in another scene (E802), so this constant is the
/// 4096x4096 one of the tool's triangle; why it differs is open (Q210).
pub const RAISE_LIMIT_C: u32 = 0x371;

/// C at 2048x2048 with 1500 vertices of the tool's triangle (E799): last raise at thr0 0xe2, first
/// silent 0xe3, inside E785's bracket [0xe0, 0x120). A 2048x2048 target in a 4096x4096 context
/// flipped at the same place (E800).
pub const RAISE_LIMIT_C_2048: u32 = 0x102;

/// The scene of a measured limit: the tool's triangle with 1500 vertices (`--tri pixel
/// --vertices 1500`; 1350 too at 4096x4096, E774), or the same with `--tri-full` (E802).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Scene {
    ToolTriangle,
    ToolTriangleFull,
}

/// The exact limit C of the tool's triangle at each target where a run found one flip (E774,
/// E799, E801). No law in the target's size fits them (E801: 4096x2048 and 2048x4096 differ), so
/// nothing is interpolated.
const RAISE_LIMITS: &[((u32, u32), u32)] = &[
    ((4096, 4096), RAISE_LIMIT_C),
    ((2048, 2048), RAISE_LIMIT_C_2048),
    ((4096, 2048), 0x1d2),
    ((2048, 4096), 0x1d6),
    ((3072, 3072), 0x208),
];

/// The highest raised threshold of `--tri-full` at 2048x2048 (E802: thr0 0xf3 raised, no silent
/// cell run): C is at least this, its value unmeasured.
const RAISED_TRI_FULL_2048: u32 = 0x113;

/// Whether the raise limit admits a raise of `thr0` by 0x20 for a target of the scene (the
/// render target's size, not the context's: E800): `Some(true)` or `Some(false)` where a measured
/// limit decides it, `None` where none does (other targets, other scenes, `--tri-full` above its
/// highest raise). Necessary for a raise, not sufficient (E625's second run must reach thr0).
pub fn raise_within_limit_at(scene: Scene, width: u32, height: u32, thr0: u32) -> Option<bool> {
    let raised = thr0.saturating_add(0x20);
    match scene {
        Scene::ToolTriangle => {
            RAISE_LIMITS.iter().find(|(t, _)| *t == (width, height)).map(|(_, c)| raised <= *c)
        }
        Scene::ToolTriangleFull => {
            ((width, height) == (2048, 2048) && raised <= RAISED_TRI_FULL_2048).then_some(true)
        }
    }
}

/// Dword 36 of the TA/3D control block from the page counts of CR_DPM_GLOBAL_PAGE_STATUS (0x072c,
/// low half) in the sample before each abort of a job: the count before the last abort less 2,
/// floor 0, and 0 without an abort (E803: held out, 6 of 6 in g-d36 with all 3 separating jobs,
/// and 54 of 54 in the side tables of four more stages; the tool's triangle at five targets and
/// `--tri-full`). The model has no such counts of its own: this reads them, it does not make them.
pub fn dword36_from_abort_counts(counts: &[u32]) -> u32 {
    counts.last().map_or(0, |c| c.saturating_sub(2))
}

/// The guard of the firmware's raise of the first threshold by 0x20, from the global page counts
/// (the high half of CR_DPM_GLOBAL_PAGE_STATUS) at the first abort, at the resume after the partial
/// render and at the next out-of-memory entry: the abort saves dword 36 as its count less 2 (floor
/// 0, E803), the resume sets `sa8` bits 7 and 8 when its count is above dword 36, and the entry
/// raises when bit 7 is set and its count is above dword 36 again (R-5 [RE], 3d.md section 6.4).
/// Held on the hardware: `sa8` read by our own task, 6 of 6, and c4-b3, the guard's one miss on
/// the timelines, silent because its resume compared one global page (E864); the raising-side step
/// cells raised after a grow (E861). The resume's count is the one the firmware read: after a grow
/// the timeline's last sample in the partial render can read one page more (E860).
pub fn guard_raises(abort_global: u32, resume_global: u32, entry_global: u32) -> bool {
    let d36 = dword36_from_abort_counts(&[abort_global]);
    resume_global > d36 && entry_global > d36
}

/// The first threshold steps S_k of the global page count of the tool's triangle with 1500
/// vertices, measured held out where a grow was tested at and around them (E852's table, repeated
/// by the calibrations of E860, the cells of E861). The steps of 4096x2048, 2048x4096 and 3072x3072
/// are left out: their only held-out stage is gated (E861's d-a2b).
const GLOBAL_STEPS: &[((u32, u32), &[u32])] =
    &[((2048, 2048), &[0x51, 0x9d, 0xe8, 0x132]), ((4096, 4096), &[0x125, 0x240, 0x35b])];

/// Whether the first out-of-memory entry grows the TA's share of the global list
/// (`CR_DPM_TA_GLOBAL_LIST`, the list-kind branch of 3d.md section 6.4): exactly when the first
/// threshold is a step S_k (H-GREQ, E860 5 of 5 repeats, E861 16 of 16 held-out rows). `None` past
/// the page after the last measured step, at other targets and for other scenes.
pub fn grows_at_first_abort(scene: Scene, width: u32, height: u32, thr0: u32) -> Option<bool> {
    if scene != Scene::ToolTriangle {
        return None;
    }
    let steps = GLOBAL_STEPS.iter().find(|(t, _)| *t == (width, height))?.1;
    (thr0 <= steps.last()? + 1).then(|| steps.contains(&thr0))
}

/// Whether the raise limit C admits a raise of `thr0` by 0x20 (E774). Necessary for a raise at the
/// measured scene and target and not sufficient anywhere else: whether the second run reaches thr0
/// (E625's rule, Q210) is not part of it, nor is the count of partial renders: E625's formula for it
/// is refuted at U = 287 (E832: 9 down to 2 over 19 buffer sizes, none of the 20 fitting pairs).
pub fn raise_within_limit(thr0: u32) -> bool {
    thr0.saturating_add(0x20) <= RAISE_LIMIT_C
}

/// The parameter buffer's default size in pages (debugfs `render_pb_pages`); a scene overflows when
/// P - 0x22 is below its page need (E625, E735, E773).
pub const PB_PAGES_DEFAULT: u32 = 0x422;
const PB_FIXED_RESERVE: u32 = 0x22;

/// How a 4x job of the tool's full-screen triangle (`--tri-full --aa4`, `CR_TE_AA` 0xe0000000) on a
/// context made for 4x targets (four region-header arrays) ends.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Ending4x {
    /// Completes with every pixel right.
    Complete,
    /// The scene overflows the parameter buffer: -ENOSPC with no BIF fault, as at 1x (E866).
    Enospc,
    /// The job faults on the 3D side at the request base (`BIF_INT_STAT` 0x90100, `BIF_FAULT`
    /// 0x10000011), no pixel right below 4096 wide (E845, E868).
    Fault,
}

/// U4, the scene pages of that job, page 0 included: 1 + ceil(2 tiles16 / 32), the doubled grid
/// (E845's fit on E824's dumps; E866 at three boundaries one page apart, two held out; E867, E868,
/// E887, E889). Two cells used two pages more, 992 x 1280 (313) and 1184 x 768 (225), both with an
/// odd count of 32-pixel tile columns on four macrotiles a side, a shape no cell matched U4 in
/// (E887, E889); `four_array_4x_ending` refuses that band.
pub fn full_triangle_4x_pages(w: u32, h: u32) -> u32 {
    1 + (2 * w.div_ceil(16) * h.div_ceil(16)).div_ceil(32)
}

/// The 32 x 16 tiles, the macrotiles a side and the tail side of a context made for `mw` x `mh`
/// (the fork's single-sampled layout, `sgx_render.c`): (tiles x, tiles y, macrotiles a side, side).
fn render_grid(mw: u32, mh: u32) -> (u32, u32, u32, u32) {
    let (tx, ty) = (mw.div_ceil(32), mh.div_ceil(16));
    let n = if mw * mh >= 640 * 480 { 4 } else { 2 };
    let (mx, my) = (tx.div_ceil(n).next_multiple_of(4), ty.div_ceil(n).next_multiple_of(4));
    (tx, ty, n, (n * mx).max(n * my).next_power_of_two())
}

/// The Z-order index of tile (x, y) of a 4x job's doubled grid (16 x 8 pixel tiles): y on the even
/// bits, x on the odd bits. The TA keeps the tile's tail pointer, one dword, at TA-data offset 4
/// times this (H-TPM: E870's fit on E869's dump, held out by E887 and E889).
pub fn tail_index_4x(x: u32, y: u32) -> u32 {
    let spread = |v: u32| (0..16).fold(0, |r, b| r | ((v >> b) & 1) << (2 * b));
    spread(y) | spread(x) << 1
}

/// The end in bytes of a `w` x `h` 4x target's tail-pointer entries: 4 x (Z(2tx - 1, 2ty - 1) + 1),
/// tx and ty its 32 x 16 tile counts (Z grows in each coordinate, so the far corner is the last).
pub fn tail_entries_end_4x(w: u32, h: u32) -> u32 {
    let (tx, ty) = (w.div_ceil(32), h.div_ceil(16));
    4 * (tail_index_4x(2 * tx - 1, 2 * ty - 1) + 1)
}

/// The tail-pointer room our kernel gives a context made for 4x targets: the rgn4 module's 4 side^2
/// bytes (fork resgx545 a2788bd8, srcversion 99CD90DA26E3AFF9C450517), the r6-kernel module's four
/// times that (fork r6-kernel 3f0b3e74, srcversion 41E2F5C756F96D20F7109A4) or its debugfs
/// `render_tail_room` (a whole number of pages).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TailRoom {
    Rgn4,
    Quad,
    Set(u32),
}

/// `td.rgn`, the region headers' offset from the TA-data base (the tail-pointer base), of a 4x
/// context made for `mw` x `mh`: the room rounded to a page, then the control, OTPM and state pages.
pub fn region_headers_4x(mw: u32, mh: u32, room: TailRoom) -> u32 {
    let (.., side) = render_grid(mw, mh);
    let bytes = match room {
        TailRoom::Rgn4 => 4 * side * side,
        TailRoom::Quad => 16 * side * side,
        TailRoom::Set(r) => r,
    };
    bytes.next_multiple_of(0x1000) + 0x3000
}

/// How the job ends at target `w` x `h` on a context made for `mw` x `mh` by the rgn4 module with
/// `p` parameter-buffer pages (`four_array_4x_ending_on` with `TailRoom::Rgn4`).
pub fn four_array_4x_ending(w: u32, h: u32, mw: u32, mh: u32, p: u32) -> Option<Ending4x> {
    four_array_4x_ending_on(w, h, mw, mh, p, TailRoom::Rgn4)
}

/// How the job ends: a fault where the target's tail-pointer entries pass the region headers of the
/// context (H-TPM: 26 of 26 recorded cells, E870; 11 of 11 held out, E887; through the kernel's
/// room and one page either side of its limit, E889), else complete when its scene fits the buffer
/// and -ENOSPC when it does not (H-ENOSPC4, E866; E889's 4096 x 1152). `None` for a target larger
/// than its maximum or a maximum past 4096 (not run), a faulting cell at a P other than 0x422
/// (every 4x fault on record ran there) and the band where the page need is not U4's (above).
pub fn four_array_4x_ending_on(w: u32, h: u32, mw: u32, mh: u32, p: u32, room: TailRoom) -> Option<Ending4x> {
    if w == 0 || h == 0 || w > mw || h > mh || mw > 4096 || mh > 4096 {
        return None;
    }
    if tail_entries_end_4x(w, h) > region_headers_4x(mw, mh, room) {
        return (p == PB_PAGES_DEFAULT).then_some(Ending4x::Fault);
    }
    let (tx, _, n, _) = render_grid(w, h);
    let need = full_triangle_4x_pages(w, h);
    let slack = if tx % 2 == 1 && n == 4 { 2 } else { 0 };
    let usable = p.saturating_sub(PB_FIXED_RESERVE);
    if usable >= need + slack {
        Some(Ending4x::Complete)
    } else if usable < need {
        Some(Ending4x::Enospc)
    } else {
        None
    }
}

/// The tool's default triangle moved by (dx, dy) pixels (`tri -n 1 --move 1:DX,DY`).
fn default_triangle(w: u32, h: u32, dx: f64, dy: f64) -> crate::ta::Tri {
    let (w, h) = (w as f64, h as f64);
    [
        (8.0 * w / 64.0 + dx, 8.0 * h / 64.0 + dy),
        (56.0 * w / 64.0 + dx, 20.0 * h / 64.0 + dy),
        (20.0 * w / 64.0 + dx, 56.0 * h / 64.0 + dy),
    ]
}

/// The macrotile of the 32 x 16 region (c, r): the TA's index, column * n + row.
fn macrotile(t: &crate::ta::Tiling, c: u32, r: u32) -> u32 {
    (c / t.mx) * t.n + r / t.my
}

/// The regions (column, row, macrotile) that list one moved default triangle in either 16 x 16
/// tile (HU1's test, E773), in the TA's walk order H-WALK64 (E899, held out on the hardware by
/// E916): strips of 64 pixel rows, each strip in 64 x 64-pixel blocks left to right, a block's
/// regions row by row.
fn walk64_regions(w: u32, h: u32, dx: u32, dy: u32) -> Vec<(u32, u32, u32)> {
    let t = crate::ta::tiling(w, h);
    let tri = default_triangle(w, h, dx as f64, dy as f64);
    let mut out = vec![];
    for r in 0..t.ty {
        for c in 0..t.tx {
            let (x0, y0) = (32.0 * c as f64, 16.0 * r as f64);
            if crate::ta::tile_lists(&tri, x0, y0) || crate::ta::tile_lists(&tri, x0 + 16.0, y0) {
                out.push((c, r, macrotile(&t, c, r)));
            }
        }
    }
    out.sort_by_key(|&(c, r, _)| (r / 4, c / 2, r, c));
    out
}

/// HU1, the page need U of one moved default triangle (E773: 128 bytes a stream, a page per 32
/// streams of a macrotile, plus the global page; E916's five calibrations held out).
pub fn one_triangle_page_need(w: u32, h: u32, dx: u32, dy: u32) -> u32 {
    let mut per = BTreeMap::new();
    for (_, _, m) in walk64_regions(w, h, dx, dy) {
        *per.entry(m).or_insert(0u32) += 1;
    }
    1 + per.values().map(|k| k.div_ceil(32)).sum::<u32>()
}

/// HU1, the page need U of a scene of any triangles in one render or several kicks of one open
/// scene: a region that lists any of them counted once, 128 bytes a stream, a page per 32 streams
/// of a macrotile, plus the global page (E773). Held out on r8-ldpm's five multi-kick scenes and
/// eight one-triangle shapes from a full-target triangle to slivers (E939); a stream for every
/// region of the bounding box (H-BBOX) failed 5 of 8 there.
pub fn scene_page_need(w: u32, h: u32, tris: &[crate::ta::Tri]) -> u32 {
    let t = crate::ta::tiling(w, h);
    let mut per = BTreeMap::new();
    for r in 0..t.ty {
        for c in 0..t.tx {
            let (x0, y0) = (32.0 * c as f64, 16.0 * r as f64);
            if tris
                .iter()
                .any(|tri| crate::ta::tile_lists(tri, x0, y0) || crate::ta::tile_lists(tri, x0 + 16.0, y0))
            {
                *per.entry(macrotile(&t, c, r)).or_insert(0u32) += 1;
            }
        }
    }
    1 + per.values().map(|k| k.div_ceil(32)).sum::<u32>()
}

/// The targets where the walk-order replay of a one-triangle count was held out (E916: s44a and
/// s44b at 4096x4096, s42 at 4096x2048, s22 at 2048x2048, s17 at 1024x768).
const COUNT_TARGETS: &[(u32, u32)] = &[(4096, 4096), (4096, 2048), (2048, 2048), (1024, 768)];

/// The partial renders of one moved default triangle in one kick at the first threshold `thr0`
/// (`P - 0x22`), and each TA run's peak page count: E875's page replay in H-WALK64 order (E899)
/// with no fitted number. Each region takes one 128-byte stream from its macrotile's current page
/// (32 a page); the global page is page 1; a page request above the threshold (thr0 in the first
/// run, thr0 + 0x20 after the one raise) is refused, a partial render frees every page but the
/// global one and the walk goes on at the same region. Held out on five new scenes (E916): 29 of
/// 29 counts and every run's peak where the first run was sampled. `None` at a target no
/// held-out scene ran, a threshold below 2 or at the clamp, and where the raised threshold
/// still holds no page (scenes of many objects and several kicks are not this function's: Q211;
/// F9's replay of the 1500-vertex scene gave 13 of 15 held-out counts, and neither the multi-kick
/// replay nor the union's gave r8-ldpm's multi-kick counts, E938).
pub fn one_triangle_partial_renders(w: u32, h: u32, dx: u32, dy: u32, thr0: u32) -> Option<(u32, Vec<u32>)> {
    if !COUNT_TARGETS.contains(&(w, h)) || !(2..0x400).contains(&thr0) {
        return None;
    }
    let (mut used, mut thr, mut n) = (1u32, thr0, 0u32);
    let mut cur: BTreeMap<u32, u32> = BTreeMap::new();
    let mut peaks = vec![];
    for (_, _, m) in walk64_regions(w, h, dx, dy) {
        if cur.get(&m).copied().unwrap_or(0) == 0 {
            if used + 1 > thr {
                peaks.push(used);
                n += 1;
                used = 1;
                cur.clear();
                thr = thr0 + 0x20;
                if used + 1 > thr {
                    return None;
                }
            }
            used += 1;
            cur.insert(m, 32);
        }
        *cur.get_mut(&m)? -= 1;
    }
    peaks.push(used);
    Some((n, peaks))
}

/// E874's block-level replay of the TA for the tool's triangle with 1500 vertices (`--tri pixel
/// --vertices 1500`): triangle j is the default one moved j/16 pixel right and down, object b
/// holds triangles 5b to 5b + 4 in a 67-dword block, global page k is requested by object
/// b_k = floor(1024 (k - 1) / 67) and written 3 objects before that object is tiled (the fitted
/// lag); a region's entry is 2 dwords, or 3 with a mask, plus the base dword at b_k; a 128-byte
/// stream block holds 31 dwords of entries; a macrotile takes a page every 32 blocks. Returns the
/// steps S2 to S7 by k (the page count before global page k is taken) and the page count after
/// each object is tiled (the last is U), computed once a target.
fn tool_triangle_replay(w: u32, h: u32) -> (BTreeMap<u32, u32>, Vec<u32>) {
    use std::sync::{Mutex, OnceLock};
    type Replay = (BTreeMap<u32, u32>, Vec<u32>);
    static DONE: OnceLock<Mutex<BTreeMap<(u32, u32), Replay>>> = OnceLock::new();
    let done = DONE.get_or_init(|| Mutex::new(BTreeMap::new()));
    if let Some(r) = done.lock().ok().and_then(|d| d.get(&(w, h)).cloned()) {
        return r;
    }
    let r = replay_1500(w, h);
    if let Ok(mut d) = done.lock() {
        d.insert((w, h), r.clone());
    }
    r
}

fn replay_1500(w: u32, h: u32) -> (BTreeMap<u32, u32>, Vec<u32>) {
    const L: u32 = 67;
    const CAP: u32 = 31;
    const OBJS: u32 = 100;
    const PER: u32 = 5;
    const LAG: u32 = 3;
    let t = crate::ta::tiling(w, h);
    let bk = |k: u32| 1024 * (k - 1) / L;
    let gk: BTreeMap<u32, u32> = (2..12).map(|k| (bk(k), k)).collect();
    let tri = |j: u32| default_triangle(w, h, j as f64 / 16.0, j as f64 / 16.0);
    let mut writes: BTreeMap<u32, Vec<u32>> = BTreeMap::new();
    for b in 0..OBJS {
        writes.entry(b.saturating_sub(LAG)).or_default().push(b);
    }
    let (mut used, mut mt_blocks) = (BTreeMap::new(), BTreeMap::new());
    let (mut pages, mut steps, mut after) = (1u32, BTreeMap::new(), vec![]);
    for ob in 0..OBJS {
        for b in writes.get(&ob).into_iter().flatten() {
            if let Some(&k) = gk.get(b) {
                steps.insert(k, pages);
                pages += 1;
            }
        }
        let ts: Vec<_> = (0..PER).map(|i| tri(PER * ob + i)).collect();
        let xs = ts.iter().flat_map(|t| t.map(|p| p.0));
        let (x0, x1) = xs.fold((f64::MAX, f64::MIN), |(a, b), x| (a.min(x), b.max(x)));
        let ys = ts.iter().flat_map(|t| t.map(|p| p.1));
        let (y0, y1) = ys.fold((f64::MAX, f64::MIN), |(a, b), y| (a.min(y), b.max(y)));
        let rows = ((y0 / 16.0).floor().max(0.0) as u32)..t.ty.min((y1 / 16.0).floor() as u32 + 1);
        for r in rows {
            for c in ((x0 / 32.0).floor().max(0.0) as u32)..t.tx.min((x1 / 32.0).floor() as u32 + 1) {
                let (xa, ya) = (32.0 * c as f64, 16.0 * r as f64);
                let left = ts.iter().filter(|t| crate::ta::tile_lists(t, xa, ya)).count() as u32;
                let right = ts.iter().filter(|t| crate::ta::tile_lists(t, xa + 16.0, ya)).count() as u32;
                if left == 0 && right == 0 {
                    continue;
                }
                let both = left > 0 && right > 0;
                let mut dw = if (both && left == PER && right == PER) || (!both && left.max(right) <= 2) {
                    2
                } else {
                    3
                };
                dw += u32::from(gk.contains_key(&ob));
                let u = used.entry((c, r)).or_insert(CAP + 1);
                if *u + dw > CAP {
                    *u = 0;
                    let nb = mt_blocks.entry(macrotile(&t, c, r)).or_insert(0u32);
                    if *nb % 32 == 0 {
                        pages += 1;
                    }
                    *nb += 1;
                }
                *u += dw;
            }
        }
        after.push(pages);
    }
    (steps, after)
}

/// The targets of the 1500-vertex scene whose calibration's steps all fell in their brackets as
/// the step replay froze them (H-STEPMODEL, E915: 3072x3072, 3072x2048, 2560x2560, 1024x1024; the
/// premise target 2048x2048, E874's fit), and r8-ldpm's 1536x1536 and 4096x2048 (E936). 2048x3072
/// (S6 is 0x234, one page above the replay) and 2048x4096 (S3 is 0x12c, three above), both pinned
/// by the abort's global page count (E935), 2560x3072 (S6 one above) and 3072x2560 (S3 and S6 two
/// above, E936) are not. Scenes of larger objects (`--vtx-coords`) are not this replay's: with 8
/// coordinate pairs written by the vertex program the scene needs more than the clamp and its
/// steps vary by up to 2 pages between runs (E937). r9-ldpm held them at 2304x2304, 2304x1792 and
/// 1792x1792 (E961) and 1280x1280 and 2560x2048 (E963); 2048x2304 (S3 and S6 one above, E961) and
/// the four wide targets of E962 (S6 one or two above, the needs the replay's) are not.
const STEP_TARGETS: &[(u32, u32)] = &[
    (2048, 2048),
    (3072, 3072),
    (3072, 2048),
    (2560, 2560),
    (1024, 1024),
    (1536, 1536),
    (4096, 2048),
    (2304, 2304),
    (2304, 1792),
    (1792, 1792),
    (1280, 1280),
    (2560, 2048),
];

/// The steps S2 to S7 of the global page count in the first TA run of the tool's triangle with 1500
/// vertices and its page need U, by E874's replay, at a target where they were held out (E915).
pub fn tool_triangle_steps(w: u32, h: u32) -> Option<(Vec<u32>, u32)> {
    if !STEP_TARGETS.contains(&(w, h)) {
        return None;
    }
    let (steps, after) = tool_triangle_replay(w, h);
    Some((steps.values().copied().collect(), *after.last()?))
}

/// The bands k (S_k < thr0 <= the next step) where H-SPAN's frozen cells held (E915): s-m's
/// bands 3 and 5 of the new targets, band 5 of 3072x3072 (its band 6 failed at A_6, as 2560x2560's
/// did), 2560x2560's band 3, and 2048x2048's bands 2 to 7 (s-a0's controls and the replicates of
/// R6-dpm's band 5 to 7 cells). The 2048x3072 cells were scored on its calibration's steps, which
/// at bands 3 and 5 are the replay's. r8-ldpm added 3072x2048's band 6 (E936); there band 6 kept
/// the second page past A_6 at 1536x1536 and 4096x2048 and, read after the run, again at
/// 3072x3072 and 2560x2560. Band 6's margin ends at the page count once object b_6 + 1 is tiled
/// (H-NEXT1, E960's OD-2, fitted on 3072x3072 and 2560x2560 and SEMI on eight more targets): held
/// out by r9-ldpm at 2304x2304, 2048x2304, 2304x1792 and 1792x1792, 20 of 20 cells (E961); at
/// 2048x2048 and 3072x2048 that end is A_6. Band 6 stays refused at the fit and SEMI targets.
const SPAN_BANDS: &[((u32, u32), &[u32])] = &[
    ((2304, 2304), &[6]),
    ((2048, 2304), &[6]),
    ((2304, 1792), &[6]),
    ((1792, 1792), &[6]),
    ((2048, 2048), &[2, 3, 4, 5, 6, 7]),
    ((3072, 3072), &[5]),
    ((3072, 2048), &[3, 5, 6]),
    ((2048, 3072), &[3, 5]),
    ((2560, 2560), &[3]),
    ((1024, 1024), &[3, 5]),
];

/// The global pages left by the first partial render of the tool's triangle with 1500 vertices at
/// the first threshold `thr0` (H-SPAN, E900, held out by E915): 2 iff S_k < thr0 < A_k, else 1,
/// where A_k is the page count once object b_k, whose block straddles global pages k - 1 and k, is
/// tiled; at band 6 the margin runs to the page count once object b_6 + 1 is tiled (H-NEXT1,
/// E961). `None` on a step (thr0 = S_k grows the global list, H-GREQ), at a band or target where
/// no frozen cell held, and below S2.
pub fn first_partial_render_global_pages_left(w: u32, h: u32, thr0: u32) -> Option<u32> {
    let bands = SPAN_BANDS.iter().find(|(t, _)| *t == (w, h))?.1;
    let (steps, after) = tool_triangle_replay(w, h);
    let (&k, &s) = steps.iter().rfind(|&(_, &s)| s <= thr0)?;
    if thr0 == s || !bands.contains(&k) {
        return None;
    }
    if steps.get(&(k + 1)).is_some_and(|&next| thr0 >= next) {
        return None;
    }
    let b = (1024 * (k - 1) / 67) as usize + usize::from(k == 6);
    let a = *after.get(b)?;
    Some(if thr0 < a { 2 } else { 1 })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_open_list_holds_the_threshold_and_page_need_questions() {
        // Q210 the threshold raise rule, Q211 the page need of a scene; Q273 (dword 36) is answered
        // by E803, so it no longer blocks the unit
        for id in ["Q210", "Q211"] {
            assert!(OPEN.contains(&id), "{id}");
        }
        assert!(!OPEN.contains(&"Q273"));
    }

    #[test]
    fn the_raise_limit_splits_the_ladder_of_e774_at_one_flip() {
        // the first thresholds P - 0x22 of E774's cells that raised (P = 0x360 to 0x373: 0x33e to
        // 0x351) and of those that did not (P = 0x374 to 0x380: 0x352 to 0x35e), 1350 and 1500 alike
        for thr0 in 0x33e..=0x351 {
            assert!(raise_within_limit(thr0), "{thr0:#x}");
        }
        for thr0 in 0x352..=0x35e {
            assert!(!raise_within_limit(thr0), "{thr0:#x}");
        }
        // E625's default triangle (thr0 at most 0x100) and E753's raises at 0x2fe are inside, the
        // clamp of E704 (thr0 0x400) is outside
        assert!(raise_within_limit(0x100) && raise_within_limit(0x2fe));
        assert!(!raise_within_limit(0x400) && !raise_within_limit(u32::MAX));
    }

    #[test]
    fn the_limit_follows_the_threshold_the_ta_runs_over_the_poke_ladder_of_e786() {
        // E786 [HW, held out]: 1500 vertices at 4096x4096, P = 0x422, the threshold poked to V
        let ladder = [
            (0x300, true),
            (0x33e, true),
            (0x351, true),
            (0x352, false),
            (0x35e, false),
            (0x3a0, false),
            (0x3de, false),
        ];
        for (v, raised) in ladder {
            assert_eq!(raise_within_limit_at(Scene::ToolTriangle, 4096, 4096, v), Some(raised), "{v:#x}");
            assert_eq!(raise_within_limit(v), raised, "{v:#x}");
        }
    }

    #[test]
    fn at_2048x2048_the_limit_is_exact_0x102_inside_the_bracket_of_e785() {
        // E799 [HW, held out]: last raise at thr0 0xe2, first silent 0xe3 (C = 0x102); E785's cells
        // 0x80 and 0xc0 raised, 0x100 did not
        let at = |t| raise_within_limit_at(Scene::ToolTriangle, 2048, 2048, t);
        for t in [0x80, 0xc0, 0xe0, 0xe2] {
            assert_eq!(at(t), Some(true), "{t:#x}");
        }
        for t in [0xe3, 0xe4, 0xe8, 0xf0, 0x100, 0x140] {
            assert_eq!(at(t), Some(false), "{t:#x}");
        }
        assert!(at(0xe2) == Some(true) && 0xe2 + 0x20 == RAISE_LIMIT_C_2048);
        // 4096x4096's limit does not hold here (H-same refuted): 0x100 + 0x20 is below 0x371
        assert!(raise_within_limit(0x100) && at(0x100) == Some(false));
    }

    #[test]
    fn the_limit_follows_the_target_with_one_value_at_each_measured_target() {
        // E801 [HW, held out]: exact flips at three more targets of the same scene; 4096x2048 and
        // 2048x4096 have as many regions and different limits
        let at = |w, h, t| raise_within_limit_at(Scene::ToolTriangle, w, h, t);
        for (w, h, last) in
            [(4096, 2048, 0x1b2), (2048, 4096, 0x1b6), (3072, 3072, 0x1e8), (4096, 4096, 0x351)]
        {
            assert_eq!(at(w, h, last), Some(true), "{w}x{h}");
            assert_eq!(at(w, h, last + 1), Some(false), "{w}x{h}");
        }
        assert_ne!(at(4096, 2048, 0x1b4), at(2048, 4096, 0x1b4));
        // E800 [HW, held out]: a 2048x2048 target in a 4096x4096 context flipped where g-c4's did,
        // so the function takes the target's size and no context; every other target stays
        // unmeasured
        for (w, h) in [(2048, 1536), (4096, 3072), (1024, 768), (64, 64), (4096, 1024), (1024, 4096)] {
            assert_eq!(at(w, h, 0x100), None, "{w}x{h}");
        }
    }

    #[test]
    fn another_scene_at_2048x2048_raises_beyond_the_tool_triangles_limit() {
        // E802 [HW, held out]: the --tri-full scene raised at thr0 0xd2, 0xde, 0xe2, 0xe3, 0xe7 and
        // 0xf3, with no silent cell; the tool triangle's 0xe3 did not raise (E799)
        let full = |t| raise_within_limit_at(Scene::ToolTriangleFull, 2048, 2048, t);
        for t in [0xd2, 0xde, 0xe2, 0xe3, 0xe7, 0xf3] {
            assert_eq!(full(t), Some(true), "{t:#x}");
        }
        assert_eq!(raise_within_limit_at(Scene::ToolTriangle, 2048, 2048, 0xe3), Some(false));
        // no silent cell was run: above 0xf3 the limit is unmeasured, and no other target ran
        assert_eq!((full(0xf4), full(0x100)), (None, None));
        assert_eq!(raise_within_limit_at(Scene::ToolTriangleFull, 4096, 4096, 0x300), None);
    }

    #[test]
    fn dword_36_is_the_count_before_the_last_abort_less_2_e803() {
        // E803 [HW, held out]: g-d36's six jobs (three separate this reading from the peak and the
        // second-abort readings), counts of 0x072c's low half in the sample before each abort
        let rows: [(&[u32], u32); 6] = [
            (&[2, 3, 3, 3, 3, 3], 1),
            (&[2, 3, 3, 2, 2, 3], 1),
            (&[2, 4, 3], 1),
            (&[3, 4, 4], 2),
            (&[3, 4, 3], 1),
            (&[3, 4, 3], 1),
        ];
        for (counts, d36) in rows {
            assert_eq!(dword36_from_abort_counts(counts), d36, "{counts:?}");
        }
        // side tables: a job without an abort reads 0; one abort at the count 7 reads 5 (c5b-cal);
        // the floor at 0 (g-c7's counts of 1 and 2)
        assert_eq!(dword36_from_abort_counts(&[]), 0);
        assert_eq!(dword36_from_abort_counts(&[7]), 5);
        assert_eq!(dword36_from_abort_counts(&[1, 1, 2, 2, 2]), 0);
        assert_eq!(dword36_from_abort_counts(&[1, 2, 1]), 0);
    }

    #[test]
    fn the_guard_raises_when_the_resume_and_the_entry_count_above_dword_36_e864() {
        // R-5 [RE] held on the hardware (E864: sa8 bits 7 and 8 set by the resume, read by our own
        // task), counts of global pages at the first abort, at the resume, at the next entry
        assert!(guard_raises(3, 2, 4)); // E799's c4-b5, the last raise at 2048x2048
        assert!(!guard_raises(3, 1, 3)); // c4-b6, the first silent cell
        assert!(guard_raises(1, 1, 1)); // E802's raised cells: dword 36 floors at 0
        // E861 [HW, held out]: the raising-side step cells grew and raised (1 or 2 at the abort)
        assert!(guard_raises(1, 1, 2) && guard_raises(2, 1, 2));
        // E864 [HW, held out]: c4-b3's resume compared one global page (sa8 bits 7 to 9 clear
        // at its decision entry), so it is silent, as are the 4096x4096 S4 cells of E861
        assert!(!guard_raises(3, 1, 4));
        // E862: 4 global pages at the abort below S5 make dword 36 = 2, silent with 1 or 2 left
        assert!(!guard_raises(4, 2, 4) && !guard_raises(4, 1, 4));
        // the entry must see the count above dword 36 again
        assert!(!guard_raises(3, 2, 1));
    }

    #[test]
    fn the_first_abort_grows_the_global_list_exactly_on_a_step_e861() {
        // E860, E861 [HW, held out]: the tool's triangle with 1500 vertices; grow at every first
        // threshold on a step and at none one page either side, at 2048x2048 and 4096x4096
        let grows = |w, h, t| grows_at_first_abort(Scene::ToolTriangle, w, h, t);
        for t in [0x51, 0x9d, 0xe8, 0x132] {
            assert_eq!(grows(2048, 2048, t), Some(true), "{t:#x}");
            assert_eq!(grows(2048, 2048, t - 1), Some(false), "{t:#x}");
            assert_eq!(grows(2048, 2048, t + 1), Some(false), "{t:#x}");
        }
        for t in [0x240, 0x35b] {
            assert_eq!(grows(4096, 4096, t), Some(true), "{t:#x}");
        }
        assert_eq!(grows(4096, 4096, 0x23f), Some(false));
        assert_eq!(grows(4096, 4096, 0x35a), Some(false));
        // E852's kept jobs: no grow off a step (the default c4 cells)
        assert_eq!(grows(2048, 2048, 0xe2), Some(false));
        // above the last measured step, at the gated targets (E861's d-a2b) and for other
        // scenes the model refuses
        assert_eq!(grows(2048, 2048, 0x140), None);
        assert_eq!(grows(4096, 2048, 0x1b9), None);
        assert_eq!(grows_at_first_abort(Scene::ToolTriangleFull, 2048, 2048, 0xe8), None);
    }

    #[test]
    fn r6_dpm_s_gated_targets_and_bands_stay_refused_e881() {
        // E881 [HW, post hoc]: R6-dpm's step model held at 2048x1024, 1024x2048 and 1536x1536
        // (18 of 18 steps, the raise flipping at B3) and H-GREQ at 2048x2048 bands 5 to 7, but
        // every frozen headline is gated "cannot tell" (a control with no reading), so neither the
        // steps, the limits nor the grow there are modelled: the model refuses them
        for (w, h, s3, b3) in [(2048, 1024, 0x52, 0x79), (1024, 2048, 0x56, 0x7b), (1536, 1536, 0x5d, 0x87)] {
            assert_eq!(grows_at_first_abort(Scene::ToolTriangle, w, h, s3), None, "{w}x{h}");
            assert_eq!(raise_within_limit_at(Scene::ToolTriangle, w, h, b3), None, "{w}x{h}");
        }
        for t in [0x176, 0x1c1, 0x20c] {
            assert_eq!(grows_at_first_abort(Scene::ToolTriangle, 2048, 2048, t), None, "{t:#x}");
        }
    }

    #[test]
    fn the_4x_full_triangle_needs_u4_pages_at_every_measured_size() {
        // E824's dumps, E845's s0, E866's boundaries and E867's, E868's completed rows
        let needs = [
            ((288, 144), 12),
            ((512, 384), 49),
            ((640, 480), 76),
            ((256, 1536), 97),
            ((1024, 512), 129),
            ((1024, 768), 193),
            ((1280, 1024), 321),
            ((2048, 1536), 769),
        ];
        for ((w, h), u) in needs {
            assert_eq!(full_triangle_4x_pages(w, h), u, "{w}x{h}");
        }
    }

    #[test]
    fn a_4x_overflow_ends_in_enospc_one_page_short_of_the_need_e866() {
        // E866 [HW]: H-ENOSPC4 held, 6 of 6 (o4, o5 replicate E846; o6 to o9 held out)
        let rows = [
            ((1024, 768), 0xe3, Ending4x::Complete),
            ((1024, 768), 0xe2, Ending4x::Enospc),
            ((288, 144), 0x23, Ending4x::Enospc),
            ((640, 480), 0x6e, Ending4x::Complete),
            ((640, 480), 0x6d, Ending4x::Enospc),
            ((512, 384), 0x53, Ending4x::Complete),
            ((512, 384), 0x52, Ending4x::Enospc),
        ];
        for ((w, h), p, end) in rows {
            assert_eq!(four_array_4x_ending(w, h, w, h, p), Some(end), "{w}x{h} at {p:#x}");
        }
    }

    #[test]
    fn the_4x_fault_follows_the_contexts_maximum_and_no_size_rule_e867_e868() {
        // E867 [HW]: the faulting 1280x1024 completes on a context made for a larger maximum with
        // more tail room (m1, m2, m4) and faults when only the region buffer grows (m3)
        let m = [
            ((1024, 768), (2048, 2048), Ending4x::Complete),
            ((1280, 1024), (1280, 1040), Ending4x::Complete),
            ((1280, 1024), (2048, 2048), Ending4x::Complete),
            ((1280, 1024), (2048, 1024), Ending4x::Fault),
            ((2048, 1536), (4096, 4096), Ending4x::Complete),
        ];
        for ((w, h), (mw, mh), end) in m {
            assert_eq!(
                four_array_4x_ending(w, h, mw, mh, PB_PAGES_DEFAULT),
                Some(end),
                "{w}x{h} on {mw}x{mh}"
            );
        }
        // E868 [HW]: on its own maximum; E845, E869: 1280 x 1024 and 2048 x 1536 fault
        let own = [
            ((2048, 240), true),
            ((256, 1536), false),
            ((768, 2048), true),
            ((1280, 768), true),
            ((1024, 1024), true),
            ((1024, 512), false),
            ((1184, 768), true),
            ((1024, 800), true),
            ((1280, 1024), true),
            ((2048, 1536), true),
        ];
        for ((w, h), fault) in own {
            let end = if fault { Ending4x::Fault } else { Ending4x::Complete };
            assert_eq!(four_array_4x_ending(w, h, w, h, PB_PAGES_DEFAULT), Some(end), "{w}x{h}");
        }
    }

    #[test]
    fn the_4x_tail_pointers_are_z_ordered_with_y_on_the_even_bits_e870() {
        // E870's fit on E869's dump, held out by E887 and E889: one dword a tile of the doubled
        // grid at 4 x Z(x, y), y on the even bits, x on the odd bits
        assert_eq!(tail_index_4x(0, 0), 0);
        assert_eq!(tail_index_4x(0, 1), 1);
        assert_eq!(tail_index_4x(1, 0), 2);
        assert_eq!(tail_index_4x(3, 5), 27);
        // the end of a target's entries, 4 x (Z(2tx - 1, 2ty - 1) + 1) (E870's table, E887, E889)
        let ends = [
            ((64, 64), 0x80),
            ((1024, 768), 0x7000),
            ((1024, 512), 0x4000),
            ((1024, 800), 0x7ac0),
            ((1280, 768), 0xc800),
            ((1280, 1024), 0xd800),
            ((2048, 240), 0xaff0),
            ((768, 2048), 0x17800),
            ((992, 1280), 0x12fe0),
            ((1024, 1280), 0x13000),
            ((1024, 1296), 0x13ab0),
            ((2048, 2032), 0x1fff0),
            ((4096, 1152), 0x3ac00),
            ((4096, 4096), 0x80000),
        ];
        for ((w, h), end) in ends {
            assert_eq!(tail_entries_end_4x(w, h), end, "{w}x{h}");
        }
    }

    #[test]
    fn the_region_headers_follow_the_kernels_tail_room() {
        // the rgn4 module (fork a2788bd8): room 4 side^2 bytes, then the control, OTPM and state
        // pages; the r6-kernel module (fork r6-kernel 3f0b3e74): four times that room for a
        // context made for 4x targets, or the debugfs render_tail_room
        let rgn4 = [
            ((64, 64), 0x4000),
            ((1024, 768), 0x7000),
            ((2048, 1024), 0x7000),
            ((1024, 1280), 0x13000),
            ((4096, 4096), 0x43000),
        ];
        for ((mw, mh), rgn) in rgn4 {
            assert_eq!(region_headers_4x(mw, mh, TailRoom::Rgn4), rgn, "{mw}x{mh}");
        }
        let auto = [
            ((1024, 768), 0x13000),
            ((1280, 1024), 0x13000),
            ((2048, 1536), 0x43000),
            ((4096, 1152), 0x43000),
        ];
        for ((mw, mh), rgn) in auto {
            assert_eq!(region_headers_4x(mw, mh, TailRoom::Quad), rgn, "{mw}x{mh}");
        }
        for (room, rgn) in [(0x3000, 0x6000), (0x4000, 0x7000), (0xa000, 0xd000), (0xb000, 0xe000)] {
            assert_eq!(region_headers_4x(1280, 1024, TailRoom::Set(room)), rgn, "{room:#x}");
        }
    }

    #[test]
    fn the_rule_gives_every_four_array_outcome_on_record_and_the_held_out_rows_e887() {
        // (target, maximum, fault) on the rgn4 module at P 0x422: E824, E828, E845, E846, E867,
        // E868, E869 (E870's 26 cells), then E887's held-out rows a1-a14, h1, h2 and its control a4
        // (target, maximum, faulted)
        type Cell = ((u32, u32), (u32, u32), bool);
        let cells: &[Cell] = &[
            ((64, 64), (64, 64), false),
            ((288, 144), (288, 144), false),
            ((256, 288), (256, 288), false),
            ((384, 384), (384, 384), false),
            ((320, 160), (320, 160), false),
            ((512, 384), (512, 384), false),
            ((640, 480), (640, 480), false),
            ((320, 400), (320, 400), false),
            ((1024, 768), (1024, 768), false),
            ((1280, 1024), (1280, 1024), true),
            ((2048, 1536), (2048, 1536), true),
            ((4096, 1152), (4096, 1152), true),
            ((4096, 4096), (4096, 4096), true),
            ((1024, 768), (2048, 2048), false),
            ((1280, 1024), (1280, 1040), false),
            ((1280, 1024), (2048, 2048), false),
            ((1280, 1024), (2048, 1024), true),
            ((2048, 1536), (4096, 4096), false),
            ((2048, 240), (2048, 240), true),
            ((256, 1536), (256, 1536), false),
            ((768, 2048), (768, 2048), true),
            ((1280, 768), (1280, 768), true),
            ((1024, 1024), (1024, 1024), true),
            ((1024, 512), (1024, 512), false),
            ((1184, 768), (1184, 768), true),
            ((1024, 800), (1024, 800), true),
            // E887 [HW, held out]
            ((1024, 768), (2048, 1024), false),
            ((1024, 1280), (1024, 1280), false),
            ((992, 1280), (992, 1280), false),
            ((512, 1536), (512, 1536), false),
            ((1024, 1024), (1024, 1280), false),
            ((1024, 800), (1024, 1280), false),
            ((1024, 1296), (1024, 1296), true),
            ((1040, 1280), (1040, 1280), true),
            ((1024, 800), (2048, 1024), true),
            ((1024, 1536), (1024, 1536), true),
        ];
        for &((w, h), (mw, mh), fault) in cells {
            let end = if fault { Ending4x::Fault } else { Ending4x::Complete };
            assert_eq!(
                four_array_4x_ending(w, h, mw, mh, PB_PAGES_DEFAULT),
                Some(end),
                "{w}x{h} on {mw}x{mh}"
            );
        }
    }

    #[test]
    fn the_quadrupled_tail_room_ends_the_fault_and_the_knob_moves_the_limit_e889() {
        // E889 [HW]: on the r6-kernel module every own-maximum cell that faulted completes
        // (b1-b8, b9 the control), the largest targets complete or overflow without a fault
        let quad = [
            ((1024, 768), Ending4x::Complete),
            ((1280, 1024), Ending4x::Complete),
            ((1184, 768), Ending4x::Complete),
            ((1024, 800), Ending4x::Complete),
            ((2048, 240), Ending4x::Complete),
            ((768, 2048), Ending4x::Complete),
            ((2048, 1536), Ending4x::Complete),
            ((1280, 768), Ending4x::Complete),
            ((1024, 1024), Ending4x::Complete),
            ((2048, 2032), Ending4x::Complete),
            ((4096, 960), Ending4x::Complete),
            ((4096, 1152), Ending4x::Enospc),
        ];
        for ((w, h), end) in quad {
            assert_eq!(
                four_array_4x_ending_on(w, h, w, h, PB_PAGES_DEFAULT, TailRoom::Quad),
                Some(end),
                "{w}x{h}"
            );
        }
        // the knob one page apart: k1, k5, k2, k4, k3
        let knob = [
            ((1280, 1024), 0x4000, Ending4x::Fault),
            ((1024, 768), 0x4000, Ending4x::Complete),
            ((1280, 1024), 0xb000, Ending4x::Complete),
            ((1024, 768), 0x3000, Ending4x::Fault),
            ((1280, 1024), 0xa000, Ending4x::Fault),
        ];
        for ((w, h), room, end) in knob {
            assert_eq!(
                four_array_4x_ending_on(w, h, w, h, PB_PAGES_DEFAULT, TailRoom::Set(room)),
                Some(end),
                "{w}x{h} at {room:#x}"
            );
        }
    }

    #[test]
    fn a_4x_cell_outside_what_was_run_is_refused() {
        // a target larger than its context's maximum, a maximum past 4096, a faulting cell at
        // another P (every 4x fault on record ran at P 0x422)
        assert_eq!(four_array_4x_ending(1280, 1024, 1024, 768, PB_PAGES_DEFAULT), None);
        assert_eq!(four_array_4x_ending(64, 64, 8192, 64, PB_PAGES_DEFAULT), None);
        assert_eq!(four_array_4x_ending(1280, 1024, 1280, 1024, 0x200), None);
        // a completing cell at another P follows its page need (H-ENOSPC4, E866)
        assert_eq!(four_array_4x_ending(1088, 768, 1088, 768, PB_PAGES_DEFAULT), Some(Ending4x::Fault));
        assert_eq!(four_array_4x_ending(64, 64, 128, 128, 0x23), Some(Ending4x::Enospc));
    }

    #[test]
    fn the_page_need_of_odd_32_pixel_columns_on_four_macrotiles_is_refused_near_the_buffer() {
        // E887 a12 (992 x 1280) and E889 b2 (1184 x 768) used 313 and 225 pages, U4 + 2: no
        // measured cell of that shape (an odd count of 32-pixel tile columns, four macrotiles a
        // side) matched U4, so within two pages above U4 neither ending is given
        assert_eq!(full_triangle_4x_pages(992, 1280), 311);
        assert_eq!(full_triangle_4x_pages(1184, 768), 223);
        let at = |p| four_array_4x_ending(992, 1280, 992, 1280, p);
        assert_eq!(at(0x22 + 313), Some(Ending4x::Complete));
        assert_eq!(at(0x22 + 312), None);
        assert_eq!(at(0x22 + 311), None);
        assert_eq!(at(0x22 + 310), Some(Ending4x::Enospc));
        // a shape that matched U4 keeps its exact boundary (E866: 1024 x 768 at 0xe3 and 0xe2)
        assert_eq!(four_array_4x_ending(1024, 768, 1024, 768, 0xe3), Some(Ending4x::Complete));
        assert_eq!(four_array_4x_ending(1024, 768, 1024, 768, 0xe2), Some(Ending4x::Enospc));
    }

    #[test]
    fn one_moved_triangle_needs_hu1_s_pages_at_the_scenes_r7_dpm_ran() {
        // E916 [HW]: s-b's calibrations at P 0x422 needed HU1's U with no partial render
        for (w, h, dx, dy, u) in [
            (4096, 4096, 0, 2304, 157),
            (4096, 4096, 2048, 1792, 131),
            (4096, 2048, 768, 256, 145),
            (2048, 2048, 0, 384, 78),
            (1024, 768, 64, 64, 22),
        ] {
            assert_eq!(one_triangle_page_need(w, h, dx, dy), u, "{w}x{h} move {dx},{dy}");
        }
    }

    #[test]
    fn the_walk64_replay_gives_the_held_out_counts_and_run_peaks_of_r7_dpm() {
        // E916 [HW, held out]: every cell of s44a, s44b, s42 and s22, the g-qf control (E832's
        // 4096x4096 scene at P 0xa2) and the s17 cells whose first run was sampled; (thr0,
        // partial renders, each TA run's peak of the 0x0724 page count)
        type Cell = (u32, u32, &'static [u32]);
        let cells: &[(u32, u32, u32, u32, &[Cell])] = &[
            (
                4096,
                4096,
                0,
                2304,
                &[
                    (0x2, 5, &[0x2, 0x22, 0x22, 0x22, 0x22, 0x1a]),
                    (0x7, 4, &[0x7, 0x27, 0x27, 0x27, 0x27]),
                    (0x20, 3, &[0x20, 0x40, 0x40, 0x3]),
                    (0x30, 2, &[0x30, 0x50, 0x21]),
                    (0x65, 1, &[0x65, 0x3a]),
                    (0x9a, 1, &[0x9a, 0x5]),
                ],
            ),
            (
                4096,
                4096,
                2048,
                1792,
                &[
                    (0x3, 4, &[0x3, 0x23, 0x23, 0x23, 0x1b]),
                    (0x17, 3, &[0x17, 0x37, 0x37, 0x2]),
                    (0x1b, 2, &[0x1b, 0x3b, 0x2f]),
                    (0x32, 1, &[0x32, 0x52]),
                    (0x3e, 1, &[0x3e, 0x46]),
                    (0x81, 1, &[0x81, 0x3]),
                ],
            ),
            (
                4096,
                2048,
                768,
                256,
                &[
                    (0x5, 4, &[0x5, 0x25, 0x25, 0x25, 0x24]),
                    (0xd, 3, &[0xd, 0x2d, 0x2d, 0x2d]),
                    (0x1c, 2, &[0x1c, 0x3c, 0x3c]),
                    (0x45, 1, &[0x45, 0x4d]),
                ],
            ),
            (
                2048,
                2048,
                0,
                384,
                &[
                    (0x2, 3, &[0x2, 0x22, 0x22, 0xb]),
                    (0x6, 2, &[0x6, 0x26, 0x26]),
                    (0x18, 1, &[0x18, 0x37]),
                    (0x49, 1, &[0x49, 0x7]),
                ],
            ),
            (1024, 768, 64, 64, &[(0x2, 1, &[0x2, 0x15]), (0xe, 1, &[0xe, 0x9]), (0x15, 1, &[0x15, 0x3])]),
            (4096, 4096, 0, 0, &[(0x80, 2, &[0x80, 0xa0, 0x2])]),
        ];
        for &(w, h, dx, dy, rows) in cells {
            for &(thr0, n, peaks) in rows {
                let got = one_triangle_partial_renders(w, h, dx, dy, thr0);
                assert_eq!(got, Some((n, peaks.to_vec())), "{w}x{h} move {dx},{dy} thr0 {thr0:#x}");
            }
        }
        // s17 0x9: one partial render, the second run's peak 0xe; the timeline has no sample in the
        // first run (E916, read post hoc), the replay's first peak is the threshold
        assert_eq!(one_triangle_partial_renders(1024, 768, 64, 64, 0x9), Some((1, vec![0x9, 0xe])));
    }

    #[test]
    fn a_one_triangle_count_outside_what_was_held_out_is_refused() {
        // a target no held-out scene ran, a threshold below 2 (no page past the global one) or at
        // the clamp; a scene that fits its threshold takes no partial render
        assert_eq!(one_triangle_partial_renders(3072, 3072, 0, 0, 0x40), None);
        assert_eq!(one_triangle_partial_renders(4096, 4096, 0, 2304, 1), None);
        assert_eq!(one_triangle_partial_renders(4096, 4096, 0, 2304, 0x400), None);
        assert_eq!(one_triangle_partial_renders(2048, 2048, 0, 384, 78), Some((0, vec![78])));
    }

    #[test]
    fn the_first_partial_render_keeps_two_global_pages_up_to_the_straddling_block() {
        // E915 [HW, held out] H-SPAN: 1500 vertices of the tool's triangle, the pages left by the
        // first partial render at the cells of s-m (and s-a0's 2048x2048 controls); 2 iff
        // S_k < thr0 < A_k, where E874's burst end B_k gave 1 at the 19 discriminating cells
        type Row = (u32, u32);
        let cells: &[(u32, u32, &[Row])] = &[
            (
                3072,
                3072,
                &[(0x329, 2), (0x32a, 2), (0x32b, 2), (0x32c, 2), (0x32d, 2), (0x32e, 2), (0x32f, 1)],
            ),
            (
                3072,
                2048,
                &[
                    (0x14c, 2),
                    (0x14d, 1),
                    (0x224, 2),
                    (0x225, 2),
                    (0x226, 2),
                    (0x227, 2),
                    (0x228, 2),
                    (0x229, 1),
                ],
            ),
            (
                2048,
                3072,
                &[(0x14e, 2), (0x14f, 1), (0x229, 2), (0x22a, 2), (0x22b, 2), (0x22c, 2), (0x22d, 1)],
            ),
            (2560, 2560, &[(0x157, 2), (0x158, 1)]),
            (1024, 1024, &[(0x40, 2), (0x41, 1), (0x6a, 2), (0x6b, 2), (0x6c, 2), (0x6d, 1)]),
            (
                2048,
                2048,
                &[
                    (0x97, 1),
                    (0xe2, 2),
                    (0xe3, 1),
                    (0xe9, 2),
                    (0x140, 2),
                    (0x177, 2),
                    (0x178, 1),
                    (0x1c2, 2),
                    (0x1c3, 1),
                    (0x20c, 2),
                    (0x20d, 1),
                ],
            ),
        ];
        for &(w, h, rows) in cells {
            for &(thr0, left) in rows {
                assert_eq!(
                    first_partial_render_global_pages_left(w, h, thr0),
                    Some(left),
                    "{w}x{h} thr0 {thr0:#x}"
                );
            }
        }
    }

    #[test]
    fn the_span_rule_is_refused_where_it_failed_or_was_not_held_out() {
        // E915: band 6 of 3072x3072 and 2560x2560 left 2 pages at A_k (0x3cf, 0x2b1); a step cell
        // (a grow, not scored), a band no frozen cell ran, a target no held-out cell ran
        assert_eq!(first_partial_render_global_pages_left(3072, 3072, 0x3cf), None);
        assert_eq!(first_partial_render_global_pages_left(2560, 2560, 0x2b1), None);
        assert_eq!(first_partial_render_global_pages_left(2048, 2048, 0x9d), None);
        assert_eq!(first_partial_render_global_pages_left(2048, 3072, 0x240), None);
        assert_eq!(first_partial_render_global_pages_left(2048, 4096, 0x24a), None);
    }

    #[test]
    fn the_step_replay_gives_the_steps_and_need_of_the_held_out_calibrations() {
        // E915 [HW, held out] H-STEPMODEL: E874's block-level replay (lag 3) at the s-m targets;
        // 2048x3072's S6 read 0x234 against 0x233, so that target is refused
        let cal: &[(u32, u32, &[u32], Option<u32>)] = &[
            (3072, 3072, &[0xa9, 0x14d, 0x1ef, 0x293, 0x335, 0x3d9], None),
            (3072, 2048, &[0x77, 0xe2, 0x150, 0x1bf, 0x22c, 0x299], Some(0x305)),
            (2560, 2560, &[0x7a, 0xeb, 0x15c, 0x1d4, 0x244, 0x2b6], Some(0x328)),
            (1024, 1024, &[0x1c, 0x30, 0x45, 0x5a, 0x6f, 0x86], Some(0x99)),
            (2048, 2048, &[0x51, 0x9d, 0xe8, 0x132, 0x181, 0x1ca], Some(0x213)),
        ];
        for &(w, h, steps, need) in cal {
            let (s, u) = tool_triangle_steps(w, h).expect("a held-out target");
            assert_eq!(s, steps, "{w}x{h}");
            // 3072x3072 needs 0x479 pages by the replay, above the clamp: its need was not read
            if let Some(need) = need {
                assert_eq!(u, need, "{w}x{h}");
            }
        }
        assert_eq!(tool_triangle_steps(2048, 3072), None);
        assert_eq!(tool_triangle_steps(2048, 4096), None);
    }

    #[test]
    fn the_stub_refuses_and_names_its_questions() {
        match refuse() {
            Outcome::Unsupported { ids, why } => {
                assert!(!ids.is_empty() && !why.is_empty());
                assert_eq!(ids, OPEN);
            }
            o => panic!("{o:?}"),
        }
    }

    #[test]
    fn the_step_replay_holds_at_r8_ldpm_s_new_calibration_targets() {
        // E936 [HW, held out] H-STEPMODEL at r8-ldpm's m6 and f9 calibrations: 1536x1536 and
        // 4096x2048 never run before, every step in its bracket and the need as replayed
        let cal: &[(u32, u32, &[u32], u32)] = &[
            (1536, 1536, &[0x32, 0x5d, 0x8a, 0xb7, 0xe1, 0x10e], 0x13a),
            (4096, 2048, &[0x97, 0x126, 0x1b9, 0x24a, 0x2db, 0x36c], 0x3f7),
        ];
        for &(w, h, steps, need) in cal {
            assert_eq!(tool_triangle_steps(w, h), Some((steps.to_vec(), need)), "{w}x{h}");
        }
        // E935: 2048x3072's S6 is 0x234 and 2048x4096's S3 0x12c, pinned by the abort's global
        // page count; E936: 2560x3072's S6 (0x2b4) and 3072x2560's S3 and S6 (0x116, 0x2b0) are
        // off the replay too: refused
        for (w, h) in [(2048, 3072), (2048, 4096), (2560, 3072), (3072, 2560)] {
            assert_eq!(tool_triangle_steps(w, h), None, "{w}x{h}");
        }
    }

    #[test]
    fn the_span_rule_holds_at_band_6_of_3072x2048_and_is_refused_where_band_6_kept_two() {
        // E936 [HW, held out]: 3072x2048 left 2 global pages at A_6 - 1 (0x292) and 1 from A_6
        // (0x293) to A_6 + 3; band 6 kept the second page past A_6 at 1536x1536 (to A_6 + 1),
        // 4096x2048 (A_6) and, post hoc, 3072x3072 and 2560x2560 again: refused there
        for (thr0, left) in [(0x292, 2), (0x293, 1), (0x294, 1), (0x295, 1), (0x296, 1)] {
            assert_eq!(first_partial_render_global_pages_left(3072, 2048, thr0), Some(left), "{thr0:#x}");
        }
        assert_eq!(first_partial_render_global_pages_left(1536, 1536, 0x109), None);
        assert_eq!(first_partial_render_global_pages_left(4096, 2048, 0x362), None);
    }

    #[test]
    fn the_step_replay_holds_at_r9_ldpm_s_new_calibration_targets() {
        // E961, E963 [HW, held out] H-STEPMODEL at r9-ldpm's m6b and f9b calibrations: every step
        // in its bracket and the need as replayed
        let cal: &[(u32, u32, &[u32], u32)] = &[
            (2304, 2304, &[0x64, 0xc2, 0x11f, 0x17f, 0x1dd, 0x23c], 0x298),
            (2304, 1792, &[0x50, 0x99, 0xe4, 0x12c, 0x177, 0x1c2], 0x208),
            (1792, 1792, &[0x41, 0x7b, 0xb5, 0xf2, 0x12b, 0x165], 0x19f),
            (1280, 1280, &[0x26, 0x45, 0x64, 0x85, 0xa6, 0xc4], 0xe2),
            (2560, 2048, &[0x63, 0xbd, 0x11b, 0x179, 0x1d4, 0x230], 0x28c),
        ];
        for &(w, h, steps, need) in cal {
            assert_eq!(tool_triangle_steps(w, h), Some((steps.to_vec(), need)), "{w}x{h}");
        }
        // E961: 2048x2304's S3 and S6 read one page above the replay (0xae, 0x1ad); E962: the
        // four wide targets' S6 (and 4096x1536's S3) one or two above, their needs the replay's:
        // refused, as a pair of steps and need
        for (w, h) in [(2048, 2304), (4096, 1024), (4096, 1536), (3584, 1024), (2048, 512)] {
            assert_eq!(tool_triangle_steps(w, h), None, "{w}x{h}");
        }
    }

    #[test]
    fn band_6_keeps_the_second_page_until_the_object_after_the_straddling_block_e961() {
        // E961 [HW, held out] H-NEXT1 (E960's OD-2): band 6 leaves 2 global pages iff
        // S_6 < thr0 < the page count once object b_6 + 1 is tiled; 20 of 20 cells at four
        // targets never run, three where it parts from H-SPAN's A_6 (A_6 + 2, + 3, + 1)
        let cells: &[(u32, u32, &[(u32, u32)])] = &[
            (2304, 2304, &[(0x232, 2), (0x233, 2), (0x234, 2), (0x235, 1), (0x236, 1)]),
            (2048, 2304, &[(0x1f6, 2), (0x1f7, 2), (0x1f8, 2), (0x1f9, 2), (0x1fa, 1)]),
            (2304, 1792, &[(0x1b9, 2), (0x1ba, 2), (0x1bb, 1), (0x1bc, 1), (0x1bd, 1)]),
            (1792, 1792, &[(0x160, 2), (0x161, 1), (0x162, 1), (0x163, 1), (0x164, 1)]),
        ];
        for &(w, h, cs) in cells {
            for &(thr0, left) in cs {
                assert_eq!(
                    first_partial_render_global_pages_left(w, h, thr0),
                    Some(left),
                    "{w}x{h} {thr0:#x}"
                );
            }
        }
        // the ends where the margin was held before: 2048x2048 and 3072x2048 (b_6 + 1 adds no page)
        assert_eq!(first_partial_render_global_pages_left(2048, 2048, 0x1c2), Some(2));
        assert_eq!(first_partial_render_global_pages_left(2048, 2048, 0x1c3), Some(1));
        assert_eq!(first_partial_render_global_pages_left(3072, 2048, 0x293), Some(1));
        // the fit and SEMI targets of E960 stay refused at band 6 (not held out)
        assert_eq!(first_partial_render_global_pages_left(3072, 3072, 0x3d0), None);
        assert_eq!(first_partial_render_global_pages_left(1536, 1536, 0x10a), None);
    }

    #[test]
    fn scenes_of_several_kicks_and_other_shapes_need_hu1_s_pages_of_the_union() {
        // E939 [HW, held out]: r8-ldpm's k calibrations (the default triangle and K - 1 copies
        // moved by i (DX, DY), --geometry for all but the last kick; a region counted once) and
        // u's eight one-triangle shapes (--tri-unit 12 --tri-v, in 1/4096 pixel) needed HU1's U
        // with no partial render at P 0x422
        let moved = |w: u32, h: u32, k: i32, dx: f64, dy: f64| -> Vec<crate::ta::Tri> {
            (0..k).map(|i| default_triangle(w, h, i as f64 * dx, i as f64 * dy)).collect()
        };
        for (w, h, k, dx, dy, u) in [
            (2048, 2048, 2, 256.0, -256.0, 108),
            (2048, 2048, 3, -256.0, -256.0, 131),
            (2048, 2048, 4, 256.0, 0.0, 136),
            (4096, 4096, 2, 0.0, -512.0, 377),
            (4096, 4096, 4, -512.0, -512.0, 492),
        ] {
            assert_eq!(scene_page_need(w, h, &moved(w, h, k, dx, dy)), u, "{w}x{h} K {k}");
        }
        let v = |p: [i64; 6]| -> crate::ta::Tri {
            let f = |x: i64| x as f64 / 4096.0;
            [(f(p[0]), f(p[1])), (f(p[2]), f(p[3])), (f(p[4]), f(p[5]))]
        };
        for (w, h, p, u) in [
            (1024, 768, [0, 0, 8388608, 0, 0, 6291456], 49),
            (2048, 2048, [0, 0, 16777216, 0, 0, 16777216], 257),
            (2048, 2048, [32768, 32768, 8355840, 8339456, 8339456, 8355840], 15),
            (2048, 2048, [4096000, 4096000, 4177920, 4112384, 4112384, 4177920], 2),
            (4096, 2048, [65536, 4096000, 16711680, 4177920, 8388608, 4259840], 11),
            (4096, 2048, [32768, 32768, 16744448, 8339456, 16728064, 8355840], 15),
            (2048, 4096, [32768, 32768, 8355840, 16728064, 8339456, 16744448], 17),
            (2048, 2048, [8355840, 32768, 49152, 8355840, 32768, 8339456], 15),
        ] {
            assert_eq!(scene_page_need(w, h, &[v(p)]), u, "{w}x{h} {p:?}");
        }
    }
}
