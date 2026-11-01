+++
id = "E392"
claim = "The vertex-colour iteration cases of E133 (state words 13 = 0x83800, 16 = 5; shade models 0, 1, 2) give their vertex colour at all 1062 triangle pixels in every one of 18 jobs, in the order 0, 1, 2, 2, 1, 0 three times: the group of about 300 pixels keeping the previous case's colour (E133) does not occur"
unit = "pds"
method = "probes/pds/shade-order.toml on the laptop over the cable, linux fork b5a86838ae59 with the debug option on: pds_iter_nofetch.s with DOUTI0 0x21c10000, 0x23c10000, 0x25c10000 (models 0, 1, 2) and a source-1 case after each sequence, pix_pa0.s, vtx_color.s; three runs; every pixel read back"
tiers = ["HW"]
date = "2026-11-03"
data = ["pds-shade-order"]
terms = []
+++
**Results.** Model 0 gave 0xff000040, model 1 0xffbf0040, model 2 0xff00bf40 at all 1062 pixels in
every job; no pixel equalled the previous job's.

**Not shown.** What made E133's two runs, on an earlier kernel, keep about 300 pixels of the
previous case's colour: the stack of these runs does not show the group.
