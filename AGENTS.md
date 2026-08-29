# AWOL Valerion Integration - Architecture & Development Guide

Technical documentation for developers working with the AWOL Valerion integration driver. For feature overview and user documentation, see [README.md](README.md).

## Architecture Overview

```
┌─────────────────────────────────────────┐
│   Unfolded Circle Remote Two/3 API      │
└────────────────┬────────────────────────┘
                 │
         ┌───────┴────────┐
         ▼                ▼
    ┌──────────┐  ┌──────────┐
    │ Entities │  │  Drivers │
    └────┬─────┘  └──────────┘
         │
    ┌────┼───────────────────────────┐
    ▼    ▼         ▼         ▼       ▼
 Media  Remote  Select  Sensor   Setup
 Player Entity  Entities Entities Flow
    │
    └─────────────────┬──────────────────┐
                      ▼                   ▼
              ┌──────────────┐    ┌────────────────┐
              │   Device     │    │  Config        │
              │ Management   │    │  Management    │
              └──────┬───────┘    └────────────────┘
                     ▼
            ┌─────────────────────┐
            │   PJLink Client     │
            │  (Protocol Handler) │
            └──────────┬──────────┘
                       ▼
            ┌─────────────────────┐
            │ AWOL Valerion Device│
            │   (TCP/IP)          │
            └─────────────────────┘
```

---

## Entity Architecture

### Entity Base Design

All entities inherit from both a UC API entity type and `ucapi_framework.Entity`:

```python
class AwolValerionEntity(UCAPIEntityType, Entity):
    def __init__(self, device_config, device):
        self._device = device
        super().__init__(...)
        self.subscribe_to_device(device)
    
    def map_entity_states(self, device_state) -> State:
        """Map device states to UC API states"""
        
    async def sync_state(self) -> None:
        """Called when device state changes"""
```

All entity types follow this pattern:
- Store reference to `AwolValerionDevice`
- Build command maps for handler dispatch
- Subscribe to device state changes
- Map device states to UC API states
- Update attributes on device state change

---

### Media Player Entity (`media_player.py`)

**Class:** `AwolValerionMediaPlayer` (extends `MediaPlayer`, `Entity`)

- Builds command map from device methods
- State mapping: Device states → UC API states
- Attribute sync: Updates on device state changes
- See README.md for feature & command details

---

### Remote Entity (`remote.py`)

**Class:** `AwolValerionRemote` (extends `Remote`, `Entity`)

- Supports raw PJLink command execution (`SEND_CMD`)
- Supports command sequences with delays (`SEND_CMD_SEQUENCE`)
- Extends simple commands
- See README.md for feature details

---

### Select Entities (`select.py`)

**Class:** `AwolValerionSelect` (extends `Select`, `Entity`)

Factory-based entity creation via `SelectType` enum:

```python
SELECT_CONFIGS: dict[SelectType, SelectConfig] = {
    SelectType.COLOR_TEMPERATURE: SelectConfig(
        label="Color Temperature",
        command_template=AwolValerionCommands.SET_COLOR_TEMPERATURE,
        get_current_option=lambda device: device.status.color_temperature,
        get_options=lambda device: list(device.status.color_temperature_list.keys()),
        map_option_to_device_value=lambda device, option: 
            device.status.color_temperature_list.get(option),
    ),
    # ... 6 more types
}
```

Each select handles:
- Option cycling and selection
- Mapping UI options to device values
- Sending formatted PJLink commands

See README.md for select type details.

---

### Sensor Entities (`sensor.py`)

**Class:** `AwolValerionSensor` (extends `Sensor`, `Entity`)

Similar factory-based pattern to Select:

```python
SENSOR_CONFIGS: dict[SensorType, SensorConfig] = {
    SensorType.MUTE: SensorConfig(
        label="Mute",
        device_class=DeviceClasses.BINARY,
        value_getter=lambda device: "on" if device.status.muted else "off",
        unit="sound",
    ),
    # ... 15 more types
}
```

Read-only monitoring of device state via value getters. See README.md for sensor type details.

---

## Development Setup

### Toolchain: UV

