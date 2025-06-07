#!/usr/bin/env python3
"""
Smart Home Automation System
Integrates motion detection, temperature monitoring, and gas leak detection
with automated door lock
"""

import RPi.GPIO as GPIO
import Adafruit_DHT
import time
import threading
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import json
import os
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import logging
import pandas as pd
import numpy as np

# Disable Flask debug logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define pins and thresholds
PIR_PINS = {
    'Room1': 17,
    'Room2': 27,
    'Room3': 22,
    'LivingRoom': 23
}

RGB_PINS = {
    'Room1': {'R': 5, 'G': 6, 'B': 13},
    'Room2': {'R': 19, 'G': 26, 'B': 16},
    'Room3': {'R': 20, 'G': 21, 'B': 12},
    'LivingRoom': {'R': 2, 'G': 3, 'B': 14}
}

DHT_PIN = 4  # DHT11 data pin

# L298N Motor Driver pin connections for fan control
MOTOR_IN1 = 18  # Motor A direction control 1 (GPIO 18, Pin 12)
MOTOR_IN2 = 25  # Motor A direction control 2 (GPIO 25, Pin 22)
MOTOR_IN3 = 8   # Motor B direction control 1 (GPIO 8, Pin 24)
MOTOR_IN4 = 7   # Motor B direction control 2 (GPIO 7, Pin 26)

GAS_DIGITAL_PIN = 24  # Digital output from MQ-7
TEMPERATURE_THRESHOLD = 25.0  # Temperature threshold in Celsius

# Component pins
SERVO_PIN = 10  # Door lock servo control pin
BUZZER_PIN = 9  # Buzzer for audio alerts

# New component pins
GARAGE_SERVO_PIN = 11  # Garage door servo control pin
IR_SENSOR_PIN = 15     # IR sensor for garage fingerprint detection
GARAGE_AUTO_CLOSE_DELAY = 120  # Auto-close delay in seconds (2 minutes)

# Global state variables
system_state = {
    'motion': {room: False for room in PIR_PINS.keys()},
    'temperature': 0.0,
    'humidity': 0.0,
    'gas_detected': False,
    'fans_on': False,
    'emergency_mode': False,
    'door_locked': True,  # New state for door lock
    'garage_door_open': False,  # New state for garage door
    'garage_auto_close_time': None,  # Time when garage should auto-close
    'manual_override': {
        'fans': False,
        'lights': {room: False for room in RGB_PINS.keys()},
        'door': False,  # New manual override for door
        'garage': False  # New manual override for garage
    },
    'automation_rules': []  # Store automation rules
}

# Default automation rules
default_rules = [
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
    },
    {
        'id': 'rule2',
        'name': 'Motion Light Control',
        'condition': {
            'type': 'motion',
            'location': 'any',
            'operator': '==',
            'value': True
        },
        'action': {
            'type': 'light',
            'location': 'same',
            'command': 'on'
        },
        'active': True
    },
    {
        'id': 'rule3',
        'name': 'Gas Emergency',
        'condition': {
            'type': 'gas',
            'operator': '==',
            'value': True
        },
        'action': {
            'type': 'alert',
            'command': 'emergency'
        },
        'active': True
    },
    {
        'id': 'rule4',
        'name': 'Garage Door Auto-Close',
        'condition': {
            'type': 'time',
            'operator': '==',
            'value': '22:00'  # Close garage door at 10 PM if left open
        },
        'action': {
            'type': 'garage',
            'command': 'close'
        },
        'active': True
    }
]

# Initialize the automation rules
system_state['automation_rules'] = default_rules.copy()

# Setup PIR sensors as inputs
for room, pin in PIR_PINS.items():
    GPIO.setup(pin, GPIO.IN)
    print(f"Set up PIR sensor for {room} on GPIO {pin}")

# Setup RGB LEDs as outputs
for room, pins in RGB_PINS.items():
    for color, pin in pins.items():
        GPIO.setup(pin, GPIO.OUT)
        print(f"Set up {color} LED for {room} on GPIO {pin}")

# Setup L298N motor driver pins as output
for pin in [MOTOR_IN1, MOTOR_IN2, MOTOR_IN3, MOTOR_IN4]:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)  # Ensure all motors are stopped initially
    print(f"Set up L298N motor control on GPIO {pin}")

# Setup digital gas sensor pin as input
GPIO.setup(GAS_DIGITAL_PIN, GPIO.IN)
print(f"Set up MQ-7 digital output on GPIO {GAS_DIGITAL_PIN}")

# Setup servo for door lock
GPIO.setup(SERVO_PIN, GPIO.OUT)
door_servo = GPIO.PWM(SERVO_PIN, 50)  # 50Hz (standard for servos)
door_servo.start(0)  # Initialize at 0% duty cycle
print(f"Set up door lock servo on GPIO {SERVO_PIN}")

# Setup servo for garage door
GPIO.setup(GARAGE_SERVO_PIN, GPIO.OUT)
garage_servo = GPIO.PWM(GARAGE_SERVO_PIN, 50)  # 50Hz (standard for servos)
garage_servo.start(0)  # Initialize at 0% duty cycle
print(f"Set up garage door servo on GPIO {GARAGE_SERVO_PIN}")

