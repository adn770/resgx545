+++
id = "C0447"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:59"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L59"
quote = "#define EUR_CR_CLKGATECTL2_PBE_CLKG_MASK    0x00000003U"
terms = ["CR_CLKGATECTL2.PBE_CLKG"]
+++

Line 59 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_CLKGATECTL2_PBE_CLKG`. It backs the glossary bit field `CR_CLKGATECTL2.PBE_CLKG`:
clock-gating mode of the PBE (0 on, 1 off, 2 auto per psb_regs.h).
