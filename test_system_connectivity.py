#!/usr/bin/env python3
"""
Smart Home System Connectivity Test
Tests the connection between web server and main smart home system
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
SMART_HOME_API_BASE = "http://localhost:5000/api"
WEB_SERVER_BASE = "http://localhost:8080"

def test_main_system_api():
    """Test if the main smart home system API is responding"""
    print("=== Testing Main Smart Home System API ===")
    
    endpoints_to_test = [
        ("/state", "GET", None),
        ("/rules", "GET", None),
        ("/control/fan", "POST", {"action": "status"}),
        ("/control/light", "POST", {"room": "Room1", "action": "status"}),
        ("/control/door", "POST", {"action": "status"}),
        ("/control/garage", "POST", {"action": "status"})
    ]
    
    results = {}
    
    for endpoint, method, data in endpoints_to_test:
        url = f"{SMART_HOME_API_BASE}{endpoint}"
        print(f"\nTesting {method} {url}")
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=5)
            
            if response.status_code == 200:
                print(f"✓ SUCCESS - Status: {response.status_code}")
                try:
                    json_data = response.json()
                    print(f"  Response keys: {list(json_data.keys()) if isinstance(json_data, dict) else 'Non-dict response'}")
                except:
                    print(f"  Response: {response.text[:100]}...")
                results[endpoint] = True
            else:
                print(f"✗ FAILED - Status: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                results[endpoint] = False
                
        except requests.exceptions.ConnectionError:
            print(f"✗ CONNECTION ERROR - Cannot connect to {url}")
            print("  Make sure the main smart home system is running on port 5000")
            results[endpoint] = False
        except requests.exceptions.Timeout:
            print(f"✗ TIMEOUT - Request to {url} timed out")
            results[endpoint] = False
        except Exception as e:
            print(f"✗ ERROR - {e}")
            results[endpoint] = False
    
    return results

def test_web_server_api():
    """Test if the web server API is responding"""
    print("\n=== Testing Web Server API ===")
    
    endpoints_to_test = [
        ("/api/dashboard/data", "GET", None),
        ("/api/automation/rules", "GET", None),
        ("/api/control/fan", "POST", {"action": "status"}),
        ("/api/control/light", "POST", {"room": "Room1", "action": "status"}),
    ]
    
    results = {}
    
    for endpoint, method, data in endpoints_to_test:
        url = f"{WEB_SERVER_BASE}{endpoint}"
        print(f"\nTesting {method} {url}")
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=5)
            
            if response.status_code == 200:
                print(f"✓ SUCCESS - Status: {response.status_code}")
                try:
                    json_data = response.json()
                    print(f"  Response keys: {list(json_data.keys()) if isinstance(json_data, dict) else 'Non-dict response'}")
                    if 'success' in json_data:
                        print(f"  Success: {json_data['success']}")
                    if 'connection_status' in json_data:
                        print(f"  Connection Status: {json_data['connection_status']}")
                except:
                    print(f"  Response: {response.text[:100]}...")
                results[endpoint] = True
            else:
                print(f"✗ FAILED - Status: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                results[endpoint] = False
                
        except requests.exceptions.ConnectionError:
            print(f"✗ CONNECTION ERROR - Cannot connect to {url}")
            print("  Make sure the web server is running on port 8080")
            results[endpoint] = False
        except requests.exceptions.Timeout:
            print(f"✗ TIMEOUT - Request to {url} timed out")
            results[endpoint] = False
        except Exception as e:
            print(f"✗ ERROR - {e}")
            results[endpoint] = False
    
    return results

def test_system_integration():
    """Test the integration between web server and main system"""
    print("\n=== Testing System Integration ===")
    
    # Test if web server can get data from main system
    print("\n1. Testing data flow from main system to web server...")
    
    try:
        # Get state from main system directly
        main_response = requests.get(f"{SMART_HOME_API_BASE}/state", timeout=5)
        if main_response.status_code != 200:
            print("✗ Cannot get state from main system")
            return False
        
        main_data = main_response.json()
        print(f"✓ Main system state retrieved: {list(main_data.keys())}")
        
        # Get dashboard data from web server (which should fetch from main system)
        web_response = requests.get(f"{WEB_SERVER_BASE}/api/dashboard/data", timeout=5)
        if web_response.status_code != 200:
            print("✗ Cannot get dashboard data from web server")
            return False
        
        web_data = web_response.json()
        print(f"✓ Web server dashboard data retrieved")
        
        if web_data.get('success') and web_data.get('connection_status'):
            print("✓ Web server successfully connected to main system")
            return True
        else:
            print("✗ Web server reports connection issues with main system")
            print(f"  Success: {web_data.get('success')}")
            print(f"  Connection Status: {web_data.get('connection_status')}")
            return False
            
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

def test_control_commands():
    """Test control commands through web server"""
    print("\n=== Testing Control Commands ===")
    
    commands_to_test = [
        ("fan", {"action": "status"}),
        ("light", {"room": "Room1", "action": "status"}),
        ("door", {"action": "status"}),
        ("garage", {"action": "status"})
    ]
    
    results = {}
    
    for control_type, command_data in commands_to_test:
        print(f"\nTesting {control_type} control...")
        
        try:
            # Send command through web server
            url = f"{WEB_SERVER_BASE}/api/control/{control_type}"
            response = requests.post(url, json=command_data, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✓ {control_type} control successful")
                    results[control_type] = True
                else:
                    print(f"✗ {control_type} control failed - API returned success=False")
                    results[control_type] = False
            else:
                print(f"✗ {control_type} control failed - Status: {response.status_code}")
                results[control_type] = False
                
        except Exception as e:
            print(f"✗ {control_type} control error: {e}")
            results[control_type] = False
    
    return results

def check_ports():
    """Check if required ports are available"""
    print("\n=== Checking Port Availability ===")
    
    ports_to_check = [
        (5000, "Main Smart Home System"),
        (8080, "Web Server")
    ]
    
    for port, service in ports_to_check:
        try:
            response = requests.get(f"http://localhost:{port}", timeout=2)
            print(f"✓ Port {port} ({service}) is responding")
        except requests.exceptions.ConnectionError:
            print(f"✗ Port {port} ({service}) is not responding")
        except Exception as e:
            print(f"? Port {port} ({service}) - {e}")

def main():
    """Main test function"""
    print("Smart Home System Connectivity Test")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check ports first
    check_ports()
    
    # Test main system API
    main_results = test_main_system_api()
    
    # Test web server API
    web_results = test_web_server_api()
    
    # Test integration
    integration_success = test_system_integration()
    
    # Test control commands
    control_results = test_control_commands()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    print(f"\nMain System API Tests:")
    for endpoint, success in main_results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {endpoint}: {status}")
    
    print(f"\nWeb Server API Tests:")
    for endpoint, success in web_results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {endpoint}: {status}")
    
    print(f"\nIntegration Test: {'✓ PASS' if integration_success else '✗ FAIL'}")
    
    print(f"\nControl Command Tests:")
    for control_type, success in control_results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {control_type}: {status}")
    
    # Overall result
    all_main_passed = all(main_results.values())
    all_web_passed = all(web_results.values())
    all_control_passed = all(control_results.values())
    
    overall_success = all_main_passed and all_web_passed and integration_success and all_control_passed
    
    print(f"\nOVERALL RESULT: {'✓ ALL TESTS PASSED' if overall_success else '✗ SOME TESTS FAILED'}")
    
    if not overall_success:
        print("\nTROUBLESHOOTING TIPS:")
        if not all_main_passed:
            print("- Make sure the main smart home system is running: python smart_home_system.py")
        if not all_web_passed:
            print("- Make sure the web server is running: python web_server.py")
        if not integration_success:
            print("- Check network connectivity between services")
            print("- Verify API endpoints match between systems")
    
    return overall_success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1) 