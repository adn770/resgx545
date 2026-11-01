// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! A small gzip reader (RFC 1951/1952), so the crate stays dependency-free: the dumps in the
//! data repository are `.gz`.

/// Decompress a gzip file image.
pub fn gunzip(data: &[u8]) -> Result<Vec<u8>, String> {
    if data.len() < 18 || data[0] != 0x1f || data[1] != 0x8b || data[2] != 8 {
        return Err("not a gzip file".into());
    }
    let flg = data[3];
    let mut at = 10;
    if flg & 4 != 0 {
        let n = *data.get(at).ok_or("short")? as usize | (*data.get(at + 1).ok_or("short")? as usize) << 8;
        at += 2 + n;
    }
    for bit in [8, 16] {
        if flg & bit != 0 {
            while *data.get(at).ok_or("short header")? != 0 {
                at += 1;
            }
            at += 1;
        }
    }
    if flg & 2 != 0 {
        at += 2;
    }
    if at + 8 > data.len() {
        return Err("short header".into());
    }
    let body = &data[at..data.len() - 8];
    let out = inflate(body)?;
    let t = &data[data.len() - 8..];
    let crc = u32::from_le_bytes([t[0], t[1], t[2], t[3]]);
    let isize = u32::from_le_bytes([t[4], t[5], t[6], t[7]]);
    if isize != out.len() as u32 || crc != crc32(&out) {
        return Err("gzip trailer (crc or size) differs".into());
    }
    Ok(out)
}

fn crc32(d: &[u8]) -> u32 {
    let mut t = [0u32; 256];
    for (i, e) in t.iter_mut().enumerate() {
        let mut c = i as u32;
        for _ in 0..8 {
            c = if c & 1 != 0 { 0xedb88320 ^ (c >> 1) } else { c >> 1 };
        }
        *e = c;
    }
    !d.iter().fold(!0u32, |c, &b| t[((c ^ b as u32) & 0xff) as usize] ^ (c >> 8))
}

struct Bits<'a> {
    d: &'a [u8],
    pos: usize,
    acc: u32,
    n: u32,
}

impl Bits<'_> {
    fn bits(&mut self, k: u32) -> Result<u32, String> {
        while self.n < k {
            let b = *self.d.get(self.pos).ok_or("deflate stream ends early")?;
            self.pos += 1;
            self.acc |= (b as u32) << self.n;
            self.n += 8;
        }
        let v = if k == 0 { 0 } else { self.acc & ((1u32 << k) - 1) };
        self.acc = if k >= 32 { 0 } else { self.acc >> k };
        self.n -= k;
        Ok(v)
    }
}

/// Canonical Huffman code: counts per length and the symbols in code order.
struct Huff {
    count: [u16; 16],
    symbol: Vec<u16>,
}

impl Huff {
    fn new(lengths: &[u8]) -> Huff {
        let mut count = [0u16; 16];
        for &l in lengths {
            count[l as usize] += 1;
        }
        count[0] = 0;
        let mut offs = [0u16; 16];
        for i in 1..16 {
            offs[i] = offs[i - 1] + count[i - 1];
        }
        let mut symbol = vec![0u16; lengths.len()];
        for (s, &l) in lengths.iter().enumerate() {
            if l != 0 {
                symbol[offs[l as usize] as usize] = s as u16;
                offs[l as usize] += 1;
            }
        }
        Huff { count, symbol }
    }

    fn decode(&self, b: &mut Bits) -> Result<u16, String> {
        let (mut code, mut first, mut index) = (0i32, 0i32, 0i32);
        for len in 1..16 {
            code |= b.bits(1)? as i32;
            let c = self.count[len] as i32;
            if code - c < first {
                return Ok(self.symbol[(index + (code - first)) as usize]);
            }
            index += c;
            first += c;
            first <<= 1;
            code <<= 1;
        }
        Err("bad huffman code".into())
    }
}

const LBASE: [u16; 29] = [
    3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31, 35, 43, 51, 59, 67, 83, 99, 115, 131, 163, 195,
    227, 258,
];
const LEXT: [u8; 29] =
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 0];
const DBASE: [u16; 30] = [
    1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129, 193, 257, 385, 513, 769, 1025, 1537, 2049, 3073,
    4097, 6145, 8193, 12289, 16385, 24577,
];
const DEXT: [u8; 30] =
    [0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13];

