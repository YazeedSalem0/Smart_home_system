#!/usr/bin/env python3
"""
Test script for Temperature and Humidity Monitoring with DHT11 and L298N Motor Driver Fan Control
Updated for L298N Motor Driver with 2 DC Motors
"""

import RPi.GPIO as GPIO
import Adafruit_DHT
import time

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define pins
DHT_PIN = 4  # DHT11 data pin
TEMPERATURE_THRESHOLD = 25.0  # Temperature threshold in Celsius

# L298N Motor Driver pin connections
IN1 = 18  # Motor A direction control 1
IN2 = 25  # Motor A direction control 2
IN3 = 8   # Motor B direction control 1
IN4 = 7   # Motor B direction control 2

# Setup motor control pins
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# Initialize all motors to stop
GPIO.output(IN1, GPIO.LOW)
GPIO.output(IN2, GPIO.LOW)
GPIO.output(IN3, GPIO.LOW)
GPIO.output(IN4, GPIO.LOW)

print(f"Set up L298N Motor Driver:")
print(f"  IN1 (Motor A Dir 1): GPIO {IN1}")
print(f"  IN2 (Motor A Dir 2): GPIO {IN2}")
print(f"  IN3 (Motor B Dir 1): GPIO {IN3}")
print(f"  IN4 (Motor B Dir 2): GPIO {IN4}")

def motor_a_forward():
    """Motor A forward rotation (Fan 1 ON)"""
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)

def motor_a_stop():
    """Motor A stop (Fan 1 OFF)"""
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)

def motor_b_forward():
    """Motor B forward rotation (Fan 2 ON)"""
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def motor_b_stop():
    """Motor B stop (Fan 2 OFF)"""
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

def control_fans(turn_on):
    """Control both fans using L298N motor driver"""
    if turn_on:
        motor_a_forward()
        motor_b_forward()
        print("Both fans ON (forward rotation)")
    else:
        motor_a_stop()
        motor_b_stop()
        print("Both fans OFF")

def stop_all_motors():
    """Stop both motors"""
    motor_a_stop()
    motor_b_stop()

def read_dht11():
    """Read temperature and humidity from DHT11 sensor"""
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT_PIN)
    return humidity, temperature

def control_fans_based_on_temperature(temperature):
    """Control fans based on temperature threshold"""
    if temperature is not None:
        if temperature >= TEMPERATURE_THRESHOLD:
            control_fans(True)
            return True
        else:
            control_fans(False)
            return False
    return None

try:
    print("Temperature and L298N Fan Control System Active. Press CTRL+C to exit.")
    print(f"Temperature threshold set to {TEMPERATURE_THRESHOLD}°C")
    print("Note: Ensure L298N ENA and ENB pins are connected to 5V for motor enable")
    
    while True:
        # Read sensor data
        humidity, temperature = read_dht11()
        
        # Display readings
        if humidity is not None and temperature is not None:
            print(f"Temperature: {temperature:.1f}°C, Humidity: {humidity:.1f}%")
            
            # Control fans based on temperature
            fans_on = control_fans_based_on_temperature(temperature)
            if fans_on:
                print(f"Temperature ({temperature:.1f}°C) >= {TEMPERATURE_THRESHOLD}°C: Fans ON")
            else:
                print(f"Temperature ({temperature:.1f}°C) < {TEMPERATURE_THRESHOLD}°C: Fans OFF")
        else:
            print("Failed to get reading from DHT sensor. Trying again...")
        
        # Wait before next reading
        time.sleep(2)

except KeyboardInterrupt:
    print("\nExiting program")
finally:
    # Ensure all motors are stopped
    stop_all_motors()
    
    # Clean up GPIO pins
    GPIO.cleanup()
    print("GPIO cleanup completed - All motors stopped") 