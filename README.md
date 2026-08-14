# Unfolded Circle Integration AWOL Valerion

This repository contains the source code for the [Unfolded Circle Remote Two/3](https://www.unfoldedcircle.com/) integration driver for AWOL Valerion projectors.

The integration is based on the amazing work of JackJPowell's [ucapi-framework](https://github.com/jackjpowell/ucapi-framework).

It also heavily boroughs code from the [Epson projector integration](https://github.com/mase1981/uc-intg-epson).

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

### Media Player entity

tba


## Installation instructions

1. Download the integration package (tar.gz file) from the [Releases](https://github.com/tinogo/uc-intg-awol-valerion/releases) page
2. Upload the archive via the Remote's web configurator: "Integrations" → "Install custom"
3. Configure your device through the setup wizard

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
│   ├── device_attributes.py # Contains the device attributes, i.e. the state of the StormAudio ISP
│   ├── discover.py          # Network device discovery
│   ├── driver.py            # Integration Driver
│   ├── helpers.py           # Common used helper files
│   ├── media_player.py      # Media player entity
│   ├── remote.py            # Remote entity
│   ├── select.py            # Select entity
│   ├── sensor.py            # Sensor entity
│   ├── setup.py             # Setup flow and user configuration
│   └── pjlink.py            # The basic PJLink-client communicating with the AWOL Valerion projectors
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
