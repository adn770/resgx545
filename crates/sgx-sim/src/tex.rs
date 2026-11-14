// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The texture unit, as far as it is measured (doc/isa/content/usse/probe/
//! sampling.md and sampler-state.md): an smp's four state words T0-T3 (the
//! PDS doutt words, probes/texture/state-words.toml) and its coordinates
//! give the registers the sample writes. Texels are read through `load`.
//! Mipmaps follow E041 (a twiddled square chain, levels by the LOD, the
//! nearest or a blend of two); border modes, tiled layouts, PCF beyond one
//! split, the LOD of a quad's own derivatives and the formats the probes only
//! recorded are not established and stop with Err(why).

/// One sample: the state words, the normalized coordinates, whether the
/// texture is read as 1D (row 0), .pcf's reference and the level of detail.
#[derive(Clone, Copy, Debug)]
pub struct Sample {
    pub state: [u32; 4],
    pub u: f32,
    pub v: f32,
    pub one_d: bool,
    pub srd: Srd,
    pub pcf: Option<f32>,
    pub lod: Lod,
}

/// smp's SRD mode (E042): what the sample returns in place of the filtered
/// texel.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Srd {
    /// The filtered texel.
    None,
    /// .sinf: the sampling decision, the blend fraction and the level.
    Info,
    /// .rsd: the texels a filtered sample would blend, not filtered.
    Raw,
}

/// What gives a sample its LOD (E041).
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Lod {
    /// No LOD of its own, every instance at the same coordinates: zero
    /// derivatives, so minus infinity whatever a bias says (texture-mipmaps-mip-bias,
    /// texture-mipmaps-mip-level case 12 read level 0).
    Flat,
    /// smp*replace's value.
    Value(f32),
    /// smp2dgrad's du/dx, dv/dx, du/dy, dv/dy (normalized).
    Grad([f32; 4]),
    /// Not known: why.
    Open(&'static str),
}

/// A load of the dword at an address (4-aligned): the texels' memory.
pub type Load<'a> = dyn FnMut(u32) -> Result<u32, crate::Error> + 'a;

/// What a sample does, or why it is not known.
#[derive(Debug, PartialEq)]
pub enum Fail {
    Open(String),
    Load(crate::Error),
}

fn open<T>(s: impl Into<String>) -> Result<T, Fail> {
    Err(Fail::Open(s.into()))
}

/// The registers the sample writes, in order.
pub fn sample(s: &Sample, load: &mut Load) -> Result<Vec<u32>, Fail> {
    let [t0, t1, t2, t3] = s.state;
    let mut tex = Texture::new(t0, t1, t2, t3)?;
    let (levels, bilinear) = tex.pick(t0, &s.lod, s.one_d)?;
    let (u, v) = (s.u as f64, if s.one_d { 0.0 } else { s.v as f64 });
    if t3 >> 14 & 1 != 0 && tex.row.is_none() {
        // T3 bit 14 on a twiddled texture (E1047: E566's 32 x 32 32-bit texture, three fills
        // with a 1 MiB scratch, E566's and E1033's faults the reads past 64 KiB; E1049: held out
        // at W 16, 64 and 128 with H 32, u in (0, 1), (1, 2) and (2, 3), and a u16 32 x 32):
        // column s + floor(4096 frac(u)), s the wrapped bit-clear column, in E561's 16 x 16
        // tiles with a tile row of W + 4096 texels (a constant 4128 failed 6 of 6), in texels on
        // u16 (the half T & 1 of dword T >> 1). Other heights and widths, filtered samples
        // (E1049's bilinear footprint is post hoc), other modes and formats stay open (Q078)
        if !matches!(tex.w, 16 | 32 | 64 | 128)
            || tex.h != 32
            || !matches!(tex.format, 9 | 12)
            || bilinear
            || levels != [(0, 64)]
            || s.pcf.is_some()
            || s.srd != Srd::None
            || s.one_d
            || t3 >> 16 & 3 != 0
            || tex.offset != [0, 0]
            || tex.shift != 0
            || tex.address != [0, 0]
        {
            return open(
                "T3 bit 14 on a twiddled texture other than E1047's and E1049's: W 16 to 128 by 32, \
                 format 12 or 9, point sampled, repeat, unconverted (Q078)",
            );
        }
        let w = tex.w;
        let col = ((u * w as f64).floor() as i64).rem_euclid(w as i64) as u32
            + (4096.0 * (u - u.floor())).floor() as u32;
        let row = tex.row_of(v, false).rem_euclid(32) as u32;
        let bytes = if tex.format == 9 { 2 } else { 4 };
        let a = tex.base.wrapping_add(morton(col, row, w + 4096, 32) * bytes);
        let dw = load(a & !3).map_err(Fail::Load)?;
        return Ok(vec![if bytes == 4 { dw } else { dw >> (8 * (a & 3)) & 0xffff }]);
    }
    if t3 >> 14 & 1 != 0 {
        // T3 bit 14 on a stride texture (E1003, held out on six geometries; E975 post hoc; on a
        // twiddled texture above): the
        // bit-clear texel moved by floor(4096 clamp(u, 0, 1)) texels, measured point sampled, on
        // level 0, at formats 12 (32-bit) and 9 (16-bit), without T3's offset, scale or conversion
        if bilinear
            || levels != [(0, 64)]
            || s.pcf.is_some()
            || s.srd != Srd::None
            || s.one_d
            || t3 >> 16 & 3 != 0
            || tex.offset != [0, 0]
            || tex.shift != 0
            || !matches!(tex.format, 9 | 12)
        {
            return open(
                "T3 bit 14 filtered, blended, converted, offset, 1D or at a format other than 9 or 12",
            );
        }
        tex.extra = (4096.0 * u.clamp(0.0, 1.0)).floor() as u32;
    }
    if (tex.offset != [0, 0] || tex.shift != 0) && (bilinear || s.pcf.is_some() || s.srd != Srd::None) {
        return open("T3's texel offset or address scale filtered, with .pcf or an SRD mode");
    }
    if tex.format == 27 || tex.srgb {
        // E723, E724: point samples of level 0, as Texture::new admits them; E982: sRGB bilinear
        // (on E723's fills only; E1004: the rule misses where a stage's result is subnormal)
        if let [(la, _), (lb, f)] = levels[..]
            && tex.srgb
            && bilinear
            && s.pcf.is_none()
            && s.srd == Srd::None
        {
            // E1038: a trilinear sRGB sample (T0 bits 27 and 9) lerps the two levels' bilinear
            // halves by srgb_level_lerp at f / 64, f the LOD's fraction in 64ths floored (pick)
            let (a, b) = (
                tex.level(la).srgb_bilinear(u, v, s.one_d, load)?,
                tex.level(lb).srgb_bilinear(u, v, s.one_d, load)?,
            );
            return Ok(vec![(0..2).fold(0, |o, c| {
                o | srgb_level_lerp(a >> (16 * c) & 0xffff, b >> (16 * c) & 0xffff, f) << (16 * c)
            })]);
        }
        if levels != [(0, 64)] || s.pcf.is_some() || s.srd != Srd::None || bilinear && tex.format == 27 {
            return open(
                "ETC1 or sRGB blended other than E1038's trilinear, with .pcf or an SRD mode, or ETC1 \
                 filtered (not run; E1038 measured the trilinear lerp)",
            );
        }
        if bilinear {
            return Ok(vec![tex.srgb_bilinear(u, v, s.one_d, load)?]);
        }
        let (x, y) = ((u * tex.w as f64).floor() as i64, tex.row_of(v, s.one_d));
        return Ok(vec![if tex.format == 27 {
            tex.etc1(x, y, load)?
        } else {
            srgb_word(tex.fetch(x, y, load)?)
        }]);
    }
    if tex.format == 14 {
        // two registers (format_14): one level, point sampled, unconverted
        return match levels[..] {
            [(l, _)] if !bilinear && s.pcf.is_none() && s.srd == Srd::None && t3 >> 16 & 3 == 0 => {
                let t = tex.level(l);
                let raw = t.fetch((u * t.w as f64).floor() as i64, t.row_of(v, s.one_d), load)?;
                Ok(format_14(raw).to_vec())
            }
            _ => open("format 14 filtered, blended, converted, with .pcf or an SRD mode"),
        };
    }
    if s.srd != Srd::None {
        if s.pcf.is_some() {
            return open("an SRD mode with .pcf");
        }
        if t3 >> 16 & 3 != 0 {
            return open("a conversion with an SRD mode");
        }
        if tex.format != 12 {
            return open(format!("an SRD mode on format {}", tex.format));
        }
    }
    match s.srd {
        Srd::None => {}
        Srd::Info => return info(&tex, t0, &levels, bilinear),
        Srd::Raw => return raw(&tex, &levels, bilinear, u, v, s.one_d, load),
    }
    if let Some(r) = s.pcf
        && !tex.colour()
    {
        if t3 >> 16 & 3 != 0 {
            return open("a conversion with .pcf");
        }
        if levels != [(0, 64)] {
            return open(".pcf on a level other than 0");
        }
        let (t, w) = if bilinear {
            tex.quad(u, v, s.one_d, load)?
        } else {
            ([tex.fetch((u * tex.w as f64).floor() as i64, tex.row_of(v, s.one_d), load)?; 4], [1024; 4])
        };
        return tex.pcf(t, w, r, t3 >> 29).map(|v| vec![v]);
    }
    let colour = if let [(l, _)] = levels[..] {
        tex.level(l).filtered(u, v, bilinear, s.one_d, load)?.0
    } else {
        // T0 bit 9 (texture-mipmaps-mip-mipfilter): each channel blends the two levels by
        // the LOD's fraction in 1/64 (E042's six-bit fraction), to nearest,
        // halves up; levels that round on their own are not measured
        let mut out = 0;
        let mut texels = [0u32; 2];
        for (k, &(l, _)) in levels.iter().enumerate() {
            let (t, exact) = tex.level(l).filtered(u, v, bilinear, s.one_d, load)?;
            if !exact {
                return open("a blend of filtered levels that round on their own");
            }
            texels[k] = t;
        }
        let (wa, wb) = (levels[0].1, levels[1].1);
        if tex.format == 9 {
            // E1052 (u16 32 x 16, f 32, held out): one 16-bit lerp, (a (64 - f) + b f + 32) >> 6;
            // the per-byte blend of the colour formats missed 512 of 2048 pixels
            return convert((texels[0] * wa + texels[1] * wb + 32) >> 6, t3, tex.format);
        }
        for c in 0..4 {
            let (a, b) = (texels[0] >> (8 * c) & 0xff, texels[1] >> (8 * c) & 0xff);
            out |= (a * wa + b * wb + 32) >> 6 << (8 * c);
        }
        out
    };
    convert(colour, t3, tex.format)
}

/// .sinf (texture-sampler-smp-srd, E042): two dwords, the blend fraction between the
/// levels in bits 23:16 of the first (its six bits with their top two
/// repeated below them) and the level in the second (the nearest, or the
/// lower of the two blended). Measured on a mip chain with point filters:
/// the mip filter nearest at any LOD (fraction 0) and linear between two
/// levels.
fn info(tex: &Texture, t0: u32, levels: &[(u32, u32)], bilinear: bool) -> Result<Vec<u32>, Fail> {
    if tex.row.is_some() || t0 >> 18 & 1 != 0 || t0 >> 19 & 3 == 0 || t0 >> 21 & 0x3f != 0x3f {
        return open(".sinf without a mip chain");
    }
    if bilinear || matches!(t0 >> 12 & 3, 1 | 2) {
        return open(".sinf with bilinear filtering");
    }
    match *levels {
        [(l, _)] if t0 >> 9 & 1 == 0 => Ok(vec![0, l]),
        [(_, _)] => open(".sinf under the linear mip filter at a whole LOD"),
        [(l, _), (_, f)] => Ok(vec![(f << 2 | f >> 4) << 16, l]),
        _ => unreachable!(),
    }
}

/// .rsd (texture-sampler-smp-srd, E042): with point sampling of one level the texel, as
/// without the mode; filtering two levels bilinearly, each level's 2x2
/// footprint, not filtered, the lower level first, each in quad's order (x0,
/// y0), (x1, y0), (x0, y1), (x1, y1). One bilinear level, or two point ones,
/// are not measured.
fn raw(
    tex: &Texture,
    levels: &[(u32, u32)],
    bilinear: bool,
    u: f64,
    v: f64,
    one_d: bool,
    load: &mut Load,
) -> Result<Vec<u32>, Fail> {
    match (levels, bilinear) {
        ([(l, _)], false) => Ok(vec![tex.level(*l).filtered(u, v, false, one_d, load)?.0]),
        ([_, _], true) if !one_d => {
            let mut out = Vec::new();
            for &(l, _) in levels {
                out.extend(tex.level(l).quad(u, v, one_d, load)?.0);
            }
            Ok(out)
        }
        ([_], true) => open(".rsd of one bilinear level"),
        _ => open(".rsd of point-sampled levels blended"),
    }
}

/// T3 bits 17:16 convert the texel, bit 15 normalizing (texture-sampler-smp-convert): none,
/// c10, f16 pairs or f32 channels, from the B8G8R8A8 channels. Without alpha
/// (565) c10 and f32 leave its register out and f16 gives 1.0. T3's other
/// fields: see t3_fields.
fn convert(texel: u32, t3: u32, format: u32) -> Result<Vec<u32>, Fail> {
    let conv = t3 >> 16 & 3;
    if conv == 0 {
        return Ok(vec![texel]);
    }
    let norm = t3 >> 15 & 1 != 0;
    // the other formats' channels, in order (texture-sampler-smp-convert): u8 (0), two u8
    // (7, the low byte first), u16 (9; c10 takes its top byte)
    let (chans, max): (Vec<u32>, f32) = match format {
        0 => (vec![texel & 0xff], 255.0),
        7 => (vec![texel & 0xff, texel >> 8 & 0xff], 255.0),
        9 => (vec![texel & 0xffff], 65535.0),
        11 | 18 => return float_convert(texel, conv, norm, format),
        2..=5 | 12 | 13 => (vec![], 0.0),
        f => return open(format!("a conversion of format {f}")),
    };
    if !chans.is_empty() {
        let value = |c: u32| if norm { c as f32 / max } else { c as f32 };
        return Ok(match conv {
            1 if norm => return open("c10 with normalization"),
            2 if !norm && chans.iter().any(|&c| c > 65504) => return open("f16 past the largest half"),
            1 => vec![
                chans
                    .iter()
                    .enumerate()
                    .map(|(k, &c)| (if max > 255.0 { c >> 8 } else { c }) << (10 * k))
                    .sum(),
            ],
            2 => chans
                .chunks(2)
                .map(|p| p.iter().enumerate().map(|(k, &c)| half(value(c)) << (16 * k)).sum())
                .collect(),
            _ => chans.iter().map(|&c| value(c).to_bits()).collect(),
        });
    }
    let alpha = format != 5;
    let [b, g, r, a] = [0, 1, 2, 3].map(|c| texel >> (8 * c) & 0xff);
    let value = |c: u32| if norm { c as f32 / 255.0 } else { c as f32 };
    Ok(match conv {
        1 => {
            if norm {
                return open("c10 with normalization");
            }
            let mut v = vec![b | g << 10 | r << 20, a];
            v.truncate(1 + alpha as usize);
            v
        }
        2 => {
            let h = |c: u32| half(value(c));
            vec![h(r) | h(g) << 16, h(b) | if alpha { h(a) } else { 0x3c00 } << 16]
        }
        _ => [b, g, r, a][..3 + alpha as usize].iter().map(|&c| value(c).to_bits()).collect(),
    })
}

/// The float formats converted (x-smp3 136-143: format 11's half 0xD000,
/// -32.0, and 18's f32 0xD00004FF, about -8.6e9): f32 the value exactly,
/// bit 15 not acting; f16 11's half as it is and 18's saturated at -65504;
/// c10 x * 255 saturated at -510 (0x202), as pckc10f32 does. Values neither
/// saturation reaches, positive saturation and normalized c10 or f16 are not
/// measured.
fn float_convert(texel: u32, conv: u32, norm: bool, format: u32) -> Result<Vec<u32>, Fail> {
    let x = if format == 11 { half_to_f32(texel & 0xffff) } else { f32::from_bits(texel) };
    if !x.is_finite() {
        return open(format!("a conversion of a NaN or infinite texel of format {format}"));
    }
    Ok(vec![match conv {
        3 => x.to_bits(),
        _ if norm => return open(format!("a normalized c10 or f16 of format {format}")),
        2 if format == 11 => texel & 0xffff,
        2 if x < -65504.0 => 0xfbff,
        2 => return open("f16 of an f32 texel a half holds, or positive (not measured)"),
        _ if x <= -2.0 => 0x202,
        _ => return open(format!("c10 of a format {format} texel above -2 (not measured)")),
    }])
}

/// A half as an f32, exactly (not an infinity or NaN: the caller checks).
fn half_to_f32(h: u32) -> f32 {
    let (e, f) = (h >> 10 & 31, h & 1023);
    let mag = match (e, f) {
        (31, 0) => f32::INFINITY,
        (31, _) => f32::NAN,
        (0, _) => f as f32 * 2f32.powi(-24),
        _ => (1024 + f) as f32 * 2f32.powi(e as i32 - 25),
    };
    if h >> 15 != 0 { -mag } else { mag }
}

/// T3's fields beyond the conversion (x-smp2, one bit at a time on texel
/// (3, 5) of a stride texture): the texel offset 7:4 (x) and 3:0 (y), signed,
/// and the address scale 19:18 (1 or 2, the texel's byte offset from the base
/// shifted left by it); bits 8, 9, 12 and 20-22 change nothing there. The
/// compare mode 31:29 (for .pcf) and the data size 26:23 change nothing seen;
/// bit 11: the captured pixel fetches of the closed driver set it (0x00800800)
/// **[CAP]**, the mip probes (E041), which do, read as the model without it. On a twiddled
/// texture only those are measured, and bit 14 at W 16 to 128 by 32 (E1047, E1049, see sample); bits 10, 13,
/// 27 and 28 act in ways not modelled here; bits 11 and 12 change nothing on a strided texture again in E975, and on a
/// twiddled chain select the level (E1027, Texture::pick). Bit 14 on
/// a stride texture moves the texel by floor(4096 clamp(u, 0, 1)) texels (E968's S * S rule
/// failed; E975 post hoc; E1003: texels, not dwords, on a 16-bit texture; held out on six
/// geometries), see sample.
fn t3_fields(t3: u32, stride: bool) -> Result<([i64; 2], u32), Fail> {
    let not_measured = if stride { 0x1800_2400 } else { 0x187c_27ff };
    if t3 & not_measured != 0 {
        return open(format!("T3 bits 0x{:08x}", t3 & not_measured));
    }
    let shift = t3 >> 18 & 3;
    if shift == 3 {
        return open("T3 bits 19:18 = 3");
    }
    let s4 = |v: u32| ((v as i64) << 60) >> 60;
    Ok(([s4(t3 >> 4 & 15), s4(t3 & 15)], shift))
}

/// Format 14's texel (texture-sampler-smp-formats-other 4-7): A2B10G10R10, each field
/// widened to 16 bits by repeating its bits, in two registers R | G << 16 and
/// B | A << 16.
fn format_14(t: u32) -> [u32; 2] {
    let w = |v: u32| v << 6 | v >> 4;
    let a = (t >> 30) * 0x5555;
    [w(t & 0x3ff) | w(t >> 10 & 0x3ff) << 16, w(t >> 20 & 0x3ff) | a << 16]
}

/// A float in [0, 65535] as a half, rounded to nearest even.
fn half(x: f32) -> u32 {
    if x == 0.0 {
        return 0;
    }
    let e = (x.log2().floor() as i32).max(-14);
    if e == -14 && x < 2f32.powi(-14) {
        // a subnormal: m * 2^-24 (1024 is the smallest normal, 0x0400)
        return (x as f64 * 2f64.powi(24)).round_ties_even() as u32;
    }
    let m = (x as f64 / 2f64.powi(e - 10)).round_ties_even() as u32;
    // a mantissa that rounded up to 2048 is the next exponent's 1024
    let (m, e) = if m == 2048 { (1024, e + 1) } else { (m, e) };
    ((e + 15) as u32) << 10 | (m & 0x3ff)
}

/// sRGB to linear (the curve of the sRGB standard) of a byte, as a half, rounded to nearest even
/// from the double value (E723: 4 of 4 held-out fills exact, every byte 0 to 255 read).
fn srgb_half(b: u32) -> u32 {
    let c = b as f64 / 255.0;
    let l = if c <= 0.04045 { c / 12.92 } else { ((c + 0.055) / 1.055).powf(2.4) };
    half64(l)
}

/// The first register of a point sample with T0 bit 27 (E723): byte 1 of the texel decoded in the
/// high half, byte 0 in the low one. The second register (E723's r11 reads) is not modelled.
fn srgb_word(t: u32) -> u32 {
    srgb_half(t >> 8 & 0xff) << 16 | srgb_half(t & 0xff)
}

/// A double in [0, 1] as a half, rounded to nearest even (the exponent read from its bits).
fn half64(x: f64) -> u32 {
    half_rounded(x, f64::round_ties_even)
}

/// A double in [0, 1] as a half, rounded to the half grid by `round`.
fn half_rounded(x: f64, round: fn(f64) -> f64) -> u32 {
    if x == 0.0 {
        return 0;
    }
    let e = ((x.to_bits() >> 52 & 0x7ff) as i32 - 1023).max(-14);
    if e == -14 && x < 2f64.powi(-14) {
        return round(x * 2f64.powi(24)) as u32;
    }
    let m = round(x / 2f64.powi(e - 10)) as u32;
    let (m, e) = if m == 2048 { (1024, e + 1) } else { (m, e) };
    ((e + 15) as u32) << 10 | (m & 0x3ff)
}

/// The value of a half in [0, 1].
fn half_value(h: u32) -> f64 {
    let (e, m) = ((h >> 10 & 31) as i32, (h & 0x3ff) as f64);
    if e == 0 { m * 2f64.powi(-24) } else { (1024.0 + m) * 2f64.powi(e - 25) }
}

/// One lerp stage of a bilinear sRGB sample (E982: exact on r9-x's 16384 single-stage halves,
/// held out offline on three two-stage fills; a later held-out row missed it, E1004): at weight
/// 0 the first half unchanged; else both halves floored to the ulp of the larger one (an 11-bit
/// mantissa at its exponent), lerped exactly by k / 64 towards `b`, and rounded to a half,
/// nearest with ties up; a result below 2^-14 (a subnormal half) is flushed to +0 (E1004 post
/// hoc, held out offline on an-t0b27's 12 halves where it parts, one pixel column, E1016; held out
/// on hardware with the y stage's own result flushed, five strided rows reading each stage alone
/// and both, the threshold between 5.69e-5 and 6.16e-5, E1025).
fn srgb_stage(a: u32, b: u32, k: u32) -> u32 {
    srgb_floored_lerp(a, b, k, 10)
}

/// The lerp of a trilinear sRGB sample between the two levels' halves (E1038, held out on seven
/// rows of two chains at seven LODs, every pixel; fitted on E1025's row before the run): as
/// `srgb_stage` but with both halves floored to 2^-14 of the larger one's leading bit (a 15-bit
/// grid, the stage rule's is 11), the result below 2^-14 flushed to +0 (the dark chain's row
/// parts the flush, 224 pixels).
fn srgb_level_lerp(a: u32, b: u32, k: u32) -> u32 {
    srgb_floored_lerp(a, b, k, 14)
}

/// A lerp of halves by k / 64 with both floored to 2^-`bits` of the larger one's leading bit,
/// exact, rounded to a half nearest with ties up, a result below 2^-14 flushed to +0; at k = 0
/// the first half unchanged.
fn srgb_floored_lerp(a: u32, b: u32, k: u32, bits: i32) -> u32 {
    if k == 0 {
        return a;
    }
    let (fa, fb) = (half_value(a), half_value(b));
    let top = fa.max(fb);
    if top == 0.0 {
        return 0;
    }
    let g = 2f64.powi((top.to_bits() >> 52 & 0x7ff) as i32 - 1023 - bits);
    let (qa, qb) = ((fa / g).floor() * g, (fb / g).floor() * g);
    let h = half_rounded(qa + k as f64 / 64.0 * (qb - qa), |v| (v + 0.5).floor());
    if h < 0x0400 { 0 } else { h }
}

/// Why the registers a sample writes after those `sample` returns are not known, if they are not:
/// an sRGB sample (T0 bit 27) writes a second register, texel bytes 2 and 3 (E1038: byte 2 by the
/// first register's rule in the low half, byte 3 decoded b / 255 and filtered by `srgb_stage` in
/// the high one, held out on three bilinear rows; E723's point reads post hoc), not modelled here.
pub fn unknown_after(state: [u32; 4]) -> Option<&'static str> {
    (state[0] >> 27 & 1 != 0).then_some(
        "an sRGB sample's register after the first (bytes 2 and 3: E723 read it, E1038 measured it; not modelled)",
    )
}

