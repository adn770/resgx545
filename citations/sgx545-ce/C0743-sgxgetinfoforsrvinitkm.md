+++
id = "C0743"
source = "sgx545-ce"
locator = "src/services4/srvkm/devices/sgx/sgxinit.c:591"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/devices/sgx/sgxinit.c#L591"
quote = "PVRSRV_ERROR SGXGetInfoForSrvinitKM(IMG_HANDLE hDevHandle, PVRSRV_HEAP_INFO_KM *pasHeapInfo, IMG_DEV_PHYADDR *psPDDevPAddr)"
terms = ["SGXGetInfoForSrvinitKM"]
+++

Line 591 of `sgxinit.c` in Intel's GPL DDK 1.7 kernel module for Cedarview names
`SGXGetInfoForSrvinitKM`. It backs the glossary function `SGXGetInfoForSrvinitKM`: kernel side of
SGXGetInfoForSrvInit.
