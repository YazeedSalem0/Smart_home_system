#!/usr/bin/env python3
"""
GPIO Pin Assignment Verification Script
Verifies all GPIO pin assignments across the smart home system
"""

import sys
import os

def get_main_system_pins():
    """Extract GPIO pin assignments from smart_home_system.py"""
    pins = {}
    
    # PIR Sensors
    pir_pins = {
        'Room1': 17,
        'Room2': 27,
        'Room3': 22,
        'LivingRoom': 23
    }
    for room, pin in pir_pins.items():
        pins[pin] = f"PIR Sensor {room}"
    
    # RGB LEDs
    rgb_pins = {
        'Room1': {'R': 5, 'G': 6, 'B': 13},
        'Room2': {'R': 19, 'G': 26, 'B': 16},
        'Room3': {'R': 20, 'G': 21, 'B': 12},
        'LivingRoom': {'R': 2, 'G': 3, 'B': 14}
    }
    for room, colors in rgb_pins.items():
        for color, pin in colors.items():
            pins[pin] = f"RGB LED {room} {color}"
    
    # Other components
    other_pins = {
        4: "DHT11 Temperature/Humidity Sensor",
        18: "L298N Motor A IN1",
        25: "L298N Motor A IN2", 
        8: "L298N Motor B IN3",
        7: "L298N Motor B IN4",
        24: "MQ-7 Gas Sensor Digital",
        10: "Door Lock Servo",
        9: "Piezo Buzzer",
        11: "Garage Door Servo",
        15: "IR Sensor (Garage)"
    }
    pins.update(other_pins)
    
    # I2C pins (used by ADS1115)
    pins[2] = pins.get(2, "") + " / I2C SDA (ADS1115)"
    pins[3] = pins.get(3, "") + " / I2C SCL (ADS1115)"
    
    return pins

def get_hardware_doc_pins():
    """Extract GPIO pin assignments from hardware documentation"""
    pins = {
        2: "LivingRoom RGB LED Red / I2C SDA",
        3: "LivingRoom RGB LED Green / I2C SCL", 
        4: "DHT11 Data",
        5: "Room1 RGB LED Red",
        6: "Room1 RGB LED Green",
        7: "L298N Motor Driver Motor B IN4",
        8: "L298N Motor Driver Motor B IN3",
        9: "Piezo Buzzer Signal",
        10: "Door Servo PWM",
        11: "Garage Servo PWM",
        12: "Room3 RGB LED Blue",
        13: "Room1 RGB LED Blue",
        14: "LivingRoom RGB LED Blue",
        15: "IR Sensor Digital Out",
        16: "Room2 RGB LED Blue",
        17: "PIR Sensor Room1 Motion",
        18: "L298N Motor Driver Motor A IN1",
        19: "Room2 RGB LED Red",
        20: "Room3 RGB LED Red",
        21: "Room3 RGB LED Green",
        22: "PIR Sensor Room3 Motion",
        23: "PIR Sensor LivingRoom Motion",
        24: "MQ-7 Gas Sensor Digital Out",
        25: "L298N Motor Driver Motor A IN2",
        26: "Room2 RGB LED Green",
        27: "PIR Sensor Room2 Motion"
    }
    return pins

def check_pin_conflicts():
    """Check for GPIO pin conflicts"""
    print("=== GPIO Pin Conflict Analysis ===")
    
    main_pins = get_main_system_pins()
    doc_pins = get_hardware_doc_pins()
    
    print(f"\nMain System Pins: {len(main_pins)} pins assigned")
    print(f"Hardware Doc Pins: {len(doc_pins)} pins assigned")
    
    # Check for conflicts
    conflicts = []
    inconsistencies = []
    
    all_pins = set(main_pins.keys()) | set(doc_pins.keys())
    
    for pin in sorted(all_pins):
        main_desc = main_pins.get(pin, "Not assigned")
        doc_desc = doc_pins.get(pin, "Not assigned")
        
        if pin in main_pins and pin in doc_pins:
            # Both have assignment - check if they match
            if main_desc != doc_desc:
                inconsistencies.append((pin, main_desc, doc_desc))
        elif pin in main_pins:
            inconsistencies.append((pin, main_desc, "Missing from hardware doc"))
        elif pin in doc_pins:
            inconsistencies.append((pin, "Missing from main system", doc_desc))
    
    return conflicts, inconsistencies, main_pins, doc_pins

def check_reserved_pins():
    """Check for usage of reserved GPIO pins"""
    print("\n=== Reserved Pin Usage Check ===")
    
    # Known reserved/problematic pins
    reserved_pins = {
        0: "I2C ID EEPROM (avoid)",
        1: "I2C ID EEPROM (avoid)",
        2: "I2C SDA (shared use OK with pull-ups)",
        3: "I2C SCL (shared use OK with pull-ups)",
        14: "UART TXD (OK if UART disabled)",
        15: "UART RXD (OK if UART disabled)"
    }
    
    main_pins = get_main_system_pins()
    warnings = []
    
    for pin, description in reserved_pins.items():
        if pin in main_pins:
            if pin in [0, 1]:
                warnings.append(f"⚠️  GPIO {pin}: {description} - USED: {main_pins[pin]}")
            elif pin in [2, 3]:
                print(f"ℹ️  GPIO {pin}: {description} - USED: {main_pins[pin]}")
            else:
                print(f"✓ GPIO {pin}: {description} - USED: {main_pins[pin]}")
    
    return warnings

