+++
id = "E476"
claim = "lapc lands exactly on the index in pclink for each of the indices run (listed in What it shows; no index outside them is known to fail, and no other index was run): a jump through the link of a ba.savelink call returns to the instruction after it (4 of 4 cases, including a new link moved into pclink after the call with 0 to 2 instructions between), nested calls whose routine saves and restores pclink in r14 return twice with br.savelink and ba.savelink (2 of 2), lapc lands on targets 1 to 100 instructions ahead with the target a constant (8 of 8, landing at the indices 30, 31, 32, 34, 37, 45, 69 and 129) or computed by an ima32 add (8 of 8, the same indices) and 0, 1, 2, 5, 20 and 100 instructions back over three passes (6 of 6), pclink bits above bit 17 set in the register moved into it are ignored and the jump lands on bits 17:0 (4 of 4: bit 18, bit 19, bit 31 and bits 31:18), and in programs placed in the code heap the indices count from a code base that is the placement rounded down to 512 KiB (this rests on one placement that is neither 0x10000 nor a multiple of 0x100000, 0x1ff000: the step of 0x80000 is the only one the five links allow, but a second such placement was not run): a lapc to index 8192 + 129, 8192 + 200 and 8192 + 250 lands (3 targets, each run 3 times at the one offset 0x10000: 9 of 9 jobs) and so does a lapc computed from the link of a br.savelink read at run time, forward 8 instructions, in programs placed at offsets 0x10000, 0x100000, 0x1ff000, 0x200000 and 0x400000, whose links read 0x2002, 2, 0xfe02, 2 and 2 (5 placements, each run twice: 10 of 10 jobs); a jump to index T in a placed program that counts T from the program start instead faults the job (BIF fault at 0x37001014 to 0x37001031) or hangs it, and the GPU recovers (no job after the faults failed to run; 7 jobs failed in all: 3 lapc faults in place, 2 `ba #T` faults and 2 hangs in place-ctl2)"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1122 (sha256 ec423efc3d9aa34576553da70916be4ceb715a729cbc02cc4bd89fa052511244), health (a fill and a 64 x 64 triangle exact: diff 0) before the first table, after each table and after every risky probe, no reboot and no module reload: probes/usse/risky.toml (dump.s, 7 probes and 48 cases, 8 cases of the plan dropped: lapc-direct and lapc-computed lost the absolute targets 255, 256, 257 and 300 to the tool's 256-word check, and their question text, as it ran, still names them; run in the file order, ba-return only after ba-savelink-read agreed on the stored index: E475) and probes/usse/place2.toml, place-link.toml (placed programs, 3 + 10 probes, 9 + 20 jobs), with the failed runs kept: place.toml (the first placed table, probe lapc-129 with the target as the index in the program: 3 of 3 jobs faulted, 3 BIF faults 0x91000 at 0x37001019, 0x37001031, 0x37001031, dataset usse/place, kept as a failed run: the campaign runner stopped on the tool's usage message at the second probe, whose program has over 256 words, so its manifest was written by hand with the runner's own digest function, and the table lists six probes (targets 255 to 511) that never ran; the first three of its jobs counted the target from the program start, where the jump counts from the code base) and place-ctl.toml and place-ctl2.toml (controls: a 2-word, an 8-word and a 133-word placed program without a jump ran to their end, 6 of 6; `ba #T` in a 133-word one faulted twice and a 12-word one with a lapc hung twice, 4 jobs, 2 BIF faults and 2 hangs recovered by the driver; usse-place-ctl, the first of the two control tables, is kept as a failed table: its 6 jobs ran to their end (o0 0xfa11, 0xfa11 and 0x600d, twice each), but its hypotheses were scratch lists for programs that store nothing, so every probe read NONE, and the controls were rerun as usse-place-ctl2); a first run of place2 as a 7-probe table (targets to 511) stopped at its second probe on the same check of the tool, its first probe (3 of 3 landings) is not in the data, and the table was redone under the same name with targets of at most 250 words; the risky table's 7 probes ran twice, once alone each by probe.py (outside the data) and once by the campaign runner (the dataset), identical readbacks in the 48 cases, kernel.log with the campaign mark and no other line; the placed runs once each"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-risky", "usse-place", "usse-place-ctl", "usse-place-ctl2", "usse-place2", "usse-place-link"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

**What runs.** risky: ba-return calls with `ba.savelink` and returns with a plain `lapc`, then the
same with `mov pclink, r13` (r13 = the marker of the other return) 0, 1 and 2 instructions before
the `lapc`; nested: two calls deep with `mov r14, pclink` and `mov pclink, r14`; pflow-call is E477;
lapc-direct `mov r5, #T; mov pclink, r5; lapc` over T 1, 2, 3, 5, 8, 16, 40 and 100 instructions
past a skip marker (indices 30, 31, 32, 34, 37, 45, 69, 129); computed: `ima32.u` of a base and K;
backward: three passes of `lapc` to a label 0, 1, 2, 5, 20 and 100 instructions back; high-bits:
`mov r5, #T; or r5, r5, #0x00040000` (and 0x80000, 0x80000000, 0xfffc0000), `mov pclink, r5`, `nop`,
`lapc` with T = 24. Result words: 0x600D landed, 0x5741 the stale link, 0xFA11 fell through. Placed
programs: sgxfive-test's `--place OFFSET=FILE --place-form cbase` (E428) starts a program of the
table's own at the offset in the code heap in place of the fill shader; place2 runs `mov r5, #(8192
+ w); mov pclink, r5; nop; lapc` in a program of w + 4 words with `mov r10, #(0x1000 + k)` padding
and `mov.end o0, r10` as word w (o0 = 0x600D on a landing); place-link reads `br.savelink #1; mov
r10, pclink; mov.end o0, r10` (the index of the word after the call) and runs `r5 = r10 + 8; mov
pclink, r5; lapc` with the target the last word.

