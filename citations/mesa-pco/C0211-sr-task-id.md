+++
id = "C0211"
source = "mesa-pco"
locator = "src/imagination/pco/pco_isa.py:47"
link = "https://gitlab.freedesktop.org/mesa/mesa/-/blob/ab2374a4a18ba0ae4c11d499ac35607dd7bbb571/src/imagination/pco/pco_isa.py#L47"
quote = "('tile_x_pix', 49),"
terms = ["SR.TASK_ID"]
+++

Line 47 of `pco_isa.py` in Mesa's Rogue compiler (pco) names `task_id`. It backs the glossary enum
value `SR.TASK_ID`: a per-task id the scheduler assigns, constant over a 4x4 block of a fill.