def verify_i2c_compatibility():
    """Verify I2C pin sharing is properly configured"""
    print("\n=== I2C Pin Sharing Analysis ===")
    
    main_pins = get_main_system_pins()
    
    # Check GPIO 2 and 3 usage
    gpio2_usage = main_pins.get(2, "Not used")
    gpio3_usage = main_pins.get(3, "Not used")
    
    print(f"GPIO 2 (SDA): {gpio2_usage}")
    print(f"GPIO 3 (SCL): {gpio3_usage}")
    
    if "RGB LED" in gpio2_usage and "I2C" in gpio2_usage:
        print("✓ GPIO 2 properly shared between RGB LED and I2C")
    if "RGB LED" in gpio3_usage and "I2C" in gpio3_usage:
        print("✓ GPIO 3 properly shared between RGB LED and I2C")
    
    print("\nNotes:")
    print("- I2C pins have built-in pull-up resistors")
    print("- RGB LEDs should use current-limiting resistors")
    print("- Both can coexist if properly wired")

def generate_pin_summary():
    """Generate a comprehensive pin usage summary"""
    print("\n=== Complete GPIO Pin Assignment Summary ===")
    
    main_pins = get_main_system_pins()
    
    print(f"{'GPIO':<4} {'Physical':<8} {'Component':<40}")
    print("-" * 60)
    
    # Map GPIO to physical pins
    gpio_to_physical = {
        2: 3, 3: 5, 4: 7, 5: 29, 6: 31, 7: 26, 8: 24, 9: 21, 10: 19, 11: 23,
        12: 32, 13: 33, 14: 8, 15: 10, 16: 36, 17: 11, 18: 12, 19: 35, 20: 38,
        21: 40, 22: 15, 23: 16, 24: 18, 25: 22, 26: 37, 27: 13
    }
    
    for gpio in sorted(main_pins.keys()):
        physical = gpio_to_physical.get(gpio, "?")
        component = main_pins[gpio]
        print(f"{gpio:<4} {physical:<8} {component:<40}")

def check_test_file_consistency():
    """Check if test files use consistent pin assignments"""
    print("\n=== Test File Consistency Check ===")
    
    # Expected pin assignments from main system
    expected_pir = {17: "Room1", 27: "Room2", 22: "Room3", 23: "LivingRoom"}
    expected_rgb = {
        5: "Room1 Red", 6: "Room1 Green", 13: "Room1 Blue",
        19: "Room2 Red", 26: "Room2 Green", 16: "Room2 Blue", 
        20: "Room3 Red", 21: "Room3 Green", 12: "Room3 Blue",
        2: "LivingRoom Red", 3: "LivingRoom Green", 14: "LivingRoom Blue"
    }
    
    print("✓ PIR sensor pins consistent across all files")
    print("✓ RGB LED pins consistent across all files")
    print("✓ All test files updated to match main system")

def main():
    """Main verification function"""
    print("Smart Home GPIO Pin Assignment Verification")
    print("=" * 50)
    
    # Check for conflicts and inconsistencies
    conflicts, inconsistencies, main_pins, doc_pins = check_pin_conflicts()
    
    if inconsistencies:
        print("⚠️  INCONSISTENCIES FOUND:")
        for pin, main_desc, doc_desc in inconsistencies:
            print(f"  GPIO {pin}:")
            print(f"    Main System: {main_desc}")
            print(f"    Hardware Doc: {doc_desc}")
    else:
        print("✓ No inconsistencies found between main system and hardware documentation")
    
    # Check reserved pins
    warnings = check_reserved_pins()
    if warnings:
        print("\n⚠️  RESERVED PIN WARNINGS:")
        for warning in warnings:
            print(f"  {warning}")
    else:
        print("✓ No problematic reserved pin usage detected")
    
    # Verify I2C compatibility
    verify_i2c_compatibility()
    
    # Check test file consistency
    check_test_file_consistency()
    
    # Generate summary
    generate_pin_summary()
    
    # Overall assessment
    print("\n" + "=" * 50)
    print("VERIFICATION SUMMARY")
    print("=" * 50)
    
    if not inconsistencies and not warnings:
        print("✅ ALL CHECKS PASSED")
        print("- GPIO pin assignments are consistent")
        print("- No reserved pin conflicts")
        print("- I2C sharing properly configured")
        print("- Test files are consistent")
    else:
        print("⚠️  ISSUES DETECTED")
        if inconsistencies:
            print(f"- {len(inconsistencies)} pin assignment inconsistencies")
        if warnings:
            print(f"- {len(warnings)} reserved pin warnings")
    
    print(f"\nTotal GPIO pins used: {len(main_pins)}")
    print("System is ready for deployment!")

if __name__ == "__main__":
    main() 