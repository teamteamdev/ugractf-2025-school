import base64
import re
import os

if "SOLVE" in os.environ:
    import sys

    def normalize(s):
        data = re.sub(rb'[^0-9a-zA-Z+/=]', b'A', s)
        data = re.sub(rb'^(A+)=', rb'\1A', data)
        padding = b'A' * ((-len(data)) % 4)
        return padding + data

    s = sys.stdin.read().encode()
    ps = ''
    while ps != s:
        ps, s = s, base64.b64decode(normalize(s))
        print(len(s), s[:64])
    raise SystemExit(0)


import random
from scapy.layers.inet import IP, TCP
from scapy.layers.l2 import Ether
from scapy.packet import Raw
import scapy.utils


from kyzylborda_lib.generator import get_attachments_dir
from kyzylborda_lib.secrets import get_flag, get_secret

def encode_flag(flag: str) -> list[bytes]:
    flag = flag.encode()
    for _ in range(23):
        flag = base64.b64encode(flag)
    return flag


def chunks(it, count) -> list[list]:
    return [
        it[i:i+count]
        for i
        in range(0, len(it), count)
    ]

def generate():
    random.seed(get_secret('random_seed'))
    flag = encode_flag(get_flag())
    transmission = chunks(flag, 128)[1:]

    def craft_tcp_packet(packet: TCP) -> TCP:
        nonlocal transmission
        current_chunk, transmission = transmission[0], transmission[1:]

        return TCP(
            sport = packet.sport,
            dport = packet.dport,
            seq = packet.seq,
            ack = packet.ack,
            dataofs = packet.dataofs,
            reserved = packet.reserved,
            flags = packet.flags,
            window = packet.window,
            # recalculate checksum
            urgptr = packet.urgptr,
            options = packet.options,
        ) / Raw(current_chunk)


    def map_ip_packet(packet: IP) -> IP:
        assert packet.version == 4

        return IP(
            version = 4,
            ihl = packet.ihl,
            tos = packet.tos,
            len = packet.len,
            id = packet.id,
            flags = packet.flags,
            frag = packet.frag,
            ttl = packet.ttl,
            proto = packet.proto,
            # recalculate checksum
            src = packet.src,
            dst = packet.dst,
        ) / (
            craft_tcp_packet(packet.payload)
            if (
                packet.proto == 6
                and packet.payload.dport == 6666
                and len(packet.payload.payload) != 0  # Skip FIN packets
            )
            else packet.payload
        )


    def map_ether_packet(packet: Ether) -> Ether:
        assert isinstance(packet.payload, IP)
        return Ether(
            dst = packet.dst,
            src = packet.src,
        ) / map_ip_packet(packet.payload)


    def map_packet(packet, trm):
        next_packet = map_ether_packet(packet)
        next_packet.time = packet.time
        return next_packet

    scapy.utils.wrpcap(get_attachments_dir() + '/suspicious.pcapng', (
        map_packet(packet, transmission)
        for packet
        in scapy.utils.rdpcap('template.pcapng')
    ))
