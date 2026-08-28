# pylint: disable=duplicate-code

"""
Remote Entity.

:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import asyncio
import logging
from typing import Any

from ucapi import EntityTypes, Remote, StatusCodes, remote
from ucapi.remote import Attributes as RemoteAttr
from ucapi.remote import States
from ucapi_framework import Entity, create_entity_id

from uc_intg_awol_valerion.config import AwolValerionConfig
from uc_intg_awol_valerion.const import (
    AwolValerionStates,
    Loggers,
    SimpleCommands,
)
from uc_intg_awol_valerion.device import AwolValerionDevice
from uc_intg_awol_valerion.simple_commands import get_simple_command_map

_LOG = logging.getLogger(Loggers.REMOTE)

_REMOTE_STATE_MAPPING = {
    AwolValerionStates.ON: States.ON,
    AwolValerionStates.OFF: States.OFF,
    AwolValerionStates.UNAVAILABLE: States.UNAVAILABLE,
    AwolValerionStates.UNKNOWN: States.UNKNOWN,
}


class AwolValerionRemote(Remote, Entity):
    """
    Remote entity for your device.

    This class handles all Remote commands and maintains the entity state.
    """

    def __init__(self, device_config: AwolValerionConfig, device: AwolValerionDevice):
        """
        Initialize the remote entity.

        :param device_config: Device configuration from the setup
        :param device: The device instance to control
        """
        self._device = device

        self._command_map = {
            **get_simple_command_map(self._device),
        }

        entity_id = create_entity_id(EntityTypes.REMOTE, device.identifier)

        _LOG.debug("Initializing remote entity: %s", entity_id)

        super().__init__(
            identifier=entity_id,
            name=f"{device_config.name} Remote",
            features=[
                remote.Features.ON_OFF,
                remote.Features.SEND_CMD,
                remote.Features.TOGGLE,
            ],
            attributes=device.get_device_attributes(entity_id),
            simple_commands=[member.value for member in SimpleCommands],
            cmd_handler=self.handle_command,
        )

        self.subscribe_to_device(device)

    async def handle_command(
        self,
        entity: Remote,
        cmd_id: str,
        params: dict[str, Any] | None,
        _: Any | None = None,
    ) -> StatusCodes:
        """
        Handle commands from the remote.

        This method is called by the integration API when a command is sent
        to this remote entity.

        :param entity: The remote receiving the command
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

                case remote.Commands.SEND_CMD:
                    if params:
                        command = params.get("command", None)
                        repeat = params.get("repeat", 1)
                        delay = params.get("delay", 100)
                        await self._handle_send_cmd(command, repeat, delay)
                    else:
                        raise ValueError(
                            "Cannot process command without any given parameters."
                        )

                case remote.Commands.SEND_CMD_SEQUENCE:
                    if params:
                        command_list = params.get("sequence") if params else None
                        repeat = params.get("repeat", 1)
                        delay = params.get("delay", 100)

                        for command in command_list:
                            await self._handle_send_cmd(command, repeat, delay)
                    else:
                        raise ValueError(
                            "Cannot process command without any given parameters."
                        )

                # --- unhandled commands ---
                case _:
                    _LOG.warning("Unhandled command: %s", cmd_id)
                    return StatusCodes.NOT_IMPLEMENTED

            return StatusCodes.OK

        except Exception as ex:  # pylint: disable=broad-exception-caught
            _LOG.error("Error executing command %s: %s", cmd_id, ex)
            return StatusCodes.BAD_REQUEST

    async def _handle_send_cmd(self, command: str, repeat: int, delay: int) -> None:
        for _ in range(repeat):
            if command in self._command_map:
                await self._command_map[command]()
            else:
                await self._device.send_raw(command)

            if delay > 0:
                await asyncio.sleep(delay / 1000)

    def map_entity_states(self, device_state: AwolValerionStates) -> States:
        """Convert a device-specific state to a UC API entity state."""
        return _REMOTE_STATE_MAPPING[device_state]

    async def sync_state(self) -> None:
        """Update the remote attributes."""
        self.update(
            {
                RemoteAttr.STATE: _REMOTE_STATE_MAPPING[self._device.state],
            }
        )