fn inflate(d: &[u8]) -> Result<Vec<u8>, String> {
    let mut b = Bits { d, pos: 0, acc: 0, n: 0 };
    let mut out: Vec<u8> = Vec::new();
    loop {
        let last = b.bits(1)?;
        match b.bits(2)? {
            0 => {
                b.acc = 0;
                b.n = 0;
                let p = b.pos;
                if p + 4 > d.len() {
                    return Err("stored block ends early".into());
                }
                let len = u16::from_le_bytes([d[p], d[p + 1]]) as usize;
                if p + 4 + len > d.len() {
                    return Err("stored block ends early".into());
                }
                out.extend_from_slice(&d[p + 4..p + 4 + len]);
                b.pos = p + 4 + len;
            }
            t @ (1 | 2) => {
                let (lit, dist) = if t == 1 {
                    let mut l = [8u8; 288];
                    l[144..256].fill(9);
                    l[256..280].fill(7);
                    (Huff::new(&l), Huff::new(&[5u8; 30]))
                } else {
                    let nlen = b.bits(5)? as usize + 257;
                    let ndist = b.bits(5)? as usize + 1;
                    let ncode = b.bits(4)? as usize + 4;
                    const ORDER: [usize; 19] =
                        [16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15];
                    let mut cl = [0u8; 19];
                    for &o in ORDER.iter().take(ncode) {
                        cl[o] = b.bits(3)? as u8;
                    }
                    let ch = Huff::new(&cl);
                    let mut lens = vec![0u8; nlen + ndist];
                    let mut i = 0;
                    while i < nlen + ndist {
                        let s = ch.decode(&mut b)?;
                        let (v, rep) = match s {
                            0..=15 => (s as u8, 1),
                            16 => {
                                if i == 0 {
                                    return Err("repeat with no length".into());
                                }
                                (lens[i - 1], 3 + b.bits(2)? as usize)
                            }
                            17 => (0, 3 + b.bits(3)? as usize),
                            _ => (0, 11 + b.bits(7)? as usize),
                        };
                        if i + rep > nlen + ndist {
                            return Err("too many code lengths".into());
                        }
                        lens[i..i + rep].fill(v);
                        i += rep;
                    }
                    (Huff::new(&lens[..nlen]), Huff::new(&lens[nlen..]))
                };
                loop {
                    let s = lit.decode(&mut b)? as usize;
                    if s < 256 {
                        out.push(s as u8);
                    } else if s == 256 {
                        break;
                    } else {
                        let s = s - 257;
                        if s >= 29 {
                            return Err("bad length symbol".into());
                        }
                        let len = LBASE[s] as usize + b.bits(LEXT[s] as u32)? as usize;
                        let ds = dist.decode(&mut b)? as usize;
                        if ds >= 30 {
                            return Err("bad distance symbol".into());
                        }
                        let dd = DBASE[ds] as usize + b.bits(DEXT[ds] as u32)? as usize;
                        if dd > out.len() {
                            return Err("distance too far back".into());
                        }
                        for _ in 0..len {
                            out.push(out[out.len() - dd]);
                        }
                    }
                }
            }
            _ => return Err("bad block type".into()),
        }
        if last == 1 {
            return Ok(out);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::sha256::hex_digest;

    fn unhex(s: &str) -> Vec<u8> {
        (0..s.len() / 2).map(|i| u8::from_str_radix(&s[2 * i..2 * i + 2], 16).unwrap()).collect()
    }

    #[test]
    fn a_fixed_huffman_block() {
        let g = unhex("1f8b0800000000000203cb48cdc9c957c84027b9000088590b18000000");
        assert_eq!(gunzip(&g).unwrap(), b"hello hello hello hello\n");
    }

    #[test]
    fn a_dynamic_huffman_block() {
        let g = unhex(&[
        "1f8b08000000000002ff5d5551aedc200cbc4a8e009810384e56fbf45a699f5ab52b55eae90b9e1942fa1304187b3c1e",
        "3b8f8ff76965fbfbfa9db7cff3ebeb3cb6e7c7eb7da6ca358fbb68dbf9faf9edb488b59ffaadd5711bb6e79f1fbf9efd",
        "897b88797b7f7f7d14eef022c2c6f2e560ecbb637714fd49f4600a6dfbf6e8e852f285774d5e65e26e8a9b6402899541",
        "1434d13a792e892eaac7ec29f5c36972781482a2f7b4731ff15251135919801907b906f7dc9fc19c308899e1ad213cf9",
        "ee6f460a86640381ba0569d8e1d47330922b3a0c9761cdb3de5e1f2ca07beec097bb99bb3391b84b4cc650cd0e77c46d",
        "33aed7cb61aa9451090da7bb9bfb371678ca5309c33f52847114baa68a7b948ccbc01c4db62a32702ae920f7404839a7",
        "b2d69cb49165ab129f3bc6a6cd1a8a4bd4fa9042516ae9369308187bb0441966b9206024a7568a4dac408d8d5661baf2",
        "734a194c421011d54bf0471d49b233d1071afb069e463acd930dd220618e50bb1acd41272606edb9ba40ef712b0af2cf",
        "ab523529504cd2476d55159869c1257594a81d1d723a0115e4e5d3c700d18e75ea30a5ac9a5e880fa91448c16e5171c7",
        "c2cc13f1f0527d4aa9025d9dbaf5b428c15464e3e901ebd5e79a19bc1c4b5987ad65fa764c2c9685b5b0698a1d8b0690",
        "aaf25f6f68e8060907af8a0434839a46b96664bc95262223cdbdc9459d34e2352a325b70fa029f570d9911e78b2f7445",
        "5e30607665a159e77f2bf4189b284c2296118661c76c4d12d64e436bc46962958834ce213236220cd16c5737b465d071",
        "42b59be4d5febb869a7e96c3c7a122bbdbba760c6b47326351938e67d42be9c758a8fcd21ad355b344ff2fe8db61493b",
        "389436ea35bb1c75163362d4b7e5f6db992359d5f80767d1ef4655080000",
        ].concat());
        let t = gunzip(&g).unwrap();
        assert_eq!(t.len(), 2133);
        assert_eq!(hex_digest(&t), "f53639193c63109274c32b734429a5d9cce72bedf62c62aebf9f0a7939e620ea");
    }

    #[test]
    fn a_bad_stream_is_an_error_not_a_panic() {
        assert!(gunzip(b"not gzip").is_err());
        let g = unhex("1f8b0800000000000203cb48cdc9c957c84027b9000088590b18000000");
        assert!(gunzip(&g[..g.len() - 12]).is_err());
        let mut bad = g.clone();
        let n = bad.len();
        bad[n - 8] ^= 1; // the crc
        assert!(gunzip(&bad).is_err());
    }
}
