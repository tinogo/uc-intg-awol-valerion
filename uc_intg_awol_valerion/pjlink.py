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

from uc_intg_awol_valerion import Loggers
from uc_intg_awol_valerion.const import (
    AVMUTE_MUTED,
    ERST_COMPONENTS,
    ERST_LEVELS,
    PJLINK_POWER,
    AwolValerionCommands,
    AwolValerionStates,
)

_LOG = logging.getLogger(Loggers.PJLINK)

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
    input_code: str | None = None
    av_muted: bool = False
    errors: dict[str, str] = field(default_factory=dict)
    has_error: bool = False


@dataclass
class PJLinkIdentity:
    """Static device information (queried once)."""

    name: str = ""
    manufacturer: str = ""
    product: str = ""
    other_info: str = ""
    sw_version: str = ""
    rec_resolution: str = ""
    input_codes: list[str] = field(default_factory=list)


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

                writer.write(f"{payload}\r".encode("utf-8"))
                await writer.drain()
                raw = await asyncio.wait_for(reader.read(256), timeout=_TIMEOUT)
                response = raw.decode("utf-8", errors="replace").strip()
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
        value = self._value(await self._send(AwolValerionCommands.GET_POWER))
        return value is not None

    async def get_power(self) -> AwolValerionStates:
        """Return the projector's current power state."""
        value = self._value(await self._send(AwolValerionCommands.GET_POWER))
        if self._is_err(value):
            return AwolValerionStates.UNAVAILABLE
        return PJLINK_POWER.get(value, AwolValerionStates.UNAVAILABLE)

    async def get_input(self) -> str | None:
        """Return the projector's current input code (e.g. ``HDMI1``)."""
        value = self._value(await self._send(AwolValerionCommands.GET_INPUT))
        return None if self._is_err(value) else value

    async def get_av_mute(self) -> bool:
        """Return True if the projector's audio and video output is muted."""
        value = self._value(await self._send(AwolValerionCommands.GET_AVMUTE))
        if self._is_err(value):
            return False
        return value in AVMUTE_MUTED

    async def get_errors(self) -> tuple[dict[str, str], bool]:
        """Return a dict of component errors and a bool indicating if there are any."""
        value = self._value(await self._send(AwolValerionCommands.GET_ERRORS))
        if self._is_err(value) or len(value) < 6:
            return {}, False
        result: dict[str, str] = {}
        has_error = False
        for name, char in zip(ERST_COMPONENTS, value[:6]):
            level = ERST_LEVELS.get(char, "OK")
            result[name] = level
            if char == "2":
                has_error = True
        return result, has_error

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
                status.input_code = await self.get_input()
                status.av_muted = await self.get_av_mute()
            except (OSError, asyncio.TimeoutError, PJLinkError):
                pass
        try:
            status.errors, status.has_error = await self.get_errors()
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
        inst = await _q(AwolValerionCommands.GET_INPUT_LIST)
        identity.input_codes = inst.split() if inst else []
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

    async def set_av_mute(self, muted: bool) -> None:
        """Mute/unmute the projector's audio and video output."""
        await self._send(
            AwolValerionCommands.SET_AVMUTE_ON
            if muted
            else AwolValerionCommands.SET_AVMUTE_OFF
        )

    async def send_raw(self, command: str) -> str:
        """Send a raw PJLink command string (e.g. ``%1INPT 32``)."""
        return await self._send(command)
