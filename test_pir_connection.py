#!/usr/bin/env python3
"""
PIR Sensor Connection Test Script
Tests all PIR sensors and their connections to diagnose issues
"""

import RPi.GPIO as GPIO
import time
import sys

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# PIR sensor pins (matching the main system configuration)
PIR_PINS = {
    'Room1': 17,
    'Room2': 27,
    'Room3': 22,
    'LivingRoom': 23
}

def test_pir_sensors():
    """Test all PIR sensors individually"""
    print("=== PIR Sensor Connection Test ===")
    print(f"Testing {len(PIR_PINS)} PIR sensors...")
    
    # Setup all PIR pins as inputs
    for room, pin in PIR_PINS.items():
        try:
            GPIO.setup(pin, GPIO.IN)
            print(f"✓ Set up PIR sensor for {room} on GPIO {pin}")
        except Exception as e:
            print(f"✗ Error setting up PIR sensor for {room} on GPIO {pin}: {e}")
            return False
    
    print("\n=== Initial State Check ===")
    for room, pin in PIR_PINS.items():
        try:
            state = GPIO.input(pin)
            print(f"{room} (GPIO {pin}): {'MOTION DETECTED' if state else 'NO MOTION'}")
        except Exception as e:
            print(f"✗ Error reading {room} (GPIO {pin}): {e}")
    
    print("\n=== Real-time Motion Detection Test ===")
    print("Move around near each sensor to test detection...")
    print("Press CTRL+C to exit")
    
    # Store previous states to detect changes
    previous_states = {room: GPIO.input(pin) for room, pin in PIR_PINS.items()}
    
    try:
        while True:
            for room, pin in PIR_PINS.items():
                try:
                    current_state = GPIO.input(pin)
                    if current_state != previous_states[room]:
                        timestamp = time.strftime("%H:%M:%S")
                        if current_state:
                            print(f"[{timestamp}] 🔴 MOTION DETECTED in {room} (GPIO {pin})")
                        else:
                            print(f"[{timestamp}] 🟢 Motion ended in {room} (GPIO {pin})")
                        previous_states[room] = current_state
                except Exception as e:
                    print(f"✗ Error reading {room} during monitoring: {e}")
            
            time.sleep(0.1)  # Small delay to prevent CPU hogging
            
    except KeyboardInterrupt:
        print("\n\n=== Test Complete ===")
        return True

def test_individual_sensor(room_name):
    """Test a specific PIR sensor"""
    if room_name not in PIR_PINS:
        print(f"Error: Room '{room_name}' not found. Available rooms: {list(PIR_PINS.keys())}")
        return False
    
    pin = PIR_PINS[room_name]
    print(f"=== Testing {room_name} PIR Sensor (GPIO {pin}) ===")
    
    try:
        GPIO.setup(pin, GPIO.IN)
        print(f"✓ PIR sensor setup successful")
        
        print("Monitoring for 30 seconds...")
        start_time = time.time()
        motion_count = 0
        
        while time.time() - start_time < 30:
            state = GPIO.input(pin)
            if state:
                motion_count += 1
                print(f"Motion detected! (Count: {motion_count})")
                time.sleep(1)  # Avoid rapid counting
            time.sleep(0.1)
        
        print(f"Test complete. Total motion detections: {motion_count}")
        return True
        
    except Exception as e:
        print(f"✗ Error testing {room_name}: {e}")
        return False

def check_gpio_conflicts():
    """Check for potential GPIO pin conflicts"""
    print("=== GPIO Pin Conflict Check ===")
    
    # Known reserved pins
    reserved_pins = {
        0: "I2C SDA (Reserved)",
        1: "I2C SCL (Reserved)", 
        2: "I2C SDA",
        3: "I2C SCL",
        4: "DHT11 (Temperature sensor)",
        5: "RGB LED Room1 Red",
        6: "RGB LED Room1 Green",
        7: "Motor B control",
        8: "Motor B control",
        9: "Buzzer",
        10: "Door servo",
        11: "Garage servo",
        12: "RGB LED Room3 Blue",
        13: "RGB LED Room1 Blue",
        14: "RGB LED LivingRoom Blue",
        15: "IR sensor",
        16: "RGB LED Room2 Blue",
        17: "PIR Room1",
        18: "Motor A control",
        19: "RGB LED Room2 Red",
        20: "RGB LED Room3 Red",
        21: "RGB LED Room3 Green",
        22: "PIR Room3",
        23: "PIR LivingRoom",
        24: "Gas sensor digital",
        25: "Motor A control",
        26: "RGB LED Room2 Green",
        27: "PIR Room2"
    }
    
    print("Current pin assignments:")
    for pin, usage in reserved_pins.items():
        print(f"GPIO {pin:2d}: {usage}")
    
    # Check for conflicts
    conflicts = []
    pir_pins = list(PIR_PINS.values())
    
    for pin in pir_pins:
        if pin in [0, 1]:  # I2C pins
            conflicts.append(f"PIR sensor on GPIO {pin} conflicts with I2C")
    
    if conflicts:
        print("\n⚠️  CONFLICTS DETECTED:")
        for conflict in conflicts:
            print(f"  - {conflict}")
        return False
    else:
        print("\n✓ No GPIO conflicts detected")
        return True

def main():
    """Main test function"""
    if len(sys.argv) > 1:
        # Test specific sensor
        room_name = sys.argv[1]
        success = test_individual_sensor(room_name)
    else:
        # Test all sensors
        print("Smart Home PIR Sensor Test")
        print("Usage: python test_pir_connection.py [room_name]")
        print(f"Available rooms: {list(PIR_PINS.keys())}")
        print()
        
        # Check for conflicts first
        check_gpio_conflicts()
        print()
        
        # Test all sensors
        success = test_pir_sensors()
    
    # Cleanup
    try:
        GPIO.cleanup()
        print("GPIO cleanup completed")
    except:
        pass
    
    return success

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Test failed with error: {e}")
        GPIO.cleanup()
        sys.exit(1) 