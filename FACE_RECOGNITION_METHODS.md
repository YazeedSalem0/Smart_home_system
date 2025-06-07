 # Face Recognition Door System Methods Documentation

## Overview
This document provides comprehensive documentation for all methods used in `face_recognition_door.py`. The face recognition door access control system provides secure door access using facial recognition technology, integrated with the smart home automation system.

## Table of Contents
1. [Class Initialization](#class-initialization)
2. [Configuration Management](#configuration-management)
3. [GPIO and Hardware Control](#gpio-and-hardware-control)
4. [Camera Management](#camera-management)
5. [User Management](#user-management)
6. [Face Recognition Core](#face-recognition-core)
7. [Security and Access Control](#security-and-access-control)
8. [Door Control Integration](#door-control-integration)
9. [Audio Feedback](#audio-feedback)
10. [Logging and Monitoring](#logging-and-monitoring)
11. [System Status and Utilities](#system-status-and-utilities)

---

## Class Initialization

### `__init__(self, config_file='face_config.json')`
**Purpose**: Initializes the face recognition door system with all necessary components.

**Parameters**:
- `config_file` (str): Path to configuration file (default: 'face_config.json')

**Returns**: None

**Initialization Process**:
1. Sets up configuration file path
2. Initializes face recognition data structures
3. Configures GPIO pins for door control
4. Sets recognition parameters and security settings
5. Loads existing configuration
6. Sets up hardware interfaces

**Usage Example**:
```python
face_system = FaceRecognitionDoor('custom_config.json')
```

**Attributes Initialized**:
- `known_faces`: Dictionary of registered users
- `known_names`: List of user names
- `known_encodings`: List of face encodings
- `access_log`: Access attempt history
- `camera`: OpenCV camera object
- `recognition_thread`: Background processing thread
- `confidence_threshold`: Recognition accuracy threshold (0.6)
- `max_attempts`: Maximum failed attempts before lockout (3)
- `lockout_duration`: Lockout time in seconds (300)

---

## Configuration Management

### `load_configuration(self)`
**Purpose**: Loads face recognition configuration and user database from JSON file.

**Parameters**: None

**Returns**: None

**Configuration Structure**:
```json
{
  "known_faces": {
    "username": {
      "encoding": [face_encoding_array],
      "added_date": "2024-01-01T12:00:00",
      "access_count": 5,
      "last_access": "2024-01-01T18:30:00",
      "active": true
    }
  },
  "confidence_threshold": 0.6,
  "max_attempts": 3,
  "lockout_duration": 300
}
```

**Error Handling**: Creates empty configuration if file doesn't exist.

---

### `save_configuration(self)`
**Purpose**: Persists current configuration and user database to JSON file.

**Parameters**: None

**Returns**: None

**Usage Example**:
```python
face_system.add_user("John", "john.jpg")
face_system.save_configuration()  # Persist changes
```

**Features**:
- Atomic file writing
- JSON formatting with indentation
- Error logging on write failures

---

### `load_face_encodings(self)`
**Purpose**: Converts stored face encoding data into numpy arrays for recognition processing.

**Parameters**: None

**Returns**: None

**Process**:
1. Clears existing encoding arrays
2. Iterates through known faces
3. Converts JSON arrays to numpy arrays
4. Builds parallel arrays for names and encodings

**Called By**: `load_configuration()` and `add_user()`

---

## GPIO and Hardware Control

### `setup_gpio(self)`
**Purpose**: Initializes GPIO pins for door servo and buzzer control.

**Parameters**: None

**Returns**: None

**GPIO Configuration**:
- **Servo Pin 10**: Door lock control (50Hz PWM)
- **Buzzer Pin 9**: Audio alerts (440Hz default)

**Setup Process**:
1. Sets GPIO mode to BCM
2. Disables GPIO warnings
3. Configures servo PWM (50Hz for standard servos)
4. Configures buzzer PWM (440Hz default frequency)
5. Initializes both PWM channels at 0% duty cycle

**Error Handling**: Logs GPIO setup failures without crashing system.

---

## Camera Management

### `initialize_camera(self, camera_index=0)`
**Purpose**: Initializes and configures camera for face recognition.

**Parameters**:
- `camera_index` (int): Camera device index (default: 0 for primary camera)

**Returns**: bool - True if successful, False otherwise

**Camera Configuration**:
- **Resolution**: 640x480 pixels
- **Frame Rate**: 30 FPS
- **Format**: Default OpenCV format

**Usage Example**:
```python
if face_system.initialize_camera(0):
    print("Camera ready for face recognition")
else:
    print("Camera initialization failed")
```

**Error Conditions**:
- Camera device not found
- Camera already in use by another application
- Insufficient permissions
- Hardware malfunction

---

## User Management

### `add_user(self, name, image_path=None, capture_from_camera=False)`
**Purpose**: Adds a new user to the face recognition database.

**Parameters**:
- `name` (str): Unique username for the new user
- `image_path` (str, optional): Path to image file containing user's face
- `capture_from_camera` (bool): Whether to capture face from live camera

**Returns**: bool - True if user added successfully, False otherwise

**Usage Examples**:
```python
# Add user from image file
success = face_system.add_user("Alice", image_path="alice.jpg")

# Add user by capturing from camera
success = face_system.add_user("Bob", capture_from_camera=True)
```

**Process**:
1. **Image Source Validation**: Checks for valid image source
2. **Face Detection**: Locates faces in the image
3. **Encoding Generation**: Creates face encoding vector
4. **Database Storage**: Stores user data with metadata
5. **Configuration Update**: Saves changes to file

**User Data Structure**:
```python
{
    'encoding': [128-dimensional face encoding],
    'added_date': '2024-01-01T12:00:00',
    'access_count': 0,
    'last_access': None,
    'active': True
}
```

**Error Conditions**:
- No face found in image
- Multiple faces detected
- Invalid image file
- Camera not available
- Duplicate username

---

### `capture_face_from_camera(self, timeout=10)`
**Purpose**: Captures a single face from camera for user enrollment.

**Parameters**:
- `timeout` (int): Maximum time to wait for face capture in seconds

**Returns**: numpy.ndarray - Face encoding array, or None if failed

**Process**:
1. **Frame Capture Loop**: Continuously reads camera frames
2. **Face Detection**: Uses face_recognition library to find faces
3. **Single Face Validation**: Ensures exactly one face is present
4. **Encoding Generation**: Creates face encoding from detected face
5. **Quality Check**: Validates encoding quality

**Usage Example**:
```python
encoding = face_system.capture_face_from_camera(15)  # 15-second timeout
if encoding is not None:
    print("Face captured successfully")
```

**Best Practices**:
- Ensure good lighting conditions
- Position face clearly in camera view
- Avoid multiple people in frame
- Maintain steady position during capture

---

### `remove_user(self, name)`
**Purpose**: Removes a user from the face recognition database.

**Parameters**:
- `name` (str): Username to remove

**Returns**: bool - True if user removed, False if not found

**Usage Example**:
```python
if face_system.remove_user("Alice"):
    print("User Alice removed successfully")
else:
    print("User Alice not found")
```

**Process**:
1. **User Existence Check**: Verifies user exists in database
2. **Database Removal**: Deletes user data
3. **Encoding Update**: Rebuilds face encoding arrays
4. **Configuration Save**: Persists changes to file

---

### `update_user_status(self, name, active=True)`
**Purpose**: Updates the active status of a user without removing their data.

**Parameters**:
- `name` (str): Username to update
- `active` (bool): New active status

**Returns**: bool - True if updated successfully, False if user not found

**Usage Example**:
```python
# Temporarily disable user access
face_system.update_user_status("Bob", False)

# Re-enable user access
face_system.update_user_status("Bob", True)
```

**Use Cases**:
- Temporary access suspension
- User management without data loss
- Security incident response
- Maintenance periods

---

## Face Recognition Core

### `recognize_face(self, frame)`
**Purpose**: Performs face recognition on a camera frame.

**Parameters**:
- `frame` (numpy.ndarray): OpenCV image frame in BGR format

**Returns**: list - List of recognized face information dictionaries

**Recognition Process**:
1. **Color Conversion**: BGR to RGB format conversion
2. **Face Location**: Detects face positions in frame
3. **Encoding Generation**: Creates encodings for detected faces
4. **Comparison**: Compares against known face database
5. **Confidence Calculation**: Calculates recognition confidence
6. **Status Validation**: Checks user active status

**Return Format**:
```python
[
    {
        'name': 'Alice',
        'confidence': 0.85,
        'location': (top, right, bottom, left)
    },
    {
        'name': 'Unknown',
        'confidence': 0.0,
        'location': (top, right, bottom, left)
    }
]
```

**Recognition States**:
- **Known User**: Confidence above threshold, user active
- **Inactive User**: Known user but marked inactive
- **Unknown**: No match or confidence below threshold

---

## Security and Access Control

### `check_lockout(self, identifier="default")`
**Purpose**: Checks if the system is in security lockout due to failed attempts.

**Parameters**:
- `identifier` (str): Lockout identifier for tracking different sources

**Returns**: tuple (is_locked: bool, remaining_time: float)

**Usage Example**:
```python
is_locked, remaining = face_system.check_lockout()
if is_locked:
    print(f"System locked for {remaining:.1f} more seconds")
```

**Lockout Logic**:
- Triggers after `max_attempts` failed attempts
- Lockout duration: `lockout_duration` seconds
- Automatic reset after lockout period
- Separate tracking for different identifiers

---

### `record_failed_attempt(self, identifier="default")`
**Purpose**: Records a failed access attempt for security tracking.

**Parameters**:
- `identifier` (str): Identifier for attempt tracking

**Returns**: None

**Tracking Data**:
- Attempt count per identifier
- Timestamp of last attempt
- Automatic lockout triggering

**Usage Example**:
```python
if not access_granted:
    face_system.record_failed_attempt()
```

---

### `reset_failed_attempts(self, identifier="default")`
**Purpose**: Resets failed attempt counter after successful access.

**Parameters**:
- `identifier` (str): Identifier to reset

**Returns**: None

**Usage Example**:
```python
if access_granted:
    face_system.reset_failed_attempts()
```

---

## Door Control Integration

### `unlock_door(self, duration=5)`
**Purpose**: Unlocks the door for a specified duration with full integration.

**Parameters**:
- `duration` (int): Time to keep door unlocked in seconds

**Returns**: None

**Process**:
1. **Smart Home Integration**: Sends unlock command to main system
2. **Servo Control**: Moves servo to unlock position (7.5% duty cycle)
3. **Audio Feedback**: Plays success sound pattern
4. **Timed Access**: Waits for specified duration
5. **Auto-Lock**: Automatically locks door after timeout

**Usage Example**:
```python
# Unlock for 10 seconds
threading.Thread(target=face_system.unlock_door, args=(10,)).start()
```

**Safety Features**:
- Non-blocking operation (runs in separate thread)
- Automatic re-locking
- Error handling and logging
- Integration with smart home system

---

### `lock_door(self)`
**Purpose**: Locks the door and updates system state.

**Parameters**: None

**Returns**: None

**Process**:
1. **Smart Home Integration**: Sends lock command to main system
2. **Servo Control**: Moves servo to lock position (2.5% duty cycle)
3. **State Update**: Updates door lock status

**Servo Positions**:
- **Lock Position**: 2.5% duty cycle (0 degrees)
- **Unlock Position**: 7.5% duty cycle (90 degrees)

---

### `send_door_command(self, lock_state)`
**Purpose**: Sends door control commands to the main smart home system.

**Parameters**:
- `lock_state` (bool): True for lock, False for unlock

**Returns**: bool - True if command sent successfully

**Integration**:
- **API Endpoint**: `http://localhost:5000/api/control/door`
- **Request Format**: `{"lock": true/false}`
- **Timeout**: 5 seconds
- **Error Handling**: Logs communication failures

**Usage Example**:
```python
success = face_system.send_door_command(False)  # Unlock
if success:
    print("Door command sent to smart home system")
```

---

## Audio Feedback

### `play_success_sound(self)`
**Purpose**: Plays a pleasant sound pattern for successful access.

**Parameters**: None

**Returns**: None

**Sound Pattern**:
1. **First Tone**: 880Hz (A5 note) for 0.2 seconds
2. **Brief Pause**: 0.1 seconds
3. **Second Tone**: 1108Hz (C#6 note) for 0.2 seconds

**Usage**: Called automatically during successful door unlock.

---

### `play_failure_sound(self)`
**Purpose**: Plays an alert sound pattern for failed access attempts.

**Parameters**: None

**Returns**: None

**Sound Pattern**:
- **Frequency**: 220Hz (A3 note - low tone)
- **Pattern**: 3 beeps of 0.3 seconds each
- **Pause**: 0.1 seconds between beeps

**Usage**: Called automatically when access is denied.

---

## Logging and Monitoring

### `log_access_attempt(self, name, success, confidence=0.0)`
**Purpose**: Logs all access attempts for security monitoring and audit trails.

**Parameters**:
- `name` (str): Name of person attempting access
- `success` (bool): Whether access was granted
- `confidence` (float): Recognition confidence level

**Returns**: None

**Log Entry Structure**:
```python
{
    'timestamp': '2024-01-01T12:30:45',
    'name': 'Alice',
    'success': True,
    'confidence': 0.85,
    'ip_address': '127.0.0.1'
}
```

**Features**:
- **Automatic Cleanup**: Maintains last 1000 entries
- **User Statistics**: Updates access count and last access time
- **Audit Trail**: Complete access history
- **Security Monitoring**: Failed attempt tracking

---

### `get_client_ip(self)`
**Purpose**: Retrieves client IP address for access logging.

**Parameters**: None

**Returns**: str - IP address

**Note**: Currently returns localhost; can be extended for network access.

---

## System Status and Utilities

### `get_system_status(self)`
**Purpose**: Returns comprehensive system status information.

**Parameters**: None

**Returns**: dict - Complete system status

**Status Information**:
```python
{
    'is_running': True,
    'known_users': 5,
    'active_users': 4,
    'total_access_attempts': 127,
    'failed_attempts': {'default': (2, 1640995200)},
    'camera_connected': True,
    'confidence_threshold': 0.6
}
```

**Usage Example**:
```python
status = face_system.get_system_status()
print(f"System running: {status['is_running']}")
print(f"Active users: {status['active_users']}")
```

---

### `get_access_log(self, limit=100)`
**Purpose**: Retrieves recent access log entries.

**Parameters**:
- `limit` (int): Maximum number of entries to return

**Returns**: list - Recent access log entries

**Usage Example**:
```python
recent_logs = face_system.get_access_log(20)
for entry in recent_logs:
    status = "SUCCESS" if entry['success'] else "FAILED"
    print(f"{entry['timestamp']}: {entry['name']} - {status}")
```

---

### `get_user_list(self)`
**Purpose**: Returns list of all registered users with their information.

**Parameters**: None

**Returns**: list - User information dictionaries

**User Information**:
```python
[
    {
        'name': 'Alice',
        'added_date': '2024-01-01T12:00:00',
        'access_count': 15,
        'last_access': '2024-01-01T18:30:00',
        'active': True
    }
]
```

**Usage Example**:
```python
users = face_system.get_user_list()
for user in users:
    status = "Active" if user['active'] else "Inactive"
    print(f"{user['name']} ({status}) - {user['access_count']} accesses")
```

---

## Recognition Processing

### `process_frame(self, frame)`
**Purpose**: Processes a single camera frame for complete face recognition workflow.

**Parameters**:
- `frame` (numpy.ndarray): Camera frame to process

**Returns**: tuple (processed_frame, access_granted, status_message)

**Processing Workflow**:
1. **Security Check**: Verify system not in lockout
2. **Face Recognition**: Detect and recognize faces
3. **Access Decision**: Determine if access should be granted
4. **Visual Feedback**: Draw rectangles and labels on frame
5. **Action Execution**: Trigger door unlock if authorized
6. **Logging**: Record access attempt

**Visual Annotations**:
- **Green Rectangle**: Recognized authorized user
- **Red Rectangle**: Unknown or unauthorized person
- **Label Format**: "Name (confidence)"

**Usage Example**:
```python
ret, frame = camera.read()
processed_frame, granted, message = face_system.process_frame(frame)
cv2.imshow('Face Recognition', processed_frame)
```

---

## System Control

### `start_recognition(self)`
**Purpose**: Starts the face recognition system with background processing.

**Parameters**: None

**Returns**: bool - True if started successfully

**Startup Process**:
1. **Camera Initialization**: Initialize and configure camera
2. **Thread Creation**: Create background recognition thread
3. **System State**: Set running flag to True
4. **Thread Start**: Begin background processing

**Usage Example**:
```python
if face_system.start_recognition():
    print("Face recognition system started")
    # System now running in background
else:
    print("Failed to start system")
```

---

### `stop_recognition(self)`
**Purpose**: Stops the face recognition system and cleans up resources.

**Parameters**: None

**Returns**: None

**Shutdown Process**:
1. **Stop Flag**: Set running flag to False
2. **Thread Join**: Wait for background thread to finish
3. **Camera Release**: Release camera resources
4. **Cleanup**: Clean up system resources

**Usage Example**:
```python
face_system.stop_recognition()
print("Face recognition system stopped")
```

---

### `_recognition_loop(self)`
**Purpose**: Main recognition loop that runs in background thread.

**Parameters**: None

**Returns**: None (runs until stopped)

**Loop Process**:
1. **Frame Capture**: Read frame from camera
2. **Processing Control**: Process frames at reduced rate (every 0.3s)
3. **Recognition**: Perform face recognition on frame
4. **Action Handling**: Execute access control actions
5. **CPU Management**: Small delays to prevent excessive CPU usage

**Performance Optimization**:
- **Frame Skipping**: Processes every 3rd frame to reduce CPU load
- **Sleep Intervals**: 0.1-second delays between iterations
- **Error Recovery**: Continues operation despite individual frame errors

---

### `cleanup(self)`
**Purpose**: Performs complete system cleanup and resource deallocation.

**Parameters**: None

**Returns**: None

**Cleanup Process**:
1. **Recognition Stop**: Stop background recognition processing
2. **PWM Cleanup**: Stop servo and buzzer PWM signals
3. **GPIO Cleanup**: Release all GPIO resources
4. **Resource Deallocation**: Clean up system resources

**Usage Example**:
```python
try:
    # System operation
    face_system.start_recognition()
    # ... system running ...
except KeyboardInterrupt:
    print("Shutting down...")
finally:
    face_system.cleanup()
```

**Important**: Always call cleanup() before program termination to prevent GPIO conflicts.

---

## Integration Features

### Smart Home System Integration
- **API Communication**: RESTful API calls to main system
- **State Synchronization**: Door lock state coordination
- **Event Logging**: Integrated access logging
- **Error Handling**: Graceful degradation if main system unavailable

### Security Features
- **Confidence Thresholding**: Adjustable recognition accuracy
- **Attempt Limiting**: Configurable failed attempt limits
- **Lockout Protection**: Time-based access restrictions
- **Audit Logging**: Complete access attempt history
- **User Status Control**: Active/inactive user management

### Performance Optimizations
- **Frame Rate Control**: Optimized processing frequency
- **Memory Management**: Efficient face encoding storage
- **CPU Usage**: Balanced accuracy vs. performance
- **Thread Safety**: Safe concurrent operations

### Hardware Integration
- **GPIO Control**: Direct hardware interface
- **PWM Management**: Precise servo and buzzer control
- **Camera Management**: Robust camera handling
- **Error Recovery**: Hardware failure resilience

This comprehensive documentation covers all methods in the face recognition door system, providing detailed information for implementation, maintenance, and troubleshooting.