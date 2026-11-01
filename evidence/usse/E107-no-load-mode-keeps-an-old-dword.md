+++
id = "E107"
claim = "No load cache mode keeps an old dword when the host writes it while the job runs: with 1024 reloads, in two runs, ldad, ldad.bpcache, ldad.fcfill, eldd, eldd.bpcache, eldd.fcfill and eldd.bypassl1 each show pixels that read the old value for at most 149 reloads and the host's value on every later one, and no pixel ends on the old value; every ready store (stad, stad.bpcache, stad.fcfill) reached memory, seen by the host 0 to 1935 microseconds after the submit"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/cache-control.toml, probes usse-cache-control-late-n64, -late-n1024 and -late-cross (client fill on late_poll.s with the host writing scratch dword 64 = 0x12345678 once dword 128, the ready dword, leaves its fill: a warming load of dword 64, a store of 1 to dword 128 in a store mode, then 64 or 1024 reloads of dword 64 in a load mode, counting those that read the old value), 30 cases, two runs (the second is the follow-up run)"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["usse-cache-control", "usse-cache-control-followup"]
terms = []
+++

**What runs.** The pixel is the number of reloads that read the old value `0xD0000040` (28 low
bits), plus `0x10000000` when the last reload read the host's `0x12345678`. The host polls dword 128
after the submit and writes dword 64 when it leaves its fill, so a pixel's reloads before the write
read the old value by necessity. The 11 cases of each late probe are the reload modes `ldad`,
`.bpcache` and `.fcfill`, `eldd`, `.bpcache`, `.fcfill` and `.bypassl1` after a plain warming load;
`ldad` after a `stad.bpcache` or `stad.fcfill` ready store; and `ldad` and `eldd.bypassl1` with no
warming load. The cross probe warms in one mode and reloads in another (8 cases). The host's value
was written in all 30 cases of each run.

**Results.** Pixels that completed their reloads after the write read the new value on every reload
(the bulk: 1792 to 2048 of 2048). Pixels that were mid-loop at the write read the old value for a
while, then the new one to the end:

| probe | run 1: pixels mid-loop; old reloads | run 2: pixels mid-loop; old reloads |
|-------|-------------------------------------|-------------------------------------|
| late-n64 (64 reloads) | 6 to 64 per case; 1 to 58 | 1 to 64 per case; 1 to 63 |
| late-n1024 | 0 to 64 per case; 1 to 149 | 0 to 64 per case; 1 to 143 |
| late-cross | 8 to 64 per case; 1 to 145 | 60 or 64 per case; 1 to 139 |

Every reload mode has mid-loop pixels in the 1024-reload probes in at least one of the two runs, and
in the cross probe every warming and reload combination does. Mid-loop pixels come mostly in groups
of 60 or 64 pixels, with a few cases of 2 to 13. No pixel ends on the old value in any of the 38
cases (19 a run) of the 1024-reload and cross probes.

In the 64-reload probe, groups of 64 to 192 pixels read the old value for all 64 reloads and ended
on it: in run 1 for `eldd.bpcache`, `eldd.fcfill`, `eldd.bypassl1`, `ldad` after `stad.fcfill` and
`eldd.bypassl1` with no warm load (64, 64, 128, 128 and 128 pixels, the host seeing the ready dword
after 0 us); in run 2 for `ldad.bpcache` (127), `eldd.bypassl1` (192), `ldad` with no warm load (64,
the host saw the ready dword at 778 us) and `eldd.bypassl1` with no warm load (128). That fits
pixels whose 64 reloads ended before the write **[infer]**.

The ready dword (`stad`, and the `stad.bpcache` and `stad.fcfill` cases) appeared to the host 0 to
1935 us after the submit; 0 means before the first poll. Baselines before and after every probe were
exact; the visibility counters read 0.

**What it shows.** Against the host as writer, no load mode returned a value held from an earlier
load beyond about 150 reloads of 1024, and every pixel that ran long enough read the new value to
the end; the ready stores of all three store modes reached memory. Whether a mode could keep the old
value for a shorter time, or whether the 64-reload groups that ended on the old value ran before the
write rather than after, is not told by these end states.

**Not shown.** Store latency: the time shown includes the job's start and the host's poll. The runs
are races against the host's timing and give no vectors.
