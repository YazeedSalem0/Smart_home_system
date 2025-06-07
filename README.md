# Smart Home Automation System

A complete Raspberry Pi-based smart home automation system with motion detection, temperature monitoring, gas leak detection, face recognition door lock, LED display, sound alert capabilities, and customizable automation rules.

## Features

- **Motion Detection**: PIR sensors detect motion in each room and turn on RGB LEDs (white color)
- **Temperature Monitoring**: DHT11 sensor monitors temperature and humidity in the living room
- **Fan Control**: Automatically activates fans when temperature exceeds 25°C
- **Gas Leak Detection**: MQ-7 sensor detects gas leaks and triggers emergency alert (flashing red LEDs and alarm sound)
- **Face Recognition Door Lock**: Advanced face recognition system for secure door access control
- **LED Display**: 0802A LED display shows system information (temperature, gas status, door status)
- **Sound Alerts**: Piezo buzzer provides audio feedback for various events (gas alerts, door operation, authorized/unauthorized access)
- **Customizable Automation**: Create and manage automation rules through the web interface
- **Web Interface**: Control and monitor the entire system through a responsive web interface

## Hardware Requirements

See `hardware_documentation.md` for a complete list of components and wiring instructions.

## Dependencies

Install the required Python packages:

```bash
pip3 install -r requirements.txt
# For face recognition (optional):
pip3 install -r face_recognition_requirements.txt
```

## Directory Structure

```
smart-home-system/
├── hardware_documentation.md       # Hardware components and wiring details
├── test_motion_detection.py        # Test script for PIR sensors (Part 2)
├── test_temperature_fan.py         # Test script for DHT11 and fan control (Part 3)
├── test_gas_detection.py           # Test script for gas sensor (Part 4)
├── test_garage_ir.py               # Test script for garage door and IR sensor (Part 7)
├── test_buzzer.py                  # Test script for buzzer (Part 8)
├── test_l298n_motor_driver.py      # Test script for motor driver (Part 9)
├── test_face_recognition.py        # Test script for face recognition system
├── face_recognition_door.py        # Face recognition door access control
├── verify_system.py                # Complete system verification
├── automation_rules.json           # Saved automation rules configuration
├── smart_home_system.py            # Main system file
├── requirements.txt                # Python dependencies
├── setup_raspberry_pi.sh           # Automated setup script
├── PRE_DEPLOYMENT_CHECKLIST.md     # Pre-deployment verification checklist
├── WEB_SERVER_README.md            # Web server documentation
├── web_server.py                   # Separate web interface server
├── web_requirements.txt            # Web server dependencies
├── static/                         # Web interface assets
│   ├── css/
│   └── js/
└── templates/                      # HTML templates
```

## Setup Instructions

1. Connect the hardware components according to the `hardware_documentation.md` file.
2. Install the required dependencies listed above.
3. Test individual components using the separate test scripts:

```bash
# Test individual components
python3 test_motion_detection.py
python3 test_temperature_fan.py
python3 test_gas_detection.py
python3 test_garage_ir.py
python3 test_buzzer.py
python3 test_l298n_motor_driver.py

# Run complete system verification
python3 verify_system.py

# Start the main system
python3 smart_home_system.py
```

4. Once all components are working individually, run the integrated system:

```bash
python3 smart_home_system.py
```

5. Access the web interface by opening a browser and navigating to:

```
http://[Raspberry Pi IP Address]:5000
```

## Testing the System

### Motion Detection
- Move in front of PIR sensors to see LED response
- LEDs should turn white when motion is detected and turn off when no motion is detected

### Temperature Control
- Monitor temperature readings in the web interface
- Fans should turn on automatically when temperature exceeds 25°C
- Use manual controls to override fan behavior if needed

### Gas Leak Detection
- When a gas leak is detected, all LEDs should flash red
- A loud, urgent alarm sound will be played repeatedly
- The web interface will show an emergency alert
- The LED display will show a warning message
- Once the gas level returns to normal, the system should return to normal operation

### Face Recognition Door Lock
- Stand in front of the camera
- If your face is recognized, the door will unlock with a welcome sound
- If your face is not recognized, an "unauthorized access" sound will play
- The LED display and web interface will show the recognized person's name
- The door will lock automatically after a few seconds with a door-closing sound

### Sound Alerts
The system has different audio patterns for various events:
- Gas leak: Urgent, high-pitched beep pattern
- Door opening: Ascending tone sequence
- Door closing: Descending tone sequence
- Unauthorized access: Two low beeps
- Welcome/recognized user: Pleasant melody

### LED Display
- The display cycles through different screens showing:
  - Temperature and humidity readings
  - Gas sensor status
  - Door lock status and face recognition results
  - General system status

## Notes

- MQ-7 sensor requires a warm-up period of about 1-2 minutes
- PIR sensors may need 30-60 seconds to stabilize after power-up
- The system creates necessary web files automatically on first run
- The face recognition system may require good lighting for accurate results

## Troubleshooting

- If GPIO pins aren't working properly, check wiring connections and ensure there are no shorts
- For sensor issues, test components individually using the test scripts
- Check that all required Python packages are installed
- Ensure Raspberry Pi has proper network connectivity for web interface access
- If the LCD display shows incorrect characters, verify the I2C address (default 0x27)
- For face recognition issues, ensure good lighting and proper camera positioning

## Future Enhancements

- Add user authentication for the web interface
- Implement MQTT for remote access
- Add data logging and analytics
- Integrate with voice assistants like Alexa or Google Home 
- Add mobile app notification for unauthorized access attempts

## Automation Rules

The system includes a powerful automation rules engine that allows you to create custom behaviors:

### Rule Components

Each automation rule consists of:
- **Condition**: What triggers the rule (temperature, humidity, motion, gas detection, time)
- **Action**: What happens when the condition is met (fan control, light control, door control, alerts)

### Managing Rules

Access the automation rules manager by clicking "Manage Automation Rules" on the main dashboard.

From there, you can:
- **View** existing rules
- **Add** new rules
- **Edit** existing rules
- **Enable/Disable** rules
- **Delete** rules
- **Reset** to default rules

### Default Rules

The system comes with three default rules:
1. **Temperature Fan Control**: Turn on fans when temperature exceeds 25°C
2. **Motion Light Control**: Turn on lights in rooms where motion is detected
3. **Gas Emergency**: Trigger emergency mode when gas is detected

### Example Custom Rules

You can create many custom rules, such as:
- Turn on all lights at a specific time of day
- Lock the door automatically after a certain time
- Play welcome sounds when motion is detected during certain hours
- Turn on fans when humidity exceeds a threshold
- Trigger custom alerts based on specific sensor events 