### Mirrored from my personal [forgejo instance](https://git.nomsy.space/emi/dsxskyrim). I just wanted to push on GitHub for those who use github

# Skyrim Linux DualSense Haptics

Linux-native DualSense haptic feedback for Skyrim Anniversary Edition
running under Proton.  Replaces the Windows-only DSX (DualSenseX) with
a Python daemon that translates UDP packets from
[DSXSkyrim-NG](https://github.com/dvize/DSXSkyrim-NG) into
[dualsensectl](https://github.com/nowrep/dualsensectl) commands.

## How it works

```
Skyrim AE (Proton/Wine)
  └─ SKSE → DSXSkyrimNG.dll
       └─ UDP JSON → 127.0.0.1:6969
                        │
                    [ Linux host ]
                        │
              dsx-daemon.py
                    │
              dualsensectl
                    │
              DualSense controller (USB/BT)
```

The SKSE plugin sends JSON packets over UDP when you equip items.
On Windows, DSX handles them.  On Linux, `dsx-daemon.py` listens on
port 6969 and runs `dualsensectl` instead.

## Project structure

```
dsx-daemon.py          # entry point
dsx-daemon.toml        # config
dsx_daemon/
  packet.py            # protocol types
  dualsense.py         # dualsensectl wrapper
  translator.py        # DSX mode -> dualsensectl mapping
  server.py            # UDP receive loop
  cli.py               # arg parsing + main
```

## Requirements

- Skyrim Anniversary Edition (or SE) under Proton/Wine
- SKSE64 + Address Library
- DSXSkyrim-NG (install with your mod manager)
- [dualsensectl](https://github.com/nowrep/dualsensectl) installed on PATH (see below)
- Python 3.10+
- DualSense controller (USB or Bluetooth)

## Install

### [dualsensectl](https://github.com/nowrep/dualsensectl)

```bash
git clone https://github.com/nowrep/dualsensectl.git
cd dualsensectl
meson setup build && ninja -C build && sudo ninja -C build install
dualsensectl battery          # verify
```

### [DSXSkyrim-NG](https://www.nexusmods.com/skyrimspecialedition/mods/66165)

Use your mod manager to install `DSXSkyrimNG.7z` like any other SKSE
plugin.  The relevant files end up in
`Data/SKSE/Plugins/DSXSkyrim/`. Make sure to endorse them!

### Run

```bash
python3 dsx-daemon.py                        # default 127.0.0.1:6969
python3 dsx-daemon.py -v                     # verbose
python3 -m dsx_daemon                        # same thing
python3 dsx-daemon.py -d 00:A0:B0:C0:D0      # specific controller
```

Start the daemon before launching the game.  Hit Ctrl+C (or send
SIGTERM) to stop — it resets the controller triggers and LEDs
automatically.

Edit `dsx-daemon.toml` to change defaults (CLI flags override the
file).

## Trigger mode mapping

| DSX | Name | dualsensectl |
|-----|------|--------------|
| 0 | Off | `trigger off` |
| 1 | GameCube | `feedback 2 3` |
| 2 | VerySoft | `feedback 0 2` |
| 3 | Soft | `feedback 0 3` |
| 4 | Hard | `feedback 0 5` |
| 5 | VeryHard | `feedback 0 7` |
| 6 | Hardest | `feedback 0 8` |
| 7 | Rigid | `feedback 0 8` |
| 8 | VibrateTrigger | `vibration 0 4 4` |
| 9 | Choppy | `vibration 0 8 8` |
| 10 | Medium | `feedback 0 5` |
| 11 | VibrateTriggerPulse | `vibration 0 8 4` |
| 12 | CustomTriggerValue | varies |
| 13 | Resistance | `feedback pos str` |
| 14 | Bow | `bow start stop str snap` |
| 15 | Galloping | `galloping start stop f1 f2 freq` |
| 16 | SemiAutomaticGun | `weapon start stop str` |
| 17 | AutomaticGun | `weapon start stop str` |
| 18 | Machine | `machine start stop sa sb freq per` |

## Tuning

Copy `DSXSkyrimConfig.example.json` from this repo into the DSXSkyrim
plugin folder as `DSXSkyrimConfig.json` and tweak the trigger modes
to your liking.  The full fields reference is in the
[DSXSkyrim-NG config docs](https://github.com/dvize/DSXSkyrim-NG/blob/master/DSXSkyrimConfigDocumentation.html).


#### Thanks! with <3, emi