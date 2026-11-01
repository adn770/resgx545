+++
id = "E466"
claim = "Bits 26:24 of CR_ISP_ZLSCTL select the format of the stored depth: 0 the 32-bit float (512 dwords a 32 x 16 tile), 1 the 24-bit unsigned integer round(z * 0xffffff) (512 dwords a tile, 786432 of 786432 pixels exact), 2 a 16-bit integer, round(z * 0xffffff) >> 8, with the rows y even and odd of a column in the low and high half of a dword (256 dwords a tile, 786432 of 786432 exact); 4 and 7 store no depth without a stencil buffer, and 3, 5 and 6 store other layouts; bit 19 stores the depth negated (shown by the three most frequent stored dwords only); bits 2 and 18 enable the depth store and bit 17 the stencil store (bit 17 from E411; here clearing it changes nothing without a stencil buffer)"
unit = "zls"
method = "probes/zls/store-format.toml (store-format.sh) on the laptop (direct cable), linux fork 6ee9501832af: sgxfive-test tri --tri-full --tri-z (a triangle over the whole 1024 x 768 target with a depth that ramps across x in one run and across y in the other, so that a stored dword names its pixel), --depth with the buffer filled with 0xdeadbeef, G (bits 11:3) 33, the control 0x0017110c with bits 26:24 set to each of 0 to 7, with bit 19, with bits 2, 17 and 18 cleared, and with a stencil buffer (--stencil), reduced on the laptop (python3); one run of each case, each dataset ran once, after one run by hand of the script (outside the data) whose reduction was changed afterwards (see the text); the dataset holds output.txt, kernel.log, env.toml and the script and no raw dumps, so the counts are the script's own at run time and cannot be recomputed from the stored data"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["zls-store-format"]
terms = ["CR_ISP_ZLSCTL", "FRAG_FLAGS.DEPTH_BUFFER", "FRAG_FLAGS.STENCIL_BUFFER"]
+++

