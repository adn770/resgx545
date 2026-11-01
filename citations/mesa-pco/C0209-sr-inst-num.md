+++
id = "C0209"
source = "mesa-pco"
locator = "src/imagination/pco/pco_isa.py:51"
link = "https://gitlab.freedesktop.org/mesa/mesa/-/blob/ab2374a4a18ba0ae4c11d499ac35607dd7bbb571/src/imagination/pco/pco_isa.py#L51"
quote = "('samp_num', 53),"
terms = ["SR.INST_NUM"]
+++

Line 51 of `pco_isa.py` in Mesa's Rogue compiler (pco) names `inst_num`. It backs the glossary enum
value `SR.INST_NUM`: the instance's place in its 2x2 quad (x[0] + 2*y[0]).
