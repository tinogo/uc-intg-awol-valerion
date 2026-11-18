# Repository instructions

## Project commands

This project requires Python 3.14+ and UV (see `pyproject.toml`). Install the development dependencies with:

```bash
uv sync
```

Run the same checks as the Python CI workflow:

```bash
uv run -m pylint uc_intg_awol_valerion
uv run -m flake8 uc_intg_awol_valerion --count --show-source --statistics
uv run -m isort uc_intg_awol_valerion/. --check --verbose
uv format --check
```

For a focused check of one module, pass its path to each applicable tool, for example:

```bash
uv run -m pylint uc_intg_awol_valerion/device.py
uv run -m flake8 uc_intg_awol_valerion/device.py
uv run -m isort uc_intg_awol_valerion/device.py --check --verbose
uv format --check uc_intg_awol_valerion/device.py
```

There is no automated test suite or single-test runner in the repository. To run the integration locally after `uv sync`, use `uv run python -m uc_intg_awol_valerion`; runtime settings are documented in `README.md`.

## Architecture

`uc_intg_awol_valerion/__init__.py` assembles a `BaseIntegrationDriver` with the device class, entity classes, configuration manager, and setup flow. Each configured projector becomes an `AwolValerionDevice` (`device.py`), which owns the current `PJLinkStatus` and `PJLinkIdentity`, polls every five seconds, and publishes updates to its subscribed entities.

`pjlink.py` implements the asynchronous TCP/PJLink protocol, authentication, response parsing, and status snapshots. Device command methods translate integration actions into PJLink calls, refresh state, and return success status. Entities (`media_player.py`, `remote.py`, `select.py`, and `sensor.py`) translate UC API commands and attributes to/from the device model. The setup flow (`setup.py`) validates user configuration and tests connectivity; `config.py` defines the persisted device configuration.

## Repository-specific patterns

- Keep protocol details and PJLink command/response handling in `pjlink.py`; shared command strings and simple-command identifiers belong in `const.py`. Device-facing operations and state refresh belong in `device.py`.
- Entities inherit the corresponding UC API entity type and `ucapi_framework.Entity`, retain a reference to the device, subscribe to its updates, and synchronize their state/attributes from the device snapshot.
- Selects and sensors are factory-created from `SelectType`/`SensorType` enums and configuration maps in their respective modules. Add a type to both its enum and config map; the driver instantiates every enum member.
- The remote and media player dispatch simple commands through `simple_commands.py`. When adding a supported simple action, keep the command enum, map, device method, and entity handler consistent.
- Device commands should refresh/publish state through the existing device flow after a successful change. Polling is serialized by the device connection lock; PJLink requests are also serialized by the client.
- Preserve the project’s configured style: 120-character lines, double-quoted strings, and import ordering checked by isort. Manage dependencies with UV; declare them in `pyproject.toml` and keep `uv.lock` current.
- The setup UI has English and German translations; update both when changing user-facing setup text.
