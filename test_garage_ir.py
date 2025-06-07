#!/usr/bin/env python3
"""
Test script for IR sensor fingerprint detection and garage door control
"""

import RPi.GPIO as GPIO
import time
import sys

# Define pins
IR_SENSOR_PIN = 15   # GPIO 15 for IR sensor
GARAGE_SERVO_PIN = 11  # GPIO 11 for garage door servo

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup IR sensor as input with pull-up resistor
GPIO.setup(IR_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Setup servo for garage door
GPIO.setup(GARAGE_SERVO_PIN, GPIO.OUT)
garage_servo = GPIO.PWM(GARAGE_SERVO_PIN, 50)  # 50Hz (standard for servos)
garage_servo.start(0)  # Initialize at 0% duty cycle

print("IR Sensor and Garage Door Test Script")
print("=====================================")
print(f"IR Sensor connected to GPIO {IR_SENSOR_PIN}")
print(f"Garage Door Servo connected to GPIO {GARAGE_SERVO_PIN}")
print("The garage door will open when fingerprint is detected")
print("Press Ctrl+C to exit")
print("\nMode options:")
print("1. Auto mode - IR detection opens door, auto-closes after delay")
print("2. Manual control - Use commands to open/close door")
print("3. Sensor test - Just monitor IR sensor without controlling door")

# Default mode
mode = 1

# Get mode from command line argument if provided
if len(sys.argv) > 1:
    try:
        mode_arg = int(sys.argv[1])
        if 1 <= mode_arg <= 3:
            mode = mode_arg
        else:
            print("Invalid mode number. Using default mode 1.")
    except ValueError:
        print("Invalid mode argument. Using default mode 1.")

print(f"\nRunning in mode {mode}")

# Variables for auto-close
door_open = False
auto_close_time = None
AUTO_CLOSE_DELAY = 10  # 10 seconds for test (shorter than production)

def set_garage_door(open_state):
    """
    Control the garage door
    open_state: True for open, False for closed
    """
    global door_open, auto_close_time
    
    if open_state:
        # Open position (120 degrees)
        duty_cycle = 9.0  # 9.0% duty cycle corresponds to 120 degrees
        print("Opening garage door...")
    else:
        # Closed position (0 degrees)
        duty_cycle = 2.5  # 2.5% duty cycle corresponds to 0 degrees
        print("Closing garage door...")
    
    garage_servo.ChangeDutyCycle(duty_cycle)
    time.sleep(1.0)  # Allow servo to reach position
    garage_servo.ChangeDutyCycle(0)  # Stop sending pulses (reduces jitter)
    
    # Update state
    door_open = open_state
    
    # Set auto-close timer if opening the door in auto mode
    if mode == 1 and open_state:
        auto_close_time = time.time() + AUTO_CLOSE_DELAY
        print(f"Door will auto-close in {AUTO_CLOSE_DELAY} seconds")
    else:
        auto_close_time = None

def fingerprint_detected():
    """
    Check if a fingerprint is detected by the IR sensor
    Returns True if detected, False otherwise
    """
    # IR sensor returns LOW (0) when object is detected
    return GPIO.input(IR_SENSOR_PIN) == 0

def handle_auto_close():
    """Handle automatic closing of the garage door after timeout"""
    global door_open, auto_close_time
    
    # Check if auto-close time is set and has been reached
    if (auto_close_time is not None and time.time() >= auto_close_time and door_open):
        print("Auto-closing garage door after timeout")
        set_garage_door(False)  # Close the garage
        auto_close_time = None

def handle_ir_detection():
    """Handle IR fingerprint detection"""
    global door_open
    
    if fingerprint_detected():
        print("IR detection: Object/fingerprint detected!")
        
        # In auto mode, open door if it's closed
        if mode == 1 and not door_open:
            print("Fingerprint recognized - opening garage door")
            set_garage_door(True)
    else:
        pass  # No detection

def print_status():
    """Print current system status"""
    status = "OPEN" if door_open else "CLOSED"
    ir_status = "DETECTED" if fingerprint_detected() else "NONE"
    
    # Build status string
    status_str = f"Door: {status} | IR Sensor: {ir_status}"
    
    # Add auto-close info if applicable
    if auto_close_time is not None:
        remaining = int(auto_close_time - time.time())
        if remaining > 0:
            status_str += f" | Auto-close in: {remaining}s"
    
    # Print and return cursor to start of line
    print(status_str, end="\r")

def run_auto_mode():
    """Run in automatic mode"""
    print("\nRunning in auto mode. Door will open on fingerprint detection and auto-close.")
    print("Press Ctrl+C to exit")
    
    try:
        while True:
            handle_ir_detection()
            handle_auto_close()
            print_status()
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nExiting auto mode")

def run_manual_mode():
    """Run in manual control mode"""
    print("\nRunning in manual mode. Use the following commands:")
    print("  o - Open garage door")
    print("  c - Close garage door")
    print("  q - Quit")
    
    try:
        while True:
            print_status()
            
            # Check if key is pressed
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                command = sys.stdin.read(1).lower()
                
                if command == 'o':
                    set_garage_door(True)
                elif command == 'c':
                    set_garage_door(False)
                elif command == 'q':
                    break
            
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nExiting manual mode")

def run_sensor_test():
    """Run in sensor test mode"""
    print("\nRunning in sensor test mode. Monitoring IR sensor only.")
    print("Press Ctrl+C to exit")
    
    try:
        last_state = None
        while True:
            current_state = fingerprint_detected()
            
            # Print only on state change to reduce output
            if current_state != last_state:
                if current_state:
                    print("IR SENSOR: Fingerprint detected!")
                else:
                    print("IR SENSOR: No detection")
                last_state = current_state
            
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nExiting sensor test mode")

# Main execution
try:
    # Ensure garage door is closed initially
    set_garage_door(False)
    time.sleep(1)
    
    # Import select module only if needed for manual mode
    if mode == 2:
        import select
        import termios
        import tty
        
        # Set terminal to raw mode
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())
        
    # Run in selected mode
    if mode == 1:
        run_auto_mode()
    elif mode == 2:
        run_manual_mode()
    elif mode == 3:
        run_sensor_test()
        
except Exception as e:
    print(f"\nError: {e}")
finally:
    # Clean up
    if mode == 2:
        # Restore terminal settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    
    # Ensure garage door is closed
    set_garage_door(False)
    time.sleep(1)
    
    # Clean up GPIO
    garage_servo.stop()
    GPIO.cleanup()
    print("\nGPIO cleanup completed") 