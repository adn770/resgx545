+++
id = "Q050"
question = "what do the visibility group's instructions do, and how do smp's mipmaps and LOD values, the border address modes, the compressed and YUV formats and firh's edge modes past the line and fixed banks 1 and 2 behave?"
unit = "usse"
kind = "hw"
value = "high"
phase = 11
evidence = ["E083", "E091", "E123", "E147", "E292", "E293", "E294", "E298", "E563", "E565", "E568", "E1097", "E1103"]
terms = []
+++

The probes ran a case for each of 16 groups of forms that had no hardware readback (E091), pinned
atst8 as an alpha test of src0's top byte against src2's under the function in src2 bits 15:13
(E083), and fitted bilin, firv and firh models to every video-filter case they were fitted to
(E123). Run through the simulator, the vectors show no mismatch, but it stops on 19,243 USSE
vectors rather than guess (E147): 16,529 of them firh vectors whose coefficients come from the
job, 1,126 more firh centred below byte 0 and 196 firh that read latch bytes the task did not
write (E292's count; E147 gave 16,521, and its 477 latch reads were firv's).

11.7 carried each fill's job into the vectors (the transfer command's pokes, and the
coefficients they load): with the loaded sets read as E078 gives them, the fixed banks 1 and 2
as the families of taps their cases allow, centres 16 to 27 for the field's values below `#-4`
(positions 12 to 18 fold by the edge mode, from 19 read 0: E298) and the latch bytes a task did not
write taken as any value, the firh vectors run with no mismatch (E292). Bank 2's sets 2 and 3
are [1 -4 4 -1]/8 and [1 -2 1/2 1/2] (E293). The matches of banks 1 and 2 are consistent with
the fit, not a check: their families come from the same vectors (E292). atst8 runs in the
simulator as E083 gives it, and pcoeff, depthf, setfc, moest and setm as changing nothing a fill
shows (E294).

What is open (usse_isa.md §8, item 1): the rest of the visibility group, which no program of ours
has run outside a fill and a punch-through pass; smp with mipmaps and LOD values; the border
address modes; the compressed and YUV texture formats; fdpc's clip-plane result outside the TA
state our kernel sets; firh's sets 6 and 7 under fixed banks 1 and 2 (bank 1's two and bank 2's
set 6 give values no loaded group gives; bank 2's set 7 gave group 0's value: E298), and the
exact taps of banks 1 and 2, which only vectors outside the fit can check.

To settle it: on the laptop, a probe table per group with the campaign runner: the visibility
group's forms each with a known test value and the visibility counters read back; smp over
level-tagged mip chains and border colours (with E441's texture words); firh's fcs6 and fcs7
at modes 1 and 2 on impulses and pedestals, as E079 measured sets 2 to 5; and sets 2 to 5 of
banks 1 and 2 on lines no fitted case used, to test the families out of sample.

Narrowed in 11.32 (E563, E565, E568, in a fill that samples a buffer of named dwords). Mipmaps and
LOD values: whole LODs read the levels of E041's chain for non-square shapes too (E562), and a
gradient's LOD is a logarithm of a footprint that is the largest component on some cases and the
Euclidean length on others (E563, Q175 open). Border modes: modes 6 and 7 clamp and 4 and 5 repeat
along v; along u modes 4 to 7 read other texels, some past the texture, that no declared rule fits
(E565, Q177). Compressed formats: the names maps and the block jobs of formats 23 to 27 give block
layouts only in part (E568, Q179). YUV: formats 28 and 29 read opaque black in a fill whether or not
the transfer command's colour-space words were poked, so the conversion of E037 was not reached
(E568). The visibility group, fdpc, and firh's sets 6 and 7 and the exact taps of banks 1 and
2 are untouched.

Narrowed 2026-11-15 (E1097, E1103): the YUV clause above is corrected. E568's pokes went through a
dangling poke set; on t22 a fill reads E037's conversion of its texel for formats 28 and 29 when
colour-space set 0 holds the BT.601 words, and black when it holds zeros. A fill's transfer
command loads the set when its load flag is set, and a fill without the flag reads the last
loaded set (E1103, held out).
