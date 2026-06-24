import argparse
import logging
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]

from dsx_daemon.dualsense import DualSenseCtl
from dsx_daemon.server import run_server

log = logging.getLogger("dsx-daemon")

CONFIG_PATH = Path("dsx-daemon.toml")


def _load_config(path: Path) -> dict[str, Any]:
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        log.warning("failed to load %s: %s", path, e)
        return {}


def _apply_config(parser: argparse.ArgumentParser) -> None:
    cfg = _load_config(CONFIG_PATH).get("daemon", {})
    overrides = {}
    if "bind" in cfg:
        overrides["bind"] = cfg["bind"]
    if "port" in cfg:
        overrides["port"] = cfg["port"]
    if "device" in cfg and cfg["device"]:
        overrides["device"] = cfg["device"]
    if "dry_run" in cfg:
        overrides["dry_run"] = cfg["dry_run"]
    if overrides:
        parser.set_defaults(**overrides)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="DSX protocol to DualSense daemon for Linux",
    )
    parser.add_argument("-b", "--bind", default="127.0.0.1", help="Bind address")
    parser.add_argument("-p", "--port", type=int, default=6969, help="UDP port")
    parser.add_argument("-d", "--device", metavar="SERIAL",
                        help="DualSense serial (format: 00:00:00:00:00:00)")
    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="Log commands without executing")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose logging")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    _apply_config(parser)
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    log.info("starting (bind=%s:%d, dry_run=%s)", args.bind, args.port, args.dry_run)
    dsctl = DualSenseCtl(serial=args.device, dry_run=args.dry_run)
    run_server(args.bind, args.port, dsctl)


if __name__ == "__main__":
    main()
