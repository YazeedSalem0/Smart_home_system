# Smart Home Automation System - Hardware Documentation

## Overview
This document provides comprehensive information about the hardware components, wiring, and setup for the Smart Home Automation System running on Raspberry Pi 4.

## Hardware Components List

### Core Components
| Component | Quantity | Purpose |
|-----------|----------|---------|
| Raspberry Pi 4 | 1 | Main controller |
| MicroSD Card (32GB+) | 1 | Operating system and storage |
| Power Supply (5V 3A) | 1 | Power for Raspberry Pi |
| Breadboard (Large) | 1 | Component connections |
| Jumper Wires | 40+ | Connections |

### Sensors and Input Devices
| Component | Quantity | Purpose |
|-----------|----------|---------|
| PIR Motion Sensors | 4 | Motion detection in different rooms |
| DHT11 Temperature/Humidity Sensor | 1 | Environmental monitoring |
| MQ-7 Gas Sensor | 1 | Carbon monoxide detection |
| ADS1115 ADC Module | 1 | Analog-to-digital conversion for gas sensor |
| IR Sensor | 1 | Garage door fingerprint detection |

### Output Devices
| Component | Quantity | Purpose |
|-----------|----------|---------|
| RGB LEDs | 12 (3 per room) | Room lighting control |
| Servo Motors (SG90) | 2 | Door lock and garage door control |
| Piezo Buzzer | 1 | Audio alerts |
| L298N Motor Driver | 1 | Fan control |
| DC Motors | 2 | Exhaust fans |

### Resistors and Supporting Components
| Component | Quantity | Purpose |
|-----------|----------|---------|
| 220Ω Resistors | 12 | LED current limiting |
| 10kΩ Resistors | 4 | PIR sensor pull-up |
| 1kΩ Resistors | 2 | General purpose |
| Capacitors (100µF) | 2 | Power filtering |

## Detailed Component Information

### Motion Detection System
- **PIR Sensors**: HC-SR501 or similar
- **Coverage**: 4 rooms (Room1, Room2, Room3, LivingRoom)
- **Detection Range**: Up to 7 meters
- **Detection Angle**: 120 degrees

### Environmental Monitoring
- **DHT11 Sensor**: 
  - Temperature range: 0-50°C (±2°C accuracy)
  - Humidity range: 20-90% RH (±5% accuracy)
  - Update rate: 1Hz (once per second)

### Gas Detection System
- **MQ-7 Sensor**: Carbon monoxide detection
- **ADS1115**: 16-bit ADC for precise analog readings
- **Detection Range**: 20-2000ppm CO
- **Response Time**: <30 seconds

### Lighting System
- **RGB LEDs**: Common cathode configuration
- **Colors**: White (all on), Red (emergency), Off
- **Control**: PWM for brightness control
- **Rooms**: 4 independent zones

### Security System
- **Door Lock**: Servo-controlled deadbolt mechanism
- **Garage Door**: Servo-controlled opener
- **IR Sensor**: Garage access control

### Fan Control System
- **L298N Motor Driver**: Dual H-bridge for motor control
- **DC Motors**: 12V exhaust fans
- **Control**: Temperature-based automatic operation
- **Manual Override**: Web interface control

## Pin Configuration

### Raspberry Pi 4 GPIO Pinout

```
     3V3  (1) (2)  5V
   GPIO2  (3) (4)  5V
   GPIO3  (5) (6)  GND
   GPIO4  (7) (8)  GPIO14
     GND  (9) (10) GPIO15
  GPIO17 (11) (12) GPIO18
  GPIO27 (13) (14) GND
  GPIO22 (15) (16) GPIO23
     3V3 (17) (18) GPIO24
  GPIO10 (19) (20) GND
   GPIO9 (21) (22) GPIO25
  GPIO11 (23) (24) GPIO8
     GND (25) (26) GPIO7
   GPIO0 (27) (28) GPIO1
   GPIO5 (29) (30) GND
   GPIO6 (31) (32) GPIO12
  GPIO13 (33) (34) GND
  GPIO19 (35) (36) GPIO16
  GPIO26 (37) (38) GPIO20
     GND (39) (40) GPIO21
```

