#!/bin/bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# deploy_tool.sh: build this tree's sgxfive-test on the laptop as ~/sgxfive-test-1135 (a userspace
# compile, no git on the laptop) and print the sha256 of the source file, of the copy the laptop
# built from and of the binary; env.toml's tool_sha256 is the binary's, tool_source_sha256 the source's.
cd "$(dirname "$0")/../.." || exit 1
sha256sum userspace/libsgxfive/tools/sgxfive-test.c
tar cf - --exclude=build userspace/libsgxfive include/uapi 2>/dev/null |
	ssh -o HostKeyAlias=cedar jtorra@10.42.0.2 'rm -rf ~/libsgxfive-1135 && mkdir ~/libsgxfive-1135 &&
	cd ~/libsgxfive-1135 && tar xf - 2>/dev/null; sha256sum userspace/libsgxfive/tools/sgxfive-test.c;
	cd userspace/libsgxfive && make -j2 build/sgxfive-test 2>&1 | grep -E " error |warning:";
	cp build/sgxfive-test ~/sgxfive-test-1135; sha256sum ~/sgxfive-test-1135'
