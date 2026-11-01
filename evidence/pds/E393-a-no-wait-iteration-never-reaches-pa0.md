+++
id = "E393"
claim = "With a douti that has no completion bit and no wait, pa0 never holds the iterated value at any of the 1062 pixels, whether the shader reads it at once or after 4, 16 or 64 nops, in 20 jobs; it holds 0 (888-973 pixels), 2 (72-139), 6 (8-25) and a few other values, while the same iteration with bit 29 and the wait gives the iterated x at every pixel (two runs)"
unit = "pds"
method = "probes/pds/no-wait.toml on the laptop over the cable, linux fork b5a86838ae59 with the debug option on: pds_iter_nowait.s (DOUTI0 0x800, U1 4) and pds_iter_wait.s (0x20000800, U1 0x01000004) as the primary pixel program, vtx_coords.s, a pixel shader writing pa0 out after 0, 4, 16 or 64 nops; five runs; every pixel read back"
tiers = ["HW"]
date = "2026-11-03"
data = ["pds-no-wait"]
terms = []
+++
**Reading.** A later read does not bring the value, so the no-wait iteration is not a race the
shader loses by reading early: it does not write pa0 (or writes it after the task ends). E131's
clip x in one run is not seen here.