### Pin Assignments

#### 🔌 **GPIO Pin Summary Table**

| GPIO | Physical | Component Category | Specific Function | Notes |
|------|----------|-------------------|-------------------|-------|
| **2** | **Pin 3** | **LivingRoom LED / I2C** | **Red LED / SDA** | **Shared Pin** |
| **3** | **Pin 5** | **LivingRoom LED / I2C** | **Green LED / SCL** | **Shared Pin** |
| 4 | Pin 7 | Environmental | DHT11 Temperature/Humidity | Data Pin |
| 5 | Pin 29 | Room1 LED | Red Channel | PWM Output |
| 6 | Pin 31 | Room1 LED | Green Channel | PWM Output |
| 7 | Pin 26 | Motor Control | L298N Motor B IN4 | Fan Control |
| 8 | Pin 24 | Motor Control | L298N Motor B IN3 | Fan Control |
| 9 | Pin 21 | Audio Alert | Piezo Buzzer | PWM Signal |
| 10 | Pin 19 | Security | Door Lock Servo | PWM Control |
| 11 | Pin 23 | Security | Garage Door Servo | PWM Control |
| 12 | Pin 32 | Room3 LED | Blue Channel | PWM Output |
| 13 | Pin 33 | Room1 LED | Blue Channel | PWM Output |
| 14 | Pin 8 | LivingRoom LED | Blue Channel | PWM Output |
| 15 | Pin 10 | Security | IR Sensor (Garage) | Digital Input |
| 16 | Pin 36 | Room2 LED | Blue Channel | PWM Output |
| 17 | Pin 11 | Motion Detection | PIR Sensor Room1 | Digital Input |
| 18 | Pin 12 | Motor Control | L298N Motor A IN1 | Fan Control |
| 19 | Pin 35 | Room2 LED | Red Channel | PWM Output |
| 20 | Pin 38 | Room3 LED | Red Channel | PWM Output |
| 21 | Pin 40 | Room3 LED | Green Channel | PWM Output |
| 22 | Pin 15 | Motion Detection | PIR Sensor Room3 | Digital Input |
| 23 | Pin 16 | Motion Detection | PIR Sensor LivingRoom | Digital Input |
| 24 | Pin 18 | Safety | MQ-7 Gas Sensor | Digital Input |
| 25 | Pin 22 | Motor Control | L298N Motor A IN2 | Fan Control |
| 26 | Pin 37 | Room2 LED | Green Channel | PWM Output |
| 27 | Pin 13 | Motion Detection | PIR Sensor Room2 | Digital Input |

---

#### 📍 **Pin Assignments by Component Category**

##### 🚨 **Motion Detection System (PIR Sensors)**
```
Room1:      GPIO 17 (Physical Pin 11) → PIR Sensor
Room2:      GPIO 27 (Physical Pin 13) → PIR Sensor  
Room3:      GPIO 22 (Physical Pin 15) → PIR Sensor
LivingRoom: GPIO 23 (Physical Pin 16) → PIR Sensor

Power: 5V (Pin 2 or 4)
Ground: GND (Pin 6, 9, 14, 20, 25, 30, 34, 39)
```

##### 💡 **RGB LED Lighting System**
```
Room1 LEDs:
├── Red:   GPIO 5  (Physical Pin 29)
├── Green: GPIO 6  (Physical Pin 31)  
└── Blue:  GPIO 13 (Physical Pin 33)

Room2 LEDs:
├── Red:   GPIO 19 (Physical Pin 35)
├── Green: GPIO 26 (Physical Pin 37)
└── Blue:  GPIO 16 (Physical Pin 36)

Room3 LEDs:
├── Red:   GPIO 20 (Physical Pin 38)
├── Green: GPIO 21 (Physical Pin 40)
└── Blue:  GPIO 12 (Physical Pin 32)

LivingRoom LEDs: ⚠️ SHARED WITH I2C
├── Red:   GPIO 2  (Physical Pin 3)  ← I2C SDA
├── Green: GPIO 3  (Physical Pin 5)  ← I2C SCL
└── Blue:  GPIO 14 (Physical Pin 8)

All LEDs: Use 220Ω current-limiting resistors
Common: Connect to GND
```

