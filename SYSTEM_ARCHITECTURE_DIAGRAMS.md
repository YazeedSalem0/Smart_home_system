# Smart Home System Architecture Diagrams

This document contains comprehensive Mermaid.js diagrams illustrating the architecture, data flow, and component relationships of the Smart Home Automation System.

## 1. Overall System Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        WEB[Web Dashboard]
        API[REST API]
        MOBILE[Mobile Interface]
    end
    
    subgraph "Application Layer"
        MAIN[Main Controller<br/>smart_home_system.py]
        FACE[Face Recognition<br/>face_recognition_door.py]
        WEB_SERVER[Web Server<br/>web_server.py]
        AUTO[Automation Engine]
    end
    
    subgraph "Hardware Abstraction Layer"
        GPIO_CTRL[GPIO Controller]
        I2C_CTRL[I2C Controller]
        PWM_CTRL[PWM Controller]
        CAM_CTRL[Camera Controller]
    end
    
    subgraph "Hardware Layer"
        SENSORS[Sensors]
        ACTUATORS[Actuators]
        CONTROLLERS[Controllers]
        CAMERA[Camera Module]
    end
    
    %% User Interface connections
    WEB --> API
    MOBILE --> API
    API --> WEB_SERVER
    WEB_SERVER --> MAIN
    
    %% Application Layer connections
    MAIN --> FACE
    MAIN --> AUTO
    FACE --> MAIN
    AUTO --> MAIN
    
    %% Hardware Abstraction connections
    MAIN --> GPIO_CTRL
    MAIN --> I2C_CTRL
    MAIN --> PWM_CTRL
    FACE --> GPIO_CTRL
    FACE --> PWM_CTRL
    FACE --> CAM_CTRL
    
    %% Hardware Layer connections
    GPIO_CTRL --> SENSORS
    GPIO_CTRL --> ACTUATORS
    I2C_CTRL --> CONTROLLERS
    PWM_CTRL --> ACTUATORS
    CAM_CTRL --> CAMERA
    
    %% Styling
    classDef userLayer fill:#e1f5fe
    classDef appLayer fill:#f3e5f5
    classDef halLayer fill:#e8f5e8
    classDef hwLayer fill:#fff3e0
    
    class WEB,API,MOBILE userLayer
    class MAIN,FACE,WEB_SERVER,AUTO appLayer
    class GPIO_CTRL,I2C_CTRL,PWM_CTRL,CAM_CTRL halLayer
    class SENSORS,ACTUATORS,CONTROLLERS,CAMERA hwLayer
