+++
id = "E851"
claim = "Offline reading of E842's kept words (Q230; no new job): the frozen analysis of g4-rw is decided without its 18 unread words: its rule adopts a model only at 30 of 30 FIT words, and none of the 225 frozen models (score/rwfam.py, five families) reproduces all 19 FIT words that were read (best per family a 14, b 13, c 16, d 14, e 14 of 19; HELD OUT words not touched), so no completion of the table can make one fit and the frozen verdict stays 'no rule adopted'; read post hoc over all 65 known 1/w words of kept vertices (E754, E782, E795, E796, E798, E842; 49 RZ, 16 RZ + 1), H-MANT, 'whether the word is RZ or RZ + 1 follows the mantissa of w alone', is consistent with 6 of 6 mantissas read at two or three exponents (1.0625, 1.125, 1.5, 1.59375, 1.6875, 1.75: none shows both), a reading made after the data, not held out; a wider declared family (fixed-point table plus Newton steps with truncated products, 32000 models) fits none (best 49 of 54 distinct mantissas, 'always RZ' 42)"
unit = "ta"
method = "Offline, 2026-11-12, round 5 planning of the closing pass (plan closing5/pixel/exp-pixel-r5.md sections 3.1 and 3.2, user decision R5-1 a), no laptop, no job; closing5/pixel/rw_fit_alive.py (output closing5/pixel/rw_fit_alive.out) parses E842's kept out/20261111-210423/score-g4-rw.txt of render-closing-r4-pixel (60 table rows), keeps the FIT rows whose word was read (19, 6 of them RZ + 1) and scores every model of the frozen score/rwfam.py, imported from the published session unchanged (its models() and fits()); the HELD OUT words are not read by it, so the frozen test stays clean if it is ever completed; closing5/pixel/rw_explore.py (output closing5/pixel/rw_explore.out) is an exploration, declared post hoc in its docstring: it takes E842's 42 words from the same file and the 23 earlier words (w with RZ or RZ + 1) as transcribed in the script from E754, E782, E795, E796 and E798, groups them by the 23-bit mantissa of w, and fits a wider family declared in the script before it ran; both scripts re-run at the fold from their published copies (cited/closing5/pixel in resgx545-data) with output byte-identical to the kept .out files"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r4-pixel:out/20261111-210423/g4-rw/", "render-closing-r4-pixel:score/", "cited-scratch:closing5/pixel/"]
terms = ["PB_OBJ.RHW"]
+++
**What was read.** E842's table of 60 w was frozen with a FIT and a HELD OUT half and a rule: an
algorithm family counts only when a model reproduces 30 of 30 FIT words, and is then scored on the
HELD OUT half. 18 words were not read (the quarter-scaled jobs were cut at the guard band), so the
analysis did not run, and the question was whether rerunning those six jobs could complete it.

**Results [HW], read from E842's kept words.** From `closing5/pixel/rw_fit_alive.out`: 60 table
rows parsed, 19 FIT words read (6 RZ + 1); 225 frozen models; fitting all 19: 0. Best per family,
of 19: a 14, b 13, c 16, d 14, e 14; the best models (`c:s12:k1..3:rz:rn`, `c:s10:k2..3:rn:rz`)
miss 3 words.

**What it shows.** A frozen model that misses one of the 19 read FIT words cannot reach 30 of 30,
whatever the 11 unread FIT words are. So the frozen analysis of g4-rw is decided offline: no model
of its family is adopted, which is the frozen verdict "none: the words are recorded and no rule is
adopted". Rerunning the six jobs to complete that test buys nothing. This is the frozen procedure's
own first step, run on the words that exist; it uses no HELD OUT word. Refuted by: a parsing error
only (the script imports the frozen `rwfam` and uses its `fits`).

**Read after the data, post hoc (not held out) [infer].** `closing5/pixel/rw_explore.out`, over the
65 known words of kept vertices (49 RZ, 16 RZ + 1, none other), 54 distinct mantissas:

| mantissa of w | exponents read | word |
|---|---|---|
| 1.0625 | 0, 2 | RZ |
| 1.125 | 0, 3 | RZ + 1 |
| 1.5 | 0, 1, 2 | RZ |
| 1.59375 | 0, 2 | RZ + 1 |
| 1.6875 | 0, 2 | RZ + 1 |
| 1.75 | 0, 2 | RZ |

No mantissa shows both RZ and RZ + 1. On the grid 1 + k/32 the word was RZ + 1 at k = 4, 13, 19,
22, 25 and 27 and RZ at 21 others; k = 0, 3, 9, 17 and 23 were not read. H-MANT, "word - RZ is a
function of the 23-bit mantissa of w alone", fits all six repeats. With one word in four RZ + 1,
six repeats agreeing by chance is about 4 percent if the words were independent of the mantissa
(a rough figure, [infer]): suggestive, not a test. A wider family declared in the script before it
ran (a fixed-point table indexed by 2 to 11 bits, entries cut to a few more bits, one or two Newton
steps with products truncated to 24 to 40 bits, a final floor, nearest or ceiling: 32000 models)
fits none of the 54 mantissas; the best fit 49 against 42 for "always RZ".

**What it does not show.** Which mantissas store RZ + 1, by what rule: no candidate rule exists to
freeze, only H-MANT, which needs words at exponents not yet read (a rerun of E842's rows at other
scales, the plan's stage g5-rw). w below 1 (the 18 unread words), the made vertex's 1/w and the
depth formula stay open (Q230).
