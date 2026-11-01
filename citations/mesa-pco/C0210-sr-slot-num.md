+++
id = "C0210"
source = "mesa-pco"
locator = "src/imagination/pco/pco_isa.py:48"
link = "https://gitlab.freedesktop.org/mesa/mesa/-/blob/ab2374a4a18ba0ae4c11d499ac35607dd7bbb571/src/imagination/pco/pco_isa.py#L48"
quote = "('tile_y_pix', 50),"
terms = ["SR.SLOT_NUM"]
+++

Line 48 of `pco_isa.py` in Mesa's Rogue compiler (pco) names `slot_num`. It backs the glossary enum
value `SR.SLOT_NUM`: a per-slot id the scheduler assigns, constant over a quad.
