# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The kick builder (kick.py, FW-4 (a)) against the kept words of the job it rebuilds: our
kernel's structures, built from our code at the session's commits, must be the words the laptop
read (F4 of plan-fwsim: a mismatch is first a builder bug). Without the fork, the commits, a C
compiler or the public data the tests skip, and a skip is not a pass. No firmware is read."""
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import kick  # noqa: E402

S = kick.SESSIONS["r9-c-off"]
# The words of the context whose kept value after the job is not what the kernel wrote (the kept
# files themselves, words.0 -> words.1): the firmware's and the hardware's, which the builder does
# not write. Render details words 53, 76-78 and 82 hold TA command words of the job (RD_COPIES).
NOT_THE_KERNELS = {("ctx", 0), ("rtds", 1), ("pb", 5), ("pb", 6), ("pb", 8), ("kw", 2),
                   ("rd", 53), ("rd", 76), ("rd", 77), ("rd", 78), ("rd", 80),
                   ("rd", 81), ("rd", 82), ("rd", 83)}
# render details word -> the byte offset in the built TA command of the word its kept value equals
# (the render flags, the three spec-object words, the first 3D status word's address)
RD_COPIES = {53: 0x1C, 76: 0x08, 77: 0x0C, 78: 0x10, 82: 0x218}


@pytest.fixture(scope="module")
def built():
    try:
        return kick.build(S)
    except kick.Unavailable as e:
        pytest.skip(f"SKIPPED, NOT PASSED: {e}")


def test_ctx_header_keeps_only_the_offsets():
    h = kick.ctx_header("#define SGXFIVE_CTX_CCB_OFF\t0\n#define SGXFIVE_CTX_HW_OFF\t(X + 0x000)\t/* HW */\n"
                        "#define OTHER 1\nstruct x;\n")
    assert "#define SGXFIVE_CTX_CCB_OFF 0" in h
    assert "#define SGXFIVE_CTX_HW_OFF (X + 0x000)" in h
    assert "OTHER" not in h and "struct" not in h


def test_inputs_come_from_the_kept_words_before_the_job():
    try:
        i = kick.inputs(S)
    except kick.Unavailable as e:
        pytest.skip(f"SKIPPED, NOT PASSED: {e}")
    assert i == {"mem": 0x32400000, "pd_phys": 0x0761F000, "slot": 0, "max_w": 64, "max_h": 64}


def test_the_built_context_is_the_kept_one_before_the_job(built):
    w0 = kick.kept_words(S, 0)
    for space in ("ctx", "rtds", "pb", "kw", "rd"):
        assert built["init"][space] == {i: w0[space].get(i, 0) for i in built["init"][space]}, space


def test_the_job_writes_are_the_kept_words_after_it_but_the_firmwares(built):
    w1 = kick.kept_words(S, 1)
    differ = {(sp, i) for sp in ("ctx", "rtds", "pb", "kw", "rd")
              for i, v in built["job"][sp].items() if w1[sp].get(i, 0) != v}
    assert differ == NOT_THE_KERNELS


def test_the_kernel_did_not_write_the_words_the_firmware_did(built):
    """The words of NOT_THE_KERNELS keep their creation value through the kernel's job writes."""
    for sp, i in NOT_THE_KERNELS:
        assert built["job"][sp][i] == built["init"][sp][i], (sp, i)


def test_the_ta_command_is_one_scene_kick_in_the_ccb(built):
    ta = built["job"]["ta"]
    assert ta[0] == built["size"] == 0x2C0                  # the size word: its CCB stride
    assert ta[1] & 3 == 3                                    # FIRST and LAST: the whole scene
    assert built["job"]["ctl"] == {0: 0x2C0, 1: 0}           # host write offset past it
    assert built["job"]["kw"][1] == 1                        # pending: one kick
    assert ta[0x40 // 4] == built["addr"]["rtds"]            # its RT data set
    assert ta[0x38 // 4] == built["addr"]["rd"]              # its render details


def test_render_details_words_the_kernel_left_hold_the_ta_commands_words(built):
    w1 = kick.kept_words(S, 1)
    for i, off in RD_COPIES.items():
        assert built["job"]["rd"][i] == 0 and w1["rd"][i] == built["job"]["ta"][off // 4], i
