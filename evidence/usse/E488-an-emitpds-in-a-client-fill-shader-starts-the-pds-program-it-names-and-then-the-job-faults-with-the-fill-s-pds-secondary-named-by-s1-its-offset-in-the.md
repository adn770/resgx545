+++
id = "E488"
claim = "An emitpds in a client fill shader starts the PDS program it names, and then the job faults: with the fill's PDS secondary named by s1 (its offset in the pixel PDS heap shifted right by four, 4 for the copy's secondary at heap base + 0x40) and s0 = 2 data rows, addend 0x100, the emitted run of the program stores an input word to scratch in 18 of 19 ir0.0 probes (the ir0.1 and ir1 probes are not counted; the program's ir0.0 reads 3 in 16 and 2 in 2, against 0x400 to 0x403 for the fill's own run), s2 not reaching ir0.0 or ir1.0 (s2 0, 1, 0xFFFFFFFF and 0xE17D0001 give ir0.0 3, 3, 2, 3, and ir1.0 is 0 for s2 0, 0xFFFFFFFF and 0xE17D0001), and the flags .tasks, .taske, both, neither, .freep and .nosched, #incp 1 to 3, the sideband 0x1, 0x200 and 0x2000 and 2, 1 or 4 rows changing nothing seen of that, while with the addend 0x1000 the dword held the no-emit value 0x403 (1 probe, and once more in a probe.py repeat outside the data, both in jobs that faulted: one observation of no 2 or 3 seen, the late 0x400 value moving from run to run in 5 of 20 probes); every job with an emit ended with a BIF fault at 0xd2000 (22 of 24, 0x92000 once with sideband 0x1) or a hang (two emitpds in a row), 24 of 24, each recovered with no reload, and the two controls without an emit completed"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1124 (sha256 58907b06a8e9030472a809cd669d2c3823946fd67aaf4775f942704a90f6a5ae): probes/usse/emitpds.toml (26 probes of one case, PDS probes with --pds 8 --use emit_*.s --low 0x10000 --coords, campaign run, recovered after each of the 24 failed jobs; the dataset), run after exploratory runs by probe.py outside the data (below), and repeated by probe.py with each probe in a process of its own and a health triangle between (same status in 26 of 26, the program ran in the same 18 of 19, ir0.0 3 in 17 and 2 in 1 of the 18, the addend 0x1000 again unchanged; a single probe.py process for all 26 is not a repeat: after the first fault 21 of the next jobs hung before the emit ran, which the campaign's baseline triangle between probes avoids); the tool is the 11.22 sgxfive-test with two small changes made for this phase and tested first (tests/test_cli.py of the tool: 198 passed before, 204 after, the new tests seen failing before the change): a limm 0x5CB0nnnn or 0x5CB1nnnn in the fill shader or a --place program is patched to the PDS secondary's pixel PDS heap offset or its GPU address shifted right by four plus nnnn, and --pds N --use USE is accepted with --coords"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-emitpds"]
terms = []
+++

