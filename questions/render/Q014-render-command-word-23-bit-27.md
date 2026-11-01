+++
id = "Q014"
question = "why does a background object whose first PDS word has a high bit wrong render part or all of the first 32x16 tile before the job faults?"
unit = "render"
phase = 6
evidence = ["E029", "E301", "E363"]
terms = ["cmd_ta.pds_bgnd"]
+++

What word 23 is and where its surviving pixels lie on 64x64 are answered (E301): it is the
background object's first pixel PDS word (`cmd_ta.pds_bgnd[0]`); with bit 27, 28, 30 or 31 flipped
the job faults with whole rows of the first 32x16 tile rendered.

Narrowed by E363 (three runs a case on 64x32 and 128x128): bits 27 and 28 make the fetch fault at
page 0x0001f000, bits 30 and 31 at the pixel PDS heap's second page (0x2e001000). On 64x32 bits 27
and 28 leave 11 to 14 whole rows and the rest of the first 16 rows at half width (splits 12+4,
11+5, 14+2), bits 30 and 31 rows 0 to 15 whole and rows 16 to 31 at half width (16 half rows); on
128x128 no row is rendered under any of them. The second word's bits 27 and 31 and the third's bit
27 change nothing; the third's bit 31 faults at the pixel-heap page with no row. So the rows
rendered depend on the target, the pixels done before the fault stops the 3D.

What is open: why tiles render at all with a background program fetched from a wrong page (a
pipelined fetch of the previous address, or a cached copy), and what sets how many rows under bits
27 and 28.

To settle it: the same flips with the pixel PDS heap's second page mapped to a known pattern, and
with a cache invalidate before the job.
