+++
id = "C0109"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:37"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L37"
quote = "#define EUR_CR_CLKGATECTL_TSP_CLKG_MASK     0x00000030U"
terms = ["Texture and Shading Processor (TSP)"]
+++

Line 37 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_CLKGATECTL_TSP_CLKG` and `TSP`. It backs the glossary bit field `CR_CLKGATECTL.TSP_CLKG`:
clock-gating mode of the TSP (0 on, 1 off, 2 auto per psb_regs.h); and the glossary unit `Texture
and Shading Processor (TSP)`: TSP block (its clock gate).
