# pylint: disable=too-many-lines

"""
Device Communication Module.

This module handles all communication with your device. It manages connections,
sends commands, and tracks the device state.

:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import asyncio
import logging
from typing import Any

from ucapi_framework import PollingDevice

from uc_intg_awol_valerion import const
from uc_intg_awol_valerion.const import (
    AwolValerionStates,
    Loggers,
)
from uc_intg_awol_valerion.pjlink import PJLinkAuthError, PJLinkClient, PJLinkIdentity, PJLinkStatus

_LOG = logging.getLogger(Loggers.DEVICE)


class AwolValerionDevice(PollingDevice):
    """AWOL Valerion Projector Device."""

    # Keep the last-known state through that many consecutive failed polls
    # before reporting UNAVAILABLE (projectors drop the network briefly during
    # power on/off transitions and answer slowly while warming up).
    FAIL_THRESHOLD = 3

    def __init__(self, *args, **kwargs):
        """Initialize the device."""
        super().__init__(*args, **kwargs)
        self._connect_lock = asyncio.Lock()
        self._client = PJLinkClient(
            self.device_config.address,
            self.device_config.port,
            self.device_config.password,
        )
        self._status = PJLinkStatus()
        self._identity = PJLinkIdentity()
        self._color_mode: str | None = None
        self._identity_loaded = False
        self._fail_count = 0

    @property
    def address(self) -> str | None:
        """Return the device address."""
        return self._device_config.address

    @property
    def identifier(self) -> str:
        """Return the device identifier."""
        return self._device_config.identifier

    @property
    def log_id(self) -> str:
        """Return a log identifier for debugging."""
        return self.name if self.name else self.identifier

    @property
    def name(self) -> str:
        """Return the device name."""
        return self._device_config.name

    @property
    def state(self) -> AwolValerionStates:
        """Return the current device state."""
        if not self._status.reachable:
            return const.AwolValerionStates.UNAVAILABLE
        return self._status.power

    @property
    def power(self) -> bool:
        return self._status.power in (
            const.AwolValerionStates.ON,
            const.AwolValerionStates.WARMING,
        )

    async def establish_connection(self) -> Any:
        """Establish the initial connection to the projector."""
        async with self._connect_lock:
            if not self._identity_loaded:
                await self._load_identity()
            await self._refresh()
        _LOG.info("[%s] Connection established (state=%s)", self.log_id, self.state)

    async def poll_device(self) -> None:
        async with self._connect_lock:
            if not self._identity_loaded:
                await self._load_identity()
            await self._refresh()
        self.push_update()

    async def _load_identity(self) -> None:
        try:
            self._identity = await self._client.get_identity()
            self._identity_loaded = True
        except PJLinkAuthError:
            _LOG.error(
                "[%s] Authentication failed!", self.log_id
            )
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOG.info("[%s] Identity not available yet: %s", self.log_id, err)

    async def _refresh(self) -> None:
        try:
            new_status = await self._client.poll()
        except PJLinkAuthError:
            _LOG.error(
                "[%s] Authentication failed!", self.log_id
            )
            new_status = PJLinkStatus()
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOG.debug("[%s] Poll failed: %s", self.log_id, err)
            new_status = PJLinkStatus()

        if new_status.reachable:
            # A single command in the poll may transiently fail to read; keep the
            # last good value rather than flashing "N/A".
            self._status = new_status
            self._fail_count = 0
        else:
            # Tolerate transient drops: keep the last-known state for a few
            # cycles before declaring the projector UNAVAILABLE.
            self._fail_count += 1
            if self._fail_count >= self.FAIL_THRESHOLD:
                self._status = new_status

    async def power_on(self) -> bool:
        """Powers on the projector."""
        ok = False
        try:
            await self._client.power_on()
            ok = True
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOG.info(
                "[%s] power-on failed: %s", self.log_id, err
            )
        return ok

    async def power_off(self) -> bool:
        ok = False
        try:
            await self._client.power_off()
            ok = True
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOG.info(
                "[%s] power-off failed: %s", self.log_id, err
            )
        return ok

    async def power_toggle(self) -> bool:
        return await self.power_off() if self.power else await self.power_on()

    async def select_source(self, name: str) -> bool:
        try:
            if await self._client.select_input(name):
                return True
            _LOG.warning("[%s] Unknown source: %s", self.log_id, name)
            return False
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOG.error("[%s] Source select failed: %s", self.log_id, err)
            return False

    async def av_mute_on(self) -> bool:
        return await self._set_av_mute(True)

    async def av_mute_off(self) -> bool:
        return await self._set_av_mute(False)

    async def _set_av_mute(self, muted: bool) -> bool:
        try:
            await self._client.set_av_mute(muted)
            return True
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOG.error("[%s] AV-mute failed: %s", self.log_id, err)
            return False

    async def av_mute_toggle(self) -> bool:
        return await self._set_av_mute(not self._status.av_muted)

    async def send_raw(self, command: str) -> bool:
        try:
            await self._client.send_raw(command)
            return True
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOG.error("[%s] Raw command '%s' failed: %s", self.log_id, command, err)
            return False