**Results (campaign run, 48 of 48 in risky).** Every risky probe agreed with the model, the GPU
stayed healthy (the fill and the triangle exact after each table), kernel.log of the table holds
only its mark. Placed programs: place2 9 of 9 landings (o0 0x600D, no fall-through 0xFA11),
place-link read 0x2002 for the offset 0x10000 (index 0x2000 + 2: the placement divided by 8), 0x2
for 0x100000, 0xfe02 for 0x1ff000, 0x2 for 0x200000 and 0x400000 (two runs each), and the computed
`lapc` landed at the word 8 on in all 10 jobs. The code base therefore moves in steps of 0x80000
bytes (65536 instructions), as the five links read (one non-aligned placement decides the step
besides 0x10000; the jobs are 9 and 10 runs of 3 targets and 5 placements, not that many
independent cases), and the program starts at the offset within the step: 0x1ff000 - 0x180000
= 0x7f000 bytes = 0xfe00 instructions.

**Failures kept.** place (3 of 3 faulted): the first placed table put the target as the word in the
program (T = 129) and every job faulted with a BIF fault at the code heap page after the first
(0x37001019 and so on): the jump went [infer, supported by place2 and place-link] to index 129 of
the code base, which for a program placed at 0x10000 is the heap base, page 0, whose code runs to
the end of the page and fetches page 1, unmapped. place-ctl2 shows that the placed programs run when
they do not jump (6 of 6) and fail when they do (`ba #T` faulted twice, a `lapc` to T in a 12-word
program hung twice, as a jump to heap index T). The data are what the hardware did with a wrong
template, and the template's fault is the answer to "where do the indices count from" (above). The
fault recoveries are in kernel.log of the datasets (7 lines of *ERROR* in all, 3 + 4), and every
later job ran.

**What it shows.** [HW] `lapc` and `ba.savelink` are exact and need no gap, for the indices that
were run as lapc landings: in a fill 30, 31, 32, 34, 37, 45, 69 and 129 (the target a constant or
computed), the backward targets 0, 1, 2, 5, 20 and 100 instructions before the lapc, the target 24
of the high-bits cases and the call returns (about index 20); in placed programs 0x2081, 0x20c8 and
0x20fa (place2) and the link plus 8, 0x200a, 0xa, 0xfe0a, 0xa and 0xa (place-link). About 15
distinct indices in a fill and 6 in placed programs. The values 0x2002, 0xfe02 and 2 are links read,
not lapc targets (the jumps land at the link plus 8). No index outside these is known to fail. Bits
above 17 of a register moved into pclink are dropped at the move (E475), so the jump cannot go wild
that way. The index counts from the code base the DOUTU names; for a task started by the firmware
that base is whatever the firmware started it with, so a computed jump should be relative to a link
read at run time (the `br.savelink #1` and `mov rN, pclink` idiom) and not to an absolute index
[infer].

**What it does not show.** Every other index (the ranges 1 to 129 and 8194 to 8442 were not run
index by index), a second non-aligned placement (0x2ff000 or 0x1a0000, say: not run) and so whether
the step is 0x80000 and not another value that fits the five links, a firmware-started task (the
base rule for it is [infer]). Targets of 256 to 8191 in a fill (sgxfive-test refuses programs of
over 256 words, fill or placed), index bits 16 and 17 of the PC (a jump that crosses a 65536-word
step of the code base: the placed programs are one page, 512 words at most, and 256 by the tool;
Q123), `lapc` with a repeat, `.synce` and `.mon` flags, any jump from a firmware task.

**Correction, 2026-11-08 (11.25).** The measurements above are unchanged; the statements that the
step of 0x80000 'rests on one non-aligned placement' and that a second was not run are replaced by
E492: five more placements (0x2ff000, 0x1a0000, 0x3a8000, 0x4ff000 and 0x300008) read the links
0xfe02, 0x4002, 0x5002, 0xfe02 and 0x3, and the lapc to the link plus 8 landed in each (20 of 20
jobs: a read and a jump program at each offset, two jobs each). Of the ten placements seven are not
multiples of 0x80000 (0x10000, 0x1ff000 and the five new ones), and among the powers of two from
0x1000 to 0x1000000 only 0x80000 fits all ten links (0x40000 fits 7, 0x20000 and 0x100000 fit 5). A
step that is not a power of two was not excluded by a fit, a task started by the firmware stays
[infer], and the 65536-word crossing and the indices 256 to 8191 are still not run (Q123).
