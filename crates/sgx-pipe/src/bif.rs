// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! BIF: the MMU, directory lists, banks, requestors, fault fields (12.5).

use crate::Outcome;

/// Open questions that block the unit.
pub const OPEN: &[&str] = &["Q076", "Q108", "Q109", "Q110", "Q003"];

/// A refusing stub until the unit's sub-phase lands: the model never guesses. Among what it
/// refuses: the client directory's alias of the EDM's buffers (Q076), of which E980 held out that
/// only buffers 0 and 9 are needed, whatever set of the others is left out, for its scenes (E745:
/// no pair of 1 to 8, 10 and 11 needed together; E761: buffers 1 to 4 or 6 to 11 left out of two
/// overflowed 1024x768 renders kept them exact, buffer 0 left out faulted).
pub fn refuse() -> Outcome {
    Outcome::unsupported("the BIF is not modelled (12.5)", OPEN)
}

/// The `BIF_FAULT` word of the first render that runs the TA after a held TA write fault
/// (`BIF_INT_STAT` `int`, `BIF_FAULT` `held`) and the debugfs reset: the held job's page and
/// `SB`, through `list`, the directory list current at that TA run (`CID`, bits 3:0). E848 (h1,
/// h2, h4) and E891 (a0 to a2; H-LIST 2 of 2, H-WORD refuted); `flushed`, a BIF invalidate
/// (`CR_BIF_CTRL.INVAL_DC` set and cleared) while the fault was held, changes nothing (E892:
/// H-FLUSH refuted, H-PEND 3 of 3). Only the measured faults (0x90004, pages 0x20006 and
/// 0x2000a, `SB` 6, list 1) and lists are modelled; how many replays come before a render passes,
/// what ends them and the -110 boots after some resets are refused (Q003): the first boot after a
/// held reset timed out only after 0x90004 (E901, 54 of 147), not by the fault page (E919: pages
/// 0x20006 to 0x20009, E901's page rule refuted held out) nor by a CLEAR_FAULT or the hold's
/// length (E920), so no rule says which boot comes up.
pub fn replay_word(int: u32, held: u32, list: u32, flushed: bool) -> Result<u32, Outcome> {
    const RUN: &[(u32, u32, bool)] = &[
        (0x2000_a061, 1, false),
        (0x2000_a061, 2, false),
        (0x2000_6061, 1, false),
        (0x2000_6061, 2, false),
        (0x2000_a061, 1, true),
        (0x2000_a061, 2, true),
        (0x2000_6061, 1, true),
    ];
    if int != 0x90004 || !RUN.contains(&(held, list, flushed)) {
        return Err(Outcome::unsupported(
            &format!(
                "a replay after BIF_INT_STAT {int:#x}, BIF_FAULT {held:#x}, list {list}, flushed {flushed}: not run (E848, E891, E892)"
            ),
            &["Q003"],
        ));
    }
    Ok((held & !0xf) | list)
}

/// A client access through a page whose PTE flags debugfs `vm_pte_flags` set (Q108): the
/// transfer's or the 3D's pixel write (`FAULT_REQ` bit 5), the transfer's texture read of a copy's
/// source (bit 1), the render's read of its GENERAL page, the VDM stream, indices and vertices
/// (bit 3), the ZLS store of a depth-buffered render (bit 9, E965), the ZLS load of its depth
/// buffer (E1046).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PteAccess {
    PixelWrite,
    TextureRead,
    StreamRead,
    ZlsStore,
    ZlsLoad,
}

/// Where a PTE fault named its page: the mapping's first, or the last page the job wrote.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FaultPage {
    First,
    LastWritten,
}

/// A PTE fault: `BIF_INT_STAT`, the page `BIF_FAULT` names and its `SB`.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct PteFault {
    pub int_stat: u32,
    pub page: FaultPage,
    pub sb: u32,
}

/// How a job's access ends under PTE flags `pte` (WO 0x2, RO 0x4, CACHED 0x8, EDMPROT 0x10):
/// whether its pixels were written and the fault, if any.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct PteEnd {
    pub written: bool,
    pub fault: Option<PteFault>,
}