##### 🌡️ **Environmental Monitoring**
```
DHT11 Temperature/Humidity:
└── Data: GPIO 4 (Physical Pin 7)
    Power: 3.3V (Pin 1 or 17)
    Ground: GND (Pin 6)

MQ-7 Gas Sensor:
├── Digital Out: GPIO 24 (Physical Pin 18)
└── Analog Out:  ADS1115 Channel A0
    Power: 5V (Pin 2)
    Ground: GND (Pin 6)
```

##### 🔄 **Motor Control System (L298N Driver)**
```
Motor A (Fan 1):
├── IN1: GPIO 18 (Physical Pin 12)
└── IN2: GPIO 25 (Physical Pin 22)

Motor B (Fan 2):  
├── IN3: GPIO 8  (Physical Pin 24)
└── IN4: GPIO 7  (Physical Pin 26)

Power: 12V External Supply
Logic Power: 5V from Pi
Ground: Shared GND
```

##### 🔐 **Security & Access Control**
```
Door Lock Servo:
└── PWM: GPIO 10 (Physical Pin 19)
    Power: 5V (Pin 2)
    Ground: GND (Pin 6)

Garage Door Servo:
└── PWM: GPIO 11 (Physical Pin 23)  
    Power: 5V (Pin 4)
    Ground: GND (Pin 9)

IR Sensor (Garage Access):
└── Digital Out: GPIO 15 (Physical Pin 10)
    Power: 5V (Pin 2)
    Ground: GND (Pin 14)
```

##### 🔊 **Audio Alert System**
```
Piezo Buzzer:
└── Signal: GPIO 9 (Physical Pin 21)
    Ground: GND (Pin 25)
```

##### 📡 **I2C Communication (ADS1115 ADC)**
```
ADS1115 ADC Module:
├── SDA: GPIO 2 (Physical Pin 3)  ← SHARED with LivingRoom Red LED
├── SCL: GPIO 3 (Physical Pin 5)  ← SHARED with LivingRoom Green LED
├── VDD: 3.3V (Pin 1)
└── GND: GND (Pin 6)

Connected Sensors:
└── A0: MQ-7 Gas Sensor Analog Output
```

---

#### ⚠️ **Critical Pin Sharing Information**

##### **GPIO 2 & 3 Dual Usage**
```
⚠️  IMPORTANT: GPIO 2 and 3 serve dual purposes:

GPIO 2 (Physical Pin 3):
├── Primary:   I2C SDA (ADS1115 communication)
└── Secondary: LivingRoom Red LED

GPIO 3 (Physical Pin 5):  
├── Primary:   I2C SCL (ADS1115 communication)
└── Secondary: LivingRoom Green LED

✅ This configuration is SAFE because:
• I2C pins have built-in pull-up resistors
• LED circuits use current-limiting resistors  
• Both functions can coexist without interference
```

##### **Reserved Pins Status**
```
✅ SAFE - Not Used:
├── GPIO 0: I2C ID EEPROM (avoided)
└── GPIO 1: I2C ID EEPROM (avoided)

✅ SAFE - Properly Used:
├── GPIO 14: UART TXD (OK - UART disabled)
└── GPIO 15: UART RXD (OK - UART disabled)
```

---

#### 🔧 **Physical Pin Reference**

