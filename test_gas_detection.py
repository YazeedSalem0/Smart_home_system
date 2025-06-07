#!/usr/bin/env python3
"""
Test script for Gas Leak Detection with MQ-7 and Emergency Alert (Part 3)
"""

import RPi.GPIO as GPIO
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define pins
GAS_DIGITAL_PIN = 24  # Digital output from MQ-7
# RGB LEDs for emergency alert (same as in motion detection script)
RGB_PINS = {
    'Room1': {'R': 5, 'G': 6, 'B': 13},
    'Room2': {'R': 19, 'G': 26, 'B': 16},
    'Room3': {'R': 20, 'G': 21, 'B': 12},
    'LivingRoom': {'R': 1, 'G': 7, 'B': 8}
}

# Setup digital gas sensor pin as input
GPIO.setup(GAS_DIGITAL_PIN, GPIO.IN)
print(f"Set up MQ-7 digital output on GPIO {GAS_DIGITAL_PIN}")

# Setup RGB LEDs as outputs
for room, pins in RGB_PINS.items():
    for color, pin in pins.items():
        GPIO.setup(pin, GPIO.OUT)
        print(f"Set up {color} LED for {room} on GPIO {pin}")

# Setup I2C for ADS1115
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
gas_channel = AnalogIn(ads, ADS.P0)  # Connect MQ-7 analog output to A0

def set_led_color(room, r_state, g_state, b_state):
    """Set the RGB LED color for a specific room"""
    GPIO.output(RGB_PINS[room]['R'], r_state)
    GPIO.output(RGB_PINS[room]['G'], g_state)
    GPIO.output(RGB_PINS[room]['B'], b_state)

def all_leds_red():
    """Turn all LEDs red for emergency alert"""
    for room in RGB_PINS.keys():
        set_led_color(room, GPIO.HIGH, GPIO.LOW, GPIO.LOW)  # Red color

def all_leds_off():
    """Turn off all LEDs"""
    for room in RGB_PINS.keys():
        set_led_color(room, GPIO.LOW, GPIO.LOW, GPIO.LOW)

def flash_red_alert():
    """Flash all LEDs red for 5 cycles"""
    for _ in range(5):
        all_leds_red()
        time.sleep(0.5)
        all_leds_off()
        time.sleep(0.5)

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

try:
    print("Gas Leak Detection System Active. Press CTRL+C to exit.")
    print("Sensor warming up, please wait...")
    time.sleep(60)  # Allow the MQ-7 sensor to warm up (can be reduced for testing)
    print("Sensor ready for detection.")
    
    # Initial state should be all LEDs off
    all_leds_off()
    
    while True:
        # Read gas sensor
        gas_data = check_gas_sensor()
        
        print(f"Gas Sensor - Digital: {gas_data['digital']}, " +
              f"Analog: {gas_data['analog_raw']}, " +
              f"Voltage: {gas_data['analog_voltage']:.2f}V")
        
        # Check for gas leak detection using digital output
        if gas_data['digital'] == 0:  # Most MQ sensors output LOW when gas is detected
            print("GAS LEAK DETECTED! Flashing red alert!")
            flash_red_alert()
        else:
            print("No gas detected. All clear.")
            all_leds_off()
        
        # Add delay before next reading
        time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting program")
finally:
    # Turn off all LEDs
    all_leds_off()
    
    # Clean up GPIO pins
    GPIO.cleanup()
    print("GPIO cleanup completed") 