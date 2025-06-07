#!/usr/bin/env python3
"""
Smart Home Web Server
A dedicated web interface for the Smart Home Automation System
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit
import json
import os
import time
import threading
import requests
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smart_home_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration
SMART_HOME_API_BASE = "http://localhost:5000/api"
UPDATE_INTERVAL = 2  # seconds

# Global state to cache system data
cached_state = {
    'last_update': None,
    'system_data': {},
    'connection_status': False
}

def get_system_state():
    """Get current system state from the main smart home system"""
    try:
        response = requests.get(f"{SMART_HOME_API_BASE}/state", timeout=5)
        if response.status_code == 200:
            cached_state['system_data'] = response.json()
            cached_state['last_update'] = datetime.now()
            cached_state['connection_status'] = True
            logger.info("Successfully retrieved system state")
            return cached_state['system_data']
        else:
            logger.error(f"API returned status code: {response.status_code}")
            cached_state['connection_status'] = False
            return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error to smart home system: {e}")
        cached_state['connection_status'] = False
        return None
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout connecting to smart home system: {e}")
        cached_state['connection_status'] = False
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting system state: {e}")
        cached_state['connection_status'] = False
        return None

def send_control_command(endpoint, data):
    """Send control command to the main smart home system"""
    try:
        logger.info(f"Sending command to {endpoint} with data: {data}")
        response = requests.post(f"{SMART_HOME_API_BASE}/{endpoint}", 
                               json=data, timeout=5)
        if response.status_code == 200:
            logger.info(f"Command to {endpoint} successful")
            return True
        else:
            logger.error(f"Command to {endpoint} failed with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error sending command to {endpoint}: {e}")
        return False
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout sending command to {endpoint}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending command to {endpoint}: {e}")
        return False

def get_automation_rules():
    """Get automation rules from the main system"""
    try:
        response = requests.get(f"{SMART_HOME_API_BASE}/rules", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        logger.error(f"Error getting automation rules: {e}")
        return []

# Routes
@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/controls')
def controls():
    """Device controls page"""
    return render_template('controls.html')

@app.route('/automation')
def automation():
    """Automation rules page"""
    return render_template('automation.html')

@app.route('/monitoring')
def monitoring():
    """Real-time monitoring page"""
    return render_template('monitoring.html')

@app.route('/settings')
def settings():
    """System settings page"""
    return render_template('settings.html')

# API Routes
@app.route('/api/dashboard/data')
def dashboard_data():
    """Get dashboard data"""
    state = get_system_state()
    if state:
        return jsonify({
            'success': True,
            'data': state,
            'connection_status': cached_state['connection_status'],
            'last_update': cached_state['last_update'].isoformat() if cached_state['last_update'] else None
        })
    return jsonify({
        'success': False,
        'error': 'Unable to connect to smart home system',
        'connection_status': False
    })

@app.route('/api/control/fan', methods=['POST'])
def control_fan():
    """Control fan system"""
    data = request.get_json()
    success = send_control_command('control/fan', data)
    return jsonify({'success': success})

@app.route('/api/control/light', methods=['POST'])
def control_light():
    """Control lighting system"""
    data = request.get_json()
    success = send_control_command('control/light', data)
    return jsonify({'success': success})

@app.route('/api/control/door', methods=['POST'])
def control_door():
    """Control door lock"""
    data = request.get_json()
    success = send_control_command('control/door', data)
    return jsonify({'success': success})

@app.route('/api/control/garage', methods=['POST'])
def control_garage():
    """Control garage door"""
    data = request.get_json()
    success = send_control_command('control/garage', data)
    return jsonify({'success': success})

@app.route('/api/automation/rules')
def get_rules():
    """Get automation rules"""
    rules = get_automation_rules()
    return jsonify({'success': True, 'rules': rules})

@app.route('/api/automation/rules', methods=['POST'])
def create_rule():
    """Create new automation rule"""
    data = request.get_json()
    try:
        response = requests.post(f"{SMART_HOME_API_BASE}/rules", json=data, timeout=5)
        return jsonify({'success': response.status_code == 200})
    except Exception as e:
        logger.error(f"Error creating rule: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/automation/rules/<rule_id>', methods=['PUT'])
def update_rule(rule_id):
    """Update automation rule"""
    data = request.get_json()
    try:
        response = requests.put(f"{SMART_HOME_API_BASE}/rules/{rule_id}", json=data, timeout=5)
        return jsonify({'success': response.status_code == 200})
    except Exception as e:
        logger.error(f"Error updating rule: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/automation/rules/<rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    """Delete automation rule"""
    try:
        response = requests.delete(f"{SMART_HOME_API_BASE}/rules/{rule_id}", timeout=5)
        return jsonify({'success': response.status_code == 200})
    except Exception as e:
        logger.error(f"Error deleting rule: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/automation/rules/<rule_id>/toggle', methods=['POST'])
def toggle_rule(rule_id):
    """Toggle automation rule"""
    try:
        response = requests.post(f"{SMART_HOME_API_BASE}/rules/{rule_id}/toggle", timeout=5)
        return jsonify({'success': response.status_code == 200})
    except Exception as e:
        logger.error(f"Error toggling rule: {e}")
        return jsonify({'success': False, 'error': str(e)})

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('status', {'msg': 'Connected to Smart Home Server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')

@socketio.on('request_update')
def handle_update_request():
    """Handle real-time update request"""
    state = get_system_state()
    if state:
        emit('system_update', {
            'data': state,
            'timestamp': datetime.now().isoformat(),
            'connection_status': cached_state['connection_status']
        })

def background_updater():
    """Background thread to send periodic updates"""
    while True:
        try:
            state = get_system_state()
            if state:
                socketio.emit('system_update', {
                    'data': state,
                    'timestamp': datetime.now().isoformat(),
                    'connection_status': cached_state['connection_status']
                })
            time.sleep(UPDATE_INTERVAL)
        except Exception as e:
            logger.error(f"Error in background updater: {e}")
            time.sleep(UPDATE_INTERVAL)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Start background updater thread
    updater_thread = threading.Thread(target=background_updater)
    updater_thread.daemon = True
    updater_thread.start()
    
    print("Smart Home Web Server starting...")
    print("Dashboard will be available at: http://localhost:8080")
    print("Make sure the main smart home system is running on port 5000")
    
    # Run the web server
    socketio.run(app, host='0.0.0.0', port=8080, debug=False) 