```

## 2. Hardware Component Diagram

```mermaid
graph LR
    subgraph "Raspberry Pi 4"
        CPU[ARM Cortex-A72<br/>Quad Core]
        RAM[4GB RAM]
        GPIO[40-pin GPIO]
        I2C[I2C Interface]
        USB[USB Ports]
        CSI[Camera Interface]
    end
    
    subgraph "Motion Detection"
        PIR1[PIR Room1<br/>GPIO 17]
        PIR2[PIR Room2<br/>GPIO 27]
        PIR3[PIR Room3<br/>GPIO 22]
        PIR4[PIR LivingRoom<br/>GPIO 23]
    end
    
    subgraph "Environmental Sensors"
        DHT11[DHT11 Sensor<br/>GPIO 4]
        MQ7[MQ-7 Gas Sensor<br/>GPIO 24]
        ADS1115[ADS1115 ADC<br/>I2C]
    end
    
    subgraph "Lighting System"
        LED1[Room1 RGB LEDs<br/>GPIO 5,6,13]
        LED2[Room2 RGB LEDs<br/>GPIO 19,26,16]
        LED3[Room3 RGB LEDs<br/>GPIO 20,21,12]
        LED4[LivingRoom RGB LEDs<br/>GPIO 2,3,14]
    end
    
    subgraph "Security System"
        DOOR_SERVO[Door Lock Servo<br/>GPIO 10]
        GARAGE_SERVO[Garage Door Servo<br/>GPIO 11]
        IR_SENSOR[IR Sensor<br/>GPIO 15]
        CAMERA_MOD[USB Camera<br/>Face Recognition]
    end
    
    subgraph "Climate Control"
        L298N[L298N Motor Driver<br/>GPIO 18,25,8,7]
        FAN1[Exhaust Fan 1]
        FAN2[Exhaust Fan 2]
    end
    
    subgraph "Audio System"
        BUZZER[Piezo Buzzer<br/>GPIO 9]
    end
    
    %% Connections
    GPIO --> PIR1
    GPIO --> PIR2
    GPIO --> PIR3
    GPIO --> PIR4
    GPIO --> DHT11
    GPIO --> MQ7
    I2C --> ADS1115
    MQ7 --> ADS1115
    
    GPIO --> LED1
    GPIO --> LED2
    GPIO --> LED3
    GPIO --> LED4
    
    GPIO --> DOOR_SERVO
    GPIO --> GARAGE_SERVO
    GPIO --> IR_SENSOR
    USB --> CAMERA_MOD
    
    GPIO --> L298N
    L298N --> FAN1
    L298N --> FAN2
    
    GPIO --> BUZZER
    
    %% Styling
    classDef piClass fill:#ff9999
    classDef sensorClass fill:#99ccff
    classDef actuatorClass fill:#99ff99
    classDef controllerClass fill:#ffcc99
    
    class CPU,RAM,GPIO,I2C,USB,CSI piClass
    class PIR1,PIR2,PIR3,PIR4,DHT11,MQ7,IR_SENSOR sensorClass
    class LED1,LED2,LED3,LED4,DOOR_SERVO,GARAGE_SERVO,FAN1,FAN2,BUZZER actuatorClass
    class ADS1115,L298N,CAMERA_MOD controllerClass
```

## 3. Data Flow Diagram

```mermaid
flowchart TD
    START([System Start]) --> INIT[Initialize Components]
    INIT --> SENSOR_READ[Read Sensors]
    
    SENSOR_READ --> PIR_CHECK{Motion<br/>Detected?}
    SENSOR_READ --> TEMP_CHECK{Temperature<br/>> 25°C?}
    SENSOR_READ --> GAS_CHECK{Gas<br/>Detected?}
    SENSOR_READ --> FACE_CHECK{Face<br/>Detected?}
    
    PIR_CHECK -->|Yes| LED_ON[Turn On LEDs]
    PIR_CHECK -->|No| LED_OFF[Turn Off LEDs]
    
    TEMP_CHECK -->|Yes| FAN_ON[Turn On Fans]
    TEMP_CHECK -->|No| FAN_OFF[Turn Off Fans]
    
    GAS_CHECK -->|Yes| EMERGENCY[Emergency Mode<br/>Flash LEDs<br/>Sound Alarm]
    GAS_CHECK -->|No| NORMAL[Normal Operation]
    
    FACE_CHECK -->|Recognized| UNLOCK[Unlock Door<br/>Welcome Sound]
    FACE_CHECK -->|Unknown| DENY[Deny Access<br/>Alert Sound]
    FACE_CHECK -->|None| CONTINUE[Continue Monitoring]
    
    LED_ON --> UPDATE_STATE[Update System State]
    LED_OFF --> UPDATE_STATE
    FAN_ON --> UPDATE_STATE
    FAN_OFF --> UPDATE_STATE
    EMERGENCY --> UPDATE_STATE
    NORMAL --> UPDATE_STATE
    UNLOCK --> AUTO_LOCK[Auto Lock After 5s]
    DENY --> LOG_ACCESS[Log Access Attempt]
    CONTINUE --> UPDATE_STATE
    
    AUTO_LOCK --> UPDATE_STATE
    LOG_ACCESS --> UPDATE_STATE
    
    UPDATE_STATE --> WEB_UPDATE[Update Web Interface]
    WEB_UPDATE --> AUTO_RULES[Process Automation Rules]
    AUTO_RULES --> DELAY[Wait 100ms]
    DELAY --> SENSOR_READ
    
    %% Styling
    classDef startEnd fill:#ff6b6b
    classDef process fill:#4ecdc4
    classDef decision fill:#45b7d1
    classDef action fill:#96ceb4
    
    class START startEnd
    class INIT,SENSOR_READ,UPDATE_STATE,WEB_UPDATE,AUTO_RULES,DELAY process
    class PIR_CHECK,TEMP_CHECK,GAS_CHECK,FACE_CHECK decision
    class LED_ON,LED_OFF,FAN_ON,FAN_OFF,EMERGENCY,NORMAL,UNLOCK,DENY,CONTINUE,AUTO_LOCK,LOG_ACCESS action
