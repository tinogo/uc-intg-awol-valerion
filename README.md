# Unfolded Circle Integration AWOL Valerion

This repository contains the source code for the [Unfolded Circle Remote Two/3](https://www.unfoldedcircle.com/) integration driver for AWOL Valerion projectors.

The integration is based on the amazing work of JackJPowell's [ucapi-framework](https://github.com/jackjpowell/ucapi-framework).

It also heavily borrows code from the [Epson projector integration](https://github.com/mase1981/uc-intg-epson) by @mase1981 - thank you for all the great integrations! :)

## Table of contents

1. [Supported entity types](#supported-entity-types)
2. [Installation instructions](#installation-instructions)
3. [Update instructions](#update-instructions)
4. [Versioning](#versioning)
5. [Changelog](#changelog)
6. [Development](#development)
7. [Resources](#resources)
8. [License](#license)

## Supported entity types

- [Media player](#media-player-entity)
- [Remote](#remote-entity)
- [Selects](#select-entity)
- [Sensors](#sensor-entity)

### Media Player entity

The Media Player entity implements the following features:
- `ON_OFF`: Provides dedicated on/off commands
- `DPAD`: Enables navigating your projector's OSD
- `TOGGLE`: Provides the power toggle
- `VOLUME`: Enables adjusting the volume slider via the Remote 3's touch slider
- `VOLUME_UP_DOWN`: Provides dedicated volume up/down commands
- `HOME`: Provides the home and back commands.
- `MUTE`: Mutes the device
- `UNMUTE`: Unmutes the device
- `MUTE_TOGGLE`: Toggles the mute state of the device
- `SELECT_SOURCE`: Provides a dropdown of available sources

The entity doesn't provide any of the playback features, though, as the PJLink-API doesn't provide any of those commands.

### Remote entity

The Media Player entity implements the following features:
- `ON_OFF`: Provides dedicated on/off commands
- `TOGGLE`: Provides the power toggle
- `SEND_CMD`: Allows sending a command to the device
- `SEND_CMD_SEQUENCE`: Allows sending a command sequence to the device

Furthermore, it implements many Simple-Commands.

The commands `SEND_CMD` and `SEND_CMD_SEQUENCE` allow the user to send any supported PJLink-commands (see https://support.valerion.com/hc/en-us/articles/17088458288143-What-is-AWOL-Link for reference).

### Select entity

This integration provides the following Select-Types:
- Changing the Color Temperature
- Changing the Dynamic Tone Mapping
- Changing the EBL mode
- Changing the Gamma curve
- Changing the Laser luminance
- Changing the Motion Enhancement mode
- Changing the Picture mode

### Sensor entity

This integration provides the following sensors:
- Current Volume
- Muted Status
- Current Source
- Current input resolution
- Recommended resolution
- Current aspect ratio
- Current color temperature mode
- Current Dynamic tone mapping mode
- Current EBL mode
- Current Fan speed
- Current Gamma mode
- Current laser luminance level
- Current motion enhancement mode
- Current picture mode
- Current signal info
- Current temperatures of the projector

## Installation instructions

1. Ensure that you've enabled the "AWOL Link" feature in your projector's settings (it requires the latest Q0718 firmware or later).
   - **Important:** Leave the "security code" for the AWOL Link disabled, otherwise the integration won't work. Authentication needs to be figured out, still (see https://github.com/tinogo/uc-intg-awol-valerion/issues/11 for reference).
2. Download the integration package (tar.gz file) from the [Releases](https://github.com/tinogo/uc-intg-awol-valerion/releases) page
3. Upload the archive via the Remote's web configurator: "Integrations" → "Install custom"
4. Configure your device through the setup wizard

## Update instructions

1. Download the integration package (tar.gz file) from the [Releases](https://github.com/tinogo/uc-intg-awol-valerion/releases) page
2. Remove the existing integration from the Remote (twice) → no worries, all your configured activity settings will still be there.
3. Upload the archive via the Remote's web configurator: "Integrations" → "Install custom"
4. Configure your device through the setup wizard

## Versioning

We use [SemVer](https://semver.org) for versioning. For the versions available, see the [tags and releases in this repository](https://github.com/tinogo/uc-intg-awol-valerion/releases).

## Changelog

The major changes found in each new release are listed in the [changelog](https://github.com/tinogo/uc-intg-awol-valerion/blob/main/CHANGELOG.md) and under the GitHub [releases](https://github.com/tinogo/uc-intg-awol-valerion/releases).

## Development

### Project Structure

```
├── driver.json              # Integration metadata and configuration
├── uc_intg_awol_valerion/   # Main integration code
│   ├── __init__.py          # Main entry point
│   ├── config.py            # device configuration dataclass
│   ├── const.py             # Constants
│   ├── device.py            # Device communication and state management
│   ├── driver.py            # Integration Driver
│   ├── media_player.py      # Media player entity
│   ├── pjlink.py            # The basic PJLink-client communicating with the AWOL Valerion projectors
│   ├── remote.py            # Remote entity
│   ├── select.py            # Select entity
│   ├── sensor.py            # Sensor entity
│   └── setup.py             # Setup flow and user configuration
├── config/                  # Runtime configuration storage
├── Dockerfile               # Container build configuration
└── requirements.txt         # Python dependencies
```

### Prerequisites

- Python 3.11+
- uv
- Docker, Docker Compose

### Running the integration

1. Prepare the environment:
   ```bash
   uv venv
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Install the git-hooks:
   ```bash
   uv run pre-commit install
   ```

4. Run the integration either locally or via a Compose environment:
   1. Locally:
      ```bash
      uv run uc_intg_awol_valerion/__init__.py
      ```
   2. via Compose:
      ```bash
      docker compose up --remove-orphans --build --watch --pull=always
      ```

### Adding and removing dependencies

#### Adding dependencies

```bash
uv add <dependency>
uv export --format requirements.txt --output-file requirements.txt --no-annotate --no-header --no-hashes --no-dev
```

#### Removing dependencies

```bash
uv remove <dependency>
uv export --format requirements.txt --output-file requirements.txt --no-annotate --no-header --no-hashes --no-dev
```

#### Updating all dependencies

```bash
uv lock --upgrade
uv export --format requirements.txt --output-file requirements.txt --no-annotate --no-header --no-hashes --no-dev
```

### Environment Variables

| Variable                   | Description                                 | Default   |
|----------------------------|---------------------------------------------|-----------|
| `UC_LOG_LEVEL`             | Logging level (DEBUG, INFO, WARNING, ERROR) | `DEBUG`   |
| `UC_CONFIG_HOME`           | Configuration directory path                | `/config` |
| `UC_INTEGRATION_INTERFACE` | Network interface to bind                   | `0.0.0.0` |
| `UC_INTEGRATION_HTTP_PORT` | HTTP port for the integration               | `9090`    |
| `UC_DISABLE_MDNS_PUBLISH`  | Disable mDNS advertisement                  | `false`   |


## Resources

- [UC Integration Python Library](https://github.com/aitatoi/integration-python-library)
- [UCAPI Framework](https://github.com/jackjpowell/ucapi-framework)
- [Unfolded Circle Developer Documentation](https://github.com/unfoldedcircle/core-api)
- [Epson projector integration for Unfolded Circle Remote Two/3](https://github.com/mase1981/uc-intg-epson)

## License

Mozilla Public License Version 2.0 – see [LICENSE](LICENSE) for details.