##### **Raspberry Pi 4 GPIO Header (40-pin)**
```
    3V3  (1) (2)  5V     ← Power Rails
  GPIO2  (3) (4)  5V     ← LivingRoom Red LED / I2C SDA
  GPIO3  (5) (6)  GND    ← LivingRoom Green LED / I2C SCL  
  GPIO4  (7) (8)  GPIO14 ← DHT11 Data | LivingRoom Blue LED
    GND  (9) (10) GPIO15 ← IR Sensor
 GPIO17 (11) (12) GPIO18 ← PIR Room1 | Motor A IN1
 GPIO27 (13) (14) GND    ← PIR Room2
 GPIO22 (15) (16) GPIO23 ← PIR Room3 | PIR LivingRoom
    3V3 (17) (18) GPIO24 ← Gas Sensor Digital
 GPIO10 (19) (20) GND    ← Door Servo
  GPIO9 (21) (22) GPIO25 ← Buzzer | Motor A IN2
 GPIO11 (23) (24) GPIO8  ← Garage Servo | Motor B IN3
    GND (25) (26) GPIO7  ← Motor B IN4
  GPIO0 (27) (28) GPIO1  ← Reserved (Not Used)
  GPIO5 (29) (30) GND    ← Room1 Red LED
  GPIO6 (31) (32) GPIO12 ← Room1 Green LED | Room3 Blue LED
 GPIO13 (33) (34) GND    ← Room1 Blue LED
 GPIO19 (35) (36) GPIO16 ← Room2 Red LED | Room2 Blue LED
 GPIO26 (37) (38) GPIO20 ← Room2 Green LED | Room3 Red LED
    GND (39) (40) GPIO21 ← Room3 Green LED
```

---

#### 📊 **Pin Usage Statistics**

```
Total GPIO Pins Used: 26 out of 28 available
├── Motion Detection: 4 pins (PIR sensors)
├── RGB Lighting: 12 pins (4 rooms × 3 colors)
├── Motor Control: 4 pins (L298N driver)
├── Environmental: 2 pins (DHT11 + Gas sensor)
├── Security: 3 pins (2 servos + IR sensor)
├── Audio: 1 pin (Buzzer)
└── I2C Communication: 2 pins (shared with LEDs)

Unused GPIO Pins: GPIO 0, GPIO 1 (intentionally reserved)
Power Pins Used: 5V, 3.3V, Multiple GND
```

## Wiring Diagrams

### 🔌 **Component-Specific Wiring Guides**

#### 🚨 **PIR Motion Sensors (4 Units)**
```
Each PIR Sensor Wiring:
┌─────────────┐    ┌──────────────────┐
│ PIR Sensor  │    │  Raspberry Pi 4  │
├─────────────┤    ├──────────────────┤
│ VCC (Red)   │────│ 5V (Pin 2 or 4)  │
│ GND (Black) │────│ GND (Pin 6,9,etc)│
│ OUT (White) │────│ GPIO Pin         │
└─────────────┘    └──────────────────┘

Specific GPIO Assignments:
• Room1:      GPIO 17 (Pin 11)
• Room2:      GPIO 27 (Pin 13)  
• Room3:      GPIO 22 (Pin 15)
• LivingRoom: GPIO 23 (Pin 16)
```

#### 💡 **RGB LED Arrays (4 Rooms)**
```
Standard Room LED Wiring (Room1, Room2, Room3):
┌─────────────┐    ┌──────────────────┐
│ RGB LED     │    │  Raspberry Pi 4  │
├─────────────┤    ├──────────────────┤
│ Red   (R)   │────│ GPIO Pin         │──── 220Ω Resistor
│ Green (G)   │────│ GPIO Pin         │──── 220Ω Resistor  
│ Blue  (B)   │────│ GPIO Pin         │──── 220Ω Resistor
│ Common (-)  │────│ GND              │
└─────────────┘    └──────────────────┘

⚠️ LivingRoom LED Special Wiring (Shared I2C):
┌─────────────┐    ┌──────────────────┐    ┌─────────────┐
│ RGB LED     │    │  Raspberry Pi 4  │    │ ADS1115 ADC │
├─────────────┤    ├──────────────────┤    ├─────────────┤
│ Red   (R)   │────│ GPIO 2 (Pin 3)   │────│ SDA         │
│ Green (G)   │────│ GPIO 3 (Pin 5)   │────│ SCL         │
│ Blue  (B)   │────│ GPIO 14 (Pin 8)  │    │             │
│ Common (-)  │────│ GND              │────│ GND         │
└─────────────┘    └──────────────────┘    └─────────────┘
                                           │ VDD ← 3.3V   │
                                           │ A0  ← Gas    │
                                           └─────────────┘
```

