// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! ISP: coverage and depth of a triangle (12.3, E606, E607) and the multisample store window of a
//! tile (E503). The coverage rule and the vertex grid are the records' fits, reported fitted; the
//! depth plane has no bit-exact model and is reported `Near` with the record's tolerance. Coverage
//! alone is admitted on E680's ten and E913's ten further targets as well (`coverage_image`); the
//! depth there is not: 1- and 2-pixel triangles missed E606's tolerance on them (E912, E913; Q262,
//! Q240).

use crate::Outcome;

pub const OPEN: &[&str] =
    &["Q066", "Q086", "Q089", "Q199", "Q200", "Q202", "Q240", "Q241", "Q262", "Q071", "Q073", "Q032"];

pub fn refuse() -> Outcome {
    Outcome::unsupported("the ISP past triangle coverage and depth is not modelled (12.3)", OPEN)
}

/// The vertex grid: 1/256 pixel (E607).
pub const GRID: i64 = 256;
/// The depth unit of E606's tolerance: 2^-23, absolute.
pub const DEPTH_UNIT: f64 = 1.0 / 8388608.0;
/// E606: 3 units where the plane's gradient |dz/dx| + |dz/dy| is below 0.03.
pub const DEPTH_TOLERANCE: u32 = 3;
pub const DEPTH_GRADIENT_LIMIT: f64 = 0.03;

/// A triangle on the ISP's grid: window vertices in 1/256 pixel, y down, and the depth of each.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Tri {
    pub v: [(i64, i64); 3],
    pub z: [f32; 3],
}

fn open(why: impl AsRef<str>, id: &str) -> Outcome {
    Outcome::unsupported(why.as_ref(), &[id])
}

/// floor(256 c + 0.5): the vertex grid and its rounding (E607), exact for c >= 0. A negative
/// coordinate with a sub-grid fraction refuses (Q199, Q260): its tie rounds away from zero (E914,
/// E943), but the pixels within 6.4e-4 pixel of a long edge go either way (E943, held out on
/// none; on E683 neither E943's far-vertex reading nor its band is a rule, and no fixed-point
/// edge evaluation fitted on E914 and E943 beats the exact one, E952), so no image of such a
/// vertex is exact; on the grid it converts exactly.
pub fn snap(c: f64) -> Result<i64, Outcome> {
    if !c.is_finite() || c.abs() > 1.0e6 {
        return Err(open(
            format!("window coordinate {c}: not a finite coordinate of the tested range"),
            "Q199",
        ));
    }
    let q = c * GRID as f64;
    if c < 0.0 && q.fract() != 0.0 {
        return Err(Outcome::unsupported(
            &format!(
                "window coordinate {c}: negative with a sub-grid fraction, rounded away from zero at a tie (E914, E943), but the pixels near a long edge are not modelled"
            ),
            &["Q199", "Q260"],
        ));
    }
    Ok((q + 0.5).floor() as i64)
}

/// The target shapes E606 ran, in pixels: 64 x 64, 128 x 128 and 256 x 128. Only these are
/// admitted for coverage and depth together (r123 item 3): the family around them (64 x 128,
/// 256 x 64, targets below one tile) was not run, so it refuses (Q240), as does any width or
/// height past them. The sizes of E662 (the library's triangle only) are inside this set only
/// where E606 ran them.
pub const E606_TARGETS: [(u32, u32); 3] = [(64, 64), (128, 128), (256, 128)];

/// The ten targets E680 ran the coverage rule on (590 random triangles, 0 of 1092224240 pixels
/// wrong, 410 cases held out): admitted for coverage only. R7-geo's depth jobs on four of them and
/// 4096 x 4096 drew E606's coverage and stored the whole tile area, but 6 of 100 triangles, each
/// covering 1 or 2 pixels, stored a depth more than E606's 3 units off the plane, and 3 of 24
/// iterated clip z more than 4 (E912): the depth and the iterated attributes refuse (Q262).
pub const E680_TARGETS: [(u32, u32); 10] = [
    (96, 64),
    (130, 66),
    (200, 120),
    (512, 256),
    (512, 512),
    (640, 480),
    (1000, 600),
    (1024, 768),
    (2048, 1024),
    (4096, 4096),
];

/// The ten targets around E606's that R7-geo's zf ran the rule on, coverage and depth (24 random
/// triangles each, 240 of 240 images and triangle counts as the rule, held out; E913): admitted
/// for coverage only: 12 of 240 triangles of 1 or 2 pixels stored a depth more than 3 units off,
/// so the depth there, and with it a render, refuses (Q240). Two have odd heights (the userspace
/// tool refuses odd widths, Q240).
pub const E913_TARGETS: [(u32, u32); 10] = [
    (64, 128),
    (128, 64),
    (256, 64),
    (128, 96),
    (128, 144),
    (32, 16),
    (16, 8),
    (4096, 16),
    (64, 33),
    (96, 47),
];

/// The envelope of coverage and depth together: E606's three targets; E680's ten refuse naming
/// Q262 (the depth there missed E606's tolerance on 1- and 2-pixel triangles, E912), the rest
/// Q240 (E913's ten as well: the same miss).
pub fn target_in_envelope(w: u32, h: u32) -> Result<(), Outcome> {
    if E680_TARGETS.contains(&(w, h)) {
        return Err(open(
            format!(
                "a {w} x {h} target: the coverage rule holds there, but 1- and 2-pixel triangles stored a depth outside E606's tolerance (E912)"
            ),
            "Q262",
        ));
    }
    if !E606_TARGETS.contains(&(w, h)) {
        return Err(open(
            format!(
                "a {w} x {h} target: E606 ran 64 x 64, 128 x 128 and 256 x 128 only; the coverage and depth rules are not shown for it"
            ),
            "Q240",
        ));
    }
    Ok(())
}

/// The envelope of coverage alone: E606's three targets, E680's ten and E913's ten.
pub fn coverage_target_in_envelope(w: u32, h: u32) -> Result<(), Outcome> {
    if !E606_TARGETS.contains(&(w, h)) && !E680_TARGETS.contains(&(w, h)) && !E913_TARGETS.contains(&(w, h)) {
        return Err(open(
            format!(
                "a {w} x {h} target: the coverage rule ran on E606's three, E680's ten and E913's ten targets only (odd widths, sizes between them and past 4096 not run)"
            ),
            "Q240",
        ));
    }
    Ok(())
}

/// The vertex envelope of coverage: E606's range on every target, and at 4096 x 4096 no
/// negative x (E680 drew none there: x from +5% to +121%, y from -8%).
pub fn coverage_vertices_in_envelope(w: u32, h: u32, t: &Tri) -> Result<(), Outcome> {
    vertices_in_envelope(w, h, t)?;
    if (w, h) == (4096, 4096) && t.v.iter().any(|&(x, _)| x < 0) {
        return Err(open("a negative x on a 4096 x 4096 target: E680 drew none there", "Q199"));
    }
    Ok(())
}

/// The coverage of a triangle on a target, row by row, inside the coverage envelope: E606's rule
/// (`Tri::covers`), which E680 and E913 confirmed on their ten targets each with no change.
pub fn coverage_image(w: u32, h: u32, t: &Tri) -> Result<Vec<bool>, Outcome> {
    coverage_target_in_envelope(w, h)?;
    coverage_vertices_in_envelope(w, h, t)?;
    Ok((0..h).flat_map(|y| (0..w).map(move |x| t.covers(x, y))).collect())
}

/// A triangle with one or two vertices far outside the target, in 1/256 pixel on the grid (E684,
/// E979): the coordinates need more than i64 products, so it is its own type.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct FarTri {
    pub v: [(i64, i64); 3],
}

/// The far-vertex targets that ran: 64 x 64 (E684, E979) and 512 x 512 (E684).
pub const FAR_TARGETS: [(u32, u32); 2] = [(64, 64), (512, 512)];
/// The coordinate range a far vertex ran over, in pixels: -2^25 to +2^24 (E979: +-2^22, +-2^23,
/// +-2^24 and -2^25 in x or y; the tool reaches no further in its 1/32 unit).
pub const FAR_LOW: i64 = -(1 << 25);
pub const FAR_HIGH: i64 = 1 << 24;
/// E684's band: a pixel centre within 1e-3 pixel of an edge line is undetermined.
pub const FAR_BAND: f64 = 1.0e-3;

