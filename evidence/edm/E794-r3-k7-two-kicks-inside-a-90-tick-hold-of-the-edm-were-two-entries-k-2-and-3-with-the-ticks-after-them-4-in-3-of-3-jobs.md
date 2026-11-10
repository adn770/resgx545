+++
id = "E794"
claim = "R3-events stage k7 (Q290 K7; a 90-tick hold of the EDM by ring_hold, S2b's blob byte for byte, n = 1508279, hold 2262434 units, window 2, 160 ms open): with no kick the exit was followed by a burst of 4 entries (k7-ctl: 16 entries, 0 kick entries, the ticks after the hold K 2, ccbctl[0] 2 to 2; S2b's ctl90, fit 3 of 3 rows), with one GETMISCINFO kick 3 ms into the hold the burst was 5 with one kick entry (K 2), the ticks after it K 3 and ccbctl[0] 3 (k7-one; S2b's kick90 and E746's identity, fit 4 of 4 rows), and with two real kicks inside the hold, the debugfs xfer_sync's TRANSFER and, 50 ms later, its PROCESS_QUEUES, both answered (read ok), the ring held two kick entries in 3 of 3 jobs (k7, k7-r2, k7-r3), K 2 and 3 in that order, all inside the burst after the hold, the ticks after them K 4 and ccbctl[0] 4 (burst 6, 5 and 6 entries): H-EACH (each kick is delivered as its own entry) held in every row of the three jobs (5 held-out rows and 10 replicate rows) and H-MERGE (one entry and a read that times out) is refuted, 3 of 3, its 2 held-out and 4 replicate rows being the FAILED rows the scorer printed; the hold band (the kernel's hold length, the knob of S2 run 3) held in 5 of 5 jobs (2262433 to 2262436 units against 2262434); each ring held 16 entries and dropped 51 to 54 (k7-ctl 51, k7-one 52, k7 53, k7-r2 51, k7-r3 54), all of them ticks after the burst, which the 16 rungs of slot 0 could not hold, so the drops are harmless to every row (no drop inside the burst: late ticks were read in all five jobs)"
unit = "edm"
method = "R3-events stage k7 of the question-closing pass, round 2 (5 jobs: k7-ctl, k7-one, k7, k7-r2, k7-r3; blob asm/ring_hold.s, 747 instructions, sha256 fa0f79dbb5864187516febf9c96f6ceea944e5abf6ae69b5acbeb9ac8a0ac168, S2b's, accepted by the landed tools/fwtask verifier, armed with own_arm slots=0xf entry=0,1,2,3, ldr of CR_TIMER only, no str), run 1794308087-28809 of the dataset edm-closing-r3-events, on the laptop (host cedar), 2026-11-10 from 11:54:47 laptop time (10:54 UTC) (the gate was stage b's kept stage.json, exit 8), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71); each job a debugfs reset and an arm first (K0 = 2 after the arm, the free instrument ccbctl[0] read against it); the hold, n = ((90 + 0.5) * 25000 - 82) / 1.5 = 1508279 (S2b's, hold = 1.5 n + 15 units, about 90.5 ms) triggered by the host, window 2 opened 160 ms; the kicks: none (k7-ctl), one miscinfo read 3 ms into the hold (k7-one, S2b's kick90), or the landed debugfs file xfer_sync (k7, k7-r2, k7-r3), which under the kernel's lock submits a TRANSFER (kick 1), sleeps 50 ms, submits PROCESS_QUEUES (kick 2) and waits for the SW event, so two real kicks 50 ms apart, both inside a hold that began a few ms before (two miscinfo reads cannot both fall inside the hold, because every debugfs command waits for its answer under the kernel's lock: the preflight reading of the fork's sgxfive.c); the ring read twice (the second equal to the first); the entries are those from the window's own CR_TIMER stamp on, the burst those within 2000 units of the hold's exit stamp, kick entries those with pa0 = 0 and pa1 bits 23:0 = 0x100; scored by the frozen score/score_r3.py k7 (out/score-k7.txt); the freeze rests on file times, hashes and the author's word; the frozen rows for the one-kick and no-kick jobs were S2b's (fit), those for the three xfer_sync jobs H-EACH against H-MERGE (held out and replicate); the reading of the count byte at arrival rather than at service, and of the drops, is post hoc"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-r3-events:out/k7/"]
terms = ["Event Data Master (EDM)", "CR_EVENT_KICK", "CR_EVENT_TIMER"]
+++
**What ran.** E752 held the EDM for 90 ticks and sent one kick into the hold: it was queued and
logged once after the hold (3 of 3). Whether two kicks inside one hold are two entries (H-EACH) or
one with the second lost or timed out (H-MERGE: the queue merges the kick bit) was open; H-SAT
(the queue's capacity) was a third reading. The landed `xfer_sync` file gives two kernel kicks 50 ms
apart under one lock.

**Frozen verdict** (`out/score-k7.txt`). `hold band held; two-kick outcomes: EACH [k7, k7-r2,
k7-r3]`; Q290 rows: fit 7 held, 0 FAILED; held out 5 held, 2 FAILED; replicate 10 held, 4 FAILED;
control 3 held, 0 FAILED; H-MERGE refuted. The FAILED rows are not misses of the design: each is
one of H-MERGE's two rows (one kick entry, read does not return) in a job where two entries came
and the read answered, 1 job x 2 rows held out and 2 jobs x 2 rows replicate. Every H-EACH row held.

**Results [HW].** Per job (entries after the window's stamp, burst, kick entries with K, the
ticks after them, ccbctl[0], drops):

| job | hold units | burst | kick entries K | ticks after | ccbctl[0] | drops |
|---|---|---|---|---|---|---|
| k7-ctl | 2262434 | 4 | none | 2 | 2 to 2 | 51 |
| k7-one | 2262433 | 5 | 2 | 3 | 2 to 3 | 52 |
| k7 | 2262436 | 6 | 2, 3 | 4 | 2 to 4 | 53 |
| k7-r2 | 2262434 | 5 | 2, 3 | 4 | 2 to 4 | 51 |
| k7-r3 | 2262434 | 6 | 2, 3 | 4 | 2 to 4 | 54 |

Every ring held 16 entries. k7-r2's burst of 5 has both kick entries inside it (the scorer's check)
and is one fewer than k7's and k7-r3's 6; the frozen rows state no burst size for the xfer_sync
jobs (only 4 for the no-kick control), and the difference is not examined here.

**Reading [infer, post hoc].** The kicks' own entries carry K and K + 1, the values before each
bump, although both were served after the hold, when both bumps had happened: the count byte of an
event is formed when the event arrives (the kick's write), not when the task serves it. The
ticks after the hold carry K + 2 (4), so the byte counted both writes made while the task held the
EDM. This does not separate whether the hardware counts the writes (H-HWC) or reads the kernel's
kicker word (H-KW): the kernel bumps before each of these writes too. The 51 to 54 drops are the
passes after the burst that the ring's 16 rungs could not hold in a 160 ms window (the hold is 90.5
ms; 16 plus the drops is 67 to 70 entries); they sit after the burst (the scorer would call a job
with drops before the burst's end cannot tell, and none was) and k7-ctl has the same 51.

**Not shown.** More than two kicks in a hold (the queue's capacity, H-SAT, for kicks: E751's
four-tick limit is for ticks), a kick and a job's events together in a hold longer than E752's,
and the hardware's own order of latching against the bump.
