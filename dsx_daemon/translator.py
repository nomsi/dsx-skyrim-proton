import logging
from typing import Callable

from dsx_daemon.packet import (
    CustomTriggerValueMode,
    Instruction,
    InstructionType,
    MicLEDMode,
    Packet,
    PlayerLEDMode,
    TriggerMode,
)

log = logging.getLogger("dsx-daemon")

_TRIGGER_SIDE = {"1": "left", "2": "right"}


def _side(raw: str) -> str:
    return _TRIGGER_SIDE.get(raw, raw)


def _clamp(value: int, lo: int = 0, hi: int = 8) -> int:
    return max(lo, min(hi, value))


_PRESET_MAP: dict[int, tuple[int, int]] = {
    TriggerMode.GameCube: (2, 3),
    TriggerMode.VerySoft: (0, 2),
    TriggerMode.Soft: (0, 3),
    TriggerMode.Hard: (0, 5),
    TriggerMode.VeryHard: (0, 7),
    TriggerMode.Hardest: (0, 8),
    TriggerMode.Rigid: (0, 8),
}


def translate_trigger_update(inst: Instruction) -> list[list[str]]:
    """Parameters: [controllerIdx, triggerSide, triggerMode, extra...]"""
    params = inst.parameters
    if len(params) < 3:
        log.warning("TriggerUpdate: too few parameters: %s", params)
        return []

    side = _side(params[1])
    mode = int(params[2]) if len(params) > 2 else 0
    extra = params[3:]
    cmds: list[list[str]] = []

    if mode == TriggerMode.Normal:
        cmds.append(["trigger", side, "off"])

    elif mode in _PRESET_MAP:
        pos, strength = _PRESET_MAP[mode]
        cmds.append(["trigger", side, "feedback", str(pos), str(strength)])

    elif mode == TriggerMode.VibrateTrigger:
        cmds.append(["trigger", side, "vibration", "0", "4", "4"])
    elif mode == TriggerMode.Choppy:
        cmds.append(["trigger", side, "vibration", "0", "8", "8"])
    elif mode == TriggerMode.Medium:
        cmds.append(["trigger", side, "feedback", "0", "5"])
    elif mode == TriggerMode.VibrateTriggerPulse:
        cmds.append(["trigger", side, "vibration", "0", "8", "4"])

    elif mode == TriggerMode.CustomTriggerValue:
        cmds.extend(_translate_custom_trigger_value(side, extra))

    elif mode == TriggerMode.Resistance:
        pos = int(extra[0]) if extra else 0
        strength = int(extra[1]) if len(extra) > 1 else 0
        cmds.append([
            "trigger", side, "feedback",
            str(_clamp(pos, 0, 9)),
            str(_clamp(strength, 1, 8)),
        ])

    elif mode == TriggerMode.Bow:
        start = max(1, int(extra[0]) if extra else 1)
        stop = max(start + 1, int(extra[1]) if len(extra) > 1 else 8)
        strength = int(extra[2]) if len(extra) > 2 else 2
        snap = int(extra[3]) if len(extra) > 3 else 8
        cmds.append([
            "trigger", side, "bow",
            str(_clamp(start, 1, 8)),
            str(_clamp(stop, 2, 8)),
            str(_clamp(strength, 1, 8)),
            str(_clamp(snap, 1, 8)),
        ])

    elif mode == TriggerMode.Galloping:
        start = max(0, int(extra[0]) if extra else 0)
        stop = max(start + 1, int(extra[1]) if len(extra) > 1 else 9)
        f1 = int(extra[2]) if len(extra) > 2 else 0
        f2 = max(f1 + 1, int(extra[3]) if len(extra) > 3 else 4)
        freq = int(extra[4]) if len(extra) > 4 else 2
        cmds.append([
            "trigger", side, "galloping",
            str(_clamp(start, 0, 8)),
            str(_clamp(stop, 1, 9)),
            str(_clamp(f1, 0, 6)),
            str(_clamp(f2, 1, 8)),
            str(_clamp(freq, 1, 8)),
        ])

    elif mode in (TriggerMode.SemiAutomaticGun, TriggerMode.AutomaticGun):
        start = int(extra[0]) if extra else 2
        stop = max(start + 1, int(extra[1]) if len(extra) > 1 else 6)
        strength = int(extra[2]) if len(extra) > 2 else 4
        cmds.append([
            "trigger", side, "weapon",
            str(_clamp(start, 2, 7)),
            str(_clamp(stop, 3, 8)),
            str(_clamp(strength, 1, 8)),
        ])

    elif mode == TriggerMode.Machine:
        start = max(1, int(extra[0]) if extra else 1)
        stop = max(start + 1, int(extra[1]) if len(extra) > 1 else 9)
        sa = int(extra[2]) if len(extra) > 2 else 0
        sb = int(extra[3]) if len(extra) > 3 else 4
        freq = int(extra[4]) if len(extra) > 4 else 2
        period = int(extra[5]) if len(extra) > 5 else 1
        cmds.append([
            "trigger", side, "machine",
            str(_clamp(start, 1, 8)),
            str(_clamp(stop, 2, 9)),
            str(_clamp(sa, 0, 7)),
            str(_clamp(sb, 0, 7)),
            str(_clamp(freq, 1, 8)),
            str(_clamp(period, 0, 8)),
        ])

    else:
        log.warning("TriggerUpdate: unknown mode %d", mode)
        cmds.append(["trigger", side, "off"])

    return cmds


