#!/usr/bin/env python3
"""
Test script for Motion Detection with PIR Sensors and RGB LEDs (Part 1)
"""

import RPi.GPIO as GPIO
import time

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define GPIO pins for PIR sensors
PIR_PINS = {
    'Room1': 17,
    'Room2': 27,
    'Room3': 22,
    'LivingRoom': 23
}

# Define GPIO pins for RGB LEDs
RGB_PINS = {
    'Room1': {'R': 5, 'G': 6, 'B': 13},
    'Room2': {'R': 19, 'G': 26, 'B': 16},
    'Room3': {'R': 20, 'G': 21, 'B': 12},
    'LivingRoom': {'R': 2, 'G': 3, 'B': 14}
}

# Setup PIR sensors as inputs
for room, pin in PIR_PINS.items():
    GPIO.setup(pin, GPIO.IN)
    print(f"Set up PIR sensor for {room} on GPIO {pin}")

# Setup RGB LEDs as outputs
for room, pins in RGB_PINS.items():
    for color, pin in pins.items():
        GPIO.setup(pin, GPIO.OUT)
        print(f"Set up {color} LED for {room} on GPIO {pin}")

def set_led_color(room, r_state, g_state, b_state):
    """Set the RGB LED color for a specific room"""
    GPIO.output(RGB_PINS[room]['R'], r_state)
    GPIO.output(RGB_PINS[room]['G'], g_state)
    GPIO.output(RGB_PINS[room]['B'], b_state)

def led_white(room):
    """Turn on white color (R+G+B ON)"""
    set_led_color(room, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH)

def led_off(room):
    """Turn off the LED"""
    set_led_color(room, GPIO.LOW, GPIO.LOW, GPIO.LOW)

def motion_detected_callback(channel):
    """Callback function for motion detection"""
    # Find which room triggered the motion
    room = None
    for r, pin in PIR_PINS.items():
        if pin == channel:
            room = r
            break
    
    if room:
        if GPIO.input(channel):  # If motion detected
            print(f"Motion detected in {room}! Turning LED white.")
            led_white(room)
        else:  # If no motion
            print(f"No motion in {room}. Turning LED off.")
            led_off(room)

# Add event detection for PIR sensors
for room, pin in PIR_PINS.items():
    # Add both rising and falling edge detection
    GPIO.add_event_detect(pin, GPIO.BOTH, callback=motion_detected_callback)
    print(f"Added motion detection for {room}")

try:
    print("Motion detection system active. Press CTRL+C to exit.")
    # Initial state check for all rooms
    for room, pin in PIR_PINS.items():
        if GPIO.input(pin):
            print(f"Initial state: Motion detected in {room}")
            led_white(room)
        else:
            print(f"Initial state: No motion in {room}")
            led_off(room)
    
    # Keep the script running
    while True:
        time.sleep(0.1)  # Small delay to prevent CPU hogging

except KeyboardInterrupt:
    print("\nExiting program")
finally:
    # Clean up GPIO pins
    GPIO.cleanup()
    print("GPIO cleanup completed") 