```

## 4. Face Recognition System Flow

```mermaid
flowchart TD
    CAMERA_INIT[Initialize Camera] --> CAMERA_CHECK{Camera<br/>Available?}
    CAMERA_CHECK -->|No| CAMERA_ERROR[Camera Error<br/>Log & Exit]
    CAMERA_CHECK -->|Yes| START_MONITOR[Start Monitoring Thread]
    
    START_MONITOR --> CAPTURE[Capture Frame]
    CAPTURE --> RESIZE[Resize Frame<br/>for Performance]
    RESIZE --> DETECT[Detect Faces]
    
    DETECT --> FACE_FOUND{Face<br/>Found?}
    FACE_FOUND -->|No| WAIT[Wait 100ms]
    FACE_FOUND -->|Yes| ENCODE[Generate Face Encoding]
    
    ENCODE --> COMPARE[Compare with Database]
    COMPARE --> MATCH_CHECK{Match<br/>Found?}
    
    MATCH_CHECK -->|No| UNKNOWN[Unknown Person]
    MATCH_CHECK -->|Yes| CONFIDENCE_CHECK{Confidence<br/>> 0.6?}
    
    CONFIDENCE_CHECK -->|No| LOW_CONF[Low Confidence<br/>Treat as Unknown]
    CONFIDENCE_CHECK -->|Yes| RECOGNIZED[Person Recognized]
    
    UNKNOWN --> DENY_ACCESS[Play Deny Sound<br/>Log Attempt]
    LOW_CONF --> DENY_ACCESS
    
    RECOGNIZED --> GRANT_ACCESS[Unlock Door<br/>Play Welcome Sound<br/>Log Access]
    GRANT_ACCESS --> AUTO_LOCK_TIMER[Start Auto-Lock Timer<br/>5 seconds]
    
    DENY_ACCESS --> LOG_DENY[Log Denied Access]
    AUTO_LOCK_TIMER --> SCHEDULE_LOCK[Schedule Door Lock]
    LOG_DENY --> WAIT
    SCHEDULE_LOCK --> WAIT
    
    WAIT --> CAPTURE
    
    %% Styling
    classDef initClass fill:#ffd93d
    classDef processClass fill:#6bcf7f
    classDef decisionClass fill:#4d96ff
    classDef actionClass fill:#ff6b9d
    classDef errorClass fill:#ff4757
    
    class CAMERA_INIT,START_MONITOR initClass
    class CAPTURE,RESIZE,DETECT,ENCODE,COMPARE processClass
    class CAMERA_CHECK,FACE_FOUND,MATCH_CHECK,CONFIDENCE_CHECK decisionClass
    class UNKNOWN,LOW_CONF,RECOGNIZED,GRANT_ACCESS,DENY_ACCESS,AUTO_LOCK_TIMER,SCHEDULE_LOCK,LOG_DENY actionClass
    class CAMERA_ERROR errorClass