def _translate_custom_trigger_value(
        side: str, extra: list[str]
) -> list[list[str]]:
    """Parameters: [customTriggerValueMode, p0, p1]"""
    cv_mode = int(extra[0]) if extra else 0
    p0 = int(extra[1]) if len(extra) > 1 else 0
    p1 = int(extra[2]) if len(extra) > 2 else 0

    _cv = CustomTriggerValueMode
    dispatch: dict[int, list[str]] = {
        _cv.OFF: ["trigger", side, "off"],
        _cv.Rigid: ["trigger", side, "feedback", "0", "8"],
        _cv.RigidA: ["trigger", side, "feedback", str(_clamp(p0, 0, 9)), "8"],
        _cv.RigidB: ["trigger", side, "feedback", str(_clamp(p1, 0, 9)), "8"],
        _cv.RigidAB: ["trigger", side, "feedback", str(_clamp(p0, 0, 9)), "8"],
        _cv.Pulse: ["trigger", side, "vibration", "0", "8", "4"],
        _cv.PulseA: ["trigger", side, "vibration", str(_clamp(p0, 0, 9)), "8", "4"],
        _cv.PulseB: ["trigger", side, "vibration", str(_clamp(p1, 0, 9)), "8", "4"],
        _cv.PulseAB: ["trigger", side, "vibration", str(_clamp(p0, 0, 9)), "8", "4"],
    }
    cmd = dispatch.get(cv_mode, ["trigger", side, "off"])
    return [cmd]


def translate_rgb_update(inst: Instruction) -> list[list[str]]:
    """Parameters: [controllerIdx, r, g, b, brightness]"""
    params = inst.parameters
    if len(params) < 5:
        log.warning("RGBUpdate: too few parameters: %s", params)
        return []
    return [["lightbar", params[1], params[2], params[3], params[4]]]


def translate_player_led(inst: Instruction) -> list[list[str]]:
    """Parameters: [controllerIdx, ledMode]"""
    params = inst.parameters
    led_val = int(params[1]) if len(params) > 1 else 5
    if led_val == PlayerLEDMode.AllOff:
        count = 0
    else:
        count = min(int(led_val) + 1, 7)
    return [["player-leds", str(count)]]


def translate_mic_led(inst: Instruction) -> list[list[str]]:
    """Parameters: [controllerIdx, mode]"""
    params = inst.parameters
    mic_mode = int(params[1]) if len(params) > 1 else 2
    _mic_states: dict[int, str] = {
        MicLEDMode.On: "on",
        MicLEDMode.Pulse: "pulse",
        MicLEDMode.Off: "off",
    }
    return [["microphone-led", _mic_states.get(mic_mode, "off")]]


def translate_reset(_inst: Instruction) -> list[list[str]]:
    return [
        ["trigger", "left", "off"],
        ["trigger", "right", "off"],
        ["lightbar", "0", "0", "0", "0"],
        ["player-leds", "0"],
        ["microphone-led", "off"],
    ]


def _noop_trigger_threshold(_inst: Instruction) -> list[list[str]]:
    log.debug("TriggerThreshold not implemented, ignored")
    return []


_INSTRUCTION_DISPATCH: dict[int, Callable[[Instruction], list[list[str]]]] = {
    InstructionType.TriggerUpdate: translate_trigger_update,
    InstructionType.TriggerThreshold: _noop_trigger_threshold,
    InstructionType.RGBUpdate: translate_rgb_update,
    InstructionType.PlayerLEDNewRevision: translate_player_led,
    InstructionType.MicLED: translate_mic_led,
    InstructionType.ResetToUserSettings: translate_reset,
}


def translate_packet(packet: Packet) -> list[list[str]]:
    commands: list[list[str]] = []
    for inst in packet.instructions:
        handler = _INSTRUCTION_DISPATCH.get(inst.type)
        if handler:
            try:
                commands.extend(handler(inst))
            except Exception:
                log.exception(
                    "Error translating instruction type %d: %s",
                    inst.type,
                    inst.parameters,
                )
        else:
            log.warning("Unknown instruction type %d", inst.type)
    return commands
