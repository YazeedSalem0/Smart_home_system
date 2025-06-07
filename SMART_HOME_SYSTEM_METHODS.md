 # Smart Home System Methods Documentation

## Overview
This document provides comprehensive documentation for all methods used in `smart_home_system.py`. The smart home automation system integrates motion detection, temperature monitoring, gas leak detection, door control, garage automation, and web interface functionality.

## Table of Contents
1. [LED Control Methods](#led-control-methods)
2. [Audio Alert Methods](#audio-alert-methods)
3. [Door Control Methods](#door-control-methods)
4. [Garage Control Methods](#garage-control-methods)
5. [Sensor Reading Methods](#sensor-reading-methods)
6. [Motor Control Methods](#motor-control-methods)
7. [Event Handler Methods](#event-handler-methods)
8. [Automation Rule Methods](#automation-rule-methods)
9. [Flask API Routes](#flask-api-routes)
10. [Template Generation Methods](#template-generation-methods)

---

## LED Control Methods

### `set_led_color(room, r_state, g_state, b_state)`
**Purpose**: Controls individual RGB LED colors for a specific room.

**Parameters**:
- `room` (str): Room name ('Room1', 'Room2', 'Room3', 'LivingRoom')
- `r_state` (bool): Red LED state (True=ON, False=OFF)
- `g_state` (bool): Green LED state (True=ON, False=OFF)
- `b_state` (bool): Blue LED state (True=ON, False=OFF)

**Returns**: None

**Usage Example**:
```python
set_led_color('Room1', True, False, True)  # Purple light in Room1
```

**GPIO Pins Used**:
- Room1: R=5, G=6, B=13
- Room2: R=19, G=26, B=16
- Room3: R=20, G=21, B=12
- LivingRoom: R=2, G=3, B=14

---

### `led_white(room)`
**Purpose**: Sets room LED to white color (all RGB components ON).

**Parameters**:
- `room` (str): Target room name

**Returns**: None

**Usage Example**:
```python
led_white('LivingRoom')  # White light in living room
```

---

### `led_red(room)`
**Purpose**: Sets room LED to red color (emergency/alert indication).

**Parameters**:
- `room` (str): Target room name

**Returns**: None

**Usage Example**:
```python
led_red('Room2')  # Red alert light in Room2
```

---

### `led_off(room)`
**Purpose**: Turns off all LED colors in specified room.

**Parameters**:
- `room` (str): Target room name

**Returns**: None

**Usage Example**:
```python
led_off('Room3')  # Turn off all lights in Room3
```

---

### `all_leds_red()`
**Purpose**: Sets all room LEDs to red (system-wide emergency state).

**Parameters**: None

**Returns**: None

**Usage Example**:
```python
all_leds_red()  # Emergency mode - all rooms red
```

---

### `all_leds_off()`
**Purpose**: Turns off all LEDs in all rooms.

**Parameters**: None

**Returns**: None

**Usage Example**:
```python
all_leds_off()  # Turn off all lights system-wide
```

---

## Audio Alert Methods

### `buzzer_on(frequency=440, duty_cycle=50)`
**Purpose**: Activates buzzer with specified frequency and duty cycle.

**Parameters**:
- `frequency` (int): Sound frequency in Hz (default: 440Hz - A4 note)
- `duty_cycle` (int): PWM duty cycle percentage (default: 50%)

**Returns**: None

**Usage Example**:
```python
buzzer_on(880, 75)  # High-pitched loud alert
```

**GPIO Pin**: 9

---

### `buzzer_off()`
**Purpose**: Turns off the buzzer.

**Parameters**: None

**Returns**: None

**Usage Example**:
```python
buzzer_off()  # Stop all audio alerts
```

---

### `buzzer_beep(frequency=440, duty_cycle=50, duration=0.2, pause=0.2, count=1)`
**Purpose**: Creates beep patterns with specified parameters.

**Parameters**:
- `frequency` (int): Beep frequency in Hz
- `duty_cycle` (int): PWM duty cycle percentage
- `duration` (float): Beep duration in seconds
- `pause` (float): Pause between beeps in seconds
- `count` (int): Number of beeps

**Returns**: None

**Usage Example**:
```python
buzzer_beep(1000, 50, 0.1, 0.1, 3)  # Three quick high beeps
```

---

### `play_alert_pattern(pattern_type)`
**Purpose**: Plays predefined alert patterns for different system events.

**Parameters**:
- `pattern_type` (str): Alert pattern type
  - `'emergency'`: Gas leak or critical alert
  - `'warning'`: Temperature or motion warning
  - `'success'`: Successful operation
  - `'error'`: System error

**Returns**: None

**Usage Example**:
```python
play_alert_pattern('emergency')  # Play gas leak alert
```

**Implementation**: Runs in separate thread to avoid blocking main execution.

---

### `_play_alert_pattern_thread(pattern_type)`
**Purpose**: Internal method that executes alert patterns in separate thread.

**Parameters**:
- `pattern_type` (str): Alert pattern type

**Returns**: None

**Note**: This is a private method called by `play_alert_pattern()`.

---

## Door Control Methods

### `set_door_lock(lock_state)`
**Purpose**: Controls the main door lock servo mechanism.

**Parameters**:
- `lock_state` (bool): True=LOCK, False=UNLOCK

**Returns**: None

**Usage Example**:
```python
set_door_lock(False)  # Unlock door
time.sleep(5)
set_door_lock(True)   # Lock door after 5 seconds
```

**GPIO Pin**: 10 (Servo PWM)

**Servo Positions**:
- Lock: 2.5% duty cycle (0 degrees)
- Unlock: 7.5% duty cycle (90 degrees)

**Integration**: Updates `system_state['door_locked']` and logs state changes.

---

## Garage Control Methods

### `set_garage_door(open_state)`
**Purpose**: Controls garage door servo and manages auto-close functionality.

**Parameters**:
- `open_state` (bool): True=OPEN, False=CLOSE

**Returns**: None

**Usage Example**:
```python
set_garage_door(True)   # Open garage door
# Auto-close timer starts automatically
```

**GPIO Pin**: 11 (Servo PWM)

**Features**:
- Auto-close timer (120 seconds default)
- State logging and tracking
- Integration with IR fingerprint sensor

---

### `fingerprint_detected()`
**Purpose**: Handles IR fingerprint sensor detection for garage access.

**Parameters**: None

**Returns**: bool - True if valid fingerprint detected

**Usage Example**:
```python
if fingerprint_detected():
    set_garage_door(True)  # Open garage on valid fingerprint
```

**GPIO Pin**: 15 (IR sensor input)

---

### `handle_garage_auto_close()`
**Purpose**: Manages automatic garage door closing after timeout.

**Parameters**: None

**Returns**: None

**Features**:
- Checks auto-close timer
- Closes door if timeout reached
- Respects manual override settings

---

### `handle_ir_fingerprint()`
**Purpose**: Monitors IR fingerprint sensor and triggers garage door opening.

**Parameters**: None

**Returns**: None

**Implementation**: Runs continuously in sensor monitoring loop.

---

## Sensor Reading Methods

### `read_dht11()`
**Purpose**: Reads temperature and humidity from DHT11 sensor.

**Parameters**: None

**Returns**: tuple (temperature, humidity) or (None, None) on error

**Usage Example**:
```python
temp, humidity = read_dht11()
if temp is not None:
    print(f"Temperature: {temp}°C, Humidity: {humidity}%")
```

**GPIO Pin**: 4

**Error Handling**: Returns None values on sensor read failure.

---

### `check_gas_sensor()`
**Purpose**: Reads gas sensor values (both digital and analog).

**Parameters**: None

**Returns**: dict with gas sensor data
```python
{
    'digital': bool,      # Digital threshold detection
    'analog_voltage': float,  # Analog voltage reading
    'analog_raw': int,    # Raw ADC value
    'gas_detected': bool  # Combined detection result
}
```

**Usage Example**:
```python
gas_data = check_gas_sensor()
if gas_data['gas_detected']:
    handle_gas_detection()
```

**Hardware**:
- Digital Pin: 24 (MQ-7 digital output)
- Analog: ADS1115 ADC Channel A0

---

## Motor Control Methods

### `control_fans(turn_on=None)`
**Purpose**: Controls fan motors using L298N motor driver.

**Parameters**:
- `turn_on` (bool, optional): True=ON, False=OFF, None=toggle

**Returns**: None

**Usage Example**:
```python
control_fans(True)   # Turn fans on
control_fans(False)  # Turn fans off
control_fans()       # Toggle current state
```

**GPIO Pins**:
- MOTOR_IN1: 18 (Motor A direction 1)
- MOTOR_IN2: 25 (Motor A direction 2)
- MOTOR_IN3: 8 (Motor B direction 1)
- MOTOR_IN4: 7 (Motor B direction 2)

---

### `motor_a_forward()`
**Purpose**: Starts Motor A in forward direction.

**Parameters**: None

**Returns**: None

**GPIO Control**:
- IN1: HIGH, IN2: LOW

---

### `motor_a_stop()`
**Purpose**: Stops Motor A.

**Parameters**: None

**Returns**: None

**GPIO Control**:
- IN1: LOW, IN2: LOW

---

### `motor_b_forward()`
**Purpose**: Starts Motor B in forward direction.

**Parameters**: None

**Returns**: None

**GPIO Control**:
- IN3: HIGH, IN4: LOW

---

### `motor_b_stop()`
**Purpose**: Stops Motor B.

**Parameters**: None

**Returns**: None

**GPIO Control**:
- IN3: LOW, IN4: LOW

---

### `stop_all_motors()`
**Purpose**: Emergency stop for all motors.

**Parameters**: None

**Returns**: None

**Usage Example**:
```python
stop_all_motors()  # Emergency fan stop
```

---

## Event Handler Methods

### `handle_motion_detection()`
**Purpose**: Processes motion sensor events and triggers appropriate responses.

**Parameters**: None

**Returns**: None

**Features**:
- Checks all PIR sensors
- Updates motion state
- Triggers lighting automation
- Respects manual override settings

**PIR Pins**:
- Room1: 17, Room2: 27, Room3: 22, LivingRoom: 23

---

### `handle_gas_detection()`
**Purpose**: Handles gas leak detection and emergency response.

**Parameters**: None

**Returns**: None

**Emergency Actions**:
1. Sets emergency mode
2. Activates all red LEDs
3. Plays emergency alert pattern
4. Turns on ventilation fans
5. Logs emergency event

---

### `handle_temperature_control()`
**Purpose**: Manages temperature-based fan control automation.

**Parameters**: None

**Returns**: None

**Logic**:
- Turns on fans if temperature > threshold (25°C default)
- Turns off fans if temperature drops below threshold
- Respects manual override settings

---

### `sensor_monitor()`
**Purpose**: Main sensor monitoring loop that runs continuously.

**Parameters**: None

**Returns**: None (runs indefinitely)

**Monitoring Cycle**:
1. Read DHT11 sensor
2. Check gas sensors
3. Handle motion detection
4. Process temperature control
5. Handle garage auto-close
6. Monitor IR fingerprint sensor
7. Process automation rules
8. Sleep for 1 second

**Implementation**: Runs in separate daemon thread.

---

## Automation Rule Methods

### `add_rule(rule)`
**Purpose**: Adds a new automation rule to the system.

**Parameters**:
- `rule` (dict): Rule definition with structure:
```python
{
    'id': str,           # Unique rule identifier
    'name': str,         # Human-readable name
    'condition': dict,   # Trigger condition
    'action': dict,      # Action to execute
    'active': bool       # Rule enabled status
}
```

**Returns**: bool - Success status

**Usage Example**:
```python
rule = {
    'id': 'custom_rule_1',
    'name': 'Night Security',
    'condition': {'type': 'time', 'operator': '==', 'value': '22:00'},
    'action': {'type': 'light', 'command': 'on', 'location': 'all'},
    'active': True
}
add_rule(rule)
```

---

### `update_rule(rule_id, updated_rule)`
**Purpose**: Updates an existing automation rule.

**Parameters**:
- `rule_id` (str): Rule identifier to update
- `updated_rule` (dict): New rule definition

**Returns**: bool - Success status

**Usage Example**:
```python
updated_rule = {'name': 'Updated Night Security', 'active': False}
update_rule('custom_rule_1', updated_rule)
```

---

### `delete_rule(rule_id)`
**Purpose**: Removes an automation rule from the system.

**Parameters**:
- `rule_id` (str): Rule identifier to delete

**Returns**: bool - Success status

**Usage Example**:
```python
delete_rule('custom_rule_1')
```

---

### `toggle_rule(rule_id, active=None)`
**Purpose**: Toggles or sets the active status of a rule.

**Parameters**:
- `rule_id` (str): Rule identifier
- `active` (bool, optional): Specific state to set, None to toggle

**Returns**: bool - Success status

**Usage Example**:
```python
toggle_rule('rule1')        # Toggle current state
toggle_rule('rule1', False) # Disable rule
```

---

### `save_rules_to_file()`
**Purpose**: Persists automation rules to JSON file.

**Parameters**: None

**Returns**: None

**File**: `automation_rules.json`

---

### `load_rules_from_file()`
**Purpose**: Loads automation rules from JSON file.

**Parameters**: None

**Returns**: None

**Fallback**: Uses default rules if file doesn't exist.

---

### `evaluate_condition(condition)`
**Purpose**: Evaluates automation rule conditions against current system state.

**Parameters**:
- `condition` (dict): Condition definition

**Returns**: bool - True if condition is met

**Supported Conditions**:
- `temperature`: Compare temperature values
- `humidity`: Compare humidity values
- `gas`: Gas detection status
- `motion`: Motion detection in rooms
- `time`: Current time matching
- `door`: Door lock status
- `garage`: Garage door status

**Usage Example**:
```python
condition = {'type': 'temperature', 'operator': '>', 'value': 25.0}
if evaluate_condition(condition):
    # Execute temperature-based action
```

---

### `execute_action(action, condition=None)`
**Purpose**: Executes automation rule actions.

**Parameters**:
- `action` (dict): Action definition
- `condition` (dict, optional): Original condition for context

**Returns**: None

**Supported Actions**:
- `fan`: Control ventilation fans
- `light`: Control room lighting
- `alert`: Play alert patterns
- `door`: Control door lock
- `garage`: Control garage door

**Usage Example**:
```python
action = {'type': 'fan', 'command': 'on'}
execute_action(action)
```

---

### `process_automation_rules()`
**Purpose**: Processes all active automation rules.

**Parameters**: None

**Returns**: None

**Implementation**: Called every sensor monitoring cycle.

---

## Flask API Routes

### `@app.route('/')`
### `def index()`
**Purpose**: Serves the main web interface dashboard.

**HTTP Method**: GET

**Returns**: HTML template

**URL**: `http://localhost:5000/`

---

### `@app.route('/automation')`
### `def automation_page()`
**Purpose**: Serves the automation rules management page.

**HTTP Method**: GET

**Returns**: HTML template

**URL**: `http://localhost:5000/automation`

---

### `@app.route('/api/state')`
### `def get_state()`
**Purpose**: Returns current system state as JSON.

**HTTP Method**: GET

**Returns**: JSON with complete system state

**Response Example**:
```json
{
  "motion": {"Room1": false, "Room2": true, ...},
  "temperature": 24.5,
  "humidity": 60.0,
  "gas_detected": false,
  "fans_on": true,
  "door_locked": true,
  "garage_door_open": false
}
```

---

### `@app.route('/api/control/fan', methods=['POST'])`
### `def control_fan_api()`
**Purpose**: API endpoint for fan control.

**HTTP Method**: POST

**Request Body**:
```json
{"command": "on|off|toggle"}
```

**Returns**: JSON success response

---

### `@app.route('/api/control/fan/auto', methods=['POST'])`
### `def fan_auto_mode()`
**Purpose**: Toggles automatic fan control mode.

**HTTP Method**: POST

**Returns**: JSON with new auto mode status

---

### `@app.route('/api/control/light', methods=['POST'])`
### `def control_light_api()`
**Purpose**: API endpoint for lighting control.

**HTTP Method**: POST

**Request Body**:
```json
{
  "room": "Room1|Room2|Room3|LivingRoom|all",
  "command": "on|off|white|red"
}
```

**Returns**: JSON success response

---

### `@app.route('/api/control/light/auto', methods=['POST'])`
### `def light_auto_mode()`
**Purpose**: Toggles automatic lighting control.

**HTTP Method**: POST

**Request Body**:
```json
{"room": "Room1|all", "auto": true|false}
```

**Returns**: JSON success response

---

### `@app.route('/api/control/door', methods=['POST'])`
### `def control_door_api()`
**Purpose**: API endpoint for door lock control.

**HTTP Method**: POST

**Request Body**:
```json
{"lock": true|false}
```

**Returns**: JSON success response

---

### `@app.route('/api/control/door/auto', methods=['POST'])`
### `def door_auto_mode()`
**Purpose**: Toggles automatic door control mode.

**HTTP Method**: POST

**Returns**: JSON success response

---

### `@app.route('/api/control/garage', methods=['POST'])`
### `def control_garage_api()`
**Purpose**: API endpoint for garage door control.

**HTTP Method**: POST

**Request Body**:
```json
{"open": true|false}
```

**Returns**: JSON success response

---

### `@app.route('/api/control/garage/auto', methods=['POST'])`
### `def garage_auto_mode()`
**Purpose**: Toggles automatic garage control mode.

**HTTP Method**: POST

**Returns**: JSON success response

---

### `@app.route('/api/rules', methods=['GET'])`
### `def get_rules()`
**Purpose**: Returns all automation rules.

**HTTP Method**: GET

**Returns**: JSON array of rules

---

### `@app.route('/api/rules/<rule_id>', methods=['GET'])`
### `def get_rule(rule_id)`
**Purpose**: Returns specific automation rule.

**HTTP Method**: GET

**Parameters**: `rule_id` in URL path

**Returns**: JSON rule object or 404

---

### `@app.route('/api/rules', methods=['POST'])`
### `def create_rule()`
**Purpose**: Creates new automation rule.

**HTTP Method**: POST

**Request Body**: Rule definition JSON

**Returns**: JSON success response

---

### `@app.route('/api/rules/<rule_id>', methods=['PUT'])`
### `def update_rule_api(rule_id)`
**Purpose**: Updates existing automation rule.

**HTTP Method**: PUT

**Parameters**: `rule_id` in URL path

**Request Body**: Updated rule definition

**Returns**: JSON success response

---

### `@app.route('/api/rules/<rule_id>', methods=['DELETE'])`
### `def delete_rule_api(rule_id)`
**Purpose**: Deletes automation rule.

**HTTP Method**: DELETE

**Parameters**: `rule_id` in URL path

**Returns**: JSON success response

---

### `@app.route('/api/rules/<rule_id>/toggle', methods=['POST'])`
### `def toggle_rule_api(rule_id)`
**Purpose**: Toggles rule active status.

**HTTP Method**: POST

**Parameters**: `rule_id` in URL path

**Returns**: JSON success response

---

### `@app.route('/api/rules/reset', methods=['POST'])`
### `def reset_rules()`
**Purpose**: Resets all rules to default configuration.

**HTTP Method**: POST

**Returns**: JSON success response

---

## Template Generation Methods

### `create_html_template()`
**Purpose**: Generates the main dashboard HTML template.

**Parameters**: None

**Returns**: None (writes to file)

**File Created**: `templates/index.html`

**Features**:
- Responsive design
- Real-time system status
- Control panels for all devices
- Bootstrap styling
- WebSocket integration

---

### `create_automation_template()`
**Purpose**: Generates the automation rules management HTML template.

**Parameters**: None

**Returns**: None (writes to file)

**File Created**: `templates/automation.html`

**Features**:
- Rule creation interface
- Rule editing and deletion
- Condition and action builders
- Real-time rule status

---

### `create_css_file()`
**Purpose**: Generates CSS stylesheet for web interface.

**Parameters**: None

**Returns**: None (writes to file)

**File Created**: `static/css/style.css`

**Features**:
- Modern responsive design
- Dark/light theme support
- Animation effects
- Mobile-friendly layout

---

## System Integration

### Main Execution Flow
1. **Initialization**: GPIO setup, sensor initialization, default rules loading
2. **Thread Startup**: Sensor monitoring thread starts
3. **Flask Server**: Web interface starts on port 5000
4. **Continuous Operation**: System runs until interrupted

### Error Handling
- All methods include comprehensive exception handling
- Logging for debugging and monitoring
- Graceful degradation on sensor failures
- GPIO cleanup on system shutdown

### Performance Considerations
- Sensor reading optimized for 1-second intervals
- Non-blocking operations using threading
- Efficient GPIO state management
- Memory-conscious data structures

### Security Features
- Input validation on all API endpoints
- Safe GPIO operations
- Emergency shutdown procedures
- Access logging and monitoring

---

## Configuration

### Default Thresholds
- Temperature: 25.0°C
- Gas detection: Digital + analog threshold
- Motion sensitivity: PIR sensor dependent
- Auto-close delay: 120 seconds

### GPIO Pin Assignments
All pin assignments are documented in the hardware compatibility report and can be verified using `verify_gpio_pinouts.py`.

### File Locations
- Configuration: `automation_rules.json`
- Templates: `templates/` directory
- Static files: `static/` directory
- Logs: Console output with configurable levels

This documentation covers all methods in the smart home system. Each method is designed for reliability, efficiency, and integration with the overall home automation ecosystem.