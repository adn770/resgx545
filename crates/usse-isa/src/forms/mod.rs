// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The instruction families, one module each (tools/usse-dis/forms/README.md):
//! their operand kinds, fields and table entries. Like the rest of the table,
//! their layouts are held by the random cross-checks with the C decoder.

pub(crate) mod float;
pub(crate) mod intpack;
pub(crate) mod memctl;
pub(crate) mod misc;
