"""DSX network protocol data models.

Mirrors the types in DSXController.hpp.
"""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


class TriggerMode(IntEnum):
    """DSX trigger effect modes (0..18)."""

    Normal = 0
    GameCube = 1
    VerySoft = 2
    Soft = 3
    Hard = 4
    VeryHard = 5
    Hardest = 6
    Rigid = 7
    VibrateTrigger = 8
    Choppy = 9
    Medium = 10
    VibrateTriggerPulse = 11
    CustomTriggerValue = 12
    Resistance = 13
    Bow = 14
    Galloping = 15
    SemiAutomaticGun = 16
    AutomaticGun = 17
    Machine = 18


class CustomTriggerValueMode(IntEnum):
    """Sub-mode for CustomTriggerValue (mode 12)."""

    OFF = 0
    Rigid = 1
    RigidA = 2
    RigidB = 3
    RigidAB = 4
    Pulse = 5
    PulseA = 6
    PulseB = 7
    PulseAB = 8


class InstructionType(IntEnum):
    """DSX instruction type identifiers."""

    GetDSXStatus = 0
    TriggerUpdate = 1
    RGBUpdate = 2
    TriggerThreshold = 4
    MicLED = 5
    PlayerLEDNewRevision = 6
    ResetToUserSettings = 7


class PlayerLEDMode(IntEnum):
    """Player LED brightness settings."""

    One = 0
    Two = 1
    Three = 2
    Four = 3
    Five = 4
    AllOff = 5


class MicLEDMode(IntEnum):
    """Microphone LED states."""

    On = 0
    Pulse = 1
    Off = 2


@dataclass
class Instruction:
    type: int
    parameters: list[str] = field(default_factory=list)


@dataclass
class Packet:
    instructions: list[Instruction] = field(default_factory=list)

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Packet:
        pkt = cls()
        for raw in data.get("instructions", []):
            pkt.instructions.append(
                Instruction(
                    type=raw.get("type", 0),
                    parameters=list(raw.get("parameters", [])),
                )
            )
        return pkt
