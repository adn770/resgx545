+++
id = "C0150"
source = "intel-ctp-santos10"
locator = "drivers/staging/mrst/pvr/services4/srvkm/devices/sgx/sgxutils.h:184"
link = "https://github.com/trevd/android_kernel_samsung_santos10/blob/09fd129b1eb122f11ff12441c65dca778d9602bb/drivers/staging/mrst/pvr/services4/srvkm/devices/sgx/sgxutils.h#L184"
quote = "SGXMKIF_HWTRANSFERCONTEXT or SGXMKIF_HW2DCONTEXT"
terms = ["hw_2d_context", "hw_transfer_context"]
+++

Line 184 of `sgxutils.h` in Samsung's Santos10 kernel (DDK 1.9) declares `SGXMKIF_HW2DCONTEXT` and
`SGXMKIF_HWTRANSFERCONTEXT`. It backs the glossary structure `hw_2d_context`: HW 2D context; no 2D
core on SGX545; and the glossary structure `hw_transfer_context`: HW transfer context.