```

## 5. GPIO Pin Assignment Diagram

```mermaid
graph LR
    subgraph "Raspberry Pi GPIO"
        GPIO2[GPIO 2<br/>Pin 3]
        GPIO3[GPIO 3<br/>Pin 5]
        GPIO4[GPIO 4<br/>Pin 7]
        GPIO5[GPIO 5<br/>Pin 29]
        GPIO6[GPIO 6<br/>Pin 31]
        GPIO7[GPIO 7<br/>Pin 26]
        GPIO8[GPIO 8<br/>Pin 24]
        GPIO9[GPIO 9<br/>Pin 21]
        GPIO10[GPIO 10<br/>Pin 19]
        GPIO11[GPIO 11<br/>Pin 23]
        GPIO12[GPIO 12<br/>Pin 32]
        GPIO13[GPIO 13<br/>Pin 33]
        GPIO14[GPIO 14<br/>Pin 8]
        GPIO15[GPIO 15<br/>Pin 10]
        GPIO16[GPIO 16<br/>Pin 36]
        GPIO17[GPIO 17<br/>Pin 11]
        GPIO18[GPIO 18<br/>Pin 12]
        GPIO19[GPIO 19<br/>Pin 35]
        GPIO20[GPIO 20<br/>Pin 38]
        GPIO21[GPIO 21<br/>Pin 40]
        GPIO22[GPIO 22<br/>Pin 15]
        GPIO23[GPIO 23<br/>Pin 16]
        GPIO24[GPIO 24<br/>Pin 18]
        GPIO25[GPIO 25<br/>Pin 22]
        GPIO26[GPIO 26<br/>Pin 37]
        GPIO27[GPIO 27<br/>Pin 13]
    end
    
    subgraph "Components"
        LR_RED[LivingRoom Red LED]
        LR_GREEN[LivingRoom Green LED]
        DHT[DHT11 Sensor]
        R1_RED[Room1 Red LED]
        R1_GREEN[Room1 Green LED]
        MOTOR_B4[Motor B IN4]
        MOTOR_B3[Motor B IN3]
        BUZZER_COMP[Piezo Buzzer]
        DOOR_SERVO_COMP[Door Servo]
        GARAGE_SERVO_COMP[Garage Servo]
        R3_BLUE[Room3 Blue LED]
        R1_BLUE[Room1 Blue LED]
        LR_BLUE[LivingRoom Blue LED]
        IR_COMP[IR Sensor]
        R2_BLUE[Room2 Blue LED]
        PIR_R1[PIR Room1]
        MOTOR_A1[Motor A IN1]
        R2_RED[Room2 Red LED]
        R3_RED[Room3 Red LED]
        R3_GREEN[Room3 Green LED]
        PIR_R3[PIR Room3]
        PIR_LR[PIR LivingRoom]
        GAS_COMP[Gas Sensor]
        MOTOR_A2[Motor A IN2]
        R2_GREEN[Room2 Green LED]
        PIR_R2[PIR Room2]
        I2C_SDA[I2C SDA]
        I2C_SCL[I2C SCL]
    end
    
    %% GPIO to Component connections
    GPIO2 --> LR_RED
    GPIO2 --> I2C_SDA
    GPIO3 --> LR_GREEN
    GPIO3 --> I2C_SCL
    GPIO4 --> DHT
    GPIO5 --> R1_RED
    GPIO6 --> R1_GREEN
    GPIO7 --> MOTOR_B4
    GPIO8 --> MOTOR_B3
    GPIO9 --> BUZZER_COMP
    GPIO10 --> DOOR_SERVO_COMP
    GPIO11 --> GARAGE_SERVO_COMP
    GPIO12 --> R3_BLUE
    GPIO13 --> R1_BLUE
    GPIO14 --> LR_BLUE
    GPIO15 --> IR_COMP
    GPIO16 --> R2_BLUE
    GPIO17 --> PIR_R1
    GPIO18 --> MOTOR_A1
    GPIO19 --> R2_RED
    GPIO20 --> R3_RED
    GPIO21 --> R3_GREEN
    GPIO22 --> PIR_R3
    GPIO23 --> PIR_LR
    GPIO24 --> GAS_COMP
    GPIO25 --> MOTOR_A2
    GPIO26 --> R2_GREEN
    GPIO27 --> PIR_R2
    
    %% Styling
    classDef gpioClass fill:#ff9999
    classDef ledClass fill:#99ff99
    classDef sensorClass fill:#99ccff
    classDef motorClass fill:#ffcc99
    classDef servoClass fill:#cc99ff
    classDef i2cClass fill:#ffff99
    
    class GPIO2,GPIO3,GPIO4,GPIO5,GPIO6,GPIO7,GPIO8,GPIO9,GPIO10,GPIO11,GPIO12,GPIO13,GPIO14,GPIO15,GPIO16,GPIO17,GPIO18,GPIO19,GPIO20,GPIO21,GPIO22,GPIO23,GPIO24,GPIO25,GPIO26,GPIO27 gpioClass
    class LR_RED,LR_GREEN,R1_RED,R1_GREEN,R1_BLUE,LR_BLUE,R2_BLUE,R2_RED,R3_RED,R3_GREEN,R3_BLUE,R2_GREEN ledClass
    class DHT,PIR_R1,PIR_R2,PIR_R3,PIR_LR,GAS_COMP,IR_COMP sensorClass
    class MOTOR_A1,MOTOR_A2,MOTOR_B3,MOTOR_B4 motorClass
    class DOOR_SERVO_COMP,GARAGE_SERVO_COMP,BUZZER_COMP servoClass
    class I2C_SDA,I2C_SCL i2cClass
