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


class AwolValerionCommands(StrEnum):
    """Defines the possible commands of the AWOL Valerion projector."""

    POWER_ON = "%1POWR 1"
    POWER_OFF = "%1POWR 0"
    GET_POWER = "%1POWR ?"
    GET_INPUT = "%1INPT ?"
    SET_INPUT = "%1INPT {code}"
    GET_AVMUTE = "%1AVMT ?"
    SET_AVMUTE_ON = "%1AVMT 31"
    SET_AVMUTE_OFF = "%1AVMT 30"
    GET_NAME = "%1NAME ?"
    GET_MANUFACTURER = "%1INF1 ?"
    GET_PRODUCT = "%1INF2 ?"
    GET_OTHER_INFO = "%1INFO ?"
    GET_CLASS = "%2CLSS ?"
    GET_SW_VERSION = "%2SVER ?"
    GET_REC_RESOLUTION = "%2RRES ?"
    GET_VOLUME = "%3VOLM ?"
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
    VOLUME_X_FORMAT = "%3VOLM {}"


MEDIA_PLAYER_STATE_MAPPING = {
    AwolValerionStates.ON: MediaPlayerStates.ON,
    AwolValerionStates.OFF: MediaPlayerStates.OFF,
    AwolValerionStates.UNAVAILABLE: MediaPlayerStates.UNAVAILABLE,
    AwolValerionStates.UNKNOWN: MediaPlayerStates.UNKNOWN,
}