# Setup IR sensor for garage fingerprint detection
GPIO.setup(IR_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Use pull-up resistor
print(f"Set up IR fingerprint sensor on GPIO {IR_SENSOR_PIN}")

# Setup buzzer for alerts
GPIO.setup(BUZZER_PIN, GPIO.OUT)
buzzer = GPIO.PWM(BUZZER_PIN, 440)  # 440Hz (A4 note) as default frequency
buzzer.start(0)  # Initialize with 0% duty cycle (no sound)
print(f"Set up alert buzzer on GPIO {BUZZER_PIN}")

# Setup I2C for ADS1115
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
gas_channel = AnalogIn(ads, ADS.P0)  # Connect MQ-7 analog output to A0

# Create Flask app
app = Flask(__name__)
socketio = SocketIO(app)

# Create template directory if it doesn't exist
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

# LED control functions
def set_led_color(room, r_state, g_state, b_state):
    """Set the RGB LED color for a specific room"""
    GPIO.output(RGB_PINS[room]['R'], r_state)
    GPIO.output(RGB_PINS[room]['G'], g_state)
    GPIO.output(RGB_PINS[room]['B'], b_state)

def led_white(room):
    """Turn on white color (R+G+B ON)"""
    set_led_color(room, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH)

def led_red(room):
    """Turn on red color (R ON, G+B OFF)"""
    set_led_color(room, GPIO.HIGH, GPIO.LOW, GPIO.LOW)

def led_off(room):
    """Turn off the LED"""
    set_led_color(room, GPIO.LOW, GPIO.LOW, GPIO.LOW)

def all_leds_red():
    """Turn all LEDs red for emergency alert"""
    for room in RGB_PINS.keys():
        led_red(room)

def all_leds_off():
    """Turn off all LEDs"""
    for room in RGB_PINS.keys():
        led_off(room)

# Buzzer control functions
def buzzer_on(frequency=440, duty_cycle=50):
    """Turn on buzzer with specified frequency and duty cycle"""
    buzzer.ChangeFrequency(frequency)
    buzzer.ChangeDutyCycle(duty_cycle)

def buzzer_off():
    """Turn off buzzer"""
    buzzer.ChangeDutyCycle(0)

def buzzer_beep(frequency=440, duty_cycle=50, duration=0.2, pause=0.2, count=1):
    """
    Generate beep pattern with specified parameters
    frequency: tone frequency in Hz
    duty_cycle: volume (0-100)
    duration: length of each beep in seconds
    pause: silence between beeps in seconds
    count: number of beeps
    """
    for _ in range(count):
        buzzer_on(frequency, duty_cycle)
        time.sleep(duration)
        buzzer_off()
        if _ < count - 1:  # No pause after the last beep
            time.sleep(pause)

def play_alert_pattern(pattern_type):
    """
    Play predefined alert patterns
    pattern_type: 'gas', 'door_open', 'door_close', 'unauthorized', 'welcome'
    """
    # Start in a new thread to avoid blocking
    alert_thread = threading.Thread(
        target=_play_alert_pattern_thread,
        args=(pattern_type,)
    )
    alert_thread.daemon = True
    alert_thread.start()

def _play_alert_pattern_thread(pattern_type):
    """Thread function to play alert patterns"""
    if pattern_type == 'gas':
        # Urgent, continuous alternating high-low pattern
        for _ in range(5):  # Play pattern for 5 cycles
            buzzer_beep(880, 70, 0.2, 0.1, 3)  # High pitch, multiple beeps
            time.sleep(0.3)
    
    elif pattern_type == 'door_open':
        # Ascending tones
        frequencies = [523, 659, 784]  # C5, E5, G5 (C major chord)
        for freq in frequencies:
            buzzer_beep(freq, 50, 0.15, 0, 1)
            time.sleep(0.05)
    
    elif pattern_type == 'door_close':
        # Descending tones
        frequencies = [784, 659, 523]  # G5, E5, C5 (C major chord reversed)
        for freq in frequencies:
            buzzer_beep(freq, 50, 0.15, 0, 1)
            time.sleep(0.05)
    
    elif pattern_type == 'unauthorized':
        # Two low beeps
        buzzer_beep(330, 70, 0.3, 0.1, 2)  # Low pitch, two beeps
    
    elif pattern_type == 'welcome':
        # Pleasant melody
        melody = [(523, 0.1), (659, 0.1), (784, 0.2)]  # C5, E5, G5
        for freq, dur in melody:
            buzzer_beep(freq, 50, dur, 0, 1)
            time.sleep(0.05)

# Door lock control functions
def set_door_lock(lock_state):
    """
    Control the door lock
    lock_state: True for locked, False for unlocked
    """
    try:
        if lock_state:
            # Locked position (0 degrees)
            duty_cycle = 2.5  # 2.5% duty cycle corresponds to 0 degrees
        else:
            # Unlocked position (90 degrees)
            duty_cycle = 7.5  # 7.5% duty cycle corresponds to 90 degrees
        
        door_servo.ChangeDutyCycle(duty_cycle)
        time.sleep(0.5)  # Allow servo to reach position
        door_servo.ChangeDutyCycle(0)  # Stop sending pulses (reduces jitter)
        
        # Update system state
        previous_state = system_state['door_locked']
        system_state['door_locked'] = lock_state
        
        # Play appropriate sound alert
        if previous_state != lock_state:  # Only play if state changed
            if lock_state:
                play_alert_pattern('door_close')
            else:
                play_alert_pattern('door_open')
        
        status = "locked" if lock_state else "unlocked"
        print(f"Door {status}")
        return status
    except Exception as e:
        print(f"Error controlling door lock: {e}")
        return "error"

# Garage door control functions
def set_garage_door(open_state):
    """
    Control the garage door
    open_state: True for open, False for closed
    """
    try:
        if open_state:
            # Open position (120 degrees)
            duty_cycle = 9.0  # 9.0% duty cycle corresponds to 120 degrees
        else:
            # Closed position (0 degrees)
            duty_cycle = 2.5  # 2.5% duty cycle corresponds to 0 degrees
        
        garage_servo.ChangeDutyCycle(duty_cycle)
        time.sleep(1.0)  # Allow servo to reach position (garage needs more time)
        garage_servo.ChangeDutyCycle(0)  # Stop sending pulses (reduces jitter)
        
        # Update system state
        previous_state = system_state['garage_door_open']
        system_state['garage_door_open'] = open_state
        
        # Set auto-close timer if opening the garage
        if open_state and not previous_state:
            system_state['garage_auto_close_time'] = time.time() + GARAGE_AUTO_CLOSE_DELAY
            print(f"Garage door will auto-close in {GARAGE_AUTO_CLOSE_DELAY} seconds")
            
            # Play door open sound
            play_alert_pattern('door_open')
        
        # Play door close sound if closing
        elif not open_state and previous_state:
            system_state['garage_auto_close_time'] = None
            play_alert_pattern('door_close')
        
        status = "open" if open_state else "closed"
        print(f"Garage door {status}")
        return status
    except Exception as e:
        print(f"Error controlling garage door: {e}")
        return "error"

def fingerprint_detected():
    """
    Check if a fingerprint is detected by the IR sensor
    Returns True if detected, False otherwise
    """
    # IR sensor returns LOW (0) when object is detected
    return GPIO.input(IR_SENSOR_PIN) == 0

def handle_garage_auto_close():
    """
    Handle automatic closing of the garage door after timeout
    """
    # Skip if garage is closed or manual override is active
    if not system_state['garage_door_open'] or system_state['manual_override']['garage']:
        return
    
    # Check if auto-close time is set and has been reached
    if (system_state['garage_auto_close_time'] is not None and 
            time.time() >= system_state['garage_auto_close_time']):
        print("Auto-closing garage door after timeout")
        set_garage_door(False)  # Close the garage
        system_state['garage_auto_close_time'] = None

def handle_ir_fingerprint():
    """
    Handle IR fingerprint detection for garage door
    """
    if fingerprint_detected():
        # Only take action if garage is currently closed
        if not system_state['garage_door_open']:
            print("Fingerprint detected - opening garage door")
            # Welcome sound alert
            play_alert_pattern('welcome')
            # Open the garage door
            set_garage_door(True)

# Sensor reading functions
def read_dht11():
    """Read temperature and humidity from DHT11 sensor"""
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT_PIN)
    return humidity, temperature

