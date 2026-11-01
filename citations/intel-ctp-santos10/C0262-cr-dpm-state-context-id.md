+++
id = "C0262"
source = "intel-ctp-santos10"
locator = "drivers/staging/mrst/pvr/services4/srvkm/devices/sgx/sgxinit.c:1402"
link = "https://github.com/trevd/android_kernel_samsung_santos10/blob/09fd129b1eb122f11ff12441c65dca778d9602bb/drivers/staging/mrst/pvr/services4/srvkm/devices/sgx/sgxinit.c#L1402"
quote = "SGXDumpDebugReg(psDevInfo, ui32CoreNum, \"EUR_CR_DPM_STATE_CONTEXT_ID: \", EUR_CR_DPM_STATE_CONTEXT_ID);"
terms = ["CR_DPM_STATE_CONTEXT_ID"]
+++

Line 1402 of `sgxinit.c` in Samsung's Santos10 kernel (DDK 1.9) names `EUR_CR_DPM_STATE_CONTEXT_ID`.
It backs the glossary register `CR_DPM_STATE_CONTEXT_ID`: selects DPM context for load/store/alloc.