/// The coverage of a triangle with one or two vertices outside the target, row by row: the exact
/// rule of E606/E607 (centres strictly inside, ties to the left and top edges, either winding) at
/// every pixel whose centre is 1e-3 pixel or more from an edge line, and `None` inside that band
/// (E684: the 16 pixels it got wrong lay within 5.6e-4 pixel). E979 held this at one vertex up to
/// 2^24 pixels both ways and -2^25, and at two vertices at +-2^23 and +-2^24, 10 of 10 rows: no
/// clamp or wrap of a 24.8 word (H-SAT, H-WRAP refuted). Inside the band E979's rows drew exactly
/// the pixels on a far edge between its near vertex and the far one (E984, post hoc, 26 of 46 on
/// three rows: as if the far vertex sat tens of pixels away); E1005 held the exact coverage outside
/// the band on 36 more rows (E979's x23p, x24p and x25n with the far vertex's y moved by 0 to -544
/// pixels) and read the band as a displacement D of the far vertex along y that fits each
/// triangle's rows but differs between them (x24p: 339 to 467 pixels; x23p and x25n: above 586)
/// and is not one angle. E1012 (round 11 offline, post hoc, no held-out row) fits all 48 of those
/// rows with one integer: the far edges clipped to a guard x in [-G, 64 + G] (G 16 to 22 fit; the
/// lower bound fits anywhere from -8 to -32, the y bounds untested), each new vertex rounded half
/// up to 1/256, the edges then exact; being fitted, the band stays `None`. Refuses other
/// targets, three far vertices and the band's own form (Q261), and coordinates past what ran
/// (Q199).
pub fn far_coverage_image(w: u32, h: u32, t: &FarTri) -> Result<Vec<Option<bool>>, Outcome> {
    if !FAR_TARGETS.contains(&(w, h)) {
        return Err(open(
            format!("far vertices on a {w} x {h} target: E684 and E979 ran 64 x 64 and 512 x 512"),
            "Q261",
        ));
    }
    let far = |&(x, y): &(i64, i64)| {
        let inside = |c: i64, s: u32| (0..=GRID * s as i64).contains(&c);
        !(inside(x, w) && inside(y, h))
    };
    if t.v.iter().filter(|v| far(v)).count() > 2 {
        return Err(open("three far vertices: E979 ran one or two", "Q261"));
    }
    for &(x, y) in &t.v {
        for c in [x, y] {
            if !(FAR_LOW * GRID..=FAR_HIGH * GRID).contains(&c) {
                return Err(open(
                    format!(
                        "a vertex coordinate of {} pixels: E979 ran -2^25 to +2^24",
                        c as f64 / GRID as f64
                    ),
                    "Q199",
                ));
            }
        }
    }
    let v: Vec<(i128, i128)> = t.v.iter().map(|&(x, y)| (x as i128, y as i128)).collect();
    let area = (v[1].0 - v[0].0) * (v[2].1 - v[0].1) - (v[2].0 - v[0].0) * (v[1].1 - v[0].1);
    let v = if area < 0 { [v[0], v[2], v[1]] } else { [v[0], v[1], v[2]] };
    let band = 1.0 / FAR_BAND;
    let mut out = Vec::with_capacity((w * h) as usize);
    for y in 0..h {
        for x in 0..w {
            if area == 0 {
                out.push(Some(false));
                continue;
            }
            let (px, py) = ((GRID * x as i64 + GRID / 2) as i128, (GRID * y as i64 + GRID / 2) as i128);
            let mut inside = true;
            let mut near = false;
            for i in 0..3 {
                let (a, b) = (v[i], v[(i + 1) % 3]);
                let (dx, dy) = (b.0 - a.0, b.1 - a.1);
                let e = dx * (py - a.1) - dy * (px - a.0);
                inside &= e > 0 || (e == 0 && (dy < 0 || (dy == 0 && dx > 0)));
                // the centre's distance to the edge line, |e| / (256 |d|), below 1e-3 pixel
                let (ef, df) = (e as f64, ((dx * dx + dy * dy) as f64).sqrt());
                near |= ef.abs() * band < GRID as f64 * df;
            }
            out.push(if near { None } else { Some(inside) });
        }
    }
    Ok(out)
}

/// The range of E606's vertices, as fractions of the target: -8.9% to +124.1%.
const RANGE_LOW: f64 = -0.09;
const RANGE_HIGH: f64 = 1.241;

/// Whether the vertices lie in the range E606 tested (about -9% to +124% of the target).
pub fn vertices_in_envelope(w: u32, h: u32, t: &Tri) -> Result<(), Outcome> {
    for &(x, y) in &t.v {
        for (c, size) in [(x, w), (y, h)] {
            let f = c as f64 / (GRID as f64 * size as f64);
            if !(RANGE_LOW..=RANGE_HIGH).contains(&f) {
                return Err(open(
                    format!(
                        "a vertex at {:.3} of the {w} x {h} target: E606 tested -9% to +124% (far vertices: far_coverage_image, E979)",
                        f
                    ),
                    "Q199",
                ));
            }
        }
    }
    Ok(())
}

impl Tri {
    /// Twice the signed area in (1/256 pixel)^2, positive when the vertices go clockwise on the
    /// screen (y down).
    pub fn area2(&self) -> i64 {
        let [a, b, c] = self.v;
        (b.0 - a.0) * (c.1 - a.1) - (c.0 - a.0) * (b.1 - a.1)
    }

    fn normalised(&self) -> [(i64, i64); 3] {
        let [a, b, c] = self.v;
        if self.area2() < 0 { [a, c, b] } else { [a, b, c] }
    }

    /// Whether the pixel (x, y) is covered: its centre exactly inside the triangle, a centre on an
    /// edge belongs to the triangle iff the edge is a left or a top edge (E606). Zero area: never.
    pub fn covers(&self, x: u32, y: u32) -> bool {
        if self.area2() == 0 {
            return false;
        }
        let v = self.normalised();
        let (px, py) = (GRID * x as i64 + GRID / 2, GRID * y as i64 + GRID / 2);
        (0..3).all(|i| {
            let (a, b) = (v[i], v[(i + 1) % 3]);
            let (dx, dy) = (b.0 - a.0, b.1 - a.1);
            // for a clockwise (positive) triangle the inside has e > 0; the edge owns the tie iff it
            // runs up the screen, or along the top (R4 of E606)
            let e = dx * (py - a.1) - dy * (px - a.0);
            e > 0 || (e == 0 && (dy < 0 || (dy == 0 && dx > 0)))
        })
    }

    /// The plane's depth at the centre of pixel (x, y), exact (f64 over exact integer products).
    pub fn depth_at(&self, x: u32, y: u32) -> f64 {
        let area = self.area2();
        if area == 0 {
            return self.z[0] as f64;
        }
        let [a, b, c] = self.v;
        let (px, py) = (GRID * x as i64 + GRID / 2, GRID * y as i64 + GRID / 2);
        // barycentric weights of b and c: cross products over the area
        let wb = (px - a.0) * (c.1 - a.1) - (c.0 - a.0) * (py - a.1);
        let wc = (b.0 - a.0) * (py - a.1) - (px - a.0) * (b.1 - a.1);
        let z0 = self.z[0] as f64;
        z0 + ((self.z[1] as f64 - z0) * wb as f64 + (self.z[2] as f64 - z0) * wc as f64) / area as f64
    }

    /// |dz/dx| + |dz/dy| of the plane, per pixel.
    pub fn gradient(&self) -> f64 {
        let area = self.area2();
        if area == 0 {
            return f64::INFINITY;
        }
        let [a, b, c] = self.v;
        let (z0, z1, z2) = (self.z[0] as f64, self.z[1] as f64, self.z[2] as f64);
        // dz/dx and dz/dy per 1/256 pixel, then per pixel
        let dzdx = ((z1 - z0) * (c.1 - a.1) as f64 - (z2 - z0) * (b.1 - a.1) as f64) / area as f64;
        let dzdy = ((z2 - z0) * (b.0 - a.0) as f64 - (z1 - z0) * (c.0 - a.0) as f64) / area as f64;
        (dzdx.abs() + dzdy.abs()) * GRID as f64
    }
}

/// The depth comparison of ISP word 0 bits 24:22 in the GL order (E072, E995, 3d.md 11.1), the
/// object's depth on the left.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Cmp {
    Never,
    Less,
    Equal,
    LessEqual,
    Greater,
    NotEqual,
    GreaterEqual,
    Always,
}

/// What an object's ISP words say about a pixel it covers (12.3).
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Mode {
    /// ISP0 bits 27:25
    pub pass: u32,
    pub cmp: Cmp,
    /// ISP0 bit 20 clear
    pub depth_write: bool,
    /// ISP0 bit 21 clear: the object leaves its tag (colour) where it wins; set, it only writes depth
    pub tag_write: bool,
    /// removed whole: pass types 3 and 7 (E065), or ISP1 bits 31:26 under CR_ISP_CTL bits 5:0 for
    /// an opaque or translucent pass (E232, E235)
    pub removed: bool,
}

/// The library's ISP word 1 with bits 31:26 clear: line width 0x10, bits 7:4 set.
const ISP1_LIBRARY: u32 = 0x10f0;

/// CR_ISP_CTL bits 5:0 values E232 ran with the library's ISP word 1 (gate 0): 0, 1 to 8, 16, 32, 63.
const E232_THRESHOLDS: [u32; 12] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 16, 32, 63];

/// The (pass type, ISP1 bits 31:26, CR_ISP_CTL bits 5:0) triples a record measured (r123 item 5):
/// E232 for the library's gate 0 at every threshold above, pass types 0, 1, 2, 4, 5, 6 (the
/// pass types 2, 4, 5, 6 draw whatever the threshold); E235 for gate 0 and 63 at the thresholds 1
/// and 63, pass types 0, 2, 4, 5, 6. Pass types 3 and 7 were run with the library's words only.
/// Every other triple refuses: the comparison between the pairs is inference.
pub fn gate_measured(pass: u32, gate: u32, thr: u32) -> bool {
    match pass {
        3 | 7 => (gate, thr) == (0, 0),
        0 | 2 | 4 | 5 | 6 => {
            (gate == 0 && E232_THRESHOLDS.contains(&thr)) || (gate == 63 && (thr == 1 || thr == 63))
        }
        1 => gate == 0 && E232_THRESHOLDS.contains(&thr),
        _ => false,
    }
}

