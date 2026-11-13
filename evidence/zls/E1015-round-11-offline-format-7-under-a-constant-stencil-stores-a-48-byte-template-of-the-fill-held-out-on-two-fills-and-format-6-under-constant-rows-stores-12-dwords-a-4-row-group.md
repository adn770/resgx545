+++
id = "E1015"
claim = "Round 11 offline (Q120; no run): two of E986's 'store less' layouts decode byte for byte from r10-zls zst2's kept dumps, rules frozen by hash (c7_rule.py, 4d87c5ad...): format 7 under a constant stencil fill S (E978's x ramp, 64 x 32) stores the first 12 dwords of each 256-dword tile block as one 48-byte template of 0x3f, 0x1f and S (F7K), fitted on fill 0xa5 and held out blind on fills 0x00 and 0xff (48 of 48 dwords each, no other dword changed), where the same template with S fixed at 0xa5 matched 0 of 48 [HW data, held out]; format 6 where four tile rows each hold one depth (the y ramp) stores 12 dwords for the four rows (F6C: a record 0x9e, the row's float without its sign bit, 0x00 a row at fixed bytes, words 0x3f000000 at fixed dwords), fitted on block 0 and holding on the two applicable groups of blocks 1 and 2 (48 of 48 dwords), where E985's raw layout matched 0 [HW data, SEMI: those blocks were printed before the freeze]; not decoded: format 5 under constant rows, format 7 under the index stencil, format 6's edge tiles and its groups after the first non-constant row (116 of z2y-f6's 212 changed dwords; post hoc a one-hot count mask of a row's last n pixels decodes 48 more)"
unit = "zls"
method = "Offline, no run (round 11, decision R11-10 (a), package P2; the round 11 ranking, finding 7). Data: r10-zls (render/closing-r10-zls, dataset render-closing-r10-zls) attempt out/20261113-102039, stage zst2 (E986): the depth dumps of z2y-f6, z2e-f6, z2d-f6, z2x-f7-s00, -sff and -sa5 and their format-0 references z2y-f0, z2e-f0, z2d-f0 and z2x-f0 (.depth.1.bin.gz), read through the session's gen/zst2.py (tiles, in_tile_index). The ranking's closing11/plan/c7-q120/: c7_rule.py (F6C, F7K and the rivals F6RAW and F7K with a fixed byte; sha256 4d87c5ad9082cbcd3045e5b3f776df305ba81246633c5c817e7cb4d57a94342c in c7_rule.sha256, with score.py d7eb408b... frozen beside it), FREEZE.log (11:11:40Z, every dump read before the freeze: all four z2y-f6 blocks, z2y-f5 and z2y-f7 block 0, z2e-f6 block 1, the symbol positions of z2x-f7 s00 and sff blocks 0 and 1; so F6C's blocks 1 and 2 are not blind, and F7K's held-out reads are blocks 2 and 3 of s00 and sff and the no-other-dword test), score.py with lib.py (standard library) and score.out; posthoc.py and posthoc.out (the count-mask form, written after reading). This record re-ran score.py and posthoc.py with the repository's .venv (PYTHONPATH=. python -B) and got score.out and posthoc.out byte-identical to the ranking's."
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r10-zls:out/20261113-102039/zst2/", "cited-scratch:closing11/plan/c7-q120/"]
terms = ["CR_ISP_ZLSCTL"]
+++
**What was done.** E986 held E985's layouts of formats 3 and 4 everywhere and those of 5 and 6
where every pixel of a tile row has its own depth; where a row repeats one depth (the y ramp) or a
tile holds the constant background, 5 and 6 stored fewer dwords, and format 7 stored 48 dwords
under a constant stencil and 784 under the index one. The ranking wrote two layouts from one fit
block each, froze them with their rivals by hash, and scored the rest.

**F7K.** With a constant stencil fill S, format 7 writes the first 12 dwords of each 256-dword
tile block (E985's block order), the 48 bytes `ASBASBASBASBASBABASBASBASBASBASBSBASBASBASBASBAS`
(A = 0x3f, B = 0x1f, S = the fill byte, byte 0 first), and no other dword. The template is not of
period 3: a one-byte shift sits at bytes 15 to 17 and 31 to 33 [infer: the 17-byte period of
format 3's address rule].

**F6C.** A format-6 block (512 dwords) whose first four tile rows are each one depth v_r (the
format-0 float, sign clear) holds them in a 48-byte group: row r mod 4 writes 0x9e, v_r little
endian and 0x00 at byte 6, 26, 14 or 34 (r = 0 to 3), bytes 46 and 47 are 0x9e and the low byte of
v_2, the words 0x3f000000 sit at dwords 3, 0, 5 and 10 for rows 0 to 3, and the next four rows
follow as the next group while they too are constant.

**Results [HW data]** (score.out, dwords):

| rule | fit | scored after the freeze | rival |
|---|---|---|---|
| F7K | z2x-f7-sa5, 48 of 48 | s00 48 of 48, sff 48 of 48, no other dword changed | S fixed: 0 of 48 on each |
| F6C | z2y-f6 block 0, 4 of 4 groups (48) | blocks 1 and 2, 2 of 2 groups each (48) [SEMI] | E985's raw format 6: 0 |

Not predicted: z2y-f6's block 1 and 2 groups after the first non-constant row and its block 3
(116 of 212 changed dwords); z2e-f6 (1364 dwords) and z2d-f6 (2048) have no constant group (z2d's
rows hold 32 depths each and are E985's raw layout, E986). Post hoc (posthoc.py, fitted after
reading): a row of v for 32 - n pixels and v + 1 ulp for the last n gives the record v and the
mask 0x3f000000 | 1 << (24 - n), decoding block 1's other two groups (48 dwords); block 2's later
groups turn variable in length and stay undecoded.

**What it shows.** Format 7 under a constant stencil and format 6 under constant rows are not
noise: fixed-length records keyed by the stencil fill and by the row's single depth [HW data;
F7K held out, F6C SEMI]. [infer] Formats 5 to 7 are a run or plane compression of the depth and
stencil with a count mask; no mechanism is known, and E986's "compressed form keyed by the row's
values" stands.

**What it does not show.** Format 7 under the index stencil (784 dwords, stencil bytes in row
groups with 0x3f and 0x1f markers between them), format 5 under constant rows (988 dwords; its
first dwords repeat F6C's with the stencil bytes between), format 6's edge tiles and its
variable-length runs, F7K at fills equal to a marker (0x3f, 0x1f) or at another size, F6C at
another size or origin, and any of these without a stencil buffer. sgx-pipe keeps formats 5 to 7
refused (Q120).
