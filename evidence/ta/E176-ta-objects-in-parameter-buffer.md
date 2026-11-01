+++
id = "E176"
claim = "The TA's object, at the start of the parameter buffer, is three header words (read as the pixel program's words, which is not tested), one 1/w per vertex followed by that vertex's iterated outputs, the ISP words, the primitive list and line widths, a format word whose bytes count the stored and iterated dwords per vertex, four per-set masks, and the packed vertices; 13 probes give the format words and masks listed"
unit = "ta"
method = "the 13 object probes of probes/ta/objects.toml (position only, one 2-component set, a 4-dword set at coordsize 1 to 5, two sets of 2, both at half precision, the vertex colour, a perspective w, the viewport z offset and scale), 64x64 triangle, with the parameter buffer saved after the render and its first page read as 32-bit words, on the laptop, linux fork with the debug option on; one run"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["ta-objects"]
terms = ["PB_OBJ.RHW", "PB_OBJ.SET_MASKS", "PB_OBJ.PDS_WORDS", "PB_OBJ.ISP_WORDS", "BG.TSP_DWORDS", "BG.TSP_STORED_DWORDS", "COORDFMT.SET_F16", "Parameter Buffer (PB)"]
+++

**What runs.** Each probe is the triangle job with one change to the vertex outputs. After the
render the kernel's copy of the parameter buffer is saved (4603904 bytes) and its first page read
as dwords up to the last non-zero one. In every probe the page holds one object, 23 to 35 dwords.

**Results.** The layout, common to the probes:

- *Three header words.* Position only: 0x04000004, 0x00030001, 0x04000000. With any iterated
  output other than none (the textured forms, the half-precision forms, the perspective probe,
  the vertex colour): 0x04000004, 0x00030004, 0x0c000080.
- *Per vertex*, three vertices in sequence, the vertex's 1/w and then its iterated outputs
  undivided: position only 1 dword per vertex; one 2-component set 3 (1/w, u, v); a 4-dword set 5;
  two sets of 2 5; the vertex colour 2 (1/w and one packed ARGB8888 dword, 0xff000040,
  0xffbf0040, 0xff00bf40); a 4-dword set at half precision 3 (1/w and two dwords of 16-bit
  pairs, for example 0x2e66ba00 and 0x39993555 for the first vertex); two sets of 2 at half
  precision 3. The 1/w values are 1.0 for the unit-w probes and 0.8, 0.3636 and 0.6154 (0x3f4ccccc,
  0x3eba2e8b, 0x3f1d89d8) for the probe with w = x + 2.
- *Then* ISP word 0 and ISP word 1 (0x01d00200 and 0x000010f0 for the plain probes), the
  primitive list (E181), the line widths (0x00001010), a **format word**, four **masks** and the
  packed vertices, 8 dwords for 3 vertices (0x00100800, 0x00001008, 0x14003f00, 0x10380010,
  0x3f000000, 0x00103800, 0x00001014, 0x00003f00 in the plain probes).

The format words and masks:

| vertex outputs | dwords per vertex | format word | four masks |
|---|---|---|---|
| position only | 1 | 0x00040101 | 0, 0, 0, 0 |
| one 2-component set | 3 | 0x00040303 | 0, 0, 0, 0 |
| 1 set, w = x + 2 | 3 | 0x00040303 | 0, 0, 0, 0 |
| one 4-dword set | 5 | 0x00040505 | by coordsize, below |
| two sets of 2 | 5 | 0x00040505 | 0, 0, 0, 0 |
| 4-dword set, half | 3 | 0x00040503 | 2, 0, 2, 2 |
| two sets of 2, half | 3 | 0x00040503 | 6, 0, 0, 0 |
| vertex colour | 2 | 0x000c0202 | 0, 0, 0, 0 |

The four-dword set's masks by coordsize 1 to 5: 1 gives 0, 2, 0, 0; 2 gives 0, 0, 0, 0; 3 gives 0,
0, 2, 0; 4 gives 0, 0, 0, 2; 5 gives 0, 0, 2, 2. The object's other dwords are the same in all five.

So bits 7:0 of the format word are the dwords a vertex takes as stored and bits 15:8 as iterated
(the half-precision pairs counted unpacked: stored 3 against iterated 5); bit 18 is set in every
format word, and the colour probe also sets bit 19. Each mask has bit i set for coordinate set i
counted from 1 in these probes, and its bits move with the coordsize and precision settings as the
table shows: the masks reading "the set is half precision, has one component, has z, has w" is the
pattern of the data, not tested beyond these probes [infer]. The viewport z offset and scale probe
(z 0.75) changes three packed-vertex dwords (0x14003f40, 0x3f400000 and 0x00003f40 in place of
0x14003f00, 0x3f000000 and 0x00003f00) and nothing else of the object.

**Not shown.** What the header words are made from: the pixel-program words of the state block
that the job supplies are not read here, so "pixel-program words as given" is not tested. The
packed vertices' fields beyond the one z change. Vertices past three. One run.