/// Decode an object's ISP words under `CR_ISP_CTL` (`ctl`), for `nprims` triangles in the object.
/// What no record settles refuses: the stencil words (Q071), the bits and compares that were
/// inferred or not separated (Q241), the passes of several triangles (Q073, Q032).
pub fn decode_words(isp: [u32; 2], ctl: u32, nprims: usize) -> Result<Mode, Outcome> {
    let [w0, w1] = isp;
    if w0 & 0x0900 != 0 || w0 & 0xff != 0 {
        return Err(open(
            "ISP word 0 with a stencil reference, the stencil word present or two-sided stencil: not modelled",
            "Q071",
        ));
    }
    // bits 15 to 17 changed the image when flipped (48 pixels left, empty: E065), each removed
    // E977's ramp triangle under less with writes (E998: one vertex order), and bit 18 faults
    if w0 & 0x0007_8000 != 0 {
        return Err(open(
            format!(
                "ISP word 0 bit 15 to 18 set ({w0:#x}): E065 saw a changed image, no pixels or a fault, E998 the triangle removed on one vertex order"
            ),
            "Q241",
        ));
    }
    // bit 28 adds samples to the object's coverage (E214, E224): multisample positions are not E606's
    if w0 >> 28 & 1 != 0 {
        return Err(open("ISP word 0 bit 28: samples beyond the pixel centre (E214, E224)", "Q202"));
    }
    if w1 & !(0x3f << 26) != ISP1_LIBRARY {
        return Err(open(
            format!(
                "ISP word 1 {w1:#x}: only the library's low bits are modelled (a visibility test, the polygon offset or other bits change what is counted or drawn; E998 saw bits 3 and 23 change nothing on one ramp)"
            ),
            "Q241",
        ));
    }
    // the GL order, exact on equal depths (E995: 14 of 14 held out; E072 on unequal depths)
    let cmp = match w0 >> 22 & 7 {
        0 => Cmp::Never,
        1 => Cmp::Less,
        2 => Cmp::Equal,
        3 => Cmp::LessEqual,
        4 => Cmp::Greater,
        5 => Cmp::NotEqual,
        6 => Cmp::GreaterEqual,
        _ => Cmp::Always,
    };
    let pass = w0 >> 25 & 7;
    let (gate, thr) = (w1 >> 26 & 0x3f, ctl & 0x3f);
    if !gate_measured(pass, gate, thr) {
        return Err(open(
            format!(
                "pass type {pass} with ISP word 1 bits 31:26 = {gate} under CR_ISP_CTL bits 5:0 = {thr}: E232 and E235 measured other pairs only"
            ),
            "Q241",
        ));
    }
    let removed = match pass {
        3 | 7 => true,
        // opaque and translucent passes are removed when ISP1 bits 31:26 are below CR_ISP_CTL bits 5:0
        // (E232, E235: read as a comparison from the pairs below, [infer])
        0 | 1 => gate < thr,
        _ => false,
    };
    if pass != 0 && nprims > 1 && !removed {
        let q = match pass {
            1 => "Q073",
            4 | 5 => "Q032",
            _ => "Q241",
        };
        return Err(open(
            format!(
                "pass type {pass} with {nprims} triangles in an object: only a single triangle was shown to draw as an opaque one (E065)"
            ),
            q,
        ));
    }
    Ok(Mode { pass, cmp, depth_write: w0 >> 20 & 1 == 0, tag_write: w0 >> 21 & 1 == 0, removed })
}

/// What a pixel holds after the objects: the winning primitive and its depth. The depth is the
/// plane at the centre (exact, f64) with the units of tolerance E606 gives: `Some(3)` for a plane
/// of gradient below 0.03, `None` for a plane the model cannot compare (refused on need), 0 for
/// the background's exact value.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Pixel {
    /// (object, primitive) of the visible triangle, None for the background object
    pub tag: Option<(usize, usize)>,
    pub depth: f64,
    pub tol: Option<u32>,
}

/// One object of a tile: its mode, its triangles and the primitives listed for the left and the
/// right 16 pixels of the tile (bit k = primitive k).
pub struct Listed<'a> {
    pub mode: Mode,
    pub prims: &'a [Tri],
    pub left: u32,
    pub right: u32,
}

/// Resolve the 32 x 16 pixels of tile (tx, ty) in raster order: each object in turn, each listed
/// primitive in turn, painter fashion with the depth test (3d.md 11.4). A pixel whose depth test
/// cannot be decided from the plane's tolerance refuses (Q200): two depths closer than the sum of
/// their tolerances, or a compare against a plane of gradient 0.03 or more.
pub fn resolve_tile(tile: (u32, u32), bg_depth: f32, objs: &[Listed]) -> Result<Vec<Pixel>, Outcome> {
    resolve_tile_from(tile, &[bg_depth; 512], objs)
}

/// [`resolve_tile`] over a tile whose depth starts as `start` (the 512 pixels in raster order of
/// the tile): the clear value, or a depth the ZLS loaded (12.4, E467). Synthetic tests only: no
/// hardware run of a load with two objects exists, and the single-object images over a loaded
/// depth of E411 part B are counts and hashes (no dump), with the background object and the
/// stencil in them, so they do not check this function. A start depth enters the compare as its
/// magnitude, NaN and infinity above every depth (E995: -0.25, -0.75, -0.0 and NaN under the
/// compares 1 to 6, 14 of 14 held out; E977: NaN and infinity under less and greater); a pixel
/// that no object writes keeps the start value itself.
pub fn resolve_tile_from(
    tile: (u32, u32),
    start: &[f32; 512],
    objs: &[Listed],
) -> Result<Vec<Pixel>, Outcome> {
    // the compare's view of a depth: its magnitude, NaN above every depth (E995)
    let key = |d: f64| if d.is_nan() { f64::INFINITY } else { d.abs() };
    let mut px: Vec<Pixel> =
        start.iter().map(|&d| Pixel { tag: None, depth: d as f64, tol: Some(0) }).collect();
    for (o, obj) in objs.iter().enumerate() {
        if obj.mode.removed {
            continue;
        }
        for (k, tri) in obj.prims.iter().enumerate() {
            let low = tri.gradient() < DEPTH_GRADIENT_LIMIT;
            for j in 0..16 {
                for i in 0..32 {
                    let listed = if i < 16 { obj.left } else { obj.right } >> k & 1 != 0;
                    let (x, y) = (32 * tile.0 + i, 16 * tile.1 + j);
                    if !listed || !tri.covers(x, y) {
                        continue;
                    }
                    let p = &mut px[(j * 32 + i) as usize];
                    // E287 (one run, [infer]): the depth is clamped on its way, a negative one
                    // compares as 0 and one above 1 as itself; a z the hardware changes is not the
                    // plane's, so it refuses unless the compare and the write never use it
                    let uses_z = obj.mode.cmp != Cmp::Always || obj.mode.depth_write;
                    if uses_z && tri.z.iter().any(|z| !(0.0..=1.0).contains(z)) {
                        return Err(open(
                            format!(
                                "a vertex depth {:?} outside [0, 1] under a compare or a depth write: E287 saw it clamped in clip space (one run, inferred), the plane's value is not the stored one",
                                tri.z
                            ),
                            "Q241",
                        ));
                    }
                    let z = tri.depth_at(x, y);
                    let pass = match obj.mode.cmp {
                        Cmp::Never => false,
                        Cmp::Always => true,
                        c => {
                            let (Some(tn), Some(to)) = (low.then_some(DEPTH_TOLERANCE), p.tol) else {
                                return Err(open(
                                    "a depth compare against a plane of gradient 0.03 or more: the plane's error reaches 145 units (E606)",
                                    "Q200",
                                ));
                            };
                            let d = z - key(p.depth);
                            if d.abs() <= (tn + to) as f64 * DEPTH_UNIT {
                                return Err(open(
                                    format!(
                                        "pixel ({x}, {y}): the depths differ by {:.1} units of 2^-23, inside the planes' tolerance: the hardware's decision is not predictable",
                                        d / DEPTH_UNIT
                                    ),
                                    "Q200",
                                ));
                            }
                            // equal depths are inside the tolerance and refused above
                            match c {
                                Cmp::Less | Cmp::LessEqual => d < 0.0,
                                Cmp::Greater | Cmp::GreaterEqual => d > 0.0,
                                Cmp::Equal => false,
                                _ => true,
                            }
                        }
                    };
                    if pass {
                        if obj.mode.depth_write {
                            p.depth = z;
                            p.tol = low.then_some(DEPTH_TOLERANCE);
                        }
                        if obj.mode.tag_write {
                            p.tag = Some((o, k));
                        }
                    }
                }
            }
        }
    }
    Ok(px)
}

/// The source pixel (x, y) that the stored pixel (a, b) of tile (tx, ty), 32 x 16 pixels, holds
/// in a multisampled render of `mode` (CR_ISP_MSAA mode 0 to 2) with `te_aa` the CR_TE_AA word
/// (E503): x = 32 tx + 16 b31 + a div sx, y = 16 ty + 8 b30 + b div sy, (sx, sy) = (1, 1),
/// (2, 1), (2, 2) for the modes 0, 1, 2; b30 counts in mode 2 only. E281's sample slots hold in
/// the tiles past the first under every window run (E990). Mode 0 has no window: every stored
/// pixel is its own under CR_TE_AA 0x2, 0x6, 0xa and 0xe (E502, E1010: 12 of 12 identity maps
/// held out, the region model's seam holes background). Mode 3 hangs (E210); its window was not
/// measured and no question asks for it (the sample-layout question is answered by E1010): it
/// refuses naming none.
pub fn msaa_source(mode: u32, te_aa: u32, tx: u32, ty: u32, a: u32, b: u32) -> Result<(u32, u32), Outcome> {
    let (b31, b30) = (te_aa >> 31 & 1, te_aa >> 30 & 1);
    let (sx, sy) = match mode {
        0 => return Ok((32 * tx + a, 16 * ty + b)),
        1 => (2, 1),
        2 => (2, 2),
        m => {
            return Err(Outcome::unsupported(
                &format!("the window of mode {m} was not measured (mode 3 hangs, E210)"),
                &[],
            ));
        }
    };
    let b30 = if mode == 2 { b30 } else { 0 };
    Ok((32 * tx + 16 * b31 + a / sx, 16 * ty + 8 * b30 + b / sy))
}

/// What `check_windows` found in a pair of dumps of one multisampled render.
#[derive(Debug, Default, Clone, PartialEq)]
pub struct WindowCheck {
    /// pixels the dumps hold in both ramps
    pub stored: u64,
    /// decodable to a source pixel in both
    pub decodable: u64,
    /// tiles with a decodable pixel
    pub tiles: u64,
    /// of those, tiles whose every decodable pixel is the rule's
    pub equal: u64,
    /// tiles decodable in all 512 pixels
    pub full: u64,
    /// tiles that are both equal and fully decodable (the others that are equal hold background
    /// pixels, Q141)
    pub equal_full: u64,
    /// decodable pixels that differ from the rule
    pub wrong: u64,
}

/// Dump pixels: (x, y, dword).
pub type Rows = Vec<(u32, u32, u32)>;

/// The offsets of the decoding (E502 / E503's post hoc reading): the iterated position of a
/// pixel is (x + 0.375, y + 0.125) in every mode.
pub const OX: f64 = 0.375;
pub const OY: f64 = 0.125;

