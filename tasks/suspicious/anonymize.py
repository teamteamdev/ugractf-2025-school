import random
import os
from scapy.layers.inet import IP, ICMP, IPerror, TCP, UDP
from scapy.layers.l2 import Ether
from scapy.packet import Raw
import scapy.utils


MAC_SRC = "4a:7a:8f:55:18:d3"
MAC_DST = "41:a7:b3:ee:00:01"
SERVER_ADDR = "135.181.93.68"  # incubator.net.ttc.tf
LOCAL_IP = os.env["LOCAL_IP"]  # 192.168.1.xxx
LOCAL_IP_MAPPING = {
    0: 0,  # https://en.wikipedia.org/wiki/IPv4#First_and_last_subnet_addresses
    1: 1,  # Gateway
    255: 255,  # Broadcast
}


def map_ip(ip: str) -> str:
    global LOCAL_IP_MAPPING
    if not ip.startswith('192.168.1.'):
        return ip
    # LAN: randomize IPs
    current = int(ip.split('.')[3])
    if current not in LOCAL_IP_MAPPING:
        LOCAL_IP_MAPPING[current] = random.randint(34, 210)
    return f'192.168.1.{LOCAL_IP_MAPPING[current]}'


def map_tcp_packet(packet: TCP, error: bool, correct_stream: bool) -> TCP:
    if correct_stream:
        # TODO: Replace body with flag parts
        pass
    return packet


def map_icmp_packet(packet: ICMP) -> ICMP:
    assert packet.extpad == b'', repr(packet)
    return ICMP(
        type = packet.type,
        code = packet.code,
        reserved = packet.reserved,
        length = packet.length,
        nexthopmtu = packet.nexthopmtu,
        unused = packet.unused,
        extpad = packet.extpad,
    ) / map_ip_packet(packet, error=True)


def map_ip_packet(packet: IP, /, error: bool = False) -> IP:
    assert packet.version == 4
    assert packet.proto in [1, 6, 17]  # ICMP, TCP, UDP

    is_icmp = packet.proto == 1
    is_tcp = packet.proto == 6
    correct_stream = packet.proto == 6 and 6666 in (packet.payload.sport, packet.payload.dport)
    source_is_incorrect = packet.src == "192.168.1.1" and packet.dst == LOCAL_IP and correct_stream 
    destination_is_incorrect = packet.src == LOCAL_IP and packet.dst == "192.168.1.1" and correct_stream

    return (IP if not error else IPerror)(
        version = 4,
        ihl = packet.ihl,
        tos = packet.tos,
        len = packet.len,
        id = packet.id,
        flags = packet.flags,
        frag = packet.frag,
        ttl = packet.ttl - 15 if source_is_incorrect else packet.ttl,
        proto = packet.proto,
        # recalculate checksum
        src = SERVER_ADDR if source_is_incorrect else map_ip(packet.src),
        dst = SERVER_ADDR if destination_is_incorrect else map_ip(packet.dst),
    ) / (
        map_icmp_packet(packet.payload) if is_icmp else
        map_tcp_packet(packet.payload, error, correct_stream) if is_tcp else
        packet.payload
    )


def map_ether_packet(packet: Ether) -> Ether:
    assert isinstance(packet.payload, IP)
    return Ether(dst=MAC_DST, src=MAC_SRC) / map_ip_packet(packet.payload)


def map_packet(packet):
    next_packet = map_ether_packet(packet)
    next_packet.time = packet.time
    return next_packet


scapy.utils.wrpcap(os.environ["OUTPUT"], (
    map_packet(packet)
    for packet
    in scapy.utils.rdpcap(os.environ["INPUT"])
))
print(LOCAL_IP_MAPPING)
