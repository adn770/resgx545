// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
/* test_usse_api.c — unit test for the usse.h analysis API (run by test_forms.py).
 * The words are made up (most are pinned.tsv's), none is taken from a program. */
#include "usse.h"
#include <stdio.h>

static int fails;
#define CHECK(c) do { if (!(c)) { printf("FAIL %s:%d: %s\n", __FILE__, __LINE__, #c); fails++; } } while (0)
#define T(w, t) CHECK(usse_classify(w##ull) == (t))

int main(void) {
    int call, cond, rel;
    int32_t off;

    /* the opcode classes outside class 31: every class gets a type */
    T(0x04177312E1041E82, USSE_T_MUL);     /* 0: p3 fadm */
    T(0x0C8FD53548E00B80, USSE_T_ALU);     /* 1: p3 fcos (float functions) */
    T(0x1696B120ABE009AE, USSE_T_MUL);     /* 2: !p1 fdp (dot products) */
    T(0x1E9CBA5573C9E6ED, USSE_T_ALU);     /* 3: !p1 fminmax */
    T(0x2603AA50288007C1, USSE_T_ALU);     /* 4: !p1 fdsy */
    T(0x28851001A0800180, USSE_T_MOV);     /* 5: mov */
    T(0x349AF6D51D566BAF, USSE_T_MUL);     /* 6: p3 fmad16 */
    T(0x3C16FFBC867AD2BB, USSE_T_MUL);     /* 7: efo */
    T(0x450BE523A0F652C2, USSE_T_MOV);     /* 8: !p0 unpcks16o8 */
    T(0x45BC610B137EEDE0, USSE_T_MOV);     /* 8: unpcks16u8 */
    T(0x4796F221A80DBA57, USSE_T_STORE);   /* 8: Pn statomic */
    T(0x41E1623071B90CAA, USSE_T_STORE);   /* 8: p0 statomic */
    T(0x4E8C596F6FDCB310, USSE_T_ALU);     /* 9: !p1 xor (test group) */
    T(0x5CC5F8112A916F0F, USSE_T_ALU);     /* 11: p3 xor */
    T(0x6B41B9266960C375, USSE_T_ALU);     /* 13: p2 shr */
    T(0x721EE0050156E400, USSE_T_ALU);     /* 14: p1 rlp */
    T(0x7E483110A45C61E3, USSE_T_ALU);     /* 15: !p1 or (test group) */
    T(0x82183E058709682D, USSE_T_ALU);     /* 16: p0 sop2 */
    T(0x8BC9F0C761CC3288, USSE_T_ALU);     /* 17: p0 sop3 */
    T(0x8D7452064367B83F, USSE_T_ALU);     /* 17: lrp */
    T(0x8AF24E4AC4760CA9, USSE_T_ALU);     /* 17: sop3c */
    T(0x96618E59F6000DF1, USSE_T_ALU);     /* 18: !p0 sop2wm */
    T(0x986BCF34A1D78207, USSE_T_MUL);     /* 19: ima8 */
    T(0xA529341D5ECF54FB, USSE_T_MUL);     /* 20: p1 ima16 */
    T(0xADE62CA746E17D5E, USSE_T_MUL);     /* 21: p1 imae */
    T(0xB406100228003C09, USSE_T_ALU);     /* 22: p1 adif */
    T(0xB7E7B607559C2B7C, USSE_T_ALU);     /* 22: bilin */
    T(0xB6F69682C673F73F, USSE_T_ALU);     /* 22: firv */
    T(0xBD325DBA81DE529D, USSE_T_ALU);     /* 23: p1 firh */
    T(0xC57A51C151E12E71, USSE_T_MUL);     /* 24: p1 u16dot4off */
    T(0xC9862263F1B7C589, USSE_T_MUL);     /* 25: fpma */
    T(0xD2CC13812D4C7323, USSE_T_MUL);     /* 26: p1 ima32 */
    T(0xD39130816E4037C8, USSE_T_DIV);     /* 26: idiv */
    T(0xDC08807FAF7C07ED, USSE_T_ALU);     /* 27: ima32+fmad16 (dual issue) */
    T(0xDBE303E9EF05EFD2, USSE_T_ALU);     /* 27: fmad (dual issue) */
    T(0xE3462855C88F4C00, USSE_T_LOAD);    /* 28: p2 smp3d (texture sampling) */
    T(0xE4F674D1CFB5FC00, USSE_T_LOAD);    /* 28: smp2d */
    T(0xEB21D069437D6625, USSE_T_LOAD);    /* 29: p2 ldab */
    T(0xECEEBE7AE0A4FFDB, USSE_T_LOAD);    /* 29: eldq */
    T(0xF3DF840FB0034741, USSE_T_STORE);   /* 30: p2 stld */

    /* class 31, flow control: branches, lapc, the pclink moves, nop */
    T(0xFB801A0000038EE0, USSE_T_CALL);    /* p2 ba.nosched.savelink.syncent */
    T(0xFE801E40000293D1, USSE_T_CALL);    /* !p1 br.nosched.savelink... */
    T(0xF800000000000010, USSE_T_JMP);     /* ba #0x10 */
    T(0xFE0808000000EA9B, USSE_T_CJMP);    /* !p1 bexception.nosched */
    T(0xFA0808400002D56B, USSE_T_CJMP);    /* p1 bexception.rel.nosched */
    T(0xF800008000000000, USSE_T_RET);     /* lapc */
    T(0xFB00088000000000, USSE_T_CRET);    /* p2 lapc.nosched */
    T(0xF80000C000002180, USSE_T_MOV);     /* mov pclink, r67 */
    T(0xF800010001C00000, USSE_T_MOV);     /* mov r14, pclink */
    T(0xFC0008C0C0000A80, USSE_T_MOV);     /* p3 mov.nosched pclink, sa21 */
    T(0xFE00090306E00000, USSE_T_MOV);     /* !p1 mov.nosched o[ih + #7], pclink */
    T(0xF800014000000000, USSE_T_NOP);     /* nop */
    T(0xF804015234567800, USSE_T_NOP);     /* nop.end, ignored bits set */
    T(0xF884094000000003, USSE_T_NOP);     /* nop.syncs.nosched.end.tog.trigger */
    T(0xFA8539763E0BD678, USSE_T_NOP);     /* nop.syncs.nosched.end */
    T(0xF800018000000000, USSE_T_UNK);     /* no form decodes it */

    /* limm */
    T(0xFCE44C7101FE9D67, USSE_T_MOV);     /* !p1 mov.skipinv.nosched.end o15, #... */

    /* ldr and str: the unit's registers */
    T(0xFE210801288A402A, USSE_T_LOAD);    /* ldr.nosched r68, #5290, drc1 */
    T(0xFEA108821D20003C, USSE_T_LOAD);    /* ldr.skipinv.nosched pa105, c60, drc2 */
    T(0xFE6734C36316181C, USSE_T_LOAD);    /* ldr pa24, #11292, drc3 */
    T(0xFEE298F6CD6025C9, USSE_T_LOAD);    /* ldr.skipinv.nosched pa107, r73, drc2 */
    T(0xFEAB0800A0150252, USSE_T_STORE);   /* str.skipinv.nosched #10834, #4 */
    T(0xFE2B0800B0001CC8, USSE_T_STORE);   /* str.nosched i72, #57 */
    T(0xFEE9C902AD27A6D4, USSE_T_STORE);   /* str.skipinv.nosched #3924, pa77 */
    T(0xFEE903B25ACD7D87, USSE_T_STORE);   /* str.skipinv c7, o123 */

    /* fences, mutexes, waits, cache control and phas: synchronisation */
    T(0xF820000100000000, USSE_T_SYNC);    /* idf drc1, bif */
    T(0xF920000100000000, USSE_T_SYNC);    /* wdf drc1 */
    T(0xF820C80200000000, USSE_T_SYNC);    /* idf.nosched drc2, reserved(=3) */
    T(0xF920080200000000, USSE_T_SYNC);    /* wdf.nosched drc2 */
    T(0xFF2008000000000D, USSE_T_SYNC);    /* wop.nosched.twopart #5 */
    T(0xFD20080000000020, USSE_T_SYNC);    /* lock.nosched #2 */
    T(0xFD20080000000021, USSE_T_SYNC);    /* release.nosched #2 */
    T(0xF8425B0030001B1B, USSE_T_SYNC);    /* ci.nosched.dm_nomatch ... */
    T(0xFA4C37950001D69A, USSE_T_SYNC);    /* phas.end #120474, ... */
    T(0xFA490800B0000C26, USSE_T_SYNC);    /* phas.nosched.end pa24, i38 */
    T(0xFACD2A77B72F0613, USSE_T_SYNC);    /* phas.end #198163, ... */
    T(0xFAC3E5A4EBF89490, USSE_T_SYNC);    /* phas i41, #16 */

    /* the MOE group and setm: writes of the unit's state */
    T(0xF81D0000700002F5, USSE_T_MOV);     /* smoa.nosched o5, i117 */
    T(0xF91D0000D00038AB, USSE_T_MOV);     /* smr */
    T(0xFA1D000040000569, USSE_T_MOV);     /* smlsi */
    T(0xFB1D00009000112A, USSE_T_MOV);     /* smbo */
    T(0xF814F665C4914A6B, USSE_T_MOV);     /* smoa, immediates */
    T(0xF914C6BF7134D1B1, USSE_T_MOV);     /* smr, immediates */
    T(0xFB14EFE57608B328, USSE_T_MOV);     /* smbo, immediates */
    T(0xFA1435A182E5B5ED, USSE_T_MOV);     /* smlsi, immediates */
    T(0xFC1472572407A299, USSE_T_MOV);     /* imo */
    T(0xFD14000000000001, USSE_T_MOV);     /* setfc */
    T(0xFE9C580101A00000, USSE_T_MOV);     /* moest */
    T(0xFA2008000000000B, USSE_T_MOV);     /* setm */

    /* the emits and the visibility test group: output to other units */
    T(0xFB2E0B07002DD700, USSE_T_IO);      /* emitpix1 */
    T(0xFBE70ACB90E1BB44, USSE_T_IO);      /* emitpix2 */
    T(0xFB26B8B69A2CA157, USSE_T_IO);      /* emitpds */
    T(0xFB2D4E0090200997, USSE_T_IO);      /* emitmtest */
    T(0xFB267E0340202BD2, USSE_T_IO);      /* emitmtevtx */
    T(0xFB26CC02A020006B, USSE_T_IO);      /* emitvcbst */
    T(0xFB26DE00A0200044, USSE_T_IO);      /* emitvcbvtx */
    T(0xF83F0804200493EA, USSE_T_IO);      /* pcoeff */
    T(0xF834880000000000, USSE_T_IO);      /* ptoff */
    T(0xF9F20DEB61718A0C, USSE_T_IO);      /* p1 atst8 */
    T(0xFBB50C2C800F4F6F, USSE_T_IO);      /* p1 depthf */

    /* branch targets */
    CHECK(usse_branch(0xFB801A0000038EE0ull, &call, &cond, &rel, &off) == 1);
    CHECK(call == 1 && cond == 1 && rel == 0 && off == 0x38EE0);
    CHECK(usse_branch(0xFE801E40000293D1ull, &call, &cond, &rel, &off) == 1);
    CHECK(call == 1 && cond == 1 && rel == 1 && off == -0x16C2F);
    CHECK(usse_branch(0xF800008000000000ull, &call, &cond, &rel, &off) == 0);   /* lapc */

    if (fails)
        return 1;
    printf("ok\n");
    return 0;
}