/// Parse a dump's text: lines `row N: v v v ...` of hex dwords into (x, y, dword); a token that
/// is not a hex number keeps its column and is left out.
pub fn parse_rows(text: &str) -> Vec<(u32, u32, u32)> {
    let mut out = vec![];
    for line in text.lines() {
        // "row N: v v ..." anywhere in the line (the dump's lines may carry a prefix)
        let Some(at) = line.find("row ") else { continue };
        let Some((n, vals)) = line[at + 4..].split_once(": ") else { continue };
        let Ok(y) = n.trim().parse::<u32>() else { continue };
        for (x, tok) in vals.split_whitespace().enumerate() {
            if let Ok(v) = u32::from_str_radix(tok, 16) {
                out.push((x as u32, y, v));
            }
        }
    }
    out
}

fn source_of(v: u32, off: f64) -> Option<u32> {
    let x = f32::from_bits(v) as f64 - off;
    (x.is_finite() && (x - x.round()).abs() < 1e-4 && x > -1.0 && x < 4096.0).then(|| x.round() as u32)
}

/// Check the window rule over the x-position and y-position dumps of one render.
pub fn check_windows(
    mode: u32,
    te_aa: u32,
    x: &[(u32, u32, u32)],
    y: &[(u32, u32, u32)],
) -> Result<WindowCheck, Outcome> {
    msaa_source(mode, te_aa, 0, 0, 0, 0)?; // refuse the modes and bits no record measured
    let ymap: std::collections::HashMap<(u32, u32), u32> = y.iter().map(|&(a, b, v)| ((a, b), v)).collect();
    let mut c = WindowCheck::default();
    // per tile: decodable pixels, wrong ones
    let mut tiles = std::collections::BTreeMap::<(u32, u32), (u64, u64)>::new();
    for &(px, py, vx) in x {
        let Some(&vy) = ymap.get(&(px, py)) else { continue };
        c.stored += 1;
        let (Some(sx), Some(sy)) = (source_of(vx, OX), source_of(vy, OY)) else { continue };
        c.decodable += 1;
        let t = tiles.entry((px / 32, py / 16)).or_default();
        t.0 += 1;
        if msaa_source(mode, te_aa, px / 32, py / 16, px % 32, py % 16)? != (sx, sy) {
            t.1 += 1;
            c.wrong += 1;
        }
    }
    for &(n, wrong) in tiles.values() {
        c.tiles += 1;
        c.equal += (wrong == 0) as u64;
        c.full += (n == 512) as u64;
        c.equal_full += (wrong == 0 && n == 512) as u64;
    }
    Ok(c)
}

#[cfg(test)]
mod tests {

    /// r9-x stage far (E979) and E684's far21d0: the vertices in 1/256 pixel, the determined pixels
    /// the frozen H-EXACT drew, its band pixels and the hardware's drawn count.
    const E979_ROWS: [(&str, [i64; 6], usize, usize, usize); 11] = [
        ("far-ctl", [4066, 8385, 7356, 9765, 536870912, 11776], 208, 1, 208),
        ("far-x22p", [2112, 1728, 1408, 14656, 1073741824, 7808], 2854, 0, 2854),
        ("far-x23p", [14656, 1728, 2147483648, 536870912, 14976, 14656], 310, 16, 312),
        ("far-x24p", [1600, 2368, 2432, 13760, 4294967296, 1073741824], 2422, 13, 2432),
        ("far-x25n", [14400, 1984, -8589934592, -2147483648, 14464, 14272], 2596, 16, 2610),
        ("far-y22n", [1728, 14912, 7616, -1073741824, 14656, 14016], 2825, 0, 2825),
        ("far-y23p", [1856, 1600, 14400, 1984, 536870912, 2147483648], 2686, 0, 2686),
        ("far-y24n", [1472, 14656, 1073741824, -4294967296, 14784, 14144], 2784, 0, 2784),
        ("far-y25n", [1344, 14784, -2147483648, -8589934592, 14912, 14400], 2878, 0, 2878),
        ("far-2a", [2147483648, 2688, -2147483648, 12992, 8256, 1856], 1536, 0, 1536),
        ("far-2b", [4294967296, 1073741824, 7872, 15424, -4294967296, -1073741824], 3320, 0, 3320),
    ];

    #[test]
    fn far_vertices_draw_the_exact_triangle_outside_e684s_band() {
        for (name, v, drawn, band, hw) in E979_ROWS {
            let t = FarTri { v: [(v[0], v[1]), (v[2], v[3]), (v[4], v[5])] };
            let img = far_coverage_image(64, 64, &t).unwrap();
            let det = img.iter().filter(|p| **p == Some(true)).count();
            let und = img.iter().filter(|p| p.is_none()).count();
            assert_eq!((det, und), (drawn, band), "{name}");
            // the hardware drew every determined pixel and some of the band (E979: H-EXACT held)
            assert!(det <= hw && hw <= det + und, "{name}");
        }
        // E984 (post hoc): 26 of the 46 band pixels were drawn, each on a far edge between its near
        // vertex and the far one, and the other 20 not; one-sided, but read on three rows only, so
        // the band stays undetermined
        let band: usize = E979_ROWS.iter().map(|r| r.3).sum();
        let drawn_in_band: usize = E979_ROWS.iter().map(|r| r.4 - r.2).sum();
        assert_eq!((band, drawn_in_band), (46, 26));
    }

    /// r10-geo stage pivot (E1005): E979's far-x23p, far-x24p and far-x25n with the far vertex's
    /// y moved by 0 to -544 pixels (1/256 pixel), the determined pixels drawn, the band and the
    /// hardware's drawn count.
    const E1005_ROWS: [(&str, [i64; 6], usize, usize, usize); 36] = [
        ("piv-x23p-d0", [14656, 1728, 2147483648, 536870912, 14976, 14656], 310, 16, 312),
        ("piv-x23p-m16", [14656, 1728, 2147483648, 536866816, 14976, 14656], 310, 16, 312),
        ("piv-x23p-m32", [14656, 1728, 2147483648, 536862720, 14976, 14656], 310, 16, 312),
        ("piv-x23p-m48", [14656, 1728, 2147483648, 536858624, 14976, 14656], 310, 16, 312),
        ("piv-x23p-m64", [14656, 1728, 2147483648, 536854528, 14976, 14656], 310, 16, 312),
        ("piv-x23p-m96", [14656, 1728, 2147483648, 536846336, 14976, 14656], 310, 16, 312),
        ("piv-x23p-m128", [14656, 1728, 2147483648, 536838144, 14976, 14656], 310, 14, 312),
        ("piv-x23p-m160", [14656, 1728, 2147483648, 536829952, 14976, 14656], 310, 12, 312),
        ("piv-x23p-m224", [14656, 1728, 2147483648, 536813568, 14976, 14656], 310, 10, 312),
        ("piv-x23p-m288", [14656, 1728, 2147483648, 536797184, 14976, 14656], 310, 8, 312),
        ("piv-x23p-m416", [14656, 1728, 2147483648, 536764416, 14976, 14656], 310, 6, 312),
        ("piv-x23p-m544", [14656, 1728, 2147483648, 536731648, 14976, 14656], 310, 5, 312),
        ("piv-x24p-d0", [1600, 2368, 2432, 13760, 4294967296, 1073741824], 2422, 13, 2432),
        ("piv-x24p-m16", [1600, 2368, 2432, 13760, 4294967296, 1073737728], 2422, 13, 2432),
        ("piv-x24p-m32", [1600, 2368, 2432, 13760, 4294967296, 1073733632], 2422, 13, 2432),
        ("piv-x24p-m48", [1600, 2368, 2432, 13760, 4294967296, 1073729536], 2422, 13, 2432),
        ("piv-x24p-m64", [1600, 2368, 2432, 13760, 4294967296, 1073725440], 2422, 13, 2432),
        ("piv-x24p-m96", [1600, 2368, 2432, 13760, 4294967296, 1073717248], 2422, 13, 2432),
        ("piv-x24p-m128", [1600, 2368, 2432, 13760, 4294967296, 1073709056], 2422, 13, 2432),
        ("piv-x24p-m160", [1600, 2368, 2432, 13760, 4294967296, 1073700864], 2422, 13, 2432),
        ("piv-x24p-m224", [1600, 2368, 2432, 13760, 4294967296, 1073684480], 2422, 13, 2432),
        ("piv-x24p-m288", [1600, 2368, 2432, 13760, 4294967296, 1073668096], 2422, 13, 2432),
        ("piv-x24p-m416", [1600, 2368, 2432, 13760, 4294967296, 1073635328], 2422, 12, 2422),
        ("piv-x24p-m544", [1600, 2368, 2432, 13760, 4294967296, 1073602560], 2422, 10, 2422),
        ("piv-x25n-d0", [14400, 1984, -8589934592, -2147483648, 14464, 14272], 2596, 16, 2610),
        ("piv-x25n-m16", [14400, 1984, -8589934592, -2147487744, 14464, 14272], 2596, 16, 2610),
        ("piv-x25n-m32", [14400, 1984, -8589934592, -2147491840, 14464, 14272], 2596, 16, 2610),
        ("piv-x25n-m48", [14400, 1984, -8589934592, -2147495936, 14464, 14272], 2596, 16, 2610),
        ("piv-x25n-m64", [14400, 1984, -8589934592, -2147500032, 14464, 14272], 2596, 16, 2610),
        ("piv-x25n-m96", [14400, 1984, -8589934592, -2147508224, 14464, 14272], 2596, 16, 2610),
        ("piv-x25n-m128", [14400, 1984, -8589934592, -2147516416, 14464, 14272], 2596, 16, 2610),
        ("piv-x25n-m160", [14400, 1984, -8589934592, -2147524608, 14464, 14272], 2596, 16, 2610),
        ("piv-x25n-m224", [14400, 1984, -8589934592, -2147540992, 14464, 14272], 2596, 16, 2610),
        ("piv-x25n-m288", [14400, 1984, -8589934592, -2147557376, 14464, 14272], 2596, 16, 2610),
        ("piv-x25n-m416", [14400, 1984, -8589934592, -2147590144, 14464, 14272], 2596, 16, 2610),
        ("piv-x25n-m544", [14400, 1984, -8589934592, -2147622912, 14464, 14272], 2596, 16, 2610),
    ];

