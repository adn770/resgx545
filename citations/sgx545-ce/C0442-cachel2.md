+++
id = "C0442"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:62"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L62"
quote = "#define EUR_CR_CLKGATECTL2_CACHEL2_CLKG_MASK 0x0000000CU"
terms = ["CACHEL2", "CR_CLKGATECTL2.CACHEL2_CLKG"]
+++

Line 62 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines `CACHEL2` and
`EUR_CR_CLKGATECTL2_CACHEL2_CLKG`. It backs the glossary unit `CACHEL2`: level 2 cache [infer]; and
the glossary bit field `CR_CLKGATECTL2.CACHEL2_CLKG`: clock-gating mode of the L2 cache (0 on, 1
off, 2 auto per psb_regs.h).
