+++
id = "E147"
claim = "Run through the repository's decoder and simulator, the 29,137 vectors the probe runs gave (27,174 USSE, 1,963 PDS) show no mismatch: 6,028 scalar USSE vectors, 135 pixel vectors and 634 PDS vectors pass, 19,217 + 26 + 235 stop as unsupported, and 166 USSE (165 scalar and 1 pixel) and 18 PDS vectors are left out because one instance cannot reproduce their readback; 170 of the 219 USSE forms and 24 of the 27 PDS forms have a passing vector"
unit = "usse"
method = "offline: every raw readback of the probe runs of the data repository (the first and the follow-up rounds, usse, pds, texture and the other units whose probes carry a program) was converted with tools/usse-asm/vectors.py into instruction vectors (program words as sent, initial state, readback), and cargo test --release -p sgx-sim ran them through the decoder and the simulator as crates/sgx-sim/tests/vectors.rs does, one run; nothing ran on the hardware for this record"
tiers = ["HW"]
date = "2026-11-01"
data = [
    "vectors-usse", "vectors-usse-followup", "vectors-pds", "vectors-pds-followup",
    "vectors-texture", "vectors-isp", "vectors-isp-followup", "vectors-mte", "vectors-pbe",
    "vectors-pbe-followup", "vectors-ta", "vectors-vdm", "vectors-vdm-followup", "pds-alu",
    "pds-alu-followup", "pds-data-words", "pds-data-words-followup", "pds-douta",
    "pds-douta-followup", "pds-douti-fields", "pds-douti-fields-followup", "pds-end-of-tile",
    "pds-iteration-sources", "pds-iteration-sources-followup", "pds-iteration-waits",
    "pds-iteration-waits-followup", "pds-load-store", "pds-memory", "pds-memory-followup",
    "pds-moves", "pds-moves-followup", "pds-pixel-event", "pds-pixel-event-followup",
    "pds-task-limits", "pds-timer", "pds-timer-followup", "pds-vertex-programs",
    "texture-sampler-cache", "usse-alpha-test", "usse-branch", "usse-cache-control",
    "usse-cache-control-followup", "usse-colour-ops", "usse-constant-banks",
    "usse-constant-banks-followup", "usse-decoder-vectors", "usse-dot-products",
    "usse-dual-issue", "usse-efo", "usse-emits", "usse-filter-banks", "usse-filter-control",
    "usse-filter-gain", "usse-filter-sets", "usse-filter-taps", "usse-flags",
    "usse-float-functions", "usse-float-minmax", "usse-float-misc", "usse-fmad", "usse-fmad16",
    "usse-form-coverage", "usse-gradients", "usse-helper-instances", "usse-indexing",
    "usse-instance-masking", "usse-integer", "usse-integer-dot", "usse-internal-registers",
    "usse-lane-integer", "usse-loop-timing", "usse-memory", "usse-moe", "usse-moe-followup",
    "usse-movc", "usse-numbered-modifiers", "usse-numbered-modifiers-followup",
    "usse-output-registers", "usse-pack", "usse-phases", "usse-predicates", "usse-quad-lock",
    "usse-quad-lock-followup", "usse-repeat", "usse-rlp", "usse-sample-rate",
    "usse-test-channels", "usse-tests", "usse-unorm8", "usse-video-filters",
    "usse-video-filters-followup", "usse-video-ops", "usse-write-masks",
]
terms = []
+++

**What runs.** Each case of a probe table is a program the hardware ran as the shader of a 64 x 32
fill (or of a 64 x 64 triangle), with its readback: `o0`, the scratch dwords that changed and,
where the run reported them, every pixel. A PDS case is a fill's secondary program followed by
the fill shader that stores the secondary attributes. The converter keeps the program words as
the run sent them (all 29,137 vectors are recorded, none rebuilt), the initial state and the
readback, in 1,932 files of 96 directories (77 probe tables, each with a follow-up directory where it
was run again; doc/specs/vectors.md). The simulator runs
a scalar vector as one instance, a pixel vector as the fill's 2 x 2 quads and a PDS vector as
the fill's secondary; a form, operand or input it does not model stops it as "unsupported",
which is not a pass. 115 USSE vectors record a job the hardware refused or lost and are not
compared. The triangle-host vectors read back the scene's output rather than the shader's, so
they are not compared either: 1,076 PDS vectors (82 of them failed jobs) are never run. The
other 94 failed PDS vectors are run, and a job the hardware lost to a hang or a fault is
compared against a program that hangs or faults; they are inside the PDS results.

**Results.** Scalar USSE vectors: 6,028 pass, 19,217 unsupported, none differ. Pixel vectors:
135 pass, 26 unsupported, none differ. PDS vectors: 634 pass, 235 unsupported, none differ.
Of the 219 USSE forms, 180 have a vector and 170 have a passing one (205 have semantics in the
simulator); of the 27 PDS forms, 25 have a vector and 24 a passing one.

The unsupported scalar vectors are mostly `firh` (16,521, because the result depends on the
coefficients the job loaded, which the vector does not carry; E078 gives the filter block), with
1,126 more of `firh` centred below byte 0 and 477 that read latch bytes the task did not write.
Then 687 of `atst8` (E083), 87 of `moest`, 64 + 16 + 8 of `smoa` addressing modes the
simulator does not take, 22 of `setm`, 16 of `setfc`, 20 `smlsi` with non-zero limits, and a few
of `eld`, `efo.gpiext` across the quad, fetches past the temporaries and 28 texture formats. The
unsupported PDS vectors are programs that read an input register the task does not define
(127, the `ir` specials and the spare registers), the 76 index sweeps the instruction
tables do not decode, `pc` as a move source (10), a few open ports and moves, and `tim`
reads (8).

**Left out.** 165 scalar vectors and one pixel vector differ from what one instance of the
simulator gives, for a reason that is not the simulator's: 100 vectors of loop-timing
run loops of 100,000 to 10 million iterations, past the simulator's limit of 10,000 steps; 45
vectors of cache-control (the modes and the late-load cases, in both rounds) load and store
one dword that all 2048 instances share, so the readback is whichever instance's store came
last; 20 vectors of sampler-cache read a texel after a store to it, which the sampler cache
hides and the simulator does not model. Pixel (38, 6) of the internal-registers bank7 case 16
reads 0x511eb000 where the simulator gives 0x511e7000 (an i127 read; no record explains it).
18 PDS store vectors (9 programs, each in both rounds) depend on the job before them or differ
between two runs of the same program (E144 gives the store totals that fault and the jobs that
fault after a fault). Each of these is left out by the simulator's skip list with its reason;
the triangle-host vectors are left out by the kind of run (see "What runs").

**Not shown.** That the unsupported vectors agree: 19,243 USSE and 235 PDS vectors say nothing
about the simulator until their semantics are modelled. The pass count is only as strong as
the inputs the cases chose, and each table was run once in each round it belongs to. The words of the firmware's
microkernel are not covered by these vectors.
