"""Async PJLink (Class 1/2) client for AWOL Valerion projectors.

One short-lived TCP connection per command (the PJLink reference behaviour),
serialised through a lock. Handles the optional MD5 authentication handshake
and parses the AWOL Valerion responses.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
from dataclasses import dataclass, field

from uc_intg_awol_valerion.const import (
    AwolValerionCommands,
    AwolValerionStates,
    Loggers,
)

_LOG = logging.getLogger(Loggers.PJLINK)

# PJLink power reply codes (from ``%1POWR ?`` / ``%1POWR=<n>``)
# PJLink power reply codes (from ``%1POWR ?`` / ``%1POWR=<n>``)
PJLINK_POWER = {
    "0": AwolValerionStates.OFF,  # standby
    "1": AwolValerionStates.ON,  # on
    "2": AwolValerionStates.OFF,  # off
}

# PJLink AV-mute reply codes (``%1AVMT=<n>``): 30 off, 11/21/31 muted
AVMUTE_MUTED = {"21"}

_TIMEOUT = 4.0


class PJLinkError(Exception):
    """Raised for PJLink protocol-level failures (auth, ERR responses)."""


class PJLinkAuthError(PJLinkError):
    """Raised when the projector rejects the supplied PJLink password."""


@dataclass
class PJLinkStatus:
    """A polled snapshot of the projector's dynamic state."""

    power: AwolValerionStates = AwolValerionStates.UNAVAILABLE
    reachable: bool = False
    input_id: str | None = None
    input_list: dict[str, str] = field(
        default_factory=lambda: {
            "Home": "30",
            "HDMI 1": "31",
            "HDMI 2": "32",
            "HDMI 3": "33",
        }
    )
    muted: bool = False
    volume: int = 0
    input_resolution: str | None = None
    aspect_ratio_id: str | None = None
    aspect_ratio_list: dict[str, str] = field(
        default_factory=lambda: {
            "Auto": "0",
            "4:3": "1",
            "Zoom": "2",
            "16:9": "3",
            "21:9": "4",
            "32:9": "5",
            "Anamorphic: 16:9": "6",
            "Anamorphic: 2.39:1": "7",
            "Anamorphic: 1.85:1": "8",
            "Anamorphic: 2.0:1": "9",
        }
    )
    color_temperature_id: str | None = None
    color_temperature_list: dict[str, str] = field(
        default_factory=lambda: {
            "Warm 1": "0",
            "Warm 2": "1",
            "Standard": "2",
            "Cool": "3",
        }
    )
    dynamic_tone_mapping_id: str | None = None
    dynamic_tone_mapping_list: dict[str, str] = field(
        default_factory=lambda: {
            "Off": "0",
            "Low": "1",
            "High": "2",
        }
    )
    ebl_id: str | None = None
    ebl_list: dict[str, str] = field(
        default_factory=lambda: {
            "Off": "0",
            "Low": "1",
            "Medium": "2",
            "High": "3",
        }
    )
    fan_speed: str | None = None
    gamma_id: str | None = None
    gamma_list: dict[str, str] = field(
        default_factory=lambda: {
            "2.0": "0",
            "2.2": "1",
            "2.4": "2",
            "BT1886": "3",
            "SMTP2084": "4",
            "HLG": "5",
        }
    )
    laser_luminance: str | None = None
    motion_enhancement_id: str | None = None
    motion_enhancement_list: dict[str, str] = field(
        default_factory=lambda: {
            "Off": "0",
            "Custom": "1",
            "Film": "2",
            "Clear": "3",
            "Standard": "4",
            "Smooth": "5",
        }
    )
    picture_mode: str | None = None
    signal_info: str | None = None
    temperature: str | None = None

    @property
    def source_list(self) -> list[str]:
        """Return a list of the available input sources."""
        return list(self.input_list.keys())

    @property
    def input(self) -> str | None:
        """Return the current pretty printed source."""
        if self.input_id is None:
            return None

        try:
            return list(self.input_list.keys())[
                list(self.input_list.values()).index(self.input_id)
            ]
        except ValueError:
            return None

    @property
    def aspect_ratio(self) -> str | None:
        """Return the current pretty printed aspect ratio."""
        if self.aspect_ratio_id is None:
            return None

        try:
            return list(self.aspect_ratio_list.keys())[
                list(self.aspect_ratio_list.values()).index(self.aspect_ratio_id)
            ]
        except ValueError:
            return None

    @property
    def color_temperature(self) -> str | None:
        """Return the current pretty printed color temperature."""
        if self.color_temperature_id is None:
            return None

        try:
            return list(self.color_temperature_list.keys())[
                list(self.color_temperature_list.values()).index(
                    self.color_temperature_id
                )
            ]
        except ValueError:
            return None

    @property
    def ebl(self) -> str | None:
        """Return the current pretty printed EBL mode."""
        if self.ebl_id is None:
            return None

        try:
            return list(self.ebl_list.keys())[
                list(self.ebl_list.values()).index(self.ebl_id)
            ]
        except ValueError:
            return None

    @property
    def dynamic_tone_mapping(self) -> str | None:
        """Return the current pretty printed dynamic tone mapping mode."""
        if self.dynamic_tone_mapping_id is None:
            return None

        try:
            return list(self.dynamic_tone_mapping_list.keys())[
                list(self.dynamic_tone_mapping_list.values()).index(
                    self.dynamic_tone_mapping_id
                )
            ]
        except ValueError:
            return None

    @property
    def gamma(self) -> str | None:
        """Return the current pretty printed Gamma mode."""
        if self.gamma_id is None:
            return None

        try:
            return list(self.gamma_list.keys())[
                list(self.gamma_list.values()).index(self.gamma_id)
            ]
        except ValueError:
            return None

    @property
    def motion_enhancement(self) -> str | None:
        """Return the current pretty printed motion enhancement mode."""
        if self.motion_enhancement_id is None:
            return None

        try:
            return list(self.motion_enhancement_list.keys())[
                list(self.motion_enhancement_list.values()).index(
                    self.motion_enhancement_id
                )
            ]
        except ValueError:
            return None


