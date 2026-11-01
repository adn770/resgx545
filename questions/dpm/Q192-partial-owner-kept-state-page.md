+++
id = "Q192"
question = "does the store that follows the next context's render replace the state page a partial-render owner left (18 non-zero dwords after its partial renders, E591), and what does it write there?"
unit = "dpm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E310", "E464", "E591", "E631"]
terms = ["CR_DPM_STATE_BASE0", "CR_DPM_CONTROL_BASE"]
+++

E591: a kept first context that rendered 1024x768 on 0x28 pages (partial renders) holds 18 non-zero
dwords in its state page (page 6) and non-zero dwords in the pages 7 to 11 (4 of 4, solo). The
second context was not rendered after the overflowed first render in the 4 jobs with it: the tool
closes the second context first (0 of 1 renders ok), so the kept context was the second.

To settle it: a tool whose early close of the first context follows an overflowed render (an option,
the tool is unchanged), render_keep armed, flags 0x4 and 0xc, and the kept pages 4 to 6 compared
with the solo runs'.

Narrowed in 11.38 (E631). One case was run: a kept first context of 1024x768 in 0x28 pages (one
partial render), flags 0xc and 0x4, then the second context rendered: the state page (page 6)
holds 0 non-zero dwords of the 18, read after the tool exits (2 runs of each flag, 4 of 4), while
the solo controls with the flag poked keep their 18 dwords (2 of 2), so the zeroing is the second
context's and not the flag's. What the data do not give is the question's own cause: that it is
the store that follows the second context's render and not its creation or the close of the first
(a kept copy before the close exists only for the 64x64 owner, E631), what that store writes
besides zero, and whether it holds at another size or buffer (one size, one P). The owner words of
Q191 do not appear for this owner.
