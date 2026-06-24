import logging
import shlex
import shutil
import subprocess
import sys

log = logging.getLogger("dsx-daemon")


class DualSenseCtl:
    """Wrapper around the ``dualsensectl`` binary."""

    def __init__(self, serial: str | None = None, dry_run: bool = False) -> None:
        self._serial = serial
        self._dry_run = dry_run
        self._binary = self._resolve_binary()
        self._device_args = ["-d", serial] if serial else []

    @staticmethod
    def _resolve_binary() -> str:
        path = shutil.which("dualsensectl")
        if path:
            return path
        log.error("dualsensectl not found in PATH")
        sys.exit(1)

    def run(self, args: list[str]) -> None:
        cmd = [self._binary, *self._device_args, *args]
        log.debug("Running: %s", shlex.join(cmd))
        if self._dry_run:
            log.info("[DRY-RUN] %s", shlex.join(cmd))
            return
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            log.warning(
                "dualsensectl failed (exit %d): %s", e.returncode, e.stderr.strip()
            )
        except FileNotFoundError:
            log.error("dualsensectl not found at %s", self._binary)
            sys.exit(1)

    def execute_commands(self, commands: list[list[str]]) -> None:
        for cmd in commands:
            if cmd:
                self.run(cmd)

    def reset(self) -> None:
        self.execute_commands(
            [
                ["trigger", "left", "off"],
                ["trigger", "right", "off"],
                ["lightbar", "0", "0", "0", "0"],
                ["player-leds", "0"],
                ["microphone-led", "off"],
            ]
        )