@dataclass
class PJLinkIdentity:
    """Static device information (queried once)."""

    name: str = ""
    manufacturer: str = ""
    product: str = ""
    other_info: str = ""
    sw_version: str = ""
    rec_resolution: str = ""


class PJLinkClient:
    """Talks PJLink to a single projector."""

    def __init__(self, host: str, port: int, password: str = "") -> None:
        """Initialize the client."""
        self._host = host
        self._port = port
        self._password = password or ""
        self._lock = asyncio.Lock()

    @property
    def host(self) -> str:
        """Return the host address."""
        return self._host

    async def _send_and_get_value(self, command: str) -> str | None:
        """Send a command and get its value."""
        response = await self._send(command)
        value = self._value(response)
        if self._is_err(value):
            return None
        return value

    async def _send(self, command: str) -> str:
        """Open a connection, (optionally) authenticate, send one command, read reply."""
        async with self._lock:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port), timeout=_TIMEOUT
            )
            try:
                greeting = (
                    (await asyncio.wait_for(reader.read(64), timeout=_TIMEOUT))
                    .decode("utf-8", errors="replace")
                    .strip()
                )
                payload = command
                if greeting.startswith("PJLINK 1"):
                    parts = greeting.split(" ")
                    if len(parts) < 3:
                        raise PJLinkError("Malformed authentication challenge")
                    seed = parts[2].strip()
                    digest = hashlib.md5(
                        (self._password + seed).encode("utf-8")
                    ).hexdigest()
                    payload = f"{digest}{command}"
                elif greeting.startswith("PJLINK ERRA"):
                    raise PJLinkAuthError("Authentication required")

                _LOG.debug("[%s] Sending: %s", self._host, payload)

                writer.write(f"{payload}\r".encode("utf-8"))
                await writer.drain()
                raw = await asyncio.wait_for(reader.read(256), timeout=_TIMEOUT)
                response = raw.decode("utf-8", errors="replace").strip()

                _LOG.debug("[%s] Received: %s", self._host, response)

                if "PJLINK ERRA" in response:
                    raise PJLinkAuthError("Invalid PJLink password")
                return response
            finally:
                writer.close()
                try:
                    await writer.wait_closed()
                except Exception:  # pylint: disable=broad-exception-caught
                    pass

    @staticmethod
    def _value(response: str) -> str | None:
        """Extract the value from an ``%<cmd>=<value>`` reply."""
        if "=" not in response:
            return None
        return response.split("=", 1)[1].strip()

    @staticmethod
    def _is_err(value: str | None) -> bool:
        return value is None or value.upper().startswith("ERR")

    # -- high-level queries -------------------------------------------------
    async def test(self) -> bool:
        """Return True if the projector answers a power query (validates setup)."""
        return (
            await self._send_and_get_value(AwolValerionCommands.GET_POWER) is not None
        )

    async def get_power(self) -> AwolValerionStates:
        """Return the projector's current power state."""
        value = await self._send_and_get_value(AwolValerionCommands.GET_POWER)
        if value is None:
            return AwolValerionStates.UNAVAILABLE
        return PJLINK_POWER.get(value, AwolValerionStates.UNAVAILABLE)

    async def get_mute(self) -> bool:
        """Return True if the projector's audio output is muted."""
        value = await self._send_and_get_value(AwolValerionCommands.GET_AVMUTE)
        return value in AVMUTE_MUTED

    async def get_volume(self) -> int:
        """Return the current volume of the projector."""
        value = await self._send_and_get_value(AwolValerionCommands.GET_VOLUME)
        if value is None:
            return 0
        return int(value)

    async def poll(self) -> PJLinkStatus:
        """Fetch a full dynamic snapshot; sets ``reachable`` on TCP success."""
        status = PJLinkStatus()
        try:
            status.power = await self.get_power()
            status.reachable = status.power != AwolValerionStates.UNAVAILABLE
        except PJLinkAuthError:
            raise
        except (OSError, asyncio.TimeoutError, PJLinkError) as err:
            _LOG.debug("[%s] PJLink unreachable: %s", self._host, err)
            return status

        if status.power in (
            AwolValerionStates.ON,
            AwolValerionStates.UNKNOWN,
        ):
            try:
                status.input_id = await self._send_and_get_value(
                    AwolValerionCommands.GET_INPUT
                )
                status.muted = await self.get_mute()
                status.volume = await self.get_volume()
                status.input_resolution = await self._send_and_get_value(
                    AwolValerionCommands.GET_INPUT_RESOLUTION
                )
                status.aspect_ratio_id = await self._send_and_get_value(
                    AwolValerionCommands.GET_ASPECT_RATIO
                )
                status.color_temperature_id = await self._send_and_get_value(
                    AwolValerionCommands.GET_COLOR_TEMPERATURE
                )
                status.dynamic_tone_mapping_id = await self._send_and_get_value(
                    AwolValerionCommands.GET_DYNAMIC_TONE_MAPPING
                )
                status.ebl_id = await self._send_and_get_value(
                    AwolValerionCommands.GET_EBL
                )
                status.fan_speed = await self._send_and_get_value(
                    AwolValerionCommands.GET_FAN_SPEED
                )
                status.gamma_id = await self._send_and_get_value(
                    AwolValerionCommands.GET_GAMMA
                )
                status.laser_luminance = await self._send_and_get_value(
                    AwolValerionCommands.GET_LASER_LUMINANCE
                )
                status.motion_enhancement_id = await self._send_and_get_value(
                    AwolValerionCommands.GET_MOTION_ENHANCEMENT
                )
                status.picture_mode = await self._send_and_get_value(
                    AwolValerionCommands.GET_PICTURE_MODE
                )
                status.signal_info = await self._send_and_get_value(
                    AwolValerionCommands.GET_SIGNAL_INFO
                )
                status.temperature = await self._send_and_get_value(
                    AwolValerionCommands.GET_TEMPERATURE
                )
            except (OSError, asyncio.TimeoutError, PJLinkError):
                pass
        return status

    async def get_identity(self) -> PJLinkIdentity:
        """Query the static device information (name, model, inputs...)."""
        identity = PJLinkIdentity()

        async def _q(command: str) -> str:
            value = self._value(await self._send(command))
            return "" if self._is_err(value) else value

        identity.name = await _q(AwolValerionCommands.GET_NAME)
        identity.manufacturer = await _q(AwolValerionCommands.GET_MANUFACTURER)
        identity.product = await _q(AwolValerionCommands.GET_PRODUCT)
        identity.other_info = await _q(AwolValerionCommands.GET_OTHER_INFO)
        identity.sw_version = await _q(AwolValerionCommands.GET_SW_VERSION)
        identity.rec_resolution = await _q(AwolValerionCommands.GET_REC_RESOLUTION)

        return identity

    # -- commands -----------------------------------------------------------
    async def power_on(self) -> None:
        """Power on the projector."""
        await self._send(AwolValerionCommands.POWER_ON)

    async def power_off(self) -> None:
        """Power off the projector."""
        await self._send(AwolValerionCommands.POWER_OFF)

    async def select_input(self, code: str) -> None:
        """Select a different input."""
        await self._send(AwolValerionCommands.SET_INPUT.format(code=code))

    async def set_mute(self, muted: bool) -> None:
        """Mute/unmute the projector's audio output."""
        await self._send(
            AwolValerionCommands.SET_MUTE_ON
            if muted
            else AwolValerionCommands.SET_MUTE_OFF
        )

    async def send_raw(self, command: str) -> str:
        """Send a raw PJLink command string (e.g. ``%1INPT 32``)."""
        return await self._send(command)
