+++
id = "E308"
claim = "The 28 object dumps of probes/ta/objects.toml, from which 3d.md §10.1 was written, and the 45 taken since (the 15 of probes/vdm/index2.toml with an object and 30 of the 31 of probes/ta/object-words.toml, the faulting case keeping no TA data to place it) decode with one layout placed by the stream's object word: three PDS words, each vertex's dwords (the object word's ISP address less three, over the vertices, gives 1, 2, 3 or 5 dwords a vertex), the two ISP words, the primitive list, the line widths, a format word whose bits 7:0 are those dwords a vertex, the four set masks, then the packed vertices; the set masks over the coordinate-size settings 1 to 5 of one set read as one bit in mask 2, none, mask 3, mask 4, masks 3 and 4; the 45 new objects all have the format 0x00040101 (one dword a vertex) and differ only in their vertex counts, so they test the placement by the stream, the vertex count and bits 7:0 of that one format, while the other formats and the masks rest on the dumps the layout was read from; bit 15 of a primitive list entry is set in 11 of the 24 random triangles, exactly those of one winding"
unit = "ta"
method = "offline decode of the saved render dumps of the datasets named (ta-objects, vdm-index2, ta-object-words) with ta_words.py object (pbdump.py object_fields): the first stream's primitive and object words give the object's vertices (CSTREAM.PRIM_VERTICES + 1), primitives ((CSTREAM.OBJ_PRIMS + 1) / 2) and ISP words (CSTREAM.OBJ_ISP_ADDR)"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["ta-objects", "vdm-index2", "ta-object-words"]
terms = ["PB_OBJ.PDS_WORDS", "PB_OBJ.RHW", "PB_OBJ.ISP_WORDS", "PB_OBJ.PRIM_LIST",
         "PB_OBJ.LINE_WIDTHS", "PB_OBJ.FORMAT", "PB_OBJ.SET_MASKS", "CSTREAM.OBJ_ISP_ADDR"]
+++

**What runs.** No new run: the decoder reads the objects the earlier tables saved, placing each
field from the stream rather than from fixed offsets, and checks that the dwords between the
header and the ISP words divide evenly among the vertices.

**Results.** Every object decodes: the 28 in-sample objects of ta-objects, which §10.1 was written
from, and the 45 new ones of vdm-index2 and ta-object-words, all of the format `0x00040101`. The
format word's bits 7:0 equal the dwords a vertex takes in each: 1 (`0x00040101`, a position only,
lines, points, every ISP variant), 2 (`0x000c0202`, the vertex colour), 3 (`0x00040303` one
two-component set, `0x00040503` one four-dword set at half precision) and 5 (`0x00040505`, one set
of four dwords, or two sets). The masks by setting:

| dump | masks 1 to 4 |
|---|---|
| half precision on set 1 (`cfmt-05-1`) | 2, 0, 2, 2 |
| half precision on sets 1 and 2 (`cfmt-12-3`) | 6, 0, 0, 0 |
| coordinate size 1 on set 1 | 0, 2, 0, 0 |
| coordinate size 2 | 0, 0, 0, 0 |
| coordinate size 3 | 0, 0, 2, 0 |
| coordinate size 4 | 0, 0, 0, 2 |
| coordinate size 5 | 0, 0, 2, 2 |

The masks come from the in-sample dumps alone: the new objects have one format, no set and all masks
0. The VDM_INDEX2 objects (E300) decode with 15, 12 and 9 vertices and their primitive lists number
the vertices from 16 in order; with 0x0f000000 bit 15 of both entries of the first dword is set
(`pbdump._entries` keeps it apart from the vertex numbers). The 24 random triangles of E307 have one
entry each, (16, 17, 18): bit 15 is set in 11 of them (`0xca30`), exactly those whose vertices, in
the order the probe gives them, have a negative signed area in target coordinates (y down), and
clear in the other 13.

**What it shows.** The object's layout of 3d.md §10.1 holds over every dump taken, with the stream's
words giving its variable parts; outside the dumps it was read from, that is shown for one format
only. The format word's low byte counts a vertex's dwords in the object. Bit 15 of a primitive entry
marks a triangle's winding [infer: one table of 24 triangles]. The set masks give set 1 bit 1; size
1 sets mask 2, size 3 mask 3, size 4 mask 4 and size 5 both, so masks 2 to 4 read as one component,
has z, has w [infer: one value per setting, in the dumps the layout was read from], and mask 1 as
half precision.
