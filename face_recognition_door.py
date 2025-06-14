#!/usr/bin/env python3
"""
Face Recognition Door Access Control System
Integrates with Smart Home System for secure door access
"""

import cv2
import face_recognition
import numpy as np
import json
import os
import time
import threading
import logging
from datetime import datetime, timedelta
import RPi.GPIO as GPIO
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceRecognitionDoor:
    def __init__(self, config_file='face_config.json'):
        """Initialize the face recognition door system"""
        self.config_file = config_file
        self.known_faces = {}
        self.known_names = []
        self.known_encodings = []
        self.access_log = []
        self.camera = None
        self.is_running = False
        self.recognition_thread = None
        
        # GPIO pins (using existing smart home system pins)
        self.SERVO_PIN = 10  # Door lock servo
        self.BUZZER_PIN = 9  # Alert buzzer
        
        # Recognition settings
        self.confidence_threshold = 0.6
        self.max_attempts = 3
        self.lockout_duration = 300  # 5 minutes in seconds
        self.failed_attempts = {}
        
        # Smart home system integration
        self.smart_home_api = "http://localhost:5000/api"
        
        self.load_configuration()
        self.setup_gpio()

    def setup_gpio(self):
        """Setup GPIO pins for door control"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Setup servo for door lock
            GPIO.setup(self.SERVO_PIN, GPIO.OUT)
            self.door_servo = GPIO.PWM(self.SERVO_PIN, 50)
            self.door_servo.start(0)
            
            # Setup buzzer
            GPIO.setup(self.BUZZER_PIN, GPIO.OUT)
            self.buzzer = GPIO.PWM(self.BUZZER_PIN, 440)
            self.buzzer.start(0)
            
            logger.info("GPIO setup completed")
        except Exception as e:
            logger.error(f"GPIO setup failed: {e}")

    def load_configuration(self):
        """Load face recognition configuration and known faces"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.known_faces = config.get('known_faces', {})
                    self.confidence_threshold = config.get('confidence_threshold', 0.6)
                    self.max_attempts = config.get('max_attempts', 3)
                    self.lockout_duration = config.get('lockout_duration', 300)
                    
                # Load face encodings
                self.load_face_encodings()
                logger.info(f"Loaded {len(self.known_faces)} known faces")
            else:
                logger.info("No configuration file found, starting with empty database")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")

    def save_configuration(self):
        """Save current configuration to file"""
        try:
            config = {
                'known_faces': self.known_faces,
                'confidence_threshold': self.confidence_threshold,
                'max_attempts': self.max_attempts,
                'lockout_duration': self.lockout_duration
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info("Configuration saved")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")

    def load_face_encodings(self):
        """Load face encodings from stored face data"""
        self.known_names = []
        self.known_encodings = []
        
        for name, face_data in self.known_faces.items():
            if 'encoding' in face_data:
                encoding = np.array(face_data['encoding'])
                self.known_encodings.append(encoding)
                self.known_names.append(name)

    def initialize_camera(self, camera_index=0):
        """Initialize camera for face recognition"""
        try:
            self.camera = cv2.VideoCapture(camera_index)
            if not self.camera.isOpened():
                raise Exception("Could not open camera")
            
            # Set camera properties for better performance
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            logger.info("Camera initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Camera initialization failed: {e}")
            return False

    def add_user(self, name, image_path=None, capture_from_camera=False):
        """Add a new user to the face recognition database"""
        try:
            if capture_from_camera:
                if not self.camera or not self.camera.isOpened():
                    if not self.initialize_camera():
                        return False
                
                logger.info(f"Capturing face for user: {name}")
                face_encoding = self.capture_face_from_camera()
                if face_encoding is None:
                    return False
            elif image_path and os.path.exists(image_path):
                image = face_recognition.load_image_file(image_path)
                face_encodings = face_recognition.face_encodings(image)
                
                if len(face_encodings) == 0:
                    logger.error("No face found in the image")
                    return False
                
                face_encoding = face_encodings[0]
            else:
                logger.error("No valid image source provided")
                return False
            
            # Store user data
            self.known_faces[name] = {
                'encoding': face_encoding.tolist(),
                'added_date': datetime.now().isoformat(),
                'access_count': 0,
                'last_access': None,
                'active': True
            }
            
            self.load_face_encodings()
            self.save_configuration()
            logger.info(f"User {name} added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error adding user {name}: {e}")
            return False

    def capture_face_from_camera(self, timeout=10):
        """Capture a face from camera for enrollment"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            ret, frame = self.camera.read()
            if not ret:
                continue
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Find faces in the frame
            face_locations = face_recognition.face_locations(rgb_frame)
            
            if len(face_locations) == 1:  # Exactly one face
                face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
                logger.info("Face captured successfully")
                return face_encoding
            elif len(face_locations) > 1:
                logger.warning("Multiple faces detected, please ensure only one person is in frame")
            
            time.sleep(0.1)
        
        logger.error("Face capture timeout")
        return None

    def remove_user(self, name):
        """Remove a user from the face recognition database"""
        try:
            if name in self.known_faces:
                del self.known_faces[name]
                self.load_face_encodings()
                self.save_configuration()
                logger.info(f"User {name} removed successfully")
                return True
            else:
                logger.warning(f"User {name} not found")
                return False
        except Exception as e:
            logger.error(f"Error removing user {name}: {e}")
            return False

    def update_user_status(self, name, active=True):
        """Update user active status"""
        try:
            if name in self.known_faces:
                self.known_faces[name]['active'] = active
                self.save_configuration()
                logger.info(f"User {name} status updated to {'active' if active else 'inactive'}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating user status: {e}")
            return False

    def recognize_face(self, frame):
        """Recognize faces in the given frame"""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Find face locations and encodings
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            recognized_faces = []
            
            for face_encoding in face_encodings:
                # Compare with known faces
                matches = face_recognition.compare_faces(self.known_encodings, face_encoding)
                face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
                
                name = "Unknown"
                confidence = 0.0
                
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        distance = face_distances[best_match_index]
                        confidence = 1 - distance
                        
                        if confidence >= self.confidence_threshold:
                            name = self.known_names[best_match_index]
                            
                            # Check if user is active
                            if name in self.known_faces and not self.known_faces[name]['active']:
                                name = "Inactive User"
                                confidence = 0.0
                
                recognized_faces.append({
                    'name': name,
                    'confidence': confidence,
                    'location': face_locations[len(recognized_faces)] if len(recognized_faces) < len(face_locations) else None
                })
            
            return recognized_faces
            
        except Exception as e:
            logger.error(f"Error in face recognition: {e}")
            return []

    def check_lockout(self, identifier="default"):
        """Check if system is in lockout due to failed attempts"""
        if identifier in self.failed_attempts:
            attempts, last_attempt = self.failed_attempts[identifier]
            if attempts >= self.max_attempts:
                time_since_last = time.time() - last_attempt
                if time_since_last < self.lockout_duration:
                    return True, self.lockout_duration - time_since_last
                else:
                    # Reset failed attempts after lockout period
                    del self.failed_attempts[identifier]
        return False, 0

    def record_failed_attempt(self, identifier="default"):
        """Record a failed access attempt"""
        current_time = time.time()
        if identifier in self.failed_attempts:
            attempts, _ = self.failed_attempts[identifier]
            self.failed_attempts[identifier] = (attempts + 1, current_time)
        else:
            self.failed_attempts[identifier] = (1, current_time)

    def reset_failed_attempts(self, identifier="default"):
        """Reset failed attempts for successful access"""
        if identifier in self.failed_attempts:
            del self.failed_attempts[identifier]

    def unlock_door(self, duration=5):
        """Unlock the door for specified duration"""
        try:
            logger.info(f"Unlocking door for {duration} seconds")
            
            # Send unlock command to smart home system
            self.send_door_command(False)  # False = unlock
            
            # Control servo directly
            self.door_servo.ChangeDutyCycle(7.5)  # Unlock position
            time.sleep(0.5)
            self.door_servo.ChangeDutyCycle(0)
            
            # Play success sound
            self.play_success_sound()
            
            # Wait for specified duration
            time.sleep(duration)
            
            # Lock the door again
            self.lock_door()
            
        except Exception as e:
            logger.error(f"Error unlocking door: {e}")

    def lock_door(self):
        """Lock the door"""
        try:
            logger.info("Locking door")
            
            # Send lock command to smart home system
            self.send_door_command(True)  # True = lock
            
            # Control servo directly
            self.door_servo.ChangeDutyCycle(2.5)  # Lock position
            time.sleep(0.5)
            self.door_servo.ChangeDutyCycle(0)
            
        except Exception as e:
            logger.error(f"Error locking door: {e}")

    def send_door_command(self, lock_state):
        """Send door control command to smart home system"""
        try:
            data = {'lock': lock_state}
            response = requests.post(f"{self.smart_home_api}/control/door", 
                                   json=data, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error sending door command: {e}")
            return False

    def play_success_sound(self):
        """Play success sound"""
        try:
            self.buzzer.ChangeFrequency(880)  # A5 note
            self.buzzer.ChangeDutyCycle(50)
            time.sleep(0.2)
            self.buzzer.ChangeDutyCycle(0)
            time.sleep(0.1)
            self.buzzer.ChangeFrequency(1108)  # C#6 note
            self.buzzer.ChangeDutyCycle(50)
            time.sleep(0.2)
            self.buzzer.ChangeDutyCycle(0)
        except Exception as e:
            logger.error(f"Error playing success sound: {e}")

    def play_failure_sound(self):
        """Play failure sound"""
        try:
            for _ in range(3):
                self.buzzer.ChangeFrequency(220)  # A3 note (low)
                self.buzzer.ChangeDutyCycle(50)
                time.sleep(0.3)
                self.buzzer.ChangeDutyCycle(0)
                time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error playing failure sound: {e}")

    def log_access_attempt(self, name, success, confidence=0.0):
        """Log access attempt"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'name': name,
                'success': success,
                'confidence': confidence,
                'ip_address': self.get_client_ip()
            }
            
            self.access_log.append(log_entry)
            
            # Update user access count and last access time
            if success and name in self.known_faces:
                self.known_faces[name]['access_count'] += 1
                self.known_faces[name]['last_access'] = datetime.now().isoformat()
                self.save_configuration()
            
            # Keep only last 1000 log entries
            if len(self.access_log) > 1000:
                self.access_log = self.access_log[-1000:]
            
            logger.info(f"Access attempt logged: {name} - {'Success' if success else 'Failed'}")
            
        except Exception as e:
            logger.error(f"Error logging access attempt: {e}")

    def get_client_ip(self):
        """Get client IP address (placeholder for web integration)"""
        return "127.0.0.1"

    def process_frame(self, frame):
        """Process a single frame for face recognition"""
        try:
            # Check for lockout
            is_locked, remaining_time = self.check_lockout()
            if is_locked:
                logger.warning(f"System locked out for {remaining_time:.1f} more seconds")
                return frame, False, f"System locked for {remaining_time:.1f}s"
            
            # Recognize faces
            recognized_faces = self.recognize_face(frame)
            
            access_granted = False
            status_message = "No face detected"
            
            if recognized_faces:
                for face_info in recognized_faces:
                    name = face_info['name']
                    confidence = face_info['confidence']
                    location = face_info['location']
                    
                    # Draw rectangle around face
                    if location:
                        top, right, bottom, left = location
                        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                        
                        # Draw label
                        label = f"{name} ({confidence:.2f})"
                        cv2.putText(frame, label, (left, top - 10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    
                    if name != "Unknown" and name != "Inactive User":
                        access_granted = True
                        status_message = f"Access granted to {name}"
                        self.log_access_attempt(name, True, confidence)
                        self.reset_failed_attempts()
                        
                        # Unlock door in separate thread
                        threading.Thread(target=self.unlock_door, args=(5,)).start()
                        break
                    else:
                        status_message = f"Access denied: {name}"
                        self.log_access_attempt(name, False, confidence)
                        self.record_failed_attempt()
                        self.play_failure_sound()
            
            return frame, access_granted, status_message
            
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return frame, False, "Processing error"

    def start_recognition(self):
        """Start the face recognition system"""
        try:
            if not self.initialize_camera():
                logger.error("Failed to initialize camera")
                return False
            
            self.is_running = True
            self.recognition_thread = threading.Thread(target=self._recognition_loop)
            self.recognition_thread.daemon = True
            self.recognition_thread.start()
            
            logger.info("Face recognition system started")
            return True
            
        except Exception as e:
            logger.error(f"Error starting recognition system: {e}")
            return False

    def stop_recognition(self):
        """Stop the face recognition system"""
        try:
            self.is_running = False
            
            if self.recognition_thread:
                self.recognition_thread.join(timeout=5)
            
            if self.camera:
                self.camera.release()
            
            logger.info("Face recognition system stopped")
            
        except Exception as e:
            logger.error(f"Error stopping recognition system: {e}")

    def _recognition_loop(self):
        """Main recognition loop (runs in separate thread)"""
        while self.is_running:
            try:
                ret, frame = self.camera.read()
                if not ret:
                    continue
                
                # Process frame every few frames to reduce CPU load
                if int(time.time() * 10) % 3 == 0:  # Process every 0.3 seconds
                    processed_frame, access_granted, status = self.process_frame(frame)
                    
                    if access_granted:
                        logger.info(f"Access granted: {status}")
                
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                
            except Exception as e:
                logger.error(f"Error in recognition loop: {e}")
                time.sleep(1)

    def get_system_status(self):
        """Get current system status"""
        return {
            'is_running': self.is_running,
            'known_users': len(self.known_faces),
            'active_users': sum(1 for user in self.known_faces.values() if user['active']),
            'total_access_attempts': len(self.access_log),
            'failed_attempts': dict(self.failed_attempts),
            'camera_connected': self.camera is not None and self.camera.isOpened(),
            'confidence_threshold': self.confidence_threshold
        }

    def get_access_log(self, limit=100):
        """Get recent access log entries"""
        return self.access_log[-limit:] if self.access_log else []

    def get_user_list(self):
        """Get list of all users"""
        users = []
        for name, data in self.known_faces.items():
            users.append({
                'name': name,
                'added_date': data.get('added_date'),
                'access_count': data.get('access_count', 0),
                'last_access': data.get('last_access'),
                'active': data.get('active', True)
            })
        return users

    def cleanup(self):
        """Cleanup resources"""
        try:
            self.stop_recognition()
            
            if hasattr(self, 'door_servo'):
                self.door_servo.stop()
            if hasattr(self, 'buzzer'):
                self.buzzer.stop()
            
            GPIO.cleanup()
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Main execution
if __name__ == "__main__":
    face_system = FaceRecognitionDoor()
    
    try:
        print("Face Recognition Door System")
        print("1. Add user")
        print("2. Remove user")
        print("3. Start recognition")
        print("4. View users")
        print("5. View access log")
        print("6. Exit")
        
        while True:
            choice = input("\nEnter choice (1-6): ").strip()
            
            if choice == '1':
                name = input("Enter user name: ").strip()
                method = input("Capture from camera? (y/n): ").strip().lower()
                
                if method == 'y':
                    success = face_system.add_user(name, capture_from_camera=True)
                else:
                    image_path = input("Enter image path: ").strip()
                    success = face_system.add_user(name, image_path=image_path)
                
                print(f"User {'added' if success else 'not added'}")
                
            elif choice == '2':
                name = input("Enter user name to remove: ").strip()
                success = face_system.remove_user(name)
                print(f"User {'removed' if success else 'not found'}")
                
            elif choice == '3':
                print("Starting face recognition system...")
                if face_system.start_recognition():
                    print("System started. Press Ctrl+C to stop.")
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        face_system.stop_recognition()
                        print("\nSystem stopped.")
                
            elif choice == '4':
                users = face_system.get_user_list()
                print(f"\nRegistered Users ({len(users)}):")
                for user in users:
                    status = "Active" if user['active'] else "Inactive"
                    print(f"- {user['name']} ({status}) - Access count: {user['access_count']}")
                
            elif choice == '5':
                log_entries = face_system.get_access_log(20)
                print(f"\nRecent Access Log ({len(log_entries)} entries):")
                for entry in log_entries[-10:]:
                    status = "SUCCESS" if entry['success'] else "FAILED"
                    print(f"{entry['timestamp']}: {entry['name']} - {status}")
                
            elif choice == '6':
                break
                
            else:
                print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        face_system.cleanup()
