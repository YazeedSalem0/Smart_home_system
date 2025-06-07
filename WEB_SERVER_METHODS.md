# Web Server Methods Documentation

## Overview
This document provides comprehensive documentation for all methods used in `web_server.py`. The web server provides a dedicated web interface for the Smart Home Automation System, offering real-time monitoring, device control, and automation management through a modern web dashboard.

## Table of Contents
1. [System Communication](#system-communication)
2. [Web Route Handlers](#web-route-handlers)
3. [API Endpoints](#api-endpoints)
4. [WebSocket Events](#websocket-events)
5. [Background Services](#background-services)
6. [Configuration and Setup](#configuration-and-setup)

---

## System Communication

### `get_system_state()`
**Purpose**: Retrieves current system state from the main smart home system via API.

**Parameters**: None

**Returns**: dict - System state data, or None if connection failed

**API Integration**:
- **Endpoint**: `http://localhost:5000/api/state`
- **Method**: GET
- **Timeout**: 5 seconds
- **Error Handling**: Connection errors, timeouts, HTTP errors

**Response Caching**:
- Updates `cached_state['system_data']` on success
- Sets `cached_state['last_update']` timestamp
- Updates `cached_state['connection_status']`

**Usage Example**:
```python
state = get_system_state()
if state:
    temperature = state['temperature']
    motion_status = state['motion']
    print(f"Temperature: {temperature}°C")
else:
    print("Unable to connect to smart home system")
```

**Error Conditions**:
- **ConnectionError**: Main system not running or network issues
- **Timeout**: System overloaded or network latency
- **HTTP Errors**: Invalid API responses
- **JSON Errors**: Malformed response data

**Logging**: All errors logged with appropriate severity levels.

---

### `send_control_command(endpoint, data)`
**Purpose**: Sends control commands to the main smart home system.

**Parameters**:
- `endpoint` (str): API endpoint path (e.g., 'control/fan', 'control/light')
- `data` (dict): Command data to send as JSON

**Returns**: bool - True if command sent successfully, False otherwise

**API Integration**:
- **Base URL**: `http://localhost:5000/api/`
- **Method**: POST
- **Content-Type**: application/json
- **Timeout**: 5 seconds

**Usage Examples**:
```python
# Control fan
success = send_control_command('control/fan', {'command': 'on'})

# Control lighting
success = send_control_command('control/light', {
    'room': 'Room1',
    'command': 'white'
})

# Control door
success = send_control_command('control/door', {'lock': False})
```

**Error Handling**:
- **Connection Errors**: Network connectivity issues
- **Timeout Errors**: System response delays
- **HTTP Errors**: Invalid endpoints or server errors
- **JSON Errors**: Malformed request data

**Logging**: Detailed logging of all command attempts and results.

---

### `get_automation_rules()`
**Purpose**: Retrieves automation rules from the main smart home system.

**Parameters**: None

**Returns**: list - List of automation rules, or empty list on error

**API Integration**:
- **Endpoint**: `http://localhost:5000/api/rules`
- **Method**: GET
- **Timeout**: 5 seconds

**Rule Structure**:
```python
[
    {
        'id': 'rule1',
        'name': 'Temperature Fan Control',
        'condition': {
            'type': 'temperature',
            'operator': '>',
            'value': 25.0
        },
        'action': {
            'type': 'fan',
            'command': 'on'
        },
        'active': True
    }
]
```

**Usage Example**:
```python
rules = get_automation_rules()
active_rules = [rule for rule in rules if rule['active']]
print(f"Found {len(active_rules)} active automation rules")
```

---

## Web Route Handlers

### `@app.route('/')`
### `dashboard()`
**Purpose**: Serves the main dashboard page with system overview.

**HTTP Method**: GET

**Parameters**: None

**Returns**: HTML template response

**Template**: `templates/dashboard.html`

**Features**:
- Real-time system status display
- Quick control panels
- System health indicators
- Recent activity summary

**URL**: `http://localhost:8080/`

---

### `@app.route('/controls')`
### `controls()`
**Purpose**: Serves the device controls page for manual system operation.

**HTTP Method**: GET

**Parameters**: None

**Returns**: HTML template response

**Template**: `templates/controls.html`

**Features**:
- Individual device control panels
- Manual override controls
- System mode toggles
- Real-time status updates

**URL**: `http://localhost:8080/controls`

---

### `@app.route('/automation')`
### `automation()`
**Purpose**: Serves the automation rules management page.

**HTTP Method**: GET

**Parameters**: None

**Returns**: HTML template response

**Template**: `templates/automation.html`

**Features**:
- Rule creation interface
- Rule editing and deletion
- Condition and action builders
- Rule activation toggles

**URL**: `http://localhost:8080/automation`

---

### `@app.route('/monitoring')`
### `monitoring()`
**Purpose**: Serves the real-time monitoring page with live data feeds.

**HTTP Method**: GET

**Parameters**: None

**Returns**: HTML template response

**Template**: `templates/monitoring.html`

**Features**:
- Live sensor data graphs
- Real-time event logs
- System performance metrics
- Historical data visualization

**URL**: `http://localhost:8080/monitoring`

---

### `@app.route('/settings')`
### `settings()`
**Purpose**: Serves the system settings and configuration page.

**HTTP Method**: GET

**Parameters**: None

**Returns**: HTML template response

**Template**: `templates/settings.html`

**Features**:
- System configuration options
- User preferences
- Network settings
- Backup and restore functions

**URL**: `http://localhost:8080/settings`

---

## API Endpoints

### `@app.route('/api/dashboard/data')`
### `dashboard_data()`
**Purpose**: Provides dashboard data for real-time updates.

**HTTP Method**: GET

**Parameters**: None

**Returns**: JSON response with dashboard data

**Response Format**:
```json
{
    "success": true,
    "data": {
        "motion": {"Room1": false, "Room2": true},
        "temperature": 24.5,
        "humidity": 60.0,
        "gas_detected": false,
        "fans_on": true,
        "door_locked": true,
        "garage_door_open": false
    },
    "connection_status": true,
    "last_update": "2024-01-01T12:30:45"
}
```

**Error Response**:
```json
{
    "success": false,
    "error": "Unable to connect to smart home system",
    "connection_status": false
}
```

**Usage**: Called by frontend JavaScript for real-time dashboard updates.

---

### `@app.route('/api/control/fan', methods=['POST'])`
### `control_fan()`
**Purpose**: API endpoint for fan system control.

**HTTP Method**: POST

**Request Body**:
```json
{
    "command": "on|off|toggle"
}
```

**Returns**: JSON success response

**Response Format**:
```json
{
    "success": true
}
```

**Usage Example**:
```javascript
fetch('/api/control/fan', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({command: 'on'})
})
.then(response => response.json())
.then(data => console.log('Fan control:', data.success));
```

---

### `@app.route('/api/control/light', methods=['POST'])`
### `control_light()`
**Purpose**: API endpoint for lighting system control.

**HTTP Method**: POST

**Request Body**:
```json
{
    "room": "Room1|Room2|Room3|LivingRoom|all",
    "command": "on|off|white|red"
}
```

**Returns**: JSON success response

**Usage Example**:
```javascript
// Turn on white light in Room1
fetch('/api/control/light', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        room: 'Room1',
        command: 'white'
    })
});
```

---

### `@app.route('/api/control/door', methods=['POST'])`
### `control_door()`
**Purpose**: API endpoint for door lock control.

**HTTP Method**: POST

**Request Body**:
```json
{
    "lock": true|false
}
```

**Returns**: JSON success response

**Security Note**: Door control commands are logged for security audit.

**Usage Example**:
```javascript
// Unlock door
fetch('/api/control/door', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({lock: false})
});
```

---

### `@app.route('/api/control/garage', methods=['POST'])`
### `control_garage()`
**Purpose**: API endpoint for garage door control.

**HTTP Method**: POST

**Request Body**:
```json
{
    "open": true|false
}
```

**Returns**: JSON success response

**Features**:
- Auto-close timer management
- Safety interlocks
- Status tracking

**Usage Example**:
```javascript
// Open garage door
fetch('/api/control/garage', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({open: true})
});
```

---

### `@app.route('/api/automation/rules')`
### `get_rules()`
**Purpose**: Retrieves all automation rules for management interface.

**HTTP Method**: GET

**Parameters**: None

**Returns**: JSON response with rules array

**Response Format**:
```json
{
    "success": true,
    "rules": [
        {
            "id": "rule1",
            "name": "Temperature Control",
            "condition": {...},
            "action": {...},
            "active": true
        }
    ]
}
```

---

### `@app.route('/api/automation/rules', methods=['POST'])`
### `create_rule()`
**Purpose**: Creates a new automation rule.

**HTTP Method**: POST

**Request Body**: Complete rule definition

**Returns**: JSON success response

**Rule Creation Process**:
1. Validates rule structure
2. Sends to main system
3. Returns creation status

**Usage Example**:
```javascript
const newRule = {
    name: 'Night Security',
    condition: {
        type: 'time',
        operator: '==',
        value: '22:00'
    },
    action: {
        type: 'light',
        command: 'on',
        location: 'all'
    },
    active: true
};

fetch('/api/automation/rules', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(newRule)
});
```

---

### `@app.route('/api/automation/rules/<rule_id>', methods=['PUT'])`
### `update_rule(rule_id)`
**Purpose**: Updates an existing automation rule.

**HTTP Method**: PUT

**Parameters**:
- `rule_id` (str): Rule identifier in URL path

**Request Body**: Updated rule definition

**Returns**: JSON success response

**Usage Example**:
```javascript
const updatedRule = {
    name: 'Updated Night Security',
    active: false
};

fetch('/api/automation/rules/rule1', {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(updatedRule)
});
```

---

### `@app.route('/api/automation/rules/<rule_id>', methods=['DELETE'])`
### `delete_rule(rule_id)`
**Purpose**: Deletes an automation rule.

**HTTP Method**: DELETE

**Parameters**:
- `rule_id` (str): Rule identifier in URL path

**Returns**: JSON success response

**Usage Example**:
```javascript
fetch('/api/automation/rules/rule1', {
    method: 'DELETE'
});
```

---

### `@app.route('/api/automation/rules/<rule_id>/toggle', methods=['POST'])`
### `toggle_rule(rule_id)`
**Purpose**: Toggles the active status of an automation rule.

**HTTP Method**: POST

**Parameters**:
- `rule_id` (str): Rule identifier in URL path

**Returns**: JSON success response

**Usage Example**:
```javascript
// Toggle rule active status
fetch('/api/automation/rules/rule1/toggle', {
    method: 'POST'
});
```

---

## WebSocket Events

### `@socketio.on('connect')`
### `handle_connect()`
**Purpose**: Handles new WebSocket client connections.

**Parameters**: None (automatic Flask-SocketIO parameter)

**Returns**: None

**Actions**:
1. Logs client connection
2. Sends welcome message to client
3. Initializes client session

**Client Message**:
```json
{
    "msg": "Connected to Smart Home Server"
}
```

**Usage**: Automatically called when client establishes WebSocket connection.

---

### `@socketio.on('disconnect')`
### `handle_disconnect()`
**Purpose**: Handles WebSocket client disconnections.

**Parameters**: None

**Returns**: None

**Actions**:
1. Logs client disconnection
2. Cleans up client session data
3. Updates connection statistics

**Usage**: Automatically called when client closes WebSocket connection.

---

### `@socketio.on('request_update')`
### `handle_update_request()`
**Purpose**: Handles client requests for immediate system updates.

**Parameters**: None

**Returns**: None (sends data via WebSocket emit)

**Process**:
1. Retrieves current system state
2. Formats data for client
3. Emits update to requesting client

**Emitted Event**: `system_update`

**Data Format**:
```json
{
    "data": {...},
    "timestamp": "2024-01-01T12:30:45",
    "connection_status": true
}
```

**Usage**: Called when client needs immediate data refresh.

---

## Background Services

### `background_updater()`
**Purpose**: Background thread that sends periodic system updates to all connected clients.

**Parameters**: None

**Returns**: None (runs indefinitely)

**Update Process**:
1. **Data Retrieval**: Gets current system state
2. **Broadcasting**: Sends update to all connected clients
3. **Timing**: Waits for `UPDATE_INTERVAL` (2 seconds)
4. **Error Handling**: Continues operation despite individual errors

**Emitted Event**: `system_update`

**Performance Considerations**:
- **Update Frequency**: Configurable via `UPDATE_INTERVAL`
- **Error Recovery**: Continues operation on API failures
- **Resource Management**: Efficient data formatting and transmission

**Usage**: Automatically started as daemon thread during server initialization.

**Thread Configuration**:
```python
updater_thread = threading.Thread(target=background_updater)
updater_thread.daemon = True
updater_thread.start()
```

---

## Configuration and Setup

### Global Configuration Variables

#### `SMART_HOME_API_BASE`
**Purpose**: Base URL for smart home system API communication.

**Value**: `"http://localhost:5000/api"`

**Usage**: Prefix for all API endpoint calls to main system.

---

#### `UPDATE_INTERVAL`
**Purpose**: Interval between background updates in seconds.

**Value**: `2` (seconds)

**Usage**: Controls frequency of real-time data updates to clients.

---

#### `cached_state`
**Purpose**: Global state cache for system data and connection status.

**Structure**:
```python
{
    'last_update': datetime,     # Timestamp of last successful update
    'system_data': dict,         # Cached system state data
    'connection_status': bool    # Connection status to main system
}
```

**Usage**: Provides cached data when main system is temporarily unavailable.

---

### Flask Application Configuration

#### `app.config['SECRET_KEY']`
**Purpose**: Secret key for Flask session management and security.

**Value**: `'smart_home_secret_key_2024'`

**Security Note**: Should be changed in production deployment.

---

#### `socketio = SocketIO(app, cors_allowed_origins="*")`
**Purpose**: WebSocket configuration for real-time communication.

**Features**:
- **CORS**: Allows connections from any origin
- **Real-time**: Bidirectional communication
- **Event-driven**: Custom event handling

---

### Main Execution Block

#### Server Initialization Process
```python
if __name__ == '__main__':
    # Create required directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Start background services
    updater_thread = threading.Thread(target=background_updater)
    updater_thread.daemon = True
    updater_thread.start()
    
    # Server startup messages
    print("Smart Home Web Server starting...")
    print("Dashboard will be available at: http://localhost:8080")
    print("Make sure the main smart home system is running on port 5000")
    
    # Start web server
    socketio.run(app, host='0.0.0.0', port=8080, debug=False)
```

**Startup Process**:
1. **Directory Creation**: Ensures required directories exist
2. **Background Services**: Starts update thread
3. **User Information**: Displays access URLs and requirements
4. **Server Launch**: Starts Flask-SocketIO server

**Server Configuration**:
- **Host**: `0.0.0.0` (accepts connections from any IP)
- **Port**: `8080`
- **Debug**: Disabled for production stability

---

## Integration Architecture

### Communication Flow
1. **Client Request**: Web browser sends HTTP/WebSocket request
2. **Web Server**: Processes request and validates parameters
3. **API Call**: Forwards command to main smart home system
4. **Response**: Returns result to client
5. **Real-time Updates**: Background thread broadcasts system changes

### Error Handling Strategy
- **Connection Resilience**: Graceful handling of main system unavailability
- **User Feedback**: Clear error messages for failed operations
- **Logging**: Comprehensive logging for debugging and monitoring
- **Fallback**: Cached data when real-time data unavailable

### Security Considerations
- **Input Validation**: All API inputs validated before forwarding
- **CORS Policy**: Configurable cross-origin access
- **Session Management**: Secure session handling
- **Audit Logging**: All control commands logged

### Performance Optimizations
- **Caching**: System state caching reduces API calls
- **Efficient Updates**: Targeted data updates via WebSocket
- **Thread Management**: Background processing doesn't block requests
- **Resource Management**: Proper cleanup and resource deallocation

This comprehensive documentation covers all methods and functionality in the web server system, providing detailed information for development, deployment, and maintenance of the smart home web interface. 