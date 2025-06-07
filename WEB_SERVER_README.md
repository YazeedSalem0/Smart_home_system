# Smart Home Web Server

A modern, responsive web interface for the Smart Home Automation System. This web server acts as a dedicated interface that communicates with the main smart home system running on the Raspberry Pi.

## Features

### 🏠 Dashboard
- Real-time system status overview
- Temperature and humidity monitoring
- Motion detection indicators
- Security status (door lock, garage, face recognition)
- Lighting status with color indicators
- Quick action buttons
- Recent activity log

### 🎛️ Controls
- Manual fan control with auto mode toggle
- Individual room lighting control
- Security system controls (door lock, garage)
- System-wide controls (emergency stop, all lights)
- Manual override status monitoring

### 🤖 Automation
- Create, edit, and delete automation rules
- Condition-based triggers (temperature, motion, time, etc.)
- Multiple action types (fan, lights, door, alerts)
- Rule activation/deactivation
- Visual rule management interface

### 📊 Monitoring
- Real-time sensor data charts
- Device status grid with visual indicators
- System logs with real-time updates
- Data export functionality
- Historical data visualization

### ⚙️ Settings
- System configuration options
- Connection settings and testing
- Settings import/export
- System diagnostics
- Console log monitoring

## Installation

### Prerequisites
- Python 3.7 or higher
- The main smart home system running on port 5000

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r web_requirements.txt
   ```

2. **Run the web server:**
   ```bash
   python web_server.py
   ```

3. **Access the interface:**
   Open your browser and navigate to `http://localhost:8080`

## Architecture

### System Components

```
┌─────────────────┐    HTTP/WebSocket    ┌──────────────────┐
│   Web Browser   │ ◄─────────────────► │   Web Server     │
│   (Port 8080)   │                     │   (Port 8080)    │
└─────────────────┘                     └──────────────────┘
                                                   │
                                                   │ HTTP API
                                                   ▼
                                        ┌──────────────────┐
                                        │ Smart Home System│
                                        │   (Port 5000)    │
                                        └──────────────────┘
                                                   │
                                                   │ GPIO/Sensors
                                                   ▼
                                        ┌──────────────────┐
                                        │ Raspberry Pi     │
                                        │ Hardware         │
                                        └──────────────────┘
```

### File Structure

```
├── web_server.py              # Main web server application
├── templates/                 # HTML templates
│   ├── base.html             # Base template with navigation
│   ├── dashboard.html        # Main dashboard
│   ├── controls.html         # Device controls
│   ├── automation.html       # Automation rules
│   ├── monitoring.html       # Real-time monitoring
│   └── settings.html         # System settings
├── static/                   # Static assets
│   ├── css/
│   │   └── style.css        # Custom styles
│   └── js/
│       └── main.js          # Main JavaScript functionality
├── web_requirements.txt      # Python dependencies
└── WEB_SERVER_README.md     # This file
```

## Configuration

### Environment Variables
- `SMART_HOME_API_BASE`: URL of the main smart home system (default: `http://localhost:5000/api`)
- `UPDATE_INTERVAL`: Update frequency in seconds (default: 2)
- `WEB_SERVER_PORT`: Port for the web server (default: 8080)

### Settings
The web interface includes a settings page where you can configure:
- Update intervals
- Temperature thresholds
- Notification preferences
- Connection settings

## API Endpoints

### Dashboard Data
- `GET /api/dashboard/data` - Get current system status

### Device Control
- `POST /api/control/fan` - Control fan system
- `POST /api/control/light` - Control lighting
- `POST /api/control/door` - Control door lock
- `POST /api/control/garage` - Control garage door

### Automation Rules
- `GET /api/automation/rules` - Get all automation rules
- `POST /api/automation/rules` - Create new rule
- `PUT /api/automation/rules/<id>` - Update existing rule
- `DELETE /api/automation/rules/<id>` - Delete rule
- `POST /api/automation/rules/<id>/toggle` - Toggle rule status

## Real-time Communication

The web server uses WebSocket connections for real-time updates:

### WebSocket Events
- `connect` - Client connected
- `disconnect` - Client disconnected
- `request_update` - Request system data update
- `system_update` - Broadcast system data to clients

## Usage

### Starting the System

1. **Start the main smart home system:**
   ```bash
   python smart_home_system.py
   ```

2. **Start the web server:**
   ```bash
   python web_server.py
   ```

3. **Access the web interface:**
   Navigate to `http://localhost:8080` in your browser

### Navigation

- **Dashboard**: Overview of all system components
- **Controls**: Manual control of devices
- **Automation**: Manage automation rules
- **Monitoring**: Real-time charts and logs
- **Settings**: System configuration

### Creating Automation Rules

1. Go to the Automation page
2. Click "Add Rule"
3. Configure the condition (trigger)
4. Set the action to perform
5. Save the rule

Example rule: "When temperature > 25°C, turn on fans"

### Monitoring System Health

The monitoring page provides:
- Real-time temperature and humidity charts
- Device status indicators
- System logs
- Data export capabilities

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Ensure the main smart home system is running on port 5000
   - Check network connectivity
   - Verify firewall settings

2. **Real-time Updates Not Working**
   - Check WebSocket connection in browser developer tools
   - Ensure no proxy is blocking WebSocket connections
   - Try refreshing the page

3. **Controls Not Responding**
   - Verify the main system is responding to API calls
   - Check the connection status in Settings
   - Review console logs for errors

### Debug Mode

To enable debug logging, modify `web_server.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Browser Compatibility

Supported browsers:
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Security Considerations

- The web server runs on localhost by default
- For remote access, consider using a reverse proxy with SSL
- Implement authentication for production use
- Regular security updates recommended

## Development

### Adding New Features

1. **Backend**: Add new routes in `web_server.py`
2. **Frontend**: Create/modify templates in `templates/`
3. **Styling**: Update `static/css/style.css`
4. **JavaScript**: Add functionality to `static/js/main.js`

### Testing

Test the web interface by:
1. Running the main smart home system
2. Starting the web server
3. Accessing all pages and features
4. Verifying real-time updates
5. Testing device controls

## License

This project is part of the Smart Home Automation System. See the main project for license information.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review console logs
3. Test connection to the main system
4. Verify all dependencies are installed 