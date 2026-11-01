+++
id = "E299"
claim = "VDM state word 1 with bits 11:9 = 7 hangs some jobs and completes others, on the library's triangle job and on the probe's: in this run, of six jobs with it, the three with every pixel read back hung and the three without completed, whatever the render dump or the pixel program; earlier runs went the other way (E060's sweep hung without the readback and its probe completed with it, two runs each), so the readback does not decide the hang from run to run [infer: two tables]; a library job that completes draws the job's own image and leaves render memory byte for byte that of bits 11:9 = 2; one run of each job"
unit = "vdm"
method = "probes/vdm/state1-split.toml on the laptop, linux fork with the debug option on: its script state1-split.sh runs sgxfive-test tri (the library's triangle job) unpoked, then with vdm:1^=0xa00 alone, with every pixel read back (--pixels) and with the render memory dumped (--dump-render); its probes run the probe's triangle (probe --tri) with vdm:1 = 0x0a022e05 and a pixel shader writing green (pixels read, render dumped), with the original probe's o0 copy and no readback or dump, and as the original probe (o0 copied, pixels read, dumped); one run each; dumps read with pbdump.py"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["vdm-state1-split", "ta-te-psg"]
terms = ["VDM_STATE1.BITS11_9"]
+++

**What runs.** The sweep case of E060 and E185 (`vdm:1^=0xa00`, bits 11:9 from 2 to 7) split by
what the sweep and the earlier probe did differently, one job each, after an unpoked control.

**Results.**

| job | word | readback | dump | outcome |
|---|---|---|---|---|
| library, control | 0x0a022405 | none | none | completes, 1062 triangle pixels |
| library | 7 | none | none | completes, 1062 triangle pixels, hash of the control |
| library | 7 | every pixel | none | hangs (4096 pixels at the sentinel) |
| library | 7 | none | dumped | completes, the control's image |
| probe, green shader | 7 | every pixel | dumped | hangs |
| probe, o0 copied | 7 | none | none | completes, 3792 background and 304 o0 leftovers |
| probe, o0 copied | 7 | every pixel | dumped | hangs |

The library job's dump with bits 11:9 = 7 equals, dword for dword, the dump of the library job
with the job's own word (2) of probes/ta/te-psg.toml's control. The two hung probes' memory,
saved after the failure, holds no object and no written TA data page; the earlier probe of the
same word (E185), which completed, held the triangle's object.

**What it shows.** In this run the hangs follow the readback exactly: every job with every pixel
read back hung, every job without it completed, in both job builders and with either pixel program.
The run does not show that the readback causes them. The earlier table ran the other way in both its
runs: its sweep, which reads no pixel back, hung, and its probe, which reads every pixel, completed
(E060, E185). That the value hangs some runs whatever the readback rests on those two tables
together [infer]; the five-copy job with its own words also hung once with every pixel read back
(E300, first run), so a readback hang is not peculiar to 7 [infer: one case]. When a library job
completes, 7 tiles and renders as 2 does [infer: one completed dump]. What decides a hang is not
shown.