/// The texture words of the fills of E723 to E725 (p1141): T0 point filters, repeat, level 0
/// only; T3 of a twiddled and of a stride texture.
const T0_REP: u32 = 0x07fe_0000;
const T3_TW: u32 = 0x0080_0800;
const T3_ST: u32 = 0xa080_0000;
/// E723's stride texture: T0_REP's role with the stride of 8 dwords and bit 27.
const T0_SRGB_STRIDE8: u32 = 0x0800_0e00;
/// E723's bilinear fills (g-bl-st-a and -b, 8 x 8): the same with bilinear filters (E982).
const T0_SRGB_BL_STRIDE8: u32 = 0x0800_1e00;
/// E1025's and E1038's trilinear chains (16 x 16 and 4 x 4, twiddled): sRGB, the LOD the operand
/// (26:21 0x3f), max level 14, bilinear both ways, T0 bit 9.
const T0_SRGB_TRI: u32 = 0x0ffc_1600;
/// The sizes E724 ran format 27 at and E725 types 1 and 3 at (twiddled block grids, rasters), and
/// those E910 held the raster of the width out at in the window's 64 columns: 4 x 16 for type 1,
/// 64 x 8 for both (type 3 at 4 x 16 read rows 8 dwords apart; 128 x 8 ran, but only its first
/// 64 columns were read).
const ETC1_SIZES: [(u32, u32); 5] = [(16, 16), (32, 16), (16, 32), (8, 16), (8, 8)];
const RASTER_SIZES: [(u32, u32); 4] = [(8, 8), (32, 32), (32, 16), (16, 32)];
const RASTER_SIZES_E910: [(u32, u32); 2] = [(4, 16), (64, 8)];
/// E940 (held out): type 3 below 8 wide (its rows max(8, w) dwords apart, with E910's 4 x 16) and
/// at 24 and 40 wide, type 1 at 2 and 1 wide.
const TYPE3_SIZES_E940: [(u32, u32); 8] =
    [(4, 16), (2, 16), (4, 8), (4, 32), (2, 8), (1, 16), (24, 8), (40, 8)];
const TYPE1_SIZES_E940: [(u32, u32); 2] = [(2, 16), (1, 16)];
/// E958 (held out): type 1 at 24 and 40 wide, a raster of the width.
const TYPE1_SIZES_E958: [(u32, u32); 2] = [(24, 8), (40, 8)];
/// E958 (held out): type 3 of format 5 (16-bit texels), rows max(8, w) texels apart.
const TYPE3_F5_SIZES_E958: [(u32, u32); 2] = [(4, 8), (8, 8)];
/// Type 4's 32 x 32 blocks row by row at every size where all its texels were read: E910's
/// 4 x 16, 64 x 8 and 64 x 32, E941's held-out windows and E958's widths that are not multiples of
/// 32 (ceil(w / 32) blocks a block row).
const TYPE4_SIZES: [(u32, u32); 10] =
    [(4, 16), (64, 8), (64, 32), (64, 64), (128, 64), (128, 128), (256, 32), (48, 64), (80, 64), (96, 32)];
/// Type 5 (format 12, point filters) at E911's and E942's sizes.
const TYPE5_SIZES: [(u32, u32); 7] = [(8, 8), (16, 16), (32, 32), (64, 64), (32, 8), (8, 32), (16, 8)];

/// T0 bit 27 (sRGB), format 27 (ETC1) and texture types 1, 3, 4 and 5 are admitted with the state
/// words of the held-out jobs that measured them and at their sizes only (E723, E724, E725, E910,
/// E940, E941, E942, E958).
fn measured_r4(t0: u32, t1: u32, t3: u32) -> Result<(), Fail> {
    let (ty, fmt) = (t1 >> 29, t1 >> 24 & 31);
    let (w, h) = ((t1 >> 12 & 0xfff) + 1, (t1 & 0xfff) + 1);
    let ok = if t0 >> 27 & 1 != 0 {
        fmt == 12
            && match ty {
                6 => {
                    ((w, h) == (8, 4) && t0 == T0_SRGB_STRIDE8
                        || (w, h) == (8, 8) && t0 == T0_SRGB_BL_STRIDE8)
                        && t3 == T3_ST
                }
                0 => {
                    (matches!((w, h), (8, 8) | (32, 32)) && t0 == T0_REP | 1 << 27
                        || matches!((w, h), (16, 16) | (4, 4)) && t0 == T0_SRGB_TRI)
                        && t3 == T3_TW
                }
                _ => false,
            }
    } else if fmt == 27 {
        ty == 0 && ETC1_SIZES.contains(&(w, h)) && t0 == T0_REP && t3 == T3_TW
    } else {
        let sized = match ty {
            1 => {
                RASTER_SIZES.contains(&(w, h))
                    || RASTER_SIZES_E910.contains(&(w, h))
                    || TYPE1_SIZES_E940.contains(&(w, h))
                    || TYPE1_SIZES_E958.contains(&(w, h))
            }
            3 => RASTER_SIZES.contains(&(w, h)) || (w, h) == (64, 8) || TYPE3_SIZES_E940.contains(&(w, h)),
            4 => TYPE4_SIZES.contains(&(w, h)),
            5 => TYPE5_SIZES.contains(&(w, h)),
            _ => false,
        };
        // E958: type 3 of format 5 at its two held-out sizes
        let f5 = ty == 3 && fmt == 5 && TYPE3_F5_SIZES_E958.contains(&(w, h));
        // E1055: types 1, 3 and 4 at 16 x 16 (E567's images, replicated by E1039's references)
        // and 32 x 32 (held out: type 4 its block, 32 t + s), in mode 0 and with u mode 4
        let e1055 = matches!(ty, 1 | 3 | 4) && matches!((w, h), (16, 16) | (32, 32)) && fmt == 12;
        let t0_ok = t0 == T0_REP || e1055 && t0 == T0_REP | 4 << 6;
        (fmt == 12 && sized || f5 || e1055) && t0_ok && t3 == T3_TW
    };
    if !ok
        && matches!(ty, 1 | 3 | 4)
        && fmt == 12
        && t3 == T3_TW
        && (4..8).contains(&(t0 >> 6 & 7))
        && t0 == T0_REP | (t0 >> 6 & 7) << 6
    {
        // E1065: E1055's two-size fit of the name (39 W + 52, type 4 40 W + 20) failed at 8 x 8,
        // 64 x 64 and 64 x 16 (types 1 and 3: every row; type 4 held at 8 x 8 only); modes 6 and
        // 7 at 64 x 64 and mode 5 at 8 x 8 and 64 x 64 read other names, post hoc only
        return open(format!(
            "T0 0x{t0:08x}, T1 0x{t1:08x}: u modes 4 to 7 of types 1, 3 and 4 ran at 16 x 16 and 32 x 32 only (E1055); \
             the fit of their name, 39 W + 52 (40 W + 20), failed at 8 x 8, 64 x 64 and 64 x 16 (E1065, post hoc \
             readings only; Q177)"
        ));
    }
    if !ok {
        return open(format!(
            "T0 0x{t0:08x}, T1 0x{t1:08x}, T3 0x{t3:08x}: sRGB (E723), format 27 (E724) and types 1 and 3 \
             (E725, E910, E940, E958), 4 (E941, E958) and 5 (E942) ran only with the state words and at the sizes of their \
             held-out jobs (sRGB: E982's, E1025's and E1038's words only)"
        ));
    }
    Ok(())
}

#[derive(Clone, Copy)]
struct Texture {
    w: u32,
    h: u32,
    format: u32,
    base: u32,
    /// Bytes per row of a stride texture, None for a twiddled one.
    row: Option<u32>,
    address: [u32; 2],
    /// T3's texel offset (x, y) and address scale (t3_fields).
    offset: [i64; 2],
    shift: u32,
    /// T3 bit 14's texels past the addressed one (sample; 0 without the bit).
    extra: u32,
    /// Types 1, 3, 4 and 5: a layout of their own that wraps at the size by the address modes
    /// (E725, E940, E941, E942).
    raster: bool,
    /// Type 4: 32 x 32 blocks of 1024 dwords, numbered row by row (E941).
    blocks: bool,
    /// Type 5: one bit per 8 texels, bit 0 of dword floor(t / 8), t = y w + x (E942).
    bits: bool,
    /// T0 bit 27: the sRGB decode (E723).
    srgb: bool,
    /// T3 bits 12:11 on a twiddled texture (E1027): 1 the LOD's level, 0 level 0, 2 and 3 the
    /// last level T0's max level allows (pick).
    lodsel: u32,
}

impl Texture {
    /// T0's measured fields: the stride or (twiddled) the mip fields 26:17
    /// (see pick), filters 13:12, the min and mip filters or STRIDELO 11:9,
    /// the address modes 8:0; on a stride texture bits 14-16, 28 and 29 change
    /// nothing (x-smp2 11-13, 15, 16). Any other bit (27, 30 the second format
    /// table, 31 the luma key's alpha: x-smp2 14, 17, 18 read other values),
    /// and T2's low two, is not measured. T3: t3_fields.
    fn new(t0: u32, t1: u32, t2: u32, t3: u32) -> Result<Texture, Fail> {
        let stride = t1 >> 29 == 6;
        let (srgb, raster) = (t0 >> 27 & 1 != 0, matches!(t1 >> 29, 1 | 3 | 4 | 5));
        if srgb || raster || t1 >> 24 & 31 == 27 {
            measured_r4(t0, t1, t3)?;
        }
        let t0_open = t0 & !(1 << 27) & if stride { 0xc800_0000 } else { 0xf801_c000 };
        if t0_open != 0 || t2 & 3 != 0 {
            return open(format!("T0 bits 0x{t0_open:08x}, T2 bits {}", t2 & 3));
        }
        let (w, h) = ((t1 >> 12 & 0xfff) + 1, (t1 & 0xfff) + 1);
        let row = match t1 >> 29 {
            // NP2_STRIDE_EXT: the stride in dwords minus 1, STRIDELO T0[11:9]
            // and STRIDEHI T0[26:17]
            6 => Some(((t0 >> 9 & 7 | (t0 >> 17 & 0x3ff) << 3) + 1) * 4),
            0 if w.is_power_of_two() && h.is_power_of_two() => None,
            // p1132 tx-types-risky: TEXTYPE 7 reads as twiddled; measured at 16x16 only
            7 if (w, h) == (16, 16) => None,
            // E725, E940: type 1 indexes a raster of w dwords per row, type 3 of max(8, w)
            // texels (E958: texels at format 5, so the row is set below from the texel's bytes;
            // measured_r4 checked them)
            1 => Some(4 * w),
            3 => Some(4 * w.max(8)),
            // E941: type 4's 32 x 32 blocks (fetch); E942: type 5's bits (fetch)
            4 => Some(128),
            5 => Some(4 * w),
            0 => return open("a twiddled texture of a size other than a power of two"),
            t => return open(format!("texture type {t}")),
        };
        let (offset, shift) = t3_fields(t3, stride)?;
        let mut tex = Texture {
            w,
            h,
            format: t1 >> 24 & 31,
            base: t2 & !3,
            row,
            address: [t0 >> 6 & 7, t0 >> 3 & 7],
            offset,
            shift,
            extra: 0,
            raster,
            blocks: t1 >> 29 == 4,
            bits: t1 >> 29 == 5,
            srgb,
            lodsel: if stride { 1 } else { t3 >> 11 & 3 },
        };
        if t1 >> 29 == 3 {
            // E940, E958: max(8, w) texels a row, 8 dwords at format 12, 8 16-bit words at format 5
            tex.row = Some(tex.bytes()? * w.max(8));
        }
        if tex.format == 27 {
            // ETC1's blocks have their own order (Texture::etc1); measured_r4 checked the rest
            return Ok(tex);
        }
        // E1049 (tw-refu16): a u16 32 x 32 read E561's tiles in texels, every pixel
        let u16_ran = tex.format == 9 && (w, h) == (32, 32);
        let u16_chain = tex.format == 9 && CHAIN16_SIZES.contains(&(w, h));
        if tex.row.is_none()
            && (w > 16 || h > 16)
            && !(tile_law_ran(w, h) && (tex.bytes()? == 4 || u16_ran))
            && !u16_chain
        {
            return open(format!(
                "a twiddled {w}x{h} texture of format {} (the 16 x 16 tiles ran only on 32-bit texels in the sizes of E561 and E562)",
                tex.format
            ));
        }
        if tex.bytes()? != 4 && shift != 0 {
            return open(format!("T3's address scale on format {}", tex.format));
        }
        if tex.format == 20 && !stride {
            return open("format 20 on a twiddled texture (its texel pairs)");
        }
        Ok(tex)
    }

    /// Level l of a twiddled chain (E041): the levels follow level 0 back
    /// to back, largest first, each twiddled at its own size, no padding.
    fn level(&self, l: u32) -> Texture {
        let bytes = self.bytes().unwrap_or(4);
        let side = |n: u32, k: u32| (n >> k).max(1);
        let off: u32 = (0..l).map(|k| bytes * side(self.w, k) * side(self.h, k)).sum();
        Texture { w: side(self.w, l), h: side(self.h, l), base: self.base.wrapping_add(off), ..*self }
    }

    /// The levels a sample reads, with their weights in 1/64, and whether
    /// it filters bilinearly (E041). The filter is T0 13:12's magnifying (LOD
    /// 0 or below) and 11:10's minifying (above 0; 1 and 2 linear, 0 and 3
    /// point, texture-mipmaps-mip-minfilter). T0 bit 18 set reads level 0 only, as do
    /// 20:19 = 0 and 26:21 = 0-3 or 7; 26:21 = 0x3f with 20:19 non-zero
    /// enables the chain (texture-mipmaps-mip-t0-field); 26:21 = 0 also keeps magnifying. The LOD clamps to [0, the last
    /// level]; T0 bit 9 = 0 takes the nearest level, a half rounding up, = 1
    /// blends the two around it (texture-mipmaps-mip-mipfilter).
    fn pick(&self, t0: u32, lod: &Lod, one_d: bool) -> Result<(Vec<(u32, u32)>, bool), Fail> {
        let mag = matches!(t0 >> 12 & 3, 1 | 2);
        let level0 = |bilinear: bool| Ok((vec![(0, 64)], bilinear));
        if self.row.is_some() {
            // a stride texture: 26:17 and 11:9 are its stride, so neither a
            // level nor a minification filter; a quad's own LOD samples as
            // enlarged (the copies' pixel vectors), a value above 0 is not
            // measured
            return match lod {
                Lod::Open(_) => level0(mag),
                _ if self.lambda(lod)?.0 <= 0.0 => level0(mag),
                _ => open("a LOD above 0 on a stride texture"),
            };
        }
        let min = matches!(t0 >> 10 & 3, 1 | 2);
        if self.lodsel != 1 {
            // E1027: T3 bits 12:11 = 00 read level 0 whatever the LOD (mips off too), 1x the last
            // level T0's max level allows; run with one filter both ways and without bit 9 only
            if mag != min || t0 >> 9 & 1 != 0 || one_d {
                return open("T3 bits 12:11 other than 01 with T0 bit 9, two filters or 1D (not run; Q078)");
            }
            let (mx, top) = (t0 >> 17 & 15, t0 >> 21 & 0x3f);
            if self.lodsel == 0 {
                return level0(min);
            }
            if top == 0 || mx == 0 || mx == 15 {
                return open("T3 bit 12 with mips off (not run; Q078)");
            }
            if self.w != self.h && !CHAIN_SIZES.contains(&(self.w, self.h)) {
                return open(format!("mipmaps of a non-square {}x{} texture (not run)", self.w, self.h));
            }
            let last = self.w.trailing_zeros().max(self.h.trailing_zeros()).min(mx);
            if last > 0 && self.bytes()? != 4 {
                return open("mip levels of a format other than 32 bits");
            }
            return Ok((vec![(last, 64)], min));
        }
        // E276, E441: bits 20:17 are the highest level read (0 and 15 level 0 only), bits 26:21 an
        // LOD bias in eighths, 63 as none; the level is also capped at the chain's last
        let mx = t0 >> 17 & 15;
        let top = t0 >> 21 & 0x3f;
        if top == 0 {
            return level0(mag);
        }
        if mx == 0 || mx == 15 {
            if min == mag {
                return level0(mag);
            }
            if self.lambda(lod)?.0 <= 0.0 {
                return level0(mag);
            }
            if mx == 15 && top == 0x3f {
                // texture-mipmaps-mip-minfilter case 14: no mipmaps (E276: 15), level 0 minified
                return level0(min);
            }
            return open(format!("level 0 minified under T0 0x{t0:08x}"));
        }
        let (l0, exact) = self.lambda(lod)?;
        let l = l0 + (top as f64 - 63.0) / 8.0;
        if l <= 0.0 {
            return level0(mag);
        }
        if mag && !min && l <= 0.5 {
            return open("magnification linear, minification point, a LOD in (0, 0.5]");
        }
        // p1132 tx-shapes (E562) and E1052: both sides halve down to 1, so the chain ends at the longer side's log2
        let last = self.w.trailing_zeros().max(self.h.trailing_zeros()).min(mx);
        if one_d && self.h != 1 {
            // E1052: smp1d on 64 x 1 reads chain A (both sides halve to 1) like smp2d
            return open("mipmaps of a 1D texture taller than one texel (not run)");
        }
        let u16_chain = self.format == 9 && CHAIN16_SIZES.contains(&(self.w, self.h));
        if self.w != self.h && !CHAIN_SIZES.contains(&(self.w, self.h)) && !u16_chain {
            return open(format!("mipmaps of a non-square {}x{} texture (not run)", self.w, self.h));
        }
        // a fractional LOD from gradients: E721 fitted its fraction (truncated to 1/64) with residuals
        if !exact && l < last as f64 {
            return open("a LOD from gradients that are not a power of two");
        }
        let l = l.min(last as f64);
        let (lo, f) = (l.floor() as u32, (l - l.floor()) * 64.0);
        let levels = if t0 >> 9 & 1 == 0 {
            if f > 31.0 && f < 32.0 {
                return open("a LOD fraction just under a half");
            }
            vec![(lo + (f >= 32.0) as u32, 64)]
        } else if f == 0.0 {
            vec![(lo, 64)]
        } else if f.fract() != 0.0 && !self.srgb {
            return open("a blend at a LOD fraction other than 1/64");
        } else if f.floor() == 0.0 {
            // E1038 (sRGB, LOD 1.2): the fraction in 64ths floored
            vec![(lo, 64)]
        } else if !self.colour() && self.format != 9 {
            return open(format!("a blend of levels of format {}", self.format));
        } else {
            // E1038: an sRGB blend floors the fraction (LOD 1.2 read f = 12, not 13)
            let f = f.floor() as u32;
            vec![(lo, 64 - f), (lo + 1, f)]
        };
        if levels.iter().any(|&(l, _)| l > 0)
            && self.bytes()? != 4
            && !(self.format == 9 && CHAIN16_SIZES.contains(&(self.w, self.h)))
        {
            return open("mip levels of a format other than 32 bits (u16 ran at 32 x 16 and 16 x 64, E1052)");
        }
        Ok((levels, min))
    }

    /// The LOD (E041) and whether it is exact: smp2dgrad's is log2 of the
    /// larger footprint in texels (texture-mipmaps-mip-grad, du/dx against dv/dy), measured
    /// at powers of two and without du/dy or dv/dx.
    fn lambda(&self, lod: &Lod) -> Result<(f64, bool), Fail> {
        Ok(match *lod {
            Lod::Flat => (f64::NEG_INFINITY, true),
            Lod::Value(x) if x.is_nan() => return open("a NaN LOD"),
            Lod::Value(x) => (x as f64, true),
            Lod::Grad([dudx, dvdx, dudy, dvdy]) => {
                // E721: with independent operands the footprint is, to within 0.1%, the larger
                // Euclidean length of (op0, op2) and (op1, op3) scaled by the level size, fitted with
                // residuals of 19 to 56 pixels on 4 of 8 held-out jobs: no exact rule, refused
                if dvdx != 0.0 || dudy != 0.0 {
                    return open("gradients off the diagonal");
                }
                if !dudx.is_finite() || !dvdy.is_finite() || dudx < 0.0 || dvdy < 0.0 {
                    return open("negative or not finite gradients");
                }
                let rho = (dudx as f64 * self.w as f64).max(dvdy as f64 * self.h as f64);
                let l = rho.log2();
                (l, rho == 0.0 || l.fract() == 0.0)
            }
            Lod::Open(why) => return open(why),
        })
    }

    /// The row of a point sample.
    fn row_of(&self, v: f64, one_d: bool) -> i64 {
        if one_d { 0 } else { (v * self.h as f64).floor() as i64 }
    }

