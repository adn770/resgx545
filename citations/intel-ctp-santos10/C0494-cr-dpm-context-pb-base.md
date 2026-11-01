+++
id = "C0494"
source = "intel-ctp-santos10"
locator = "drivers/staging/mrst/pvr/services4/srvkm/devices/sgx/sgxinit.c:1403"
link = "https://github.com/trevd/android_kernel_samsung_santos10/blob/09fd129b1eb122f11ff12441c65dca778d9602bb/drivers/staging/mrst/pvr/services4/srvkm/devices/sgx/sgxinit.c#L1403"
quote = "SGXDumpDebugReg(psDevInfo, ui32CoreNum, \"EUR_CR_DPM_CONTEXT_PB_BASE: \", EUR_CR_DPM_CONTEXT_PB_BASE);"
terms = ["CR_DPM_CONTEXT_PB_BASE"]
+++

Line 1403 of `sgxinit.c` in Samsung's Santos10 kernel (DDK 1.9) names `EUR_CR_DPM_CONTEXT_PB_BASE`.
It backs the glossary register `CR_DPM_CONTEXT_PB_BASE`: parameter-buffer base of the DPM context.