**This project uses [UV](https://docs.astral.sh/uv/) as the Python package manager and project toolchain.**

UV is explicitly required in `pyproject.toml`:
```toml
[tool.uv]
required-version = ">=0.12.7"
```

### Quick Start

```bash
# Create virtual environment
uv venv

# Activate (Linux/macOS)
source .venv/bin/activate
# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
uv sync

# Install git hooks
uv run pre-commit install

# Run integration locally (choose one)
uv run uc_intg_awol_valerion/__init__.py        # Via __init__.py
python -m uc_intg_awol_valerion                 # As Python module
uc-intg-awol-valerion                          # Via installed script entry point

# Or via Docker Compose
docker compose up --remove-orphans --build --watch --pull=always
```

### Dependency Management

```bash
# Add a new dependency
uv add package_name

# Remove a dependency
uv remove package_name

# Upgrade a single dependency
uv lock --upgrade-package package_name

# Upgrade all dependencies
uv lock --upgrade

# Export requirements.txt (after changes)
uv export --format requirements.txt --output-file requirements.txt \
  --no-annotate --no-header --no-hashes --no-dev
```

For complete UV documentation, see: https://docs.astral.sh/uv/

### Code Quality & Linting

**Code Style Guidelines** (see `docs/code_guidelines.md`):
- Maximum line length: 120 characters
- Use double quotes for string literals (enforced by pylint)
- Configuration files: `.pylintrc`, `setup.cfg`

**Verify Code Quality:**
```bash
# Lint with pylint
uv run -m pylint uc_intg_awol_valerion

# Check style with flake8
uv run -m flake8 uc_intg_awol_valerion --count --show-source --statistics

# Verify import ordering with isort
uv run -m isort uc_intg_awol_valerion/. --check --verbose
```

**Format Code:**
```bash
# Auto-format with uv's built-in formatter
uv format
```

All checks are run automatically via GitHub Actions on each push and pull request to the main branch.

---

## Core Classes

### Device Communication (`device.py`)

**Class:** `AwolValerionDevice` (extends `PollingDevice`)

Central state management and command execution:

```python
class AwolValerionDevice(PollingDevice):
    _client: PJLinkClient      # Protocol handler
    status: PJLinkStatus       # Current device state snapshot
    identity: PJLinkIdentity   # Static device info
    
    FAIL_THRESHOLD = 3  # Polls before marking unavailable
    _poll_interval = 5  # seconds
```

**State Management:**
- `establish_connection()` - Load identity & refresh state
- `poll_device()` - Periodic state refresh (locks for serialization)
- `_refresh()` - Query device and handle transient failures
- `_fail_count` - Tolerates 3 consecutive poll failures before UNAVAILABLE

**Command Methods:**
```python
# Power control
await device.power_on() / power_off() / power_toggle()

# Volume & mute
await device.volume_x(level: int)  # 0-100
await device.volume_up() / volume_down()
await device.mute_on() / mute_off() / mute_toggle()

# Input/source
await device.select_source(name: str)

# OSD navigation
await device.cursor_up/down/left/right/enter()
await device.back() / home() / menu() / settings()

# Raw command
await device.send_raw(command: str)  # e.g., "%1POWR 1"
```

All command methods:
1. Execute via PJLinkClient
2. Poll device to refresh state
3. Return success/failure bool
4. Log errors

---

### PJLink Protocol Handler (`pjlink.py`)

**Class:** `PJLinkClient`

Low-level async TCP client implementing PJLink protocol:

```python
class PJLinkClient:
    _host: str
    _port: int = 4352
    _password: str
    _send_lock: asyncio.Lock  # Serialize commands
```

**Protocol Features:**
- MD5 authentication handshake (if password set)
- One TCP connection per command (reference implementation)
- 4-second timeout per command
- Response parsing with error detection

**Public Methods:**
```python
# Connection testing
await client.test() -> bool

# Querying state
await client.poll() -> PJLinkStatus
await client.get_identity() -> PJLinkIdentity
await client.get_power() -> AwolValerionStates

# Commands
await client.power_on() / power_off()
await client.select_input(input_code: str)
await client.set_mute(muted: bool)
await client.send_raw(command: str)
```

**Data Classes:**
- `PJLinkStatus` - Dynamic state snapshot (power, volume, input, settings, etc.)
- `PJLinkIdentity` - Static device info (name, product, manufacturer, etc.)

**Exception Classes:**
- `PJLinkAuthError` - Authentication failure (wrong password)
- `PJLinkError` - Protocol errors or device errors (ERR response)

---

### Configuration (`config.py`)

**Class:** `AwolValerionConfig` (dataclass)

```python
@dataclass
class AwolValerionConfig:
    identifier: str   # Unique ID (used for entity IDs)
    name: str         # Friendly name
    address: str      # IP or hostname
    port: int         # PJLink port (default 4352)
    password: str = ""  # Optional auth password
```

---

### Setup Flow (`setup.py`)

**Class:** `AwolValerionSetupFlow` (extends `BaseSetupFlow[AwolValerionConfig]`)

Device discovery and initial configuration:

```python
async def get_manual_entry_form() -> RequestUserInput:
    # Returns form schema with:
    # - address (required, text)
    # - port (required, number, default 4352)
    # - password (optional, password)

async def query_device(input_values: dict) -> AwolValerionConfig | SetupError:
    # 1. Validate required fields
    # 2. Create AwolValerionConfig
    # 3. Test connection via _test_connection()
    # 4. Return config or SetupError

async def _test_connection(config: AwolValerionConfig) -> PJLinkIdentity | None:
    # Attempt single connection, return device info or None
```

**Error Handling:**
- `IntegrationSetupError.AUTHORIZATION_ERROR` - Wrong password
- `IntegrationSetupError.CONNECTION_REFUSED` - Can't connect
- `IntegrationSetupError.TIMEOUT` - Connection timeout
- Returns form for retry on non-critical errors

**Internationalization:**
- English and German UI strings

---

### Constants (`const.py`)

**Enum Classes:**

```python
class Loggers(StrEnum):
    DRIVER, MEDIA_PLAYER, REMOTE, DEVICE, PJLINK, SELECT, SENSOR, SETUP_FLOW

class AwolValerionStates(StrEnum):
    ON, OFF, UNAVAILABLE, UNKNOWN

class AwolValerionCommands(StrEnum):
    # Query commands
    GET_POWER = "%1POWR ?"
    GET_VOLUME = "%3VOLM ?"
    # ... 20+ commands
    
    # Control commands with parameters
    SET_POWER_ON = "%1POWR 1"
    SET_VOLUME_X_FORMAT = "%3VOLM {}"  # Format: values 0-100
    # ... more

class SimpleCommands(StrEnum):
    POWER_ON, POWER_OFF, POWER_TOGGLE, ...
```

---

### Simple Commands Utility (`simple_commands.py`)

Helper function for mapping UC API simple commands to device methods:

```python
def build_simple_commands_map(device: AwolValerionDevice) -> dict[str, Callable]:
    """Map SimpleCommands enum to corresponding device methods."""
    return {
        SimpleCommands.POWER_ON: device.power_on,
        SimpleCommands.POWER_OFF: device.power_off,
        # ... maps all simple commands to async device methods
    }
```

Used in `remote.py` and `media_player.py` to dispatch simple command requests.

## Integration Flows

### 1. Startup (`__init__.py` and `__main__.py`)

The integration initializes via `main()` function in `__init__.py`:

```
__main__.py or __init__.py → main()
  ├─ Setup logging from UC_LOG_LEVEL env (default: DEBUG)
  ├─ Initialize BaseIntegrationDriver with:
  │  ├─ device_class: AwolValerionDevice
  │  ├─ entity_classes: [MediaPlayer, Remote, SelectFactory, SensorFactory]
  │  │  └─ Select/Sensor factories return lists of typed entities
  │  ├─ config_manager: BaseConfigManager(AwolValerionConfig)
  │  └─ setup_handler: AwolValerionSetupFlow
  ├─ register_all_device_instances() from config files
  ├─ init API with driver.json config
  └─ await indefinitely
```

**Entry Points:**
- `python -m uc_intg_awol_valerion` - via `__main__.py`
- `uv run uc_intg_awol_valerion/__init__.py` - direct via __init__.py
- `uc-intg-awol-valerion` - via script entry point (after `uv sync`)


### 2. Device Addition (Setup)

```
User clicks "Setup" in Remote UI
  ↓
AwolValerionSetupFlow.get_manual_entry_form()
  ↓ (User enters address, port, password)
  ↓
AwolValerionSetupFlow.query_device(input_values)
  ├─ validate inputs
  ├─ create AwolValerionConfig
  ├─ _test_connection() → PJLinkClient.test()
  ├─ on success: return config
  └─ on error: return SetupError or form for retry
  ↓
Driver adds device to config storage
  ↓
AwolValerionDevice instantiated & begins polling
```

### 3. Polling & State Update Loop

```
every 5 seconds:
  AwolValerionDevice.poll_device()
    ├─ acquire _connect_lock
    ├─ _load_identity() if needed
    ├─ _refresh():
    │  ├─ PJLinkClient.poll() → PJLinkStatus
    │  └─ update self.status
    └─ release lock
      ↓
      push_update() to all subscribed entities
        ↓ (for each entity)
        ├─ entity.sync_state()
        │  └─ entity.update(attributes)
        └─ send updated attributes to Remote
```

### 4. Command Execution

```
User sends command from Remote UI
  ↓
Entity.handle_command(cmd_id, params)
  ├─ dispatch via command_map:
  │  ├─ simple commands: call device.method()
  │  └─ complex: call device.method(params)
  ├─ device method:
  │  ├─ execute via PJLinkClient
  │  ├─ call poll_device()
  │  └─ return success bool
  ├─ return StatusCode.OK or BAD_REQUEST
  └─ device push_update()
    ↓
    entities.sync_state() → Remote UI updates
```

---

## Development Patterns

### Adding a New Select Type

1. Add to `SelectType` enum in `select.py`
2. Create `SelectConfig` entry in `SELECT_CONFIGS` dict:
   ```python
   SelectType.NEW_SETTING: SelectConfig(
       label="Display Name",
       command_template=AwolValerionCommands.SET_NEW_SETTING,
       get_current_option=lambda dev: dev.status.new_setting,
       get_options=lambda dev: list(dev.status.new_setting_list.keys()),
       map_option_to_device_value=lambda dev, opt: dev.status.new_setting_list[opt],
   )
   ```
3. Add PJLink command to `const.py`
4. Entities auto-instantiated in `__init__.py` via:
   ```python
   [AwolValerionSelect(dev, select_type) for select_type in SelectType]
   ```

### Adding a New Sensor Type

Same pattern as Select:
1. Add to `SensorType` enum
2. Create `SensorConfig` in `SENSOR_CONFIGS`:
   ```python
   SensorType.NEW_METRIC: SensorConfig(
       label="Display Name",
       device_class=DeviceClasses.CUSTOM,
       value_getter=lambda dev: str(dev.status.new_metric),
       unit="unit_if_any",
   )
   ```
3. Auto-instantiated in `__init__.py`

### Adding a Device Method

1. Implement in `AwolValerionDevice`:
   ```python
   async def my_command(self, param: str) -> bool:
       try:
           await self._client.send_raw(command_string)
           await self.poll_device()
           return True
       except Exception as err:
           _LOG.error("[%s] Command failed: %s", self.log_id, err)
           return False
   ```
2. Add to entity's command map
3. Handle in entity's `handle_command()`

### Debugging

- Set `UC_LOG_LEVEL=DEBUG` for verbose logging
- Each module has dedicated logger: `Loggers.DEVICE`, `Loggers.PJLINK`, etc.
- Device state queryable via `device.status` snapshot
- PJLink commands logged with `_LOG.debug()`

### Testing & Validation

**Manual Testing:**
1. Start the integration with debug logging: `UC_LOG_LEVEL=DEBUG uv run -m uc_intg_awol_valerion`
2. Check logs for device polling cycles and command execution
3. Use Remote UI to send commands and observe logs
4. Verify entity state changes propagate correctly

**Code Quality Checks (pre-commit hook automated):**
- Pylint for code analysis
- Flake8 for style compliance
- isort for import ordering
- All checks must pass before commits

**Integration Testing:**
- Run `docker compose up --build` for containerized testing
- Test with actual AWOL Valerion device on network
- Monitor logs at `UC_LOG_LEVEL=DEBUG` for error handling


