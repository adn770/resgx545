+++
id = "C0073"
source = "intel-ctp-santos10"
locator = "drivers/staging/mrst/pvr/services4/srvkm/devices/sgx/sgxinit.c:1398"
link = "https://github.com/trevd/android_kernel_samsung_santos10/blob/09fd129b1eb122f11ff12441c65dca778d9602bb/drivers/staging/mrst/pvr/services4/srvkm/devices/sgx/sgxinit.c#L1398"
quote = "SGXDumpDebugReg(psDevInfo, ui32CoreNum, \"EUR_CR_EVENT_OTHER_PDS_INFO: \", EUR_CR_EVENT_OTHER_PDS_INFO);"
terms = ["CR_EVENT_OTHER_PDS_INFO"]
+++

Line 1398 of `sgxinit.c` in Samsung's Santos10 kernel (DDK 1.9) names `EUR_CR_EVENT_OTHER_PDS_INFO`.
It backs the glossary register `CR_EVENT_OTHER_PDS_INFO`: other-event task sizes.
