+++
id = "E098"
claim = "eldd and eldq load the dword or the four dwords of element index + offset from the base when that element is below the limit (their last operand), and zeros otherwise; no cache mode (ldad's, stad's, eld's .bypassl1) makes a reload miss a store: in one instance all 21 combinations read the stored value on every pixel, and across instances the stored value is read except by 12 or 64 pixels of tile (0, 0) in 10 of 21 combinations"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/cache-control.toml, probes eld-address, eld-limit, modes and cross, fills whose pixel program runs eldd or eldq on a scratch buffer the host filled with 0xd0000000 | index, or warms a dword with ldad, stores a new value (0x12345678) with stad in a mode, and reloads it with ldad or eldd in a mode (in one instance, or the tile's top-left pixels store and the others warm, spin and reload); two runs (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-cache-control", "usse-cache-control-followup"]
terms = []
+++

**What runs.** eld-address (24 cases) and eld-limit (25): `eldd` and `eldq d, [base, index,
#offset], limit` at many indices, offsets and limits. modes (21): warm, `stad` in a mode
(none, .bpcache, .fcfill), reload in one of seven modes (`ldad`, `.bpcache`, `.fcfill`, `eldd`,
`.bpcache`, `.fcfill`, `.bypassl1`) in the same instance. cross (21): the same combinations
with writers and readers in different instances.

**Results.** eld: the index and the offset count elements of the load's size (a dword for
`eldd`, four for `eldq`); element index + offset loads when it is below the limit, and
anything at or past it gives zeros. `eldd` index 3 limit 4 loads dword 3 and index 4 gives 0;
offset 3 loads and offset 4 gives 0; index 1 + offset 2 loads dword 3 and index 2 + offset 2
gives 0; `eldq` index 1 loads dwords 4 to 7, index 0 + offset 3 dwords 12 to 15, and index 4
with limit 4 four zeros. A limit of 0 gives zeros; an index of 0x10001 is just a large index
(zeros against a limit of 0x10). A limit with bit 31 set gives zeros even at index 0 (0x80000000),
and so does index 0xffffffff against limit 4 and index 0x7fffffff against limit 0xffffffff.

Cache modes: in one instance all 21 combinations read 0x12345678 on every pixel. Across instances 11
combinations read it on every pixel in the first run, and 10 leave 12 (4 combinations) or 64 (6
combinations) pixels at the old value 0xd0000040, all in tile (0, 0), in combinations with and
without bypass modes. Tile (0, 0) is the first tile rendered, so those readers ran before any writer
had stored.

**Not shown.** Whether the tile (0, 0) pixels are a race rather than a cache is a reading, not
measured; no combination shows a stale value outside the first tile. The follow-up run again leaves
12 (5 combinations) or 64 (5) pixels of tile (0, 0) at the old value in 10 of the 21 cross
combinations, but not the same ten; the other tables repeat exactly.