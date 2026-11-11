+++
id = "E829"
claim = "R4-A stages a-pb0 and a-pb (Q285 rerun, 8 jobs, split flow -n 2 --geometry 1 at 64 x 64, CR_TE_AA 0x40000000, forced render_rgn_arrays 1, module srcversion 99CD90DA, controls frozen from E827's two-render jobs of the same shape): the four controls passed (pb-d0-te40, pb-p1-te40 and pb-p2-own11: hash 0x8ea26cdfee74a325, 3969 of 4096 pixels wrong, first (1, 1) 0xff000080, parameter buffer sha256 b8ada427...; pb-p0-te60: hash 0xd2bfb75560f4c325, 0 of 4096 wrong) and the gate opened; poking the twin's 16 words into dwords 11 to 26 of render 1's parameter buffer between the two renders gave the twin's picture in 2 of 2 jobs (pb-p3a, pb-p3b: 0 of 4096 wrong, render 2 4096 triangle pixels, hash 0xd2bfb75560f4c325, the dump's dwords 11 to 26 the poked words, 16 of 16 pokes applied) and poking dword 11 with 0xffffffff drew nothing in 2 of 2 (pb-p4a, pb-p4b: 3969 of 4096 wrong, render 2 0 triangle, 4096 background, 0 other pixels); frozen verdict 'Q285: H-OLD: the 3D reads render 1's object in the old layout (4 of 4 rows decided)', both readings H-FIELD needed (p3 not the twin's picture, p4 drawn) contradicted by both replicate pairs"
unit = "isp"
method = "R4-A (decision 10, reruns; the rerun of K2's stage k-pb whose controls failed, E825), dataset render-closing-r4-q285, 2026-11-11, attempt out/20261111-081210 (run 08:12 Mac time, a-pb0 then a-pb gated on a-pb0's three controls, 8 jobs, 0 void, 0 faults, one attempt, no refreeze), the laptop (host cedar), kernel 7.3.0-resgx545, module of the linux fork's branch resgx545 at a2788bd8 (srcversion 99CD90DA26E3AFF9C450517, installed = loaded), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a, built from resgx545 r3-rgn4 at 4623753); every row `tri --tri-full --keep-going --wait-ms 20000 --width 64 --height 64 --max-width 64 --max-height 64 -n 2 --geometry 1 --poke cmd:1=0x40000000 --poke cmd:10=0xeaa26e26 --poke cmd:13=0x80000002 --poke cmd:16=0xeaa26e26 --dump-render DIR`, K2's commands byte for byte, plus the row's `--kpoke-render 2:par:N=V` (p2: dword 11 = 0, its own value; p3: dwords 11 to 26 = 0x00040101, 0, 0, 0, 0, 0x00100000, 0x00001000, 0x00003f00, 0x10500010, 0x3f000000, 0x00105000, 0x00001000, 0x50003f00, 0x10500010, 0x3f000000, 0; p4: dword 11 = 0xffffffff), the pokes armed before render 2 so that they land after render 1's geometry-only kick; the new default render_rgn_arrays 0 refuses TE bit 30 or 31 on a context without the 4x flag, so the runner wrote render_rgn_arrays 1 after each job's reset (read back), 0 after the job and at the exit (read 0 after the stage), the one-array layout of E728, E825 and E827 (E828 checked that forced 1 reproduces E827's row on this module and tool); a debugfs reset before each job, fault limit 1, health ok after both stages; controls frozen before the run from the kept output of E827's two-render jobs pb-n40-a and pb-n60 (predictions/a-pb0.tsv and a-pb.tsv, PREDICTIONS.sha256), including the sha256 of the 4.6 MB parameter buffer, the TA data sha256 8ec0ebc7..., dwords 0 to 63 and the kernel's `kpoke ... applied` lines; the twin's two-render hash was reported against p3 and never decided it (E825 noted the hash is not the picture's alone; K2 had frozen the one-render value 0xd0530839d87ea325); scored by the frozen score/score_a.py (out/20261111-081210/score-a-pb0.txt, score-a-pb.txt, gate-a-pb.txt) with scorekit from resgx545 6421c1c. The runner's exit code 0 is from the lead's plan log; the kept outputs hold the stage's end lines, the knob line and the health outputs. README.md and PREFLIGHT.md of the dataset are the pre-run documents"
tiers = ["HW", "infer"]
date = "2026-11-11"
data = ["render-closing-r4-q285:out/20261111-081210/"]
terms = ["CR_TE_AA", "Parameter Buffer (PB)", "PB_OBJ.FORMAT"]
+++
**What ran.** E728: with `CR_TE_AA` bit 29 clear and bit 30 or 31 set, dwords 11 to 26 of the
parameter buffer (the format word, the set masks and the packed vertices) sit one dword later than
in the bit-29-set job, a zero dword at 11, and the image is empty. Q285 asks what that stretch is
and why the image is empty. K2 (E825) built the pokes of the stretch between the TA and the 3D, but
its three controls were frozen from one-render jobs while the stage ran two renders, so the gate
closed. E827 measured the two-render value of the controls on the new module. R4-A runs K2's eight
jobs again, the same commands, with the controls frozen from E827's two-render output. H-OLD: the
3D reads the stretch in the old layout (so the twin's words poked at 11 to 26 give the twin's
picture, and a garbage dword 11 draws nothing). H-FIELD: dword 11 is a field the 3D uses (so a
garbage dword 11 draws triangle pixels and the twin's words do not give the twin's picture).

