#!/usr/bin/env python3
"""
Test script for the buzzer sound alerts
"""

import RPi.GPIO as GPIO
import time

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define buzzer pin
BUZZER_PIN = 9

# Setup buzzer
GPIO.setup(BUZZER_PIN, GPIO.OUT)
buzzer = GPIO.PWM(BUZZER_PIN, 440)  # 440Hz (A4 note) initially
buzzer.start(0)  # Start with 0% duty cycle (no sound)

def buzzer_on(frequency=440, duty_cycle=50):
    """Turn on buzzer with specified frequency and duty cycle"""
    buzzer.ChangeFrequency(frequency)
    buzzer.ChangeDutyCycle(duty_cycle)
    print(f"Buzzer ON: {frequency}Hz at {duty_cycle}% volume")

def buzzer_off():
    """Turn off buzzer"""
    buzzer.ChangeDutyCycle(0)
    print("Buzzer OFF")

def buzzer_beep(frequency=440, duty_cycle=50, duration=0.2, pause=0.2, count=1):
    """
    Generate beep pattern with specified parameters
    frequency: tone frequency in Hz
    duty_cycle: volume (0-100)
    duration: length of each beep in seconds
    pause: silence between beeps in seconds
    count: number of beeps
    """
    print(f"Beeping {count} times at {frequency}Hz")
    for i in range(count):
        buzzer_on(frequency, duty_cycle)
        time.sleep(duration)
        buzzer_off()
        if i < count - 1:  # No pause after the last beep
            time.sleep(pause)

def test_tones():
    """Test basic tones"""
    print("\nTesting basic tones...")
    
    print("Testing low tone (220Hz)")
    buzzer_beep(220, 50, 1, 0, 1)
    time.sleep(0.5)
    
    print("Testing middle tone (440Hz)")
    buzzer_beep(440, 50, 1, 0, 1)
    time.sleep(0.5)
    
    print("Testing high tone (880Hz)")
    buzzer_beep(880, 50, 1, 0, 1)
    time.sleep(0.5)

def test_volume():
    """Test different volume levels"""
    print("\nTesting volume levels...")
    
    print("Testing 25% volume")
    buzzer_beep(440, 25, 1, 0, 1)
    time.sleep(0.5)
    
    print("Testing 50% volume")
    buzzer_beep(440, 50, 1, 0, 1)
    time.sleep(0.5)
    
    print("Testing 75% volume")
    buzzer_beep(440, 75, 1, 0, 1)
    time.sleep(0.5)

def test_alert_patterns():
    """Test the alert patterns used in the main system"""
    print("\nTesting alert patterns...")
    
    print("Gas leak alert pattern:")
    for _ in range(2):  # Play pattern for 2 cycles (shortened for test)
        buzzer_beep(880, 70, 0.2, 0.1, 3)  # High pitch, multiple beeps
        time.sleep(0.3)
    time.sleep(1)
    
    print("Door open alert pattern:")
    # Ascending tones
    frequencies = [523, 659, 784]  # C5, E5, G5 (C major chord)
    for freq in frequencies:
        buzzer_beep(freq, 50, 0.15, 0, 1)
        time.sleep(0.05)
    time.sleep(1)
    
    print("Door close alert pattern:")
    # Descending tones
    frequencies = [784, 659, 523]  # G5, E5, C5 (C major chord reversed)
    for freq in frequencies:
        buzzer_beep(freq, 50, 0.15, 0, 1)
        time.sleep(0.05)
    time.sleep(1)
    
    print("Unauthorized access alert pattern:")
    # Two low beeps
    buzzer_beep(330, 70, 0.3, 0.1, 2)  # Low pitch, two beeps
    time.sleep(1)
    
    print("Welcome alert pattern:")
    # Pleasant melody
    melody = [(523, 0.1), (659, 0.1), (784, 0.2)]  # C5, E5, G5
    for freq, dur in melody:
        buzzer_beep(freq, 50, dur, 0, 1)
        time.sleep(0.05)
    time.sleep(1)

def main():
    try:
        print("Buzzer Test Script")
        print("-----------------")
        print("BUZZER_PIN:", BUZZER_PIN)
        print("Make sure the buzzer is connected correctly.")
        time.sleep(1)
        
        test_tones()
        test_volume()
        test_alert_patterns()
        
        print("\nAll tests completed!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        buzzer.stop()
        GPIO.cleanup()
        print("GPIO cleanup completed")

if __name__ == "__main__":
    main() 