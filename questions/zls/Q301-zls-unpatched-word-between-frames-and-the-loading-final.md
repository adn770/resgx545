+++
id = "Q301"
question = "what does the closed driver write the unpatched ZLS control word 0x0011700a into the render details for between frames, and why does a final render that loads the depth draw no triangle against the loaded depth?"
unit = "zls"
kind = "fw"
phase = 11
evidence = ["E335", "E336", "E337", "E1093", "E1094", "E1101"]
terms = ["CR_ISP_ZLSCTL", "hw_render_details.isp_zlsctl"]
+++

Split 2026-11-15 from Q088 (retired, answered by E1101; decision R22-8 a), its parts left as fw.
The hardware part is answered: for every render of a kick the firmware loads `CR_ISP_ZLSCTL` from
the render details' word and ORs bits 14, 18 and 19 into it for each partial render (E1094); after a
raised kick the final loads the load buffer and writes it back to the store without the triangle,
load bits or not (E1093), and after a kick that was not raised it does so with load bits and
follows its word without them (E1101, E1093).

Open, parked as fw: between frames the closed driver writes `0x0011700a` into the render details'
own word, which the next render's 3D patch overrides (E336); what it means it for is the closed
driver's own choice. And why a final that loads draws no triangle at z 0.5 against a 0.75 load (a
depth test that fails, a test against another buffer, or no test of the final's own): the firmware's
handling of a loading final is not seen by any register read so far.

To settle it: the closed driver's frames with the word's load bits read back between them, and a
loading final with the triangle at z 0.25 and 0.9 against the 0.75 load.