**Frozen verdict (as printed).** `SUMMARY: a-pb0: controls {'pb-d0-te40': 'PASS', 'pb-p0-te60':
'PASS', 'pb-p1-te40': 'PASS'}; gate a-pb open`; `gate a-pb: open (a-pb0's dump run, p0 and p1
passed)`; `SUMMARY: a-pb: p3 twin, p4 empty; Q285: H-OLD: the 3D reads render 1's object in the old
layout (p3, the twin's dwords 11-26, gives the twin's picture; p4, dword 11 = 0xffffffff, draws
nothing) (4 of 4 rows decided)`.

**Results [HW].**

| job | set | poke before render 2 | render 2 | wrong | target hash | reading |
|---|---|---|---|---|---|---|
| pb-d0-te40 | control | none (TE 0x40) | 0 triangle, 4096 background | 3969 of 4096 | 0x8ea26cdfee74a325 | PASS |
| pb-p0-te60 | control | none (TE 0x60, the twin) | full image | 0 of 4096 | 0xd2bfb75560f4c325 | PASS |
| pb-p1-te40 | control | none | as d0 | 3969 | 0x8ea26cdfee74a325 | PASS |
| pb-p2-own11 | control | dword 11 = 0 (its own value) | as d0 | 3969 | 0x8ea26cdfee74a325 | PASS |
| pb-p3a-twin | held out | dwords 11 to 26 = the twin's | 4096 triangle, 0 background, 0 other | 0 | 0xd2bfb75560f4c325 | twin |
| pb-p3b-twin | replicate | as p3a | 4096 triangle | 0 | 0xd2bfb75560f4c325 | twin |
| pb-p4a-ffff | held out | dword 11 = 0xffffffff | 0 triangle, 4096 background, 0 other | 3969 | 0x8ea26cdfee74a325 | empty |
| pb-p4b-ffff | replicate | as p4a | 0 triangle, 4096 background | 3969 | 0x8ea26cdfee74a325 | empty |

Every job class ok; p0 and p3 returned rc 0, the others rc 1 as the image check does. The kernel
logged `kpoke ... applied` once for p2 and p4 and 16 times for each p3; the kpoke state was empty
after p2. The hash of p3 equals the twin's two-render hash, which was reported, not used.

**What it shows and does not.** With controls of the stage's own shape the TE 0x40 job reproduces
E728's empty image (d0, p1, and p2 with its own value), the twin draws (p0), and the stage's
pokes work (the dump's dwords 11 to 26 are the poked words). Putting the twin's words in the
stretch, with the displaced zero overwritten, makes the 3D draw the twin's whole picture, and a
dword 11 of 0xffffffff, with the rest of the stretch as the TA wrote it, draws nothing and does
not hang the ISP: the 3D reads dword 11 as the start of the object in the old layout (the format
word of the bit-29-set job), as E728's decoding said, and a bit-29-clear job's zero there is what
leaves the image empty [infer, from p3 and p4 together; p4 alone does not tell a format word from
a word the 3D skips]. H-FIELD needed p3 not the twin's picture and p4 drawn, and both pairs
contradict it. What is not answered: why the TA writes the extra zero when
bit 29 is clear and bit 30 or 31 is set (the TA side of the question), whether render 2's own
object (written from dword 27, E825) is read in the displaced layout (its image is not drawn
here), and what the 3D does with other values at dword 11. The pokes land after render 1's
geometry-only kick, so they change render 1's object and render 2's 3D draws it
[infer, from the fork's commit 8fc748b0 and the kept dumps]; the result is for the one-array
layout (render_rgn_arrays 1), the layout E728 measured.