    #[test]
    fn far_vertices_keep_the_exact_triangle_outside_the_band_and_the_band_stays_open() {
        for (name, v, drawn, band, hw) in E1005_ROWS {
            let t = FarTri { v: [(v[0], v[1]), (v[2], v[3]), (v[4], v[5])] };
            let img = far_coverage_image(64, 64, &t).unwrap();
            let det = img.iter().filter(|p| **p == Some(true)).count();
            let und = img.iter().filter(|p| p.is_none()).count();
            assert_eq!((det, und), (drawn, band), "{name}");
            // E1005: H-EXACT-BAND 36 of 36 (every determined pixel as drawn)
            assert!(det <= hw && hw <= det + und, "{name}");
        }
        // the band is no fixed rule: far-x24p draws its band pixels down to d = -288 and not from
        // -416 (D in (339, 467) px), while far-x23p and far-x25n draw theirs at every d to -544
        // (D above 586): neither "the band drawn" nor "the band empty" holds, nor one D (Q261)
        let hw = |n: &str| E1005_ROWS.iter().find(|r| r.0 == n).unwrap().4;
        assert_eq!((hw("piv-x24p-m288"), hw("piv-x24p-m416")), (2432, 2422));
        assert_eq!((hw("piv-x23p-m544"), hw("piv-x25n-m544")), (312, 2610));
    }

    #[test]
    fn far_coverage_refuses_what_did_not_run() {
        let far = |x: i64| FarTri { v: [(1024, 1024), (1024, 14000), (x, 8000)] };
        // past 2^24 pixels to the right and 2^25 to the left: not reachable with the tool (Q199)
        for x in [(1i64 << 32) + 256, -(1i64 << 33) - 256] {
            assert!(
                matches!(far_coverage_image(64, 64, &far(x)), Err(Outcome::Unsupported { ref ids, .. }) if ids == &["Q199"]),
                "{x}"
            );
        }
        // targets other than E684's and E979's
        assert!(
            matches!(far_coverage_image(4096, 4096, &far(1 << 32)), Err(Outcome::Unsupported { ref ids, .. }) if ids == &["Q261"])
        );
        // three far vertices did not run
        let t = FarTri { v: [(1 << 32, 0), (-(1 << 32), 0), (0, 1 << 32)] };
        assert!(
            matches!(far_coverage_image(64, 64, &t), Err(Outcome::Unsupported { ref ids, .. }) if ids == &["Q261"])
        );
    }

    use super::*;

    fn tri(v: [(i64, i64); 3]) -> Tri {
        Tri { v, z: [0.5; 3] }
    }

    /// (0,0), (10,0), (0,10) pixels: the E606 reference triangle, a top and a left edge
    fn corner() -> Tri {
        tri([(0, 0), (2560, 0), (0, 2560)])
    }

    #[test]
    fn a_vertex_snaps_half_up_to_the_nearest_256th() {
        assert_eq!(snap(1.0).unwrap(), 256);
        assert_eq!(snap(0.5 / 256.0).unwrap(), 1, "a tie rounds up");
        assert_eq!(snap(0.49 / 256.0).unwrap(), 0);
        assert_eq!(snap(63.9990234375).unwrap(), 16384, "16383.75 rounds up");
        assert_eq!(snap(3.5 / 256.0 + 7.0).unwrap(), 7 * 256 + 4);
    }

    #[test]
    fn a_negative_vertex_with_a_sub_grid_fraction_refuses_and_names_q199_and_q260() {
        // the tie rounds away from zero (E914, E943), but the pixels within 6.4e-4 pixel of a
        // long edge go either way (E943: 738 of 738 off pixels there): no image is exact
        for c in [-0.3 / 256.0, -3.3, -0.5 / 256.0] {
            match snap(c) {
                Err(Outcome::Unsupported { ids, .. }) => assert_eq!(ids, ["Q199", "Q260"], "{c}"),
                o => panic!("{c}: {o:?}"),
            }
        }
        // on the grid, negative is fine (9 of E606's cases)
        assert_eq!(snap(-2.0).unwrap(), -512);
        assert_eq!(snap(-1.0 / 256.0).unwrap(), -1);
        assert!(matches!(snap(f64::NAN), Err(Outcome::Unsupported { .. })));
    }

    #[test]
    fn the_centre_sample_decides_and_the_top_and_left_edges_own_the_tie() {
        let t = corner();
        // pixel (0, 0): centre (0.5, 0.5) inside; (9, 0): centre (9.5, 0.5), 0.5 + 9.5 = 10: on the hypotenuse
        assert!(t.covers(0, 0));
        assert!(!t.covers(9, 0), "the hypotenuse is a right/bottom edge: not owned");
        assert!(t.covers(8, 0) && t.covers(0, 8) && !t.covers(0, 9));
        assert!(!t.covers(10, 10));
    }

    #[test]
    fn a_centre_exactly_on_a_top_or_left_edge_is_drawn_and_on_a_bottom_or_right_edge_is_not() {
        // vertices at the pixel centres (0.5, 0.5), (3.5, 0.5), (0.5, 3.5): the top edge runs through
        // the centres of row 0, the left edge through those of column 0, the hypotenuse x + y = 4
        let t = tri([(128, 128), (3 * 256 + 128, 128), (128, 3 * 256 + 128)]);
        assert!(t.covers(0, 0), "the corner is on the top and the left edge, both own it");
        assert!(t.covers(1, 0) && t.covers(2, 0), "centres on the top edge");
        assert!(t.covers(0, 1) && t.covers(0, 2), "centres on the left edge");
        assert!(!t.covers(3, 0) && !t.covers(0, 3), "the corners on the hypotenuse: not owned");
        assert!(!t.covers(1, 2) && !t.covers(2, 1), "centres on the hypotenuse");
        assert!(t.covers(1, 1));
    }

    #[test]
    fn the_winding_does_not_matter() {
        let a = corner();
        let b = tri([a.v[0], a.v[2], a.v[1]]);
        assert_eq!(a.area2(), -b.area2());
        for y in 0..12 {
            for x in 0..12 {
                assert_eq!(a.covers(x, y), b.covers(x, y), "({x}, {y})");
            }
        }
    }

    #[test]
    fn a_zero_area_triangle_draws_nothing() {
        let t = tri([(0, 0), (2560, 2560), (1280, 1280)]);
        assert_eq!(t.area2(), 0);
        for y in 0..12 {
            for x in 0..12 {
                assert!(!t.covers(x, y));
            }
        }
        assert!(!tri([(128, 128), (128, 128), (128, 128)]).covers(0, 0));
    }

    #[test]
    fn a_centre_one_unit_inside_an_edge_is_drawn_and_one_unit_outside_is_not() {
        // E607: a centre 1 unit (1/65536 pixel squared of cross product) inside an edge is drawn.
        // The edge from (0, 0) down to (256, 256 * 3): the centre (128, 128) is 128 * 3 - 128 away
        let t = tri([(0, 0), (0, 1024), (1000, 0)]);
        assert!(t.covers(0, 0));
        // move the vertical left edge to x = 128 (through the centre of column 0): owned
        let on = tri([(128, 0), (128, 1024), (1000, 0)]);
        assert!(on.covers(0, 0), "a left edge owns the tie");
        let on_right = tri([(128, 0), (1000, 0), (128, 1024)]);
        assert!(on_right.covers(0, 0), "the same triangle in the other winding");
        let off = tri([(129, 0), (129, 1024), (1000, 0)]);
        assert!(!off.covers(0, 0), "1/256 pixel past the centre: out");
    }

    #[test]
    fn the_depth_plane_through_the_vertices_at_the_centre() {
        let t = Tri { v: [(0, 0), (2560, 0), (0, 2560)], z: [0.0, 1.0, 0.5] };
        // z = x / 10 + y / 20 along the plane; at the centre (0.5, 0.5): 0.05 + 0.025
        assert!((t.depth_at(0, 0) - 0.075).abs() < 1e-12);
        assert!((t.depth_at(4, 2) - (4.5 / 10.0 + 2.5 / 20.0)).abs() < 1e-12);
        assert!((t.gradient() - (0.1 + 0.05)).abs() < 1e-12);
        let flat = Tri { z: [0.5; 3], ..t };
        assert_eq!((flat.depth_at(3, 3), flat.gradient()), (0.5, 0.0));
    }

    #[test]
    fn only_the_three_targets_e606_ran_are_inside_for_depth_and_every_other_refuses() {
        for (w, h) in E606_TARGETS {
            assert!(target_in_envelope(w, h).is_ok(), "{w} x {h}");
        }
        assert_eq!(E606_TARGETS, [(64, 64), (128, 128), (256, 128)]);
        // E680's ten and E913's ten: coverage only; the depth there missed E606's tolerance on
        // 1- and 2-pixel triangles (E912, E913): Q262 on E680's, Q240 on E913's
        for (w, h) in E680_TARGETS {
            match target_in_envelope(w, h) {
                Err(Outcome::Unsupported { ids, .. }) => assert_eq!(ids, ["Q262"], "{w} x {h}"),
                o => panic!("{w} x {h}: {o:?}"),
            }
        }
        for (w, h) in E913_TARGETS {
            match target_in_envelope(w, h) {
                Err(Outcome::Unsupported { ids, .. }) => assert_eq!(ids, ["Q240"], "{w} x {h}"),
                o => panic!("{w} x {h}: {o:?}"),
            }
        }
        for (w, h) in NOT_RUN {
            match target_in_envelope(w, h) {
                Err(Outcome::Unsupported { ids, .. }) => assert_eq!(ids, ["Q240"], "{w} x {h}"),
                o => panic!("{w} x {h}: {o:?}"),
            }
        }
    }

