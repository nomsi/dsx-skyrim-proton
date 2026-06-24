"""Wrapper around the ``dualsensectl`` binary.

Dispatches commands to the physical DualSense controller
through the system-installed ``dualsensectl`` tool.
"""

import logging
import shlex
import shutil
import subprocess
import sys

log = logging.getLogger("dsx-daemon")


class DualSenseCtl:
    """Manages a DualSense controller via the ``dualsensectl`` binary.

    :param serial: Optional device serial number for ``-d``.
    :param dry_run: If true, log commands without executing them.
    """

    def __init__(self, serial: str | None = None, dry_run: bool = False) -> None:
        self._serial = serial
        self._dry_run = dry_run
        self._binary = self._resolve_binary()
        self._device_args = ["-d", serial] if serial else []

    @staticmethod
    def _resolve_binary() -> str:
        """Locate ``dualsensectl`` on ``PATH``.

        :return: Absolute path to the binary.
        :raises SystemExit: If the binary is not found.
        """
        path = shutil.which("dualsensectl")
        if path:
            return path
        log.error("dualsensectl not found in PATH")
        sys.exit(1)

    def run(self, args: list[str]) -> None:
        """Execute a ``dualsensectl`` subcommand.

        :param args: Arguments to pass after device flags.
        """
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
        """Run multiple command lists in sequence.

        :param commands: A list of argument lists, one per invocation.
        """
        for cmd in commands:
            if cmd:
                self.run(cmd)

    def reset(self) -> None:
        """Reset the controller to a neutral state: no trigger effects, dark LEDs."""
        self.execute_commands(
            [
                ["trigger", "left", "off"],
                ["trigger", "right", "off"],
                ["lightbar", "0", "0", "0", "0"],
                ["player-leds", "0"],
            ]
        )
