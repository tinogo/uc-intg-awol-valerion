"""Transport abstraction for Epson projector control."""

from __future__ import annotations

from dataclasses import dataclass, field

from uc_intg_awol_valerion import const


@dataclass
class ProjectorStatus:
    """A polled snapshot of the projector's dynamic state."""

    power: const.AwolValerionStates = const.AwolValerionStates.UNAVAILABLE
    reachable: bool = False
    source: str = ""  # friendly input name (already mapped)
    av_muted: bool = False
    lamp_hours: int | None = None
    color_mode: str | None = None
    errors: dict[str, str] = field(default_factory=dict)
    has_error: bool = False


@dataclass
class ProjectorIdentity:
    """Static device information (queried once)."""

    name: str = ""
    manufacturer: str = ""
    product: str = ""
    serial: str = ""
    sw_version: str = ""
    rec_resolution: str = ""
    filter_model: str = ""
    source_names: list[str] = field(default_factory=list)
    color_mode_list: list[str] = field(default_factory=list)


class TransportAuthError(Exception):
    """Raised when the transport rejects the supplied credentials."""


class Transport:
    """Common async interface implemented by every protocol client."""

    name: str = "transport"
    supports_color_mode: bool = False

    async def probe(self) -> bool:
        """Return True if the projector answers on this transport."""
        raise NotImplementedError

    async def get_identity(self) -> ProjectorIdentity:
        raise NotImplementedError

    async def poll(self) -> ProjectorStatus:
        raise NotImplementedError

    async def power_on(self) -> None:
        raise NotImplementedError

    async def power_off(self) -> None:
        raise NotImplementedError

    async def select_source(self, name: str) -> bool:
        return False

    async def set_av_mute(self, muted: bool) -> None:
        raise NotImplementedError

    async def send_raw(self, command: str) -> str:
        raise NotImplementedError

    async def get_color_mode(self) -> str | None:
        return None

    async def set_color_mode(self, name: str) -> bool:
        return False

    async def close(self) -> None:
        return None
