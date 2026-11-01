# Userspace build of the SGX545 firmware loader core and its fwdump harness.
# tools/fwcutter/test_cloader.py builds fwdump and checks it against fwload.py.
CC      ?= cc
CFLAGS  ?= -O2 -g
WERROR  ?= -Werror
# override keeps the warning flags when CFLAGS is given on the command line
override CFLAGS += -std=c11 -Wall -Wextra $(WERROR) -pedantic

all: fwdump

fwdump: fwdump.o sgx_fw.o
	$(CC) $(CFLAGS) -o $@ fwdump.o sgx_fw.o

fwdump.o: fwdump.c sgx_fw.h sgx_fw_types.h
sgx_fw.o: sgx_fw.c sgx_fw.h sgx_fw_types.h

# the cross-check against the reference loader is tools/fwcutter/test_cloader.py;
# this builds the harness and runs it on a file that must be rejected
test: fwdump
	@printf 'not a firmware file' > fwdump-test.fw; : > fwdump-test.txt; \
	if ./fwdump fwdump-test.fw fwdump-test.txt . >/dev/null 2>&1; then \
		echo "fwdump accepted a bad file"; rm -f fwdump-test.*; exit 1; fi; \
	rm -f fwdump-test.*; echo "fwdump ok"

clean:
	rm -f fwdump *.o

.PHONY: all test clean