#### 🌡️ **Environmental Sensors**
```
DHT11 Temperature/Humidity Sensor:
┌─────────────┐    ┌──────────────────┐
│ DHT11       │    │  Raspberry Pi 4  │
├─────────────┤    ├──────────────────┤
│ VCC (Red)   │────│ 3.3V (Pin 1/17)  │
│ DATA (Yel)  │────│ GPIO 4 (Pin 7)   │
│ NC          │    │ (Not Connected)  │
│ GND (Black) │────│ GND (Pin 6)      │
└─────────────┘    └──────────────────┘

MQ-7 Gas Sensor with ADS1115:
┌─────────────┐    ┌─────────────┐    ┌──────────────────┐
│ MQ-7 Sensor │    │ ADS1115 ADC │    │  Raspberry Pi 4  │
├─────────────┤    ├─────────────┤    ├──────────────────┤
│ VCC         │────│ VDD (5V)    │────│ 5V (Pin 2)       │
│ GND         │────│ GND         │────│ GND (Pin 6)      │
│ AOUT        │────│ A0          │    │                  │
│ DOUT        │────┼─────────────┼────│ GPIO 24 (Pin 18) │
└─────────────┘    │ SDA         │────│ GPIO 2 (Pin 3)   │
                   │ SCL         │────│ GPIO 3 (Pin 5)   │
                   │ VDD         │────│ 3.3V (Pin 1)     │
                   └─────────────┘    └──────────────────┘
```

#### 🔄 **Motor Control System (L298N)**
```
L298N Motor Driver Connections:
┌─────────────┐    ┌──────────────────┐    ┌─────────────┐
│ 12V Supply  │    │     L298N        │    │ Raspberry Pi│
├─────────────┤    ├──────────────────┤    ├─────────────┤
│ +12V        │────│ VCC              │    │             │
│ GND         │────│ GND              │────│ GND (Pin 6) │
└─────────────┘    │ IN1              │────│ GPIO 18     │
                   │ IN2              │────│ GPIO 25     │
┌─────────────┐    │ IN3              │────│ GPIO 8      │
│ Motor A     │    │ IN4              │────│ GPIO 7      │
│ (Fan 1)     │    │ OUT1             │────│ Motor A +   │
├─────────────┤    │ OUT2             │────│ Motor A -   │
│ +           │────│ OUT3             │────│ Motor B +   │
│ -           │────│ OUT4             │────│ Motor B -   │
└─────────────┘    └──────────────────┘    └─────────────┘
┌─────────────┐
│ Motor B     │
│ (Fan 2)     │
├─────────────┤
│ +           │────┘
│ -           │────┘
└─────────────┘
```

#### 🔐 **Security & Access Control**
```
Servo Motors (Door Lock & Garage):
┌─────────────┐    ┌──────────────────┐
│ Door Servo  │    │  Raspberry Pi 4  │
├─────────────┤    ├──────────────────┤
│ Red (VCC)   │────│ 5V (Pin 2)       │
│ Brown (GND) │────│ GND (Pin 6)      │
│ Orange (PWM)│────│ GPIO 10 (Pin 19) │
└─────────────┘    └──────────────────┘

┌─────────────┐    ┌──────────────────┐
│ Garage Servo│    │  Raspberry Pi 4  │
├─────────────┤    ├──────────────────┤
│ Red (VCC)   │────│ 5V (Pin 4)       │
│ Brown (GND) │────│ GND (Pin 9)      │
│ Orange (PWM)│────│ GPIO 11 (Pin 23) │
└─────────────┘    └──────────────────┘

IR Sensor (Garage Access):
┌─────────────┐    ┌──────────────────┐
│ IR Sensor   │    │  Raspberry Pi 4  │
├─────────────┤    ├──────────────────┤
│ VCC (Red)   │────│ 5V (Pin 2)       │
│ GND (Black) │────│ GND (Pin 14)     │
│ OUT (White) │────│ GPIO 15 (Pin 10) │
└─────────────┘    └──────────────────┘
```