    /// Targets neither E606, E680 nor E913 ran.
    const NOT_RUN: [(u32, u32); 21] = [
        // the family around E606's that no run covered
        (2, 2),
        (32, 32),
        (64, 32),
        (16, 16),
        (8, 8),
        // between and past the sizes run
        (512, 64),
        (512, 128),
        (512, 16),
        (256, 256),
        (128, 256),
        (64, 256),
        (64, 144),
        (4096, 2048),
        (8192, 16),
        (2048, 16),
        // odd and degenerate sizes
        (0, 16),
        (0, 0),
        (100, 64),
        (65, 64),
        (64, 65),
        (95, 47),
    ];

    #[test]
    fn coverage_admits_e606s_three_e680s_ten_and_e913s_ten_targets_and_refuses_the_rest_naming_q240() {
        // E913 (R7-geo zf, held out): 24 random triangles on each, 240 of 240 images exact
        assert_eq!(
            E913_TARGETS,
            [
                (64, 128),
                (128, 64),
                (256, 64),
                (128, 96),
                (128, 144),
                (32, 16),
                (16, 8),
                (4096, 16),
                (64, 33),
                (96, 47)
            ]
        );
        assert_eq!(
            E680_TARGETS,
            [
                (96, 64),
                (130, 66),
                (200, 120),
                (512, 256),
                (512, 512),
                (640, 480),
                (1000, 600),
                (1024, 768),
                (2048, 1024),
                (4096, 4096)
            ]
        );
        for (w, h) in E606_TARGETS.into_iter().chain(E680_TARGETS).chain(E913_TARGETS) {
            assert!(coverage_target_in_envelope(w, h).is_ok(), "{w} x {h}");
        }
        for (w, h) in NOT_RUN {
            match coverage_target_in_envelope(w, h) {
                Err(Outcome::Unsupported { ids, .. }) => assert_eq!(ids, ["Q240"], "{w} x {h}"),
                o => panic!("{w} x {h}: {o:?}"),
            }
        }
    }

    #[test]
    fn the_coverage_image_is_the_rule_and_refuses_outside_its_envelope() {
        let t = tri([(0, 0), (96 * 256, 0), (0, 64 * 256)]);
        let img = coverage_image(96, 64, &t).unwrap();
        assert_eq!(img.len(), 96 * 64);
        for (i, &c) in img.iter().enumerate() {
            assert_eq!(c, t.covers(i as u32 % 96, i as u32 / 96), "pixel {i}");
        }
        match coverage_image(100, 64, &t) {
            Err(Outcome::Unsupported { ids, .. }) => assert_eq!(ids, ["Q240"]),
            o => panic!("{o:?}"),
        }
        // E606's vertex range applies; at 4096 x 4096 E680 drew no negative x (Q199)
        let far = tri([(0, 0), (130 * 256, 0), (0, 64 * 256)]);
        match coverage_image(96, 64, &far) {
            Err(Outcome::Unsupported { ids, .. }) => assert_eq!(ids, ["Q199"]),
            o => panic!("{o:?}"),
        }
        let neg = tri([(-256, 0), (4096 * 256, 0), (0, 4096 * 256)]);
        assert!(vertices_in_envelope(4096, 4096, &neg).is_ok());
        match coverage_vertices_in_envelope(4096, 4096, &neg) {
            Err(Outcome::Unsupported { ids, .. }) => assert_eq!(ids, ["Q199"]),
            o => panic!("{o:?}"),
        }
        let neg_y = tri([(256, -256), (4096 * 256, 0), (0, 4096 * 256)]);
        assert!(coverage_vertices_in_envelope(4096, 4096, &neg_y).is_ok());
    }

    #[test]
    fn vertices_beyond_minus_9_and_plus_124_percent_refuse_naming_q199() {
        let at = |x: i64, y: i64| tri([(x, y), (2560, 0), (0, 2560)]);
        // a 64 x 64 target: -5.7 pixels is -8.9%, 79.4 pixels is 124.1%
        assert!(vertices_in_envelope(64, 64, &at(-5 * 256 - 190, 0)).is_ok());
        assert!(vertices_in_envelope(64, 64, &at(79 * 256 + 100, 0)).is_ok());
        for bad in [at(-6 * 256, 0), at(0, -6 * 256), at(80 * 256, 0), at(0, 80 * 256)] {
            match vertices_in_envelope(64, 64, &bad) {
                Err(Outcome::Unsupported { ids, .. }) => assert_eq!(ids, ["Q199"]),
                o => panic!("{o:?}"),
            }
        }
    }

    #[test]
    fn mode_1_doubles_in_x_and_the_window_is_the_left_16_columns_unless_b31() {
        assert_eq!(msaa_source(1, 0, 0, 0, 0, 0).unwrap(), (0, 0));
        assert_eq!(msaa_source(1, 0, 0, 0, 5, 3).unwrap(), (2, 3)); // 5 div 2, y not halved
        assert_eq!(msaa_source(1, 0x2000_0000, 1, 2, 31, 15).unwrap(), (32 + 15, 32 + 15));
        assert_eq!(msaa_source(1, 0xa000_0000, 0, 0, 0, 0).unwrap(), (16, 0)); // b31
    }

    #[test]
    fn mode_2_doubles_in_both_and_b30_shifts_the_window_8_rows() {
        assert_eq!(msaa_source(2, 0x2000_0000, 0, 0, 31, 15).unwrap(), (15, 7));
        assert_eq!(msaa_source(2, 0x6000_0000, 0, 0, 0, 0).unwrap(), (0, 8)); // b30
        assert_eq!(msaa_source(2, 0xe000_0000, 1, 1, 0, 0).unwrap(), (32 + 16, 16 + 8));
    }

    #[test]
    fn b30_does_not_act_in_mode_1() {
        assert_eq!(msaa_source(1, 0x6000_0000, 0, 0, 0, 0).unwrap(), (0, 0));
    }

    #[test]
    fn mode_0_has_no_window_and_mode_3_refuses_with_no_question() {
        // E1010: mode 0 stores each pixel's own position under CR_TE_AA 0x6, 0xa and 0xe
        for te in [0x2000_0000, 0x6000_0000, 0xa000_0000, 0xe000_0000u32] {
            assert_eq!(msaa_source(0, te, 2, 3, 17, 9).unwrap(), (81, 57), "{te:#x}");
        }
        // mode 3 hangs (E210) and no question asks for its window (the layout one is answered, E1010)
        match msaa_source(3, 0x2000_0000, 0, 0, 0, 0) {
            Err(Outcome::Unsupported { ids, .. }) => assert!(ids.is_empty()),
            o => panic!("{o:?}"),
        }
    }

    #[test]
    fn modes_and_bits_no_record_measured_refuse() {
        // mode 0 is the identity under every window (E502, E1010); mode 3 and above never ran
        assert_eq!(msaa_source(0, 0x2000_0000, 1, 1, 7, 9).unwrap(), (39, 25));
        assert_eq!(msaa_source(0, 0x6000_0000, 1, 1, 7, 9).unwrap(), (39, 25));
        assert!(matches!(msaa_source(3, 0x2000_0000, 0, 0, 0, 0), Err(Outcome::Unsupported { .. })));
        assert!(matches!(msaa_source(4, 0x2000_0000, 0, 0, 0, 0), Err(Outcome::Unsupported { .. })));
    }

    #[test]
    fn rows_parse_with_columns_kept_over_a_bad_token() {
        let t = "junk\nrow 0: 3f800000 zz 40000000\n[ 12.5] row 1: 1\n";
        assert_eq!(parse_rows(t), vec![(0, 0, 0x3f800000), (2, 0, 0x40000000), (0, 1, 1)]);
    }

    fn pos(v: u32, off: f64) -> u32 {
        ((v as f64 + off) as f32).to_bits()
    }

    /// dumps of a W x H mode-`mode` render stored the way the rule says
    fn render(w: u32, h: u32, mode: u32, te: u32) -> (Rows, Rows) {
        let (mut x, mut y) = (vec![], vec![]);
        for py in 0..h {
            for px in 0..w {
                let (sx, sy) = msaa_source(mode, te, px / 32, py / 16, px % 32, py % 16).unwrap();
                x.push((px, py, pos(sx, OX)));
                y.push((px, py, pos(sy, OY)));
            }
        }
        (x, y)
    }

    #[test]
    fn a_render_stored_as_the_rule_says_has_every_tile_equal() {
        let (x, y) = render(64, 32, 2, 0xe000_0000);
        let c = check_windows(2, 0xe000_0000, &x, &y).unwrap();
        assert_eq!((c.stored, c.decodable, c.tiles, c.equal, c.full, c.wrong), (2048, 2048, 4, 4, 4, 0));
        assert_eq!(c.equal_full, 4);
    }

    #[test]
    fn a_wrong_pixel_makes_its_tile_unequal() {
        let (mut x, y) = render(64, 32, 1, 0x2000_0000);
        x[5].2 = pos(60, OX);
        let c = check_windows(1, 0x2000_0000, &x, &y).unwrap();
        assert_eq!((c.tiles, c.equal, c.wrong), (4, 3, 1));
    }

    #[test]
    fn undecodable_pixels_are_not_counted_as_wrong() {
        let (mut x, y) = render(32, 16, 1, 0x2000_0000);
        x[0].2 = 0x3f800000 + 1; // 1.0000001: not a position + 0.375
        let c = check_windows(1, 0x2000_0000, &x, &y).unwrap();
        assert_eq!((c.decodable, c.wrong, c.equal, c.full, c.equal_full), (511, 0, 1, 0, 0));
    }

    fn ids(o: Result<Mode, Outcome>) -> Vec<String> {
        match o {
            Err(Outcome::Unsupported { ids, .. }) => ids,
            o => panic!("{o:?}"),
        }
    }

    #[test]
    fn the_librarys_and_the_depth_probes_words_decode() {
        let m = decode_words([0x01d0_0200, 0x10f0], 0, 1).unwrap();
        assert_eq!(
            (m.pass, m.cmp, m.depth_write, m.tag_write, m.removed),
            (0, Cmp::Always, false, true, false)
        );
        let m = decode_words([0x0040_0200, 0x10f0], 0, 5).unwrap();
        assert_eq!((m.cmp, m.depth_write, m.tag_write), (Cmp::Less, true, true));
        // bit 21 stops colour while depth is still written (E282); bits 29 to 31 change nothing
        let m = decode_words([0x0060_0200 | 0xe000_0000, 0x10f0], 0, 1).unwrap();
        assert!(m.depth_write && !m.tag_write);
        assert_eq!(decode_words([0x0100_0000, 0x10f0], 0, 1).unwrap().cmp, Cmp::Greater);
        assert_eq!(decode_words([0x0000_0000, 0x10f0], 0, 1).unwrap().cmp, Cmp::Never);
    }