/// The measured PTE flags (E945, the r8-k2 triangle rows, frozen; E946, the transfer rows, read
/// post hoc; READONLY on a fill's write is E946's isolation control; E964 and E965, the r9-faults
/// rows, frozen): WRITEONLY lets the pixel writes land and then faults at the last page written
/// (`SB` 31; held out at 64 x 16 from row 16 and at 64 x 64, E964), lets the ZLS store land and
/// then faults at its last page (`SB` 0, E965), and faults the texture and stream reads before
/// anything is drawn; CACHECONSISTENT changes nothing either read showed; EDMPROTECT faults a
/// pixel write and the ZLS store at the first page (`FAULT_TYPE` 2) and lets the stream read and
/// a copy's texture read of its READONLY source through (E964); WRITEONLY with EDMPROTECT faults
/// a pixel write as EDMPROTECT alone (E965). CACHECONSISTENT on the depth buffer the ZLS loads
/// ends clean, and with it or without it the load of a second render on the context reads what
/// the host wrote between the renders, never the first render's data (E1046, r14-bif, frozen).
/// Alone on a mapping that is only read (E1071, r18-flag, held out): WRITEONLY faults the ZLS load
/// (0x80200) and a texture read of the probe's scratch (0x80002) at the mapping's first page
/// (`SB` 0) before anything is drawn, and EDMPROTECT lets both through (the load stores E1046's
/// store byte for byte, the texture read gives E1047's image). Both together (0x12) on those two
/// reads fault as WRITEONLY alone (0x80200, 0x80002, the first page; E1108, r29-flag, held out),
/// not with EDMPROTECT's type as a write does (E965). Any other flag and access is refused (Q108).
pub fn pte_access(pte: u32, access: PteAccess) -> Result<PteEnd, Outcome> {
    use FaultPage::*;
    use PteAccess::*;
    let fault = |int_stat, page, sb| PteEnd {
        written: page == LastWritten,
        fault: Some(PteFault { int_stat, page, sb }),
    };
    let clean = PteEnd { written: true, fault: None };
    Ok(match (pte, access) {
        (0, _) => clean,
        (0x2, PixelWrite) => fault(0x80020, LastWritten, 31),
        (0x2, StreamRead) => fault(0x80008, First, 0),
        (0x6, TextureRead) => fault(0x80002, First, 0),
        (0x4, PixelWrite) => fault(0x80020, First, 0),
        (0x2, ZlsStore) => fault(0x80200, LastWritten, 0),
        (0x8, StreamRead) | (0xc, TextureRead) | (0x10, StreamRead) | (0x14, TextureRead) => clean,
        (0x8, ZlsLoad) | (0x10, ZlsLoad) | (0x10, TextureRead) => clean,
        (0x2, ZlsLoad) | (0x12, ZlsLoad) => fault(0x80200, First, 0),
        (0x2, TextureRead) | (0x12, TextureRead) => fault(0x80002, First, 0),
        (0x10, PixelWrite) | (0x12, PixelWrite) => fault(0xa0020, First, 0),
        (0x10, ZlsStore) => fault(0xa0200, First, 0),
        _ => {
            return Err(Outcome::unsupported(
                &format!(
                    "PTE flags {pte:#x} on {access:?}: not run (E945, E946, E964, E965, E1046, E1071, E1108)"
                ),
                &["Q108"],
            ));
        }
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_stub_refuses_and_names_its_questions() {
        match refuse() {
            Outcome::Unsupported { ids, why } => {
                assert!(!ids.is_empty() && !why.is_empty());
                assert_eq!(ids, OPEN);
            }
            o => panic!("{o:?}"),
        }
    }

    #[test]
    fn the_replay_goes_through_the_list_of_the_next_ta_run() {
        // E848 h1, h2, h4; E891 a0, a1, a2: the job's page and SB, the list current at the next
        // TA run (2 after a fill took list 1)
        for (held, list, want) in [
            (0x2000_a061, 1, 0x2000_a061),
            (0x2000_a061, 2, 0x2000_a062),
            (0x2000_6061, 1, 0x2000_6061),
            (0x2000_6061, 2, 0x2000_6062),
        ] {
            assert_eq!(replay_word(0x90004, held, list, false), Ok(want), "{held:#x} {list}");
        }
    }

    #[test]
    fn a_bif_flush_while_the_fault_is_held_does_not_drop_the_replay() {
        // E892 b0, b1, b2: INVAL_DC set and cleared while held, then the reset; the replay as
        // without it (H-FLUSH refuted, H-PEND 3 of 3)
        assert_eq!(replay_word(0x90004, 0x2000_a061, 1, true), Ok(0x2000_a061));
        assert_eq!(replay_word(0x90004, 0x2000_a061, 2, true), Ok(0x2000_a062));
        assert_eq!(replay_word(0x90004, 0x2000_6061, 1, true), Ok(0x2000_6061));
    }

    #[test]
    fn what_no_replay_measured_is_refused() {
        let refused = |i, w, l, f| matches!(replay_word(i, w, l, f), Err(Outcome::Unsupported { .. }));
        assert!(refused(0x90100, 0x1000_0011, 1, false), "another requestor (E845: no replay)");
        assert!(refused(0x90004, 0x2000_8061, 1, false), "a page no replay was read at");
        assert!(refused(0x90004, 0x2000_a051, 1, false), "another SB");
        assert!(refused(0x90004, 0x2000_a062, 1, false), "a fault through list 2");
        assert!(refused(0x90004, 0x2000_a061, 3, false), "list 3 never ran");
        assert!(refused(0x90004, 0x2000_6061, 2, true), "flushed, list 2 at 288 x 144: not run");
    }

    #[test]
    fn pte_flags_end_each_measured_access_as_the_r8_k2_rows() {
        // E945 (r8-k2 stage tri, frozen) and E946 (stage xf, read post hoc): the job's pixels
        // written or not, BIF_INT_STAT, the faulting page (the mapping's first or the image's
        // last) and SB
        use PteAccess::*;
        let fault = |int_stat, page, sb| Some(PteFault { int_stat, page, sb });
        let rows: &[(&str, u32, PteAccess, bool, Option<PteFault>)] = &[
            ("tri-wo-fb", 0x2, PixelWrite, true, fault(0x80020, FaultPage::LastWritten, 31)),
            ("xf-wo-fill", 0x2, PixelWrite, true, fault(0x80020, FaultPage::LastWritten, 31)),
            ("tri-wo-gen", 0x2, StreamRead, false, fault(0x80008, FaultPage::First, 0)),
            ("xf-wo-copy", 0x6, TextureRead, false, fault(0x80002, FaultPage::First, 0)),
            ("tri-cc-gen", 0x8, StreamRead, true, None),
            ("xf-cc-copy", 0xc, TextureRead, true, None),
            ("tri-edm-fb", 0x10, PixelWrite, false, fault(0xa0020, FaultPage::First, 0)),
            ("xf-edm-fill", 0x10, PixelWrite, false, fault(0xa0020, FaultPage::First, 0)),
            ("tri-edm-gen", 0x10, StreamRead, true, None),
            ("xf-c-ro", 0x4, PixelWrite, false, fault(0x80020, FaultPage::First, 0)),
        ];
        for (row, pte, access, written, fault) in rows {
            assert_eq!(pte_access(*pte, *access), Ok(PteEnd { written: *written, fault: *fault }), "{row}");
        }
        for access in [PixelWrite, TextureRead, StreamRead, ZlsStore, ZlsLoad] {
            assert_eq!(pte_access(0, access), Ok(PteEnd { written: true, fault: None }));
        }
    }

    #[test]
    fn pte_flags_end_each_measured_access_as_the_r9_faults_rows() {
        // E964 (r9-faults stage xf2, frozen) and E965 (tri2, frozen): WRITEONLY's fill writes land
        // and the fault names the page of the last pixel written, whatever the size (64 x 16 at y
        // 16, 64 x 64); EDMPROTECT lets a copy's texture read of its READONLY source through; the
        // two flags together fault as EDMPROTECT alone; on the ZLS store (FAULT_REQ bit 9)
        // EDMPROTECT faults at the first page, nothing stored, and WRITEONLY lets the store land,
        // then faults at the store's last page (SB 0)
        use PteAccess::*;
        let fault = |int_stat, page, sb| Some(PteFault { int_stat, page, sb });
        let rows: &[(&str, u32, PteAccess, bool, Option<PteFault>)] = &[
            ("xf-wo-fill-low", 0x2, PixelWrite, true, fault(0x80020, FaultPage::LastWritten, 31)),
            ("xf-wo-fill-64", 0x2, PixelWrite, true, fault(0x80020, FaultPage::LastWritten, 31)),
            ("xf-edm-copy", 0x14, TextureRead, true, None),
            ("tri-woedm-fb", 0x12, PixelWrite, false, fault(0xa0020, FaultPage::First, 0)),
            ("tri-edm-dst", 0x10, ZlsStore, false, fault(0xa0200, FaultPage::First, 0)),
            ("tri-wo-dst", 0x2, ZlsStore, true, fault(0x80200, FaultPage::LastWritten, 0)),
        ];
        for (row, pte, access, written, fault) in rows {
            assert_eq!(pte_access(*pte, *access), Ok(PteEnd { written: *written, fault: *fault }), "{row}");
        }
    }

    #[test]
    fn cacheconsistent_on_the_zls_load_ends_clean_as_the_r14_bif_rows() {
        // E1046 (r14-bif stage refill, frozen): CACHECONSISTENT on the depth buffer the ZLS loads
        // (rf-cc-keep, rf-cc-refill, rf-c-unread): no fault, both renders' loads read
        assert_eq!(pte_access(0x8, PteAccess::ZlsLoad), Ok(PteEnd { written: true, fault: None }));
    }

    #[test]
    fn writeonly_alone_faults_a_read_and_edmprotect_lets_it_through_as_the_r18_flag_rows() {
        // E1071 (r18-flag stage f2, frozen, held out): on the ZLS load of the depth buffer and the
        // probe's texture read of its scratch, each mapping only read
        use PteAccess::*;
        let clean = Ok(PteEnd { written: true, fault: None });
        let first = |int_stat| {
            Ok(PteEnd { written: false, fault: Some(PteFault { int_stat, page: FaultPage::First, sb: 0 }) })
        };
        assert_eq!(pte_access(0x10, ZlsLoad), clean, "q108-edm-load");
        assert_eq!(pte_access(0x10, TextureRead), clean, "q108-edm-tex");
        assert_eq!(pte_access(0x2, ZlsLoad), first(0x80200), "q108-wo-load");
        assert_eq!(pte_access(0x2, TextureRead), first(0x80002), "q108-wo-tex");
    }

    #[test]
    fn both_flags_fault_a_read_as_writeonly_alone_as_the_r29_flag_rows() {
        // E1108 (r29-flag stage f1, frozen, held out): WRITEONLY with EDMPROTECT (0x12) on the
        // same two reads faults as WRITEONLY alone, not with EDMPROTECT's type as on a write
        use PteAccess::*;
        let first = |int_stat| {
            Ok(PteEnd { written: false, fault: Some(PteFault { int_stat, page: FaultPage::First, sb: 0 }) })
        };
        assert_eq!(pte_access(0x12, ZlsLoad), first(0x80200), "q108-both-load");
        assert_eq!(pte_access(0x12, TextureRead), first(0x80002), "q108-both-tex");
        assert!(pte_access(0x12, ZlsStore).is_err());
    }

    #[test]
    fn pte_flags_no_row_ran_are_refused() {
        use PteAccess::*;
        let refused = |p, a| matches!(pte_access(p, a), Err(Outcome::Unsupported { .. }));
        assert!(refused(0x8, PixelWrite), "CACHED on a write: not run");
        assert!(refused(0x12, StreamRead), "two knob flags together on a read: not run");
        assert!(refused(0x1a, PixelWrite), "three flags together: not run");
        assert!(refused(0x8, ZlsStore), "CACHED on the ZLS store: not run");
        assert!(
            refused(0x12, ZlsStore),
            "WO and EDMPROT together on the ZLS store: not run (E1108 ran the load)"
        );
        assert!(refused(0x4, StreamRead), "READONLY on a read: not in these rows");
        assert!(refused(0x1, PixelWrite), "VALID is no flag");
    }
}
