import json
import logging
import signal
import socket
import sys

from dsx_daemon.dualsense import DualSenseCtl
from dsx_daemon.packet import Packet
from dsx_daemon.translator import translate_packet

log = logging.getLogger("dsx-daemon")

_SHUTDOWN = False


def _handle_signal(sig: int, _frame) -> None:
    global _SHUTDOWN
    _SHUTDOWN = True


def run_server(bind: str, port: int, dsctl: DualSenseCtl) -> None:
    """UDP receive loop — receives JSON packets and dispatches to DualSenseCtl."""
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(1.0)
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

    while not _SHUTDOWN:
        try:
            data, addr = sock.recvfrom(4096)
        except socket.timeout:
            continue
        except OSError:
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

    log.info("Shutting down")
    dsctl.reset()
