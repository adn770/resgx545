# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
CC      ?= cc
CFLAGS  ?= -O2 -Wall -Wextra -Werror -std=c11
OBJS     = usse.o usse_form.o main.o

all: usse-dis pds-dis

usse-dis: $(OBJS)
	$(CC) $(CFLAGS) -o $@ $(OBJS)

usse.o: usse.c usse.h usse_form.h usse_table.inc $(wildcard forms/*.inc)
usse_form.o: usse_form.c usse_form.h
main.o: main.c usse.h usse_form.h

pds-dis: pds.c pdsmain.c pds.h pds_table.inc usse_form.c usse_form.h usse.o usse_form.o
	$(CC) $(CFLAGS) -o $@ pds.c pdsmain.c usse.o usse_form.o

clean:
	rm -f $(OBJS) usse-dis pds-dis

.PHONY: all clean