def check_gas_sensor():
    """Read both digital and analog values from gas sensor"""
    digital_value = GPIO.input(GAS_DIGITAL_PIN)
    analog_value = gas_channel.value
    analog_voltage = gas_channel.voltage
    
    return {
        'digital': digital_value,
        'analog_raw': analog_value,
        'analog_voltage': analog_voltage
    }

# Control functions
def control_fans(turn_on=None):
    """Control fans based on input parameter or temperature threshold using L298N motor driver"""
    if turn_on is None:  # Automatic mode based on temperature
        if system_state['temperature'] >= TEMPERATURE_THRESHOLD:
            turn_on = True
        else:
            turn_on = False
    
    # Control motors using L298N motor driver
    if turn_on:
        motor_a_forward()  # Turn on Fan 1 (Motor A)
        motor_b_forward()  # Turn on Fan 2 (Motor B)
    else:
        stop_all_motors()  # Turn off both fans
    
    system_state['fans_on'] = turn_on
    return turn_on

def handle_motion_detection():
    """Handle motion detection and LED control"""
    for room, pin in PIR_PINS.items():
        motion_detected = GPIO.input(pin)
        system_state['motion'][room] = motion_detected
        
        # If not in emergency mode and no manual override
        if not system_state['emergency_mode'] and not system_state['manual_override']['lights'][room]:
            if motion_detected:
                led_white(room)
            else:
                led_off(room)

def handle_gas_detection():
    """Handle gas detection and emergency alerts"""
    gas_data = check_gas_sensor()
    gas_detected = gas_data['digital'] == 0  # LOW means gas detected for most MQ sensors
    
    # Update system state
    previous_state = system_state['gas_detected']
    system_state['gas_detected'] = gas_detected
    
    # Handle emergency mode
    if gas_detected:
        if not previous_state:  # Only alert if this is a new detection
            play_alert_pattern('gas')  # Play gas alert sound
        
        system_state['emergency_mode'] = True
        all_leds_red()  # Set all LEDs to red for alert
    else:
        if system_state['emergency_mode']:
            system_state['emergency_mode'] = False
            # Return to normal operation
            handle_motion_detection()

def handle_temperature_control():
    """Handle temperature reading and fan control"""
    humidity, temperature = read_dht11()
    
    if humidity is not None and temperature is not None:
        system_state['humidity'] = humidity
        system_state['temperature'] = temperature
        
        # If no manual override
        if not system_state['manual_override']['fans']:
            control_fans()  # Automatic control based on temperature

# Motor control functions for L298N
def motor_a_forward():
    """Motor A forward rotation (Fan 1 ON)"""
    GPIO.output(MOTOR_IN1, GPIO.HIGH)
    GPIO.output(MOTOR_IN2, GPIO.LOW)

def motor_a_stop():
    """Motor A stop (Fan 1 OFF)"""
    GPIO.output(MOTOR_IN1, GPIO.LOW)
    GPIO.output(MOTOR_IN2, GPIO.LOW)

def motor_b_forward():
    """Motor B forward rotation (Fan 2 ON)"""
    GPIO.output(MOTOR_IN3, GPIO.HIGH)
    GPIO.output(MOTOR_IN4, GPIO.LOW)

def motor_b_stop():
    """Motor B stop (Fan 2 OFF)"""
    GPIO.output(MOTOR_IN3, GPIO.LOW)
    GPIO.output(MOTOR_IN4, GPIO.LOW)

def stop_all_motors():
    """Stop both motors"""
    motor_a_stop()
    motor_b_stop()

# Sensor monitoring thread function
def sensor_monitor():
    """Monitor sensors and update system state in a loop"""
    while True:
        # Handle motion detection and control LEDs
        handle_motion_detection()
        
        # Handle temperature monitoring and fan control
        handle_temperature_control()
        
        # Handle gas detection and emergency mode
        handle_gas_detection()
        
        # Handle IR fingerprint detection for garage
        handle_ir_fingerprint()
        
        # Handle garage door auto-close
        handle_garage_auto_close()
        
        # Process automation rules
        process_automation_rules()
        
        # Update clients with the latest state
        socketio.emit('state_update', system_state)
        
        # Sleep for a short duration before next read
        time.sleep(1)

