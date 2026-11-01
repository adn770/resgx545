/* SPDX-License-Identifier: MIT */
/* Host shim for the kernel headers sgxfive_owntask.c and sgx_fw.c include (tools/fwtask/host). */
#ifndef HOST_LINUX_TYPES_H
#define HOST_LINUX_TYPES_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <sys/types.h>

typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
typedef int64_t loff_t;

#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))

#endif
