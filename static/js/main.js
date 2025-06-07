// Main JavaScript for Smart Home Web Interface

// Global variables
let socket;
let systemData = {};
let connectionStatus = false;
let updateInterval;

// Initialize the application
$(document).ready(function() {
    initializeSocket();
    initializeUI();
    startPeriodicUpdates();
    
    // Set active navigation item
    setActiveNavItem();
});

// Socket.IO initialization
function initializeSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to server');
        updateConnectionStatus(true);
        socket.emit('request_update');
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from server');
        updateConnectionStatus(false);
    });
    
    socket.on('system_update', function(data) {
        console.log('Received system update:', data);
        systemData = data.data;
        updateSystemData(systemData);
        updateLastUpdateTime(data.timestamp);
        updateConnectionStatus(data.connection_status);
    });
    
    socket.on('status', function(data) {
        console.log('Status:', data.msg);
    });
}

// Initialize UI components
function initializeUI() {
    // Add loading indicators
    showLoadingState();
    
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Add click handlers for navigation
    $('.nav-link').click(function() {
        setActiveNavItem($(this));
    });
}

// Start periodic updates
function startPeriodicUpdates() {
    // Request updates every 5 seconds
    updateInterval = setInterval(function() {
        if (socket && socket.connected) {
            socket.emit('request_update');
        } else {
            // Fallback to HTTP request if socket is not connected
            fetchSystemData();
        }
    }, 5000);
}

// Fetch system data via HTTP (fallback)
function fetchSystemData() {
    $.get('/api/dashboard/data')
        .done(function(response) {
            if (response.success) {
                systemData = response.data;
                updateSystemData(systemData);
                updateConnectionStatus(response.connection_status);
                if (response.last_update) {
                    updateLastUpdateTime(response.last_update);
                }
            } else {
                updateConnectionStatus(false);
                console.error('Failed to fetch system data:', response.error);
            }
        })
        .fail(function() {
            updateConnectionStatus(false);
            console.error('Failed to communicate with server');
        });
}

// Update system data (to be overridden by page-specific functions)
function updateSystemData(data) {
    console.log('Updating system data:', data);
    // This function will be extended by page-specific scripts
}

// Update connection status indicator
function updateConnectionStatus(connected) {
    connectionStatus = connected;
    const statusElement = $('#connection-status');
    
    if (connected) {
        statusElement.removeClass('bg-danger bg-warning bg-secondary')
                   .addClass('bg-success')
                   .html('<i class="fas fa-circle me-1"></i>Connected');
    } else {
        statusElement.removeClass('bg-success bg-warning bg-secondary')
                   .addClass('bg-danger')
                   .html('<i class="fas fa-circle me-1"></i>Disconnected');
    }
}

// Update last update time
function updateLastUpdateTime(timestamp) {
    const updateTime = new Date(timestamp);
    const formattedTime = updateTime.toLocaleTimeString();
    $('#last-update').text(formattedTime);
}

// Set active navigation item
function setActiveNavItem(activeLink) {
    const currentPath = window.location.pathname;
    
    $('.nav-link').removeClass('active');
    
    if (activeLink) {
        activeLink.addClass('active');
    } else {
        // Auto-detect based on current path
        $('.nav-link').each(function() {
            const href = $(this).attr('href');
            if (href === currentPath || (currentPath === '/' && href === '/')) {
                $(this).addClass('active');
            }
        });
    }
}

// Show loading state
function showLoadingState() {
    // Add loading indicators to data elements
    $('.sensor-value, .badge, .status-indicator').each(function() {
        if ($(this).text().trim() === '' || $(this).text().includes('--')) {
            $(this).html('<span class="loading"></span>');
        }
    });
}

// Utility functions
function formatTemperature(temp) {
    return temp ? temp.toFixed(1) + '°C' : '--°C';
}

function formatHumidity(humidity) {
    return humidity ? humidity.toFixed(1) + '%' : '--%';
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}