#### 🔊 **Audio Alert System**
```
Piezo Buzzer:
┌─────────────┐    ┌──────────────────┐
│ Buzzer      │    │  Raspberry Pi 4  │
├─────────────┤    ├──────────────────┤
│ + (Red)     │────│ GPIO 9 (Pin 21)  │
│ - (Black)   │────│ GND (Pin 25)     │
└─────────────┘    └──────────────────┘
```

---

### 🔌 **Power Distribution Diagram**

```
External Power Sources:
┌─────────────────┐
│ 12V Power Supply│ (For L298N Motor Driver)
│ (3A minimum)    │
└─────────┬───────┘
          │
┌─────────────────┐    ┌──────────────────────────────────┐
│ 5V Power Supply │    │        Raspberry Pi 4            │
│ (3A minimum)    │    │                                  │
└─────────┬───────┘    │  ┌─────────────────────────────┐ │
          │            │  │     Internal Power Rails    │ │
          └────────────┼──┤ 5V  ────────────────────────┼─┼─── PIR Sensors (4x)
                       │  │     ├─── Door Servo         │ │
                       │  │     ├─── Garage Servo       │ │
                       │  │     ├─── IR Sensor          │ │
                       │  │     └─── MQ-7 Gas Sensor    │ │
                       │  │                             │ │
                       │  │ 3.3V ───────────────────────┼─┼─── DHT11 Sensor
                       │  │     ├─── ADS1115 ADC        │ │
                       │  │     └─── RGB LEDs (via 220Ω)│ │
                       │  │                             │ │
                       │  │ GND ────────────────────────┼─┼─── All Components
                       │  └─────────────────────────────┘ │
                       └──────────────────────────────────┘

Power Consumption Estimate:
├── Raspberry Pi 4: ~2.5A @ 5V
├── PIR Sensors: ~0.2A @ 5V (4 units)
├── Servo Motors: ~1.0A @ 5V (2 units, peak)
├── RGB LEDs: ~0.3A @ 3.3V (12 LEDs)
├── Other Sensors: ~0.1A @ 3.3V/5V
└── Total: ~4.1A @ 5V (use 5A supply minimum)
```

---

### 📋 **Wiring Checklist**

#### ✅ **Pre-Wiring Verification**
- [ ] Power off Raspberry Pi completely
- [ ] Gather all components and verify part numbers
- [ ] Check all jumper wires for continuity
- [ ] Verify resistor values (220Ω for LEDs)
- [ ] Ensure proper ESD protection

#### ✅ **Component Installation Order**
1. [ ] Install power rails on breadboard
2. [ ] Connect ground connections first
3. [ ] Install I2C components (ADS1115)
4. [ ] Connect sensors (PIR, DHT11, MQ-7)
5. [ ] Install RGB LEDs with resistors
6. [ ] Connect motor driver (L298N)
7. [ ] Install servo motors
8. [ ] Connect buzzer last

#### ✅ **Post-Wiring Verification**
- [ ] Visual inspection of all connections
- [ ] Continuity test with multimeter
- [ ] Verify no short circuits (power to ground)
- [ ] Check voltage levels at key points
- [ ] Verify I2C device detection: `sudo i2cdetect -y 1`
- [ ] Test individual components before full system

#### ⚠️ **Safety Warnings**
- **Never connect/disconnect while powered**
- **Double-check polarity on all components**
- **Use current-limiting resistors for LEDs**
- **Ensure proper grounding for all components**
- **Keep 12V motor supply isolated from Pi**

## Software Dependencies

### Required Python Libraries
```bash
pip install RPi.GPIO
pip install Adafruit-DHT
pip install adafruit-circuitpython-ads1x15
pip install pandas
pip install numpy
pip install flask
pip install flask-socketio
```

### System Requirements
- Raspberry Pi OS (Bullseye or newer)
- Python 3.7+
- I2C enabled
- Camera interface enabled
- SSH enabled (optional, for remote access)

## Setup Instructions

### 1. Raspberry Pi Configuration
```bash
# Enable I2C
sudo raspi-config
# Navigate to Interface Options > I2C > Enable

# Enable Camera
sudo raspi-config
# Navigate to Interface Options > Camera > Enable

# Reboot
sudo reboot
```

