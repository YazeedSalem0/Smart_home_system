#!/usr/bin/env python3
"""
Test if all required packages are installed for the Smart Home Automation System
"""

import sys
import subprocess
import importlib

def check_package(package_name, import_name=None):
    """Check if a package is installed and can be imported"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✓ {package_name} is installed")
        return True
    except ImportError:
        print(f"✗ {package_name} is NOT installed")
        return False

def suggest_install_command():
    """Suggest pip install command for missing packages"""
    return """
Install required packages with:

pip3 install RPi.GPIO Adafruit_DHT adafruit-circuitpython-ads1x15 flask flask-socketio pandas numpy openpyxl
"""

def main():
    """Check all required packages"""
    print("Checking required packages for Smart Home Automation System...\n")
    
    print("Installing required packages...")
    print("pip3 install RPi.GPIO Adafruit_DHT adafruit-circuitpython-ads1x15 flask flask-socketio pandas numpy openpyxl")

    # Test imports
    test_packages = [
        ("RPi.GPIO", "RPi.GPIO"),
        ("Adafruit_DHT", "Adafruit_DHT"),
        ("adafruit-circuitpython-ads1x15", "adafruit_ads1x15.ads1115"),
        ("flask", "flask"),
        ("flask-socketio", "flask_socketio"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("openpyxl", "openpyxl")
    ]
    
    all_installed = True
    for package, import_name in test_packages:
        if not check_package(package, import_name):
            all_installed = False
    
    print("\nSummary:")
    if all_installed:
        print("All required packages are installed!")
    else:
        print("Some packages are missing.")
        print(suggest_install_command())

if __name__ == "__main__":
    main() 