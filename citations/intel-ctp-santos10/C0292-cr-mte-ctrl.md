+++
id = "C0292"
source = "intel-ctp-santos10"
locator = "drivers/staging/mrst/pvr/services4/srvkm/devices/sgx/sgxinit.c:1395"
link = "https://github.com/trevd/android_kernel_samsung_santos10/blob/09fd129b1eb122f11ff12441c65dca778d9602bb/drivers/staging/mrst/pvr/services4/srvkm/devices/sgx/sgxinit.c#L1395"
quote = "SGXDumpDebugReg(psDevInfo, ui32CoreNum, \"EUR_CR_MTE_CTRL: \", EUR_CR_MTE_CTRL);"
terms = ["CR_MTE_CTRL"]
+++

Line 1395 of `sgxinit.c` in Samsung's Santos10 kernel (DDK 1.9) names `EUR_CR_MTE_CTRL`. It backs
the glossary register `CR_MTE_CTRL`: macro tiling engine control.
