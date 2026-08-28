"""
Sensor Entity.

:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import logging
from dataclasses import dataclass
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


@dataclass(frozen=True)
class SensorConfig:
    """Configuration for one sensor type."""

    label: str
    device_class: str
    value_getter: Callable[[AwolValerionDevice], Any]
    unit: str | None = None


SENSOR_CONFIGS: dict[SensorType, SensorConfig] = {
    SensorType.MUTE: SensorConfig(
        label="Mute",
        device_class=DeviceClasses.BINARY,
        value_getter=lambda device: "on" if device.status.muted else "off",
        unit="sound",
    ),
    SensorType.SOURCE: SensorConfig(
        label="Source",
        device_class=DeviceClasses.CUSTOM,
        value_getter=lambda device: device.status.input,
    ),
    SensorType.VOLUME: SensorConfig(
        label="Volume",
        device_class=DeviceClasses.CUSTOM,
        value_getter=lambda device: str(device.status.volume),
    ),
    SensorType.INPUT_RESOLUTION: SensorConfig(
        label="Input Resolution",
        device_class=DeviceClasses.CUSTOM,
        value_getter=lambda device: str(device.status.input_resolution),
    ),
    SensorType.RECOMMENDED_RESOLUTION: SensorConfig(
        label="Recommended Resolution",
        device_class=DeviceClasses.CUSTOM,
        value_getter=lambda device: str(device.identity.rec_resolution),
    ),
    SensorType.ASPECT_RATIO: SensorConfig(
        label="Aspect Ratio",
        device_class=DeviceClasses.CUSTOM,
        value_getter=lambda device: str(device.status.aspect_ratio),
    ),
    SensorType.COLOR_TEMPERATURE: SensorConfig(
        label="Color Temperature",
        device_class=DeviceClasses.CUSTOM,
        value_getter=lambda device: str(device.status.color_temperature),
    ),
    SensorType.DYNAMIC_TONE_MAPPING: SensorConfig(
        label="Dynamic Tone Mapping",
        device_class=DeviceClasses.CUSTOM,
        value_getter=lambda device: str(device.status.dynamic_tone_mapping),
    ),
    SensorType.EBL: SensorConfig(
        label="EBL",
        device_class=DeviceClasses.CUSTOM,
        value_getter=lambda device: str(device.status.ebl),
    ),
    SensorType.FAN_SPEED: SensorConfig(
        label="Fan Speed",
        device_class=DeviceClasses.CUSTOM,
        value_getter=lambda device: str(device.status.fan_speed_display),
    ),
    SensorType.GAMMA: SensorConfig(
        label="Gamma",
        device_class=DeviceClasses.CUSTOM,
        value_getter=lambda device: str(device.status.gamma),
    ),
    SensorType.LASER_LUMINANCE: SensorConfig(
        label="Laser Luminance",
        device_class=DeviceClasses.CUSTOM,
        value_getter=lambda device: str(device.status.laser_luminance),
    ),
    SensorType.MOTION_ENHANCEMENT: SensorConfig(
        label="Motion Enhancement",
        device_class=DeviceClasses.CUSTOM,
        value_getter=lambda device: str(device.status.motion_enhancement),
    ),
    SensorType.PICTURE_MODE: SensorConfig(
        label="Picture Mode",
        device_class=DeviceClasses.CUSTOM,
        value_getter=lambda device: str(device.status.picture_mode),
    ),
    SensorType.SIGNAL_INFO: SensorConfig(
        label="Signal Info",
        device_class=DeviceClasses.CUSTOM,
        value_getter=lambda device: str(device.status.signal_info),
    ),
    SensorType.TEMPERATURE: SensorConfig(
        label="Temperature",
        device_class=DeviceClasses.CUSTOM,
        value_getter=lambda device: str(device.status.temperature_display),
    ),
}


class AwolValerionSensor(Sensor, Entity):  # pylint: disable=too-few-public-methods
    """Sensor for the AWOL Valerion projectors."""

    def __init__(self, device: AwolValerionDevice, sensor_type: SensorType):
        """Initialize the sensor entity."""
        self._device = device
        sensor_config = self._get_sensor_config(sensor_type, device)
        self._sensor_config: SensorConfig = sensor_config["sensor_config"]

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
        sensor_entity_id = create_entity_id(
            EntityTypes.SENSOR,
            device.identifier,
            sensor_type,
        )

        config = SENSOR_CONFIGS.get(sensor_type)
        if config is None:
            raise ValueError(f"Unsupported sensor type: {sensor_type}")

        return {
            "identifier": sensor_entity_id,
            "name": f"{device.name} Sensor: {config.label}",
            "device_class": config.device_class,
            "attributes": self._device.get_device_attributes(sensor_entity_id),
            "sensor_config": config,
        }

    def map_entity_states(self, device_state: AwolValerionDevice) -> States:
        """Convert a device-specific state to a UC API entity state."""
        return SENSOR_STATE_MAPPING[device_state]

    async def sync_state(self) -> None:
        """Update the sensor attributes."""
        self.update(self._get_sensor_attributes())

    def _get_sensor_attributes(self) -> dict[str, Any]:
        """Build UC API attributes from the active sensor config."""
        attributes = {
            SensorAttr.STATE: SENSOR_STATE_MAPPING[self._device.state],
            SensorAttr.VALUE: self._sensor_config.value_getter(self._device),
        }
        if self._sensor_config.unit is not None:
            attributes[SensorAttr.UNIT] = self._sensor_config.unit
        return attributes
