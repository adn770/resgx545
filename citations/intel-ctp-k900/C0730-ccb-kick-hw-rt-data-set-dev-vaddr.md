+++
id = "C0730"
source = "intel-ctp-k900"
locator = "linux/modules/intel_media/graphics/sgx/services4/include/sgxinfo.h:236"
link = "https://github.com/xxx-man/android_kernel_lenovo_redhookbay/blob/41a61d5ffcbee9e185a2aeeb980e69de9274adf6/linux/modules/intel_media/graphics/sgx/services4/include/sgxinfo.h#L236"
quote = "IMG_DEV_VIRTADDR\tsHWRTDataSetDevAddr;"
terms = ["cmd_ta.hw_rt_data_set_dev_vaddr"]
+++

Line 236 of `sgxinfo.h` in the Lenovo K900 kernel (DDK 1.11) declares `sHWRTDataSetDevAddr`. It
backs the glossary field `cmd_ta.hw_rt_data_set_dev_vaddr`: RT data set.
