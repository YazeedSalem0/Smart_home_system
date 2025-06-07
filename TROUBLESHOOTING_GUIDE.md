# Smart Home System Troubleshooting Guide

## Overview
This guide helps diagnose and fix common issues with the Smart Home System, particularly focusing on web server connectivity and PIR sensor problems.

## Quick Diagnosis

### 1. Run System Tests
```bash
# Test PIR sensor connections
python test_pir_connection.py

# Test system connectivity
python test_system_connectivity.py

# Test individual PIR sensor (replace Room1 with desired room)
python test_pir_connection.py Room1
```

## Common Issues and Solutions

### Issue 1: Web Server Cannot Connect to Main System

**Symptoms:**
- Web server shows "Unable to connect to smart home system"
- Dashboard shows connection_status: false
- API calls return success: false

**Diagnosis:**
```bash
# Check if main system is running
netstat -an | findstr :5000

# Test main system API directly
curl http://localhost:5000/api/state
```

**Solutions:**

1. **Start the Main System:**
   ```bash
   python smart_home_system.py
   ```

2. **Check Port Conflicts:**
   ```bash
   # Kill any process using port 5000
   netstat -ano | findstr :5000
   taskkill /PID <PID_NUMBER> /F
   ```

3. **Verify API Endpoints:**
   - Main system should provide: `/api/state`, `/api/control/fan`, etc.
   - Check `smart_home_system.py` for correct Flask routes

### Issue 2: PIR Sensors Not Working

**Symptoms:**
- Motion detection not triggering
- LEDs not responding to motion
- GPIO errors in logs

**Diagnosis:**
```bash
# Test all PIR sensors
python test_pir_connection.py

# Test specific sensor
python test_pir_connection.py Room1
```

**Common Causes and Solutions:**

1. **GPIO Pin Conflicts:**
   - **Problem:** Using GPIO 0/1 (I2C pins) for LEDs
   - **Solution:** Updated to use GPIO 2/3 for LivingRoom LEDs
   - **Verification:** Run `python test_pir_connection.py` to check conflicts

2. **Wiring Issues:**
   - **VCC:** Connect to 5V (Pin 2 or 4)
   - **GND:** Connect to Ground (Pin 6, 9, 14, 20, 25, 30, 34, 39)
   - **OUT:** Connect to assigned GPIO pin
   - **Verify:** Check continuity with multimeter

3. **PIR Sensor Calibration:**
   - Allow 30-60 seconds warm-up time
   - Adjust sensitivity potentiometer (if available)
   - Check detection range (typically 3-7 meters)

### Issue 3: GPIO Permission Errors

**Symptoms:**
- "Permission denied" errors
- GPIO setup failures
- Cannot access /dev/gpiomem

**Solutions:**
```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Set GPIO permissions
sudo chmod 666 /dev/gpiomem

# Reboot to apply changes
sudo reboot
```

### Issue 4: Web Server Template Errors

**Symptoms:**
- 404 errors for web pages
- Missing templates
- Static files not loading

**Solutions:**
```bash
# Create required directories
mkdir -p templates static/css static/js

# Run web server to auto-create templates
python web_server.py
```

### Issue 5: I2C Communication Errors

**Symptoms:**
- ADS1115 not responding
- Gas sensor readings fail
- I2C device not found

**Solutions:**
```bash
# Enable I2C
sudo raspi-config
# Navigate to: Interface Options > I2C > Enable

# Check I2C devices
sudo i2cdetect -y 1

# Install I2C tools
sudo apt-get install i2c-tools
```

## GPIO Pin Configuration

### Current Pin Assignments:
```
GPIO  2: LivingRoom LED Red / I2C SDA
GPIO  3: LivingRoom LED Green / I2C SCL
GPIO  4: DHT11 Temperature Sensor
GPIO  5: Room1 LED Red
GPIO  6: Room1 LED Green
GPIO  7: Motor B Control
GPIO  8: Motor B Control
GPIO  9: Buzzer
GPIO 10: Door Servo
GPIO 11: Garage Servo
GPIO 12: Room3 LED Blue
GPIO 13: Room1 LED Blue
GPIO 14: LivingRoom LED Blue
GPIO 15: IR Sensor
GPIO 16: Room2 LED Blue
GPIO 17: PIR Room1
GPIO 18: Motor A Control
GPIO 19: Room2 LED Red
GPIO 20: Room3 LED Red
GPIO 21: Room3 LED Green
GPIO 22: PIR Room3
GPIO 23: PIR LivingRoom
GPIO 24: Gas Sensor Digital
GPIO 25: Motor A Control
GPIO 26: Room2 LED Green
GPIO 27: PIR Room2
```

### PIR Sensor Connections:
- **Room1:** GPIO 17
- **Room2:** GPIO 27
- **Room3:** GPIO 22
- **LivingRoom:** GPIO 23

## System Architecture

### Main System (Port 5000)
- Handles hardware control
- Provides REST API
- Manages automation rules
- Real-time sensor monitoring

### Web Server (Port 8080)
- Web interface
- Proxies API calls to main system
- WebSocket for real-time updates
- Dashboard and controls

## Debugging Commands

### Check System Status:
```bash
# Check running processes
ps aux | grep python

# Check port usage
netstat -tulpn | grep :5000
netstat -tulpn | grep :8080

# Check GPIO status
gpio readall  # (if wiringpi installed)
```

### Test Individual Components:
```bash
# Test temperature sensor
python -c "import Adafruit_DHT; print(Adafruit_DHT.read_retry(11, 4))"

# Test I2C
sudo i2cdetect -y 1

# Test GPIO
python -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(17, GPIO.IN); print(GPIO.input(17))"
```

## Log Analysis

### Enable Detailed Logging:
```python
# Add to your Python scripts
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Log Messages:
- `Connection error to smart home system`: Main system not running
- `GPIO already in use`: Pin conflict or cleanup needed
- `Permission denied`: GPIO permissions issue
- `Timeout`: Network or hardware communication timeout

## Recovery Procedures

### Complete System Reset:
```bash
# Stop all processes
pkill -f python

# Clean GPIO
python -c "import RPi.GPIO as GPIO; GPIO.cleanup()"

# Restart services
python smart_home_system.py &
python web_server.py &
```

### Factory Reset Configuration:
```bash
# Remove automation rules
rm -f automation_rules.json

# Restart with defaults
python smart_home_system.py
```

## Performance Optimization

### Reduce CPU Usage:
- Increase sensor polling intervals
- Optimize GPIO operations
- Use hardware PWM where possible

### Improve Response Time:
- Reduce API timeout values
- Use connection pooling
- Cache frequently accessed data

## Getting Help

### Collect Debug Information:
```bash
# System info
uname -a
python --version
pip list | grep -E "(RPi|Adafruit|Flask)"

# GPIO state
gpio readall

# Process info
ps aux | grep python
netstat -tulpn | grep -E "(5000|8080)"
```

### Report Issues:
Include the following in bug reports:
1. Error messages and logs
2. GPIO pin configuration
3. Hardware setup description
4. Steps to reproduce
5. System information from above commands

## Preventive Maintenance

### Regular Checks:
- Monitor GPIO pin assignments
- Check for loose connections
- Update software dependencies
- Test backup/restore procedures
- Verify automation rules

### Best Practices:
- Always use GPIO.cleanup() in exception handlers
- Implement proper error handling
- Use appropriate timeouts
- Monitor system resources
- Keep logs for troubleshooting 