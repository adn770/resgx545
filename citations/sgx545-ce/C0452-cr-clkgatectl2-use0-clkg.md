+++
id = "C0452"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:68"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L68"
quote = "#define EUR_CR_CLKGATECTL2_USE0_CLKG_MASK   0x000000C0U"
terms = ["CR_CLKGATECTL2.USE0_CLKG"]
+++

Line 68 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_CLKGATECTL2_USE0_CLKG`. It backs the glossary bit field `CR_CLKGATECTL2.USE0_CLKG`:
clock-gating mode of the USSE 0 (0 on, 1 off, 2 auto per psb_regs.h).
