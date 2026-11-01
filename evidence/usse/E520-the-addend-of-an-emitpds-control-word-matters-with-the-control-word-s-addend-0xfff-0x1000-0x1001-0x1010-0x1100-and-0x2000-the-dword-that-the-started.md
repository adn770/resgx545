+++
id = "E520"
claim = "The addend of an emitpds control word matters: with the addends 0xFFF, 0x1000, 0x1001, 0x1010, 0x1100 and 0x2000 the dwords that the started PDS program stores (dword 8 and dwords 16 to 31) read 0x403, the value the fill's own run leaves, in 12 of 12 probes (6 in the first table, which ran them consecutively, 6 in the interleaved second table); of the other 27 probes, 24 read 3 or 2 (the base addend 0x100 in 11 of 11, the addends 0, 0x10, 0xF0, 0xFF, 0x101, 0x110, 0x200, 0x400, 0x4000, 0x8000 and 0x10000 once each in the first table, and 0x200 and 0x4000 in the second), 0x800 read 0x401 in the first table and 0x400 in the second (2 of 2), and 0x10 read 0x400 in the second table; every emitting job faulted (37 of 39) or hung (2 of 39, the addend 0x2000 in each table), in a client pixel task"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e): probes/usse/emit-addend.toml (19 probes of one case, one run, addends 0, 0x10, 0xF0, 0xFF, 0x100, 0x101, 0x110, 0x200, 0x400, 0x800, 0xFFF, 0x1000, 0x1001, 0x1010, 0x1100, 0x2000, 0x4000, 0x8000, 0x10000; the first run read 0x403 for the seven consecutive probes 0x800 to 0x2000, which a drift in time would also give) and emit-addend2.toml (20 probes in an interleaved order: 0x100 between the others and 0x1000, 0x1100, 0x800, 0xFFF, 0x1001, 0x1010, 0x10, 0x200, 0x4000, 0x2000 once each, base 10 times), the E488 shader and PDS program (emit_base.s with r2 changed, --pds 8 --use, --low 0x10000, --coords, one quad emitting, E513), campaign runner, a baseline triangle clean after every probe, no reload; the predictions: none (recorded, E488 had no hypothesis); the interleaving was my test of addend against time"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-emit-addend", "usse-emit-addend2"]
terms = []
+++

**Results.** The dwords read after the emit (dwords 16 to 31) and the pre-read (dword 8, which the
later instances read after the emitted run stored) hold one value per probe. First table (19 probes,
one each): 3 or 2 for 0, 0x10, 0xF0, 0xFF, 0x100, 0x101, 0x110, 0x200, 0x400, 0x4000, 0x8000 and
0x10000 (12 probes); 0x401 for 0x800; 0x403 for 0xFFF, 0x1000, 0x1001, 0x1010, 0x1100 and 0x2000.
Second table (20 probes, interleaved): 3 or 2 for 0x100 (10 probes), 0x200 and 0x4000; 0x400 for
0x800 and for 0x10; 0x403 for 0xFFF, 0x1000, 0x1001, 0x1010, 0x1100 and 0x2000. So the value 0x400
was read at 0x800 and at 0x10 (the second table), and 0x401 at 0x800 (the first table). The final
dword 0 is 0x400 or 0x401 in some of the probes that read 3 or 2 (as in E488). The job faulted (BIF
fault) in 18 and 19 probes and hung (0x2000) in 1 and 1 of the two tables.

**What it shows.** [HW] The addend of the control word changes what the PDS program's store leaves
in dword 8 and after: 3 or 2 at the base 0x100 and at every addend run below 0x800 and above 0x2000
but 0x10 once (24 of the 27 probes outside the 0x403 group read 3 or 2, the other three being 0x800
twice and 0x10 once), and 0x403 (the fill's own run) at 0xFFF to 0x2000 in 12 of 12 probes,
reproduced in an interleaved order, so not a drift in time. [infer] The PDS program's emitted run
does not store (or stores the same) in that range; the addend may select an address or size the PDS
fetches from, whose effect at 0x800 (0x400, 0x401) is a third state, which 0x10 also read once, so
the 0x400 value is not tied to the 0x800 addend. The shape (0x403 from 0xFFF to 0x2000; no addend
from 0x801 to 0xFFE was run) is not an interval rule measured by a step finer than the values run.
All of this was measured in client pixel tasks (fills), not in firmware tasks, and by one emitting
quad (E513).

**What it does not show.** Addends between the ones run (0x801 to 0xFFE, 0x2001 to 0x3FFF), several
emits with different addends, the cause of the fault, a job that does not fault (none was found, so
the addend was measured in jobs that all ended in a fault or a hang: the emitted run raced the
fault, as E488 says).