// Error handling
function handleError(error, context) {
    console.error(`Error in ${context}:`, error);
    showNotification(`Error: ${error.message || error}`, 'error');
}

// Generic notification function
function showNotification(message, type, duration = 3000) {
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';
    
    const icon = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-exclamation-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    }[type] || 'fas fa-info-circle';
    
    const notification = $(`
        <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
             style="top: 80px; right: 20px; z-index: 1050; min-width: 300px; max-width: 400px;">
            <i class="${icon} me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    
    $('body').append(notification);
    
    // Auto-remove after specified duration
    setTimeout(() => {
        notification.alert('close');
    }, duration);
}

// Confirmation dialog
function showConfirmDialog(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Format device status
function formatDeviceStatus(status, type) {
    const statusMap = {
        'fan': {
            true: { text: 'ON', class: 'bg-success' },
            false: { text: 'OFF', class: 'bg-danger' }
        },
        'door': {
            true: { text: 'LOCKED', class: 'bg-success' },
            false: { text: 'UNLOCKED', class: 'bg-danger' }
        },
        'garage': {
            true: { text: 'OPEN', class: 'bg-warning' },
            false: { text: 'CLOSED', class: 'bg-success' }
        },
        'gas': {
            true: { text: 'DETECTED', class: 'bg-danger' },
            false: { text: 'CLEAR', class: 'bg-success' }
        },
        'emergency': {
            true: { text: 'ACTIVE', class: 'bg-danger' },
            false: { text: 'NORMAL', class: 'bg-success' }
        },
        'face': {
            true: { text: 'RECOGNIZED', class: 'bg-success' },
            false: { text: 'NO FACE', class: 'bg-secondary' }
        }
    };
    
    const mapping = statusMap[type];
    if (mapping && mapping[status]) {
        return mapping[status];
    }
    
    return { text: status ? 'ON' : 'OFF', class: status ? 'bg-success' : 'bg-secondary' };
}

// Update motion sensor indicators
function updateMotionSensors(motionData) {
    if (!motionData) return;
    
    Object.keys(motionData).forEach(room => {
        const indicator = $(`#motion-${room}`);
        if (indicator.length) {
            indicator.removeClass('bg-success bg-secondary bg-danger')
                   .addClass(motionData[room] ? 'bg-success' : 'bg-secondary');
        }
    });
}

// Update light indicators
function updateLightIndicators(lightData) {
    if (!lightData) return;
    
    // This would need to be implemented based on the actual light data structure
    // For now, we'll use a placeholder implementation
    Object.keys(lightData).forEach(room => {
        const indicator = $(`#light-${room} .light-color`);
        if (indicator.length) {
            // Determine color based on light state
            let color = '#000'; // Default off
            if (lightData[room]) {
                // Assuming light data contains color information
                color = lightData[room].color || '#fff';
            }
            indicator.css('background-color', color);
        }
    });
}

// Cleanup function
function cleanup() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
    if (socket) {
        socket.disconnect();
    }
}

// Handle page unload
$(window).on('beforeunload', function() {
    cleanup();
});

// Handle visibility change (pause updates when tab is not visible)
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Page is hidden, reduce update frequency
        if (updateInterval) {
            clearInterval(updateInterval);
            updateInterval = setInterval(function() {
                if (socket && socket.connected) {
                    socket.emit('request_update');
                }
            }, 30000); // Update every 30 seconds when hidden
        }
    } else {
        // Page is visible, restore normal update frequency
        if (updateInterval) {
            clearInterval(updateInterval);
            startPeriodicUpdates();
        }
    }
});

// Export functions for use by other scripts
window.SmartHome = {
    updateSystemData: updateSystemData,
    showNotification: showNotification,
    formatDeviceStatus: formatDeviceStatus,
    updateMotionSensors: updateMotionSensors,
    updateLightIndicators: updateLightIndicators,
    systemData: systemData,
    connectionStatus: connectionStatus
}; 