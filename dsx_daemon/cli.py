"""Command-line interface for the dsx-daemon.

Handles argument parsing and wires together the controller, server,
and logging configuration.
"""

from __future__ import annotations

import argparse
import logging
import sys

from dsx_daemon.dualsense import DualSenseCtl
from dsx_daemon.server import run_server

log = logging.getLogger("dsx-daemon")

DEFAULT_BIND = "127.0.0.1"
DEFAULT_PORT = 6969


def build_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="DSX protocol to DualSense daemon for Linux",
    )
    parser.add_argument(
        "-b", "--bind", default=DEFAULT_BIND,
        help=f"Bind address (default: {DEFAULT_BIND})",
    )
    parser.add_argument(
        "-p", "--port", type=int, default=DEFAULT_PORT,
        help=f"UDP port (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "-d", "--device", metavar="SERIAL",
        help="DualSense serial number (format: 00:00:00:00:00:00)",
    )
    parser.add_argument(
        "-n", "--dry-run", action="store_true",
        help="Log commands without executing",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Verbose logging",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    """Parse arguments, configure logging, and run the server.

    :param argv: Command-line arguments (defaults to sys.argv[1:]).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    log.info("dsx-daemon starting (bind=%s:%d, dry_run=%s)",
             args.bind, args.port, args.dry_run)

    dsctl = DualSenseCtl(serial=args.device, dry_run=args.dry_run)
    run_server(args.bind, args.port, dsctl)


if __name__ == "__main__":
    main()
