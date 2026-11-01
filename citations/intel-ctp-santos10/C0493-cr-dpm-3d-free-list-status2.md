+++
id = "C0493"
source = "intel-ctp-santos10"
locator = "drivers/staging/mrst/pvr/services4/srvkm/devices/sgx/sgxinit.c:1407"
link = "https://github.com/trevd/android_kernel_samsung_santos10/blob/09fd129b1eb122f11ff12441c65dca778d9602bb/drivers/staging/mrst/pvr/services4/srvkm/devices/sgx/sgxinit.c#L1407"
quote = "SGXDumpDebugReg(psDevInfo, ui32CoreNum, \"EUR_CR_DPM_3D_FREE_LIST_STATUS2: \", EUR_CR_DPM_3D_FREE_LIST_STATUS2);"
terms = ["CR_DPM_3D_FREE_LIST_STATUS2"]
+++

Line 1407 of `sgxinit.c` in Samsung's Santos10 kernel (DDK 1.9) names
`EUR_CR_DPM_3D_FREE_LIST_STATUS2`. It backs the glossary register `CR_DPM_3D_FREE_LIST_STATUS2`: DPM
3D free-list status, word 2.
