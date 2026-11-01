+++
id = "C0274"
source = "intel-ctp-santos10"
locator = "drivers/staging/mrst/pvr/services4/srvkm/devices/sgx/sgxinit.c:1400"
link = "https://github.com/trevd/android_kernel_samsung_santos10/blob/09fd129b1eb122f11ff12441c65dca778d9602bb/drivers/staging/mrst/pvr/services4/srvkm/devices/sgx/sgxinit.c#L1400"
quote = "SGXDumpDebugReg(psDevInfo, ui32CoreNum, \"EUR_CR_DPM_ZLS_PAGE_THRESHOLD: \", EUR_CR_DPM_ZLS_PAGE_THRESHOLD);"
terms = ["CR_DPM_ZLS_PAGE_THRESHOLD"]
+++

Line 1400 of `sgxinit.c` in Samsung's Santos10 kernel (DDK 1.9) names
`EUR_CR_DPM_ZLS_PAGE_THRESHOLD`. It backs the glossary register `CR_DPM_ZLS_PAGE_THRESHOLD`: ZLS
page threshold of the DPM.
