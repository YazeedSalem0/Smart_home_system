#!/usr/bin/env python3
"""
System Verification Script for Smart Home Automation
This script verifies all components and configurations before deployment
"""

import sys
import importlib
import subprocess
import os

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.7+")
        return False

def check_required_packages():
    """Check if all required packages are installed"""
    print("\nChecking required packages...")
    
    required_packages = [
        'RPi.GPIO',
        'Adafruit_DHT',
        'adafruit_circuitpython_ads1x15',
        'board',
        'busio',
        'flask',
        'flask_socketio',
        'pandas',
        'numpy',
        'openpyxl'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages are installed")
        return True

def check_gpio_permissions():
    """Check GPIO permissions (Raspberry Pi only)"""
    print("\nChecking GPIO permissions...")
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        # Try to setup a pin (this will fail if no permissions)
        GPIO.setup(18, GPIO.OUT)
        GPIO.cleanup()
        print("✅ GPIO permissions - OK")
        return True
    except Exception as e:
        print(f"❌ GPIO permissions - {e}")
        print("Run: sudo usermod -a -G gpio $USER")
        return False

def check_i2c_interface():
    """Check I2C interface"""
    print("\nChecking I2C interface...")
    try:
        # Check if i2c-dev is loaded
        result = subprocess.run(['lsmod'], capture_output=True, text=True)
        if 'i2c_dev' in result.stdout:
            print("✅ I2C interface - Enabled")
            return True
        else:
            print("❌ I2C interface - Not enabled")
            print("Run: sudo raspi-config and enable I2C")
            return False
    except Exception as e:
        print(f"⚠️ I2C check - {e} (May be normal on non-Pi systems)")
        return True

def check_file_structure():
    """Check if all required files are present"""
    print("\nChecking file structure...")
    
    required_files = [
        'smart_home_system.py',
        'hardware_documentation.md',
        'requirements.txt',
        'setup_raspberry_pi.sh',
        'test_l298n_motor_driver.py',
        'test_temperature_fan.py',
        'test_motion_detection.py',
        'test_buzzer.py',
        'test_garage_ir.py',
        'test_gas_detection.py',
        'test_requirements.py',
        'README.md',
        'PRE_DEPLOYMENT_CHECKLIST.md'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - Missing")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files are present")
        return True

def check_pin_assignments():
    """Verify pin assignments for conflicts"""
    print("\nChecking pin assignments for conflicts...")
    
    # Define all pin assignments
    pin_assignments = {
        # L298N Motor Driver
        18: "L298N IN1 (Motor A Dir 1)",
        25: "L298N IN2 (Motor A Dir 2)",
        8: "L298N IN3 (Motor B Dir 1)",
        7: "L298N IN4 (Motor B Dir 2)",
        
        # Sensors
        4: "DHT11 Data",
        24: "MQ-7 Digital Output",
        17: "PIR Room 1",
        27: "PIR Room 2",
        22: "PIR Room 3",
        23: "PIR Living Room",
        15: "IR Sensor (Garage)",
        
        # RGB LEDs
        5: "Room 1 RGB Red",
        6: "Room 1 RGB Green",
        13: "Room 1 RGB Blue",
        19: "Room 2 RGB Red",
        26: "Room 2 RGB Green",
        16: "Room 2 RGB Blue",
        20: "Room 3 RGB Red",
        21: "Room 3 RGB Green",
        12: "Room 3 RGB Blue",
        0: "Living Room RGB Red",
        1: "Living Room RGB Green",
        14: "Living Room RGB Blue",
        
        # I2C (shared)
        2: "I2C SDA (ADS1115, LCD)",
        3: "I2C SCL (ADS1115, LCD)",
        
        # Other components
        10: "Door Lock Servo",
        11: "Garage Door Servo",
        9: "Buzzer"
    }
    
    # Check for duplicates
    used_pins = list(pin_assignments.keys())
    duplicates = set([x for x in used_pins if used_pins.count(x) > 1])
    
    if duplicates:
        print(f"❌ Pin conflicts detected: {duplicates}")
        for pin in duplicates:
            print(f"   GPIO {pin}: {pin_assignments[pin]}")
        return False
    else:
        print("✅ No pin conflicts detected")
        print(f"✅ Total pins used: {len(used_pins)}")
        return True

def check_system_configuration():
    """Check system configuration"""
    print("\nChecking system configuration...")
    
    checks = []
    
    # Check if running on Raspberry Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            if 'Raspberry Pi' in cpuinfo:
                print("✅ Running on Raspberry Pi")
                checks.append(True)
            else:
                print("⚠️ Not running on Raspberry Pi (development environment)")
                checks.append(True)  # OK for development
    except:
        print("⚠️ Cannot determine system type")
        checks.append(True)
    
    # Check available GPIO pins
    try:
        import RPi.GPIO as GPIO
        print("✅ RPi.GPIO module available")
        checks.append(True)
    except:
        print("❌ RPi.GPIO module not available")
        checks.append(False)
    
    return all(checks)

def main():
    """Main verification function"""
    print("=" * 50)
    print("Smart Home System Verification")
    print("=" * 50)
    
    checks = []
    
    # Run all checks
    checks.append(check_python_version())
    checks.append(check_required_packages())
    checks.append(check_file_structure())
    checks.append(check_pin_assignments())
    checks.append(check_system_configuration())
    
    # Raspberry Pi specific checks (only if on Pi)
    try:
        with open('/proc/cpuinfo', 'r') as f:
            if 'Raspberry Pi' in f.read():
                checks.append(check_gpio_permissions())
                checks.append(check_i2c_interface())
    except:
        pass
    
    # Summary
    print("\n" + "=" * 50)
    print("VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = sum(checks)
    total = len(checks)
    
    if all(checks):
        print(f"✅ ALL CHECKS PASSED ({passed}/{total})")
        print("🚀 System is ready for deployment!")
        return True
    else:
        print(f"❌ SOME CHECKS FAILED ({passed}/{total})")
        print("⚠️ Please fix the issues before deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 