"""
Select Entity.

:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import logging
from dataclasses import dataclass
from typing import Any, Callable, Literal

from ucapi import EntityTypes, Select, StatusCodes
from ucapi.select import Attributes as SelectAttr
from ucapi.select import Commands as SelectCommands
from ucapi.select import States
from ucapi_framework import Entity, create_entity_id

from uc_intg_awol_valerion.const import (
    SELECT_STATE_MAPPING,
    AwolValerionCommands,
    AwolValerionStates,
    Loggers,
    SelectType,
)
from uc_intg_awol_valerion.device import AwolValerionDevice

_LOG = logging.getLogger(Loggers.SELECT)


@dataclass(frozen=True)
class SelectConfig:
    """Configuration for one select type."""

    label: str
    command_template: str
    get_current_option: Callable[[AwolValerionDevice], str | None]
    get_options: Callable[[AwolValerionDevice], list[str]]
    map_option_to_device_value: Callable[[AwolValerionDevice, str], str | None]


SELECT_CONFIGS: dict[SelectType, SelectConfig] = {
    SelectType.COLOR_TEMPERATURE: SelectConfig(
        label="Color Temperature",
        command_template=AwolValerionCommands.SET_COLOR_TEMPERATURE,
        get_current_option=lambda device: device.status.color_temperature,
        get_options=lambda device: list(device.status.color_temperature_list.keys()),
        map_option_to_device_value=lambda device, option: (
            device.status.color_temperature_list.get(option)
        ),
    ),
    SelectType.DYNAMIC_TONE_MAPPING: SelectConfig(
        label="Dynamic Tone Mapping",
        command_template=AwolValerionCommands.SET_DYNAMIC_TONE_MAPPING,
        get_current_option=lambda device: device.status.dynamic_tone_mapping,
        get_options=lambda device: list(device.status.dynamic_tone_mapping_list.keys()),
        map_option_to_device_value=lambda device, option: (
            device.status.dynamic_tone_mapping_list.get(option)
        ),
    ),
    SelectType.EBL: SelectConfig(
        label="EBL",
        command_template=AwolValerionCommands.SET_EBL,
        get_current_option=lambda device: device.status.ebl,
        get_options=lambda device: list(device.status.ebl_list.keys()),
        map_option_to_device_value=lambda device, option: device.status.ebl_list.get(
            option
        ),
    ),
    SelectType.GAMMA: SelectConfig(
        label="Gamma",
        command_template=AwolValerionCommands.SET_GAMMA,
        get_current_option=lambda device: device.status.gamma,
        get_options=lambda device: list(device.status.gamma_list.keys()),
        map_option_to_device_value=lambda device, option: device.status.gamma_list.get(
            option
        ),
    ),
    SelectType.MOTION_ENHANCEMENT: SelectConfig(
        label="Motion Enhancement",
        command_template=AwolValerionCommands.SET_MOTION_ENHANCEMENT,
        get_current_option=lambda device: device.status.motion_enhancement,
        get_options=lambda device: list(device.status.motion_enhancement_list.keys()),
        map_option_to_device_value=lambda device, option: (
            device.status.motion_enhancement_list.get(option)
        ),
    ),
    SelectType.LASER_LUMINANCE: SelectConfig(
        label="Laser Luminance",
        command_template=AwolValerionCommands.SET_LASER_LUMINANCE,
        get_current_option=lambda device: device.status.laser_luminance,
        get_options=lambda _device: [str(value) for value in range(0, 11)],
        map_option_to_device_value=lambda _device, option: option,
    ),
    SelectType.PICTURE_MODE: SelectConfig(
        label="Picture Mode",
        command_template=AwolValerionCommands.SET_PICTURE_MODE,
        get_current_option=lambda device: device.status.picture_mode,
        get_options=lambda device: list(device.status.picture_mode_list),
        map_option_to_device_value=lambda _device, option: option,
    ),
}


class AwolValerionSelect(Select, Entity):
    """Select Entity for AWOL Valerion projectors."""

    def __init__(
        self,
        device: AwolValerionDevice,
        select_type: SelectType,
    ):
        """Initialize the select entity."""
        self._device = device
        select_config = self._get_select_config(select_type, device)
        self._select_config: SelectConfig = select_config["select_config"]

        _LOG.debug("Initializing select: %s", select_config["identifier"])

        super().__init__(
            identifier=select_config["identifier"],
            name=select_config["name"],
            attributes=select_config["attributes"],
            cmd_handler=self.handle_command,
        )

        self.subscribe_to_device(device)

    def _get_select_config(
        self, select_type: SelectType, device: AwolValerionDevice
    ) -> dict[str, Any]:
        """Get select configuration based on type."""
        select_entity_id = create_entity_id(
            EntityTypes.SELECT,
            device.identifier,
            select_type,
        )

        config = SELECT_CONFIGS.get(select_type)
        if config is None:
            raise ValueError(f"Unsupported select type: {select_type}")

        return {
            "identifier": select_entity_id,
            "name": f"{device.name} Select: {config.label}",
            "attributes": self._device.get_device_attributes(select_entity_id),
            "select_config": config,
        }

    async def handle_command(
        self,
        entity: Select,
        cmd_id: str,
        params: dict[str, Any] | None,
        _: Any | None = None,
    ) -> StatusCodes:
        """Handle select commands from the remote."""
        _LOG.debug(
            "[%s] Received command for select entity: %s %s",
            entity.id,
            cmd_id,
            params if params else "",
        )

        return await self._handle_select_command(cmd_id, params)

    def _get_select_attributes(self) -> dict[str, Any]:
        """Build UC API attributes from the active select config."""
        return {
            SelectAttr.STATE: SELECT_STATE_MAPPING[self._device.state],
            SelectAttr.CURRENT_OPTION: self._select_config.get_current_option(
                self._device
            ),
            SelectAttr.OPTIONS: self._select_config.get_options(self._device),
        }

    async def _handle_select_command(  # pylint: disable=too-many-branches
        self,
        cmd_id: str,
        params: dict[str, Any] | None,
    ) -> Literal[StatusCodes.OK]:
        attributes = self._get_select_attributes()
        options = list(attributes.get(SelectAttr.OPTIONS, []))
        current_option = attributes.get(SelectAttr.CURRENT_OPTION)
        cycle = bool(params.get("cycle")) if params is not None else False

        target_option = None

        match cmd_id:
            case SelectCommands.SELECT_OPTION:
                target_option = params.get("option") if params is not None else None

            case SelectCommands.SELECT_FIRST:
                if options:
                    target_option = options[0]

            case SelectCommands.SELECT_LAST:
                if options:
                    target_option = options[-1]

            case SelectCommands.SELECT_NEXT:
                if current_option in options:
                    current_index = options.index(current_option)
                    if current_index < len(options) - 1:
                        target_option = options[current_index + 1]
                    elif cycle and options:
                        target_option = options[0]

            case SelectCommands.SELECT_PREVIOUS:
                if current_option in options:
                    current_index = options.index(current_option)
                    if current_index > 0:
                        target_option = options[current_index - 1]
                    elif cycle and options:
                        target_option = options[-1]

        if target_option is not None:
            device_value = self._select_config.map_option_to_device_value(
                self._device, str(target_option)
            )
            if device_value is not None:
                await self._device.send_raw(
                    self._select_config.command_template.format(device_value)
                )

        return StatusCodes.OK

    def map_entity_states(self, device_state: AwolValerionStates) -> States:
        """Convert a device-specific state to a UC API entity state."""
        return SELECT_STATE_MAPPING[device_state]

    async def sync_state(self) -> None:
        """Update the select attributes."""
        self.update(self._get_select_attributes())