    /// The corner texel of a bilinear sample and the fractions of a texel past it in 1/64,
    /// truncated per axis (texture-sampler-smp-bilinear: finer weights miss the landed vectors).
    fn corner(&self, u: f64, v: f64, one_d: bool) -> ((i64, i64), (u32, u32)) {
        let (x, y) = (u * self.w as f64 - 0.5, v * self.h as f64 - 0.5);
        let (x0, y0) = (x.floor(), y.floor());
        let fx = ((x - x0) * 64.0).floor() as u32;
        let fy = if one_d { 0 } else { ((y - y0) * 64.0).floor() as u32 };
        ((x0 as i64, if one_d { 0 } else { y0 as i64 }), (fx, fy))
    }

    /// The four texels of a bilinear sample and their weights in 1/4096 (the products of the
    /// fractions of `corner`), as `.pcf` weighs them.
    fn quad(&self, u: f64, v: f64, one_d: bool, load: &mut Load) -> Result<([u32; 4], [u32; 4]), Fail> {
        let ((x0, y0), (fx, fy)) = self.corner(u, v, one_d);
        let mut t = [0u32; 4];
        for (k, (dx, dy)) in [(0, 0), (1, 0), (0, 1), (1, 1)].into_iter().enumerate() {
            t[k] = self.fetch(x0 + dx, y0 + dy, load)?;
        }
        Ok((t, [(64 - fx) * (64 - fy), fx * (64 - fy), (64 - fx) * fy, fx * fy]))
    }

    /// A bilinear sample of an sRGB texture's first register (E982): bytes 0 and 1 of the four
    /// texels decoded to halves (E723), each filtered by `srgb_stage` on x on both rows and then
    /// on y, with `corner`'s 1/64 weights (E723's two fills and r9-x's rows were on that grid).
    fn srgb_bilinear(&self, u: f64, v: f64, one_d: bool, load: &mut Load) -> Result<u32, Fail> {
        let ((x0, y0), (fx, fy)) = self.corner(u, v, one_d);
        let mut t = [0u32; 4];
        for (k, (dx, dy)) in [(0, 0), (1, 0), (0, 1), (1, 1)].into_iter().enumerate() {
            t[k] = self.fetch(x0 + dx, y0 + dy, load)?;
        }
        let mut out = 0;
        for c in 0..2 {
            let h = |k: usize| srgb_half(t[k] >> (8 * c) & 0xff);
            let (top, bottom) = (srgb_stage(h(0), h(1), fx), srgb_stage(h(2), h(3), fx));
            out |= srgb_stage(top, bottom, fy) << (16 * c);
        }
        Ok(out)
    }

    /// A point or bilinear sample, and whether no channel rounded.
    fn filtered(
        &self,
        u: f64,
        v: f64,
        bilinear: bool,
        one_d: bool,
        load: &mut Load,
    ) -> Result<(u32, bool), Fail> {
        if !bilinear {
            let raw = self.fetch((u * self.w as f64).floor() as i64, self.row_of(v, one_d), load)?;
            return Ok((if self.colour() { self.colour_texel(raw)? } else { self.plain_texel(raw)? }, true));
        }
        if !self.colour() {
            return open(format!("bilinear filtering of format {}", self.format));
        }
        let ((x0, y0), (fx, fy)) = self.corner(u, v, one_d);
        let mut t = [0u32; 4];
        for (k, (dx, dy)) in [(0, 0), (1, 0), (0, 1), (1, 1)].into_iter().enumerate() {
            t[k] = self.colour_texel(self.fetch(x0 + dx, y0 + dy, load)?)?;
        }
        // E720 (8 of 8 held-out jobs, the joint form 0 of 8): each 8-bit channel is filtered in
        // two stages, x on both rows and then y, each (a (64 - f) + b f + 32) >> 6; E733: this
        // form replays E720's 8 vectors, every other vector's outcome unchanged. The jobs'
        // fractions were on the 1/64 grid; that the weights truncate to it rests on the landed
        // vectors (finer weights miss 8 of 21) and the 11.32 jobs, not on E720.
        let stage = |a: u32, b: u32, f: u32| (a * (64 - f) + b * f + 32) >> 6;
        let (mut out, mut exact) = (0, true);
        for c in 0..4 {
            let at = |k: usize| t[k] >> (8 * c) & 0xff;
            let (top, bottom) = (stage(at(0), at(1), fx), stage(at(2), at(3), fx));
            out |= stage(top, bottom, fy) << (8 * c);
            // a stage that rounds is the hardware's own: the exact value is not what it gives
            exact &= (at(0) * (64 - fx) + at(1) * fx) % 64 == 0
                && (at(2) * (64 - fx) + at(3) * fx) % 64 == 0
                && (top * (64 - fy) + bottom * fy) % 64 == 0;
        }
        Ok((out, exact))
    }

    /// Bytes per texel (texture-sampler-smp-formats).
    fn bytes(&self) -> Result<u32, Fail> {
        Ok(match self.format {
            0 | 1 => 1,
            2..=11 | 20 => 2,
            12..=19 | 21 | 22 | 30 | 31 => 4,
            // texture-sampler-smp-formats-other recorded four texels of each: at (15, 15)
            // 23-26 read 0xFFA50000, colour 0xD000 as RGB555 (PVRTC's colour
            // B?); 27 is ETC1 by the captures; 28 and 29 convert
            // through colour-space set 0 (E037, E040), whose contents the
            // vector does not record (BT.601's words miss by one or two)
            f @ 23..=27 => {
                return open(format!("texture format {f}, compressed: four texels fix no decoder"));
            }
            // 28 and 29 (YUV): opaque black with the colour-space set not loaded (E037, E040,
            // E568); with it loaded (E037) the conversion is not modelled. Machine::smp lets
            // them through only where the vector says the set is unloaded (init.job.pokes).
            28 | 29 => 2,
            f => return open(format!("texture format {f}")),
        })
    }

    /// The formats returned as B8G8R8A8 channels.
    fn colour(&self) -> bool {
        matches!(self.format, 2..=5 | 12 | 13)
    }

    /// Texel (x, y) of an ETC1 texture (format 27, E724: 6 of 6 held-out fills exact) as B8G8R8A8,
    /// alpha 0xff: the 4 x 4 blocks of two dwords (the high word first) in the Morton order of
    /// the block grid with y in the low bit, the longer side's extra bits above; the texel at
    /// (x, y) of a block is bit x * 4 + y of the low word's halves, decoded as ETC1 (the
    /// individual and differential modes, the flip bit and the modifier tables).
    fn etc1(&self, x: i64, y: i64, load: &mut Load) -> Result<u32, Fail> {
        let wrap = |t: i64, n: u32| t.rem_euclid(n as i64) as u32;
        let (x, y) = (wrap(x, self.w), wrap(y, self.h));
        let (nbx, nby) = (self.w / 4, self.h / 4);
        let (bx, by) = (x / 4, y / 4);
        let common = nbx.trailing_zeros().min(nby.trailing_zeros());
        let mut i = 0;
        for b in 0..common {
            i |= (by >> b & 1) << (2 * b) | (bx >> b & 1) << (2 * b + 1);
        }
        i |= (if nbx > nby { bx } else { by }) >> common << (2 * common);
        let a = self.base.wrapping_add(8 * i);
        let hi = load(a).map_err(Fail::Load)?;
        let lo = load(a.wrapping_add(4)).map_err(Fail::Load)?;
        let [r, g, b] = etc1_texel(hi, lo, x & 3, y & 3);
        Ok(0xff00_0000 | r << 16 | g << 8 | b)
    }

    /// Texel (x, y) addressed by the modes (texture-sampler-smp-address): a stride texture
    /// clamps to the edge; a twiddled one repeats (0), mirrors (1), clamps
    /// (2) or mirrors once (3). Modes 4 to 7 on v repeat (4, 5) and clamp (6, 7) (E565, held out
    /// at a pitch of one texel by E932); on u they read the texel the v rule names moved by an
    /// offset that grows with the size, 116, 180 and 308 dwords at 8, 16 and 32 (E932 post hoc,
    /// E957: the same in modes 4 and 6, whatever T3 or the v mode; 8 N + 52 fitted, not held
    /// out; E983: 308 on E565's 32 x 8 too, SEMI; E1000: 8 max(W, H) + 52 on W != H, every frozen
    /// single-side rival failing a held-out shape, post hoc), and past the texture mode 5 reads
    /// 5 max(W, H) + 52 + t left and 6 max(W, H) + 52 + t right (E983, E1000, post hoc), above and
    /// below it 7 M + 52 + s and 4 M + 52 + s and a corner dword whose base moves with the shape
    /// (E1017, post hoc). E1026 held out 8 max(W, H) + 52 texels on seven shapes of both
    /// orientations in modes 4, 6 and 7 and on a 16-bit format: on u, modes 4 and 5 wrap as v's
    /// 4 (repeat), 6 and 7 clamp, and the index moves by that many texels; mode 5 inside the
    /// texture alike. Mode 5 past the texture, 32-bit texels, M = max(W, H), s and t the texel's
    /// column and row: left 5 M + 52 + t, right 6 M + 52 + t, with v in mode 5 above 7 M + 52 + s
    /// and below 4 M + 52 + s, and the corners 4 log2 M plus 0 (above left), 1 (above right), 2
    /// (below left), 3 (below right) texels past the base (E1026 the sides at two shapes; E1039
    /// held out every region at 8 x 8, 32 x 32, 128 x 32, 32 x 128, 128 x 128 and 256 x 32, the
    /// corner base E1026's post hoc 4 log2 M against five rivals).
    fn fetch(&self, x: i64, y: i64, load: &mut Load) -> Result<u32, Fail> {
        if self.raster && self.address[0] == 4 && self.offset == [0, 0] && self.shift == 0 {
            // E1039 (fitted), E1055 (the form held out on ten rows, the 16 x 16 map's wrap on a
            // held-out u range, 32 x 32 post hoc): types 1, 3 and 4 with u mode 4 read the dword
            // N + (x mod W) whatever the row, each byte halved, rounded up; N = 676 at 16
            // and 1300 at 32, type 4 at 16 x 16 660 (measured_r4 admits these sizes only; the fit
            // 39 W + 52 failed at 8 x 8, 64 x 64 and 64 x 16, E1065). The halves leave N's byte 1
            // one of two values: N - 256 (16) and N + 256 (32) fit alike
            // E1065: not a formula in W: at 8 x 8, 64 x 64 and 64 x 16 it failed (measured_r4
            // refuses those sizes); the two sizes admitted are their measured names
            let n = match (self.blocks, self.w) {
                (true, 16) => 660,
                (_, 16) => 676,
                (_, 32) => 1300,
                (_, w) => return open(format!("the name of u mode 4 at width {w} (E1065: the fit failed)")),
            };
            let i = n + x.rem_euclid(self.w as i64) as u32;
            let d = load(self.base.wrapping_add(4 * i)).map_err(Fail::Load)?;
            return Ok((0..4).fold(0, |o, k| o | ((d >> (8 * k) & 0xff) + 1) >> 1 << (8 * k)));
        }
        let mut umode_extra = 0u32;
        if self.row.is_none() && (4..8).contains(&self.address[0]) {
            let (ux, vy) = (self.offset[0] + x, self.offset[1] + y);
            let past_u = self.address[0] == 5 && !(0..self.w as i64).contains(&ux);
            let past_v = self.address[0] == 5 && self.address[1] == 5 && !(0..self.h as i64).contains(&vy);
            if past_u || past_v {
                if self.bytes()? != 4 || self.extra != 0 || self.shift != 0 {
                    return open(
                        "address mode 5 past the texture at a format other than 32 bits, with T3's \
                                 bit 14 or scale (not run; Q177)",
                    );
                }
                let m = self.w.max(self.h) as i64;
                let t = if past_v { vy } else { vy.rem_euclid(self.h as i64) };
                let i = match (past_u, past_v) {
                    (true, false) => (if ux < 0 { 5 } else { 6 }) * m + 52 + t,
                    (false, true) => (if vy < 0 { 7 } else { 4 }) * m + 52 + ux,
                    _ => 4 * m.trailing_zeros() as i64 + 2 * (vy >= 0) as i64 + (ux >= 0) as i64,
                };
                return load(self.base.wrapping_add(4 * i as u32) & !3).map_err(Fail::Load);
            }
            umode_extra = 8 * self.w.max(self.h) + 52;
        }
        let axis = |t: i64, n: u32, mode: u32, v: bool| -> Result<u32, Fail> {
            let n = n as i64;
            let clamp = |t: i64| t.clamp(0, n - 1);
            Ok(if self.row.is_some() && !self.raster {
                clamp(t)
            } else {
                match mode {
                    0 => t.rem_euclid(n),
                    1 => {
                        let m = t.rem_euclid(2 * n);
                        if m >= n { 2 * n - 1 - m } else { m }
                    }
                    2 => clamp(t),
                    3 => clamp(if t < 0 { -t - 1 } else { t }),
                    4 | 5 if v || self.row.is_none() => t.rem_euclid(n),
                    6 | 7 if v || self.row.is_none() => clamp(t),
                    m => {
                        return open(format!(
                            "address mode {m} on u of a raster type (E1055: at 16 x 16 modes 6 and 7 read mode 4's \
                             last column on every pixel and mode 5 one other dword, halved, post hoc; Q177)"
                        ));
                    }
                }
            } as u32)
        };
        let (x, y) = (self.offset[0] + x, self.offset[1] + y);
        let (x, y) = (axis(x, self.w, self.address[0], false)?, axis(y, self.h, self.address[1], true)?);
        let bytes = self.bytes()?;
        let off = match self.row {
            // E941: block (y div 32) ceil(w / 32) + (x div 32) of 1024 dwords, raster inside
            Some(_) if self.blocks => {
                ((y / 32 * self.w.div_ceil(32) + x / 32) * 1024 + y % 32 * 32 + x % 32) * 4
            }
            // E942: texel t = y w + x is bit 0 of dword floor(t / 8)
            Some(_) if self.bits => (y * self.w + x) / 8 * 4,
            Some(row) => (y * row + x * bytes) << self.shift,
            None => morton(x, y, self.w, self.h) * bytes,
        };
        let a = self
            .base
            .wrapping_add(off)
            .wrapping_add(self.extra.wrapping_add(umode_extra).wrapping_mul(bytes));
        let dw = load(a & !3).map_err(Fail::Load)?;
        if self.bits {
            return Ok(if dw & 1 != 0 { 0x0000_ffff } else { 0 });
        }
        Ok(match bytes {
            4 => dw,
            // format 20: the pair's dword, the texel's own byte (0 or 2) first
            _ if self.format == 20 => dw >> (8 * (a & 2)) & 0xff | (dw >> 8 & 0xff) << 8 | (dw >> 24) << 16,
            _ => dw >> (8 * (a & 3)) & ((1 << (8 * bytes)) - 1),
        })
    }

    /// A texel of a colour format as B8G8R8A8: the 16-bit ones expand each
    /// field by repeating its bits, alpha 0xff without one; 13 is R8G8B8A8.
    fn colour_texel(&self, t: u32) -> Result<u32, Fail> {
        let f = |v: u32, lo: u32, n: u32| {
            let x = v >> lo & ((1 << n) - 1);
            let mut out = 0;
            let mut have = 0;
            while have < 8 {
                out = out << n | x;
                have += n;
            }
            out >> (have - 8)
        };
        let bgra = |b: u32, g: u32, r: u32, a: u32| b | g << 8 | r << 16 | a << 24;
        Ok(match self.format {
            2 => bgra(f(t, 0, 4), f(t, 4, 4), f(t, 8, 4), f(t, 12, 4)),
            3 => bgra(f(t, 0, 2), f(t, 2, 3), f(t, 5, 3), f(t, 8, 8)),
            4 => bgra(f(t, 0, 5), f(t, 5, 5), f(t, 10, 5), f(t, 15, 1)),
            5 => bgra(f(t, 0, 5), f(t, 5, 6), f(t, 11, 5), 0xff),
            12 => t,
            13 => t & 0xff00_ff00 | (t & 0xff) << 16 | (t >> 16 & 0xff),
            _ => unreachable!(),
        })
    }

    /// .pcf (texture-sampler-smp-pcf): texel OP reference by the compare mode (never, <,
    /// ==, <=, >, >=, !=, always) on an f32 texture (format 18) or a u16 one
    /// (9, read as texel / 65535), giving 1.0 or 0xffff when it holds, else
    /// 0. Filtered, the results average: measured where they agree and for
    /// one of two texels at half weight.
    fn pcf(&self, t: [u32; 4], w: [u32; 4], r: f32, mode: u32) -> Result<u32, Fail> {
        let value = |t: u32| -> Result<f64, Fail> {
            Ok(match self.format {
                18 if f32::from_bits(t).is_nan() => return open("a NaN texel with .pcf"),
                18 => f32::from_bits(t) as f64,
                9 => t as f64 / 65535.0,
                f => return open(format!(".pcf on format {f}")),
            })
        };
        let r = r as f64;
        let mut held = 0;
        for k in 0..4 {
            let x = value(t[k])?;
            let ok = match mode {
                0 => false,
                1 => x < r,
                2 => x == r,
                3 => x <= r,
                4 => x > r,
                5 => x >= r,
                6 => x != r,
                _ => true,
            };
            held += ok as u32 * w[k];
        }
        let one = if self.format == 18 { 0x3f80_0000 } else { 0xffff };
        Ok(match held {
            0 => 0,
            4096 => one,
            2048 if w.iter().filter(|&&w| w == 2048).count() == 2 => {
                if self.format == 18 {
                    0x3f00_0000
                } else {
                    0x8000
                }
            }
            _ => return open("filtered .pcf at weights other than one of two halves"),
        })
    }

    /// A texel of the other formats, as stored (texture-sampler-smp-formats): 19 clears the
    /// sign bit, 21 the top byte, 30 sets it. texture-sampler-smp-formats-other: 6 is
    /// L6V5U5, the six-bit field 15:10 in B, the signed fields 9:5 in G and
    /// 4:0 in R, each its sign then its four bits below it repeated (2 is
    /// 0x11, -15 0x88), alpha 0xff; 20 the texel's own byte in R, its pair's
    /// bytes 1 and 3 in G and B (fetch), alpha 0xff, unconverted.
    fn plain_texel(&self, t: u32) -> Result<u32, Fail> {
        let s5 = |v: u32| (v & 0x10) << 3 | (v & 15) << 3 | (v & 15) >> 1;
        Ok(match self.format {
            6 => {
                let l = t >> 10 & 0x3f;
                0xff00_0000 | s5(t) << 16 | s5(t >> 5) << 8 | (l << 2 | l >> 4)
            }
            19 => t & 0x7fff_ffff,
            20 => 0xff00_0000 | (t & 0xff) << 16 | (t >> 8 & 0xff) << 8 | t >> 16,
            21 => t & 0x00ff_ffff,
            30 => t | 0xff00_0000,
            28 | 29 => 0xff00_0000,
            _ => t,
        })
    }
}

/// Texel (x, y) of an ETC1 block (the Khronos ETC1 decode; E724): R, G and B.
fn etc1_texel(hi: u32, lo: u32, x: u32, y: u32) -> [u32; 3] {
    let (diff, flip) = (hi >> 1 & 1 != 0, hi & 1 != 0);
    let (c1, c2) = if diff {
        let base = |sh: u32| hi >> sh & 31;
        let delta = |sh: u32| ((hi >> sh & 7) as i32 ^ 4) - 4;
        let e = |v: u32| v << 3 | v >> 2;
        let one = [27, 19, 11].map(base);
        // the second colour stays inside 0 to 31 for every valid block; clamp as the decode does
        let two = [(27, 24), (19, 16), (11, 8)].map(|(b, d)| (base(b) as i32 + delta(d)).clamp(0, 31) as u32);
        (one.map(e), two.map(e))
    } else {
        let n = |sh: u32| (hi >> sh & 15) * 0x11;
        ([28, 20, 12].map(n), [24, 16, 8].map(n))
    };
    const TABLE: [[i32; 2]; 8] =
        [[2, 8], [5, 17], [9, 29], [13, 42], [18, 60], [24, 80], [33, 106], [47, 183]];
    let i = x * 4 + y;
    let first = if flip { y < 2 } else { x < 2 };
    let (t, base) =
        if first { (TABLE[(hi >> 5 & 7) as usize], c1) } else { (TABLE[(hi >> 2 & 7) as usize], c2) };
    let m = match (lo >> (16 + i) & 1, lo >> i & 1) {
        (0, 0) => t[0],
        (0, _) => t[1],
        (_, 0) => -t[0],
        _ => -t[1],
    };
    base.map(|c| (c as i32 + m).clamp(0, 255) as u32)
}

/// Whether an smp3d (the form without a LOD operand) may be read as the smp2d of the same state
/// words: it ran (p1132 tx-types, tx-types-risky; E567) on TEXTYPE 0, 6 and 7 only, format 12,
/// point filters and one level, a 16x16 twiddled texture and a 64x32 stride one, with the T0 and T3
/// words of those jobs (T2 varied nowhere). Its third coordinate acts on TEXTYPE 2 (E567), which
/// the rule refuses with the rest. With .pcf or an SRD mode it did not run.
pub fn smp3d_as_2d(state: [u32; 4], pcf_or_srd: bool) -> Result<(), String> {
    let [t0, t1, _, t3] = state;
    let ty = t1 >> 29;
    let no = |what: String| {
        Err(format!(
            "smp3d {what}: only the point-sampled 16x16 twiddled and 64x32 stride textures of E567 ran"
        ))
    };
    if pcf_or_srd {
        return no("with .pcf or an SRD mode".into());
    }
    if !matches!(ty, 0 | 6 | 7) {
        return no(format!("on TEXTYPE {ty}"));
    }
    let (w, h) = ((t1 >> 12 & 0xfff) + 1, (t1 & 0xfff) + 1);
    let (size, t0_ran, t3_ran) =
        if ty == 6 { ((64, 32), 0x000e_0e00, 0xa080_0000) } else { ((16, 16), 0x07fe_0000, 0x0080_0800) };
    if (w, h) != size {
        return no(format!("on a {w}x{h} texture of TEXTYPE {ty}"));
    }
    if t1 >> 24 & 31 != 12 {
        return no(format!("on format {}", t1 >> 24 & 31));
    }
    if t0 != t0_ran || t3 != t3_ran {
        return no(format!("with T0 0x{t0:08x} and T3 0x{t3:08x}"));
    }
    Ok(())
}

/// The sizes of 32-bit twiddled textures, with a side above 16, that p1132 ran (E561 tx-twiddle,
/// E562 tx-shapes) and r13-tex's 32 x 64 (E1026: three rows, every pixel the tile law's index plus
/// the u-mode offset): the tiles of 16 x 16 and their raster order are measured there only.
const TILE_SIZES: [(u32, u32); 19] = [
    // E1039: 256 x 32 in mode 5 (the inside the tile law's index plus 8 M + 52, every pixel)
    (256, 32),
    // E1052: a side of 1 at level 0 (1 x 32, 32 x 1 and, read 1D, 64 x 1), every texel its index
    (1, 32),
    (32, 1),
    (64, 1),
    (32, 64),
    (32, 32),
    (64, 32),
    (64, 16),
    (64, 64),
    (128, 16),
    (128, 32),
    (32, 128),
    (128, 128),
    (16, 64),
    (8, 128),
    (32, 16),
    (16, 32),
    (64, 4),
    (8, 64),
];

