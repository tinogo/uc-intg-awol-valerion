"""
Select Entity.

:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import logging
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

_selects = {
    SelectType.COLOR_TEMPERATURE: "Color Temperature",
    SelectType.DYNAMIC_TONE_MAPPING: "Dynamic Tone Mapping",
    SelectType.EBL: "EBL",
    SelectType.GAMMA: "Gamma",
    SelectType.LASER_LUMINANCE: "Laser Luminance",
    SelectType.MOTION_ENHANCEMENT: "Motion Enhancement",
    SelectType.PICTURE_MODE: "Picture Mode",
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
        self._select_type = select_type
        self._entity_attribute_map: dict[SelectType, Callable] = {
            SelectType.COLOR_TEMPERATURE: self._get_color_temperature_select_attributes,
            SelectType.DYNAMIC_TONE_MAPPING: self._get_dynamic_tone_mapping_select_attributes,
            SelectType.EBL: self._get_ebl_select_attributes,
            SelectType.GAMMA: self._get_gamma_select_attributes,
            SelectType.LASER_LUMINANCE: self._get_laser_luminance_select_attributes,
            SelectType.MOTION_ENHANCEMENT: self._get_motion_enhancement_select_attributes,
            SelectType.PICTURE_MODE: self._get_picture_mode_select_attributes,
        }
        self._select_command_template_map: dict[SelectType, str] = {
            SelectType.COLOR_TEMPERATURE: AwolValerionCommands.SET_COLOR_TEMPERATURE,
            SelectType.DYNAMIC_TONE_MAPPING: AwolValerionCommands.SET_DYNAMIC_TONE_MAPPING,
            SelectType.EBL: AwolValerionCommands.SET_EBL,
            SelectType.GAMMA: AwolValerionCommands.SET_GAMMA,
            SelectType.LASER_LUMINANCE: AwolValerionCommands.SET_LASER_LUMINANCE,
            SelectType.MOTION_ENHANCEMENT: AwolValerionCommands.SET_MOTION_ENHANCEMENT,
            SelectType.PICTURE_MODE: AwolValerionCommands.SET_PICTURE_MODE,
        }

        select_config = self._get_select_config(select_type, device)

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
        select = {}
        select_entity_id = create_entity_id(
            EntityTypes.SELECT,
            device.identifier,
            select_type,
        )

        match select_type:
            case select_type if _selects.get(select_type) is not None:
                select = {
                    "identifier": select_entity_id,
                    "name": f"{device.name} Select: {_selects.get(select_type)}",
                    "attributes": self._device.get_device_attributes(select_entity_id),
                }

            case _:
                raise ValueError(f"Unsupported select type: {select_type}")
        return select

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

        command_template = self._select_command_template_map.get(self._select_type)
        if command_template is None:
            raise ValueError(f"Unsupported select type: {self._select_type}")

        return await self._handle_select_command(cmd_id, params, command_template)

    def _map_option_to_device_value(self, option: str) -> str | None:  # pylint: disable=too-many-return-statements
        """Map UI option labels to projector values for dict-backed select entities."""
        match self._select_type:
            case SelectType.COLOR_TEMPERATURE:
                return self._device.status.color_temperature_list.get(option)
            case SelectType.DYNAMIC_TONE_MAPPING:
                return self._device.status.dynamic_tone_mapping_list.get(option)
            case SelectType.EBL:
                return self._device.status.ebl_list.get(option)
            case SelectType.GAMMA:
                return self._device.status.gamma_list.get(option)
            case SelectType.LASER_LUMINANCE:
                return option
            case SelectType.MOTION_ENHANCEMENT:
                return self._device.status.motion_enhancement_list.get(option)
            case SelectType.PICTURE_MODE:
                return option
            case _:
                return None

    async def _handle_select_command(  # pylint: disable=too-many-branches
        self, cmd_id: str, params: dict[str, Any] | None, command_template: str
    ) -> Literal[StatusCodes.OK]:
        attributes = self._entity_attribute_map[self._select_type]()
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
            device_value = self._map_option_to_device_value(target_option)
            if device_value is not None:
                await self._device.send_raw(command_template.format(device_value))

        return StatusCodes.OK

    def map_entity_states(self, device_state: AwolValerionStates) -> States:
        """Convert a device-specific state to a UC API entity state."""
        return SELECT_STATE_MAPPING[device_state]

    async def sync_state(self) -> None:
        """Update the select attributes."""
        attributes = self._entity_attribute_map.get(self._select_type)
        if attributes is not None:
            self.update(attributes())
        else:
            raise ValueError(f"Unsupported select type: {self._select_type}")

    def _get_color_temperature_select_attributes(self) -> dict[str, Any]:
        """Get the color temperature select attributes."""
        return {
            SelectAttr.STATE: SELECT_STATE_MAPPING[self._device.state],
            SelectAttr.CURRENT_OPTION: self._device.status.color_temperature,
            SelectAttr.OPTIONS: list(self._device.status.color_temperature_list.keys()),
        }

    def _get_dynamic_tone_mapping_select_attributes(self) -> dict[str, Any]:
        """Get the dynamic tone mapping select attributes."""
        return {
            SelectAttr.STATE: SELECT_STATE_MAPPING[self._device.state],
            SelectAttr.CURRENT_OPTION: self._device.status.dynamic_tone_mapping,
            SelectAttr.OPTIONS: list(
                self._device.status.dynamic_tone_mapping_list.keys()
            ),
        }

    def _get_ebl_select_attributes(self) -> dict[str, Any]:
        """Get the EBL select attributes."""
        return {
            SelectAttr.STATE: SELECT_STATE_MAPPING[self._device.state],
            SelectAttr.CURRENT_OPTION: self._device.status.ebl,
            SelectAttr.OPTIONS: list(self._device.status.ebl_list.keys()),
        }

    def _get_gamma_select_attributes(self) -> dict[str, Any]:
        """Get the gamma select attributes."""
        return {
            SelectAttr.STATE: SELECT_STATE_MAPPING[self._device.state],
            SelectAttr.CURRENT_OPTION: self._device.status.gamma,
            SelectAttr.OPTIONS: list(self._device.status.gamma_list.keys()),
        }

    def _get_motion_enhancement_select_attributes(self) -> dict[str, Any]:
        """Get the motion enhancement select attributes."""
        return {
            SelectAttr.STATE: SELECT_STATE_MAPPING[self._device.state],
            SelectAttr.CURRENT_OPTION: self._device.status.motion_enhancement,
            SelectAttr.OPTIONS: list(
                self._device.status.motion_enhancement_list.keys()
            ),
        }

    def _get_laser_luminance_select_attributes(self) -> dict[str, Any]:
        """Get the laser luminance select attributes."""
        return {
            SelectAttr.STATE: SELECT_STATE_MAPPING[self._device.state],
            SelectAttr.CURRENT_OPTION: self._device.status.laser_luminance,
            SelectAttr.OPTIONS: list(range(0, 11)),
        }

    def _get_picture_mode_select_attributes(self) -> dict[str, Any]:
        """Get the picture mode select attributes."""
        return {
            SelectAttr.STATE: SELECT_STATE_MAPPING[self._device.state],
            SelectAttr.CURRENT_OPTION: self._device.status.picture_mode,
            SelectAttr.OPTIONS: self._device.status.picture_mode_list,
        }
