// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
/*
 * pingen: writes pinned.tsv (make pinned), one made-up word per form of the USSE and PDS
 * tables. For each form it draws words with the form's fields at random (a fixed seed, so
 * the output only changes when a table does), keeps the words that decode with that form,
 * re-encodes the decoded text where the encoder gives back the same form and text, and
 * keeps the best-spread candidate: fields off their defaults, nonzero and distinct from each
 * other. A form the encoder never reaches (its distinguishing bits lie outside its fields)
 * gets a decoded word drawn with every non-fixed bit at random.
 */
#include "usse.h"
#include "usse_form.h"
#include "pds.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t seed = 0x9e3779b97f4a7c15ull;

static uint64_t rnd(void) {
    seed ^= seed >> 12;
    seed ^= seed << 25;
    seed ^= seed >> 27;
    return seed * 0x2545F4914F6CDD1Dull;
}

static uint64_t fieldbits(const usse_form *fm) {
    uint64_t b = 0;

    for (int i = 0; i < USSE_MAX_FIELDS && fm->f[i].k; i++)
        for (int c = 0; c < USSE_MAX_CHUNKS && fm->f[i].c[c].w; c++)
            b |= (fm->f[i].c[c].w >= 64 ? ~0ull : ((1ull << fm->f[i].c[c].w) - 1))
                 << fm->f[i].c[c].lo;
    return b;
}

static int nfields(const usse_form *fm) {
    int n = 0;

    while (n < USSE_MAX_FIELDS && fm->f[n].k)
        n++;
    return n;
}

/* fields off their default, nonzero and distinct from each other score higher (5 at most) */
static int field_score(const usse_form *fm, uint64_t w) {
    uint32_t v[USSE_MAX_FIELDS];
    int n = 0, sc = 0;

    for (int i = 0; i < USSE_MAX_FIELDS && fm->f[i].k; i++) {
        int dup = 0;

        v[n] = usse_field_get(&fm->f[i], w);
        if (v[n] != usse_field_get(&fm->f[i], fm->dflt))
            sc += 2;
        if (v[n])
            sc++;
        for (int j = 0; j < n; j++)
            if (v[j] == v[n])
                dup = 1;
        if (!dup)
            sc += 2;
        n++;
    }
    return sc;
}

/*
 * Bits a pinned word must have set, so that a field one bit narrower reads it differently:
 * idiv's repeat count is the four bits 44..47 (three until 11.15), so its pinned word needs
 * bit 47 set, a count of 8 or more.
 */
static const struct { const char *pat; uint64_t bit; } high_bits[] = {
    { "idiv", 1ull << 47 },
};

static int high_bits_set(const usse_form *fm, uint64_t w) {
    for (size_t i = 0; i < sizeof high_bits / sizeof *high_bits; i++)
        if (fm->pat && strstr(fm->pat, high_bits[i].pat) && !(w & high_bits[i].bit))
            return 0;
    return 1;
}

/* the same on the numbers of the decoded text */
static int text_score(const char *t) {
    unsigned long long v[64];
    int n = 0, sc = 0;

    while (*t && n < 64) {
        if (*t >= '0' && *t <= '9') {
            char *e;
            unsigned long long x = strtoull(t, &e, 0);
            int dup = 0;

            t = e;
            for (int j = 0; j < n; j++)
                if (v[j] == x)
                    dup = 1;
            sc += dup ? -4 : (x ? 3 : 1);
            v[n++] = x;
        } else {
            t++;
        }
    }
    return sc;
}

static int run(const usse_table *t, const char *tag, int width) {
    int missing = 0;

    for (size_t i = 0; i < t->n; i++) {
        const usse_form *fm = &t->forms[i];
        uint64_t fb = fieldbits(fm) & ~fm->mask;
        uint64_t bits = usse_form_bits(fm);
        uint64_t lim = width == 32 ? 0xFFFFFFFFull : ~0ull;
        uint64_t best = 0;
        int bests = -1, nf = nfields(fm);
        char btxt[256] = "";

        for (int k = 0; k < 40000; k++) {
            uint64_t w = (fm->val | (rnd() & fb) | (fm->dflt & ~bits)) & lim;
            char txt[256], t2[256];
            uint64_t e2;
            int sc, ts, r = 0;

            if (k >= 20000) {
                if (bests >= 0)
                    break;
                w = (fm->val | (rnd() & ~fm->mask)) & lim;
            }
            if (usse_form_decode_in(t, w, txt, sizeof txt) != fm || !high_bits_set(fm, w))
                continue;
            ts = text_score(txt);
            if (5 * nf + ts + 100 <= bests)
                continue;       /* cannot beat the best even re-encoded: skip the encoder */
            if (usse_form_encode_in(t, txt, &e2) &&
                usse_form_decode_in(t, e2, t2, sizeof t2) == fm && !strcmp(t2, txt)) {
                if (high_bits_set(fm, e2)) {
                    w = e2;
                    r = 1;
                }
            }
            sc = field_score(fm, w) + ts + r * 100;
            if (sc > bests) {
                bests = sc;
                best = w;
                strcpy(btxt, txt);
            }
        }
        if (bests < 0) {
            fprintf(stderr, "%s form %zu: no word decodes with it\n", tag, i);
            missing = 1;
            continue;
        }
        printf("%s\t%zu\t%0*llX\t%s\n", tag, i, width / 4, (unsigned long long)best, btxt);
    }
    return missing;
}

int main(void) {
    int missing;

    /* REUSE-IgnoreStart */
    printf("# SPDX-License-Identifier: MIT\n"
           "# SPDX-FileCopyrightText: 2026 Josep Torra\n"
           "# One made-up word per form (test_pinned.py): instruction set, form index, word, the\n"
           "# decoder's text. Written by pingen.c (make pinned); regenerate it when a form\n"
           "# changes on purpose, and review the lines that change.\n");
    /* REUSE-IgnoreEnd */
    missing = run(&usse_table_main, "usse", 64);
    missing |= run(&pds_table, "pds", 32);
    return missing;
}
