+++
id = "C0373"
source = "openpvrsgx-1.9"
locator = "drivers/gpu/drm/pvrsgx/1.9.2253347/services4/srvkm/devices/sgx/sgxinit.c:1332"
link = "https://github.com/openpvrsgx-devgroup/linux_openpvrsgx/blob/2342ce92fdde66ac5a7ed7548b47a3a0836c9e77/drivers/gpu/drm/pvrsgx/1.9.2253347/services4/srvkm/devices/sgx/sgxinit.c#L1332"
quote = "SGXDumpDebugReg(psDevInfo, ui32CoreNum, \"EUR_CR_MTE_CTRL: \", EUR_CR_MTE_CTRL);"
terms = ["cmd_ta.mte_ctrl"]
+++

Line 1332 of `sgxinit.c` in the openpvrsgx DDK 1.9 names `EUR_CR_MTE_CTRL`. It backs the glossary
field `cmd_ta.mte_ctrl`: MTE control: the TA kick loads this word into CR_MTE_CTRL (0x023c).
