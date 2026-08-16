"""
Sensor Entity.

:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import logging
from typing import Any, Callable

from ucapi import EntityTypes, Sensor
from ucapi.sensor import Attributes as SensorAttr
from ucapi.sensor import DeviceClasses, States
from ucapi_framework import Entity, create_entity_id

from uc_intg_awol_valerion.const import (
    SENSOR_STATE_MAPPING,
    Loggers,
    SensorType,
)
from uc_intg_awol_valerion.device import AwolValerionDevice

_LOG = logging.getLogger(Loggers.SENSOR)

_simple_custom_sensors = {
    SensorType.SOURCE: "Source",
    SensorType.VOLUME: "Volume",
    SensorType.INPUT_RESOLUTION: "Input Resolution",
    SensorType.RECOMMENDED_RESOLUTION: "Recommended Resolution",
    SensorType.ASPECT_RATIO: "Aspect Ratio",
    SensorType.COLOR_TEMPERATURE: "Color Temperature",
    SensorType.DYNAMIC_TONE_MAPPING: "Dynamic Tone Mapping",
    SensorType.EBL: "EBL",
    SensorType.FAN_SPEED: "Fan Speed",
    SensorType.GAMMA: "Gamma",
    SensorType.LASER_LUMINANCE: "Laser Luminance",
    SensorType.MOTION_ENHANCEMENT: "Motion Enhancement",
    SensorType.PICTURE_MODE: "Picture Mode",
    SensorType.SIGNAL_INFO: "Signal Info",
    SensorType.TEMPERATURE: "Temperature",
}

_binary_sensors = {
    SensorType.MUTE: "Mute",
}


class AwolValerionSensor(Sensor, Entity):  # pylint: disable=too-few-public-methods
    """Sensor for the AWOL Valerion projectors."""

    def __init__(self, device: AwolValerionDevice, sensor_type: SensorType):
        """Initialize the sensor entity."""
        self._device = device
        self._sensor_type = sensor_type
        self._entity_attribute_map: dict[SensorType, Callable] = {
            SensorType.MUTE: self._get_mute_sensor_attributes,
            SensorType.SOURCE: self._get_source_sensor_attributes,
            SensorType.VOLUME: self._get_volume_sensor_attributes,
            SensorType.INPUT_RESOLUTION: self._get_input_resolution_sensor_attributes,
            SensorType.RECOMMENDED_RESOLUTION: self._get_recommended_resolution_sensor_attributes,
            SensorType.ASPECT_RATIO: self._get_aspect_ratio_sensor_attributes,
            SensorType.COLOR_TEMPERATURE: self._get_color_temperature_sensor_attributes,
            SensorType.DYNAMIC_TONE_MAPPING: self._get_dynamic_tone_mapping_sensor_attributes,
            SensorType.EBL: self._get_ebl_sensor_attributes,
            SensorType.FAN_SPEED: self._get_fan_speed_sensor_attributes,
            SensorType.GAMMA: self._get_gamma_sensor_attributes,
            SensorType.LASER_LUMINANCE: self._get_laser_luminance_sensor_attributes,
            SensorType.MOTION_ENHANCEMENT: self._get_motion_enhancement_sensor_attributes,
            SensorType.PICTURE_MODE: self._get_picture_mode_sensor_attributes,
            SensorType.SIGNAL_INFO: self._get_signal_info_sensor_attributes,
            SensorType.TEMPERATURE: self._get_temperature_sensor_attributes,
        }

        sensor_config = self._get_sensor_config(sensor_type, device)

        _LOG.debug("Initializing sensor: %s", sensor_config["identifier"])

        super().__init__(
            identifier=sensor_config["identifier"],
            name=sensor_config["name"],
            features=[],
            attributes=sensor_config["attributes"],
            device_class=sensor_config["device_class"],
            options=sensor_config.get("options", {}),
        )

        self.subscribe_to_device(device)

    def _get_sensor_config(
        self, sensor_type: SensorType, device: AwolValerionDevice
    ) -> dict[str, Any]:
        """Get sensor configuration based on type."""
        sensor = {}
        sensor_entity_id = create_entity_id(
            EntityTypes.SENSOR,
            device.identifier,
            sensor_type,
        )

        match sensor_type:
            case sensor_type if _simple_custom_sensors.get(sensor_type) is not None:
                sensor = {
                    "identifier": sensor_entity_id,
                    "name": f"{device.name} Sensor: {_simple_custom_sensors.get(sensor_type)}",
                    "device_class": DeviceClasses.CUSTOM,
                    "attributes": self._device.get_device_attributes(sensor_entity_id),
                }

            case sensor_type if _binary_sensors.get(sensor_type) is not None:
                sensor = {
                    "identifier": sensor_entity_id,
                    "name": f"{device.name} Sensor: {_binary_sensors.get(sensor_type)}",
                    "device_class": DeviceClasses.BINARY,
                    "attributes": self._device.get_device_attributes(sensor_entity_id),
                }

            case _:
                raise ValueError(f"Unsupported sensor type: {sensor_type}")
        return sensor

    def map_entity_states(self, device_state: AwolValerionDevice) -> States:
        """Convert a device-specific state to a UC API entity state."""
        return SENSOR_STATE_MAPPING[device_state]

    async def sync_state(self) -> None:
        """Update the sensor attributes."""
        attributes = self._entity_attribute_map.get(self._sensor_type)
        if attributes is not None:
            self.update(attributes())
        else:
            raise ValueError(f"Unsupported sensor type: {self._sensor_type}")

    def _get_mute_sensor_attributes(self) -> dict[str, Any]:
        """Get the mute sensor attributes."""
        return {
            SensorAttr.STATE: SENSOR_STATE_MAPPING[self._device.state],
            SensorAttr.VALUE: "on" if self._device.status.muted else "off",
            SensorAttr.UNIT: "sound",
        }

    def _get_source_sensor_attributes(self) -> dict[str, Any]:
        """Get the source sensor attributes."""
        return {
            SensorAttr.STATE: SENSOR_STATE_MAPPING[self._device.state],
            SensorAttr.VALUE: self._device.status.input,
        }

    def _get_volume_sensor_attributes(self) -> dict[str, Any]:
        """Get the volume sensor attributes."""
        return {
            SensorAttr.STATE: SENSOR_STATE_MAPPING[self._device.state],
            SensorAttr.VALUE: str(self._device.status.volume),
        }

    def _get_input_resolution_sensor_attributes(self) -> dict[str, Any]:
        """Get the input resolution sensor attributes."""
        return {
            SensorAttr.STATE: SENSOR_STATE_MAPPING[self._device.state],
            SensorAttr.VALUE: str(self._device.status.input_resolution),
        }

    def _get_recommended_resolution_sensor_attributes(self) -> dict[str, Any]:
        """Get the recommended resolution sensor attributes."""
        return {
            SensorAttr.STATE: SENSOR_STATE_MAPPING[self._device.state],
            SensorAttr.VALUE: str(self._device.identity.rec_resolution),
        }

    def _get_aspect_ratio_sensor_attributes(self) -> dict[str, Any]:
        """Get the aspect ratio sensor attributes."""
        return {
            SensorAttr.STATE: SENSOR_STATE_MAPPING[self._device.state],
            SensorAttr.VALUE: str(self._device.status.aspect_ratio),
        }

    def _get_color_temperature_sensor_attributes(self) -> dict[str, Any]:
        """Get the color temperature sensor attributes."""
        return {
            SensorAttr.STATE: SENSOR_STATE_MAPPING[self._device.state],
            SensorAttr.VALUE: str(self._device.status.color_temperature),
        }

    def _get_dynamic_tone_mapping_sensor_attributes(self) -> dict[str, Any]:
        """Get the dynamic tone mapping sensor attributes."""
        return {
            SensorAttr.STATE: SENSOR_STATE_MAPPING[self._device.state],
            SensorAttr.VALUE: str(self._device.status.dynamic_tone_mapping),
        }

    def _get_ebl_sensor_attributes(self) -> dict[str, Any]:
        """Get the EBL sensor attributes."""
        return {
            SensorAttr.STATE: SENSOR_STATE_MAPPING[self._device.state],
            SensorAttr.VALUE: str(self._device.status.ebl),
        }

    def _get_fan_speed_sensor_attributes(self) -> dict[str, Any]:
        """Get the fan speed sensor attributes."""
        return {
            SensorAttr.STATE: SENSOR_STATE_MAPPING[self._device.state],
            SensorAttr.VALUE: str(self._device.status.fan_speed_display),
        }

    def _get_gamma_sensor_attributes(self) -> dict[str, Any]:
        """Get the gamma sensor attributes."""
        return {
            SensorAttr.STATE: SENSOR_STATE_MAPPING[self._device.state],
            SensorAttr.VALUE: str(self._device.status.gamma),
        }

    def _get_laser_luminance_sensor_attributes(self) -> dict[str, Any]:
        """Get the laser luminance sensor attributes."""
        return {
            SensorAttr.STATE: SENSOR_STATE_MAPPING[self._device.state],
            SensorAttr.VALUE: str(self._device.status.laser_luminance),
        }

    def _get_motion_enhancement_sensor_attributes(self) -> dict[str, Any]:
        """Get the motion enhancement sensor attributes."""
        return {
            SensorAttr.STATE: SENSOR_STATE_MAPPING[self._device.state],
            SensorAttr.VALUE: str(self._device.status.motion_enhancement),
        }

    def _get_picture_mode_sensor_attributes(self) -> dict[str, Any]:
        """Get the picture mode sensor attributes."""
        return {
            SensorAttr.STATE: SENSOR_STATE_MAPPING[self._device.state],
            SensorAttr.VALUE: str(self._device.status.picture_mode),
        }

    def _get_signal_info_sensor_attributes(self) -> dict[str, Any]:
        """Get the signal info sensor attributes."""
        return {
            SensorAttr.STATE: SENSOR_STATE_MAPPING[self._device.state],
            SensorAttr.VALUE: str(self._device.status.signal_info),
        }

    def _get_temperature_sensor_attributes(self) -> dict[str, Any]:
        """Get the temperature sensor attributes."""
        return {
            SensorAttr.STATE: SENSOR_STATE_MAPPING[self._device.state],
            SensorAttr.VALUE: str(self._device.status.temperature),
        }
