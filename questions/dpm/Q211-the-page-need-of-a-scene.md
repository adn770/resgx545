+++
id = "Q211"
question = "what is the page need U of a scene at a macrotile grid (19 pages for the default triangle at 1024x768, 287 at 4096x4096) and what is the constant k, 2 to 13, that the partial-render count adds to it?"
unit = "dpm"
kind = "hw"
value = "high"
phase = 11
evidence = ["E310", "E625", "E630", "E705"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)"]
+++

E625: a one-triangle scene overflows exactly when P - 0x22 is below 19 pages (1024x768) or 287
pages (4096x4096), the two numbers E310 gave for the whole-buffer jobs (0x13, 0x11f); the counts
of its partial renders fit 1 + floor((287 + k - thr0) / (thr0 + 0x1f)) for every k from 2 to 13,
with the spacing 0x1f not pinned either (0x1e fits the 4096x4096 counts too). E630: wide scenes of
300 to 900 vertices at 4096x4096 need 2836 to 8318 pages by the same count formula, 9.2 to 9.8
pages a vertex, but the 300-vertex scene gives two ranges (0x40 and 0x23 pages) that do not meet
with the spacing 0x1f and overlap with 0x1e: these are lower bounds of a model that does not
close, not measures of a need, and neither a constant U per scene nor its failure is shown. A
second triangle at 1024x768 needs 23 to 26 pages (E627: overflow in 0x38, completion in 0x3c).

Open: how the lists' pages add up (one page per macrotile list at least, the global list's pages,
the pages the final lists take), what k is and what the pages it adds are, the spacing, and the
exact need of a scene as a function of its triangles and macrotiles, which `dpm.rs` must compute.

To settle it: scenes of 1 to 4 triangles whose whole-buffer page need is read from the free list
(the walk after the job) and the counts of partial renders at three buffer sizes each, with the
spacing fitted first on the one-triangle scene.

Reworded in 11.39: the figure "9.2 to 9.8 pages a vertex" for the wide scenes is dropped from the
question line (E630 calls it a lower bound of a model that does not close, and it does not hold
beyond the one threshold at which it was found); the paragraph above keeps the measurements.

Narrowed in 11.39 (E705). The page need of a one-triangle scene is not 19 pages: the same
triangle at 1024x768 moved by 0, 192, 384 and 576 pixels reaches status 0x13, 0x14, 0x11 and
0xc (19, 20, 17 and 12 pages), and E625's overflow rule (overflow iff P - 0x22 is below the
need) with those needs gives the outcome of all 8 distinct conditions (4 positions at each of
P = 0x28 and 0x30; the 22 renders include 14 repeats of an input already rendered; computed after
the run, so a check, not a held-out test). The planned stacked-against-disjoint comparison was
not made: the tool's -n 4 is four renders, one triangle each, so the two frozen predictions
(disj4 against stack4) are void, and the higher maximum status of disj4 is the position
dependence. Open: the need of a scene of 2 to 4
triangles (a tool option that puts several triangles in one render), the need as a function of
the macrotiles filled, k and the spacing.
