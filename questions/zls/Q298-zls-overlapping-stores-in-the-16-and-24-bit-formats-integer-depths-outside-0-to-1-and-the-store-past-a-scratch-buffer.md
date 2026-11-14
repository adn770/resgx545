+++
id = "Q298"
question = "which pixel does a dword shared by overlapping tiles hold in the 16-bit format, and in the 24-bit one with edge tiles or four macrotiles a side; what do the integer formats store for a depth outside 0 to 1; and what does a store whose pitch runs past its buffer do (E411's faulting pitches and bit 25 rows)?"
unit = "zls"
kind = "hw"
value = "low"
phase = 12
evidence = ["E411", "E465", "E490", "E977", "E991", "E996", "E1041", "E1051"]
terms = ["CR_ISP_ZLSCTL"]
+++

Opened 2026-11-14 with Q242's retirement (answered by E1041, round 14 decision R14-6 (a), the lead
confirming). Q242 asked which pixel a shared slot holds, what the integer formats store past odd
targets and what lay on E411's pages 16 and 18: E996 and E1041 decided every clause with held-out
rows. What sgx-pipe's `zls` still refuses was never decided there and is carried here:

- overlapping tiles in the 16-bit format (no overlapping 16-bit store ran), and in the 24-bit
  format with edge tiles or four macrotiles a side (E996 ran it on whole tiles and two
  macrotiles; E1041 ran the overlaps in the float format only);
- an integer format at a depth outside 0 to 1 (E977's floor rule ran over 0 to 1; the clamp
  above 1 and a depth below 0 reaching the conversion were not run);
- E411's scratch arrangement at the pitches that faulted (bits 5 to 11: the extent past the
  16-page buffer [infer], E991) and its bit-25 row (the 16-bit format at G 1 stored pages the
  model does not decode).

What would settle it: E996's overlap rows in formats 1 and 2 with edge tiles and at 640 x 480;
E977's integer rows with the viewport's z offset and scale pushing depths past 0 and 1; E411's
faulting pitches with a buffer sized to their extent (flagged class if a fault is expected).

Narrowed 2026-11-14 (r15-zls, E1051). Overlapping stores in the 16-bit format and in the 24-bit
one with edge tiles and four macrotiles a side hold the last-visited tile by the floor rule
(H-LATE/HDR 4 of 4); the integer formats clamp a depth above 1 (format 0 kept 1.25) and store 0
for a negative one (H-INT-SAT 4 of 4); E411's pitches G 5, 9 and 17 store E465's pages with the
buffer sized (H-E465-EXT 3 of 3) and its bit-25 row the 16-bit floor of 0.5 (H-B25-FLOOR).
sgx-pipe's `zls::store` and `encode_depth` model them.

Status: open.