    #[test]
    fn the_compares_2_3_5_6_decode_in_the_gl_order_e995_held() {
        // E995: equal, less or equal, not equal, greater or equal, exact at equal depths
        for (m, c) in [(2u32, Cmp::Equal), (3, Cmp::LessEqual), (5, Cmp::NotEqual), (6, Cmp::GreaterEqual)] {
            assert_eq!(decode_words([m << 22 | 0x200, 0x10f0], 0, 1).unwrap().cmp, c, "compare {m}");
        }
    }

    #[test]
    fn the_eight_compares_on_e995s_rows_give_its_drawn_counts() {
        // r10-x dcmp (E995): t the triangle, l the loaded depth, the compare as 0 or all pixels;
        // the ulp rows are inside the planes' tolerance, so only the order is checked here
        let rows: [(u32, f32, f32, bool); 10] = [
            (1, 0.5, 0.75, true),
            (2, 0.5, 0.75, false),
            (3, 0.5, 0.75, true),
            (4, 0.5, 0.75, false),
            (5, 0.5, 0.75, true),
            (6, 0.5, 0.75, false),
            (3, 0.5, 0.25, false),
            (6, 0.5, 0.25, true),
            (4, 0.5, -0.25, true), // neg25-m4: the magnitude 0.25
            (1, 0.5, -0.75, true), // neg75-m1: the magnitude 0.75
        ];
        for (m, t, l, drawn) in rows {
            let tri = [flat(0, t)];
            let c = decode_words([m << 22 | 0x200, 0x10f0], 0, 1).unwrap().cmp;
            let o = [Listed { mode: mode(c, true), prims: &tri, left: 1, right: 1 }];
            let px = resolve_tile_from((0, 0), &[l; 512], &o).unwrap();
            assert_eq!(px[0].tag.is_some(), drawn, "mode {m}, {t} against {l}");
        }
    }

    #[test]
    fn pass_types_3_and_7_remove_the_object_and_the_others_draw_a_single_triangle() {
        for (pass, removed) in
            [(0, false), (1, false), (2, false), (3, true), (4, false), (5, false), (6, false), (7, true)]
        {
            let m = decode_words([0x01d0_0200 | pass << 25, 0x10f0], 0, 1).unwrap();
            assert_eq!(m.removed, removed, "pass {pass}");
        }
    }

    #[test]
    fn the_isp1_gate_decodes_for_the_pairs_e232_and_e235_measured_and_no_others() {
        // E232: the library's ISP1 (gate 0) under thresholds 0 to 8, 16, 32 and 63: pass types 0 and
        // 1 are removed above 0, 2, 4, 5 and 6 drawn; E235: gate 0 and 63 at the thresholds 1 and 63
        let w0 = |pass: u32| 0x01d0_0200 | pass << 25;
        let gate = |g: u32| 0x10f0 | g << 26;
        for thr in [0, 1, 2, 3, 4, 5, 6, 7, 8, 16, 32, 63] {
            for pass in [0, 1] {
                let m = decode_words([w0(pass), gate(0)], thr, 1).unwrap();
                assert_eq!(m.removed, thr > 0, "pass {pass}, threshold {thr}");
            }
            for pass in [2, 4, 5, 6] {
                assert!(!decode_words([w0(pass), gate(0)], thr, 1).unwrap().removed, "{pass} {thr}");
            }
        }
        for thr in [1, 63] {
            assert!(!decode_words([w0(0), gate(63)], thr, 1).unwrap().removed, "gate 63, threshold {thr}");
            for pass in [2, 4, 5, 6] {
                assert!(!decode_words([w0(pass), gate(63)], thr, 1).unwrap().removed);
            }
        }
        // everything else is inference and refuses naming Q241: the equality away from 63, values
        // between, the thresholds E232 did not run, pass type 1 at a non-zero gate, 3 and 7 off the
        // library's words
        for (pass, g, thr) in [
            (0, 3, 5),
            (0, 3, 3),
            (0, 2, 3),
            (0, 63, 0),
            (0, 63, 62),
            (0, 62, 63),
            (0, 0, 9),
            (0, 0, 33),
            (1, 63, 1),
            (1, 1, 1),
            (2, 5, 5),
            (4, 63, 2),
            (3, 0, 1),
            (7, 63, 63),
        ] {
            assert_eq!(ids(decode_words([w0(pass), gate(g)], thr, 1)), ["Q241"], "{pass} {g} {thr}");
        }
    }

    #[test]
    fn words_no_record_settles_refuse_naming_their_question() {
        assert_eq!(ids(decode_words([0x01d0_0300, 0x10f0], 0, 1)), ["Q071"], "stencil word present");
        assert_eq!(ids(decode_words([0x01d0_0a00, 0x10f0], 0, 1)), ["Q071"], "two-sided");
        assert_eq!(ids(decode_words([0x01d0_0201, 0x10f0], 0, 1)), ["Q071"], "a stencil reference");
        // bits 15 to 17 each removed E977's ramp triangle under less with writes (E998), not a
        // rule over vertex orders; bit 18 faults (E065)
        for bit in [15, 16, 17, 18] {
            assert_eq!(ids(decode_words([0x01d0_0200 | 1 << bit, 0x10f0], 0, 1)), ["Q241"], "bit {bit}");
        }
        assert_eq!(ids(decode_words([0x01d0_0200 | 1 << 28, 0x10f0], 0, 1)), ["Q202"]);
        // ISP word 1 bits 3 and 23 changed nothing on one ramp (E998): not a rule for the counter
        // or the offset's units
        for w1 in [0x10f0 | 8, 0x10f0 | 1 << 23, 0x1000] {
            assert_eq!(ids(decode_words([0x01d0_0200, w1], 0, 1)), ["Q241"], "{w1:#x}");
        }
        assert_eq!(ids(decode_words([1 << 25 | 0x200, 0x10f0], 0, 2)), ["Q073"]);
        assert_eq!(ids(decode_words([4 << 25 | 0x200, 0x10f0], 0, 2)), ["Q032"]);
        assert_eq!(ids(decode_words([2 << 25 | 0x200, 0x10f0], 0, 2)), ["Q241"]);
    }

    fn flat(x0: i64, z: f32) -> Tri {
        // a triangle covering tile (0, 0)'s top-left 8 x 8 pixels at x0 pixels on
        Tri { v: [(x0 * 256, 0), (x0 * 256 + 20 * 256, 0), (x0 * 256, 20 * 256)], z: [z; 3] }
    }

    fn mode(cmp: Cmp, depth_write: bool) -> Mode {
        Mode { pass: 0, cmp, depth_write, tag_write: true, removed: false }
    }

    #[test]
    fn the_nearer_of_two_flat_triangles_wins_under_less_in_either_order() {
        for order in [[0.25f32, 0.5], [0.5, 0.25]] {
            let tris: Vec<Tri> = order.iter().map(|&z| flat(0, z)).collect();
            let o = [Listed { mode: mode(Cmp::Less, true), prims: &tris, left: 3, right: 3 }];
            let px = resolve_tile((0, 0), 1.0, &o).unwrap();
            let want = if order[0] < order[1] { 0 } else { 1 };
            assert_eq!(px[0].tag, Some((0, want)), "{order:?}");
            assert_eq!(px[0].depth, 0.25);
            assert_eq!(px[31 + 15 * 32].tag, None, "outside the triangle");
        }
    }

    #[test]
    fn a_triangle_farther_than_the_background_loses_under_less_and_wins_under_greater() {
        let t = [flat(0, 0.5)];
        let less = resolve_tile(
            (0, 0),
            0.25,
            &[Listed { mode: mode(Cmp::Less, true), prims: &t, left: 1, right: 1 }],
        )
        .unwrap();
        assert_eq!(less[0].tag, None);
        let gt = resolve_tile(
            (0, 0),
            0.25,
            &[Listed { mode: mode(Cmp::Greater, true), prims: &t, left: 1, right: 1 }],
        )
        .unwrap();
        assert_eq!(gt[0].tag, Some((0, 0)));
        let never = resolve_tile(
            (0, 0),
            1.0,
            &[Listed { mode: mode(Cmp::Never, true), prims: &t, left: 1, right: 1 }],
        )
        .unwrap();
        assert_eq!(never[0].tag, None);
    }

    #[test]
    fn only_the_listed_halves_draw() {
        let t = [flat(0, 0.5)];
        let o = [Listed { mode: mode(Cmp::Always, false), prims: &t, left: 1, right: 0 }];
        let px = resolve_tile((0, 0), 1.0, &o).unwrap();
        assert!(px[5].tag.is_some() && px[15].tag.is_some());
        assert_eq!(px[16].tag, None, "x = 16 is in the right half, which does not list the primitive");
    }

    #[test]
    fn depths_inside_the_tolerance_refuse_and_name_q200() {
        // a depth 2 units of 2^-23 under the stored one: 3 + 0 > 2
        let t = [flat(0, (0.5 - 2.0 * DEPTH_UNIT) as f32)];
        let o = [Listed { mode: mode(Cmp::Less, true), prims: &t, left: 1, right: 1 }];
        match resolve_tile((0, 0), 0.5, &o) {
            Err(Outcome::Unsupported { ids, why }) => {
                assert_eq!(ids, ["Q200"]);
                assert!(why.contains("tolerance"), "{why}");
            }
            r => panic!("{r:?}"),
        }
        // 4 units apart: decided
        let t = [flat(0, (0.5 - 4.0 * DEPTH_UNIT) as f32)];
        let o = [Listed { mode: mode(Cmp::Less, true), prims: &t, left: 1, right: 1 }];
        assert!(resolve_tile((0, 0), 0.5, &o).is_ok());
    }

