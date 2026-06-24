# Skyrim Linux DualSense Haptics

**Linux-native DualSense haptic feedback for Skyrim Anniversary Edition (Proton).**

Replaces the closed-source Windows app **DSX (DualSenseX)** with a lightweight Python daemon that translates UDP packets from [DSXSkyrim-NG](https://github.com/dvize/DSXSkyrim-NG) (running inside the game under Proton) into [`dualsensectl`](https://github.com/nowrep/dualsensectl) commands.

## How it works

```
Skyrim AE (Proton/Wine)
  └─ SKSE → DSXSkyrimNG.dll
       └─ UDP JSON → 127.0.0.1:6969
                        │
                    [ Linux host ]
                        │
              dsx-daemon.py (this project)
                    │
              dualsensectl
                    │
              DualSense controller (USB/BT)
```

The SKSE plugin detects item equips in Skyrim and sends JSON packets describing the desired trigger effects over UDP. On Windows, DSX receives these and talks to the controller. On Linux, `dsx-daemon.py` receives them and runs `dualsensectl` instead.

## Requirements

- **Skyrim Anniversary Edition** (or SE) running under **Proton** (or Wine)
- **SKSE64** + Address Library for your Skyrim version
- **DSXSkyrim-NG.7z** — get it from the [DSXSkyrim-NG releases](https://github.com/dvize/DSXSkyrim-NG/releases) (or build from source)
- **dualsensectl** — install from your distro or build from [source](https://github.com/nowrep/dualsensectl)
- **Python 3.10+** (or any recent Python 3)
- **DualSense controller** (PS5) — connected via USB or Bluetooth

## Installation

### 1. Install dualsensectl

On Gentoo you likely already have it. Otherwise:

```bash
# From source:
git clone https://github.com/nowrep/dualsensectl.git
cd dualsensectl
meson setup build && ninja -C build && sudo ninja -C build install
```

Verify it works:
```bash
dualsensectl battery
```
If you get a permission error, install the udev rules from the dualsensectl repo.

### 2. Install DSXSkyrim-NG for Skyrim

Extract `DSXSkyrimNG.7z` into your Skyrim `Data` directory. The file layout inside
Proton's wine prefix should look like:

```
"<pfx>/drive_c/Program Files (x86)/Steam/steamapps/common/Skyrim Anniversary Edition/Data/SKSE/Plugins/DSXSkyrim/"
  ├── DSXSkyrimNG.dll
  └── DSXSkyrim/DSXSkyrimConfig.json
```

Or inside `Data/` if your mod manager places files there. The plugin auto-detects both layouts.

### 3. (Optional) Proton networking fix

Wine/Proton can access `127.0.0.1` by default, but some Proton versions restrict UDP.
If the game sends packets but the daemon doesn't receive them, add this to your game's
launch options (in Steam):

```
WINEDLLOVERRIDES="winedevice.exe=d" %command%
```

Or ensure `winecfg` has `win10` as the Windows version.

### 4. Run the daemon

```bash
# Start before launching the game, or in a terminal/tmux/screen:
python3 /path/to/dsx-daemon.py

# With verbose logging:
python3 /path/to/dsx-daemon.py -v

# If you have multiple controllers, specify by serial:
dualsensectl -l                     # list devices
python3 /path/to/dsx-daemon.py -d 00:A0:B0:C0:D0
```

Add it to your autostart or launch it alongside Steam.

## Usage

1. Connect your DualSense controller
2. Start `dsx-daemon.py`
3. Launch Skyrim AE via Proton

That's it. The daemon will log when it receives packets and which `dualsensectl` commands it runs.

## DSX → dualsensectl trigger mode mapping

| DSX Mode | Name | dualsensectl command |
|----------|------|---------------------|
| 0 | Normal/Off | `trigger off` |
| 1 | GameCube | `feedback 0 1` |
| 2 | VerySoft | `feedback 0 2` |
| 3 | Soft | `feedback 0 3` |
| 4 | Hard | `feedback 0 4` |
| 5 | VeryHard | `feedback 0 6` |
| 6 | Hardest | `feedback 0 8` |
| 7 | Rigid | `feedback 0 8` |
| 8 | VibrateTrigger | `vibration 0 4 4` |
| 9 | Choppy | `vibration 0 8 8` |
| 10 | Medium | `feedback 0 5` |
| 11 | VibrateTriggerPulse | `vibration 0 8 4` |
| 12 | CustomTriggerValue | varies (off/feedback/vibration) |
| 13 | Resistance | `feedback pos str` |
| 14 | Bow | `bow start stop str snap` |
| 15 | Galloping | `galloping start stop f1 f2 freq` |
| 16 | SemiAutomaticGun | `weapon start stop str` |
| 17 | AutomaticGun | `weapon start stop str` |
| 18 | Machine | `machine start stop sa sb freq per` |

## Tuning

Edit `DSXSkyrimConfig.json` in `<game>/Data/SKSE/Plugins/DSXSkyrim/` to tweak
trigger effects per weapon category. See the original [DSXSkyrimConfigDocumentation.html](https://github.com/dvize/DSXSkyrim-NG/blob/master/DSXSkyrimConfigDocumentation.html)
for all available fields.
