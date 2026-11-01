+++
id = "E422"
claim = "In seven hung pixel-task jobs (five with recovery held, two without) the render memory dump holds the object in the parameter buffer every time, and the TA data holds 71 non-zero dwords in the five held dumps and none in the two unheld ones; the three held VDM state hangs have no object at the start of the buffer; the object E186 found missing is not reproduced"
unit = "render"
method = "probes/render/hold-hang-repeat.toml (hold-hang-repeat.sh, the staged jobs of vdm/state1: the pixel-task control and VDM state word 1 bits 15:13 = 0) on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: the pixel control held five times, not held twice, the VDM job held three times, the render memory dumped before the recovery and its non-zero dwords counted, the PB page count (debugfs render_pb_pages, 0x422 each time) printed before each of the five held pixel-task jobs (10 hung jobs and 18 reset lines: two for a held job, one for an unheld one)"
tiers = ["HW"]
date = "2026-11-07"
data = ["render-hold-hang-repeat"]
terms = ["VDM_STATE1.BITS15_13", "Parameter Buffer (PB)"]
+++

**What was seen.** All five held pixel-task dumps: param 0x464000 bytes with 1147 non-zero dwords
starting 0x0 = 0x04000004, 0x4 = 0x00030004, 0x8 = 0x0c000080 and the triangle's vertices (the
object), tadata 71 non-zero dwords (0x4000 = 0x04000000 and the region headers). The two unheld
jobs: the same 1147 dwords in param and tadata with no non-zero dword (the recovery had cleared it
before the dump). The three held VDM hangs: param 1066 non-zero dwords from 0x422004 (0xffff0002,
0x00010003, ...: the index list pages) and no object at 0, tadata with no non-zero dword.

**What it shows.** The object of the hung pixel-task job is in the parameter buffer in seven of
seven dumps (and in E318's), held or not; the TA data survives a held hang and not a recovery.
E186's missing object is not reproduced; its dump may have been taken after the TA data's clearing
and from another job [infer].

**What it does not show.** The page table of the PB before the job (only the page count was
printed); fresh boots, which this session could not do.
