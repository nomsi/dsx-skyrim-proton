"""DSX network protocol data models.

These types mirror the definitions in DSXController.hpp
and represent the JSON packets that DSXSkyrim-NG sends over UDP.
"""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


class TriggerMode(IntEnum):
    """Maps to the DSX ``TriggerMode`` enum (0..18)."""

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
    """Sub-mode for ``TriggerMode.CustomTriggerValue`` (mode 12)."""

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
    """The ``type`` field in a DSX JSON instruction."""

    GetDSXStatus = 0
    TriggerUpdate = 1
    RGBUpdate = 2
    TriggerThreshold = 4
    MicLED = 5
    PlayerLEDNewRevision = 6
    ResetToUserSettings = 7


class PlayerLEDMode(IntEnum):
    """Player LED brightness patterns matching DSX ``PlayerLEDNewRevision``."""

    One = 0
    Two = 1
    Three = 2
    Four = 3
    Five = 4
    AllOff = 5


class MicLEDMode(IntEnum):
    """Microphone LED state."""

    On = 0
    Pulse = 1
    Off = 2


@dataclass
class Instruction:
    """A single DSX protocol instruction.

    :param type: The ``InstructionType`` value.
    :param parameters: String-form parameters whose meaning depends on *type*.
    """

    type: int
    parameters: list[str] = field(default_factory=list)


@dataclass
class Packet:
    """A complete DSX protocol packet containing zero or more instructions.

    :param instructions: Ordered list of instructions to execute.
    """

    instructions: list[Instruction] = field(default_factory=list)

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Packet:
        """Parse a deserialized JSON dict into a ``Packet``.

        :param data: The JSON object as returned by ``json.loads``.
        :return: A new ``Packet`` with all fields populated.
        """
        pkt = cls()
        for raw in data.get("instructions", []):
            pkt.instructions.append(
                Instruction(
                    type=int(raw.get("type", 0)),
                    parameters=[str(p) for p in raw.get("parameters", [])],
                )
            )
        return pkt
