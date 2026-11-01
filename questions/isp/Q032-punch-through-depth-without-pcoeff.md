+++
id = "Q032"
question = "what does pcoeff hand the ISP in the punch-through pass, when the kept pixels' depth is the same without it and moves between runs only when it runs without the iteration it reads?"
unit = "isp"
kind = "hw"
value = "medium"
phase = 10
evidence = ["E217", "E416"]
terms = ["FEEDBACK_CTL.ENABLE", "FEEDBACK_CTL.KEEP", "ISP0.PASS_TYPE"]
+++

The five-copy punch-through scene keeps a pixel when the pt phase ends in atst8 with fb, a passing
alpha test and 0xe001 in src1, and the depth result is 1062 pixels of the nearest copy and 36 of
the next (E217). The expected reading was that the depth decision needs pcoeff together with the
source-34 iteration it reads. The data do not show that: dropping pcoeff, dropping pcoeff and the
iteration, and dropping pcoeff with a fetchless iteration all give 1062 and 36, in both runs.
Only pcoeff without the source-34 iteration changes the image, and differently in the two runs
(1054, 36 and 8 of the 1/8 copy, then 1046, 36 and 8 of the 1/4 copy). That pcoeff then reads
values the pds program did not iterate is a reading, not tested.

So pcoeff's effect on the depth in this scene is not seen when it is absent, and is seen only as
run-to-run variation when its source is missing. What it hands the ISP, and why the depth test
gives the right answer without it, are open.

To settle it: iterate a source whose values differ from the copies' own depths (a constant, or the
depths in reverse order) and hand it with pcoeff; if the kept copy follows the iterated values,
pcoeff carries the depth, and if it does not, the depth comes from the geometry. Run the variant
with pcoeff and no source-34 iteration five times, after a job that leaves a known value in the
iteration state each time, to see whether the extra pixels follow that value.

Narrowed in 11.15 (E416, five runs each): the punch pass with pcoeff and the source-34 iteration
draws the same image five times; with pcoeff alone and with neither, the kept pixels differ from run
to run (four and five outcomes in five runs), so the variation follows the missing iteration, not
pcoeff. The iterated constant or reversed depths of the settle plan were not run, so whether pcoeff
carries the depth is open. Status: narrowed, not answered.