```

## 6. Web Interface Architecture

```mermaid
graph TB
    subgraph "Frontend"
        DASHBOARD[Dashboard Page<br/>dashboard.html]
        CONTROLS[Controls Page<br/>controls.html]
        AUTOMATION[Automation Page<br/>automation.html]
        MONITORING[Monitoring Page<br/>monitoring.html]
        SETTINGS[Settings Page<br/>settings.html]
    end
    
    subgraph "Static Assets"
        CSS[Stylesheets<br/>style.css]
        JS[JavaScript<br/>main.js]
        AUTO_JS[Automation JS<br/>automation.js]
    end
    
    subgraph "Backend API"
        FLASK[Flask Server<br/>Port 5000]
        SOCKETIO[SocketIO<br/>Real-time Updates]
    end
    
    subgraph "API Endpoints"
        STATE_API[/api/state]
        CONTROL_API[/api/control/*]
        RULES_API[/api/rules/*]
        FACE_API[/api/face/*]
        SYSTEM_API[/api/system/*]
    end
    
    subgraph "Core System"
        MAIN_SYS[Main System<br/>smart_home_system.py]
        FACE_SYS[Face Recognition<br/>face_recognition_door.py]
    end
    
    %% Frontend connections
    DASHBOARD --> CSS
    DASHBOARD --> JS
    CONTROLS --> CSS
    CONTROLS --> JS
    AUTOMATION --> CSS
    AUTOMATION --> AUTO_JS
    MONITORING --> CSS
    MONITORING --> JS
    SETTINGS --> CSS
    SETTINGS --> JS
    
    %% Frontend to Backend
    DASHBOARD --> FLASK
    CONTROLS --> FLASK
    AUTOMATION --> FLASK
    MONITORING --> FLASK
    SETTINGS --> FLASK
    
    %% Real-time updates
    FLASK --> SOCKETIO
    SOCKETIO --> DASHBOARD
    SOCKETIO --> CONTROLS
    SOCKETIO --> MONITORING
    
    %% API connections
    FLASK --> STATE_API
    FLASK --> CONTROL_API
    FLASK --> RULES_API
    FLASK --> FACE_API
    FLASK --> SYSTEM_API
    
    %% Backend to Core System
    STATE_API --> MAIN_SYS
    CONTROL_API --> MAIN_SYS
    RULES_API --> MAIN_SYS
    FACE_API --> FACE_SYS
    SYSTEM_API --> MAIN_SYS
    
    %% System integration
    MAIN_SYS --> FACE_SYS
    FACE_SYS --> MAIN_SYS
    
    %% Styling
    classDef frontendClass fill:#e3f2fd
    classDef staticClass fill:#f3e5f5
    classDef backendClass fill:#e8f5e8
    classDef apiClass fill:#fff3e0
    classDef systemClass fill:#fce4ec
    
    class DASHBOARD,CONTROLS,AUTOMATION,MONITORING,SETTINGS frontendClass
    class CSS,JS,AUTO_JS staticClass
    class FLASK,SOCKETIO backendClass
    class STATE_API,CONTROL_API,RULES_API,FACE_API,SYSTEM_API apiClass
    class MAIN_SYS,FACE_SYS systemClass
```

## 7. Automation Rules Engine

```mermaid
flowchart TD
    RULE_START[Rule Engine Start] --> LOAD_RULES[Load Automation Rules]
    LOAD_RULES --> RULE_LOOP[Process Each Rule]
    
    RULE_LOOP --> RULE_ACTIVE{Rule<br/>Active?}
    RULE_ACTIVE -->|No| NEXT_RULE[Next Rule]
    RULE_ACTIVE -->|Yes| EVAL_CONDITION[Evaluate Condition]
    
    EVAL_CONDITION --> CONDITION_TYPE{Condition<br/>Type?}
    
    CONDITION_TYPE -->|Temperature| TEMP_CHECK[Check Temperature<br/>vs Threshold]
    CONDITION_TYPE -->|Humidity| HUM_CHECK[Check Humidity<br/>vs Threshold]
    CONDITION_TYPE -->|Motion| MOTION_CHECK[Check Motion<br/>in Specified Room]
    CONDITION_TYPE -->|Gas| GAS_CHECK[Check Gas<br/>Detection Status]
    CONDITION_TYPE -->|Time| TIME_CHECK[Check Current<br/>Time vs Schedule]
    
    TEMP_CHECK --> CONDITION_MET{Condition<br/>Met?}
    HUM_CHECK --> CONDITION_MET
    MOTION_CHECK --> CONDITION_MET
    GAS_CHECK --> CONDITION_MET
    TIME_CHECK --> CONDITION_MET
    
    CONDITION_MET -->|No| NEXT_RULE
    CONDITION_MET -->|Yes| EXECUTE_ACTION[Execute Action]
    
    EXECUTE_ACTION --> ACTION_TYPE{Action<br/>Type?}
    
    ACTION_TYPE -->|Fan| FAN_ACTION[Control Fan<br/>On/Off]
    ACTION_TYPE -->|Light| LIGHT_ACTION[Control LED<br/>Color/State]
    ACTION_TYPE -->|Door| DOOR_ACTION[Control Door<br/>Lock/Unlock]
    ACTION_TYPE -->|Garage| GARAGE_ACTION[Control Garage<br/>Open/Close]
    ACTION_TYPE -->|Alert| ALERT_ACTION[Trigger Alert<br/>Sound/Visual]
    
    FAN_ACTION --> LOG_ACTION[Log Action Executed]
    LIGHT_ACTION --> LOG_ACTION
    DOOR_ACTION --> LOG_ACTION
    GARAGE_ACTION --> LOG_ACTION
    ALERT_ACTION --> LOG_ACTION
    
    LOG_ACTION --> NEXT_RULE
    NEXT_RULE --> MORE_RULES{More<br/>Rules?}
    MORE_RULES -->|Yes| RULE_LOOP
    MORE_RULES -->|No| WAIT_CYCLE[Wait 1 Second]
    WAIT_CYCLE --> RULE_START
    
    %% Styling
    classDef startClass fill:#ff6b6b
    classDef processClass fill:#4ecdc4
    classDef decisionClass fill:#45b7d1
    classDef actionClass fill:#96ceb4
    classDef conditionClass fill:#feca57
    
    class RULE_START startClass
    class LOAD_RULES,RULE_LOOP,EVAL_CONDITION,EXECUTE_ACTION,LOG_ACTION,WAIT_CYCLE processClass
    class RULE_ACTIVE,CONDITION_MET,CONDITION_TYPE,ACTION_TYPE,MORE_RULES decisionClass
    class FAN_ACTION,LIGHT_ACTION,DOOR_ACTION,GARAGE_ACTION,ALERT_ACTION,NEXT_RULE actionClass
    class TEMP_CHECK,HUM_CHECK,MOTION_CHECK,GAS_CHECK,TIME_CHECK conditionClass
```

## 8. System State Management

```mermaid
stateDiagram-v2
    [*] --> SystemInit
    
    SystemInit --> NormalOperation : Initialization Complete
    
    state NormalOperation {
        [*] --> Monitoring
        Monitoring --> MotionDetected : PIR Triggered
        Monitoring --> TemperatureHigh : Temp > 25°C
        Monitoring --> FaceDetected : Camera Detects Face
        Monitoring --> GasDetected : Gas Sensor Triggered
        
        MotionDetected --> LEDsOn : Turn On Room LEDs
        LEDsOn --> Monitoring : Motion Stops
        
        TemperatureHigh --> FansOn : Activate Cooling
        FansOn --> Monitoring : Temp < 25°C
        
        FaceDetected --> FaceRecognition : Process Face
        FaceRecognition --> DoorUnlock : Face Recognized
        FaceRecognition --> AccessDenied : Face Unknown
        DoorUnlock --> AutoLock : After 5 seconds
        AccessDenied --> Monitoring : Log Attempt
        AutoLock --> Monitoring : Door Locked
        
        GasDetected --> EmergencyMode : Gas Leak Alert
    }
    
    state EmergencyMode {
        [*] --> FlashingLEDs
        FlashingLEDs --> SoundAlarm : Visual Alert Active
        SoundAlarm --> NotifyUsers : Audio Alert Active
        NotifyUsers --> FlashingLEDs : Continue Emergency
        FlashingLEDs --> [*] : Gas Cleared
    }
    
    EmergencyMode --> NormalOperation : Gas Level Normal
    
    NormalOperation --> MaintenanceMode : Manual Override
    MaintenanceMode --> NormalOperation : Resume Normal
    
    NormalOperation --> SystemShutdown : Shutdown Command
    MaintenanceMode --> SystemShutdown : Shutdown Command
    EmergencyMode --> SystemShutdown : Emergency Shutdown
    
    SystemShutdown --> [*]
```

## 9. Network Communication Flow

```mermaid
sequenceDiagram
    participant User as User Browser
    participant Web as Web Server
    participant Main as Main System
    participant Face as Face Recognition
    participant GPIO as GPIO Hardware
    
    User->>Web: HTTP Request (Dashboard)
    Web->>Main: Get System State
    Main->>GPIO: Read Sensors
    GPIO-->>Main: Sensor Data
    Main-->>Web: System State JSON
    Web-->>User: HTML + Data
    
    Note over User,GPIO: Real-time Updates via WebSocket
    
    Main->>Web: Sensor Update (SocketIO)
    Web->>User: Live Data Update
    
    Note over User,GPIO: User Control Action
    
    User->>Web: Control Request (Turn On Fan)
    Web->>Main: API Call (/api/control/fan)
    Main->>GPIO: Set Fan State
    GPIO-->>Main: Confirmation
    Main-->>Web: Success Response
    Web-->>User: Status Update
    
    Note over User,GPIO: Face Recognition Flow
    
    Face->>GPIO: Read Camera Frame
    GPIO-->>Face: Image Data
    Face->>Face: Process Face Recognition
    alt Face Recognized
        Face->>GPIO: Unlock Door
        Face->>Main: Access Granted Event
        Main->>Web: Security Update
        Web->>User: Access Notification
    else Face Unknown
        Face->>GPIO: Play Deny Sound
        Face->>Main: Access Denied Event
        Main->>Web: Security Alert
        Web->>User: Security Notification
    end
    
    Note over User,GPIO: Automation Rule Execution
    
    Main->>Main: Evaluate Rules
    Main->>GPIO: Execute Actions
    GPIO-->>Main: Action Confirmation
    Main->>Web: State Update
    Web->>User: Automation Notification
```

## 10. File Structure and Dependencies

```mermaid
graph TD
    subgraph "Core System Files"
        MAIN_PY[smart_home_system.py<br/>Main Controller]
        WEB_PY[web_server.py<br/>Web Interface]
        FACE_PY[face_recognition_door.py<br/>Face Recognition]
    end
    
    subgraph "Configuration Files"
        REQ_TXT[requirements.txt<br/>Dependencies]
        FACE_REQ[face_recognition_requirements.txt<br/>Face Recognition Deps]
        WEB_REQ[web_requirements.txt<br/>Web Dependencies]
        RULES_JSON[automation_rules.json<br/>Automation Rules]
    end
    
    subgraph "Testing Framework"
        TEST_MOTION[test_motion_detection.py]
        TEST_TEMP[test_temperature_fan.py]
        TEST_GAS[test_gas_detection.py]
        TEST_FACE[test_face_recognition.py]
        TEST_SYSTEM[test_system_connectivity.py]
        VERIFY[verify_system.py]
    end
    
    subgraph "Documentation"
        README[README.md]
        HARDWARE_DOC[hardware_documentation.md]
        COMPREHENSIVE[COMPREHENSIVE_SYSTEM_DOCUMENTATION.md]
        WIRING[HARDWARE_WIRING_COMPATIBILITY_REPORT.md]
        DIAGRAMS[SYSTEM_ARCHITECTURE_DIAGRAMS.md]
    end
    
    subgraph "Web Interface"
        TEMPLATES[templates/<br/>HTML Files]
        STATIC[static/<br/>CSS/JS Files]
        BASE_HTML[base.html]
        DASHBOARD_HTML[dashboard.html]
        STYLE_CSS[style.css]
        MAIN_JS[main.js]
    end
    
    subgraph "Setup Scripts"
        SETUP_PI[setup_raspberry_pi.sh]
        SETUP_FACE[setup_face_recognition.sh]
    end
    
    subgraph "Data Files"
        FACE_DB[face_database.pkl<br/>Face Encodings]
        ACCESS_LOG[access_log.json<br/>Access History]
        SYSTEM_LOG[system.log<br/>System Events]
    end
    
    %% Dependencies
    MAIN_PY --> REQ_TXT
    FACE_PY --> FACE_REQ
    WEB_PY --> WEB_REQ
    MAIN_PY --> RULES_JSON
    
    %% System Integration
    WEB_PY --> MAIN_PY
    FACE_PY --> MAIN_PY
    MAIN_PY --> FACE_PY
    
    %% Testing Dependencies
    TEST_MOTION --> MAIN_PY
    TEST_TEMP --> MAIN_PY
    TEST_GAS --> MAIN_PY
    TEST_FACE --> FACE_PY
    TEST_SYSTEM --> MAIN_PY
    VERIFY --> MAIN_PY
    
    %% Web Interface Dependencies
    WEB_PY --> TEMPLATES
    TEMPLATES --> BASE_HTML
    TEMPLATES --> DASHBOARD_HTML
    STATIC --> STYLE_CSS
    STATIC --> MAIN_JS
    
    %% Data Dependencies
    FACE_PY --> FACE_DB
    FACE_PY --> ACCESS_LOG
    MAIN_PY --> SYSTEM_LOG
    
    %% Setup Dependencies
    SETUP_PI --> REQ_TXT
    SETUP_FACE --> FACE_REQ
    
    %% Styling
    classDef coreClass fill:#ff9999
    classDef configClass fill:#99ccff
    classDef testClass fill:#99ff99
    classDef docClass fill:#ffcc99
    classDef webClass fill:#cc99ff
    classDef setupClass fill:#ffff99
    classDef dataClass fill:#ff99cc
    
    class MAIN_PY,WEB_PY,FACE_PY coreClass
    class REQ_TXT,FACE_REQ,WEB_REQ,RULES_JSON configClass
    class TEST_MOTION,TEST_TEMP,TEST_GAS,TEST_FACE,TEST_SYSTEM,VERIFY testClass
    class README,HARDWARE_DOC,COMPREHENSIVE,WIRING,DIAGRAMS docClass
    class TEMPLATES,STATIC,BASE_HTML,DASHBOARD_HTML,STYLE_CSS,MAIN_JS webClass
    class SETUP_PI,SETUP_FACE setupClass
    class FACE_DB,ACCESS_LOG,SYSTEM_LOG dataClass
```

---

## Summary

These Mermaid.js diagrams provide a comprehensive visual representation of the Smart Home Automation System, covering:

1. **Overall Architecture** - High-level system layers and components
2. **Hardware Components** - Physical devices and their GPIO connections
3. **Data Flow** - How information moves through the system
4. **Face Recognition Flow** - Detailed face recognition process
5. **GPIO Pin Assignment** - Complete pin mapping visualization
6. **Web Interface Architecture** - Frontend and backend structure
7. **Automation Rules Engine** - Rule processing workflow
8. **System State Management** - State transitions and modes
9. **Network Communication** - Sequence of system interactions
10. **File Structure** - Project organization and dependencies

Each diagram uses proper Mermaid.js syntax with appropriate arrows, styling, and relationships to clearly illustrate the system's architecture and operation. 