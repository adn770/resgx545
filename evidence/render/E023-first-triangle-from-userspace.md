+++
id = "E023"
claim = "A render job submitted from userspace draws the first triangle exactly on the laptop: ten renders, at 64x64, at 128x96, at 64x64 on a context sized for 256x256 targets and at 64x64 after a faulting render, each with every pixel as the CPU reference computes it; one sgxfive-test loop iteration takes about 5 to 6 ms at 64x64, and in one run 32 render contexts took about 4.6 MiB of low memory each"
unit = "render"
method = "sgxfive-test on the laptop with the debug option on, on a fresh boot (probes/render/client-jobs.toml): tri -n 4, tri at 128x96 -n 2, tri with a 256x256 context -n 2, contexts -n 32, and tri -n 2 after a faulting render"
tiers = ["HW"]
date = "2026-11-01"
data = ["render-client-jobs"]
terms = []
+++

**What runs.** sgxfive-test creates a render context for the target size, builds the
triangle's vertex and pixel programs, its VDM stream and state blocks, and submits a render
job through the render ioctl. The renders alternate two colours, so each one is told from the
last.

**Results.** Every render is exact: 0 wrong pixels inside the triangle, outside it and on its
edges against the CPU reference, and no dword of the buffer outside the target changes
(`guard 0`, `outside: 0 dwords`). A 64x64 target has 1062 triangle and 3034 background pixels,
a 128x96 one 3252 and 9036. A context sized for 256x256 targets gives the same target hashes
as one sized for 64x64. The two renders after the faulting one (E024), on a new context,
are exact too.

The tool times one loop iteration: build, submit, wait, and the CPU's hash and check of the
target; the GPU's own time is not separated. At 64x64 the first iteration on a new context
took 6.2 to 6.3 ms and the later ones 5.1 to 5.2 ms; at 128x96, 15.4 and 13.5 ms (two
iterations).

Creating 32 render contexts for 64x64 targets in one VM lowered MemFree by 152084 KiB,
4752 KiB each, and LowFree by the same: all of it low memory. This is one run, and other
activity on the machine counts too. The memory after the tool destroys them was not
measured. The log adds no line after the boot during the renders and the contexts.
