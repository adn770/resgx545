+++
id = "E437"
claim = "A douti with DOUTI0 0x20400000 (source 0, components bits 23:22 at 1, completion bit 29) under DOUTU1 bit 24 writes the pixel's x + 0.5 to pa0 and its y + 0.5 to pa1 at all 1062 triangle pixels of the 64x64 job in three runs of each, and pa2 holds none of them (0 of 1062)"
unit = "pds"
method = "probes/dpm/partial-reload-pos.toml on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: pds_iter_nofetch.s as the triangle's primary pixel PDS program (--tri pixpds) with A = 0x20400000, B = 0 and U1 = 0x01000004, and a shader writing pa0, pa1 or pa2 out as the colour (three probes, three runs each, 9 jobs); every pixel read and the triangle's pixels compared with their coordinates"
tiers = ["HW"]
date = "2026-11-07"
data = ["dpm-partial-reload-pos"]
terms = ["DOUTI0.ATTR_SOURCE", "DOUTI0.COMPONENTS", "DOUTI0.LAST_ITER", "DOUTU1.WAIT_ITER"]
+++

**What runs.** The 64x64 triangle with the primary program of E048's wait case, whose douti reads
source 0 with two components. The shader writes one primary attribute as o0; the pixels of the
triangle (1062) are compared with the pixel's x + 0.5 and y + 0.5 as floats (within 0.001), the
background's 3034 being left out.

**Results.** pa0 equals x + 0.5 at 1062 of 1062 pixels and y + 0.5 at 30 (the pixels with x = y), in
each of three runs; pa1 equals y + 0.5 at 1062 and x + 0.5 at 30, in each of three runs; pa2 holds
leftover values (-9999220736.0 at pixel (8, 8), the same in the three runs) and no x or y. The first
triangle pixels are (8, 8) = 8.5, (9, 8) = 9.5 in pa0 and (8, 8) = 8.5, (9, 8) = 8.5 and (8, 9) =
9.5 in pa1.

**What it shows.** Source 0 with two components is the pixel's position, window coordinates plus a
half, with no coordinate set in the vertices (the vertex program here is the default's, with none),
so a program that needs the pixel's place, a background object's fetch of the target, say, has it
in pa0 and pa1. E131 read source 0 as the pixel's x + 0.5 with one component, E132 the components
bits with source 1.

**What it does not show.** Whether the third component (bits 23:22 at 2) gives anything for source
0, or the position in a background object's primary program (E442 runs it there).
