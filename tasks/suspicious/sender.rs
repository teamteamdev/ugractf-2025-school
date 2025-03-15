#!/usr/bin/env -S cargo +nightly -Zscript
---cargo
[package]
edition = "2024"
[dependencies]
tokio = { version = "1.43.0", features = ["io-std", "io-util", "macros", "net", "rt", "rt-multi-thread", "time"] }
---

use core::time::Duration;
use std::io::Result;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpStream;

#[tokio::main]
async fn main() -> Result<()> {
    let addr = std::env::var("ADDRESS").expect("no addr?");
    let mut conn = TcpStream::connect(addr).await?;
    conn.set_nodelay(true)?;
    let (_conn_rx, mut conn) = conn.split();
    let mut stdin = tokio::io::stdin();

    let mut buf = [0u8; 128];
    let mut count;
    while {
        count = stdin.read(&mut buf).await?;
        count != 0
    } {
        conn.write_all(&buf[..count]).await?;
        tokio::time::sleep(Duration::from_secs(2)).await;
    }

    Ok(())
}