**What runs.** The triangle (0,0), (3W,0), (0,3H) of `tri --tri-full` covers the 1024 x 768 target
(786432 pixels; the script keeps only the job, depth and stencil lines of the tool's output, so
the tool's own pixel check is not in the data); `--tri-z 0.25,0.75,0.25` gives it the depth 0.25 +
0.5 * x / (3 * 1024) at the pixel's x, and `0.25,0.25,0.75` the same across y, with the depth test
less (`blk:1 = 0x00400200`). The depth buffer is filled with 0xdeadbeef before the job, so a dword
that is not 0xdeadbeef afterwards was stored. Each case is one job per ramp; the address of every
stored dword follows E465 (G = 33 puts no two tiles at one address). One run of each case; no case
was repeated.

**What was chosen after the data.** The script was run once by hand before the campaign (outside
the data, debug/phase11/sf.out). There the 16-bit store was compared with round(z * 65535) and
floor(z * 65535), both inexact (the first off by -1 at 122563 pixels, the second by 0 and 1 at
513587 and 272845), and the in-tile order and the half of a dword of the 16-bit format were
already in the script. The campaign script then added round(z * 0xffffff) >> 8 and floor(z *
65536), which fit 786432 of 786432. So the 16-bit formula is a fit to this data's twin and "786432
of 786432" is an in-sample fit, not a prediction; the 16-bit address function was fitted at G = 33
only.

**Results**, control 0x0017110c with the named bits changed (the dataset's output.txt has every
line):

- none (format 0): 786432 dwords in 1536 tiles of 512 dwords, the float z of the ramp at 786432 of
  786432 pixels within 1e-5.
- Bits 26:24 = 1: 786432 dwords, 512 a tile, round(z * 0xffffff): the stored dword minus it is 0
  at 786432 of 786432 pixels (minus floor(z * 0xffffff): 0 at 333955 and 1 at 452477).
- Bits 26:24 = 2: 393216 dwords in 768 tiles of 256 dwords, two 16-bit values per dword, the pixel
  of the even row in bits 15:0 and the odd row below it in bits 31:16; the value is round(z *
  0xffffff) >> 8, which is also floor(z * 65536) (difference 0 at 786432 of 786432; minus round(z
  * 65535) is -1 at 122563).
- Bits 26:24 = 3: 965120 dwords, last dword 1023999 (1885 slots of 512), scrambled (a packed
  layout; first dwords 80355500 200000be aa00be80).
- Bits 26:24 = 4 and 7: 0 dwords, nothing stored without a stencil buffer.
- Bits 26:24 = 5: 96580 dwords, 1508 slots, other packed words (first 9d15551f aa801556 903e800a
  3f924924).
- Bits 26:24 = 6: 86084 dwords, 1536 slots, other packed words (first 9d15553f aa801556 903e800a
  3f924924).
- Bit 19: 786432 dwords, as format 0; the three most frequent dwords (be800aaa, be802000 and
  be803555, 768 times each, 1674 distinct values) have the sign bit set. The script did not
  compare the buffer with -z or with the buffer of format 0, so "the ramp negated" is shown by
  those three dwords and by E411's -1.0 for bit 19, not for the whole buffer.
- Bit 19 with 26:24 = 1 or 2: as formats 1 and 2; the three most frequent dwords are positive
  integers (00400555, 00401000 and 00401aaa; 40054005, 40104010 and 401a401a), like the first
  dwords of the formats without bit 19. The buffers were not compared, so "no sign" rests on those
  dwords.
- Bit 2 cleared: 0 dwords, nothing. Bit 18 cleared: 0 dwords, the depth store is off.
- Bit 17 cleared: 786432 dwords, as format 0 (there is no stencil buffer, so it shows nothing
  about the stencil store, which is E411's: clearing bit 17 stopped it).

With a stencil buffer (`--stencil`: render flag 0x100 and both stencil bases, bit 31 set) the
stencil store is 196608 dwords for formats 0, 1 and 2: 128 dwords a tile (one byte a pixel), at the
same tile pitch as the depth (last dword 208639 = (47 * 34 + 31) * 128 + 127); the script prints
the first 4 stencil dwords, which are 0 (the buffer's other dwords were not printed). Format 3
stores 965120 depth dwords and 17920 stencil dwords, format 4 stores 245760 depth dwords (768
slots) and no stencil dword, format 5 96580 and 1792, format 6 86084 and none, format 7 18432
depth dwords (768 slots) and none. So the formats 3 to 7 pack depth and stencil together [infer:
the counts per tile (1885 / 1536 slots, 160 and 12 dwords a tile for 4 and 7) are not a plain
multiple of one value]; their layouts are not decoded (Q120).

**The buffer's end.** The script's buffer is 1000 pages, 1024000 dwords. Format 3's last stored
dword, 1023999, is the last dword of the buffer and format 5's, 1023423, is 576 dwords short of it,
so the 965120 and 96580 counts may be cut by the buffer and not by the format; both are lower
bounds. The jobs report ok and kernel.log has no fault line (Q120).

**The 16-bit order.** Inside a 256-dword tile of the 16-bit format, the dword index has the bits x0
y1 x1 y2 x2 y3 x3 x4 from the lowest (x and y the pixel's offsets in the 32 x 16 tile): the 32-bit
order of E465 with y0 removed. y0 chooses the half of the dword, the even row in bits 15:0 and the
odd row in bits 31:16. The tile pitch is the same as for the 32-bit formats, 256 dwords a slot of
the tile's number ty * (G + 1) + tx. The script (addr16) fitted it at 786432 of 786432 pixels at G
= 33 only. The ">> 8" form over floor(z * 65536) is told apart by E411, not by this ramp (they
agree on 0.25 to 0.75): E411's clear value 1.0 stored as 0xffffffff (bit 25 set), both halves
0xffff, where floor(z * 65536) would be 0x10000 and overflow.

**What it shows.** Bits 26:24 are a field choosing the stored depth format, three of whose values
are plain: float, 24-bit and 16-bit integers (both integers are the float rounded as above), the
16-bit one with a tile of 256 dwords. Bit 19 negates the stored float; with the integer formats it
changes nothing seen. Bits 2 and 18 enable the depth store, bit 17 the stencil store (E411).

**What it does not show.** The layouts of formats 3 to 7 (Q120); what bit 19 does with the integer
formats; whether the integer formats round the hardware's float or its internal value (the same at
the 786432 pixels); the stencil store's in-tile order (the first 4 stencil dwords were 0, Q121);
a comparison of the bit 19 buffers with the buffers without it.

**Recompute, 2026-11-08 (11.24).** The measurements above are unchanged. E490 ran the script again
with the depth dumps of its parts A and B kept (the control's formats 0 to 7 and bit 19) and
recomputed from them with a separately written script: format 0 within 1e-5 of the geometry's z at
786432 of 786432 pixels, format 1 round(z * 0xffffff) at 786432 of 786432 (z the float format 0
stores at that pixel; floor, 333955), the same counts as above for formats 3 to 7 (965120, 96580 and
86084 dwords for 3, 5 and 6 in the x ramp, the y ramp storing 965120, 84480 and 73760, and format 3
reaching the last dword of the buffer, so 965120 is a lower bound; none for 4 and 7), and bit 19
stores -z at 786432 of 786432 pixels with the float format (the three frequent dwords above were the
only evidence before). For format 2 the layout was derived from the dumps alone, the halves of every
dword decoded to pixels: dword k of a tile = lx0, ly1, lx1, ly2, lx2, ly3, lx3, lx4 from the lowest
bit, the half = ly0, the same in 512 of 512 slots of every tile, at G = 33 only. The stored value of
format 2 (round(z * 0xffffff) >> 8, fitted after the first run's twin and told apart from floor(z *
65536) only by E411's clear value) was not compared again: the halves were decoded to pixels, not
checked against a formula. Not decoded: formats 3, 5 and 6, the stencil dumps (not kept), and bit 19
with a negative depth for formats 1 and 2: with the positive ramp bit 19 changes no dword of formats
1 and 2 (the dumps are byte-identical to the dumps without it, E490).