/// The non-square sizes whose mip chain p1132 ran (E562 tx-shapes, tx-fields) and r15-tex held out
/// (E1052: a side of 1, 64 x 1 read 1D, 64 x 32 and 256 x 32; u16 also at 16 x 64, CHAIN16_SIZES).
const CHAIN_SIZES: [(u32, u32); 10] =
    [(32, 16), (128, 16), (16, 32), (64, 4), (8, 64), (1, 32), (32, 1), (64, 1), (64, 32), (256, 32)];
/// E1052: the sizes a u16 (format 9) twiddled chain ran at, its levels packed in texels (the short
/// side at most 16, so the tile law is the plain interleave).
const CHAIN16_SIZES: [(u32, u32); 2] = [(32, 16), (16, 64)];

fn tile_law_ran(w: u32, h: u32) -> bool {
    TILE_SIZES.contains(&(w, h))
}

/// The twiddled index of (x, y) (texture-sampler-smp-twiddled, p1132 tx-twiddle): a tile of up to
/// 16 x 16 texels (the whole texture when it is smaller) is interleaved, y in bit 0, x in bit 1,
/// and so on, the longer side's extra bits above; the tiles follow in raster order, x first.
fn morton(x: u32, y: u32, w: u32, h: u32) -> u32 {
    let (tw, th) = (w.min(16), h.min(16));
    let (bw, bh) = (tw.trailing_zeros(), th.trailing_zeros());
    let (cx, cy) = (x & (tw - 1), y & (th - 1));
    let common = bw.min(bh);
    let mut i = 0;
    for b in 0..common {
        i |= (cy >> b & 1) << (2 * b) | (cx >> b & 1) << (2 * b + 1);
    }
    let rest = if bw > bh { cx } else { cy } >> common;
    i |= rest << (2 * common);
    i + ((x / tw) + (y / th) * (w / tw)) * tw * th
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A texture whose dwords count up from 0x100 at 0x1000.
    fn counting(a: u32) -> Result<u32, crate::Error> {
        Ok(0x100 + (a - 0x1000) / 4)
    }

    /// T0-T3 of a texture at 0x1000: `ty` 6 (stride, `stride` dwords) or 0.
    fn state(ty: u32, fmt: u32, w: u32, h: u32, stride: u32, t0: u32, t3: u32) -> [u32; 4] {
        let s = stride - 1;
        let t0 = t0 | (s & 7) << 9 | (s >> 3) << 17;
        [t0, ty << 29 | fmt << 24 | (w - 1) << 12 | (h - 1), 0x1000, t3]
    }

    fn at(st: [u32; 4], u: f32, v: f32) -> Result<Vec<u32>, Fail> {
        sample(
            &Sample { state: st, u, v, one_d: false, srd: Srd::None, pcf: None, lod: Lod::Flat },
            &mut counting,
        )
    }

    #[test]
    fn point_sampling_picks_and_clamps() {
        let st = state(6, 12, 4, 4, 4, 0, 0);
        assert_eq!(at(st, 0.0, 0.0), Ok(vec![0x100]));
        assert_eq!(at(st, 0.6, 0.3), Ok(vec![0x100 + 4 + 2]));
        // outside [0, 1) clamps to the edge
        assert_eq!(at(st, 1.5, -0.2), Ok(vec![0x103]));
        assert_eq!(
            sample(
                &Sample { state: st, u: 0.6, v: 0.9, one_d: true, srd: Srd::None, pcf: None, lod: Lod::Flat },
                &mut counting
            ),
            Ok(vec![0x102])
        );
    }

    #[test]
    fn twiddled_textures_interleave_y_then_x() {
        let st = state(0, 12, 4, 4, 1, 2 << 6 | 2 << 3, 0);
        // (x, y) = (1, 0) is index 2, (0, 1) index 1, (3, 3) 15
        assert_eq!(at(st, 0.3, 0.0), Ok(vec![0x102]));
        assert_eq!(at(st, 0.0, 0.3), Ok(vec![0x101]));
        assert_eq!(at(st, 0.9, 0.9), Ok(vec![0x10f]));
        assert_eq!(morton(5, 1, 8, 2), 0b1011);
    }

    #[test]
    fn twiddled_address_modes() {
        let x = |mode: u32, u: f32| at(state(0, 12, 4, 4, 1, mode << 6 | 2 << 3, 0), u, 0.0);
        // on row 0, texels 1, 2, 3 are indices 2, 8, 10 (y in bit 0)
        assert_eq!(x(0, 1.3), Ok(vec![0x102]), "repeat");
        assert_eq!(x(1, 1.3), Ok(vec![0x108]), "mirror: 5 is 2");
        assert_eq!(x(2, 1.3), Ok(vec![0x10a]), "clamp");
        assert_eq!(x(3, -0.3), Ok(vec![0x102]), "mirror once: |-1.2| is 1");
        // mode 4: repeat, then 8 max(W, H) + 52 = 84 texels on (E1026)
        assert_eq!(x(4, 1.3), Ok(vec![0x102 + 84]), "mode 4 on u");
    }

    #[test]
    fn modes_4_to_7_on_v_repeat_and_clamp_and_on_u_stop() {
        // E932: on v, 4 and 5 repeat and 6 and 7 clamp (held out at a pitch of one texel); on
        // column 0 texels 1, 2, 3 are indices 1, 4, 5 (y in bit 0)
        let y = |mode: u32, v: f32| at(state(0, 12, 4, 4, 1, mode << 3, 0), 0.0, v);
        assert_eq!(y(4, 1.3), Ok(vec![0x101]), "repeat: 5 is 1");
        assert_eq!(y(5, 1.3), Ok(vec![0x101]), "repeat");
        assert_eq!(y(6, 1.3), Ok(vec![0x105]), "clamp: 5 is 3");
        assert_eq!(y(7, -0.3), Ok(vec![0x100]), "clamp: -2 is 0");
        // mode 5 on u past the texture at a 16-bit format: no model (Q177)
        let e = format!("{:?}", at(state(0, 9, 4, 4, 1, 5 << 6, 0), 1.3, 0.0).unwrap_err());
        assert!(e.contains("Q177"), "{e}");
    }

    #[test]
    fn mode_5_past_the_texture_reads_its_regions() {
        // E1039 (render/closing-r14-tex addr5, out/20261114-054258): u and v in mode 5 on 32-bit
        // twiddled textures, one kept pixel a region a shape: (W, H, s, t, the texel read past
        // the base); the corners 4 log2 max(W, H) + 0 to 3, the sides 5 M / 6 M + 52 + t, above
        // and below 7 M / 4 M + 52 + s, inside the index + 8 M + 52 (fold/sim_points.out)
        let kept: [(u32, u32, i32, i32, u32); 54] = [
            (8, 8, 0, -12, 108),
            (8, 8, 0, 8, 84),
            (8, 8, 0, 0, 116),
            (8, 8, -28, -12, 12),
            (8, 8, -28, 8, 14),
            (8, 8, -28, 0, 92),
            (8, 8, 8, -12, 13),
            (8, 8, 8, 8, 15),
            (8, 8, 8, 0, 100),
            (32, 32, 0, -16, 276),
            (32, 32, 0, 32, 180),
            (32, 32, 0, 0, 308),
            (32, 32, -16, -16, 20),
            (32, 32, -16, 32, 22),
            (32, 32, -16, 0, 212),
            (32, 32, 32, -16, 21),
            (32, 32, 32, 32, 23),
            (32, 32, 32, 0, 244),
            (128, 32, 0, -16, 948),
            (128, 32, 0, 32, 564),
            (128, 32, 0, 0, 1076),
            (128, 32, -64, -16, 28),
            (128, 32, -64, 32, 30),
            (128, 32, -64, 0, 692),
            (128, 32, 128, -16, 29),
            (128, 32, 128, 32, 31),
            (128, 32, 128, 0, 820),
            (32, 128, 0, -64, 948),
            (32, 128, 0, 128, 564),
            (32, 128, 0, 0, 1076),
            (32, 128, -16, -64, 28),
            (32, 128, -16, 128, 30),
            (32, 128, -16, 0, 692),
            (32, 128, 32, -64, 29),
            (32, 128, 32, 128, 31),
            (32, 128, 32, 0, 820),
            (128, 128, 0, -64, 948),
            (128, 128, 0, 128, 564),
            (128, 128, 0, 0, 1076),
            (128, 128, -64, -64, 28),
            (128, 128, -64, 128, 30),
            (128, 128, -64, 0, 692),
            (128, 128, 128, -64, 29),
            (128, 128, 128, 128, 31),
            (128, 128, 128, 0, 820),
            (256, 32, 0, -16, 1844),
            (256, 32, 0, 32, 1076),
            (256, 32, 0, 0, 2100),
            (256, 32, -128, -16, 32),
            (256, 32, -128, 32, 34),
            (256, 32, -128, 0, 1332),
            (256, 32, 256, -16, 33),
            (256, 32, 256, 32, 35),
            (256, 32, 256, 0, 1588),
        ];
        for (w, h, s, t, read) in kept {
            let (u, v) = ((s as f32 + 0.5) / w as f32, (t as f32 + 0.5) / h as f32);
            assert_eq!(
                at(state(0, 12, w, h, 1, 5 << 6 | 5 << 3, 0), u, v),
                Ok(vec![0x100 + read]),
                "{w}x{h} ({s}, {t})"
            );
        }
    }

    #[test]
    fn a_trilinear_srgb_sample_lerps_the_levels_on_a_15_bit_grid() {
        // E1038 (render/closing-r14-tex srgb4, out/20261114-054258): smp2dreplace on twiddled sRGB
        // chains with T0 bit 9, u = (x + 0.5) / 64, v = (y + 0.5) / 32; the 16 x 16 chain on the
        // counting fill (dword i = 0xd0000000 | i) at LOD 1.125 and 1.2 (f 12, floored), the
        // 4 x 4 dark chain (gen/srgb4.py dark_inject) at LOD 0.125; kept pixels, among them
        // where the 16-bit grid (TRI-RNTU) and the unflushed lerp part (fold/sim_points.out)
        const DARK: [u32; 21] = [
            0x0202, 0x0002, 0x0203, 0x0200, 0x0002, 0x0303, 0x0000, 0x0100, 0x0102, 0x0001, 0x0101, 0x0000,
            0x0001, 0x0100, 0x0300, 0x0100, 0x0098, 0x0074, 0x0175, 0x01bb, 0x0265,
        ];
        let kept = [
            ("srgb4-t1125", 0, 0, 0x0cf9259f),
            ("srgb4-t1125", 6, 1, 0x0cf92010),
            ("srgb4-t1125", 13, 5, 0x0cf91fd4),
            ("srgb4-t1125", 40, 15, 0x0cf92789),
            ("srgb4-t1125", 28, 23, 0x0cf924fe),
            ("srgb4-t1125", 63, 31, 0x0cf92790),
            ("srgb4-t12", 0, 0, 0x0cf92660),
            ("srgb4-t12", 6, 1, 0x0cf921ce),
            ("srgb4-t12", 13, 5, 0x0cf92190),
            ("srgb4-t12", 40, 15, 0x0cf92822),
            ("srgb4-t12", 28, 23, 0x0cf925d4),
            ("srgb4-t12", 63, 31, 0x0cf9281c),
            ("srgb4-tdark", 0, 0, 0x0ff928a4),
            ("srgb4-tdark", 6, 1, 0x10db286d),
            ("srgb4-tdark", 13, 5, 0x0fa128aa),
            ("srgb4-tdark", 40, 15, 0x000028f9),
            ("srgb4-tdark", 28, 23, 0x084b28ca),
            ("srgb4-tdark", 63, 31, 0x0fdb28c5),
            ("srgb4-t1125", 12, 1, 0x0cf92047),  // parts TRI-RNTU
            ("srgb4-t1125", 16, 3, 0x0cf92034),  // parts TRI-RNTU
            ("srgb4-tdark", 2, 0, 0x105c2892),   // parts TRI-RNTU
            ("srgb4-tdark", 5, 0, 0x10ea2876),   // parts TRI-RNTU
            ("srgb4-tdark", 39, 10, 0x000027e9), // parts TRI-G15-NF
            ("srgb4-tdark", 40, 10, 0x000027d9), // parts TRI-G15-NF
        ];
        for (row, x, y, want) in kept {
            let (w, lod) = match row {
                "srgb4-t1125" => (16, 1.125f32),
                "srgb4-t12" => (16, f32::from_bits(0x3f99_999a)),
                _ => (4, 0.125),
            };
            let mut mem = |a: u32| -> Result<u32, crate::Error> {
                let i = (a - 0x1000) / 4;
                Ok(if w == 4 { 0xa55a_0000 | DARK[i as usize] } else { 0xd000_0000 | i })
            };
            let st = [T0_SRGB_TRI, (w - 1) << 12 | (w - 1) | 12 << 24, 0x1000, T3_TW];
            let s = Sample {
                state: st,
                u: (x as f32 + 0.5) / 64.0,
                v: (y as f32 + 0.5) / 32.0,
                one_d: false,
                srd: Srd::None,
                pcf: None,
                lod: Lod::Value(lod),
            };
            assert_eq!(sample(&s, &mut mem), Ok(vec![want]), "{row} ({x}, {y})");
        }
    }

    #[test]
    fn u_modes_4_to_7_add_8_max_w_h_plus_52_texels() {
        // E1026 (held out: 32 x 64, 8 x 64, 128 x 32 in modes 4 and 6, 32 x 64 in mode 7, a u16
        // 32 x 64): the v rule's index of the wrapped texel plus 8 max(W, H) + 52 texels;
        // the values from E561's tile law (render/closing-r13-tex gen/addr.py)
        let t = |w: u32, h: u32, m: u32, s: i32, tt: u32| {
            let (u, v) = ((s as f32 + 0.5) / w as f32, (tt as f32 + 0.5) / h as f32);
            at(state(0, 12, w, h, 1, m << 6, 0), u, v)
        };
        assert_eq!(t(32, 64, 4, -1, 32), Ok(vec![0x100 + 2014]), "32 x 64 mode 4");
        assert_eq!(t(32, 64, 6, 40, 5), Ok(vec![0x100 + 1007]), "32 x 64 mode 6");
        assert_eq!(t(128, 32, 7, -3, 16), Ok(vec![0x100 + 3124]), "128 x 32 mode 7");
        assert_eq!(t(16, 16, 4, 17, 0), Ok(vec![0x100 + 182]), "16 x 16 mode 4 (E932's 180)");
        // mode 5 inside the texture (v mode 0): the same offset
        assert_eq!(t(16, 64, 5, 3, 40), Ok(vec![0x100 + 1150]), "16 x 64 mode 5 inside");
    }

    #[test]
    fn bilinear_truncates_the_weights_and_rounds_each_channel() {
        // between 0x...ff and 0x...0f in byte 0, two rows: fy = k/2 (truncated)
        let st = state(6, 12, 2, 2, 2, 1 << 12, 0);
        let mut mem = |a: u32| Ok(if a < 0x1008 { 0xff } else { 0x0f });
        let mut y = |k: f32| {
            sample(
                &Sample {
                    state: st,
                    u: 0.25,
                    v: 0.25 + k / 256.0,
                    one_d: false,
                    srd: Srd::None,
                    pcf: None,
                    lod: Lod::Flat,
                },
                &mut mem,
            )
        };
        assert_eq!(y(0.0), Ok(vec![0xff]));
        assert_eq!(y(1.0), Ok(vec![0xff]));
        assert_eq!(y(3.0), Ok(vec![251]));
        // fy = 2/64: (0xff * 62 + 0x0f * 2) * 64 / 4096 = 247.5, halves up
        assert_eq!(y(4.0), Ok(vec![248]));
    }

    /// A bilinear sample of a 2 x 2 stride texture, the four texels' byte 0 given by `texel`,
    /// at the coordinates that give the fractions (fx, fy), in 1/64 of a texel, from texel 0.
    fn bilinear_at(texel: [u32; 4], fx: f32, fy: f32) -> Result<Vec<u32>, Fail> {
        let st = state(6, 12, 2, 2, 2, 1 << 12, 0);
        let mut mem = |a: u32| Ok(texel[((a - 0x1000) / 4) as usize]);
        sample(
            &Sample {
                state: st,
                u: 0.25 + fx / 128.0,
                v: 0.25 + fy / 128.0,
                one_d: false,
                srd: Srd::None,
                pcf: None,
                lod: Lod::Flat,
            },
            &mut mem,
        )
    }

    #[test]
    fn bilinear_is_two_stage_xy_with_32_added_at_each_stage() {
        // E720: per channel (a (64 - fx) + b fx + 32) >> 6 in x on each row, then the same in y,
        // 8 of 8 held-out jobs against 0 of 8 for the joint (sum + 2048) >> 12.
        // One texel of 1 at fx = fy = 32: the joint form gives (1024 + 2048) >> 12 = 0, the
        // stages (32 + 32) >> 6 = 1 and (1 * 32 + 0 + 32) >> 6 = 1.
        assert_eq!(bilinear_at([1, 0, 0, 0], 32.0, 32.0), Ok(vec![1]));
        // texels 1 2 3 4 at fx 17, fy 45: rows (1 * 47 + 2 * 17 + 32) >> 6 = 1 and (3 * 47 +
        // 4 * 17 + 32) >> 6 = 3, then (1 * 19 + 3 * 45 + 32) >> 6 = 2; the joint form gives 3.
        assert_eq!(bilinear_at([1, 2, 3, 4], 17.0, 45.0), Ok(vec![2]));
        // where the forms agree they still do (landed smp-bilinear vectors, plan 1.3)
        assert_eq!(bilinear_at([255, 0, 0, 0], 1.0, 32.0), Ok(vec![126]));
        assert_eq!(bilinear_at([0, 255, 255, 0], 32.0, 32.0), Ok(vec![128]));
    }

    #[test]
    fn bilinear_weights_still_truncate_to_1_64() {
        // E720's jobs have fractions on the 1/64 grid only, so the weights' precision is not
        // theirs: it is the landed vectors' and the 11.32 jobs' (trunc (64 frac), finer fails).
        // fx = 63.9 / 64 weighs as 63: (255 * 63 + 32) >> 6 = 251, not 255 as 64 would give.
        assert_eq!(bilinear_at([0, 255, 0, 0], 63.9, 0.0), Ok(vec![251]));
        assert_eq!(bilinear_at([0, 255, 0, 0], 63.0, 0.0), Ok(vec![251]));
        assert_eq!(bilinear_at([0, 255, 0, 0], 0.9, 0.0), Ok(vec![0]), "0.9 / 64 weighs as 0");
    }

    #[test]
    fn colour_formats_expand_and_convert() {
        let st = |fmt: u32, t3: u32| state(6, fmt, 2, 2, 1, 0, t3);
        let one = |fmt: u32, t3: u32, texel: u32| {
            sample(
                &Sample {
                    state: st(fmt, t3),
                    u: 0.0,
                    v: 0.0,
                    one_d: false,
                    srd: Srd::None,
                    pcf: None,
                    lod: Lod::Flat,
                },
                &mut |_| Ok(texel),
            )
        };
        assert_eq!(one(5, 0, 0xf81f), Ok(vec![0xffff_00ff]), "565: R and B full, alpha 0xff");
        assert_eq!(one(2, 0, 0x1234), Ok(vec![0x1122_3344]), "4444");
        assert_eq!(one(13, 0, 0x4433_2211), Ok(vec![0x4411_2233]), "R8G8B8A8");
        assert_eq!(one(0, 0, 0x4433_2211), Ok(vec![0x11]), "a byte");
        // B, G, R, A = 1, 2, 3, 4
        let t = 0x0403_0201;
        assert_eq!(one(12, 1 << 16, t), Ok(vec![1 | 2 << 10 | 3 << 20, 4]), "c10");
        assert_eq!(one(12, 2 << 16, t), Ok(vec![0x4200 | 0x4000 << 16, 0x3c00 | 0x4400 << 16]), "f16");
        let f32s = [1.0f32, 2.0, 3.0, 4.0].map(f32::to_bits).to_vec();
        assert_eq!(one(12, 3 << 16, t), Ok(f32s), "f32");
        let norm = [1.0f32 / 255.0, 2.0 / 255.0, 3.0 / 255.0, 4.0 / 255.0].map(f32::to_bits).to_vec();
        assert_eq!(one(12, 3 << 16 | 1 << 15, t), Ok(norm), "normalized");
        assert_eq!((half(1.0), half(255.0), half(1.0 / 255.0)), (0x3c00, 0x5bf8, 0x1c04));
        assert_eq!(half(1.0 / 65535.0), 0x0100);
    }

    #[test]
    fn without_alpha_the_conversions_drop_it_or_give_one() {
        // 565 (texture-sampler-smp-convert): c10 writes one register, f32 three, f16 alpha 1.0
        let one = |t3: u32| {
            let st = state(6, 5, 2, 2, 1, 0, t3);
            sample(
                &Sample {
                    state: st,
                    u: 0.0,
                    v: 0.0,
                    one_d: false,
                    srd: Srd::None,
                    pcf: None,
                    lod: Lod::Flat,
                },
                &mut |_| Ok(0xffff),
            )
        };
        assert_eq!(one(1 << 16), Ok(vec![0xff | 0xff << 10 | 0xff << 20]));
        assert_eq!(one(2 << 16), Ok(vec![0x5bf8 | 0x5bf8 << 16, 0x5bf8 | 0x3c00 << 16]));
        assert_eq!(one(3 << 16).map(|v| v.len()), Ok(3));
    }

    #[test]
    fn the_other_formats_convert_their_channels() {
        // texture-sampler-smp-convert: u8 (0), two u8 (7, low byte first), u16 (9)
        let one = |fmt: u32, t3: u32, texel: u32| {
            let st = state(6, fmt, 2, 2, 1, 0, t3);
            sample(
                &Sample {
                    state: st,
                    u: 0.0,
                    v: 0.0,
                    one_d: false,
                    srd: Srd::None,
                    pcf: None,
                    lod: Lod::Flat,
                },
                &mut |_| Ok(texel),
            )
        };
        let f = |x: f32| x.to_bits();
        assert_eq!(one(0, 1 << 16, 0xd0), Ok(vec![0xd0]));
        assert_eq!(one(0, 2 << 16, 0xd0), Ok(vec![0x5a80]));
        assert_eq!(one(0, 3 << 16, 0xd0), Ok(vec![f(208.0)]));
        assert_eq!(one(0, 3 << 16 | 1 << 15, 0xd0), Ok(vec![0x3f50_d0d1]));
        assert_eq!(one(7, 1 << 16, 0x0451), Ok(vec![0x1051]));
        assert_eq!(one(7, 2 << 16, 0x0451), Ok(vec![0x4400_5510]));
        assert_eq!(one(7, 3 << 16, 0x0451), Ok(vec![f(81.0), f(4.0)]));
        assert_eq!(one(7, 3 << 16 | 1 << 15, 0x0451), Ok(vec![0x3ea2_a2a3, 0x3c80_8081]));
        assert_eq!(one(9, 1 << 16, 0xd000), Ok(vec![0xd0]));
        assert_eq!(one(9, 2 << 16, 0x0451), Ok(vec![0x6451]));
        assert_eq!(one(9, 3 << 16, 0xd000), Ok(vec![f(53248.0)]));
        assert_eq!(one(9, 3 << 16 | 1 << 15, 0x0451), Ok(vec![0x3c8a_208a]));
        assert!(one(1, 3 << 16, 0x80).is_err(), "s8");
        assert!(one(9, 2 << 16, 0xfff0).is_err(), "past the largest half");
    }

    #[test]
    fn pcf_compares_the_texel_with_the_reference() {
        let pcf = |fmt: u32, mode: u32, t0: u32, r: f32, texels: [u32; 2], u: f32| {
            let st = state(6, fmt, 4, 4, 4, t0, mode << 29);
            // v = 1/8: y = 0, fy = 0
            let s =
                Sample { state: st, u, v: 0.125, one_d: false, srd: Srd::None, pcf: Some(r), lod: Lod::Flat };
            sample(&s, &mut |a| Ok(if a & 4 == 0 { texels[0] } else { texels[1] }))
        };
        let f = |x: f32| [x.to_bits(); 2];
        // f32 (format 18): 1.0 when texel OP reference
        assert_eq!(pcf(18, 1, 0, 0.5, f(0.25), 0.0), Ok(vec![0x3f80_0000]), "<");
        assert_eq!(pcf(18, 4, 0, 0.5, f(0.25), 0.0), Ok(vec![0]), ">");
        assert_eq!(pcf(18, 7, 0, 0.5, f(0.25), 0.0), Ok(vec![0x3f80_0000]), "always");
        // u16 (format 9): the texel / 65535, 0xffff when it holds
        assert_eq!(pcf(9, 4, 0, 0.5, [0xd000; 2], 0.0), Ok(vec![0xffff]));
        // bilinear: two texels at half weight, one holding
        // texels 0x0451 and 0xd000 share a dword
        assert_eq!(pcf(9, 4, 1 << 12, 0.5, [0xd000_0451; 2], 0.25), Ok(vec![0x8000]));
        assert_eq!(pcf(18, 1, 1 << 12, 0.5, [0, 0x4000_0000], 0.25), Ok(vec![0x3f00_0000]));
        // a colour format ignores it
        assert_eq!(pcf(12, 4, 0, 0.5, [0xd000_0453; 2], 0.0), Ok(vec![0xd000_0453]));
        // other weights are not measured
        assert!(pcf(9, 4, 1 << 12, 0.5, [0xd000_0451; 2], 0.2).is_err());
    }

    /// E041's probe texture (mips.toml): 16x16 twiddled at 0x2000, level 0 the
    /// host fill 0xD0000000 | dword index, levels 1-4 packed after it, each
    /// texel tag << 24 | level << 16 | x * 0x20 << 8 | y * 0x20.
    fn chain(a: u32) -> Result<u32, crate::Error> {
        let off = a - 0x2000;
        if off < 0x400 {
            return Ok(0xd000_0000 | (a / 4));
        }
        let mut start = 0x400;
        for l in 1..5u32 {
            let n = 16 >> l;
            if off < start + 4 * n * n {
                let i = (off - start) / 4;
                let (mut x, mut y) = (0, 0);
                for b in 0..4 {
                    y |= ((i >> (2 * b)) & 1) << b;
                    x |= ((i >> (2 * b + 1)) & 1) << b;
                }
                let tag = [0, 0x40, 0x80, 0xc0, 0xf0][l as usize];
                return Ok((tag << 24) | (l << 16) | ((x * 0x20) << 8) | (y * 0x20));
            }
            start += 4 * n * n;
        }
        Ok(0xd000_0000 | (a / 4))
    }

    /// A sample of the chain with T0 and T1's format, the probe's T3.
    fn mip(t0: u32, fmt: u32, u: f32, v: f32, lod: Lod) -> Result<Vec<u32>, Fail> {
        let state = [t0, fmt << 24 | 15 << 12 | 15, 0x2000, 0x0080_0800];
        sample(&Sample { state, u, v, one_d: false, srd: Srd::None, pcf: None, lod }, &mut chain)
    }

    /// texture-mipmaps-mip-level and texture-mipmaps-mip-mipfilter's coordinates: level 0 texel (3, 10).
    fn lod(t0: u32, l: f32) -> Result<Vec<u32>, Fail> {
        mip(t0, 12, 0.21875, 0.65625, Lod::Value(l))
    }

    #[test]
    fn t3_bits_12_11_pick_level_0_or_the_last_level() {
        // E1027 (held out with smp2dreplace on 64 x 64 and 32 x 32 chains): 00 reads level 0 and
        // 1x the last level T0's max level allows, whatever the LOD; 01 is the LOD's level
        let at = |t0: u32, t3: u32, l: f32| {
            let s = Sample {
                state: [t0, 0x0c00_f00f, 0x2000, t3],
                u: 0.21875,
                v: 0.65625,
                one_d: false,
                srd: Srd::None,
                pcf: None,
                lod: Lod::Value(l),
            };
            sample(&s, &mut |a| Ok(0xd000_0000 | ((a - 0x2000) / 4 + 0x800)))
        };
        assert_eq!(at(0x07fa_0000, 0x0080_0000, 3.0), Ok(vec![0xd000_084e]), "00: level 0");
        assert_eq!(at(0x07fa_0000, 0x0080_1800, 0.0), Ok(vec![0xd000_0954]), "11: level 4");
        assert_eq!(at(0x07fa_0000, 0x0080_1000, 1.0), Ok(vec![0xd000_0954]), "10: level 4");
        assert_eq!(at(0x07e4_0000, 0x0080_1800, 0.0), Ok(vec![0xd000_0944]), "11, max level 2");
        assert_eq!(at(0x07fa_0000, 0x0080_0800, 2.0), Ok(vec![0xd000_0944]), "01: the LOD's");
        // not run: the bits with T0 bit 9 (a blend of levels) or with mips off
        assert!(at(0x07fa_0200, 0x0080_1800, 0.0).is_err(), "bit 9");
        assert!(at(0x001a_0000, 0x0080_1800, 0.0).is_err(), "mips off");
    }

    #[test]
    fn mip_levels_follow_level_0_back_to_back() {
        // texture-mipmaps-mip-level-hostfill 1-4 (no stores): LOD 1-4 read dwords 0x913,
        // 0x944, 0x951, 0x954 of the host fill, levels 1-4 at 0x400, 0x500,
        // 0x540, 0x550 (E041)
        let host = |l: f32| {
            let state = [0x07fa_0000, 0x0c00_f00f, 0x2000, 0x0080_0800];
            let s = Sample {
                state,
                u: 0.21875,
                v: 0.65625,
                one_d: false,
                srd: Srd::None,
                pcf: None,
                lod: Lod::Value(l),
            };
            sample(&s, &mut |a| Ok(0xd000_0000 | ((a - 0x2000) / 4 + 0x800)))
        };
        assert_eq!(host(0.0), Ok(vec![0xd000_084e]));
        assert_eq!(host(1.0), Ok(vec![0xd000_0913]));
        assert_eq!(host(2.0), Ok(vec![0xd000_0944]));
        assert_eq!(host(3.0), Ok(vec![0xd000_0951]));
        assert_eq!(host(4.0), Ok(vec![0xd000_0954]));
    }

    #[test]
    fn the_nearest_level_rounds_halves_up_and_clamps() {
        // texture-mipmaps-mip-level 0-9 and texture-mipmaps-mip-mipfilter 0-10 (T0 0x07FA0000)
        let want = [
            (-1.0, 0xd000_084e),
            (0.0, 0xd000_084e),
            (0.25, 0xd000_084e),
            (0.5, 0x4001_20a0),
            (0.75, 0x4001_20a0),
            (1.0, 0x4001_20a0),
            (1.25, 0x4001_20a0),
            (1.5, 0x8002_0040),
            (2.0, 0x8002_0040),
            (2.5, 0xc003_0020),
            (3.0, 0xc003_0020),
            (3.5, 0xf004_0000),
            (4.0, 0xf004_0000),
            (4.5, 0xf004_0000),
            (5.0, 0xf004_0000),
            (8.0, 0xf004_0000),
        ];
        for (l, w) in want {
            assert_eq!(lod(0x07fa_0000, l), Ok(vec![w]), "LOD {l}");
        }
        // texture-mipmaps-mip-level 11: the driver's format 13 swaps red and blue on level 1
        assert_eq!(mip(0x07fa_0000, 13, 0.21875, 0.65625, Lod::Value(1.0)), Ok(vec![0x40a0_2001]));
    }

    #[test]
    fn t0_fields_enable_the_chain() {
        // texture-mipmaps-mip-t0-field (LOD 2): 26:21 = 0x3f with 20:17 = 0xd, 0xc, 0x9, 0x5
        // read level 2; 26:21 = 0, 1, 2, 3, 7, bit 18 set or 20:17 = 0 level 0
        for t0 in [0x07fa_0000, 0x07f8_0000, 0x07f2_0000, 0x07ea_0000] {
            assert_eq!(lod(t0, 2.0), Ok(vec![0x8002_0040]), "T0 0x{t0:08x}");
        }
        for t0 in [
            0x001a_0000,
            0x0018_0000,
            0x003a_0000,
            0x005a_0000,
            0x007a_0000,
            0x00fa_0000,
            0x07fe_0000,
            0x07e0_0000,
        ] {
            assert_eq!(lod(t0, 2.0), Ok(vec![0xd000_084e]), "T0 0x{t0:08x}");
        }
        // E276: all 64 biases are measured; 0x10 is -47/8, so LOD 2 reads level 0
        assert_eq!(lod(0x021a_0000, 2.0), Ok(vec![0xd000_084e]), "26:21 = 0x10 is a bias");
    }

    #[test]
    fn twiddled_textures_of_32_or_more_texels_are_16x16_tiles_in_raster_order() {
        // p1132 tx-twiddle (N1): in a tile y is bit 0, x bit 1, and so on over 16 texels; the
        // tiles follow in raster order, x first (D1: 32x32 i8 = x4, i9 = y4; 64x32 i8 = x4,
        // i9 = x5, i10 = y4; 128x128 i8..i10 = x4..x6, i11..i13 = y4..y6)
        assert_eq!(morton(16, 0, 32, 32), 0x100);
        assert_eq!(morton(0, 16, 32, 32), 0x200);
        assert_eq!(morton(16, 16, 32, 32), 0x300);
        assert_eq!(morton(32, 0, 64, 32), 0x200);
        assert_eq!(morton(0, 16, 64, 32), 0x400);
        assert_eq!(morton(0, 16, 128, 128), 0x800);
        assert_eq!(morton(0, 32, 128, 128), 0x1000);
        // E441's levels 0 to 2 (the texel (28, 84) at 128, (14, 42) at 64, (7, 21) at 32: u =
        // 0.21875 of the size, v = 0.65625): its decoded pairs (20, 108), (10, 46), (5, 23) are
        // plain indices of these dwords, which the tile law gives (3 of 3)
        assert_eq!(morton(28, 84, 128, 128), 0x29b0);
        assert_eq!(morton(14, 42, 64, 64), 0x8ec);
        assert_eq!(morton(7, 21, 32, 32), 0x23b);
        assert_eq!(morton(16, 0, 32, 128), 0x100);
        assert_eq!(morton(0, 64, 32, 128), 0x600 + 0x200);
        // up to 16 on a side the plain interleave stands (E035), and a narrow texture is one tile
        // wide: 16x64, 128x16 and 8x128 are as before
        assert_eq!(morton(0, 16, 16, 64), 0x100);
        assert_eq!(morton(16, 0, 128, 16), 0x100);
        assert_eq!(morton(1, 16, 8, 128), 0x82);
        assert_eq!(morton(5, 1, 8, 2), 0b1011);
    }

    #[test]
    fn the_tile_law_is_refused_off_the_sizes_it_ran_on() {
        // p1132 tx-twiddle: 32-bit texels in 14 sizes with a side above 16 (E561, E562); a 2-byte
        // format, a size not run and 256 or more on a side were not run
        for (w, h) in [(32, 32), (64, 32), (64, 16), (64, 64), (128, 16), (128, 32), (32, 128), (128, 128)] {
            assert!(at(state(0, 12, w, h, 1, 0, 0), 0.3, 0.7).is_ok(), "{w}x{h}");
        }
        for (w, h) in [(16, 64), (8, 128), (32, 16), (16, 32), (64, 4), (8, 64)] {
            assert!(at(state(0, 12, w, h, 1, 0, 0), 0.3, 0.7).is_ok(), "{w}x{h}");
        }
        for (w, h) in [(256, 256), (256, 16), (16, 256), (128, 8), (4, 64), (64, 8), (32, 8), (512, 512)] {
            let r = at(state(0, 12, w, h, 1, 0, 0), 0.3, 0.7);
            assert!(matches!(&r, Err(Fail::Open(m)) if m.contains("twiddled")), "{w}x{h}: {r:?}");
        }
        // two bytes a texel: the plain interleave up to 16 on each side stands, above it is not run
        assert!(at(state(0, 4, 16, 16, 1, 0, 0), 0.3, 0.7).is_ok());
        assert!(at(state(0, 4, 8, 8, 1, 0, 0), 0.3, 0.7).is_ok());
        let r = at(state(0, 4, 32, 32, 1, 0, 0), 0.3, 0.7);
        assert!(matches!(&r, Err(Fail::Open(m)) if m.contains("twiddled")), "{r:?}");
        let r = at(state(0, 4, 8, 128, 1, 0, 0), 0.3, 0.7);
        assert!(matches!(&r, Err(Fail::Open(m)) if m.contains("twiddled")), "{r:?}");
        // a stride texture has no tiles
        assert!(at(state(6, 12, 256, 256, 256, 0, 0xa080_0000), 0.3, 0.7).is_ok());
    }

    #[test]
    fn a_non_square_chain_is_read_only_at_the_sizes_it_ran_on() {
        // p1132 tx-shapes and tx-fields: 32x16, 128x16, 16x32, 64x4 and 8x64 (E562); the square
        // sizes were measured before (E041, E441). 64x16 and 16x64 ran at level 0 only.
        let pick = |w: u32, h: u32| {
            let t =
                Texture::new(0x07fc_0000, 12 << 24 | (w - 1) << 12 | (h - 1), 0x2000, 0x0080_0800).unwrap();
            t.pick(0x07fc_0000, &Lod::Value(1.0), false).map(|_| ())
        };
        for (w, h) in [(32, 16), (128, 16), (16, 32), (64, 4), (8, 64), (32, 32)] {
            assert_eq!(pick(w, h), Ok(()), "{w}x{h}");
        }
        for (w, h) in [(64, 16), (16, 64), (128, 32), (32, 128)] {
            let r = pick(w, h);
            assert!(matches!(&r, Err(Fail::Open(m)) if m.contains("non-square")), "{w}x{h}: {r:?}");
        }
    }

    #[test]
    fn a_mip_chain_of_a_non_square_texture_halves_both_sides_down_to_1x1() {
        // p1132 tx-shapes (E562): chain A, 8 of 8 fit and 49 of 49 held-out cases exact. 32x16
        // reads 512, 128, 32, 8, 2 and 1 dwords at 0, 512, 640, 672, 680 and 682; LOD 6 and 7 read
        // the last level (1x1)
        let t = Texture::new(0x07fc_0000, 12 << 24 | 31 << 12 | 15, 0x2000, 0x0080_0800).unwrap();
        let dims: Vec<(u32, u32, u32)> =
            (0..6).map(|l| t.level(l)).map(|t| (t.w, t.h, (t.base - 0x2000) / 4)).collect();
        assert_eq!(dims, [(32, 16, 0), (16, 8, 512), (8, 4, 640), (4, 2, 672), (2, 1, 680), (1, 1, 682)]);
        let (levels, _) = t.pick(0x07fc_0000, &Lod::Value(7.0), false).unwrap();
        assert_eq!(levels, [(5, 64)]);
        let (levels, _) = t.pick(0x07fc_0000, &Lod::Value(4.0), false).unwrap();
        assert_eq!(levels, [(4, 64)]);
        // 64x4: the short side is 1 from level 2 on, the chain goes on to level 6
        let t = Texture::new(0x07fc_0000, 12 << 24 | 63 << 12 | 3, 0x2000, 0x0080_0800).unwrap();
        assert_eq!(((t.level(6).w, t.level(6).h), (t.level(6).base - 0x2000) / 4), ((1, 1), 350));
        let (levels, _) = t.pick(0x07fc_0000, &Lod::Value(9.0), false).unwrap();
        assert_eq!(levels, [(6, 64)]);
    }

    #[test]
    fn t0_bits_26_21_at_0_keep_magnifying() {
        // x-smp 83, 87, 91, 92: T0 0x001E0400, min linear, mag
        // point, LOD 1 or 2 (replace or gradients of 2 and 4 texels) read
        // texel (3, 5) not filtered; with 26:21 = 0x3f (texture-mipmaps-mip-minfilter 14) the
        // same minifies linearly
        let at = |lod: Lod| mip(0x001e_0400, 12, 0.1875, 0.34375, lod);
        assert_eq!(at(Lod::Value(1.0)), Ok(vec![0xd000_081b]));
        assert_eq!(at(Lod::Value(2.0)), Ok(vec![0xd000_081b]));
        assert_eq!(at(Lod::Grad([0.25, 0.0, 0.0, 0.25])), Ok(vec![0xd000_081b]));
        assert_eq!(at(Lod::Open("a quad")), Ok(vec![0xd000_081b]));
        // (2.5, 5.0) on level 0: texels (2, 5) and (3, 5), 0x19 and 0x1b
        assert_eq!(mip(0x07fe_0400, 12, 0.1875, 0.34375, Lod::Value(1.0)), Ok(vec![0xd000_081a]));
        assert!(
            mip(0x007e_0400, 12, 0.1875, 0.34375, Lod::Value(1.0)).is_err(),
            "26:21 = 3, minified: not measured"
        );
    }

    #[test]
    fn the_linear_mip_filter_blends_two_levels() {
        // texture-mipmaps-mip-mipfilter 11-21 (T0 0x07FA0200): per channel, by the LOD's
        // fraction, halves up
        let want = [
            (0.0, 0xd000_084e),
            (0.25, 0xac00_0e63),
            (0.5, 0x8801_1477),
            (1.0, 0x4001_20a0),
            (1.25, 0x5001_1888),
            (1.5, 0x6002_1070),
            (1.75, 0x7002_0858),
            (2.5, 0xa003_0030),
            (3.5, 0xd804_0010),
            (4.0, 0xf004_0000),
            (4.5, 0xf004_0000),
        ];
        for (l, w) in want {
            assert_eq!(lod(0x07fa_0200, l), Ok(vec![w]), "LOD {l}");
        }
        // texture-mipmaps-mip-mipfilter 22-23: the driver's lml with bilinear levels
        assert_eq!(lod(0x07fa_1600, 0.5), Ok(vec![0x8801_1873]));
        assert_eq!(lod(0x07fa_1600, 1.5), Ok(vec![0x6002_1a6e]));
    }

    #[test]
    fn the_min_filter_acts_above_lod_0() {
        // texture-mipmaps-mip-minfilter: level-1 texel (2.0, 2.5), mag point; T0 bits
        // 11:10 at 1 or 2 filter linearly, 0 or 3 not
        let at = |t0: u32, l: f32| mip(t0, 12, 0.25, 0.3125, Lod::Value(l));
        for (k, lin) in [(0, false), (1, true), (2, true), (3, false)] {
            let t0 = 0x07fa_0000 | k << 10;
            assert_eq!(at(t0, 0.0), Ok(vec![0xd000_0831]), "{k}: LOD 0 magnifies");
            assert_eq!(at(t0, 1.0), Ok(vec![if lin { 0x4001_3040 } else { 0x4001_4040 }]), "{k}");
            assert_eq!(at(t0, 0.25), Ok(vec![if lin { 0xd000_0826 } else { 0xd000_0831 }]), "{k}");
        }
        assert_eq!(at(0x07fa_1400, 0.0), Ok(vec![0xd000_0826]), "mag linear");
        assert_eq!(at(0x07fa_1400, 1.0), Ok(vec![0x4001_3040]));
        assert_eq!(at(0x07fe_0400, 1.0), Ok(vec![0xd000_0826]), "no mipmaps: level 0 minified");
    }

    #[test]
    fn gradients_give_the_larger_axis() {
        // texture-mipmaps-mip-grad: du/dx and dv/dy of 1, 2, 4, 8, 16, 32 texels
        let g = |x: f32, y: f32| {
            mip(0x07fa_0000, 12, 0.21875, 0.65625, Lod::Grad([x / 16.0, 0.0, 0.0, y / 16.0]))
        };
        assert_eq!(g(1.0, 1.0), Ok(vec![0xd000_084e]));
        assert_eq!(g(2.0, 2.0), Ok(vec![0x4001_20a0]));
        assert_eq!(g(4.0, 4.0), Ok(vec![0x8002_0040]));
        assert_eq!(g(8.0, 8.0), Ok(vec![0xc003_0020]));
        assert_eq!(g(16.0, 16.0), Ok(vec![0xf004_0000]));
        assert_eq!(g(32.0, 32.0), Ok(vec![0xf004_0000]));
        assert_eq!(g(4.0, 1.0), Ok(vec![0x8002_0040]));
        assert_eq!(g(1.0, 4.0), Ok(vec![0x8002_0040]));
        assert!(g(3.0, 3.0).is_err(), "log2 of 3: not measured");
    }

    #[test]
    fn flat_coordinates_read_level_0() {
        // texture-mipmaps-mip-bias, texture-mipmaps-mip-level 12: zero derivatives, any bias
        assert_eq!(mip(0x07fa_0000, 12, 0.21875, 0.65625, Lod::Flat), Ok(vec![0xd000_084e]));
    }

    #[test]
    fn what_the_mip_probes_leave_open_stops() {
        assert!(lod(0x07fa_0200, 0.3).is_err(), "a blend at a fraction other than 1/64");
        assert!(lod(0x07fa_0000, 0.495).is_err(), "nearest just under the half");
        assert_eq!(lod(0x07fa_0000, 0.3), Ok(vec![0xd000_084e]));
        assert!(lod(0x07fa_1000, 0.25).is_err(), "mag linear, min point, LOD in (0, 0.5]");
        assert!(mip(0x07fa_0000, 12, 0.2, 0.6, Lod::Open("why")).is_err());
        // a LOD that cannot matter: no mipmaps, min and mag alike
        assert_eq!(mip(0x07fe_0000, 12, 0.21875, 0.65625, Lod::Open("why")), Ok(vec![0xd000_084e]));
        // a non-square chain is measured since p1132 (tx-shapes); a 1D one is not
        let rect = [0x07fa_0000, 12 << 24 | 15 << 12 | 7, 0x2000, 0];
        let s = Sample {
            state: rect,
            u: 0.0,
            v: 0.0,
            one_d: true,
            srd: Srd::None,
            pcf: None,
            lod: Lod::Value(1.0),
        };
        assert!(sample(&s, &mut chain).is_err(), "a 1D chain");
    }

    /// texture-sampler-smp-srd's sample of the chain (E042): level 0 texel (3, 10).
    fn srd(t0: u32, lod: Lod, srd: Srd) -> Result<Vec<u32>, Fail> {
        let state = [t0, 12 << 24 | 15 << 12 | 15, 0x2000, 0x0080_0800];
        let s = Sample { state, u: 0.21875, v: 0.65625, one_d: false, srd, pcf: None, lod };
        sample(&s, &mut chain)
    }

    #[test]
    fn sinf_gives_the_nearest_level_without_a_fraction() {
        // texture-sampler-smp-srd 1, 5-9 (T0 0x07FA0000): LOD 1, 0.5, 2, 2.75, 4, 6 give
        // levels 1, 1, 2, 3, 4, 4 in the second dword, 0 in the first; 3:
        // smp2d (no LOD of its own) level 0
        for (l, want) in [(1.0, 1), (0.5, 1), (2.0, 2), (2.75, 3), (4.0, 4), (6.0, 4)] {
            assert_eq!(srd(0x07fa_0000, Lod::Value(l), Srd::Info), Ok(vec![0, want]), "LOD {l}");
        }
        assert_eq!(srd(0x07fa_0000, Lod::Flat, Srd::Info), Ok(vec![0, 0]));
    }

    #[test]
    fn sinf_gives_the_lower_level_and_the_fraction_when_blending() {
        // texture-sampler-smp-srd 10-12 (T0 0x07FA0200): LOD 0.25, 1.5, 2.75 give the
        // lower level and the six-bit fraction replicated to eight bits in
        // bits 23:16
        for (l, frac, level) in [(0.25, 0x41, 0), (1.5, 0x82, 1), (2.75, 0xc3, 2)] {
            assert_eq!(srd(0x07fa_0200, Lod::Value(l), Srd::Info), Ok(vec![frac << 16, level]), "LOD {l}");
        }
    }

    #[test]
    fn rsd_returns_the_unfiltered_texels() {
        // texture-sampler-smp-srd 2 and 4: point sampling returns the texel, as without
        // the mode (smp2dreplace at LOD 1; smp2d level 0)
        assert_eq!(srd(0x07fa_0000, Lod::Value(1.0), Srd::Raw), Ok(vec![0x4001_20a0]));
        assert_eq!(srd(0x07fa_0000, Lod::Flat, Srd::Raw), Ok(vec![0xd000_084e]));
        // texture-sampler-smp-srd 13 (T0 0x07FA1600, LOD 1.5; 14 blends them to
        // 0x60021A6E): level 1's 2x2 footprint then level 2's, each in the
        // order (x0, y0), (x1, y0), (x0, y1), (x1, y1)
        assert_eq!(
            srd(0x07fa_1600, Lod::Value(1.5), Srd::Raw),
            Ok(vec![
                0x4001_2080,
                0x4001_4080,
                0x4001_20a0,
                0x4001_40a0,
                0x8002_0040,
                0x8002_2040,
                0x8002_0060,
                0x8002_2060
            ])
        );
    }

    #[test]
    fn what_the_srd_probes_leave_open_stops() {
        assert!(srd(0x07fa_0200, Lod::Value(1.0), Srd::Info).is_err(), ".sinf blending at a whole LOD");
        assert!(srd(0x07fa_1600, Lod::Value(1.5), Srd::Info).is_err(), ".sinf with bilinear levels");
        assert!(srd(0x07fe_0000, Lod::Value(1.0), Srd::Info).is_err(), ".sinf without a mip chain");
        assert!(srd(0x07fa_0200, Lod::Value(1.5), Srd::Raw).is_err(), ".rsd blending point samples");
        assert!(srd(0x07fa_1400, Lod::Value(1.0), Srd::Raw).is_err(), ".rsd of one bilinear level");
    }

    /// The sampler probes' texture (x-smp2, x-smp3): 16x16 at
    /// 0x1000, 64-byte rows, dword i 0xD0000400 + i.
    fn probe_texel(a: u32) -> Result<u32, crate::Error> {
        Ok(0xd000_0400u32.wrapping_add((a - 0x1000) / 4))
    }

    /// A point sample of the probe texture as a stride texture of format
    /// `fmt` with T0 `t0` and T3 `t3`, at texel (x + 0.5, y + 0.5).
    fn probe(fmt: u32, t0: u32, t3: u32, x: u32, y: u32) -> Result<Vec<u32>, Fail> {
        let st = state(6, fmt, 16, 16, 16, t0, t3);
        let (u, v) = ((x as f32 + 0.5) / 16.0, (y as f32 + 0.5) / 16.0);
        sample(
            &Sample { state: st, u, v, one_d: false, srd: Srd::None, pcf: None, lod: Lod::Flat },
            &mut probe_texel,
        )
    }

    /// texture-sampler-smp-formats-other's texels, as (x, y): two-byte formats read 0x0451,
    /// 0xD000, 0x04F7 and 0xD000; four-byte ones dwords 0x52, 0x53, 0xFE, 0xFF.
    const OTHER: [(u32, u32); 4] = [(2, 5), (3, 5), (14, 15), (15, 15)];

    fn other(fmt: u32) -> Vec<Result<Vec<u32>, Fail>> {
        OTHER.iter().map(|&(x, y)| probe(fmt, 0, 0xa080_0000, x, y)).collect()
    }

    #[test]
    fn format_6_is_l6_v5_u5() {
        // texture-sampler-smp-formats-other 0-3 (x-smp3 96-99): the six-bit field 15:10 in
        // B, the signed fields 9:5 in G and 4:0 in R, each sign kept and the
        // four bits below it repeated (2 is 0x11, -15 0x88), alpha 0xff
        let want = [0xff88_1104, 0xff00_00d3, 0xffbb_3b04, 0xff00_00d3];
        assert_eq!(other(6), Vec::from(want.map(|w| Ok(vec![w]))));
    }

    #[test]
    fn format_14_is_a2_b10_g10_r10_in_16_bit_pairs() {
        // texture-sampler-smp-formats-other 4-7 (x-smp3 100-103, x-smp2 20): each field
        // widened to 16 bits by repeating its bits, R | G << 16 then B | A << 16
        let want = [0x0040_1485, 0x0040_14c5, 0x0040_3f8f, 0x0040_3fcf];
        assert_eq!(other(14), Vec::from(want.map(|w| Ok(vec![w, 0xffff_4010]))));
    }

    #[test]
    fn format_20_reads_a_pair_of_texels_unconverted() {
        // texture-sampler-smp-formats-other 8-11 (x-smp3 104-107): the texel's own byte (0
        // for an even x, 2 for an odd one) in R, the pair's byte 1 in G and
        // byte 3 in B, alpha 0xff
        let want = [0xff51_04d0, 0xff00_04d0, 0xfff7_04d0, 0xff00_04d0];
        assert_eq!(other(20), Vec::from(want.map(|w| Ok(vec![w]))));
        let twiddled = [0, 20 << 24 | 15 << 12 | 15, 0x1000, 0];
        let s = Sample {
            state: twiddled,
            u: 0.0,
            v: 0.0,
            one_d: false,
            srd: Srd::None,
            pcf: None,
            lod: Lod::Flat,
        };
        assert!(sample(&s, &mut probe_texel).is_err(), "format 20 twiddled is not measured");
    }

    #[test]
    fn float_formats_convert_exactly_or_saturate() {
        // x-smp3 136-143 at texel (15, 15): format 11 reads the half 0xD000
        // (-32.0), 18 the f32 0xD00004FF (about -8.6e9); c10 saturates at
        // -510 (0x202) as pckc10f32 does, f16 at -65504, f32 is exact and
        // bit 15 does not act on it
        let c = |fmt: u32, t3: u32| probe(fmt, 0, 0xa000_0000 | t3, 15, 15);
        assert_eq!(c(11, 1 << 16), Ok(vec![0x202]));
        assert_eq!(c(11, 2 << 16), Ok(vec![0xd000]));
        assert_eq!(c(11, 3 << 16), Ok(vec![0xc200_0000]));
        assert_eq!(c(11, 3 << 16 | 1 << 15), Ok(vec![0xc200_0000]));
        assert_eq!(c(18, 1 << 16), Ok(vec![0x202]));
        assert_eq!(c(18, 2 << 16), Ok(vec![0xfbff]));
        assert_eq!(c(18, 3 << 16), Ok(vec![0xd000_04ff]));
        assert_eq!(c(18, 3 << 16 | 1 << 15), Ok(vec![0xd000_04ff]));
        // values the saturation does not reach are not measured
        let one = |fmt: u32, t3: u32, texel: u32| {
            let s = Sample {
                state: state(6, fmt, 2, 2, 1, 0, t3),
                u: 0.0,
                v: 0.0,
                one_d: false,
                srd: Srd::None,
                pcf: None,
                lod: Lod::Flat,
            };
            sample(&s, &mut |_| Ok(texel))
        };
        assert!(one(18, 1 << 16, 1.5f32.to_bits()).is_err(), "c10 within +/-2");
        assert!(one(18, 2 << 16, 1.5f32.to_bits()).is_err(), "f16 of a value a half holds");
        assert!(one(18, 2 << 16, 1e9f32.to_bits()).is_err(), "positive saturation");
        assert!(one(11, 2 << 16 | 1 << 15, 0x3c00).is_err(), "normalized f16");
        assert!(one(18, 3 << 16, f32::NAN.to_bits()).is_err(), "a NaN");
    }

    #[test]
    fn t3_bits_7_0_offset_the_texel() {
        // x-smp2 27-34 at texel (3, 5) of the stride texture: bits 3:0 add a
        // signed four-bit offset to y, bits 7:4 to x, clamped as the
        // coordinates are
        let at = |t3: u32| probe(12, 0, 0xa080_0000 | t3, 3, 5);
        assert_eq!(at(0), Ok(vec![0xd000_0453]));
        for (bit, want) in [
            (0, 0xd000_0463),
            (1, 0xd000_0473),
            (2, 0xd000_0493),
            (3, 0xd000_0403),
            (4, 0xd000_0454),
            (5, 0xd000_0455),
            (6, 0xd000_0457),
            (7, 0xd000_0450),
        ] {
            assert_eq!(at(1 << bit), Ok(vec![want]), "T3 bit {bit}");
        }
        // filtered, twiddled or with .pcf not measured
        assert!(probe(12, 1 << 12, 0xa080_0001, 3, 5).is_err(), "bilinear");
        let twiddled = [0x001e_0000, 12 << 24 | 15 << 12 | 15, 0x1000, 0xa080_0001];
        let s = Sample {
            state: twiddled,
            u: 0.0,
            v: 0.0,
            one_d: false,
            srd: Srd::None,
            pcf: None,
            lod: Lod::Flat,
        };
        assert!(sample(&s, &mut probe_texel).is_err(), "twiddled");
    }

    #[test]
    fn t3_bits_19_18_scale_the_texel_offset() {
        // x-smp2 45-46: texel (3, 5), byte 332 of the texture, read at 664
        // and 1328: the offset from the base doubled per step, past the
        // texture's end, not the coordinates (which would clamp)
        assert_eq!(probe(12, 0, 0xa084_0000, 3, 5), Ok(vec![0xd000_04a6]));
        assert_eq!(probe(12, 0, 0xa088_0000, 3, 5), Ok(vec![0xd000_054c]));
        assert!(probe(12, 0, 0xa08c_0000, 3, 5).is_err(), "3 is not measured");
        assert!(probe(5, 0, 0xa084_0000, 3, 5).is_err(), "a 16-bit format");
    }

    #[test]
    fn state_bits_that_change_nothing_on_a_stride_texture() {
        // x-smp2 11-13, 15-16 (T0 bits 14-16, 28, 29) and 35-36, 39, 47-49
        // (T3 bits 8, 9, 12, 20-22): texel (3, 5) as without them
        for t0 in [1 << 14, 1 << 15, 1 << 16, 1 << 28, 1 << 29] {
            assert_eq!(probe(12, t0, 0xa080_0000, 3, 5), Ok(vec![0xd000_0453]), "T0 0x{t0:08x}");
        }
        for bit in [8, 9, 12, 20, 21, 22] {
            assert_eq!(probe(12, 0, 0xa080_0000 | 1 << bit, 3, 5), Ok(vec![0xd000_0453]), "T3 bit {bit}");
        }
        // the bits that act in other ways stop: T0 27, 30, 31 and T3 10, 13,
        // 27, 28 (x-smp2 14, 17, 18, 37, 41, 54, 55); T3 14 (x-smp2 40) is modelled since E1003
        for t0 in [1 << 27, 1 << 30, 1 << 31] {
            assert!(probe(12, t0, 0xa080_0000, 3, 5).is_err(), "T0 0x{t0:08x}");
        }
        for bit in [10, 13, 27, 28] {
            assert!(probe(12, 0, 0xa080_0000 | 1 << bit, 3, 5).is_err(), "T3 bit {bit}");
        }
        // on a twiddled texture they are not measured
        let twiddled = [0x001e_4000, 12 << 24 | 15 << 12 | 15, 0x1000, 0];
        let s = Sample {
            state: twiddled,
            u: 0.0,
            v: 0.0,
            one_d: false,
            srd: Srd::None,
            pcf: None,
            lod: Lod::Flat,
        };
        assert!(sample(&s, &mut probe_texel).is_err());
    }

    #[test]
    fn the_recorded_formats_and_modes_without_a_model_stop() {
        // texture-sampler-smp-formats-other 12-39: compressed and YUV layouts; four texels
        // fix no decoder, and the YUV ones go through a colour-space set the
        // vector does not record (E037)
        for fmt in 23..=27 {
            assert!(other(fmt).iter().all(|r| r.is_err()), "format {fmt}");
        }
        // texture-sampler-smp-address-border: past the texture mode 5 reads E1039's regions on
        // 32-bit texels only (mode_5_past_the_texture_reads_its_regions); a 16-bit one has no model
        {
            let mode = 5;
            let st = [0x001e_0000 | mode << 6, 9 << 24 | 15 << 12 | 15, 0x1000, 0xa080_0000];
            let s = Sample {
                state: st,
                u: 1.09375,
                v: 0.03125,
                one_d: false,
                srd: Srd::None,
                pcf: None,
                lod: Lod::Flat,
            };
            assert!(sample(&s, &mut probe_texel).is_err(), "mode {mode}");
        }
    }

    #[test]
    fn the_yuv_texel_model_is_opaque_black_for_an_unloaded_set() {
        // the texel model for a set that is not loaded (E037, E040 and p1132 tx-formats-yuv-nocsc,
        // fy-28 and fy-29, two patterns: 2048 of 2048 pixels 0xff000000 in each job); whether
        // the set is unloaded is the machine's to know (Machine::csc_unloaded)
        for fmt in [28, 29] {
            assert!(other(fmt).iter().all(|r| r == &Ok(vec![0xff00_0000])), "format {fmt}");
        }
    }

    #[test]
    fn smp3d_is_smp2d_only_where_it_ran() {
        // E567: TEXTYPE 0, 6 and 7, format 12, point filters, one level, a 16x16 twiddled and
        // a 64x32 stride texture, T3 as run
        let tw = [0x07fe_0000, 0x0c00_f00f, 0x1000, 0x0080_0800];
        let st = [0x000e_0e00, 0xcc03_f01f, 0x1000, 0xa080_0000];
        assert_eq!(smp3d_as_2d(tw, false), Ok(()));
        assert_eq!(smp3d_as_2d(st, false), Ok(()));
        let mut t7 = tw;
        t7[1] |= 7 << 29;
        assert_eq!(smp3d_as_2d(t7, false), Ok(()));
        // the rule itself refuses TEXTYPE 2, whatever Texture::new does with it
        for ty in [1, 2, 3, 4, 5] {
            let mut t = tw;
            t[1] |= ty << 29;
            let r = smp3d_as_2d(t, false);
            assert!(
                matches!(&r, Err(m) if m.contains("smp3d") && m.contains(&format!("TEXTYPE {ty}"))),
                "{r:?}"
            );
        }
        assert!(smp3d_as_2d(tw, true).is_err(), "with .pcf or an SRD mode");
        let mut t = tw;
        t[1] = 0x0c01_f00f;
        assert!(smp3d_as_2d(t, false).is_err(), "32x16");
        let mut t = st;
        t[1] = 0xcc00_f00f;
        assert!(smp3d_as_2d(t, false).is_err(), "16x16 stride");
        let mut t = tw;
        t[0] = 0x07fc_0000;
        assert!(smp3d_as_2d(t, false).is_err(), "the chain");
        let mut t = tw;
        t[0] |= 3 << 12;
        assert!(smp3d_as_2d(t, false).is_err(), "a filter");
        let mut t = tw;
        t[3] |= 1 << 10;
        assert!(smp3d_as_2d(t, false).is_err(), "T3 bit 10");
    }

    #[test]
    fn texture_type_7_reads_as_twiddled_at_16x16() {
        // p1132 tx-types-risky (rt7-2d, rt7-3d-w5, rt7-3d-w15): TEXTYPE 7 on a 16x16 texture reads
        // the twiddled image, 2048 of 2048 pixels each; no other size was run
        let tw = at(state(0, 12, 16, 16, 1, 0, 0), 0.3, 0.7);
        assert!(tw.is_ok());
        assert_eq!(at(state(7, 12, 16, 16, 1, 0, 0), 0.3, 0.7), tw);
        assert!(at(state(7, 12, 32, 32, 1, 0, 0), 0.3, 0.7).is_err(), "7 at another size");
        assert!(at(state(1, 12, 16, 16, 1, 0, 0), 0.3, 0.7).is_err(), "type 1");
    }

    #[test]
    fn t3_bit_14_on_the_twiddled_32x32_widens_its_tile_rows_by_4096_texels() {
        // E1047 (r14-flag f1): column s + floor(4096 frac(u)) in 16 x 16 tiles, 258 a tile row
        let tw = |u: f32, v: f32, t3: u32| at(state(0, 12, 32, 32, 1, 0, t3), u, v);
        // u = x / 4096 at x = 5, row 3: column 5, inside tile 0 (y bits 0, 2; x bits 0, 2 at 1, 5)
        assert_eq!(tw(5.0 / 4096.0, 3.5 / 32.0, 1 << 14), Ok(vec![0x100 + 39]));
        // u = 0, row 16: the second tile row, 258 tiles on (W + 4096 = 4128 texels)
        assert_eq!(tw(0.0, 16.5 / 32.0, 1 << 14), Ok(vec![0x100 + 258 * 256]));
        // u = 1 + 33 / 64 (E566's map, q = 16): wrapped column 16, + 4096 * 33 / 64 = 2128
        assert_eq!(tw(1.0 + 33.0 / 64.0, 0.5 / 32.0, 1 << 14), Ok(vec![0x100 + 133 * 256]));
        // without the bit the tile law
        assert_eq!(tw(0.0, 16.5 / 32.0, 0), Ok(vec![0x100 + 2 * 256]));
    }

    #[test]
    fn t3_bit_14_on_twiddled_widths_16_to_128_and_u16_widens_by_4096_texels() {
        // E1049 (r15-tw tw14): the same rule at W 16, 64 and 128 (H 32) with u past 1 and 2, the
        // tile row W + 4096 texels (4112, 4160, 4224), and on u16 in texels (the half T & 1 of
        // dword T >> 1)
        let tw = |fmt: u32, w: u32, u: f32, v: f32| at(state(0, fmt, w, 32, 1, 0, 1 << 14), u, v);
        // 16 x 32, u = 11 / 128, row 16: column 1 + 352, tile 22 of the second tile row (257)
        assert_eq!(tw(12, 16, 11.0 / 128.0, 33.0 / 64.0), Ok(vec![0x100 + 71426]));
        // 64 x 32, u = 2 + 21 / 128, row 3: column 10 + 672
        assert_eq!(tw(12, 64, 2.0 + 21.0 / 128.0, 7.0 / 64.0), Ok(vec![0x100 + 10893]));
        // 128 x 32, u = 2 + 21 / 256, row 20: column 10 + 336, second tile row (264 tiles)
        assert_eq!(tw(12, 128, 2.0 + 21.0 / 256.0, 41.0 / 64.0), Ok(vec![0x100 + 73112]));
        // u16 32 x 32, u = 15 / 128, row 2: texel 7694, the low half of dword 3847
        assert_eq!(tw(9, 32, 15.0 / 128.0, 5.0 / 64.0), Ok(vec![0x1007]));
        // u16, u = 1 + 15 / 128, row 18: texel 73742, the low half of dword 36871
        assert_eq!(tw(9, 32, 1.0 + 15.0 / 128.0, 37.0 / 64.0), Ok(vec![0x9107]));
        // u16 without the bit (tw-refu16): E561's index in texels, texel 38 the low half of dword
        // 19, texel 39 the high half (0 here)
        let ref16 = |u: f32, v: f32| at(state(0, 9, 32, 32, 1, 0, 0), u, v);
        assert_eq!(ref16(5.5 / 32.0, 2.5 / 32.0), Ok(vec![0x100 + 19]));
        assert_eq!(ref16(5.5 / 32.0, 3.5 / 32.0), Ok(vec![0]));
        // not run: another height or width, a filter (E1049's bilinear footprint is post hoc), a
        // mode other than repeat, another format
        assert!(tw(12, 32, 0.0, 0.0).is_ok());
        assert!(at(state(0, 12, 32, 64, 1, 0, 1 << 14), 0.0, 0.0).is_err(), "32 x 64");
        assert!(at(state(0, 12, 256, 32, 1, 0, 1 << 14), 0.0, 0.0).is_err(), "256 x 32");
        assert!(at(state(0, 12, 8, 32, 1, 0, 1 << 14), 0.0, 0.0).is_err(), "8 x 32");
        assert!(at(state(0, 12, 32, 32, 1, 1 << 12, 1 << 14), 0.0, 0.0).is_err(), "bilinear");
        assert!(at(state(0, 12, 32, 32, 1, 2 << 6, 1 << 14), 0.0, 0.0).is_err(), "u clamped");
        assert!(at(state(0, 5, 32, 32, 1, 0, 1 << 14), 0.0, 0.0).is_err(), "format 5");
    }

    #[test]
    fn what_is_not_measured_stops() {
        assert!(at(state(6, 12, 4, 4, 4, 1 << 27, 0), 0.0, 0.0).is_err(), "T0 bit 27");
        // T3 bit 14 (E1003): a stride texture point sampled moves by floor(4096 clamp(u)) texels;
        // a twiddled texture (E566's fault), a filter or a conversion stays refused
        assert_eq!(at(state(6, 12, 4, 4, 4, 0, 1 << 14), 0.25, 0.0), Ok(vec![0x100 + 1 + 1024]), "T3 bit 14");
        assert_eq!(at(state(6, 12, 4, 4, 4, 0, 1 << 14), 1.5, 0.0), Ok(vec![0x100 + 3 + 4096]), "u clamped");
        assert_eq!(at(state(6, 9, 4, 4, 4, 0, 1 << 14), 0.5, 0.0), Ok(vec![0x100 + 1025]), "16-bit: texels");
        assert!(at(state(0, 12, 4, 4, 1, 0, 1 << 14), 0.25, 0.0).is_err(), "T3 bit 14 twiddled 4x4");
        assert!(at(state(6, 12, 4, 4, 4, 1 << 12, 1 << 14), 0.25, 0.0).is_err(), "T3 bit 14 bilinear");
        assert!(at(state(6, 12, 4, 4, 4, 0, 1 << 14 | 2 << 16), 0.25, 0.0).is_err(), "T3 bit 14 converted");
        assert!(at(state(6, 12, 4, 4, 4, 0, 0xa080_0000), 0.0, 0.0).is_ok(), "the copies' T3");
        assert!(at(state(4, 12, 4, 4, 1, 0, 0), 0.0, 0.0).is_err(), "tiled");
        assert!(at(state(6, 23, 4, 4, 4, 0, 0), 0.0, 0.0).is_err(), "format 23");
        assert!(at(state(6, 22, 4, 4, 4, 0, 3 << 16), 0.0, 0.0).is_err(), "conversion of a dword format");
    }

    /// The state words of the jobs of E723 to E725 (p1141, p1132's catalog): point filters,
    /// repeat, level 0 only (T0_REP), the T3 of a twiddled and of a stride texture.
    const T0_REP: u32 = 0x07fe_0000;
    const T3_TW: u32 = 0x0080_0800;
    const T3_ST: u32 = 0xa080_0000;

    fn t1(ty: u32, fmt: u32, w: u32, h: u32) -> u32 {
        ty << 29 | fmt << 24 | (w - 1) << 12 | (h - 1)
    }

    /// Sample texel (x, y) of a w x h texture at 0x1000 (the centre of the texel) over `mem`.
    fn texel(
        st: [u32; 4],
        w: u32,
        h: u32,
        x: u32,
        y: u32,
        mem: &dyn Fn(u32) -> u32,
    ) -> Result<Vec<u32>, Fail> {
        let (u, v) = ((x as f32 + 0.5) / w as f32, (y as f32 + 0.5) / h as f32);
        sample(
            &Sample { state: st, u, v, one_d: false, srd: Srd::None, pcf: None, lod: Lod::Flat },
            &mut |a| Ok(mem(a)),
        )
    }

    fn is_open<T: std::fmt::Debug>(r: Result<T, Fail>) -> bool {
        matches!(r, Err(Fail::Open(_)))
    }

    #[test]
    fn srgb_decodes_bytes_0_and_1_to_nearest_even_halves() {
        // E723: the dword is half(s2l(byte 1)) << 16 | half(s2l(byte 0)), s2l the sRGB curve
        for (b, h) in [
            (0, 0x0000),
            (1, 0x0cf9),
            (10, 0x1a37),
            (11, 0x1adb),
            (12, 0x1b88),
            (128, 0x32e8),
            (200, 0x389f),
            (254, 0x3bee),
            (255, 0x3c00),
        ] {
            assert_eq!(srgb_half(b), h, "byte {b}");
        }
        assert_eq!(srgb_word(0xaabb_ff01), 0x3c00_0cf9);
    }

    #[test]
    fn a_bilinear_srgb_stage_floors_both_halves_to_the_larger_ones_ulp() {
        // E982: weight 0 returns A unchanged, equal halves stay (E976's control)
        assert_eq!(srgb_stage(0x0cf9, 0x3c00, 0), 0x0cf9);
        assert_eq!(srgb_stage(0x32e8, 0x32e8, 37), 0x32e8);
        // 1.0 and byte 1's half (3.0e-4, below 1.0's ulp of 2^-10, so floored to 0): 63/64 of the
        // way down is 1/64 exactly, where the exact lerp of the halves would be 20 ulps above it
        assert_eq!(srgb_stage(0x3c00, 0x0cf9, 63), 0x2400);
        // the result rounds to nearest with ties up: between 0.5 and the next half, a quarter of
        // the way rounds down, half of it (to nearest even would give 0.5) and three quarters up
        assert_eq!(srgb_stage(0x3800, 0x3801, 16), 0x3800);
        assert_eq!(srgb_stage(0x3800, 0x3801, 32), 0x3801);
        assert_eq!(srgb_stage(0x3800, 0x3801, 48), 0x3801);
    }

    #[test]
    fn a_bilinear_srgb_stage_result_below_2_to_the_minus_14_is_flushed_to_zero() {
        // E1004 (post hoc) and E1016 (held out offline): a stage whose result would be a
        // subnormal half gives +0; byte 0 and byte 2 (6.07e-4) at weight 4 lerp to 3.8e-5
        let h = srgb_half;
        assert_eq!(srgb_stage(h(0), h(2), 4), 0);
        // a normal result is kept: byte 2 at weight 7 is 6.6e-5 (0x045a)
        assert_eq!(srgb_stage(h(0), h(2), 7), 0x045a);
        // E1016: p1132 tx-lod's an-t0b27, pixel column x = 4, channel 0: corner bytes 00, 10,
        // 01, 11, the weights kx and ky of 64, and the half the hardware stored (every one of
        // the 12 halves where the flush changes the result; detail_b.out of
        // closing11/plan/c2-texture/)
        let kept: [([u32; 4], u32, u32, u32); 12] = [
            ([21, 23, 0, 2], 4, 36, 0x1ac8),
            ([21, 23, 0, 2], 4, 44, 0x18d8),
            ([21, 23, 0, 2], 4, 52, 0x15d0),
            ([21, 23, 0, 2], 4, 60, 0x0fc0),
            ([0, 2, 1, 3], 4, 4, 0x0000),
            ([0, 2, 1, 3], 4, 12, 0x0431),
            ([0, 2, 1, 3], 4, 20, 0x06fd),
            ([0, 2, 1, 3], 4, 28, 0x08e4),
            ([0, 2, 1, 3], 4, 36, 0x0a4a),
            ([0, 2, 1, 3], 4, 44, 0x0bb0),
            ([0, 2, 1, 3], 4, 52, 0x0c8b),
            ([0, 2, 1, 3], 4, 60, 0x0d3e),
        ];
        for (b, kx, ky, want) in kept {
            let (top, bottom) = (srgb_stage(h(b[0]), h(b[1]), kx), srgb_stage(h(b[2]), h(b[3]), kx));
            assert_eq!(srgb_stage(top, bottom, ky), want, "{b:?} kx {kx} ky {ky}");
        }
    }

    #[test]
    fn srgb_samples_the_textures_e723_ran_and_refuses_the_rest() {
        let mem = |a: u32| 0xd000_0000 | ((a - 0x1000) / 4) | 0x0000_ff00;
        let want = |i: u32| srgb_word(0xd000_ff00 | i);
        // a stride 8 x 4 texture, and twiddled 8 x 8 and 32 x 32 ones (4 of 4 held out)
        let st84 = [0x0800_0e00, t1(6, 12, 8, 4), 0x1000, T3_ST];
        assert_eq!(texel(st84, 8, 4, 3, 2, &mem), Ok(vec![want(2 * 8 + 3)]));
        let tw8 = [T0_REP | 1 << 27, t1(0, 12, 8, 8), 0x1000, T3_TW];
        assert_eq!(texel(tw8, 8, 8, 1, 0, &mem), Ok(vec![want(2)]));
        let tw32 = [T0_REP | 1 << 27, t1(0, 12, 32, 32), 0x1000, T3_TW];
        assert_eq!(texel(tw32, 32, 32, 0, 1, &mem), Ok(vec![want(1)]));
        // bilinear on E723's 8 x 8 stride fills (E982): at a texel centre both weights are 0
        let bl = [T0_SRGB_BL_STRIDE8, t1(6, 12, 8, 8), 0x1000, T3_ST];
        assert_eq!(texel(bl, 8, 8, 3, 2, &mem), Ok(vec![want(2 * 8 + 3)]));
        // other sizes, formats, filters, conversions and T3 words did not run (bilinear: E982's
        // fills only)
        for st in [
            [T0_REP | 1 << 27, t1(0, 12, 16, 16), 0x1000, T3_TW],
            [T0_REP | 1 << 27, t1(0, 13, 8, 8), 0x1000, T3_TW],
            [T0_REP | 1 << 27 | 1 << 12, t1(0, 12, 8, 8), 0x1000, T3_TW],
            [T0_REP | 1 << 27, t1(0, 12, 8, 8), 0x1000, T3_TW | 2 << 16],
            [T0_SRGB_BL_STRIDE8, t1(6, 12, 8, 4), 0x1000, T3_ST],
            [0x0800_0e00, t1(6, 12, 16, 4), 0x1000, T3_ST],
        ] {
            assert!(is_open(texel(st, 8, 8, 1, 1, &mem)), "{st:08x?}");
        }
        // bilinear sRGB past the measured words names the records that measured it (E1038)
        for st in [
            [T0_REP | 1 << 27 | 1 << 12, t1(0, 12, 8, 8), 0x1000, T3_TW],
            [T0_SRGB_BL_STRIDE8, t1(6, 12, 8, 4), 0x1000, T3_ST],
        ] {
            let e = texel(st, 8, 8, 1, 1, &mem).unwrap_err();
            assert!(format!("{e:?}").contains("E1038"), "{e:?}");
        }
        // the registers after the first are not known (E723's r11 reads: no model)
        assert!(unknown_after(tw8).is_some());
        assert!(unknown_after([T0_REP, t1(0, 12, 8, 8), 0x1000, T3_TW]).is_none());
    }

    #[test]
    fn etc1_decodes_its_blocks_in_morton_order_with_y_low() {
        // E724: block (bx, by) of an 8 x 8 texture is block by | bx << 1; a block is two dwords,
        // the high word first; the texel at (x, y) of a block is its bit x * 4 + y
        let blocks = [(0x84c2_a06c_u32, 0x0000_ffff_u32), (0x8b45_f2b3, 0x1234_5678)];
        let mem = move |a: u32| {
            let d = (a - 0x1000) / 4;
            let (b, k) = ((d / 2) as usize, d % 2);
            let (hi, lo) = blocks[b.min(1)];
            if k == 0 { hi } else { lo }
        };
        let st = [T0_REP, t1(0, 27, 8, 8), 0x1000, T3_TW];
        let px = |x, y| texel(st, 8, 8, x, y, &mem).unwrap()[0];
        // block 0 at (0, 0): texels (0, 0), (1, 1), (2, 2), (3, 3)
        assert_eq!(
            [px(0, 0), px(1, 1), px(2, 2), px(3, 3)],
            [0xffb2_f6d4, 0xffb2_f6d4, 0xff6e_4c2a, 0xff6e_4c2a]
        );
        // block 1 is at (0, 4): y in the low bit
        assert_eq!(
            [px(0, 4), px(1, 5), px(2, 6), px(3, 7), px(3, 4)],
            [0xffa4_5aff, 0xff3c_00a7, 0xffe1_65ff, 0xffb7_3bff, 0xff3c_00a7]
        );
    }

    #[test]
    fn etc1_is_refused_off_the_sizes_and_state_e724_ran() {
        let mem = |_| 0u32;
        for (w, h) in [(16, 16), (32, 16), (16, 32), (8, 16), (8, 8)] {
            assert!(texel([T0_REP, t1(0, 27, w, h), 0x1000, T3_TW], w, h, 1, 1, &mem).is_ok(), "{w} x {h}");
        }
        for (w, h) in [(4, 4), (32, 32), (64, 16), (16, 8), (64, 64)] {
            assert!(is_open(texel([T0_REP, t1(0, 27, w, h), 0x1000, T3_TW], w, h, 1, 1, &mem)), "{w} x {h}");
        }
        for st in [
            [T0_REP | 1 << 12, t1(0, 27, 8, 8), 0x1000, T3_TW],
            [0x07fc_0000, t1(0, 27, 8, 8), 0x1000, T3_TW],
            [T0_REP, t1(0, 27, 8, 8), 0x1000, T3_TW | 3 << 16],
            [T0_REP, t1(6, 27, 8, 8), 0x1000, T3_ST],
            [T0_REP | 1 << 27, t1(0, 27, 8, 8), 0x1000, T3_TW],
        ] {
            assert!(is_open(texel(st, 8, 8, 1, 1, &mem)), "{st:08x?}");
        }
        // formats 23 to 26 (PVRTC) stay refused
        for f in 23..=26 {
            assert!(is_open(texel([T0_REP, t1(0, f, 8, 8), 0x1000, T3_TW], 8, 8, 1, 1, &mem)), "format {f}");
        }
    }

    #[test]
    fn types_3_and_1_read_a_raster_of_the_width_wrapping_at_the_size() {
        // E725 (8 of 8 held out): texel (x mod w, y mod h) is dword (y mod h) w + (x mod w); E910
        // held it out at 4 x 16 (type 1) and 64 x 8 (both types)
        let mem = |a: u32| 0xd000_0000 | ((a - 0x1000) / 4);
        for ty in [1, 3] {
            let more: &[(u32, u32)] = if ty == 1 { &[(4, 16), (64, 8)] } else { &[(64, 8)] };
            for &(w, h) in [(8, 8), (32, 32), (32, 16), (16, 32)].iter().chain(more) {
                let st = [T0_REP, t1(ty, 12, w, h), 0x1000, T3_TW];
                for (x, y) in [(0, 0), (3, 1), (w - 1, h - 1), (5 % w, h - 2)] {
                    assert_eq!(
                        texel(st, w, h, x, y, &mem),
                        Ok(vec![0xd000_0000 | (y * w + x)]),
                        "{ty} {w}x{h}"
                    );
                }
                // repeat: one texture past the right edge reads column 0
                let past = sample(
                    &Sample {
                        state: st,
                        u: 1.0 + 0.5 / w as f32,
                        v: 0.5 / h as f32,
                        one_d: false,
                        srd: Srd::None,
                        pcf: None,
                        lod: Lod::Flat,
                    },
                    &mut |a| Ok(mem(a)),
                );
                assert_eq!(past, Ok(vec![0xd000_0000]), "{ty} {w}x{h}");
            }
        }
    }

    #[test]
    fn e1065_the_two_size_fit_of_the_name_is_refused_at_the_sizes_it_failed_at() {
        // E1065 (render/closing-r16-tex ty, out/20261114-090305): E1055's N = 39 W + 52 (types 1
        // and 3) and 40 W + 20 (type 4) failed at 8 x 8, 64 x 64 and 64 x 16 in mode 4 (N13 0 of 3,
        // N4 1 of 2: type 4 at 8 x 8 only, not admitted), modes 6 and 7 at 64 x 64 and the
        // quadratic rival too; every state of E1065's rows but the mode 0 references that ran at
        // sizes E725 and E941 measured is refused naming E1065
        let mem = |_| 0u32;
        for (ty, w, h) in [(1, 8, 8), (4, 8, 8), (1, 64, 64), (4, 64, 64), (1, 64, 16)] {
            for m in [4u32, 5, 6, 7] {
                let st = [T0_REP | m << 6, t1(ty, 12, w, h), 0x1000, T3_TW];
                let e = format!("{:?}", texel(st, w, h, 1, 1, &mem).unwrap_err());
                assert!(e.contains("E1065"), "type {ty} {w}x{h} mode {m}: {e}");
            }
        }
        // what held is kept as it was: the 16 x 16 and 32 x 32 mode 4 reads of E1055 (above); the
        // new sizes' mode 0 references (R-W on types 1 and 3, 32 t + s on type 4 at 8 x 8) agree
        // with the sim's raster and block layouts where it already reads those sizes and are not
        // newly admitted
    }

    #[test]
    fn types_1_3_4_and_5_off_what_ran_are_refused() {
        let mem = |_| 0u32;
        for ty in [1, 3] {
            // 128 x 8 ran, but the 64-pixel window read only its first 64 columns (E910); 16 x 16
            // is E1055's (e1055_types_1_3_4_in_u_mode_4_read_a_named_dword_halved)
            for (w, h) in [(4, 4), (64, 32), (8, 16), (128, 8)] {
                assert!(
                    is_open(texel([T0_REP, t1(ty, 12, w, h), 0x1000, T3_TW], w, h, 1, 1, &mem)),
                    "{ty} {w}x{h}"
                );
            }
            for st in [
                [T0_REP | 1 << 12, t1(ty, 12, 8, 8), 0x1000, T3_TW],
                [T0_REP, t1(ty, 13, 8, 8), 0x1000, T3_TW],
                [T0_REP, t1(ty, 12, 8, 8), 0x1000, T3_TW | 2 << 16],
                [T0_REP | 1 << 6, t1(ty, 12, 8, 8), 0x1000, T3_TW],
            ] {
                assert!(is_open(texel(st, 8, 8, 1, 1, &mem)), "{st:08x?}");
            }
        }
        // type 1 at widths that are not powers of two ran at 24 and 40 only (E958)
        assert!(is_open(texel([T0_REP, t1(1, 12, 48, 8), 0x1000, T3_TW], 48, 8, 1, 1, &mem)), "type 1 48x8");
        // type 3 at a 16-bit format ran as format 5 at 4 x 8 and 8 x 8 only (E958)
        for (f, w, h) in [(5, 16, 16), (5, 2, 8), (2, 4, 8), (9, 4, 8)] {
            assert!(
                is_open(texel([T0_REP, t1(3, f, w, h), 0x1000, T3_TW], w, h, 1, 1, &mem)),
                "type 3 format {f} {w}x{h}"
            );
        }
        // type 4: E725's sizes were fitted only, 128 x 8 and 128 x 32 read half their columns
        // (E910), the sizes that are not multiples of 32 ran at 48 x 64, 80 x 64 and 96 x 32 only
        // (E958)
        // (16 x 16 and 32 x 32 are E1055's)
        for (w, h) in [(8, 8), (128, 8), (128, 32), (96, 64), (64, 48), (40, 32)] {
            assert!(
                is_open(texel([T0_REP, t1(4, 12, w, h), 0x1000, T3_TW], w, h, 1, 1, &mem)),
                "type 4 {w}x{h}"
            );
        }
        // type 5: format 12 point-sampled at the sizes of E911 and E942 only (format 9 and 18
        // and the bilinear filter are one explore row each, E942)
        for st in [
            [T0_REP, t1(5, 9, 16, 16), 0x1000, T3_TW],
            [T0_REP, t1(5, 18, 16, 16), 0x1000, T3_TW],
            [T0_REP | 1 << 12 | 1 << 10, t1(5, 12, 16, 16), 0x1000, T3_TW],
            [T0_REP, t1(5, 12, 4, 4), 0x1000, T3_TW],
            [T0_REP, t1(5, 12, 128, 8), 0x1000, T3_TW],
        ] {
            assert!(is_open(texel(st, 16, 16, 1, 1, &mem)), "{st:08x?}");
        }
    }

    #[test]
    fn type_3_pads_its_rows_to_8_dwords_and_type_1_keeps_the_width() {
        // E940 (held out): type 3 at 1, 2 and 4 wide reads dword (y mod h) max(8, w) + (x mod w)
        // (with E910's 4 x 16), type 1 at 1 and 2 wide the width; type 3 at 24 and 40 wide
        // the width, not a power of two above it
        let mem = |a: u32| 0xd000_0000 | ((a - 0x1000) / 4);
        let cases: [(u32, u32, u32, u32); 10] = [
            (3, 4, 16, 8),
            (3, 2, 16, 8),
            (3, 4, 8, 8),
            (3, 4, 32, 8),
            (3, 2, 8, 8),
            (3, 1, 16, 8),
            (1, 2, 16, 2),
            (1, 1, 16, 1),
            (3, 24, 8, 24),
            (3, 40, 8, 40),
        ];
        for (ty, w, h, pitch) in cases {
            let st = [T0_REP, t1(ty, 12, w, h), 0x1000, T3_TW];
            for (x, y) in [(0, 0), (w - 1, 1), (w / 2, h - 1)] {
                assert_eq!(
                    texel(st, w, h, x, y, &mem),
                    Ok(vec![0xd000_0000 | (y * pitch + x)]),
                    "{ty} {w}x{h}"
                );
            }
        }
    }

    #[test]
    fn e958_type_4_rounds_a_partial_block_up_type_1_keeps_the_width_and_type_3_pads_texels() {
        // E958 (held out): type 4 at widths that are not multiples of 32 keeps ceil(w / 32) whole
        // 32 x 32 blocks a block row (H-CEIL, 7 of 7 windows of 48 x 64, 80 x 64 and 96 x 32;
        // the width rounded up to a power of two failed 2, a partial block w mod 32 wide 5)
        let mem = |a: u32| 0xd000_0000 | ((a - 0x1000) / 4);
        for (w, h) in [(48, 64), (80, 64), (96, 32)] {
            let st = [T0_REP, t1(4, 12, w, h), 0x1000, T3_TW];
            for (x, y) in [(0, 0), (w - 1, h - 1), (40, 33 % h), (79 % w, 40 % h), (64 % w, 31)] {
                let want = ((y / 32) * w.div_ceil(32) + x / 32) * 1024 + (y % 32) * 32 + x % 32;
                assert_eq!(texel(st, w, h, x, y, &mem), Ok(vec![0xd000_0000 | want]), "{w}x{h} ({x}, {y})");
            }
        }
        // 80 x 64: block row 1 starts at block 3 (not 4, the power of two's)
        let st = [T0_REP, t1(4, 12, 80, 64), 0x1000, T3_TW];
        assert_eq!(texel(st, 80, 64, 0, 32, &mem), Ok(vec![0xd000_0000 | 3072]));
        // type 1 at 24 and 40 wide reads a raster of the width (2 of 2, not the power of two above)
        for w in [24, 40] {
            let st = [T0_REP, t1(1, 12, w, 8), 0x1000, T3_TW];
            for (x, y) in [(0, 0), (w - 1, 1), (w / 2, 7)] {
                assert_eq!(texel(st, w, 8, x, y, &mem), Ok(vec![0xd000_0000 | (y * w + x)]), "type 1 {w}x8");
            }
        }
        // type 3 at format 5 (B5G6R5, two texels a dword, the low half first): rows max(8, w)
        // texels apart (H-TX8, 2 of 2 at 4 x 8 and 8 x 8; 8 dwords apart failed both), each
        // field widened by repeating its bits, alpha 0xff
        let widen = |v: u32| {
            let (b, g, r) = (v & 31, v >> 5 & 63, v >> 11 & 31);
            (b << 3 | b >> 2) | (g << 2 | g >> 4) << 8 | (r << 3 | r >> 2) << 16 | 0xff << 24
        };
        for w in [4u32, 8] {
            let st = [T0_REP, t1(3, 5, w, 8), 0x1000, T3_TW];
            for (x, y) in [(0, 0), (1, 0), (w - 1, 3), (2, 7)] {
                let k = y * 8.max(w) + x;
                let dw = 0xd000_0000 | (k / 2);
                let want = widen(dw >> (16 * (k & 1)) & 0xffff);
                assert_eq!(texel(st, w, 8, x, y, &mem), Ok(vec![want]), "type 3 format 5 {w}x8 ({x}, {y})");
            }
        }
    }

    #[test]
    fn type_4_stores_32x32_blocks_numbered_row_by_row() {
        // E941 (18 of 18 held-out windows) and E910: texel (x, y) is dword ((y div 32)
        // ceil(w / 32) + (x div 32)) 1024 + (y mod 32) 32 + (x mod 32)
        let mem = |a: u32| 0xd000_0000 | ((a - 0x1000) / 4);
        for (w, h) in [(4, 16), (64, 8), (64, 32), (64, 64), (128, 64), (128, 128), (256, 32)] {
            let st = [T0_REP, t1(4, 12, w, h), 0x1000, T3_TW];
            for (x, y) in [(0, 0), (w - 1, h - 1), (w / 2 + 1, h / 2 + 3), (w / 4, h - 2)] {
                let blk = (y / 32) * w.div_ceil(32) + x / 32;
                let want = blk * 1024 + (y % 32) * 32 + x % 32;
                assert_eq!(texel(st, w, h, x, y, &mem), Ok(vec![0xd000_0000 | want]), "{w}x{h} ({x}, {y})");
            }
        }
        // E941's 128 x 64: block (0, 1) is block 4 (row by row), not 1 (by column) nor 2 (Z)
        let st = [T0_REP, t1(4, 12, 128, 64), 0x1000, T3_TW];
        assert_eq!(texel(st, 128, 64, 0, 32, &mem), Ok(vec![0xd000_0000 | 4096]));
    }

    #[test]
    fn type_5_returns_0xffff_iff_bit_0_of_dword_t_div_8_is_set() {
        // E942 (13 of 13 held out, 8 of 8 where the rival agrees) and E911: texel t = y w + x
        // reads dword floor(t / 8); 0x0000ffff iff its bit 0 is set, else 0
        let tag = |a: u32| 0xd000_0000 | ((a - 0x1000) / 4);
        for (w, h) in [(8, 8), (16, 16), (32, 32), (64, 64), (32, 8), (8, 32), (16, 8)] {
            let st = [T0_REP, t1(5, 12, w, h), 0x1000, T3_TW];
            for (x, y) in [(0, 0), (7, 0), (w - 1, 1), (w / 2, h - 1), (3, h / 2)] {
                let t = y * w + x;
                let want = if (t / 8) & 1 == 1 { 0xffff } else { 0 };
                assert_eq!(texel(st, w, h, x, y, &tag), Ok(vec![want]), "{w}x{h} ({x}, {y})");
            }
        }
        // one dword j stored 0xffffffff among zeros lights texels 8 j to 8 j + 7 (E942)
        let j = 5;
        let one = move |a: u32| if (a - 0x1000) / 4 == j { 0xffff_ffff } else { 0 };
        let st = [T0_REP, t1(5, 12, 16, 16), 0x1000, T3_TW];
        for t in 0..256u32 {
            let want = if t / 8 == j { 0xffff } else { 0 };
            assert_eq!(texel(st, 16, 16, t % 16, t / 16, &one), Ok(vec![want]), "texel {t}");
        }
        // bit 1 alone (0x2) lights nothing: not bit 1 of dword floor(t / 4) (E942's rival)
        let two = |_| 2u32;
        assert_eq!(texel(st, 16, 16, 4, 0, &two), Ok(vec![0]));
    }

    #[test]
    fn e1052_chains_of_a_side_of_1_1d_u16_and_long_sides_read_as_e562s() {
        // E1052 (render/closing-r15-tex chain, out/20261114-073318; fold/sim_points.out): each
        // held-out row at y = 0, 8, 20, 28 (LOD (y >> 2) + c) and x = 5, 50 (u = v = (32 x + 17) /
        // 2048, 1/2 on a side of 1), dword i of the texture 0xd0000000 | i: (W, H, format, 1D, T0,
        // LOD, x, the kept pixel); chain A, u16 in texels, its MIPFILTER blend one 16-bit lerp
        let kept: [(u32, u32, u32, bool, u32, f32, u32, u32); 128] = [
            (1, 32, 12, false, 0x07fc0000, 0.0, 5, 0xd0000002),
            (1, 32, 12, false, 0x07fc0000, 0.0, 50, 0xd0000019),
            (1, 32, 12, false, 0x07fc0000, 2.0, 5, 0xd0000030),
            (1, 32, 12, false, 0x07fc0000, 2.0, 50, 0xd0000036),
            (1, 32, 12, false, 0x07fc0000, 5.0, 5, 0xd000003e),
            (1, 32, 12, false, 0x07fc0000, 5.0, 50, 0xd000003e),
            (1, 32, 12, false, 0x07fc0000, 7.0, 5, 0xd000003e),
            (1, 32, 12, false, 0x07fc0000, 7.0, 50, 0xd000003e),
            (1, 32, 12, false, 0x07fc0000, 0.5, 5, 0xd0000021),
            (1, 32, 12, false, 0x07fc0000, 0.5, 50, 0xd000002c),
            (1, 32, 12, false, 0x07fc0000, 2.5, 5, 0xd0000038),
            (1, 32, 12, false, 0x07fc0000, 2.5, 50, 0xd000003b),
            (1, 32, 12, false, 0x07fc0000, 5.5, 5, 0xd000003e),
            (1, 32, 12, false, 0x07fc0000, 5.5, 50, 0xd000003e),
            (1, 32, 12, false, 0x07fc0000, 7.5, 5, 0xd000003e),
            (1, 32, 12, false, 0x07fc0000, 7.5, 50, 0xd000003e),
            (32, 1, 12, false, 0x07fc0000, 0.0, 5, 0xd0000002),
            (32, 1, 12, false, 0x07fc0000, 0.0, 50, 0xd0000019),
            (32, 1, 12, false, 0x07fc0000, 2.0, 5, 0xd0000030),
            (32, 1, 12, false, 0x07fc0000, 2.0, 50, 0xd0000036),
            (32, 1, 12, false, 0x07fc0000, 5.0, 5, 0xd000003e),
            (32, 1, 12, false, 0x07fc0000, 5.0, 50, 0xd000003e),
            (32, 1, 12, false, 0x07fc0000, 7.0, 5, 0xd000003e),
            (32, 1, 12, false, 0x07fc0000, 7.0, 50, 0xd000003e),
            (32, 1, 12, false, 0x07fc0000, 0.5, 5, 0xd0000021),
            (32, 1, 12, false, 0x07fc0000, 0.5, 50, 0xd000002c),
            (32, 1, 12, false, 0x07fc0000, 2.5, 5, 0xd0000038),
            (32, 1, 12, false, 0x07fc0000, 2.5, 50, 0xd000003b),
            (32, 1, 12, false, 0x07fc0000, 5.5, 5, 0xd000003e),
            (32, 1, 12, false, 0x07fc0000, 5.5, 50, 0xd000003e),
            (32, 1, 12, false, 0x07fc0000, 7.5, 5, 0xd000003e),
            (32, 1, 12, false, 0x07fc0000, 7.5, 50, 0xd000003e),
            (32, 1, 12, false, 0x067c0000, 0.0, 5, 0xd0000002),
            (32, 1, 12, false, 0x067c0000, 0.0, 50, 0xd0000019),
            (32, 1, 12, false, 0x067c0000, 2.0, 5, 0xd0000021),
            (32, 1, 12, false, 0x067c0000, 2.0, 50, 0xd000002c),
            (32, 1, 12, false, 0x067c0000, 5.0, 5, 0xd000003c),
            (32, 1, 12, false, 0x067c0000, 5.0, 50, 0xd000003d),
            (32, 1, 12, false, 0x067c0000, 7.0, 5, 0xd000003e),
            (32, 1, 12, false, 0x067c0000, 7.0, 50, 0xd000003e),
            (32, 16, 9, false, 0x07fc0000, 0.0, 5, 0x0000d000),
            (32, 16, 9, false, 0x07fc0000, 0.0, 50, 0x000000e9),
            (32, 16, 9, false, 0x07fc0000, 2.0, 5, 0x00000140),
            (32, 16, 9, false, 0x07fc0000, 2.0, 50, 0x0000d000),
            (32, 16, 9, false, 0x07fc0000, 5.0, 5, 0x00000155),
            (32, 16, 9, false, 0x07fc0000, 5.0, 50, 0x00000155),
            (32, 16, 9, false, 0x07fc0000, 7.0, 5, 0x00000155),
            (32, 16, 9, false, 0x07fc0000, 7.0, 50, 0x00000155),
            (32, 16, 9, false, 0x07fc0000, 0.5, 5, 0x00000101),
            (32, 16, 9, false, 0x07fc0000, 0.5, 50, 0x0000013a),
            (32, 16, 9, false, 0x07fc0000, 2.5, 5, 0x00000150),
            (32, 16, 9, false, 0x07fc0000, 2.5, 50, 0x0000d000),
            (32, 16, 9, false, 0x07fc0000, 5.5, 5, 0x00000155),
            (32, 16, 9, false, 0x07fc0000, 5.5, 50, 0x00000155),
            (32, 16, 9, false, 0x07fc0000, 7.5, 5, 0x00000155),
            (32, 16, 9, false, 0x07fc0000, 7.5, 50, 0x00000155),
            (16, 64, 9, false, 0x07fc0000, 0.0, 5, 0x0000d000),
            (16, 64, 9, false, 0x07fc0000, 0.0, 50, 0x000001d2),
            (16, 64, 9, false, 0x07fc0000, 2.0, 5, 0x0000d000),
            (16, 64, 9, false, 0x07fc0000, 2.0, 50, 0x0000029d),
            (16, 64, 9, false, 0x07fc0000, 5.0, 5, 0x000002aa),
            (16, 64, 9, false, 0x07fc0000, 5.0, 50, 0x0000d000),
            (16, 64, 9, false, 0x07fc0000, 7.0, 5, 0x000002ab),
            (16, 64, 9, false, 0x07fc0000, 7.0, 50, 0x000002ab),
            (16, 64, 9, false, 0x07fc0000, 0.5, 5, 0x00000202),
            (16, 64, 9, false, 0x07fc0000, 0.5, 50, 0x0000d000),
            (16, 64, 9, false, 0x07fc0000, 2.5, 5, 0x000002a0),
            (16, 64, 9, false, 0x07fc0000, 2.5, 50, 0x000002a7),
            (16, 64, 9, false, 0x07fc0000, 5.5, 5, 0x000002ab),
            (16, 64, 9, false, 0x07fc0000, 5.5, 50, 0x000002ab),
            (16, 64, 9, false, 0x07fc0000, 7.5, 5, 0x000002ab),
            (16, 64, 9, false, 0x07fc0000, 7.5, 50, 0x000002ab),
            (32, 16, 9, false, 0x07fc0200, 0.5, 5, 0x00006881),
            (32, 16, 9, false, 0x07fc0200, 0.5, 50, 0x00000112),
            (32, 16, 9, false, 0x07fc0200, 2.5, 5, 0x00000148),
            (32, 16, 9, false, 0x07fc0200, 2.5, 50, 0x0000d000),
            (32, 16, 9, false, 0x07fc0200, 5.5, 5, 0x00000155),
            (32, 16, 9, false, 0x07fc0200, 5.5, 50, 0x00000155),
            (32, 16, 9, false, 0x07fc0200, 7.5, 5, 0x00000155),
            (32, 16, 9, false, 0x07fc0200, 7.5, 50, 0x00000155),
            (64, 32, 12, false, 0x07fc0000, 0.0, 5, 0xd0000026),
            (64, 32, 12, false, 0x07fc0000, 0.0, 50, 0xd0000749),
            (64, 32, 12, false, 0x07fc0000, 2.0, 5, 0xd0000a02),
            (64, 32, 12, false, 0x07fc0000, 2.0, 50, 0xd0000a74),
            (64, 32, 12, false, 0x07fc0000, 5.0, 5, 0xd0000aa8),
            (64, 32, 12, false, 0x07fc0000, 5.0, 50, 0xd0000aa9),
            (64, 32, 12, false, 0x07fc0000, 7.0, 5, 0xd0000aaa),
            (64, 32, 12, false, 0x07fc0000, 7.0, 50, 0xd0000aaa),
            (256, 32, 12, false, 0x07fc0000, 0.0, 5, 0xd000012c),
            (256, 32, 12, false, 0x07fc0000, 0.0, 50, 0xd0001cc9),
            (256, 32, 12, false, 0x07fc0000, 2.0, 5, 0xd0002822),
            (256, 32, 12, false, 0x07fc0000, 2.0, 50, 0xd000299c),
            (256, 32, 12, false, 0x07fc0000, 5.0, 5, 0xd0002aa0),
            (256, 32, 12, false, 0x07fc0000, 5.0, 50, 0xd0002aa6),
            (256, 32, 12, false, 0x07fc0000, 7.0, 5, 0xd0002aac),
            (256, 32, 12, false, 0x07fc0000, 7.0, 50, 0xd0002aad),
            (256, 32, 12, false, 0x07fc0000, 1.5, 5, 0xd0002822),
            (256, 32, 12, false, 0x07fc0000, 1.5, 50, 0xd000299c),
            (256, 32, 12, false, 0x07fc0000, 3.5, 5, 0xd0002a82),
            (256, 32, 12, false, 0x07fc0000, 3.5, 50, 0xd0002a99),
            (256, 32, 12, false, 0x07fc0000, 6.5, 5, 0xd0002aac),
            (256, 32, 12, false, 0x07fc0000, 6.5, 50, 0xd0002aad),
            (256, 32, 12, false, 0x07fc0000, 8.5, 5, 0xd0002aae),
            (256, 32, 12, false, 0x07fc0000, 8.5, 50, 0xd0002aae),
            (64, 1, 12, true, 0x07fc0000, 0.0, 5, 0xd0000005),
            (64, 1, 12, true, 0x07fc0000, 0.0, 50, 0xd0000032),
            (64, 1, 12, true, 0x07fc0000, 2.0, 5, 0xd0000061),
            (64, 1, 12, true, 0x07fc0000, 2.0, 50, 0xd000006c),
            (64, 1, 12, true, 0x07fc0000, 5.0, 5, 0xd000007c),
            (64, 1, 12, true, 0x07fc0000, 5.0, 50, 0xd000007d),
            (64, 1, 12, true, 0x07fc0000, 7.0, 5, 0xd000007e),
            (64, 1, 12, true, 0x07fc0000, 7.0, 50, 0xd000007e),
            (64, 1, 12, true, 0x07fc0000, 0.5, 5, 0xd0000042),
            (64, 1, 12, true, 0x07fc0000, 0.5, 50, 0xd0000059),
            (64, 1, 12, true, 0x07fc0000, 2.5, 5, 0xd0000070),
            (64, 1, 12, true, 0x07fc0000, 2.5, 50, 0xd0000076),
            (64, 1, 12, true, 0x07fc0000, 5.5, 5, 0xd000007e),
            (64, 1, 12, true, 0x07fc0000, 5.5, 50, 0xd000007e),
            (64, 1, 12, true, 0x07fc0000, 7.5, 5, 0xd000007e),
            (64, 1, 12, true, 0x07fc0000, 7.5, 50, 0xd000007e),
            (64, 1, 12, true, 0x07e60000, 0.0, 5, 0xd0000005),
            (64, 1, 12, true, 0x07e60000, 0.0, 50, 0xd0000032),
            (64, 1, 12, true, 0x07e60000, 2.0, 5, 0xd0000061),
            (64, 1, 12, true, 0x07e60000, 2.0, 50, 0xd000006c),
            (64, 1, 12, true, 0x07e60000, 5.0, 5, 0xd0000070),
            (64, 1, 12, true, 0x07e60000, 5.0, 50, 0xd0000076),
            (64, 1, 12, true, 0x07e60000, 7.0, 5, 0xd0000070),
            (64, 1, 12, true, 0x07e60000, 7.0, 50, 0xd0000076),
        ];
        let mem = |a: u32| 0xd000_0000 | ((a - 0x1000) / 4);
        for (w, h, fmt, one_d, t0, lod, x, want) in kept {
            let c = (32 * x + 17) as f32 / 2048.0;
            let (u, v) = (if w == 1 { 0.5 } else { c }, if h == 1 || one_d { 0.5 } else { c });
            let got = sample(
                &Sample {
                    state: [t0, t1(0, fmt, w, h), 0x1000, T3_TW],
                    u,
                    v,
                    one_d,
                    srd: Srd::None,
                    pcf: None,
                    lod: Lod::Value(lod),
                },
                &mut |a| Ok(mem(a)),
            );
            assert_eq!(got, Ok(vec![want]), "{w}x{h} format {fmt} 1D {one_d} T0 {t0:08x} LOD {lod} x {x}");
        }
        // a 1D chain taller than one texel, a u16 chain at another size, a blend of 8-bit levels
        let st = |t0: u32, fmt: u32, w: u32, h: u32| [t0, t1(0, fmt, w, h), 0x1000, T3_TW];
        for (s, one_d) in [
            (st(0x07fc_0000, 12, 64, 4), true),
            (st(0x07fc_0000, 9, 64, 16), false),
            (st(0x07fc_0200, 0, 32, 16), false),
        ] {
            let r = sample(
                &Sample { state: s, u: 0.3, v: 0.3, one_d, srd: Srd::None, pcf: None, lod: Lod::Value(1.5) },
                &mut |a| Ok(mem(a)),
            );
            assert!(is_open(r), "{s:08x?}");
        }
    }

    #[test]
    fn e1055_types_1_3_4_in_u_mode_4_read_a_named_dword_halved() {
        // E1055 (render/closing-r15-tex ty, out/20261114-073318) and E1039 (r14-tex addr5): with
        // u mode 4 at 32 x 32 and 16 x 16 every pixel is the dword N + (x mod W) with each byte
        // halved, rounded up, the rows alike: N = 1300 at 32 x 32 (types 1, 3, 4), 676 (types 1,
        // 3) and 660 (type 4) at 16 x 16; (type, W, u, the kept pixel)
        let kept: [(u32, u32, f32, u32); 50] = [
            (1, 32, 1.015625, 0x6800030a),
            (1, 32, 1.234375, 0x6800030e),
            (1, 32, 1.453125, 0x68000311),
            (1, 32, 1.671875, 0x68000315),
            (1, 32, 1.890625, 0x68000318),
            (1, 32, 1.109375, 0x6800030c),
            (1, 32, 1.328125, 0x6800030f),
            (1, 32, 1.546875, 0x68000313),
            (1, 32, 1.765625, 0x68000316),
            (1, 32, 1.984375, 0x6800031a),
            (3, 32, 1.015625, 0x6800030a),
            (3, 32, 1.234375, 0x6800030e),
            (3, 32, 1.453125, 0x68000311),
            (3, 32, 1.671875, 0x68000315),
            (3, 32, 1.890625, 0x68000318),
            (3, 32, 1.109375, 0x6800030c),
            (3, 32, 1.328125, 0x6800030f),
            (3, 32, 1.546875, 0x68000313),
            (3, 32, 1.765625, 0x68000316),
            (3, 32, 1.984375, 0x6800031a),
            (4, 32, 1.015625, 0x6800030a),
            (4, 32, 1.234375, 0x6800030e),
            (4, 32, 1.453125, 0x68000311),
            (4, 32, 1.671875, 0x68000315),
            (4, 32, 1.890625, 0x68000318),
            (4, 32, 1.109375, 0x6800030c),
            (4, 32, 1.328125, 0x6800030f),
            (4, 32, 1.546875, 0x68000313),
            (4, 32, 1.765625, 0x68000316),
            (4, 32, 1.984375, 0x6800031a),
            (1, 16, -1.46875, 0x68000156),
            (1, 16, -1.03125, 0x6800015a),
            (1, 16, -0.59375, 0x68000155),
            (1, 16, -0.15625, 0x68000159),
            (1, 16, 0.28125, 0x68000154),
            (1, 16, 0.71875, 0x68000158),
            (1, 16, 1.15625, 0x68000153),
            (1, 16, 1.59375, 0x68000157),
            (1, 16, 2.03125, 0x68000152),
            (1, 16, 2.46875, 0x68000156),
            (4, 16, 1.03125, 0x6800014a),
            (4, 16, 1.46875, 0x6800014e),
            (4, 16, 1.90625, 0x68000151),
            (4, 16, 1.34375, 0x6800014d),
            (4, 16, 1.78125, 0x68000150),
            (4, 16, 1.21875, 0x6800014c),
            (4, 16, 1.65625, 0x6800014f),
            (4, 16, 1.09375, 0x6800014b),
            (4, 16, 1.53125, 0x6800014e),
            (4, 16, 1.96875, 0x68000152),
        ];
        let mem = |a: u32| 0xd000_0000 | ((a - 0x1000) / 4);
        for (ty, w, u, want) in kept {
            for v in [0.1f32, 0.7] {
                let got = sample(
                    &Sample {
                        state: [T0_REP | 4 << 6, t1(ty, 12, w, w), 0x1000, T3_TW],
                        u,
                        v,
                        one_d: false,
                        srd: Srd::None,
                        pcf: None,
                        lod: Lod::Flat,
                    },
                    &mut |a| Ok(mem(a)),
                );
                assert_eq!(got, Ok(vec![want]), "type {ty} {w}x{w} u {u} v {v}");
            }
        }
        // their mode 0 references: types 1 and 3 a raster of the width, type 4 its 32 x 32 block
        for (ty, w) in [(1, 16), (3, 16), (4, 16), (1, 32), (3, 32), (4, 32)] {
            let stride = if ty == 4 { 32 } else { w };
            let st = [T0_REP, t1(ty, 12, w, w), 0x1000, T3_TW];
            assert_eq!(texel(st, w, w, 3, 5, &mem), Ok(vec![0xd000_0000 | (5 * stride + 3)]), "{ty} {w}");
        }
        // modes 5, 6 and 7, another size and mode 4 with another T0 stay open (E1055, Q177)
        for st in [
            [T0_REP | 5 << 6, t1(1, 12, 16, 16), 0x1000, T3_TW],
            [T0_REP | 6 << 6, t1(4, 12, 16, 16), 0x1000, T3_TW],
            [T0_REP | 7 << 6, t1(1, 12, 32, 32), 0x1000, T3_TW],
            [T0_REP | 4 << 6, t1(1, 12, 8, 8), 0x1000, T3_TW],
            [T0_REP | 4 << 6 | 1 << 12, t1(1, 12, 16, 16), 0x1000, T3_TW],
        ] {
            let e = format!("{:?}", texel(st, 16, 16, 1, 1, &mem).unwrap_err());
            assert!(e.contains("Q177") || e.contains("T0 0x"), "{st:08x?} {e}");
        }
    }
}
