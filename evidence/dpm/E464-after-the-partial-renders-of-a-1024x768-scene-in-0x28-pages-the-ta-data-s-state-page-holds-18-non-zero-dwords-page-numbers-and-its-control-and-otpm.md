+++
id = "E464"
claim = "After the partial renders of a 1024x768 scene in 0x28 pages the TA data's state page holds 18 non-zero dwords (the ten printed read like page numbers) and its control and OTPM pages hold none, in 2 of 2 runs; a second job's dump holds 18 with other page numbers and flipping the second render's flag 0x8 changes nothing; a state page filled with a ramp keeps 990 of 1024 dwords, 34 leaving the ramp, and the image is unchanged; 0x0740 reads 0 after all 20 jobs and after writes of 0x200 and 0x3fe00 (2 of 2 each)"
unit = "dpm"
method = "probes/dpm/partial-state-page.toml (partial-state-page.sh) on the laptop (direct cable): sgxfive-test tri --width 1024 --height 768 --keep-overflow --dump-render DIR --dump-each --regs 0x0700-0x0750 on parameter buffers of 0x28 and 0x422 pages, one and two renders, a kernel poke ta:7^=0x8 on the second, debugfs tadata_fill of page 6 with a ramp, kregnow 0x0740 = 0x200 and 0x3fe00, the dumped control, OTPM and state pages reduced to their non-zero dwords, two runs of each of 8 cases"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["dpm-partial-state-page"]
terms = ["CR_DPM_TASK_STATE", "CR_DPM_STATE_BASE0", "CR_DPM_STATE_CONTEXT_ID"]
+++

**What runs.** E456 could not dump the TA data of an overflowing scene: the tool stopped at the
first failed job. `tri --keep-overflow --dump-render DIR --dump-each` (new in this phase) counts
the overflow, goes on and copies the kernel's render_tadata after every render as tri.N.tadata.bin.
The 1024x768 triangle (207456 pixels) on a parameter buffer of 0x28 pages overflows and the
library's background paints what the partial renders left; the dumps' control (0x4000), OTPM
(0x5000) and state (0x6000) pages are reduced on the laptop. Cases, two runs each, the GPU reset
before each: P1 one render; P2 two renders; P3 two, with the second's render flags flipped by 0x8
(`ta:7^=0x8`); P4 one render with debugfs `tadata_fill 6 0xa5000000 ramp` writing page 6 (the state
page) with a ramp (dword i = 0xa5000000 + i) before the kick; P5 the same ramp on the whole buffer
(0x422 pages, no partial render); P6 and P7 one render with 0x0740 written 0x200 and 0x3fe00 by
kregnow before it; P0 the whole buffer, nothing poked.

**Results** (the two runs of every case gave the same lines):

| case | job | triangle pixels | control and OTPM pages | state page (0x6000) |
|---|---|---|---|---|
| P0 whole buffer | ok | 207456 | 0 non-zero | 0 non-zero |
| P1 0x28 | overflowed | 162544 | 0 non-zero | 18 non-zero: 0x008=00010009 0x00c=00000009 0x010=0001000e 0x014=0000000e 0x028=0002000a ... |
| P2 0x28, 2 renders | both overflowed | 162544, 162544 | 0 non-zero | render 1 as P1; render 2 18 non-zero: 0x008=0001001d 0x00c=0000001d 0x010=00010022 ... |
| P3 as P2, second flag 0x8 | both overflowed | 162544, 162544 | 0 non-zero | as P2 |
| P4 0x28, ramp | overflowed | 162544 | 0 non-zero | 1008 non-zero, 990 equal to the ramp |
| P5 whole buffer, ramp | ok | 207456 | 0 non-zero | 1024 non-zero, all 1024 equal to the ramp |
| P6 0x28, 0x0740 = 0x200 | overflowed | 162544 | 0 non-zero | as P1 |
| P7 0x28, 0x0740 = 0x3fe00 | overflowed | 162544 | 0 non-zero | as P1 |

Register 0x0740 (the tool's `--regs 0x0700-0x0750` after each job) read 0x00000000 after all 20
jobs of the table, 16 of them overflowed; the kernel log shows each of the 4 writes (0x200 twice,
0x3fe00 twice) reading 0x00000000 at once. 20 dumps in all (P2 and P3 give two): in each the
control and OTPM pages hold nothing, and the state page holds nothing after a whole-buffer render.

**What it shows.**

- A job with partial renders leaves 18 non-zero dwords in the state page from offset 0x008 [HW].
  The tool prints ten of them: the first, second and fifth pairs read (1<<16 | n) and n
  (00010009, 00000009; 0001000e, 0000000e; 00010014, 00000014), the third (0002000a, 0000000c) and
  the fourth (0003000f, 00000013) do not; the other eight are not in the data. A second job's dump
  holds 18 non-zero dwords with other values in the same places (0x1d and 0x22 for 0x09 and 0x0e)
  [HW]. The control and OTPM pages stay zero [HW].
- The ramp shows 34 of the page's 1024 dwords left the ramp (the 18 non-zero ones and 16 zeros),
  not the whole page; the other 990 keep the poked value [HW]. That the store wrote those 34 is a
  reading [infer].
- The poked state page changed no image: the 0x28 job drew the same 162544 triangle pixels with the
  ramp as without, so a load of the state page before the kick, if the kick makes one, did not read
  the ramp [infer: the store overwrites what the load would read, and no poke was possible between
  a partial render and the final one].
- A write to register 0x0740 does not stay beside a partial render either (4 of 4 writes read 0 at
  once, 0 after the jobs) [HW].

**What it does not show.** Whether a DPM load task reads the lists back (a poke between the partial
render and the final render is not possible with these switches), what the 18 values count, and
what sets the fields of 0x0740.

**Provenance.** linux fork commit 6ee9501832af with the debug option on, module srcversion
14D099861204842EA496D85 (the installed module file and the loaded module, read from /sys/module,
were equal; the run prints both and stops if they differ), sgxfive-test sha256
fa7592a6170712ed0080066c56602304607ed31ec608afd66441a597587675a7 (built from this phase's overlay
source as it stood at the run, named in each env.toml), the laptop over the direct cable.
