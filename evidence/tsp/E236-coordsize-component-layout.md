+++
id = "E236"
claim = "Under coordinate-set size words 1 to 5 a coordinate set iterated with four components reads, from the vertex's dwords x, y, 0.25 and 0.5, as x 0 0 1.0 (size 1), x y 0 1.0 (2), x y 0.25 1.0 (3), x y 0 0.25 (4) and x y 0.25 0.5 (5), with 6 and 7 reading as 2; and read as two sets, the sizes 0x12, 0x19, 0x0b and 0x0a split the four dwords into x y | 0.25 0.5, x | y 0.25 0.5, x y 0.25 | 0.5 and x y | 0.25, with 0x00 and 0x02 reading as 0x12; one run"
unit = "tsp"
method = "the probes tsp-coordinate-sets-csize-<S>-pa<K> (S 1 to 7, K 0 to 3) and tsp-coordinate-sets-csets-<S>-pa<K> (S 0x00, 0x02, 0x0a, 0x0b, 0x12, 0x19, K 0 to 2) of probes/tsp/coordinate-sets.toml, the 64x64 triangle with the vertex shader vtx_coord4.s (o4 = x, o5 = y of the vertex, o6 = 0.25, o7 = 0.5), state word 16 set to S, a primary program that iterates one source and a pixel shader that stores primary attribute K, on the laptop with the linux fork and the debug option on, one run (no follow-up run)"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["tsp-coordinate-sets"]
terms = ["COORDSIZE.SET_LAYOUT"]
+++

**What runs.** The vertex shader writes four dwords after the position: x and y (the vertex's
clip-space values, which differ per vertex), 0.25 and 0.5. State word 16 (the coordinate-set size
word, three bits a set from bit 0) is set per probe. The primary program iterates a source
with a DOUTI0 word whose bits 23:22 give the component count.

- `csize`: source 1 (DOUTI0 0x27000800 plus the count) with 1 to 4 components, state word 16 at
  1, 2, 3, 4, 5, 6 and 7, primary attributes pa0 to pa3 read back, one probe a register.
- `csets`: sources 1 and 2 (DOUTI0 0x27800800 and 0x27801000, three components each), state
  word 16 at 0x00, 0x02, 0x0a, 0x0b, 0x12 and 0x19,
  pa0 to pa2 read back.

**Results.** One run, every baseline before and after a probe clean (0 of 4096 pixels). A
register holds the constant given, or x or y: x and y show as three value classes (the triangle's
vertex values, 1062 pixels), told apart by comparing pixel by pixel (pa0 and pa1 of the
five-component case differ at 1032 of the 4096 pixels).

With four components iterated, one set:

| size word | pa0 | pa1 | pa2 | pa3 |
|-----------|-----|-----|-----|-----|
| 1 | x | 0 | 0 | 1.0 |
| 2, 6, 7 | x | y | 0 | 1.0 |
| 3 | x | y | 0.25 | 1.0 |
| 4 | x | y | 0 | 0.25 |
| 5 | x | y | 0.25 | 0.5 |

With 1 to 3 components iterated, the registers past the count hold other values in some cases
(for example size 1 with one component: pa1 takes several values); only the four-component
case is a rule here. So a field holds the components a set has in the vertex: 1 gives x, 2 gives
x y, 3 gives x y z (the third dword), 4 gives x y w (the third dword is read as w and z reads
0), 5 gives x y z w; a component the set does not have reads 0, or 1.0 for the fourth; 6 and 7
read as 2 **[infer]**.

Two sets (source 1 then source 2, three components each, pa0 to pa2):

| size word | source 1 reads | source 2 reads |
|-----------|----------------|----------------|
| 0x12 | x y 0 | 0.25 0.5 0 |
| 0x19 | x 0 0 | y 0.25 0.5 |
| 0x0b | x y 0.25 | 0.5 0 0 |
| 0x0a | x y 0 | 0.25 0 0 |
| 0x00, 0x02 | x y 0 | 0.25 0.5 0 (as 0x12) |

The fields of 0x12 are 2 and 2, of 0x19 are 1 and 3, of 0x0b are 3 and 1, of 0x0a are 2 and 1: the
sets take the vertex dwords in order, each as many as its field says. A field of 0 reads as 2:
0x00 and 0x02 give 0x12's reading, so the vertex size, not the fields, decides how many sets
there are; the fields give their layout **[infer]**.

**Not shown.** What the vertex output size word contributes (state word 16 is varied here at the
default output size), sets of more than two, size words that make the second set larger than the
dwords left, and the closed stack's choice of sizes. One run only.
