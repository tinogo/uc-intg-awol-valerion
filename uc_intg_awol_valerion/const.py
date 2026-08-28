"""
Constants for the Integration.

This module contains constants used throughout the integration.

:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

from enum import StrEnum


class Loggers(StrEnum):
    """Defines the various logger types."""

    DRIVER = "driver"
    MEDIA_PLAYER = "media_player"
    REMOTE = "remote"
    DEVICE = "device"
    PJLINK = "pjlink"
    SELECT = "select"
    SENSOR = "sensor"
    SETUP_FLOW = "setup_flow"


class SimpleCommands(StrEnum):
    """
    Additional simple commands not covered by standard media-player features.

    Simple commands appear in the UI as buttons the user can press.
    """

    VOLUME_UP = "VOLUME_UP"
    VOLUME_DOWN = "VOLUME_DOWN"
    MUTE_ON = "MUTE_ON"
    MUTE_OFF = "MUTE_OFF"
    MUTE_TOGGLE = "MUTE_TOGGLE"
    CURSOR_UP = "CURSOR_UP"
    CURSOR_DOWN = "CURSOR_DOWN"
    CURSOR_LEFT = "CURSOR_LEFT"
    CURSOR_RIGHT = "CURSOR_RIGHT"
    CURSOR_ENTER = "CURSOR_ENTER"
    BACK = "BACK"
    MENU = "MENU"
    SETTINGS = "SETTINGS"
    HOME = "HOME"


class AwolValerionStates(StrEnum):
    """Defines the possible states of the AWOL Valerion projector."""

    UNKNOWN = "UNKNOWN"
    UNAVAILABLE = "UNAVAILABLE"
    OFF = "OFF"
    ON = "ON"


class AwolValerionCommands(StrEnum):
    """Defines the possible commands of the AWOL Valerion projector."""

    GET_POWER = "%1POWR ?"
    GET_INPUT = "%1INPT ?"
    GET_AVMUTE = "%1AVMT ?"
    GET_NAME = "%1NAME ?"
    GET_MANUFACTURER = "%1INF1 ?"
    GET_PRODUCT = "%1INF2 ?"
    GET_OTHER_INFO = "%1INFO ?"
    GET_CLASS = "%2CLSS ?"
    GET_SW_VERSION = "%2SVER ?"
    GET_INPUT_RESOLUTION = "%2IRES ?"
    GET_ASPECT_RATIO = "%3ASPR ?"
    GET_COLOR_TEMPERATURE = "%3CLTP ?"
    GET_DYNAMIC_TONE_MAPPING = "%3DYTM ?"
    GET_EBL = "%3ENBL ?"
    GET_FAN_SPEED = "%3FANS ?"
    GET_GAMMA = "%3GAMA ?"
    GET_LASER_LUMINANCE = "%3LASL ?"
    GET_MOTION_ENHANCEMENT = "%3MOTN ?"
    GET_REC_RESOLUTION = "%2RRES ?"
    GET_PICTURE_MODE = "%3PICT ?"
    GET_PICTURE_MODE_LIST = "%3PICL ?"
    GET_SIGNAL_INFO = "%3SINF ?"
    GET_TEMPERATURE = "%3TEMP ?"
    GET_VOLUME = "%3VOLM ?"
    SET_COLOR_TEMPERATURE = "%3CLTP {}"
    SET_DYNAMIC_TONE_MAPPING = "%3DYTM {}"
    SET_EBL = "%3ENBL {}"
    SET_GAMMA = "%3GAMA {}"
    SET_LASER_LUMINANCE = "%3LASL {}"
    SET_MOTION_ENHANCEMENT = "%3MOTN {}"
    SET_PICTURE_MODE = "%3PICT {}"
    SET_POWER_ON = "%1POWR 1"
    SET_POWER_OFF = "%1POWR 0"
    SET_INPUT = "%1INPT {code}"
    SET_MUTE_ON = "%1AVMT 21"
    SET_MUTE_OFF = "%1AVMT 20"
    SET_CURSOR_UP = "%3RCNC 0"
    SET_CURSOR_DOWN = "%3RCNC 1"
    SET_CURSOR_LEFT = "%3RCNC 2"
    SET_CURSOR_RIGHT = "%3RCNC 3"
    SET_CURSOR_OK = "%3RCNC 4"
    SET_RETURN = "%3RCNC 5"
    SET_MENU = "%3RCNC 6"
    SET_SETTINGS = "%3RCNC 7"
    SET_HOME = "%3RCNC 8"
    SET_VOLUME_DOWN = "%2SVOL 0"
    SET_VOLUME_UP = "%2SVOL 1"
    SET_VOLUME_X_FORMAT = "%3VOLM {}"
