+++
id = "C0499"
source = "intel-ctp-santos10"
locator = "drivers/staging/mrst/pvr/services4/srvkm/devices/sgx/sgxinit.c:1404"
link = "https://github.com/trevd/android_kernel_samsung_santos10/blob/09fd129b1eb122f11ff12441c65dca778d9602bb/drivers/staging/mrst/pvr/services4/srvkm/devices/sgx/sgxinit.c#L1404"
quote = "SGXDumpDebugReg(psDevInfo, ui32CoreNum, \"EUR_CR_DPM_TA_ALLOC_FREE_LIST_STATUS1: \", EUR_CR_DPM_TA_ALLOC_FREE_LIST_STATUS1);"
terms = ["CR_DPM_TA_ALLOC_FREE_LIST_STATUS1"]
+++

Line 1404 of `sgxinit.c` in Samsung's Santos10 kernel (DDK 1.9) names
`EUR_CR_DPM_TA_ALLOC_FREE_LIST_STATUS1`. It backs the glossary register
`CR_DPM_TA_ALLOC_FREE_LIST_STATUS1`: DPM TA allocation free-list status, word 1.
