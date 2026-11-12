+++
id = "E406"
claim = "With ISP word 0 bit 26 or 27 (0x05d00200 or 0x09d00200), CR_REG_0148 (render details dword 9) bit 0 and the state block's word 4 at 0x00030001 (PDS_SIZE 3, one data row), a shader writing o0 to o7 with a tag in each leaves o0 on its own pixel and a tag-5 word on other pixels (tags 1 and 5), which is the OR of o0 and o3, not o4 (E880), and o1 to o3 (tags 2 to 4) on no pixel at all, in 27 of 27 jobs, where the plain job shows o1 to o3 on 447 to 600 other pixels; with the data rows at 2 to 4 the pattern is tags 1, 3, 5 and 7 and at 5 to 7 the job hangs; no single flip of 1797 jobs over PDS_SIZE, the VDM stream, the state block and 20 render details words gives the setup's pattern, three give the tags 1, 3, 5, 7 pattern [corrected 2026-11-12, see Correction]"
unit = "usse"
method = "probes/usse/output-room.toml, output-room-vdm.toml, output-room-blk.toml, output-room-rd.toml, output-room-bit15.toml, output-room-isp0.toml, output-room-combos.toml, output-room-four.toml, output-room-seq.toml and output-room-rows.toml, and probes/pbe/pack-floats-room.toml on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: the shader of usse/templates/pix_tags_x.s (or _y: o0 to o7 each the pixel's own x or y float with the register's number plus one in the low 16 bits) as the triangle's pixel program with the iteration of pds_iter_xy.s, every pixel read; output_room.py counts, per tag, the pixels that carry it and those that carry it on their own pixel (1797 jobs, 222 hung); the pack-floats probes of 11.14 under the setup, 30 probes"
tiers = ["HW"]
date = "2026-11-07"
data = ["usse-output-room", "usse-output-room-vdm", "usse-output-room-blk", "usse-output-room-rd", "usse-output-room-bit15", "usse-output-room-isp0", "usse-output-room-combos", "usse-output-room-four", "usse-output-room-seq", "usse-output-room-rows", "pbe-pack-floats-room"]
terms = ["PDS_SIZE.BITS17_16", "SIDEBAND.PACKMODE", "PACKMODE", "CR_REG_0148", "ISP0"]
+++

**The plain job.** With the shader of tags and the state block's word 4 as the tool builds it
(0x00030001 in the PDS_SIZE tables, which set it), o0 reaches its own pixel on 905 to 993 of the
triangle's 1062 pixels and o1 to o3 reach pixels that are not their own (tag 2 on 447 to 516, tag 3
on 31 to 85, a few of tags 5 to 7); this is E081's one dword a pixel. PDS_SIZE bits 17:16 at 0, 1, 2
and 3 (two runs each, x and y tags) change the counts a little and never remove the displaced
writes; no job hung.

**The searches.** 1797 jobs in all: each bit of the state block's word 4 (30 values: bits 0 and 2 to
6 hang), every bit of the VDM stream (352 cases, 167 hung), of state block words 0 to 2, 6 to 12, 14
and 15 (384, absolute values, 2 hung), of render details words 3, 4, 9, 16 to 21 and 26 to 36
through the kernel poke (640, 14 hung), render details dword 22 at 12 values, each bit of the pixel
PDS program's U1 (33 values, 3 hung) and word 4's bit 15 with each size and row count (36). Flips
that changed the counts: word 4 bit 15 cuts o1 from about 500 to 114 to 218 pixels (3 of 3 runs);
ISP word 0 bits 26 and 27 (blk:1 0x05d00200, 0x09d00200) leave tags 1, 3, 5 and 7 only (o0 on 1004
pixels, o2, o4, o6 on 34, 18 and 6): the tags 1, 3, 5, 7 pattern, in 36 of 36 jobs of the twelve
values with bit 26 xor bit 27 set (bits 28:24 = 0x04, 0x05, 0x08 to 0x0b, 0x14, 0x15, 0x18 to 0x1b;
three runs each); and render details dword 9 bit 0 (CR_REG_0148) leaves tags 1, 3, 5 and 7 as well
(o0 on 1038, o2 on 342). ISP word 0 with bits 26 and 27 together is the plain job; with bit 25 and
bit 26 (0x06, 0x07, 0x16, 0x17) or bits 25 to 27 no pixel is drawn (24 of 24 jobs).

**The combination.** ISP word 0 bit 26 or 27 with CR_REG_0148 bit 0 and word 4 at 0x00030001 leaves
tags 1 and 5 only: o0 on 985 to 1017 pixels (its own), o4 on 45 to 77 other pixels (the two sum to
the 1062 pixels), tags 2 to 4 (o1 to o3) on no pixel, own or other: 27 of 27 jobs (6 in the
combination table, 18 in the table of the same words after other jobs, each of six predecessors
three times, and 3 in the table of data rows at row 1). With the data rows 2, 3 and 4 the same words
leave tags 1, 3, 5 and 7 (o0 on 967 to 1032, 30 to 95 others; tag 7 on a few pixels, on none in a
handful of runs): the tags 1, 3, 5, 7 pattern; the table of five runs, whose program has three data
rows, gave the same pattern in 20 of 20 jobs (tag 7 absent in the ten that read tags from y); with 5
to 7 rows every job hung (27 of 27). Without bit 0 of CR_REG_0148, or without the ISP bit, at one
row the pattern is tags 1, 3, 5, 7 too (15 of 15 jobs).

