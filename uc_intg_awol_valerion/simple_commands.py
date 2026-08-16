"""
This module provides a map of simple commands to their corresponding methods in the device.

:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

from typing import Callable

from uc_intg_awol_valerion.const import (
    SimpleCommands,
)
from uc_intg_awol_valerion.device import AwolValerionDevice


def get_simple_command_map(device: AwolValerionDevice) -> dict[str, Callable]:
    """Return a map of simple commands to their corresponding methods in the device."""
    return {
        SimpleCommands.VOLUME_UP.value: device.volume_up,
        SimpleCommands.VOLUME_DOWN.value: device.volume_down,
        SimpleCommands.MUTE_ON.value: device.mute_on,
        SimpleCommands.MUTE_OFF.value: device.mute_off,
        SimpleCommands.MUTE_TOGGLE.value: device.mute_toggle,
        SimpleCommands.CURSOR_UP.value: device.cursor_up,
        SimpleCommands.CURSOR_DOWN.value: device.cursor_down,
        SimpleCommands.CURSOR_LEFT.value: device.cursor_left,
        SimpleCommands.CURSOR_RIGHT.value: device.cursor_right,
        SimpleCommands.CURSOR_ENTER.value: device.cursor_enter,
        SimpleCommands.BACK.value: device.back,
        SimpleCommands.HOME.value: device.home,
        SimpleCommands.MENU.value: device.menu,
        SimpleCommands.SETTINGS.value: device.settings,
    }
