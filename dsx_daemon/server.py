"""UDP server that receives DSX protocol packets and dispatches them.

Listens for JSON-encoded DSX packets on a configurable address/port
and forwards them through the translator and controller pipeline.
"""

import json
import logging
import socket
import sys

from dsx_daemon.dualsense import DualSenseCtl
from dsx_daemon.packet import Packet
from dsx_daemon.translator import translate_packet

log = logging.getLogger("dsx-daemon")


def run_server(bind: str, port: int, dsctl: DualSenseCtl) -> None:
    """Start the UDP receive loop.

    :param bind: IP address to bind to (e.g. ``"127.0.0.1"``).
    :param port: UDP port number.
    :param dsctl: Initialised DualSenseCtl instance.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((bind, port))
    except PermissionError:
        log.error(
            "Cannot bind to %s:%d — try a port ≥1024 or run as root", bind, port
        )
        sys.exit(1)
    except OSError as e:
        log.error("Bind failed: %s", e)
        sys.exit(1)

    log.info("Listening on %s:%d", bind, port)

    while True:
        try:
            data, addr = sock.recvfrom(4096)
        except KeyboardInterrupt:
            log.info("Shutting down")
            dsctl.reset()
            break

        log.debug("Received %d bytes from %s", len(data), addr)

        try:
            raw = json.loads(data.decode("utf-8", errors="replace"))
        except json.JSONDecodeError as e:
            log.warning("Invalid JSON from %s: %s", addr, e)
            continue

        pkt = Packet.from_json(raw)
        if not pkt.instructions:
            log.debug("Empty packet from %s", addr)
            continue

        commands = translate_packet(pkt)
        if commands:
            dsctl.execute_commands(commands)
