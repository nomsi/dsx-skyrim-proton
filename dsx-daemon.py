#!/usr/bin/env python3
"""
dsx-daemon.py — Linux DSX protocol receiver for DualSense controllers.

Listens on UDP port 6969 for JSON packets from DSXSkyrim-NG (running
inside Skyrim under Proton/Wine) and translates them to dualsensectl
commands for the physical DualSense controller.

Usage:
  ./dsx-daemon.py                    # bind to 127.0.0.1:6969
  ./dsx-daemon.py -d 00:A0:B0:C0:D0 # use a specific controller by serial
  ./dsx-daemon.py -v                 # verbose logging
"""

from dsx_daemon.cli import main

if __name__ == "__main__":
    main()