# Automation rule functions
def add_rule(rule):
    """Add a new automation rule to the system"""
    # Generate unique ID if not provided
    if 'id' not in rule:
        rule['id'] = f"rule{len(system_state['automation_rules']) + 1}"
    
    # Set rule to active by default
    if 'active' not in rule:
        rule['active'] = True
    
    # Add the rule to the system
    system_state['automation_rules'].append(rule)
    save_rules_to_file()
    return rule['id']

def update_rule(rule_id, updated_rule):
    """Update an existing automation rule"""
    for i, rule in enumerate(system_state['automation_rules']):
        if rule['id'] == rule_id:
            # Keep the original ID
            updated_rule['id'] = rule_id
            system_state['automation_rules'][i] = updated_rule
            save_rules_to_file()
            return True
    return False

def delete_rule(rule_id):
    """Delete an automation rule"""
    for i, rule in enumerate(system_state['automation_rules']):
        if rule['id'] == rule_id:
            del system_state['automation_rules'][i]
            save_rules_to_file()
            return True
    return False

def toggle_rule(rule_id, active=None):
    """Enable or disable a rule"""
    for rule in system_state['automation_rules']:
        if rule['id'] == rule_id:
            if active is None:
                # Toggle current state
                rule['active'] = not rule['active']
            else:
                # Set to specified state
                rule['active'] = active
            save_rules_to_file()
            return True
    return False

