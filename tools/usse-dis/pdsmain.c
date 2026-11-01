// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
/* pdsmain.c — pds-dis CLI. Disassembles a raw PDS program: little-endian 32-bit
 * words, the first <data_dwords> of which are the data segment, one line per
 * word, easy to diff:
 *
 *   <index>: 0x<HEX8>\t<text>
 *
 * Usage: pds-dis [--which] [--regs] <program.bin> <data_dwords> | --forms
 *
 * --forms lists the form table (index, mask, value, the bits the form reads,
 * pattern), as usse-dis --forms does. --which appends "\t#<n>", the index of
 * the form that decoded each instruction (-1 for none). --regs follows each
 * data dword's "data" with the register it loads: the segment is stored in
 * rows of four dwords, ds0[2r], ds0[2r+1], ds1[2r], ds1[2r+1]. */
#include "pds.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc > 1 && !strcmp(argv[1], "--forms")) {
        for (size_t i = 0; i < pds_nforms; i++) {
            const usse_form *fm = &pds_forms[i];
            printf("%zu\t%08X\t%08X\t%08X\t%s\n", i, (unsigned)fm->mask, (unsigned)fm->val,
                   (unsigned)usse_form_bits(fm), fm->pat ? fm->pat : "(reject)");
        }
        return 0;
    }
    int which = 0, regs = 0;
    const char *prog = argv[0];
    while (argc > 1 && argv[1][0] == '-' && argv[1][1] == '-') {
        if (!strcmp(argv[1], "--which")) {
            which = 1;
        } else if (!strcmp(argv[1], "--regs")) {
            regs = 1;
        } else {
            fprintf(stderr, "%s: unknown option %s\n", prog, argv[1]);
            return 2;
        }
        argv++;
        argc--;
    }
    if (argc < 3) {
        fprintf(stderr, "usage: %s [--which] [--regs] <program.bin> <data_dwords> | --forms\n", prog);
        return 2;
    }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror(argv[1]); return 1; }
    unsigned data = (unsigned)strtoul(argv[2], 0, 0), i = 0;
    unsigned char b[4];
    while (fread(b, 1, 4, f) == 4) {
        uint32_t w = b[0] | b[1] << 8 | b[2] << 16 | (uint32_t)b[3] << 24;
        char txt[128] = "data";
        if (i >= data) {
            pds_decode(w, txt, sizeof txt);
        } else if (regs) {
            snprintf(txt, sizeof txt, "data ds%u[%u]", i >> 1 & 1, (i >> 2) * 2 + (i & 1));
        }
        printf("%u: 0x%08X\t%s", i, w, txt);
        if (which && i >= data) {
            char t[128];
            const usse_form *fm = usse_form_decode_in(&pds_table, w, t, sizeof t);
            printf("\t#%ld", fm ? (long)(fm - pds_forms) : -1L);
        }
        putchar('\n');
        i++;
    }
    fclose(f);
    return 0;
}
