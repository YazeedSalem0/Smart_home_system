#!/bin/bash

# Smart Home Automation System Setup Script for Raspberry Pi 4
# This script prepares the Raspberry Pi with all necessary configurations

echo "=========================================="
echo "Smart Home System Setup for Raspberry Pi 4"
echo "=========================================="

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip if not already installed
echo "Installing Python 3 and pip..."
sudo apt install python3 python3-pip python3-venv -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt install -y \
    i2c-tools \
    python3-dev \
    python3-setuptools \
    build-essential \
    cmake \
    pkg-config \
    libjpeg-dev \
    libtiff5-dev \
    libjasper-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libfontconfig1-dev \
    libcairo2-dev \
    libgdk-pixbuf2.0-dev \
    libpango1.0-dev \
    libgtk2.0-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran \
    libhdf5-dev \
    libhdf5-serial-dev \
    libhdf5-103 \
    python3-pyqt5 \
    python3-h5py \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev

# Enable I2C interface
echo "Enabling I2C interface..."
sudo raspi-config nonint do_i2c 0

# Enable SPI interface (if needed)
echo "Enabling SPI interface..."
sudo raspi-config nonint do_spi 0

# Add user to i2c group
echo "Adding user to i2c group..."
sudo usermod -a -G i2c $USER

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv smart_home_env

# Activate virtual environment
echo "Activating virtual environment..."
source smart_home_env/bin/activate

# Upgrade pip in virtual environment
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python packages
echo "Installing Python packages..."
pip install -r requirements.txt

# Install additional packages that might be needed
echo "Installing additional packages..."
pip install RPi.GPIO --upgrade

# Create systemd service file for auto-start
echo "Creating systemd service file..."
sudo tee /etc/systemd/system/smart-home.service > /dev/null <<EOF
[Unit]
Description=Smart Home Automation System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/smart_home_env/bin
ExecStart=$(pwd)/smart_home_env/bin/python smart_home_system.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Set permissions for GPIO access
echo "Setting up GPIO permissions..."
sudo usermod -a -G gpio $USER

# Test I2C devices
echo "Testing I2C devices..."
echo "Available I2C devices:"
sudo i2cdetect -y 1

# Create log directory
echo "Creating log directory..."
mkdir -p logs

# Set up log rotation
echo "Setting up log rotation..."
sudo tee /etc/logrotate.d/smart-home > /dev/null <<EOF
$(pwd)/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
EOF

echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Reboot the Raspberry Pi: sudo reboot"
echo "2. After reboot, test the hardware connections"
echo "3. Run the test scripts to verify components:"
echo "   - python test_motion_detection.py"
echo "   - python test_temperature_fan.py"
echo "   - python test_gas_detection.py"
echo "   - python test_garage_ir.py"
echo "   - python test_buzzer.py"
echo "   - python test_l298n_motor_driver.py"
echo "4. Start the main system: python smart_home_system.py"
echo "5. Enable auto-start: sudo systemctl enable smart-home.service"
echo ""
echo "Hardware Checklist:"
echo "- [ ] L298N motor driver connected (IN1=GPIO18, IN2=GPIO25, IN3=GPIO8, IN4=GPIO7)"
echo "- [ ] DC motors connected to L298N outputs"
echo "- [ ] External power supply connected to L298N +12V terminal"
echo "- [ ] DHT11 sensor connected to GPIO 4"
echo "- [ ] PIR sensors connected to GPIO 17, 27, 22, 23"
echo "- [ ] RGB LEDs connected with proper resistors"
echo "- [ ] MQ-7 gas sensor connected to GPIO 24 and ADS1115"
echo "- [ ] I2C devices (ADS1115, LCD) connected to GPIO 2 (SDA) and GPIO 3 (SCL)"
echo "- [ ] Servos connected to GPIO 10 and GPIO 11"
echo "- [ ] Buzzer connected to GPIO 9"
echo "- [ ] IR sensor connected to GPIO 15"
echo ""
echo "Important Notes:"
echo "- Ensure ENA and ENB pins on L298N are connected to 5V"
echo "- Use external power supply for motors to prevent Pi reboots"
echo "- Connect common ground between Pi and external power supply"
echo "- Test each component individually before running the full system"

echo "Available test scripts:"
echo "   - python test_motion_detection.py"
echo "   - python test_temperature_fan.py"
echo "   - python test_gas_detection.py"
echo "   - python test_garage_ir.py"
echo "   - python test_buzzer.py"
echo "   - python test_l298n_motor_driver.py" 