def save_rules_to_file():
    """Save automation rules to a file"""
    try:
        with open('automation_rules.json', 'w') as f:
            json.dump(system_state['automation_rules'], f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving rules: {e}")
        return False

def load_rules_from_file():
    """Load automation rules from a file"""
    try:
        if os.path.exists('automation_rules.json'):
            with open('automation_rules.json', 'r') as f:
                rules = json.load(f)
            system_state['automation_rules'] = rules
            return True
        else:
            # Create file with default rules if it doesn't exist
            system_state['automation_rules'] = default_rules.copy()
            save_rules_to_file()
            return True
    except Exception as e:
        print(f"Error loading rules: {e}")
        # Fall back to default rules
        system_state['automation_rules'] = default_rules.copy()
        return False

def evaluate_condition(condition):
    """Evaluate a rule condition against the current system state"""
    condition_type = condition['type']
    operator = condition['operator']
    value = condition['value']
    
    # Get the current state value based on condition type
    if condition_type == 'temperature':
        current_value = system_state['temperature']
    elif condition_type == 'humidity':
        current_value = system_state['humidity']
    elif condition_type == 'gas':
        current_value = system_state['gas_detected']
    elif condition_type == 'motion':
        if condition.get('location', 'any') == 'any':
            # Check if motion is detected in any room
            current_value = any(system_state['motion'].values())
        else:
            # Check specific room
            room = condition['location']
            if room in system_state['motion']:
                current_value = system_state['motion'][room]
            else:
                return False
    elif condition_type == 'time':
        # Time-based condition
        import datetime
        current_time = datetime.datetime.now().time()
        time_value = datetime.datetime.strptime(value, "%H:%M").time()
        
        # For time comparisons
        if operator == '>':
            return current_time > time_value
        elif operator == '<':
            return current_time < time_value
        elif operator == '==':
            # Allow 1-minute tolerance for equality
            return abs((datetime.datetime.combine(datetime.date.today(), current_time) - 
                      datetime.datetime.combine(datetime.date.today(), time_value)).total_seconds()) < 60
        else:
            return False
    else:
        # Unknown condition type
        return False
    
    # Evaluate condition using appropriate operator
    if operator == '>':
        return current_value > value
    elif operator == '<':
        return current_value < value
    elif operator == '>=':
        return current_value >= value
    elif operator == '<=':
        return current_value <= value
    elif operator == '==':
        return current_value == value
    elif operator == '!=':
        return current_value != value
    else:
        # Unknown operator
        return False

def execute_action(action, condition=None):
    """Execute an action based on a rule"""
    action_type = action['type']
    command = action['command']
    
    if action_type == 'fan':
        if command == 'on':
            control_fans(True)
        elif command == 'off':
            control_fans(False)
        elif command == 'toggle':
            control_fans(not system_state['fans_on'])
    
    elif action_type == 'light':
        location = action.get('location', 'all')
        
        # Handle 'same' location (use the location from the condition)
        if location == 'same' and condition and 'location' in condition and condition['location'] != 'any':
            location = condition['location']
        
        if location == 'all':
            rooms = RGB_PINS.keys()
        elif location in RGB_PINS:
            rooms = [location]
        else:
            # Invalid location
            return False
        
        for room in rooms:
            if command == 'on':
                # Override manual control
                system_state['manual_override']['lights'][room] = True
                led_white(room)
            elif command == 'off':
                # Override manual control
                system_state['manual_override']['lights'][room] = True
                led_off(room)
            elif command == 'auto':
                # Return to automatic control
                system_state['manual_override']['lights'][room] = False
                handle_motion_detection()
    
    elif action_type == 'door':
        if command == 'lock':
            set_door_lock(True)
        elif command == 'unlock':
            set_door_lock(False)
        elif command == 'auto':
            system_state['manual_override']['door'] = False
            set_door_lock(True)  # Default to locked when in auto mode
    
    elif action_type == 'garage':
        if command == 'open':
            system_state['manual_override']['garage'] = True
            set_garage_door(True)
        elif command == 'close':
            system_state['manual_override']['garage'] = True
            set_garage_door(False)
        elif command == 'auto':
            system_state['manual_override']['garage'] = False
            # Default to closed when in auto mode
            if system_state['garage_door_open']:
                # Set auto-close timer
                system_state['garage_auto_close_time'] = time.time() + GARAGE_AUTO_CLOSE_DELAY
    
    elif action_type == 'alert':
        if command == 'emergency':
            system_state['emergency_mode'] = True
            all_leds_red()
            play_alert_pattern('gas')
        elif command == 'sound':
            alert_type = action.get('alert_type', 'welcome')
            play_alert_pattern(alert_type)
    
    return True

def process_automation_rules():
    """Process all active automation rules"""
    for rule in system_state['automation_rules']:
        if rule['active']:
            if evaluate_condition(rule['condition']):
                execute_action(rule['action'], rule['condition'])

# Flask routes
@app.route('/')
def index():
    """Serve the web interface"""
    return render_template('index.html')

@app.route('/automation')
def automation_page():
    """Serve the automation rules management page"""
    return render_template('automation.html')

@app.route('/api/state')
def get_state():
    """API endpoint to get current system state"""
    return jsonify(system_state)

@app.route('/api/control/fan', methods=['POST'])
def control_fan_api():
    """API endpoint to control fan manually"""
    data = request.get_json()
    if 'state' in data:
        # Set manual override
        system_state['manual_override']['fans'] = True
        control_fans(data['state'])
        return jsonify({'success': True, 'fans_on': system_state['fans_on']})
    return jsonify({'success': False, 'error': 'Invalid request'})

@app.route('/api/control/fan/auto', methods=['POST'])
def fan_auto_mode():
    """API endpoint to return fan to automatic control"""
    system_state['manual_override']['fans'] = False
    control_fans()  # Return to temperature-based control
    return jsonify({'success': True, 'fans_on': system_state['fans_on']})

@app.route('/api/control/light', methods=['POST'])
def control_light_api():
    """API endpoint to control room lights manually"""
    data = request.get_json()
    if 'room' in data and 'state' in data and data['room'] in RGB_PINS:
        room = data['room']
        # Set manual override for this room
        system_state['manual_override']['lights'][room] = True
        
        if data['state']:
            led_white(room)
        else:
            led_off(room)
            
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Invalid request'})

@app.route('/api/control/light/auto', methods=['POST'])
def light_auto_mode():
    """Disable manual override for a room's light"""
    data = request.json
    room = data.get('room')
    
    if room in system_state['manual_override']['lights']:
        system_state['manual_override']['lights'][room] = False
        print(f"Light auto mode enabled for {room}")
        
        # Return to motion-based control
        handle_motion_detection()
        
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Invalid room'})

@app.route('/api/control/door', methods=['POST'])
def control_door_api():
    """Control door lock"""
    data = request.json
    lock_state = data.get('state', True)  # Default to locked
    
    # Set manual override
    system_state['manual_override']['door'] = True
    
    # Control the door lock
    set_door_lock(lock_state)
    
    return jsonify({
        'success': True, 
        'door_locked': system_state['door_locked']
    })

@app.route('/api/control/door/auto', methods=['POST'])
def door_auto_mode():
    """Disable manual override for door lock"""
    # Disable manual override
    system_state['manual_override']['door'] = False
    
    # Default to locked state when returning to auto
    set_door_lock(True)
    
    return jsonify({
        'success': True,
        'door_locked': system_state['door_locked']
    })

# Garage door API endpoints
@app.route('/api/control/garage', methods=['POST'])
def control_garage_api():
    """Control garage door"""
    data = request.json
    open_state = data.get('state', False)  # Default to closed
    
    # Set manual override
    system_state['manual_override']['garage'] = True
    
    # Control the garage door
    set_garage_door(open_state)
    
    return jsonify({
        'success': True, 
        'garage_door_open': system_state['garage_door_open']
    })

@app.route('/api/control/garage/auto', methods=['POST'])
def garage_auto_mode():
    """Disable manual override for garage door"""
    # Disable manual override
    system_state['manual_override']['garage'] = False
    
    # If garage is open, set auto-close timer
    if system_state['garage_door_open']:
        system_state['garage_auto_close_time'] = time.time() + GARAGE_AUTO_CLOSE_DELAY
    
    return jsonify({
        'success': True,
        'garage_door_open': system_state['garage_door_open']
    })

# Automation rules API endpoints
@app.route('/api/rules', methods=['GET'])
def get_rules():
    """Get all automation rules"""
    return jsonify(system_state['automation_rules'])

@app.route('/api/rules/<rule_id>', methods=['GET'])
def get_rule(rule_id):
    """Get a specific automation rule"""
    for rule in system_state['automation_rules']:
        if rule['id'] == rule_id:
            return jsonify(rule)
    return jsonify({'error': 'Rule not found'}), 404

@app.route('/api/rules', methods=['POST'])
def create_rule():
    """Create a new automation rule"""
    data = request.json
    
    # Validate required fields
    if 'name' not in data or 'condition' not in data or 'action' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Add the rule
    rule_id = add_rule(data)
    
    return jsonify({'success': True, 'id': rule_id}), 201

@app.route('/api/rules/<rule_id>', methods=['PUT'])
def update_rule_api(rule_id):
    """Update an existing automation rule"""
    data = request.json
    
    # Validate required fields
    if 'name' not in data or 'condition' not in data or 'action' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Update the rule
    if update_rule(rule_id, data):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Rule not found'}), 404

@app.route('/api/rules/<rule_id>', methods=['DELETE'])
def delete_rule_api(rule_id):
    """Delete an automation rule"""
    if delete_rule(rule_id):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Rule not found'}), 404

@app.route('/api/rules/<rule_id>/toggle', methods=['POST'])
def toggle_rule_api(rule_id):
    """Toggle a rule's active state"""
    data = request.json
    active = data.get('active', None)
    
    if toggle_rule(rule_id, active):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Rule not found'}), 404

@app.route('/api/rules/reset', methods=['POST'])
def reset_rules():
    """Reset to default rules"""
    system_state['automation_rules'] = default_rules.copy()
    save_rules_to_file()
    return jsonify({'success': True})

# Create HTML template
def create_html_template():
    """Create an HTML template for the web interface"""
    with open('templates/index.html', 'w') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Home System</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="/static/style.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
</head>
<body>
    <div class="container mt-4">
        <h1 class="text-center mb-4">Smart Home Automation System</h1>
        
        <div class="text-center mb-3">
            <a href="/automation" class="btn btn-info">Manage Automation Rules</a>
        </div>
        
        <div class="row">
            <!-- Environment Information -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        Environment Information
                    </div>
                    <div class="card-body">
                        <p>
                            <strong>Temperature:</strong> 
                            <span id="temperature-value" class="sensor-value">--</span> °C
                        </p>
                        <p>
                            <strong>Humidity:</strong> 
                            <span id="humidity-value" class="sensor-value">--</span> %
                        </p>
                        
                        <p>
                            <strong>Fan Status:</strong> 
                            <span id="fan-indicator" class="status-indicator status-off"></span>
                            <span id="fan-status">Off</span>
                        </p>
                        
                        <div class="control-buttons">
                            <button id="fan-on" class="btn btn-success btn-sm">Turn On</button>
                            <button id="fan-off" class="btn btn-danger btn-sm">Turn Off</button>
                            <button id="fan-auto" class="btn btn-primary btn-sm">Auto</button>
                        </div>
                    </div>
                </div>
                
                <div class="card mt-3">
                    <div class="card-header">
                        Safety
                    </div>
                    <div class="card-body">
                        <p>
                            <strong>Gas Leak Alert:</strong> 
                            <span id="emergency-indicator" class="status-indicator status-off"></span>
                            <span id="emergency-status">Inactive</span>
                        </p>
                </div>
            </div>
            
                <!-- Door Lock Control -->
                <div class="card mt-3">
                    <div class="card-header">
                        Door Lock Control
                    </div>
                    <div class="card-body">
                        <p>
                            <strong>Door Status:</strong> 
                            <span id="door-indicator" class="status-indicator status-off"></span>
                            <span id="door-status">Locked</span>
                        </p>
                        
                        <div class="control-buttons">
                            <button id="door-lock" class="btn btn-danger btn-sm">Lock</button>
                            <button id="door-unlock" class="btn btn-success btn-sm">Unlock</button>
                            <button id="door-auto" class="btn btn-primary btn-sm">Auto</button>
                        </div>
                    </div>
                </div>
            </div>
                
                <!-- Garage Door Control -->
                <div class="card mt-3">
                    <div class="card-header">
                        Garage Door Control
        </div>
                    <div class="card-body">
                        <p>
                            <strong>Garage Status:</strong> 
                            <span id="garage-indicator" class="status-indicator status-off"></span>
                            <span id="garage-status">Closed</span>
                        </p>
                        <p>
                            <strong>Auto-Close:</strong> 
                            <span id="garage-timer">Not set</span>
                        </p>
                        <p>
                            <small class="text-muted">IR fingerprint sensor will automatically open the garage door when detected</small>
                        </p>
                        
                        <div class="control-buttons">
                            <button id="garage-open" class="btn btn-success btn-sm">Open</button>
                            <button id="garage-close" class="btn btn-danger btn-sm">Close</button>
                            <button id="garage-auto" class="btn btn-primary btn-sm">Auto</button>
                        </div>
                    </div>
        </div>
    </div>

            <!-- Room Status and Controls -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        Room Status and Controls
                    </div>
                    <div class="card-body" id="rooms-container">
                        <!-- Room statuses will be dynamically added here -->
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        
        // Function to create room status elements
        function initRooms() {
            const roomsContainer = document.getElementById('rooms-container');
            const rooms = ['Room1', 'Room2', 'Room3', 'LivingRoom'];
            
            rooms.forEach(room => {
                const roomDiv = document.createElement('div');
                roomDiv.className = 'mb-4';
                roomDiv.innerHTML = `
                    <h5>${room.replace(/([A-Z])/g, ' $1').trim()}</h5>
                    <p>
                        <strong>Motion:</strong> 
                        <span id="${room}-motion-indicator" class="status-indicator status-off"></span>
                        <span id="${room}-motion-status">None</span>
                    </p>
                    <p>
                        <strong>Light:</strong> 
                        <span id="${room}-light-indicator" class="status-indicator status-off"></span>
                                <span id="${room}-light-status">Off</span>
                            </p>
                    <div class="control-buttons">
                        <button class="btn btn-success btn-sm light-on" data-room="${room}">Turn On</button>
                        <button class="btn btn-danger btn-sm light-off" data-room="${room}">Turn Off</button>
                        <button class="btn btn-primary btn-sm light-auto" data-room="${room}">Auto</button>
                            </div>
                    <hr>
                `;
                roomsContainer.appendChild(roomDiv);
            });
        }
        
        // Function to update UI based on system state
        function updateUI(state) {
            // Update temperature and humidity
            document.getElementById('temperature-value').textContent = state.temperature.toFixed(1);
            document.getElementById('humidity-value').textContent = state.humidity.toFixed(1);
            
            // Update fan status
            const fanIndicator = document.getElementById('fan-indicator');
            const fanStatus = document.getElementById('fan-status');
            fanIndicator.className = 'status-indicator ' + (state.fans_on ? 'status-on' : 'status-off');
            fanStatus.textContent = state.fans_on ? 'On' : 'Off';
            
            // Update emergency status
            const emergencyIndicator = document.getElementById('emergency-indicator');
            const emergencyStatus = document.getElementById('emergency-status');
            emergencyIndicator.className = 'status-indicator ' + (state.emergency_mode ? 'status-warning' : 'status-off');
            emergencyStatus.textContent = state.emergency_mode ? 'ACTIVE' : 'Inactive';
            
            // Update door lock status
            const doorIndicator = document.getElementById('door-indicator');
            const doorStatus = document.getElementById('door-status');
            doorIndicator.className = 'status-indicator ' + (state.door_locked ? 'status-off' : 'status-on');
            doorStatus.textContent = state.door_locked ? 'Locked' : 'Unlocked';
            
            // Update garage door status
            const garageIndicator = document.getElementById('garage-indicator');
            const garageStatus = document.getElementById('garage-status');
            const garageTimer = document.getElementById('garage-timer');
            
            garageIndicator.className = 'status-indicator ' + (state.garage_door_open ? 'status-on' : 'status-off');
            garageStatus.textContent = state.garage_door_open ? 'Open' : 'Closed';
            
            // Update auto-close timer if set
            if (state.garage_door_open && state.garage_auto_close_time) {
                const timeRemaining = Math.max(0, Math.floor(state.garage_auto_close_time - Date.now() / 1000));
                if (timeRemaining > 0) {
                    garageTimer.textContent = `Auto-close in ${timeRemaining} seconds`;
                } else {
                    garageTimer.textContent = 'Closing now...';
                }
            } else {
                garageTimer.textContent = 'Not set';
            }
            
            // Update room status
            for (const room in state.motion) {
                // Motion status
                const motionIndicator = document.getElementById(`${room}-motion-indicator`);
                const motionStatus = document.getElementById(`${room}-motion-status`);
                motionIndicator.className = 'status-indicator ' + (state.motion[room] ? 'status-on' : 'status-off');
                motionStatus.textContent = state.motion[room] ? 'Detected' : 'None';
                
                // Light status (inferred from motion + manual override)
                const lightIndicator = document.getElementById(`${room}-light-indicator`);
                const lightStatus = document.getElementById(`${room}-light-status`);
                
                let lightOn = false;
                if (state.emergency_mode) {
                    lightOn = true; // During emergency, lights are red
                } else if (state.manual_override.lights[room]) {
                    // We don't know the exact state, API doesn't report it
                    // This is a simplified approximation
                    lightOn = true;
                } else {
                    lightOn = state.motion[room]; // Normal motion-based control
                }
                
                lightIndicator.className = 'status-indicator ' + (lightOn ? 'status-on' : 'status-off');
                lightStatus.textContent = lightOn ? 'On' : 'Off';
            }
        }
        
        // Handle fan control buttons
        function setupFanButtons() {
            document.getElementById('fan-on').addEventListener('click', () => {
                fetch('/api/control/fan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ state: true })
                });
            });
            
            document.getElementById('fan-off').addEventListener('click', () => {
                fetch('/api/control/fan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ state: false })
                });
            });
            
            document.getElementById('fan-auto').addEventListener('click', () => {
                fetch('/api/control/fan/auto', {
                    method: 'POST'
                });
            });
        }
        
        // Handle light control buttons
        function setupLightButtons() {
            document.querySelectorAll('.light-on').forEach(button => {
                button.addEventListener('click', () => {
                    const room = button.getAttribute('data-room');
                    fetch('/api/control/light', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ room: room, state: true })
                    });
                });
            });
            
            document.querySelectorAll('.light-off').forEach(button => {
                button.addEventListener('click', () => {
                    const room = button.getAttribute('data-room');
                    fetch('/api/control/light', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ room: room, state: false })
                    });
                });
            });
            
            document.querySelectorAll('.light-auto').forEach(button => {
                button.addEventListener('click', () => {
                    const room = button.getAttribute('data-room');
                    fetch('/api/control/light/auto', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ room: room })
                    });
                });
            });
        }
        
        // Handle door lock control buttons
        function setupDoorButtons() {
            document.getElementById('door-lock').addEventListener('click', () => {
                fetch('/api/control/door', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ state: true })
                });
            });
            
            document.getElementById('door-unlock').addEventListener('click', () => {
                fetch('/api/control/door', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ state: false })
                });
            });
            
            document.getElementById('door-auto').addEventListener('click', () => {
                fetch('/api/control/door/auto', {
                    method: 'POST'
                });
            });
        }
        
        // Handle garage door control buttons
        function setupGarageButtons() {
            document.getElementById('garage-open').addEventListener('click', () => {
                fetch('/api/control/garage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ state: true })
                });
            });
            
            document.getElementById('garage-close').addEventListener('click', () => {
                fetch('/api/control/garage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ state: false })
                });
            });
            
            document.getElementById('garage-auto').addEventListener('click', () => {
                fetch('/api/control/garage/auto', {
                    method: 'POST'
                });
            });
        }
        
        // Initialize the page
        document.addEventListener('DOMContentLoaded', () => {
            initRooms();
            setupFanButtons();
            setupLightButtons();
            setupDoorButtons();
            setupGarageButtons();
            
            // Get initial state
            fetch('/api/state')
                .then(response => response.json())
                .then(state => updateUI(state));
            
            // Listen for state updates via Socket.IO
            socket.on('state_update', (state) => {
                updateUI(state);
            });
        });
    </script>
