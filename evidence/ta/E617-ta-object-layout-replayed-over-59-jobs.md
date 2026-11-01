+++
id = "E617"
claim = "The object layout of E541 (a vertex holds 1 + N dwords less, for each coordinate set whose format bit is set, the components its size code names minus half of them rounded up, with 1, 2, 3, 3 and 4 components for the codes 1 to 5, the format word 0x0004 in bits 31:16 and 1 + N in bits 15:8, and the four set masks) held to the 59 jobs of ta-object-format and ta-object-format2 by a rule function written for the pipeline simulator (sgx-pipe ta::object_layout): the stored dwords, the format word and the masks of 56 completed jobs agree in 56 of 56, and the three jobs that did not complete (N = 2 faulted, N = 3 and N = 8 hung) are refused as Q165 with the record named, recalled from E541 and not predicted (the rule says nothing of why they failed), 0 mismatches; a set of code 0 with its format bit set takes no component (4 of 4 completed jobs of the alt pattern)"
unit = "ta"
method = "offline, no laptop, no new run: tools/usse-asm/unit_vectors.py writes one ta-object vector for each job of ta/object-format (47) and its second run (12), the stored dwords, format word and masks read from the first object of the dumps by the dataset's recompute_p1131.py decoder (or the failure text: job faulted, job hung), and cargo test --release -p sgx-pipe replays them with the Rust rule, which refuses as Q165 the three recorded failing inputs (n, size word, format word) = (2, 5, 1), (3, 5, 1) and (8, 29, 5) and a size code the records never saw as Q070; the verdict of the 56 is fitted, because E541 states H70-F2 as written from the first run's 42 held-out jobs"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["ta-object-format", "unit-vectors-12-0"]
terms = ["PB_OBJ.FORMAT", "PB_OBJ.SET_MASKS"]
+++

**What ran.** The Rust rule takes N (the vertex program's coordinate outputs), the size word and the
format word of a job and returns the layout, or a hang or fault for the three recorded inputs, or a
refusal for a size code the records never saw (6 and 7: Q070).

**Results.** 59 of 59 vectors replay with no mismatch: 56 layouts equal the dumps' and 3 failures
are refused as Q165 with the record named (2 hangs, 1 fault, recalled from E541, not predicted:
the rule says nothing of why they failed, and the simulator returns no hang or fault for them).
The three failing inputs are inputs of the `alt` pattern, whose same settings completed at N = 4,
5, 6, 9 and 11; the Rust rule computes those, and does not predict which N fails (Q165).

**What it shows.** [HW] E541's rule, with one addition that a flagged set of code 0 takes no
component (the 4 completed alt jobs: stored 4, 5, 8 and 10 for N = 5, 6, 9 and 11 are 1 + N less
the two dwords the flagged set of code 5 saves), is implemented in the simulator's TA and gives
the dumps' layout. [infer] The flagged set of code 0 taking no component is that addition: the
record does not state it, the 4 completed alt jobs are what it was set from.

**What it does not show.** The size codes 6 and 7; the format bits other than bit 18; why the alt
pattern failed at N = 2, 3 and 8 (Q165); who reads the format word.
