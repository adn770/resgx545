// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
/* test_pds_api.c — unit test for the pds.h analysis API (run by test_pds.py).
 * The words are made up, none is taken from a program. */
#include "pds.h"
#include <stdio.h>

static int fails;
#define CHECK(c) do { if (!(c)) { printf("FAIL %s:%d: %s\n", __FILE__, __LINE__, #c); fails++; } } while (0)

int main(void) {
    int call, cond;
    uint32_t t;

    CHECK(pds_classify(0x070CA305) == PDS_T_IO);       /* movs doutu, ... */
    CHECK(pds_classify(0x07806406) == PDS_T_IO);       /* movs douta, ... */
    CHECK(pds_classify(0x07000000) == PDS_T_MOV);      /* movs mr, ... */
    CHECK(pds_classify(0x17000000) == PDS_T_MOV);      /* mov32 */
    CHECK(pds_classify(0x37000000) == PDS_T_LOAD);
    CHECK(pds_classify(0x3F000000) == PDS_T_STORE);
    CHECK(pds_classify(0x47000000) == PDS_T_ADD);
    CHECK(pds_classify(0x4F000000) == PDS_T_SUB);
    CHECK(pds_classify(0x67000000) == PDS_T_MUL);
    CHECK(pds_classify(0xCF623074) == PDS_T_AND);
    CHECK(pds_classify(0xD76AC473) == PDS_T_XOR);
    CHECK(pds_classify(0xF7000000) == PDS_T_SHL);
    CHECK(pds_classify(0x87820001) == PDS_T_CMP);      /* tstz */
    CHECK(pds_classify(0x9700003A) == PDS_T_JMP);
    CHECK(pds_classify(0x9F000010) == PDS_T_CALL);
    CHECK(pds_classify(0xA7000000) == PDS_T_RET);
    CHECK(pds_classify(0xAF000000) == PDS_T_HALT);
    CHECK(pds_classify(0xB0000000) == PDS_T_NOP);
    CHECK(pds_classify(0xBC000001) == PDS_T_ALU);      /* (if1) alum signed */
    CHECK(pds_classify(0x7F000000) == PDS_T_SYNC);     /* rfence */
    CHECK(pds_classify(0x705E4D75) == PDS_T_UNK);      /* reserved */

    CHECK(pds_predicated(0x90000015));                 /* (p0) bra */
    CHECK(!pds_predicated(0x9700003A));                /* bra */
    CHECK(!pds_predicated(0x30000000));                /* load: [26:24] is a count */
    CHECK(!pds_predicated(0xB0000000));                /* nop */

    CHECK(pds_branch(0x90000015, &call, &cond, &t) && !call && cond && t == 0x15);
    CHECK(pds_branch(0x9700003A, &call, &cond, &t) && !call && !cond && t == 0x3A);
    CHECK(pds_branch(0x9F07FFFF, &call, &cond, &t) && call && !cond && t == 0x7FFFF);
    CHECK(!pds_branch(0xAF000000, &call, &cond, &t));

    if (!fails) puts("ok");
    return fails != 0;
}
