"""
Setup Flow Module.

This module handles the device setup and configuration process. It provides
forms for manual device entry and validation of device connections.

:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import logging
from typing import Any

from ucapi import IntegrationSetupError, RequestUserInput, SetupError
from ucapi_framework import BaseSetupFlow, DiscoveredDevice

from uc_intg_awol_valerion import transport
from uc_intg_awol_valerion.config import AwolValerionConfig
from uc_intg_awol_valerion.const import Loggers
from uc_intg_awol_valerion.pjlink import PJLinkTransport
from uc_intg_awol_valerion.transport import ProjectorIdentity, TransportAuthError

_LOG = logging.getLogger(Loggers.SETUP_FLOW)

# This form is displayed when the user chooses manual device entry
_MANUAL_INPUT_SCHEMA = RequestUserInput(
    {"en": "AWOL Valerion Setup"},
    [
        {
            "id": "info",
            "label": {
                "en": "Setup your AWOL Valerion projector",
                "de": "Einrichtung deines AWOL Valerion Projektors",
            },
            "field": {
                "label": {
                    "value": {
                        "en": (
                            "Please enter the IP Address or hostname of your AWOL Valerion projector."
                        ),
                        "de": (
                            "Bitte gebe die IP-Adresse oder den Hostnamen deines AWOL Valerion Projektors an."
                        ),
                    }
                }
            },
        },
        {
            "field": {"text": {"value": ""}},
            "id": "address",
            "label": {
                "en": "IP Address or hostname",
                "de": "IP-Adresse oder Hostname",
            },
        },
        {
            "field": {"number": {"value": 4352}},
            "id": "port",
            "label": {
                "en": "Port",
                "de": "Port",
            },
        },
        {
            "field": {"password": {"value": ""}},
            "id": "password",
            "label": {
                "en": "Optional password of the AWOL-Link connection",
                "de": "Optionales Passwort der AWOL-Link Verbindung",
            },
        },
    ],
)


class AwolValerionSetupFlow(BaseSetupFlow[AwolValerionConfig]):
    """
    Setup flow for device integration.

    Handles device configuration through manual entry.
    Extend this class to add custom setup logic for your device.
    """

    def get_manual_entry_form(self) -> RequestUserInput:
        """
        Return the manual entry form for device setup.

        Override this method to return a custom form for your device.

        :return: RequestUserInput with form fields for manual configuration
        """
        return _MANUAL_INPUT_SCHEMA

    async def query_device(
        self, input_values: dict[str, Any]
    ) -> AwolValerionConfig | SetupError | RequestUserInput:
        """
        Create device configuration from user input.

        This method is called after the user submits the setup form.
        It should validate the input, attempt to connect to the device,
        and return a DeviceConfig if successful.

        :param input_values: Dictionary of user input from the form
        :return: DeviceConfig on success, SetupError on failure, or
                 RequestUserInput to re-display the form
        """
        # Extract form values
        address = input_values.get("address", "").strip()
        port = int(input_values.get("port", 0))
        password = input_values.get("password", "")

        # Validate required fields
        if not address:
            _LOG.warning("Address is required, re-displaying form")
            return _MANUAL_INPUT_SCHEMA

        if not port:
            _LOG.warning("Port is required, re-displaying form")
            return _MANUAL_INPUT_SCHEMA

        name = f"AWOL Valerion projector ({address})"

        try:
            config = AwolValerionConfig(
                identifier=address.replace(".", "_"),
                name=name,
                address=address,
                password=password,
                port=int(port),
            )

            identity, detected = await self._probe(config)
            if detected:
                _LOG.info("Detected %s via %s (serial %s)",
                          identity.product, detected, identity.serial or "unknown")
            else:
                _LOG.info("Projector %s not reachable now; will connect when available", address)

            return config

        except ConnectionError as ex:
            _LOG.error("Connection refused to %s: %s", address, ex)
            return SetupError(IntegrationSetupError.CONNECTION_REFUSED)

        except TimeoutError as ex:
            _LOG.error("Connection timeout to %s: %s", address, ex)
            return SetupError(IntegrationSetupError.TIMEOUT)

        except Exception as ex:  # pylint: disable=broad-exception-caught
            _LOG.error("Failed to connect to %s: %s", address, ex)
            _LOG.info("Please verify the device address and try again")
            return SetupError(IntegrationSetupError.CONNECTION_REFUSED)

    async def _probe(self, config: AwolValerionConfig) -> tuple[ProjectorIdentity, str]:
        """Try each candidate transport; return (identity, protocol_name) or empty."""
        transport = PJLinkTransport(config.address, config.port, config.password)
        try:
            if await transport.probe():
                identity = await transport.get_identity()
                await transport.close()
                return identity, transport.name
            await transport.close()
        except TransportAuthError:
            _LOG.warning("%s needs a password for %s; completing anyway",
                         transport.name, config.address)
            await transport.close()
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOG.debug("%s probe failed for %s: %s", transport.name, config.address, err)
            try:
                await transport.close()
            except Exception:  # pylint: disable=broad-exception-caught
                pass
        return ProjectorIdentity(), ""
