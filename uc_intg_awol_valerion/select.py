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
            SelectType.MOTION_ENHANCEMENT: self._get_motion_enhancement_select_attributes,
            SelectType.PICTURE_MODE: self._get_picture_mode_select_attributes,
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

        match self._select_type:
            case SelectType.COLOR_TEMPERATURE:
                return await self._handle_color_temperature_command(cmd_id, params)

            case SelectType.DYNAMIC_TONE_MAPPING:
                return await self._handle_dynamic_tone_mapping_command(cmd_id, params)

            case SelectType.EBL:
                return await self._handle_ebl_command(cmd_id, params)

            case SelectType.GAMMA:
                return await self._handle_gamma_command(cmd_id, params)

            case SelectType.MOTION_ENHANCEMENT:
                return await self._handle_motion_enhancement_command(cmd_id, params)

            case SelectType.PICTURE_MODE:
                return await self._handle_picture_mode_command(cmd_id, params)

    async def _handle_color_temperature_command(
        self, cmd_id: str, params: dict[str, Any] | None
    ) -> Literal[StatusCodes.OK]:
        color_temperature_list = list(self._device.status.color_temperature_list.keys())
        match cmd_id:
            case SelectCommands.SELECT_OPTION:
                await self._device.send_raw(
                    AwolValerionCommands.SET_COLOR_TEMPERATURE.format(params["option"])
                )

            case SelectCommands.SELECT_FIRST:
                first_color_temperature_name = color_temperature_list[0]
                await self._device.send_raw(
                    AwolValerionCommands.SET_COLOR_TEMPERATURE.format(
                        first_color_temperature_name
                    )
                )

            case SelectCommands.SELECT_LAST:
                last_color_temperature_name = color_temperature_list[-1]
                await self._device.send_raw(
                    AwolValerionCommands.SET_COLOR_TEMPERATURE.format(
                        last_color_temperature_name
                    )
                )

            case SelectCommands.SELECT_NEXT:
                current_index = color_temperature_list.index(
                    self._device.status.color_temperature
                )
                if current_index < len(color_temperature_list) - 1:
                    next_color_temperature_name = color_temperature_list[
                        current_index + 1
                    ]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_COLOR_TEMPERATURE.format(
                            next_color_temperature_name
                        )
                    )
                elif params["cycle"]:
                    next_color_temperature_name = color_temperature_list[0]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_COLOR_TEMPERATURE.format(
                            next_color_temperature_name
                        )
                    )

            case SelectCommands.SELECT_PREVIOUS:
                current_index = color_temperature_list.index(
                    self._device.status.color_temperature
                )
                if current_index > 0:
                    previous_color_temperature_name = color_temperature_list[
                        current_index - 1
                    ]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_COLOR_TEMPERATURE.format(
                            previous_color_temperature_name
                        )
                    )
                elif params["cycle"]:
                    previous_color_temperature_name = color_temperature_list[
                        len(color_temperature_list)
                    ]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_COLOR_TEMPERATURE.format(
                            previous_color_temperature_name
                        )
                    )

        return StatusCodes.OK

    async def _handle_dynamic_tone_mapping_command(
        self, cmd_id: str, params: dict[str, Any] | None
    ) -> Literal[StatusCodes.OK]:
        dynamic_tone_mapping_list = list(
            self._device.status.dynamic_tone_mapping_list.keys()
        )
        match cmd_id:
            case SelectCommands.SELECT_OPTION:
                await self._device.send_raw(
                    AwolValerionCommands.SET_DYNAMIC_TONE_MAPPING.format(
                        params["option"]
                    )
                )

            case SelectCommands.SELECT_FIRST:
                first_dynamic_tone_mapping_name = dynamic_tone_mapping_list[0]
                await self._device.send_raw(
                    AwolValerionCommands.SET_DYNAMIC_TONE_MAPPING.format(
                        first_dynamic_tone_mapping_name
                    )
                )

            case SelectCommands.SELECT_LAST:
                last_dynamic_tone_mapping_name = dynamic_tone_mapping_list[-1]
                await self._device.send_raw(
                    AwolValerionCommands.SET_DYNAMIC_TONE_MAPPING.format(
                        last_dynamic_tone_mapping_name
                    )
                )

            case SelectCommands.SELECT_NEXT:
                current_index = dynamic_tone_mapping_list.index(
                    self._device.status.dynamic_tone_mapping
                )
                if current_index < len(dynamic_tone_mapping_list) - 1:
                    next_dynamic_tone_mapping_name = dynamic_tone_mapping_list[
                        current_index + 1
                    ]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_DYNAMIC_TONE_MAPPING.format(
                            next_dynamic_tone_mapping_name
                        )
                    )
                elif params["cycle"]:
                    next_dynamic_tone_mapping_name = dynamic_tone_mapping_list[0]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_DYNAMIC_TONE_MAPPING.format(
                            next_dynamic_tone_mapping_name
                        )
                    )

            case SelectCommands.SELECT_PREVIOUS:
                current_index = dynamic_tone_mapping_list.index(
                    self._device.status.dynamic_tone_mapping
                )
                if current_index > 0:
                    previous_dynamic_tone_mapping_name = dynamic_tone_mapping_list[
                        current_index - 1
                    ]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_DYNAMIC_TONE_MAPPING.format(
                            previous_dynamic_tone_mapping_name
                        )
                    )
                elif params["cycle"]:
                    previous_dynamic_tone_mapping_name = dynamic_tone_mapping_list[
                        len(dynamic_tone_mapping_list)
                    ]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_DYNAMIC_TONE_MAPPING.format(
                            previous_dynamic_tone_mapping_name
                        )
                    )

        return StatusCodes.OK

    async def _handle_ebl_command(
        self, cmd_id: str, params: dict[str, Any] | None
    ) -> Literal[StatusCodes.OK]:
        ebl_list = list(self._device.status.ebl_list.keys())
        match cmd_id:
            case SelectCommands.SELECT_OPTION:
                await self._device.send_raw(
                    AwolValerionCommands.SET_EBL.format(params["option"])
                )

            case SelectCommands.SELECT_FIRST:
                first_ebl_name = ebl_list[0]
                await self._device.send_raw(
                    AwolValerionCommands.SET_EBL.format(first_ebl_name)
                )

            case SelectCommands.SELECT_LAST:
                last_ebl_name = ebl_list[-1]
                await self._device.send_raw(
                    AwolValerionCommands.SET_EBL.format(last_ebl_name)
                )

            case SelectCommands.SELECT_NEXT:
                current_index = ebl_list.index(self._device.status.ebl)
                if current_index < len(ebl_list) - 1:
                    next_ebl_name = ebl_list[current_index + 1]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_EBL.format(next_ebl_name)
                    )
                elif params["cycle"]:
                    next_ebl_name = ebl_list[0]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_EBL.format(next_ebl_name)
                    )

            case SelectCommands.SELECT_PREVIOUS:
                current_index = ebl_list.index(self._device.status.ebl)
                if current_index > 0:
                    previous_ebl_name = ebl_list[current_index - 1]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_EBL.format(previous_ebl_name)
                    )
                elif params["cycle"]:
                    previous_ebl_name = ebl_list[len(ebl_list)]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_EBL.format(previous_ebl_name)
                    )

        return StatusCodes.OK

    async def _handle_gamma_command(
        self, cmd_id: str, params: dict[str, Any] | None
    ) -> Literal[StatusCodes.OK]:
        gamma_list = list(self._device.status.gamma_list.keys())
        match cmd_id:
            case SelectCommands.SELECT_OPTION:
                await self._device.send_raw(
                    AwolValerionCommands.SET_GAMMA.format(params["option"])
                )

            case SelectCommands.SELECT_FIRST:
                first_gamma_name = gamma_list[0]
                await self._device.send_raw(
                    AwolValerionCommands.SET_GAMMA.format(first_gamma_name)
                )

            case SelectCommands.SELECT_LAST:
                last_gamma_name = gamma_list[-1]
                await self._device.send_raw(
                    AwolValerionCommands.SET_GAMMA.format(last_gamma_name)
                )

            case SelectCommands.SELECT_NEXT:
                current_index = gamma_list.index(self._device.status.gamma)
                if current_index < len(gamma_list) - 1:
                    next_gamma_name = gamma_list[current_index + 1]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_GAMMA.format(next_gamma_name)
                    )
                elif params["cycle"]:
                    next_gamma_name = gamma_list[0]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_GAMMA.format(next_gamma_name)
                    )

            case SelectCommands.SELECT_PREVIOUS:
                current_index = gamma_list.index(self._device.status.gamma)
                if current_index > 0:
                    previous_gamma_name = gamma_list[current_index - 1]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_GAMMA.format(previous_gamma_name)
                    )
                elif params["cycle"]:
                    previous_gamma_name = gamma_list[len(gamma_list)]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_GAMMA.format(previous_gamma_name)
                    )

        return StatusCodes.OK

    async def _handle_motion_enhancement_command(
        self, cmd_id: str, params: dict[str, Any] | None
    ) -> Literal[StatusCodes.OK]:
        motion_enhancement_list = list(
            self._device.status.motion_enhancement_list.keys()
        )
        match cmd_id:
            case SelectCommands.SELECT_OPTION:
                await self._device.send_raw(
                    AwolValerionCommands.SET_MOTION_ENHANCEMENT.format(params["option"])
                )

            case SelectCommands.SELECT_FIRST:
                first_motion_enhancement_name = motion_enhancement_list[0]
                await self._device.send_raw(
                    AwolValerionCommands.SET_MOTION_ENHANCEMENT.format(
                        first_motion_enhancement_name
                    )
                )

            case SelectCommands.SELECT_LAST:
                last_motion_enhancement_name = motion_enhancement_list[-1]
                await self._device.send_raw(
                    AwolValerionCommands.SET_MOTION_ENHANCEMENT.format(
                        last_motion_enhancement_name
                    )
                )

            case SelectCommands.SELECT_NEXT:
                current_index = motion_enhancement_list.index(
                    self._device.status.motion_enhancement
                )
                if current_index < len(motion_enhancement_list) - 1:
                    next_motion_enhancement_name = motion_enhancement_list[
                        current_index + 1
                    ]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_MOTION_ENHANCEMENT.format(
                            next_motion_enhancement_name
                        )
                    )
                elif params["cycle"]:
                    next_motion_enhancement_name = motion_enhancement_list[0]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_MOTION_ENHANCEMENT.format(
                            next_motion_enhancement_name
                        )
                    )

            case SelectCommands.SELECT_PREVIOUS:
                current_index = motion_enhancement_list.index(
                    self._device.status.motion_enhancement
                )
                if current_index > 0:
                    previous_motion_enhancement_name = motion_enhancement_list[
                        current_index - 1
                    ]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_MOTION_ENHANCEMENT.format(
                            previous_motion_enhancement_name
                        )
                    )
                elif params["cycle"]:
                    previous_motion_enhancement_name = motion_enhancement_list[
                        len(motion_enhancement_list)
                    ]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_MOTION_ENHANCEMENT.format(
                            previous_motion_enhancement_name
                        )
                    )

        return StatusCodes.OK

    async def _handle_picture_mode_command(
        self, cmd_id: str, params: dict[str, Any] | None
    ) -> Literal[StatusCodes.OK]:
        picture_mode_list = self._device.status.picture_mode_list
        match cmd_id:
            case SelectCommands.SELECT_OPTION:
                await self._device.send_raw(
                    AwolValerionCommands.SET_PICTURE_MODE.format(params["option"])
                )

            case SelectCommands.SELECT_FIRST:
                first_picture_mode_name = picture_mode_list[0]
                await self._device.send_raw(
                    AwolValerionCommands.SET_PICTURE_MODE.format(
                        first_picture_mode_name
                    )
                )

            case SelectCommands.SELECT_LAST:
                last_picture_mode_name = picture_mode_list[-1]
                await self._device.send_raw(
                    AwolValerionCommands.SET_PICTURE_MODE.format(last_picture_mode_name)
                )

            case SelectCommands.SELECT_NEXT:
                current_index = picture_mode_list.index(
                    self._device.status.picture_mode
                )
                if current_index < len(picture_mode_list) - 1:
                    next_picture_mode_name = picture_mode_list[current_index + 1]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_PICTURE_MODE.format(
                            next_picture_mode_name
                        )
                    )
                elif params["cycle"]:
                    next_picture_mode_name = picture_mode_list[0]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_PICTURE_MODE.format(
                            next_picture_mode_name
                        )
                    )

            case SelectCommands.SELECT_PREVIOUS:
                current_index = picture_mode_list.index(
                    self._device.status.picture_mode
                )
                if current_index > 0:
                    previous_picture_mode_name = picture_mode_list[current_index - 1]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_PICTURE_MODE.format(
                            previous_picture_mode_name
                        )
                    )
                elif params["cycle"]:
                    previous_picture_mode_name = picture_mode_list[
                        len(picture_mode_list)
                    ]
                    await self._device.send_raw(
                        AwolValerionCommands.SET_PICTURE_MODE.format(
                            previous_picture_mode_name
                        )
                    )

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

    def _get_picture_mode_select_attributes(self) -> dict[str, Any]:
        """Get the picture mode select attributes."""
        return {
            SelectAttr.STATE: SELECT_STATE_MAPPING[self._device.state],
            SelectAttr.CURRENT_OPTION: self._device.status.picture_mode,
            SelectAttr.OPTIONS: self._device.status.picture_mode_list,
        }