    #[test]
    fn a_compare_against_a_steep_plane_refuses_but_always_does_not_need_the_depth() {
        let steep = Tri { v: [(0, 0), (20 * 256, 0), (0, 20 * 256)], z: [0.0, 1.0, 1.0] };
        assert!(steep.gradient() >= DEPTH_GRADIENT_LIMIT);
        let t = [steep];
        let less = [Listed { mode: mode(Cmp::Less, true), prims: &t, left: 1, right: 1 }];
        assert!(matches!(resolve_tile((0, 0), 1.0, &less), Err(Outcome::Unsupported { .. })));
        let always = [Listed { mode: mode(Cmp::Always, false), prims: &t, left: 1, right: 1 }];
        assert!(resolve_tile((0, 0), 1.0, &always).is_ok());
        // but an always that writes depth leaves a plane the next compare cannot trust
        let write = [
            Listed { mode: mode(Cmp::Always, true), prims: &t, left: 1, right: 1 },
            Listed { mode: mode(Cmp::Less, true), prims: &[flat(0, 0.5)], left: 1, right: 1 },
        ];
        assert!(matches!(resolve_tile((0, 0), 1.0, &write), Err(Outcome::Unsupported { .. })));
    }

    #[test]
    fn an_object_that_only_writes_depth_leaves_the_tag_alone() {
        let t = [flat(0, 0.5)];
        let o = [Listed {
            mode: Mode { tag_write: false, ..mode(Cmp::Less, true) },
            prims: &t,
            left: 1,
            right: 1,
        }];
        let px = resolve_tile((0, 0), 1.0, &o).unwrap();
        assert_eq!((px[0].tag, px[0].depth), (None, 0.5));
    }

    #[test]
    fn a_removed_object_draws_nothing() {
        let t = [flat(0, 0.5)];
        let o = [Listed {
            mode: Mode { removed: true, ..mode(Cmp::Always, true) },
            prims: &t,
            left: 1,
            right: 1,
        }];
        assert!(resolve_tile((0, 0), 1.0, &o).unwrap().iter().all(|p| p.tag.is_none()));
    }

    #[test]
    fn the_depth_tolerance_is_the_three_units_e606_states_and_the_iteration_one_is_four() {
        assert_eq!((DEPTH_TOLERANCE, crate::iter::TOLERANCE), (3, 4), "E606's stated bounds");
        assert_eq!(DEPTH_GRADIENT_LIMIT, 0.03);
    }

    /// Two flat planes, both with a tolerance (3 units each), the first stored by an always that
    /// writes depth, the second compared under less: the depths `units` apart in 2^-23.
    fn two_planes(units: f64) -> Result<Vec<Pixel>, Outcome> {
        let (a, b) = (flat(0, 0.5), flat(0, (0.5 - units * DEPTH_UNIT) as f32));
        resolve_tile(
            (0, 0),
            1.0,
            &[
                Listed { mode: mode(Cmp::Always, true), prims: &[a], left: 1, right: 1 },
                Listed { mode: mode(Cmp::Less, true), prims: &[b], left: 1, right: 1 },
            ],
        )
    }

    #[test]
    fn two_planes_with_a_tolerance_each_refuse_up_to_the_sum_of_theirs_and_decide_beyond() {
        // 3 + 3 = 6 units: 5 and exactly 6 refuse (the bound is inclusive), 7 decides
        for units in [0.0, 5.0, 6.0] {
            match two_planes(units) {
                Err(Outcome::Unsupported { ids, .. }) => assert_eq!(ids, ["Q200"], "{units}"),
                r => panic!("{units}: {r:?}"),
            }
        }
        let px = two_planes(7.0).unwrap();
        assert_eq!(px[0].tag, Some((1, 0)), "7 units nearer: the second wins under less");
        assert_eq!((px[0].tol, px[0].depth < 0.5), (Some(DEPTH_TOLERANCE), true));
    }

    #[test]
    fn a_vertex_depth_outside_zero_to_one_refuses_unless_the_compare_never_uses_it() {
        // E287: negative compares as 0 and above 1 as itself (one run): the plane's value is not the
        // stored one. A background at 0.0 and a flat triangle at -0.5 under less is the probe case.
        for z in [-0.5f32, 1.5, -1e-9, 1.0000001, f32::NAN, f32::INFINITY] {
            let t = [flat(0, z)];
            for (cmp, write) in
                [(Cmp::Less, true), (Cmp::Less, false), (Cmp::Greater, true), (Cmp::Always, true)]
            {
                let o = [Listed { mode: mode(cmp, write), prims: &t, left: 1, right: 1 }];
                match resolve_tile((0, 0), 0.0, &o) {
                    Err(Outcome::Unsupported { ids, .. }) => assert_eq!(ids, ["Q241"], "{z} {cmp:?} {write}"),
                    r => panic!("{z} {cmp:?} {write}: {r:?}"),
                }
            }
            // always without a depth write never reads the depth: drawn, as before
            let o = [Listed { mode: mode(Cmp::Always, false), prims: &t, left: 1, right: 1 }];
            assert_eq!(resolve_tile((0, 0), 0.0, &o).unwrap()[0].tag, Some((0, 0)));
        }
        // the bounds themselves are inside, a vertex off the triangle's tile is not looked at
        for z in [0.0f32, 1.0] {
            let o = [Listed { mode: mode(Cmp::Less, true), prims: &[flat(0, z)], left: 1, right: 1 }];
            assert!(resolve_tile((0, 0), 0.5, &o).is_ok(), "{z}");
        }
        let off = Tri { v: [(100 * 256, 0), (120 * 256, 0), (100 * 256, 20 * 256)], z: [-1.0; 3] };
        let o = [Listed { mode: mode(Cmp::Less, true), prims: &[off], left: 1, right: 1 }];
        assert!(resolve_tile((0, 0), 0.5, &o).is_ok(), "no covered pixel in this tile");
    }

    // ---- 12.4: a tile that starts from a loaded depth, several objects ----

    fn loaded(first_half: f32, second_half: f32) -> [f32; 512] {
        let mut s = [0.0f32; 512];
        for (k, d) in s.iter_mut().enumerate() {
            *d = if k % 32 < 16 { first_half } else { second_half };
        }
        s
    }

    #[test]
    fn resolve_from_the_clear_value_is_resolve_tile() {
        let t = [flat(0, 0.5)];
        let o = [Listed { mode: mode(Cmp::Less, true), prims: &t, left: 1, right: 1 }];
        assert_eq!(
            resolve_tile_from((0, 0), &[1.0; 512], &o).unwrap(),
            resolve_tile((0, 0), 1.0, &o).unwrap()
        );
    }

    #[test]
    fn a_loaded_depth_decides_each_pixel_for_every_object_in_list_order() {
        // two objects over a depth loaded 0.25 on the left half and 0.75 on the right: the first
        // (z 0.5) loses on the left and wins on the right; the second (z 0.625, written depth
        // 0.5 by the first) loses on the right where the first stands
        let (a, b) = ([flat(0, 0.5)], [flat(0, 0.625)]);
        let o = [
            Listed { mode: mode(Cmp::Less, true), prims: &a, left: 1, right: 1 },
            Listed { mode: mode(Cmp::Less, true), prims: &b, left: 1, right: 1 },
        ];
        let px = resolve_tile_from((0, 0), &loaded(0.25, 0.75), &o).unwrap();
        assert_eq!((px[0].tag, px[0].depth), (None, 0.25));
        // the 20-pixel triangle covers x < 20 - y: pixel (17, 0) is on the right half
        assert_eq!((px[17].tag, px[17].depth), (Some((0, 0)), 0.5));
    }

    #[test]
    fn the_second_object_wins_where_it_is_nearer_than_the_first() {
        let (a, b) = ([flat(0, 0.5)], [flat(0, 0.375)]);
        let o = [
            Listed { mode: mode(Cmp::Less, true), prims: &a, left: 1, right: 1 },
            Listed { mode: mode(Cmp::Less, true), prims: &b, left: 1, right: 1 },
        ];
        let px = resolve_tile_from((0, 0), &[1.0; 512], &o).unwrap();
        assert_eq!((px[0].tag, px[0].depth), (Some((1, 0)), 0.375));
    }

    #[test]
    fn a_start_depth_compares_with_its_sign_cleared_and_nan_above_every_depth() {
        // E995 (14 of 14 held out) and E977: the loaded dword's magnitude, NaN and infinity above
        let t = [flat(0, 0.5)];
        for (c, v, drawn) in [
            (Cmp::Less, f32::NAN, true),
            (Cmp::Greater, f32::NAN, false),
            (Cmp::LessEqual, f32::NAN, true),
            (Cmp::GreaterEqual, f32::NAN, false),
            (Cmp::Equal, f32::NAN, false),
            (Cmp::NotEqual, f32::NAN, true),
            (Cmp::Less, f32::INFINITY, true),
            (Cmp::Greater, f32::INFINITY, false),
            (Cmp::Less, -0.25, false),
            (Cmp::Greater, -0.25, true),
            (Cmp::Less, -0.75, true),
        ] {
            let o = [Listed { mode: mode(c, false), prims: &t, left: 1, right: 1 }];
            let px = resolve_tile_from((0, 0), &[v; 512], &o).unwrap();
            assert_eq!(px[0].tag.is_some(), drawn, "{c:?} against {v}");
            // a pixel the triangle does not draw keeps the loaded value itself
            assert_eq!(px[0].depth.to_bits(), (v as f64).to_bits(), "{c:?} {v}");
        }
    }

    #[test]
    fn a_loaded_depth_within_the_planes_tolerance_refuses_q200() {
        let t = [flat(0, 0.5)];
        let o = [Listed { mode: mode(Cmp::Less, true), prims: &t, left: 1, right: 1 }];
        let start = [(0.5 + DEPTH_UNIT) as f32; 512];
        let Err(Outcome::Unsupported { ids, .. }) = resolve_tile_from((0, 0), &start, &o) else { panic!() };
        assert_eq!(ids, ["Q200"]);
    }
}