</body>
</html>''')

# Create the automation rules page
def create_automation_template():
    """Create HTML template for automation rules management"""
    with open('templates/automation.html', 'w') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Home Automation Rules</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container mt-4">
        <h1 class="text-center mb-4">Automation Rules Manager</h1>
        
        <div class="text-center mb-3">
            <a href="/" class="btn btn-secondary">Back to Dashboard</a>
            <button id="add-rule-btn" class="btn btn-success ml-2">Add New Rule</button>
            <button id="reset-rules-btn" class="btn btn-danger ml-2">Reset to Default</button>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        Active Rules
                    </div>
                    <div class="card-body">
                        <div id="rules-container">
                            <!-- Rules will be displayed here -->
                            <div class="text-center">
                                <div class="spinner-border" role="status">
                                    <span class="sr-only">Loading...</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Modal for adding/editing rules -->
        <div class="modal fade" id="ruleModal" tabindex="-1" role="dialog" aria-labelledby="ruleModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="ruleModalLabel">Add New Rule</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <form id="rule-form">
                            <input type="hidden" id="rule-id">
                            
                            <div class="form-group">
                                <label for="rule-name">Rule Name</label>
                                <input type="text" class="form-control" id="rule-name" required>
                            </div>
                            
                            <h5>Condition</h5>
                            <div class="form-row">
                                <div class="form-group col-md-4">
                                    <label for="condition-type">Type</label>
                                    <select class="form-control" id="condition-type" required>
                                        <option value="">Select Type</option>
                                        <option value="temperature">Temperature</option>
                                        <option value="humidity">Humidity</option>
                                        <option value="motion">Motion</option>
                                        <option value="gas">Gas Detection</option>
                                        <option value="time">Time</option>
                                    </select>
                                </div>
                                
                                <div class="form-group col-md-4" id="location-field" style="display: none;">
                                    <label for="condition-location">Location</label>
                                    <select class="form-control" id="condition-location">
                                        <option value="any">Any Room</option>
                                        <option value="Room1">Room 1</option>
                                        <option value="Room2">Room 2</option>
                                        <option value="Room3">Room 3</option>
                                        <option value="LivingRoom">Living Room</option>
                                    </select>
                                </div>
                                
                                <div class="form-group col-md-4">
                                    <label for="condition-operator">Operator</label>
                                    <select class="form-control" id="condition-operator" required>
                                        <option value="==">Equals (==)</option>
                                        <option value="!=">Not Equals (!=)</option>
                                        <option value=">">Greater Than (>)</option>
                                        <option value="<">Less Than (<)</option>
                                        <option value=">=">Greater or Equal (>=)</option>
                                        <option value="<=">Less or Equal (<=)</option>
                                    </select>
                                </div>
                                
                                <div class="form-group col-md-4">
                                    <label for="condition-value">Value</label>
                                    <input type="text" class="form-control" id="condition-value" required>
                                    <small class="form-text text-muted" id="value-help">
                                        For temperature/humidity: numeric value
                                    </small>
                                </div>
                            </div>
                            
                            <h5>Action</h5>
                            <div class="form-row">
                                <div class="form-group col-md-4">
                                    <label for="action-type">Type</label>
                                    <select class="form-control" id="action-type" required>
                                        <option value="">Select Type</option>
                                        <option value="fan">Fan Control</option>
                                        <option value="light">Light Control</option>
                                        <option value="door">Door Control</option>
                                        <option value="alert">Alert</option>
                                    </select>
                                </div>
                                
                                <div class="form-group col-md-4" id="action-location-field" style="display: none;">
                                    <label for="action-location">Location</label>
                                    <select class="form-control" id="action-location">
                                        <option value="all">All Rooms</option>
                                        <option value="same">Same as Condition</option>
                                        <option value="Room1">Room 1</option>
                                        <option value="Room2">Room 2</option>
                                        <option value="Room3">Room 3</option>
                                        <option value="LivingRoom">Living Room</option>
                                    </select>
                                </div>
                                
                                <div class="form-group col-md-4">
                                    <label for="action-command">Command</label>
                                    <select class="form-control" id="action-command" required>
                                        <option value="">Select Command</option>
                                        <!-- Options will be populated based on action type -->
                                    </select>
                                </div>
                                
                                <div class="form-group col-md-4" id="alert-type-field" style="display: none;">
                                    <label for="alert-type">Alert Type</label>
                                    <select class="form-control" id="alert-type">
                                        <option value="gas">Gas Alert</option>
                                        <option value="door_open">Door Open</option>
                                        <option value="door_close">Door Close</option>
                                        <option value="unauthorized">Unauthorized</option>
                                        <option value="welcome">Welcome</option>
                                    </select>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="save-rule-btn">Save Rule</button>
                    </div>
                </div>
            </div>
        </div>
        
    </div>
    
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    <script src="/static/automation.js"></script>
</body>
</html>''')