### 2. Hardware Assembly
1. **Power off** the Raspberry Pi before making any connections
2. Connect all components according to the wiring diagrams
3. Double-check all connections before powering on
4. Use a multimeter to verify continuity if needed

### 3. Software Installation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install python3-pip python3-dev cmake

# Install Python libraries
pip3 install -r requirements.txt

# Test I2C devices
sudo i2cdetect -y 1
```

### 4. Testing Components
1. **PIR Sensors**: Use `test_motion_detection.py`
2. **Temperature Sensor**: Use `test_temperature_fan.py`
3. **Gas Sensor**: Use `test_gas_detection.py`
4. **RGB LEDs**: Test each room individually
5. **Servo Motors**: Use `test_garage_ir.py`
6. **Buzzer**: Use `test_buzzer.py`

### 5. System Verification
Run the complete system test:
```bash
python3 verify_system.py
```

## Troubleshooting

### Common Issues

1. **I2C devices not detected**:
   - Check wiring connections
   - Verify I2C is enabled: `sudo raspi-config`
   - Check device addresses: `sudo i2cdetect -y 1`

2. **PIR sensors not triggering**:
   - Check power connections (5V, GND)
   - Verify GPIO pin assignments
   - Allow 30-60 seconds for sensor warm-up

3. **DHT11 reading errors**:
   - Check data pin connection (GPIO 4)
   - Ensure stable power supply
   - Add delay between readings (minimum 2 seconds)

4. **RGB LEDs not working**:
   - Verify resistor values (220Ω)
   - Check common cathode connections to GND
   - Test individual colors

5. **Servo motors not responding**:
   - Check PWM signal connections
   - Verify 5V power supply capacity
   - Test with simple PWM signals

6. **Gas sensor false readings**:
   - Allow 24-48 hours for sensor burn-in
   - Check analog connections to ADS1115
   - Calibrate in clean air environment

### Debug Commands
```bash
# Check GPIO status
gpio readall

# Monitor I2C traffic
sudo i2cdetect -y 1

# Test individual components
python3 test_requirements.py

# Check system logs
sudo journalctl -f

# Monitor CPU temperature
vcgencmd measure_temp
```

## Maintenance

### Regular Checks
- **Weekly**: Visual inspection of connections
- **Monthly**: Clean dust from sensors and components
- **Quarterly**: Check servo motor operation
- **Annually**: Replace gas sensor if needed

### Backup Procedures
- **System Image**: Create full SD card backup
- **Configuration**: Backup automation rules and settings
- **Face Database**: Backup known faces Excel file

### Performance Monitoring
- Monitor CPU temperature and usage
- Check memory usage
- Verify network connectivity
- Test all sensors and actuators

## Safety Considerations

### Electrical Safety
- Always power off before making connections
- Use appropriate fuse protection
- Ensure proper grounding
- Check voltage levels before connecting

### Gas Sensor Safety
- Install in well-ventilated area
- Regular calibration required
- Replace sensor every 2-3 years
- Test emergency procedures

### Fire Safety
- Use flame-retardant enclosure
- Install smoke detectors
- Keep fire extinguisher nearby
- Regular electrical inspections

## Expansion Options

### Additional Sensors
- Temperature sensors for each room
- Door/window magnetic sensors
- Smoke detectors
- Water leak sensors

### Additional Actuators
- Window blinds control
- HVAC system integration
- Smart locks
- Irrigation system

### Communication
- WiFi range extenders
- Zigbee/Z-Wave integration
- Mobile app development
- Cloud connectivity

## Software Features

- **Motion Detection**: PIR sensors in each room trigger lighting
- **Temperature Control**: Automatic fan activation based on temperature
- **Gas Detection**: MQ-7 sensor with emergency alerts
- **Door Lock Control**: Servo-controlled door lock system
- **Garage Door Control**: Servo-controlled garage door with IR sensor
- **Audio Alerts**: Buzzer with different patterns for various events
- **Web Interface**: Real-time monitoring and control via web browser
- **Automation Rules**: Customizable automation based on sensor inputs

This documentation provides a complete reference for building and maintaining the Smart Home Automation System. Always prioritize safety and double-check connections before powering on the system. 