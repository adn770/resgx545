+++
id = "C0497"
source = "intel-ctp-santos10"
locator = "drivers/staging/mrst/pvr/services4/srvkm/devices/sgx/sgxinit.c:1410"
link = "https://github.com/trevd/android_kernel_samsung_santos10/blob/09fd129b1eb122f11ff12441c65dca778d9602bb/drivers/staging/mrst/pvr/services4/srvkm/devices/sgx/sgxinit.c#L1410"
quote = "SGXDumpDebugReg(psDevInfo, ui32CoreNum, \"EUR_CR_DPM_PAGE: \", EUR_CR_DPM_PAGE);"
terms = ["CR_DPM_PAGE"]
+++

Line 1410 of `sgxinit.c` in Samsung's Santos10 kernel (DDK 1.9) names `EUR_CR_DPM_PAGE`. It backs
the glossary register `CR_DPM_PAGE`: DPM page register: while a 3D frees pages it holds the pages
still held, as CR_DPM_PAGE_STATUS does, counting down to 0 (to 1, the global list's page, in a
partial render).
