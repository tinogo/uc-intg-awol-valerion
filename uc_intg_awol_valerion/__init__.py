"""
Remote Two/3 Integration Driver.

This is the main entry point for the integration driver. It initializes
the driver, sets up logging, and starts the integration API.

:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import asyncio
import logging
import os

from ucapi_framework import BaseConfigManager, BaseIntegrationDriver, get_config_path

from uc_intg_awol_valerion.config import AwolValerionConfig
from uc_intg_awol_valerion.const import Loggers
from uc_intg_awol_valerion.device import AwolValerionDevice
from uc_intg_awol_valerion.media_player import AwolValerionMediaPlayer
from uc_intg_awol_valerion.setup import AwolValerionSetupFlow


async def main():
    """Start the Remote Two integration driver."""
    logging.basicConfig()

    # Configure logging level from environment variable
    level = os.getenv("UC_LOG_LEVEL", "DEBUG").upper()
    for logger in Loggers:
        logging.getLogger(logger).setLevel(level)

    # Initialize the integration driver
    integration_driver = BaseIntegrationDriver(
        device_class=AwolValerionDevice,
        entity_classes=[
            AwolValerionMediaPlayer,
        ],
    )

    # Configure the device config manager
    integration_driver.config_manager = BaseConfigManager(
        get_config_path(integration_driver.api.config_dir_path),
        integration_driver.on_device_added,
        integration_driver.on_device_removed,
        config_class=AwolValerionConfig,
    )

    # Register all configured devices from config file
    await integration_driver.register_all_device_instances(True)

    setup_handler = AwolValerionSetupFlow.create_handler(driver=integration_driver)

    # Initialize the API with the driver configuration
    await integration_driver.api.init("driver.json", setup_handler)

    # Keep the driver running
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
