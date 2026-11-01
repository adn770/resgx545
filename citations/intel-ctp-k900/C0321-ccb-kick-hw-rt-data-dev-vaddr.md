+++
id = "C0321"
source = "intel-ctp-k900"
locator = "linux/modules/intel_media/graphics/sgx/services4/include/sgxinfo.h:237"
link = "https://github.com/xxx-man/android_kernel_lenovo_redhookbay/blob/41a61d5ffcbee9e185a2aeeb980e69de9274adf6/linux/modules/intel_media/graphics/sgx/services4/include/sgxinfo.h#L237"
quote = "IMG_DEV_VIRTADDR\tsHWRTDataDevAddr;"
terms = ["cmd_ta.hw_rt_data_dev_vaddr"]
+++

Line 237 of `sgxinfo.h` in the Lenovo K900 kernel (DDK 1.11) declares `sHWRTDataDevAddr`. It backs
the glossary field `cmd_ta.hw_rt_data_dev_vaddr`: RT data used by this kick.
