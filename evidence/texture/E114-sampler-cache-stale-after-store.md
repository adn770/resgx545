+++
id = "E114"
claim = "The texture sampler keeps what it fetched in a cache that USSE stores do not update: after a pixel samples a texel, a store to it or to the texel beside it is not seen by the next sample, with idf + wdf and with every ci, cf and cfi level and flag between (17 cases); a texel the sampler has not fetched shows the store (the texel far away, and the cold cases); idf pixelbe and smp.syncs hang a fill"
unit = "texture"
method = "on the laptop, linux fork with the debug option on: probes/texture/sampler-cache.toml, probes texture-sampler-cache-texcache, -texcache-cold and -texcache2 (client fill on dump.s: a 16x16 texture at scratch + 0x2000, point sampling, no mipmaps, texel 0 the host fill 0xD0000800, sampled with smp2dreplace), one probe a group, one run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["texture-sampler-cache"]
terms = []
+++

**What runs.** Each pixel samples texel (0, 0), stores `0x12345678` to a texel, and samples
again with the case's fence or cache operation between; the second sample is the pixel. Every
case that completes is uniform over the 2048 pixels.

**Results.**

| between the first sample and the second | second sample |
|-----------------------------------------|---------------|
| no store (control) | `0xd0000800` (old) |
| store, no fence | old |
| store, `idf drc0, bif` + `wdf drc0` | old |
| the same, then `ci`, `cf` or `cfi` on level `#1`, `#2` or `#3` (nine cases) | old in all nine |
| the same, then `ci` or `cfi` with `.global`, `.dm_nomatch` or both, on `#3` (6) | old in all six |
| store, `idf drc0, pixelbe` + `wdf drc0` | the job hung |
| store, `idf` + `wdf`, the second sample `smp2dreplace.syncs` | the job hung |

Granularity and the cold case:

- Sample (0, 0), store to the texel beside it, (0, 1) (twiddled index 1), sample (0, 1): old
  (`0xd0000801`).
- Sample (0, 0), store to (0, 8) (index 64), sample (0, 8): the new value `0x12345678`.
- No first sample: a store and then a sample, with or without `idf` + `wdf`, read the new value
  (both cases).

Baselines before and after every probe were exact, hangs included; the visibility counters
read 0.

**What it shows.** The sampler holds what it fetched in lines that span at least the two
neighbouring texels (8 bytes, a texel being one dword) and do not reach the texel 64 texels (256
bytes) away, and USSE stores do not update or invalidate them. None of the cache operations tried
reaches that cache, whatever level or flag they carry. A texel the sampler has not fetched reads
through to memory. `idf` with `pixelbe` and a `.syncs` sample wait for something a fill does not
give **[infer]**.

**Not shown.** The line size between 8 and 256 bytes; whether a job boundary or the firmware
invalidates the sampler cache. One run.
