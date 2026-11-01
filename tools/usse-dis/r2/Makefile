# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# radare2 USSE arch plugin — out-of-tree build.
# R2_PREFIX, the prefix of your radare2 install, is required: make R2_PREFIX=<prefix>.
ifeq ($(R2_PREFIX),)
ifneq ($(MAKECMDGOALS),clean)
$(error set R2_PREFIX to your radare2 prefix: make R2_PREFIX=<prefix>)
endif
endif
R2_INC    := $(R2_PREFIX)/include/libr
R2_USER_PLUGINS := $(shell $(R2_PREFIX)/bin/radare2 -H R2_USER_PLUGINS 2>/dev/null)

UNAME := $(shell uname)
ifeq ($(UNAME),Darwin)
  SOEXT   := dylib
  LDEXTRA := -undefined dynamic_lookup
else
  SOEXT   := so
  LDEXTRA :=
endif

CFLAGS  += -fPIC -Wall -Wextra -O2 -std=c11 -I$(R2_INC) -I..
PLUGIN   := arch_usse.$(SOEXT)

$(PLUGIN): arch_usse.c ../usse.c ../usse.h ../usse_form.c ../usse_form.h ../usse_table.inc $(wildcard ../forms/*.inc)
	$(CC) $(CFLAGS) -shared -o $@ arch_usse.c ../usse.c ../usse_form.c $(LDEXTRA)

install: $(PLUGIN)
	mkdir -p "$(R2_USER_PLUGINS)"
	cp $(PLUGIN) "$(R2_USER_PLUGINS)/"
	@echo "installed $(PLUGIN) -> $(R2_USER_PLUGINS)"

uninstall:
	rm -f "$(R2_USER_PLUGINS)/$(PLUGIN)"

clean:
	rm -f $(PLUGIN)

.PHONY: install uninstall clean
