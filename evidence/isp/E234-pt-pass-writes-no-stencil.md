+++
id = "E234"
claim = "A punch-through pass writes no stencil: with a second, opaque object that draws only where the stencil equals 0x55, it draws nowhere after a punch-through object whose depth-pass stencil op is replace, under atst8 fb, optdwd and each with twosided, though it draws over the whole of an opaque object with that op; the punch-through object draws alike under all eight stencil compares, and atst8 right after pcoeff draws nothing while one nop between them lets it draw"
unit = "isp"
method = "the probes isp-punch-through-stencil-ptread-* of probes/isp/punch-through-stencil.toml (two objects, the second added by the host: opaque, blue, ISP0 0x01d00355, depth always, stencil compare equal to 0x55) and the ptst-never and ptst-always probes, one probe a case, fenced, on the laptop with the linux fork and the debug option on, one run (no follow-up run)"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["isp-punch-through-stencil"]
terms = ["ISP0", "FEEDBACK_CTL.ENABLE"]
+++

**What runs.** The first object is one copy of the triangle with stencil reference 0x55, ISP word
2 at compare always with the depth-pass op replace (0x0e02ffff) or keep (0x0e00ffff). It is
either opaque (green, ISP0 0x00400355; the controls) or punch-through (ISP0 0x08400355, the
shader of E226 ending in `atst8 ... fb` with control word 0xe001, or `optdwd`, or `twosided`
with each). The second object, the same triangle shape as the second copy, is opaque, blue
(0xff0000ff), depth test always, stencil compare equal, reference 0x55: it draws where the
first object wrote 0x55 to the stencil. Three more groups: the punch-through scene of five copies
alone (as E226) with ISP word 2 at each stencil compare 1 to 6 (`ptread-alone-cmp*`) and at never
and always (`ptst-never`, `ptst-always`); and `ptread-gap-*`, the scene with ISP word 2 at 255,
the `atst8` straight after `pcoeff` or with a `nop` between them.

**Results.** One run; every baseline before and after a probe was clean (0 of 4096 pixels).

| first object | depth-pass op | the image |
|--------------|---------------|-----------|
| opaque (control) | replace | 1062 pixels of blue (0xff0000ff), 3034 background |
| opaque (control) | keep | 1062 pixels of green, no blue |
| punch-through, `fb` | replace | 1062 pixels of the first object (0x00000000), no blue |
| punch-through, `optdwd` | replace | the same |
| punch-through, `twosided, fb` | replace | the same |
| punch-through, `twosided, optdwd` | replace | the same |
| punch-through, `fb` | keep | the same |

- The five-copy punch-through scene alone drew 2998 pixels of background, 1062 of 0x00000000 and
  36 of 0x3d800000 under every stencil compare, never, 1 to 6 and always (8 probes).
- `atst8` straight after `pcoeff` drew nothing: 4096 pixels of the background. With a `nop`
  between them the scene drew the same 1062 and 36 pixels.

**What it shows.** An opaque object's stencil is read back exactly by the second object, so the
host works. A punch-through object leaves no 0x55 for it to find, in any of the four `atst8`
forms, so in this setup the punch-through pass neither tests nor writes the ISP stencil, and
`twosided` and `optdwd` act on nothing that the stencil shows. The `atst8` straight after
`pcoeff` loses the feedback and the object is dropped; reading the coefficient write before it
lands is our guess **[infer]**, and probes keep a gap there.

**Not shown.** Other stencil ops than replace and keep; a second object with another stencil
test; punch-through with other ISP0 bits or pass type 5. What `twosided` and `optdwd` do remains
open. The data come from one run.
