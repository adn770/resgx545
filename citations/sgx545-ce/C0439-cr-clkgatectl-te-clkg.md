+++
id = "C0439"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:40"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L40"
quote = "#define EUR_CR_CLKGATECTL_TE_CLKG_MASK      0x000000C0U"
terms = ["CR_CLKGATECTL.TE_CLKG"]
+++

Line 40 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_CLKGATECTL_TE_CLKG`. It backs the glossary bit field `CR_CLKGATECTL.TE_CLKG`: clock-gating
mode of the TE (0 on, 1 off, 2 auto per psb_regs.h).