**Reading the registers the setup leaves.** With the setup (word 4 set to 0x00030001, one data row,
and with the tool's own word 4, whose program has three data rows) the pack-floats probes of 11.14
(E387, o0 to o3 each alone and together; the pixels read are the ones mode 0 draws in the same case)
give one value per case on the triangle's pixels in 12 of 16 pack mode 0 cases of each of the four
tables (the four others are the x and y ramps; 1062 pixels, 1064 or 1070 in four of the 64 cases),
where the plain job (E387's table) gave one value in four cases of 16, two in six, 32 in two and 48
or 49 in the ramps. Pack mode 22, both runs, one data row: o0 = 1.0 alone 0xc0000000, o1 = 2.0 alone
0x000ffc00, o2 = 0.5 and o3 = 0.25 alone 0, all four 0xc00ffc00 on 1062 of 1062 pixels; o0 = x + 0.5
alone 0xc0000000 on 1017 and 0 on 45 (1039 or 1040 with the three-row program), o1 = y + 0.5 alone
0x000ffc00 on 1019 and 0 on 43. Every value that set a field in mode 22 was saturated (1.0 and 2.0,
and x + 0.5 and y + 0.5, above 1.0 but in the first column and row), so these runs place the fields,
o0 in bits 31:30 and o1 in bits 19:10, and say nothing of what the fields encode [infer]; o2 and o3
at 0.5 and 0.25 may feed fields these values leave at 0. Pack mode 34: o1 = 2.0 alone 0x00200000, o0
= 1.0, o2 = 0.5 and o3 = 0.25 alone 0, all four 0x00200000; a ramp o1 = 0.5 + y/128 alone gives bits
30:20 of the single in bits 21:11 on 1017 of 1062 pixels at one data row (1026 with three; the
others lower by two to four in the field, 0x1000 to 0x2000), and with o3 = 0.9 and o2 = 0.3 as well
1015, the difference the low bits 0x666 of o3 [infer]. That mid-range ramp is what puts o1 in bits
21:11 of mode 34. In two runs a few pixels beyond the 1062 (8 and 2) hold o3 = 0.25's word
0x001f4000, the word o1 = 0.25 gives in E387. So at the values tried o2 and o3 feed nothing seen on
the 1062 pixels, and E387's constants 0x88 and 0x60800000 sit on pixels the triangle does not cover
[infer from the mask of mode 0].

**What it shows.** The displaced writes of E081 (o1 to o3 on other pixels) depend on the pixel
task's setup, not only on the shader: with ISP word 0 bit 26 or 27, CR_REG_0148 bit 0 and the
one-row PDS size, o1 to o3 stop landing on other pixels and o0 and o4 take every pixel between
them. That each pixel then has room for four output dwords (and two for the tags 1, 3, 5, 7
pattern) is the reading of those landings [infer]; the runs show where registers land, not a
count of dwords. CR_REG_0148 bit 0 is not inert here, though E412 saw nothing with shaders that
write o0 only.

**What it does not show.** What bits 26 and 27 of ISP word 0 mean otherwise (bit 27 is the punch-
through pass bit of probes/isp/punch-through [infer]); why one data row and why the combination; the
o4 on other pixels (a fifth dword reaching the next pixel's room [infer]); the fields of modes 22
and 34 beyond o0 and o1 (the values tried leave o2 and o3 out), and what the fields of mode 22
encode.

**Correction 2026-11-12:** The claim read "a shader writing o0 to o7 with a tag in each leaves o0
on its own pixel and o4 on other pixels (tags 1 and 5) and o1 to o3 (tags 2 to 4) on no pixel at
all". E880 walked this setup (ISP word 0 at 0x05d00200, render details dword 9 bit 0, state block
word 4 at 0x00030001) with words that mark one output by bit 4 and the others by bit 5: the tag-5
word's bits 5:4 read 3, 2, 2, 3, 2, 2, 2, 2 for `o0` to `o7` and a program with no `o4` write left
the plain tag 5 (held out, 18 jobs), as in E709's command (E858). Tag 5 is tag 1 OR tag 4, so the
tag-5 word is the OR of the source instance's `o0` and `o3` words, not `o4`'s; the claim line is
edited to say so. "What it shows" ("o0 and o4 take every pixel between them") and "What it does
not show" ("the o4 on other pixels, a fifth dword reaching the next pixel's room") read the tag-5
word as `o4`'s and are corrected the same way; the counts and the setup stand. Only ISP word 0 bit
26 and one data row were walked.
