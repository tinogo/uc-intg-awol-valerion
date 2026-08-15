"""
Constants for the Integration.

This module contains constants used throughout the integration.

:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

from enum import StrEnum

from ucapi.media_player import States as MediaPlayerStates


class Loggers(StrEnum):
    """Defines the various logger types."""

    DRIVER = "driver"
    MEDIA_PLAYER = "media_player"
    DEVICE = "device"
    PJLINK = "pjlink"
    SETUP_FLOW = "setup_flow"


class AwolValerionStates(StrEnum):
    """Defines the possible states of the AWOL Valerion projector."""

    UNKNOWN = "UNKNOWN"
    UNAVAILABLE = "UNAVAILABLE"
    OFF = "OFF"
    ON = "ON"


# PJLink power reply codes (from ``%1POWR ?`` / ``%1POWR=<n>``)
# PJLink power reply codes (from ``%1POWR ?`` / ``%1POWR=<n>``)
PJLINK_POWER = {
    "0": AwolValerionStates.OFF,  # standby
    "1": AwolValerionStates.ON,  # lamp on
}

# PJLink AV-mute reply codes (``%1AVMT=<n>``): 30 off, 11/21/31 muted
AVMUTE_MUTED = {"11", "21", "31"}

# PJLink error-status positions for ``%1ERST=<6 chars>``
ERST_COMPONENTS = ("Fan", "Lamp", "Temperature", "Cover", "Filter", "Other")
ERST_LEVELS = {"0": "OK", "1": "Warning", "2": "Error"}

# PJLink input-code -> friendly name. INST reports which exist per device;
# type digit: 1=RGB 2=Video 3=Digital 4=Storage 5=Network.
PJLINK_INPUT_NAMES = {
    "30": "Home",
    "31": "HDMI 1",
    "32": "HDMI 2",
    "33": "HDMI 3",
}
PJLINK_INPUT_NAMES_INV = {v: k for k, v in PJLINK_INPUT_NAMES.items()}


class AwolValerionCommands(StrEnum):
    """Defines the possible commands of the AWOL Valerion projector."""

    POWER_ON = "%1POWR 1"
    POWER_OFF = "%1POWR 0"
    GET_POWER = "%1POWR ?"
    GET_INPUT = "%1INPT ?"
    SET_INPUT = "%1INPT {code}"
    GET_INPUT_LIST = "%1INST ?"
    GET_AVMUTE = "%1AVMT ?"
    SET_AVMUTE_ON = "%1AVMT 31"
    SET_AVMUTE_OFF = "%1AVMT 30"
    GET_ERRORS = "%1ERST ?"
    GET_NAME = "%1NAME ?"
    GET_MANUFACTURER = "%1INF1 ?"
    GET_PRODUCT = "%1INF2 ?"
    GET_OTHER_INFO = "%1INFO ?"
    GET_CLASS = "%2CLSS ?"
    GET_SW_VERSION = "%2SVER ?"
    GET_REC_RESOLUTION = "%2RRES ?"
    CURSOR_UP = "%3RCNC 0"
    CURSOR_DOWN = "%3RCNC 1"
    CURSOR_LEFT = "%3RCNC 2"
    CURSOR_RIGHT = "%3RCNC 3"
    CURSOR_OK = "%3RCNC 4"
    RETURN = "%3RCNC 5"
    MENU = "%3RCNC 6"
    SETTINGS = "%3RCNC 7"
    HOME = "%3RCNC 8"
    VOLUME_DOWN = "%2SVOL 0"
    VOLUME_UP = "%2SVOL 1"


MEDIA_PLAYER_STATE_MAPPING = {
    AwolValerionStates.ON: MediaPlayerStates.ON,
    AwolValerionStates.OFF: MediaPlayerStates.OFF,
    AwolValerionStates.UNAVAILABLE: MediaPlayerStates.UNAVAILABLE,
    AwolValerionStates.UNKNOWN: MediaPlayerStates.UNKNOWN,
}
