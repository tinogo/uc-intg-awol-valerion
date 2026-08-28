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
from uc_intg_awol_valerion.pjlink import (
    PJLinkAuthError,
    PJLinkClient,
    PJLinkIdentity,
    PJLinkStatus,
)

_LOG = logging.getLogger(Loggers.DEVICE)

MIN_VOLUME = 0
MAX_VOLUME = 100


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
        self.status = PJLinkStatus()
        self.identity = PJLinkIdentity()
        self._identity_loaded = False
        self._poll_interval = 5
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
        if not self.status.reachable:
            return const.AwolValerionStates.UNAVAILABLE
        return self.status.power

    @property
    def power(self) -> bool:
        """Return the current power state."""
        return self.status.power in (const.AwolValerionStates.ON,)

    async def establish_connection(self) -> Any:
        """Establish the initial connection to the projector."""
        async with self._connect_lock:
            if not self._identity_loaded:
                await self._load_identity()
            await self._refresh()
        _LOG.info("[%s] Connection established (state=%s)", self.log_id, self.state)

    async def poll_device(self) -> None:
        """Poll the device for the current device state."""
        async with self._connect_lock:
            if not self._identity_loaded:
                await self._load_identity()
            await self._refresh()
        self.push_update()

    async def _load_identity(self) -> None:
        try:
            self.identity = await self._client.get_identity()
            self._identity_loaded = True
        except PJLinkAuthError:
            _LOG.error("[%s] Authentication failed!", self.log_id)
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOG.info("[%s] Identity not available yet: %s", self.log_id, err)

    async def _refresh(self) -> None:
        try:
            new_status = await self._client.poll()
        except PJLinkAuthError:
            _LOG.error("[%s] Authentication failed!", self.log_id)
            new_status = PJLinkStatus()
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOG.debug("[%s] Poll failed: %s", self.log_id, err)
            new_status = PJLinkStatus()

        if new_status.reachable:
            # A single command in the poll may transiently fail to read; keep the
            # last good value rather than flashing "N/A".
            self.status = new_status
            self._fail_count = 0
        else:
            # Tolerate transient drops: keep the last-known state for a few
            # cycles before declaring the projector UNAVAILABLE.
            self._fail_count += 1
            if self._fail_count >= self.FAIL_THRESHOLD:
                self.status = new_status

    async def power_on(self) -> bool:
        """Power on the projector."""
        if await self._client.get_power() is AwolValerionStates.ON:
            return True

        try:
            await self._client.power_on()
            await self.poll_device()
            return True
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOG.info("[%s] power-on failed: %s", self.log_id, err)
        return False

    async def power_off(self) -> bool:
        """Power off the projector."""
        if await self._client.get_power() is AwolValerionStates.OFF:
            return True

        try:
            await self._client.power_off()
            await self.poll_device()
            return True
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOG.info("[%s] power-off failed: %s", self.log_id, err)
        return False

    async def power_toggle(self) -> bool:
        """Toggle the power of the projector."""
        return await self.power_off() if self.power else await self.power_on()

    async def select_source(self, name: str) -> bool:
        """Switch the projector to a different input."""
        source = self.status.input_list.get(name)

        if source is None:
            _LOG.warning("[%s] Unknown source: %s", self.log_id, name)
            return False

        try:
            if await self._client.select_input(source):
                await self.poll_device()
                return True
            return False
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOG.error("[%s] Source select failed: %s", self.log_id, err)
            return False

    async def mute_on(self) -> bool:
        """Mute the projector's audio output."""
        return await self._set_mute(True)

    async def mute_off(self) -> bool:
        """Unmute the projector's audio output."""
        return await self._set_mute(False)

    async def _set_mute(self, muted: bool) -> bool:
        """Set the mute state."""
        try:
            await self._client.set_mute(muted)
            await self.poll_device()
            return True
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOG.error("[%s] AV-mute failed: %s", self.log_id, err)
            return False

    async def mute_toggle(self) -> bool:
        """Toggle the projector's audio output mute state."""
        return await self._set_mute(not self.status.muted)

    async def cursor_up(self) -> bool:
        """Move the cursor up in the projector's OSD."""
        return await self.send_raw(const.AwolValerionCommands.SET_CURSOR_UP)

    async def cursor_down(self) -> bool:
        """Move the cursor down in the projector's OSD."""
        return await self.send_raw(const.AwolValerionCommands.SET_CURSOR_DOWN)

    async def cursor_left(self) -> bool:
        """Move the cursor left in the projector's OSD."""
        return await self.send_raw(const.AwolValerionCommands.SET_CURSOR_LEFT)

    async def cursor_right(self) -> bool:
        """Move the cursor right in the projector's OSD."""
        return await self.send_raw(const.AwolValerionCommands.SET_CURSOR_RIGHT)

    async def cursor_enter(self) -> bool:
        """Presses the OK key in the projector's OSD."""
        return await self.send_raw(const.AwolValerionCommands.SET_CURSOR_OK)

    async def back(self) -> bool:
        """Presses the BACK key in the projector's OSD."""
        return await self.send_raw(const.AwolValerionCommands.SET_RETURN)

    async def home(self) -> bool:
        """Show the home screen of the projector."""
        return await self.send_raw(const.AwolValerionCommands.SET_HOME)

    async def menu(self) -> bool:
        """Show the menu of the projector."""
        return await self.send_raw(const.AwolValerionCommands.SET_MENU)

    async def settings(self) -> bool:
        """Show the settings of the projector."""
        return await self.send_raw(const.AwolValerionCommands.SET_SETTINGS)

    async def volume_up(self) -> bool:
        """Increase the projector's volume."""
        return await self.send_raw(const.AwolValerionCommands.SET_VOLUME_UP)

    async def volume_down(self) -> bool:
        """Decrease the projector's volume."""
        return await self.send_raw(const.AwolValerionCommands.SET_VOLUME_DOWN)

    async def volume_x(self, volume) -> bool:
        """Set the projector's volume to a specific level."""
        sanitized_volume = max(MIN_VOLUME, min(MAX_VOLUME, int(volume)))

        return await self.send_raw(
            const.AwolValerionCommands.SET_VOLUME_X_FORMAT.format(sanitized_volume)
        )

    async def send_raw(self, command: str) -> bool:
        """Send a raw PJLink command string (e.g. ``%1INPT 32``)."""
        try:
            await self._client.send_raw(command)
            await self.poll_device()
            return True
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOG.error("[%s] Raw command '%s' failed: %s", self.log_id, command, err)
            return False
