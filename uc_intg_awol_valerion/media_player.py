# pylint: disable=duplicate-code

"""
Media Player Entity.

:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import logging
from typing import Any, Callable

from ucapi import EntityTypes, MediaPlayer, StatusCodes, media_player
from ucapi.media_player import Attributes as MediaAttr
from ucapi.media_player import DeviceClasses, States
from ucapi_framework import Entity, create_entity_id

from uc_intg_awol_valerion.config import AwolValerionConfig
from uc_intg_awol_valerion.const import (
    MEDIA_PLAYER_STATE_MAPPING,
    AwolValerionStates,
    Loggers,
    SimpleCommands,
)
from uc_intg_awol_valerion.device import AwolValerionDevice
from uc_intg_awol_valerion.simple_commands import get_simple_command_map

_LOG = logging.getLogger(Loggers.MEDIA_PLAYER)

FEATURES = [
    media_player.Features.ON_OFF,
    media_player.Features.DPAD,
    media_player.Features.TOGGLE,
    media_player.Features.VOLUME,
    media_player.Features.VOLUME_UP_DOWN,
    media_player.Features.HOME,
    media_player.Features.MUTE,
    media_player.Features.UNMUTE,
    media_player.Features.MUTE_TOGGLE,
    media_player.Features.SELECT_SOURCE,
]


class AwolValerionMediaPlayer(MediaPlayer, Entity):
    """
    Media Player entity for your device.

    This class handles all media player commands and maintains the entity state.
    """

    def __init__(self, device_config: AwolValerionConfig, device: AwolValerionDevice):
        """
        Initialize the media player entity.

        :param device_config: Device configuration from the setup
        :param device: The device instance to control
        """
        self._device = device

        self._command_map: dict[str, Callable] = {
            media_player.Commands.ON.value: device.power_on,
            media_player.Commands.OFF.value: device.power_off,
            media_player.Commands.TOGGLE.value: device.power_toggle,
            media_player.Commands.VOLUME_UP.value: device.volume_up,
            media_player.Commands.VOLUME_DOWN.value: device.volume_down,
            media_player.Commands.MUTE.value: device.av_mute_on,
            media_player.Commands.UNMUTE.value: device.av_mute_off,
            media_player.Commands.MUTE_TOGGLE.value: device.av_mute_toggle,
            media_player.Commands.CURSOR_UP.value: device.cursor_up,
            media_player.Commands.CURSOR_DOWN.value: device.cursor_down,
            media_player.Commands.CURSOR_LEFT.value: device.cursor_left,
            media_player.Commands.CURSOR_RIGHT.value: device.cursor_right,
            media_player.Commands.CURSOR_ENTER.value: device.cursor_enter,
            media_player.Commands.BACK.value: device.back,
            media_player.Commands.HOME.value: device.home,
            **get_simple_command_map(self._device),
        }

        entity_id = create_entity_id(EntityTypes.MEDIA_PLAYER, device.identifier)

        _LOG.debug("Initializing media player entity: %s", entity_id)

        super().__init__(
            identifier=entity_id,
            name=f"{device_config.name} Media Player",
            features=FEATURES,
            attributes=device.get_device_attributes(entity_id),
            device_class=DeviceClasses.TV,
            options={
                media_player.Options.SIMPLE_COMMANDS: [
                    member.value for member in SimpleCommands
                ]
            },
            cmd_handler=self.handle_command,
        )

        self.subscribe_to_device(device)

    async def handle_command(
        self,
        entity: MediaPlayer,
        cmd_id: str,
        params: dict[str, Any] | None,
        _: Any | None = None,
    ) -> StatusCodes:
        """
        Handle media player commands from the remote.

        This method is called by the integration API when a command is sent
        to this media player entity.

        :param entity: The media player entity receiving the command
        :param cmd_id: The command identifier
        :param params: Optional command parameters
        :param _: Optional parameter containing the websocket resource

        :return: Status code indicating success or failure
        """
        _LOG.info(
            "[%s] Received command: %s %s", entity.id, cmd_id, params if params else ""
        )

        try:
            match cmd_id:
                case cmd_id if cmd_id in self._command_map:
                    await self._command_map[cmd_id]()

                # complex commands (with parameters)
                case media_player.Commands.VOLUME:
                    volume = params.get("volume") if params else None
                    await self._device.volume_x(volume)

                case media_player.Commands.SELECT_SOURCE:
                    source = params.get("source") if params else None
                    await self._device.select_source(source)

                # --- unhandled commands ---
                case _:
                    _LOG.warning("Unhandled command: %s", cmd_id)
                    return StatusCodes.NOT_IMPLEMENTED

            return StatusCodes.OK

        except Exception as ex:  # pylint: disable=broad-exception-caught
            _LOG.error("Error executing command %s: %s", cmd_id, ex)
            return StatusCodes.BAD_REQUEST

    def map_entity_states(self, device_state: AwolValerionStates) -> States:
        """Convert a device-specific state to a UC API entity state."""
        return MEDIA_PLAYER_STATE_MAPPING[device_state]

    async def sync_state(self) -> None:
        """Update the media player attributes."""
        self.update(
            {
                MediaAttr.STATE: MEDIA_PLAYER_STATE_MAPPING[self._device.state],
                MediaAttr.SOURCE: self._device.status.input,
                MediaAttr.SOURCE_LIST: list(self._device.status.source_list),
                MediaAttr.VOLUME: self._device.status.volume,
                MediaAttr.MUTED: self._device.status.muted,
            }
        )
