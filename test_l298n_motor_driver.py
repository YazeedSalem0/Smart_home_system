#!/usr/bin/env python3
"""
Test script for L298N Motor Driver with 2 DC Motors
This script tests the L298N motor driver functionality for controlling 2 DC motors (fans)
"""

import RPi.GPIO as GPIO
import time

# L298N Motor Driver pin connections
IN1 = 18  # Motor A direction control 1 (GPIO 18, Pin 12)
IN2 = 25  # Motor A direction control 2 (GPIO 25, Pin 22)
IN3 = 8   # Motor B direction control 1 (GPIO 8, Pin 24)
IN4 = 7   # Motor B direction control 2 (GPIO 7, Pin 26)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup motor control pins
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

print("L298N Motor Driver Test Script")
print("=============================")
print(f"Motor A Control: IN1=GPIO{IN1}, IN2=GPIO{IN2}")
print(f"Motor B Control: IN3=GPIO{IN3}, IN4=GPIO{IN4}")
print("Note: Ensure ENA and ENB are connected to 5V for motor enable")
print("Note: Connect external power supply to +12V terminal for better performance")
print()

def motor_a_forward():
    """Motor A forward rotation"""
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    print("Motor A: Forward")

def motor_a_reverse():
    """Motor A reverse rotation"""
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    print("Motor A: Reverse")

def motor_a_stop():
    """Motor A stop"""
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    print("Motor A: Stop")

def motor_b_forward():
    """Motor B forward rotation"""
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    print("Motor B: Forward")

def motor_b_reverse():
    """Motor B reverse rotation"""
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    print("Motor B: Reverse")

def motor_b_stop():
    """Motor B stop"""
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    print("Motor B: Stop")

def stop_all_motors():
    """Stop both motors"""
    motor_a_stop()
    motor_b_stop()
    print("All motors stopped")

def test_individual_motors():
    """Test each motor individually"""
    print("Testing Individual Motors")
    print("-------------------------")
    
    # Test Motor A
    print("\n1. Testing Motor A...")
    print("Motor A Forward for 3 seconds")
    motor_a_forward()
    time.sleep(3)
    
    print("Motor A Stop for 1 second")
    motor_a_stop()
    time.sleep(1)
    
    print("Motor A Reverse for 3 seconds")
    motor_a_reverse()
    time.sleep(3)
    
    print("Motor A Stop")
    motor_a_stop()
    time.sleep(1)
    
    # Test Motor B
    print("\n2. Testing Motor B...")
    print("Motor B Forward for 3 seconds")
    motor_b_forward()
    time.sleep(3)
    
    print("Motor B Stop for 1 second")
    motor_b_stop()
    time.sleep(1)
    
    print("Motor B Reverse for 3 seconds")
    motor_b_reverse()
    time.sleep(3)
    
    print("Motor B Stop")
    motor_b_stop()
    time.sleep(1)

def test_both_motors():
    """Test both motors together"""
    print("\n3. Testing Both Motors Together...")
    print("----------------------------------")
    
    print("Both Motors Forward for 3 seconds")
    motor_a_forward()
    motor_b_forward()
    time.sleep(3)
    
    print("Both Motors Stop for 1 second")
    stop_all_motors()
    time.sleep(1)
    
    print("Both Motors Reverse for 3 seconds")
    motor_a_reverse()
    motor_b_reverse()
    time.sleep(3)
    
    print("Both Motors Stop")
    stop_all_motors()
    time.sleep(1)

def test_alternating_motors():
    """Test alternating motor operation"""
    print("\n4. Testing Alternating Motors...")
    print("--------------------------------")
    
    for i in range(3):
        print(f"Cycle {i+1}: Motor A Forward, Motor B Reverse")
        motor_a_forward()
        motor_b_reverse()
        time.sleep(2)
        
        print(f"Cycle {i+1}: Motor A Reverse, Motor B Forward")
        motor_a_reverse()
        motor_b_forward()
        time.sleep(2)
        
        print(f"Cycle {i+1}: Both Motors Stop")
        stop_all_motors()
        time.sleep(1)

def interactive_test():
    """Interactive motor control test"""
    print("\n5. Interactive Test Mode")
    print("------------------------")
    print("Commands:")
    print("  a1 - Motor A Forward")
    print("  a2 - Motor A Reverse")
    print("  a0 - Motor A Stop")
    print("  b1 - Motor B Forward")
    print("  b2 - Motor B Reverse")
    print("  b0 - Motor B Stop")
    print("  both1 - Both Motors Forward")
    print("  both2 - Both Motors Reverse")
    print("  both0 - Both Motors Stop")
    print("  q - Quit interactive mode")
    print()
    
    while True:
        try:
            cmd = input("Enter command: ").strip().lower()
            
            if cmd == 'q':
                break
            elif cmd == 'a1':
                motor_a_forward()
            elif cmd == 'a2':
                motor_a_reverse()
            elif cmd == 'a0':
                motor_a_stop()
            elif cmd == 'b1':
                motor_b_forward()
            elif cmd == 'b2':
                motor_b_reverse()
            elif cmd == 'b0':
                motor_b_stop()
            elif cmd == 'both1':
                motor_a_forward()
                motor_b_forward()
                print("Both Motors: Forward")
            elif cmd == 'both2':
                motor_a_reverse()
                motor_b_reverse()
                print("Both Motors: Reverse")
            elif cmd == 'both0':
                stop_all_motors()
            else:
                print("Invalid command. Try again.")
        except KeyboardInterrupt:
            break
    
    print("Exiting interactive mode...")

try:
    # Initialize motors to stop
    stop_all_motors()
    time.sleep(1)
    
    print("Starting L298N Motor Driver Tests...")
    print("Press CTRL+C at any time to stop\n")
    
    # Run all tests
    test_individual_motors()
    test_both_motors()
    test_alternating_motors()
    
    # Ask user if they want interactive mode
    response = input("\nWould you like to run interactive test mode? (y/n): ")
    if response.lower().startswith('y'):
        interactive_test()
    
    print("\nAll tests completed successfully!")

except KeyboardInterrupt:
    print("\nTest interrupted by user")
except Exception as e:
    print(f"\nError during test: {e}")
finally:
    # Ensure all motors are stopped
    stop_all_motors()
    
    # Clean up GPIO pins
    GPIO.cleanup()
    print("GPIO cleanup completed - All motors stopped")
    print("\nL298N Motor Driver Test Complete!")
    print("\nTroubleshooting Tips:")
    print("- If motors don't spin: Check ENA/ENB connections to 5V")
    print("- If motors are slow: Use external power supply on +12V terminal")
    print("- If wrong direction: Swap motor wires or modify code logic")
    print("- If Pi reboots: Use separate power supply for motors") 