**What runs.** A PDS program (the fill's PDS secondary, replacing the built-in one) stores one
input word ({SRC}: ir0.0, ir0.1, ir1.0 or ir1.1) to scratch dword 0 (mapped at 0x10000 through the
kernel's vm_low) and starts the secondary USE task as the built-in program does; the shader of the
copy (`--coords`, the texel in pa0) reads dword 0, tests `pa0 == 0` so that only one instance emits
(`!p0 br #2` over the emit), executes `emitpds<flags> #incp, r2, r3, r4, #sideband` with r2 = (rows
<< 23) | addend, r3 = 0x5CB00000 (patched to the secondary's heap offset >> 4), r4 = s2, then reads
dword 0 sixteen times and stores the reads (no loop). 2 data rows hold the program's data. 26
probes: control (no emit), base (.tasks.taske, 2 rows, addend 0x100, s2 0xE17D0001), .tasks,
.taske, neither, .freep, .nosched, #incp 1, 2, 3, addend 0x1000, s2 0, 1, 0xFFFFFFFF, sideband 0x1,
0x200, 0x2000, two emits (s2 0xE17D0001 then 0xE17D0002), rows 1 and 4, and the PDS program storing
ir0.1, ir1.0 and ir1.1 (and s2 0 and 0xFFFFFFFF with ir1.0, and a control with ir1.0).

**Results.** control: the fill's own run leaves 0x402 in dword 0 (0x403 in two earlier runs; ir1.0
is 0). With an emit the dword reads 3 in 16 probes (base, .tasks, .taske, neither, .freep,
.nosched, incp 1 and 2, s2 0, 1, sideband 0x1, 0x200, 0x2000, two emits, rows 1, rows 4) and 2 in 2
(s2 0xFFFFFFFF, incp 3), ir0.1 reads 2, ir1.0 and ir1.1 read 0; with addend 0x1000 it stays 0x403
(the emitted run did not store, or stored the same). In 4 of the 19 ir0.0 probes (freep, nosched,
s2 0, sideband 0x200) and in the ir0.1 probe the dword is again 0x400 or 0x401 at the end (after
the 16 reads showed 3 or 2), as if another run of the program stored later. Failure: 22 jobs ended
with `BIF fault 0xd2000` (second number 0x12 in 20, 0x16 in base, 0x15 in rows 1), one with 0x92000
(sideband 0x1, second number 0x13), and the two-emits job hung; each was recovered by the driver,
the health triangle after each was clean, and the readbacks of the shader's own stores (the 16
reads, the pre-read) landed before it.

**Repeat (probe.py, one process and a health triangle per probe, outside the data).** 26 of 26
probes end as in the campaign (2 controls complete, 23 fault, two-emits hangs); the pre-read of
dword 0 is 3 in 17 and 2 in 1 (incp 1) of the 18 ir0.0 probes that ran, ir0.1 3, ir1.0 and ir1.1 0,
the control 0x403 and 0x0, and with addend 0x1000 0x403 again; the 2 and the 3 and the late 0x400
values move from run to run (5 of the 20 probes that store ir0.0 or ir0.1 showed 0x400 or 0x401 at
the end in the campaign, 3 in the repeat, in other probes), so they are not a function of the
operands.

**Exploratory runs (probe.py, outside the data, earlier template versions).** With a fill (no
--coords) all 2048 instances emitted: base, .tasks, .taske, neither, .freep and .nosched hung or
faulted the job (6 of 6) and left 2 or 3 in dword 0. A PDS program that starts no USE task
(control) completed, but the next job hung once (recovered); the same program with the emit hung,
then faulted with an eight-dword store (the control with the eight-dword store faulted with no
emit, E144's totals): that comparison is not clean and is not used. A one-dword store avoids the
faults of the control.

**What it shows.** [HW] A client shader's emitpds is not refused or ignored: the PDS program at s1
runs (18 of 19), with the program's ir0.0 2 or 3 (the first run: 0x400 to 0x403 [infer: the 0x400
bit marks the pixel task]). [HW] s2 is not ir0 (.0 or .1) of the started program: with s2 0, 1 and
0xFFFFFFFF the program saw 3, 3 and 2; E146's reading (from the operand order only, [infer]) is not
supported in a client fill, where ir0 is a small number independent of the operands. [HW] No flag,
`#incp` or sideband value tried changed whether the program ran; the addend 0x1000 once left the
no-emit value (1 probe, twice including the repeat outside the data, in jobs that all faulted, with
a fault racing the emitted run; "no 2 or 3 seen" is not shown to be "stopped"), 0x100 started it,
[infer] the addend may be part of the address or size the PDS fetches from. [HW] The emit ends in a
fault at 0xd2000 (or a hang) every time in a client fill; the cause is not known (Q128). [infer]
Whether the simulator models an emit on the bus of a client fill was read from its code, not checked
against the data.

**What it does not show.** What the emitted program's s0 rows and addend do individually (2 rows
with 0x100 only); s1 other than the program itself; an emitpds from a firmware task (the question
the item meant); whether the fault is the emitted run's doutu, its store, or the client's missing
PDS context; what ir0 is.

**Correction, 2026-11-08 (11.27).** The measurements above are unchanged. E513 shows that a branch
over code selected by a test of `pa0` is taken by a whole 2 x 2 quad, from the test of its top-left
lane (a test of `pa0` == 0 ran the code in the pixels 0, 1, 64 and 65, == 2 in 2, 3, 66 and 67, == 1
and == 3 in none), so the 'one instance emitting' of this record was a quad of four lanes emitting,
and 'one emit' in the counts above is one quad's. E520 ran the addend over 0, 0x10, 0xF0, 0xFF,
0x100, 0x101, 0x110, 0x200, 0x400, 0x800, 0xFFF, 0x1000, 0x1001, 0x1010, 0x1100, 0x2000, 0x4000,
0x8000 and 0x10000 in 39 probes: the addends 0xFFF, 0x1000, 0x1001, 0x1010, 0x1100 and 0x2000 left
the fill's own 0x403 in 12 of 12 probes, in an interleaved order too, where 0x100 read 3 or 2 (11 of
11), so 'the addend 0x1000 once left the no-emit value' is now 2 probes of that addend and the
window of six; every one of the 39 emitting jobs faulted (37) or hung (2), still with a fault racing
the emitted run (Q145, Q128).
