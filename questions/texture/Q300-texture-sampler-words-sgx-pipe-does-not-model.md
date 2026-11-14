+++
id = "Q300"
question = "what does a texture sample read and return for the sampler words, formats, sizes and modes that sgx-sim's tex::sample refuses, where a transfer's copy or a background object samples its texture (sgx-pipe's xfer and bglayer): T0 and T3 bits and values no record ran (T3 bits 12:11 other than 01 with T0 bit 9, two filters or 1D, T3 bit 12 with mips off, T3 bit 14 at sizes, formats and modes not run), and a texel read outside the scene's memory?"
unit = "texture"
kind = "hw"
value = "medium"
phase = 12
evidence = ["E274", "E397", "E564", "E566", "E722", "E723", "E1027", "E1047", "E1049", "E1058", "E1067"]
terms = ["T3.BIT14", "T3.BITS7_0", "T3.BITS19_18", "T3.BITS28_27", "T0.BIT27"]
+++

Opened 2026-11-14 as Q078's successor (Q078 answered by E1067, round 17, the user's decision). Q078
began as the T3 and T0 bits read in a copy (E274) and, as its clauses were answered, kept being
the question sgx-pipe named whenever `tex::sample` refused a copy's or a background object's texture
read: `xfer` and `bglayer` refuse under it, and the transfer scene vectors list it for every poked
texture, primitive-PDS and background word. Those refusals were never a clause of Q078's last line
(the bilinear bit-14 footprint, E1067) and are carried here:

- the sampler words no record ran: T0 bits outside the measured fields, T3 bits 12:11 other than 01
  with T0 bit 9, two filters or 1D, and T3 bit 12 with mips off (E1027 ran the rest), T3 bits 7:0,
  10, 18-19 and 27-28 outside E397's and E722's fills, and T3 bit 14 at the sizes, formats, filters
  and address modes no fill ran (E1003, E1047, E1049, E1058, E1067 ran the others);
- formats, filters and address modes `tex::sample` refuses on the texture a copy or a background
  object samples (E564, E566, E723 measured the rest);
- a texel read outside the scene's memory (with Q076 and Q003).

What would settle a clause: the refused words in the probe fills of E566's tx_map form, each held
out against a frozen reading, the way E1027 and E1067 settled theirs. sgx-pipe refuses each case
under Q300 until a record models it.
