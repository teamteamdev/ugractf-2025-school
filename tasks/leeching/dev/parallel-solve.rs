#!/usr/bin/env -S cargo +nightly -Zscript
---cargo
[package]
edition = "2024"

[dependencies]
itertools = "0.14"
rayon = "1.10"
serde = "1"
serde_bencode = "0.2"
serde_bytes = "0.11"
serde_derive = "1"
sha1 = { version = "0.10", features = ["asm"] }

[profile.dev]
opt-level = 3
---

#![feature(slice_as_chunks)]

use itertools::Itertools;
use rayon::prelude::*;
use serde_derive::Deserialize;
use sha1::{Digest as _, Sha1};
use std::collections::HashMap;
use std::sync::Mutex;
use std::time::Instant;

#[derive(Deserialize)]
struct Info {
    pieces: serde_bytes::ByteBuf,
    #[serde(rename = "piece length")]
    piece_length: i64,
    length: i64,
}

#[derive(Deserialize)]
struct Torrent {
    info: Info,
}

#[derive(Clone)]
struct SyncPointer<T>(*mut T);
// SAFETY: convenient tho
unsafe impl<T> Sync for SyncPointer<T> {}

fn main() {
    let filename = std::env::var("SOLVE").expect("SOLVE=path/to/file.torrent ./parallel-solve.rs");
    let contents = std::fs::read(&filename).expect("read");
    let Torrent {
        info: Info {
            length,
            piece_length,
            pieces,
        },
    } = serde_bencode::de::from_bytes(&contents).expect("torrent");

    let length: usize = length.try_into().expect("length is long?");
    let piece_length: usize = piece_length.try_into().expect("piece_length is long?");
    let (pieces, last) = pieces.as_chunks::<20>();
    assert!(last.is_empty(), "pieces are of uneven sizes?");

    let mut hash_positions = HashMap::<[u8; 20], Mutex<Vec<usize>>>::new();
    for (index, piece) in pieces.iter().enumerate() {
        hash_positions
            .entry(*piece)
            .or_default()
            .get_mut()
            .unwrap()
            .push(index);
    }

    let mut text = vec![b'_'; length as usize];
    let text_ptr_sync = SyncPointer(text.as_mut_ptr());

    let start = Instant::now();

    for partial_length in [length % piece_length, piece_length] {
        (0..=255u8).into_par_iter().for_each(|first_byte| {
            let SyncPointer(text_ptr) = text_ptr_sync.clone();

            for value in (0..partial_length)
                .map(|i| {
                    if i == 0 {
                        first_byte..=first_byte
                    } else {
                        0..=255u8
                    }
                })
                .multi_cartesian_product()
                .take_while(|_| !hash_positions.is_empty())
            {
                let hash: [u8; 20] = Sha1::digest(&value).into();
                if hash_positions.contains_key(&hash) {
                    for index in hash_positions.get(&hash).unwrap().lock().unwrap().drain(..) {
                        let begin = index * piece_length;

                        // SAFETY: begin is in bounds
                        let base = unsafe { text_ptr.add(begin) };

                        // SAFETY:
                        // - nonoverlapping `text` and `value`
                        // - only the first to encounter hash "claims" all its hash_positions.get(&hash)
                        // - indices are unique: no index has two hashes attached to it; therefore
                        //   they are written to only once and data races dont happen
                        unsafe {
                            base.copy_from_nonoverlapping(value.as_ptr(), partial_length);
                        }
                    }
                }
            }
        });
    }

    let newname = filename + ".cracked";
    std::fs::write(&newname, &text).expect("save");

    eprintln!("Check {newname} for raw data. Took {:?}", start.elapsed());

    println!("{}", String::from_utf8_lossy(&text));
}
