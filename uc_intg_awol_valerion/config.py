"""
Configuration for the Integration.

This module contains the configuration dataclass

:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

from dataclasses import dataclass


@dataclass
class AwolValerionConfig:
    """
    Device configuration dataclass.

    This dataclass holds all the configuration needed to connect to and
    identify a device.
    """

    identifier: str
    """Unique identifier of the device (e.g., MAC address, serial number)."""

    name: str
    """Friendly name of the device for display purposes."""

    address: str
    """IP address or hostname of the device."""

    port: int
    """Port number for device communication."""

    password: str = ""
    """Optional password for device authentication."""
