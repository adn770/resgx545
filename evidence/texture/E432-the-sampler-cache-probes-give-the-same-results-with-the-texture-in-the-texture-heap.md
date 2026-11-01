+++
id = "E432"
claim = "The 24 cases of the three sampler-cache probes (a store to a sampled texel, with each fence and cache operation between) give the same results with the texture and its buffer in the texture heap (0xf0000000) as in the general heap, in 3 of 3 runs each (72 of 72 jobs)"
unit = "texture"
method = "probes/texture/sampler-cache-texheap.toml on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: the probes of texture/sampler-cache.toml with the scratch buffer (the texture) allocated in the texture heap (sgxfive-test probe --scratch-heap texture, scratch at 0xf0000000), three runs; each case compared with the stored general-heap run (probe.py's observations: the pixel, the changed scratch dwords, the failure)"
tiers = ["HW"]
date = "2026-11-07"
data = ["texture-sampler-cache-texheap"]
terms = ["T2.TEXADDR"]
+++

**Results.** texcache (18 cases), texcache-cold (2) and texcache2 (4): every case's pixels and
scratch changes equal those of the general-heap run, in each of three runs. The kernel flags the
part with the quirk SAMPLE_CACHE (DEV_QUERY).

**What it shows.** The texture region half of the test shows no erratum on this revision-3 bridge,
with the same firmware. A texture and other data at addresses that differ only above bit 28 at
once was not run. Q096 is narrowed.
