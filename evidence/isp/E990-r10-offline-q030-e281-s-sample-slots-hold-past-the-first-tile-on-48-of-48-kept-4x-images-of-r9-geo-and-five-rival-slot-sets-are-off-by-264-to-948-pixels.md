+++
id = "E990"
claim = "Round 10 offline (Q030; no run): on the 48 kept --pixels images of r9-geo's stages seam1 and seam4 (E953, E954: tri-full renders 64 x 96 to 128 x 96 and six single triangles of new slopes, CR_ISP_MSAA modes 0 to 2, CR_TE_AA 0x2, 0x6, 0xa and 0xe windows, the two controls included), the landed region model (msaa_model.py, 1c0e8205..., frozen before the run) with E281's sample slots (6, 2), (14, 6), (2, 10), (10, 14) in every tile gives the stored triangle pixels of every tile past the first exactly, 48 of 48 jobs and 0 pixels off; five rival slot sets declared and hashed before the images were read (q030_slots_rule.json, 0dd46dec...: every sample at the centre, E281 mirrored in x, mirrored in y, transposed, the slots swapped within a pair) differ from E281's on 30 to 42 jobs and are off the kept images past the first tile by 504, 484, 948, 264 and 910 pixels [HW data, read offline after the rivals' freeze; the E281 sets were frozen before the run]; mode 0 with bits 31 or 30 ran on tri-full renders only, where the slots decide the edge pixels but no identity map was read, and mode 3 did not run"
unit = "isp"
method = "Offline, no run (round 10, decision R10-1 a, package O10-1; ranking closing10/rank/rank-round10.md finding 1). Data: r9-geo (render/closing-r9-geo, dataset render-closing-r9-geo) attempt out/20261113-081038, stages seam1 and seam4, the kept per-job --pixels images (seam1/NAME.txt.gz and seam4/f4-NAME.txt.gz, 24 jobs a stage, the jobs and vertices of the session's own gen/seam.py: jobs() and prims()), the triangle colour the session's G.TRI; module B60AB0B4, tool t4, as E953 and E954 give them. Model: resgx545-data texture/p1141/recompute/msaa_model.py (sha256 1c0e8205..., the region model E922 read in sample and r8's O8 table froze for E953), its predict(prims, w, h, mode, te, slots=S) with S each slot set. The ranking's closing10/rank/q030_slots.py (standard library; checks the rule's hash and the model's sha before it reads an image) scored, per job, the stored pixels of every tile other than (0, 0) (x >= 32 or y >= 16) as a set against each rival's prediction, and the first tile apart; the rivals are in q030_slots_rule.json with its sha256 in q030_slots_rule.sha256, written before the script read the images (the ranking's account and the file order). This record re-ran the script with the repository's .venv (python -B, the session's modules read in place) and got q030_slots.out byte-identical to the ranking's."
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r9-geo:out/20261113-081038/seam1/", "render-closing-r9-geo:out/20261113-081038/seam4/", "cited-scratch:closing10/rank/"]
terms = ["CR_ISP_MSAA", "CR_ISP_MULTISAMPLECTL", "CR_TE_AA", "programmable sample positions"]
+++
**What was done.** E281 fitted the multisampled layouts with the sample slots of
`CR_ISP_MULTISAMPLECTL` from eight positions of a known edge inside the target's first 16 x 16 tile,
and Q030 asked whether the slots are the same in the tiles past the first and in each window, which
E502's identity maps cannot show (every slot of a pixel held the same iterated position). r9-geo's
seam stages (E953, E954) scored their images as sets under the region model, which carries E281's
slots everywhere, and found every set exact; they did not ask whether another slot set would have
been exact too. The round 10 ranking declared five rivals, hashed them, and then scored the kept
images of the tiles past the first under each.

**Results [HW].** S-E281: exact past the first tile on 48 of 48 jobs, 0 pixels off (and exact in the
first tile). The rivals, past the first tile (jobs exact, jobs where the rival's set differs from
E281's, pixels off the kept image): S-CENTRE 6, 42, 504; S-MIRX 8, 40, 484; S-MIRY 6, 42, 948;
S-TRANS 18, 30, 264; S-SWAP 6, 42, 910. The two tri-full mode 2 TE 0xa jobs (96 x 64, 128 x 96) and
the full-target control store every pixel and part no rival. Mode 0 ran with TE 0x6, 0xa and 0xe on
tri-full renders (five jobs a stage), where the slots decide which edge pixels store the triangle:
S-E281 is exact there too and three to five of the rivals are off on each.

**What it shows.** [HW] The slot set of E281 gives the stored pixels of every tile and window r9-geo
ran (modes 0 to 2, TE 0x6, 0xa, 0xe, sizes 64 x 64 to 128 x 96), where each declared rival is off on
at least 30 jobs; the rivals were declared after E953 and E954 had reported the sets exact, so what
is held out is the model's slots (frozen before the run), not the choice of rivals. [infer] The
sample positions do not change with the tile or the window.

**What it does not show.** Mode 0's window with TE bits 31 or 30 as an identity map (the source
pixel each stored pixel holds; sgx-pipe's `msaa_source` refuses it, Q030), mode 3 (hangs, E210; its
window never ran), other slot values than the library's `CR_ISP_MULTISAMPLECTL`, and slot sets other
than the five declared (a rival that differs from E281 at no kept pixel is not refuted).
