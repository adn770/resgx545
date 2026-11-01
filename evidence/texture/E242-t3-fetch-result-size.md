+++
id = "E242"
claim = "T3 bits 26:23 do not change what a single fetch writes (pa0 in all 21 cases, and pa0 to pa3 for f32 channels), and with two fetches in one primary program the second fetch's texel lands in the primary attribute numbered by the first fetch's field for the values 0, 1, 2, 3, 4 and 6, after the first fetch's own dwords (over them at 0)"
unit = "texture"
method = "the probes texture-fetch-t3size-pa0 to pa3 and texture-fetch-tex2-pa0 to pa7 of probes/texture/fetch.toml (pds_tex_t3.s and pds_tex2.s, one probe a primary attribute read back), on the laptop with the linux fork and the debug option on, one run (no follow-up run)"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["texture-fetch"]
terms = ["T3.DATA_SIZE", "T3.CONVERT", "DOUTI0.LAST_FETCH", "DOUTU1.WAIT_FETCH"]
+++

**What runs.** The triangle job's primary PDS program is replaced by one that issues the
iteration and fetch of a 16x16 RGBA8888 texture, and a pixel shader that stores one primary
attribute to o0, a probe a register. The first texture's dwords are 0xD0000000 | i and the second
texture's, 0x4000 bytes on in the scratch buffer, 0xD0001000 | i.

- `t3size`: one fetch (DOUTI0 0x46012201) with T3 = 0x800 | field << 23 | conversion, where the
  conversion is none (0), f16 pairs (0x20000) or f32 channels (0x30000) and the field is 0, 1,
  2, 3, 4, 8 and 15 (21 cases), pa0 to pa3 read back.
- `tex2`: two fetches (DOUTI0 0x06012201 then 0x46012201), the second with T3 0x00800800 (field
  1, no conversion) and the first with the T3 of the eight cases: field 1 as the control, then
  none with field 0, 2 and 3, and f32 channels with field 1, 2, 4 and 6; pa0 to pa7 read back.

**Results.** One run of the table; the baseline triangle before and after every probe was
clean.

- One fetch. pa0 holds the same classes in all seven field values of the none conversion, of the
  f16 pairs and of the f32 channels (the first texel, its two half floats, and the f32
  channel); for f32 channels pa0 to pa3 are the same in all seven field values (pa1 0.0 on all
  1062 triangle pixels, pa3 0x43500000). The registers past what the fetch writes differ between
  cases by a few pixels without following the field (pa1 in the none conversion: 1048 to 1052
  pixels of 0.0 and 3 to 5 pixels of other values; pa2 in the none and f16 conversions: the
  share of each value changes from case to case), which fits registers left over from other jobs
  **[infer]**.
- Two fetches. The second texel (the 0x1000 in the low half of its dwords) is in:

| first fetch | field | register holding the second texel | first fetch's dwords |
|-------------|-------|------------------------------------|----------------------|
| none | 0 | pa0 | overwritten |
| none | 1 | pa1 | pa0 |
| none | 2 | pa2 | pa0 |
| none | 3 | pa3 | pa0 |
| f32 channels | 1 | pa1 | pa0 (0.0), pa2 and pa3 |
| f32 channels | 2 | pa2 | pa0 and pa1 (0.0), pa3 |
| f32 channels | 4 | pa4 | pa0 and pa1 (0.0), pa2 and pa3 |
| f32 channels | 6 | pa6 | pa0 and pa1 (0.0), pa2 and pa3 |

  With f32 channels and field 1 the second texel is written over the channel at pa1 and the
  channels at pa2 and pa3 stay; with field 2 it is written over pa2 and pa3 stays. The rows for
  field 4 and 6 compare whole images: pa4 with field 4 and pa6 with field 6 are the second
  texel's image of the control case (pa1, field 1) pixel for pixel, 0 of 4096 pixels differ. In
  every other case pa4 and pa6 also hold values of the second texture's pattern, but differ from
  that image in 622 to 1000 of the 1062 triangle pixels, which fits registers left over from
  other jobs **[infer]**. pa5 and pa7 hold constants that no fetch wrote (0x99aabbcc, 0xaaaa9465
  and others).

**What it shows.** In this table the field makes the second fetch write at the primary attribute
numbered by the field's value, whatever the first fetch's conversion wrote: a field shorter than the
conversion's four f32 channels lets the second texel overwrite them. With one fetch nothing follows
the first, so the field shows nothing, which is what the `t3size` cases give. We read the field as
the size in dwords of a fetch's result among the primary attributes **[infer]**.

**Not shown.** The values 8 and 15 of the field in a two-fetch program. A second fetch whose
own field is varied. Any variation of LAST_FETCH or WAIT_FETCH, which the table leaves as they are.
The data come from one run.