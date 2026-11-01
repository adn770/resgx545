+++
id = "E479"
claim = "A wdf drcN does not wait for loads counted on other counters that were issued after the loads it waits for: in a client pixel task, eight cases run ten times each, of which the data hold one run: in that run two ldr on drc2 followed by four ldad on drc1 and a wdf drc2 only leave all four ldad registers at their markers (case 7) and four ldad on drc1 followed by four on drc0 and a wdf drc1 only leave the drc0 registers at their markers (case 3), and the other six cases return all their data; nine more runs of the table, kept in the scratch tree and not in the data, were recounted by the reviewer together with the dataset's: markers in case 7 in 10 of 10 runs, in case 3 in 2 of 10 runs (the dataset's run and one of the nine), and none in the other six cases in 10 of 10 runs each (60 of 60 case readings), counts a reader of the data cannot recompute"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1122 (sha256 ec423efc3d9aa34576553da70916be4ceb715a729cbc02cc4bd89fa052511244): probes/usse/fence-batching.toml probe counters (8 cases) run ten times, one process each: the campaign run (one of the ten, the only one in the dataset), a whole-table run by probe.py and eight runs of this probe alone by probe.py (the other nine are not kept in the data, only in the scratch tree, debug/phase11/p1124/runs, where the reviewer recounted all ten; per-run timing was not logged); the eight repeat runs overlapped in time with the ZLS rerun of E489 and E490 on the same GPU (they ran between two ZLS cases and neither is affected: every ZLS case reproduced the 11.22 counts)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-fence-batching"]
terms = []
+++

**What runs.** Four `ldad` on drc0 (lines 0 to 3) and four on drc1 (lines 4 to 7) into r10-r17
preset to markers, with `wdf drc0` only, `wdf drc1` only, or both; two cases issue the drc1 loads
first; `ldr #7, #8` on drc2 and drc3 with the matching wdf (control), `ldad` x 4 on drc0 then `ldr`
x 2 on drc3 with `wdf drc0` only, and `ldr` x 2 on drc2 then `ldad` x 4 on drc1 with `wdf drc2`
only. The registers are stored after the wdf and the markers counted.

**Results (markers seen in the later-issued, unwaited loads; ten runs, of which one is in the
data and nine are scratch runs recounted by the reviewer).**

| case | waited | unwaited loads | runs with markers |
|---|---|---|---|
| 4 ldad drc0 + 4 ldad drc1, both wdf (control) | both | none | 0 of 10 |
| drc0 x 4, then drc1 x 4 | wdf drc0 | drc1, issued after | 0 of 10 (all data) |
| drc0 x 4, then drc1 x 4 | wdf drc1 | drc0, issued before | 0 of 10 |
| drc1 x 4, then drc0 x 4 | wdf drc1 | drc0, issued after | 2 of 10 (4 markers each) |
| drc1 x 4, then drc0 x 4 | wdf drc0 | drc1, issued before | 0 of 10 |
| ldr x 2 drc2, ldr x 2 drc3 | both (control) | none | 0 of 10 |
| ldad x 4 drc0, then ldr x 2 drc3 | wdf drc0 | ldr on drc3, issued after | 0 of 10 |
| ldr x 2 drc2, then ldad x 4 drc1 | wdf drc2 | drc1, issued after | 10 of 10 (4 markers each) |

**What it shows.** [HW] In a client pixel task, a wdf is not a barrier for loads of other counters
that were issued after the loads it waits for: the four ldad on drc1 after two ldr on drc2 still
hold their markers when `wdf drc2` returns in all ten runs, and the four ldad on drc0 after four on
drc1 in two of ten. The 10 of 10, 2 of 10 and 60 of 60 are counts of scratch runs recounted by the
reviewer; the data hold one run, in which cases 3 and 7 show their markers and the other six none.
Loads issued before the waited loads were always complete. Loads issued after a wait on four ldad
(which takes longer than a wait on two ldr) were complete in 28 of 30 runs (cases 1 and 6, markers
in 0 of 10 runs each, and case 3, in 2 of 10), so what has landed is a matter of timing (a guess:
no per-run timing was logged): [infer] each counter counts its own loads and the wdf returns when
its own count is zero, the other counters' loads being in flight or not. A program that waits for
several counters waits on each. Of the four cases where the documented model (a wdf waits for its
own counter only) predicted markers, one (ldr drc2 then ldad drc1) shows them every run, one (drc1
then drc0) in two runs, and two (drc0 then drc1, ldad drc0 then ldr drc3) never; the runner's
verdict was "none of the hypotheses fits", recorded as measured.

**What it does not show.** The latency of a load in time; why four ldad issued after a wait on four
ldad of another counter were complete in 8 or 10 of 10 runs, and four ldad issued after a wait on
two ldr in none (Q130); the nine runs behind the counts, which are not in the data. All of this was
measured in client pixel tasks (fills), not in firmware tasks.