# Create a CSS file for the web interface
def create_css_file():
    """Create a CSS file for the web interface"""
    with open('static/style.css', 'w') as f:
        f.write('''body {
    font-family: 'Arial', sans-serif;
    background-color: #f5f5f5;
    margin: 0;
    padding: 20px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
}

.card {
    margin-bottom: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.card-header {
    background-color: #007bff;
    color: white;
    padding: 10px 15px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: bold;
}

.sensor-value {
    font-size: 1.2em;
    font-weight: bold;
}

.status-indicator {
    display: inline-block;
    width: 15px;
    height: 15px;
    border-radius: 50%;
    margin-right: 5px;
}

.status-on {
    background-color: #28a745;
}

.status-off {
    background-color: #dc3545;
}

.status-warning {
    background-color: #ffc107;
}

.control-buttons {
    margin-top: 15px;
}

.btn {
    margin-right: 5px;
}''')

# Main function
if __name__ == "__main__":
    try:
        # Create the HTML template
        create_html_template()
        create_automation_template()
        create_css_file()
        
        # Load automation rules
        load_rules_from_file()
        print(f"Loaded {len(system_state['automation_rules'])} automation rules")
        
        # Start the sensor monitoring in a separate thread
        sensor_thread = threading.Thread(target=sensor_monitor)
        sensor_thread.daemon = True
        sensor_thread.start()
        
        # Start the Flask web server
        print("Starting web server...")
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\nExiting program")
    finally:
        # Clean up
        buzzer.stop()
        door_servo.stop()
        GPIO.cleanup()
        print("GPIO cleanup completed") 