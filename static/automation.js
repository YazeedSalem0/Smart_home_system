// Smart Home Automation Rules UI
document.addEventListener('DOMContentLoaded', function() {
    // Load all rules
    loadRules();
    
    // Setup event listeners
    document.getElementById('add-rule-btn').addEventListener('click', function() {
        resetRuleForm();
        $('#ruleModal').modal('show');
    });
    
    document.getElementById('reset-rules-btn').addEventListener('click', function() {
        if (confirm('Are you sure you want to reset all rules to default? This cannot be undone.')) {
            resetRules();
        }
    });
    
    document.getElementById('save-rule-btn').addEventListener('click', saveRule);
    
    // Setup dynamic form elements
    setupDynamicForm();
});

// Load all rules from the server
function loadRules() {
    fetch('/api/rules')
        .then(response => response.json())
        .then(rules => {
            displayRules(rules);
        })
        .catch(error => {
            console.error('Error loading rules:', error);
            document.getElementById('rules-container').innerHTML = 
                '<div class="alert alert-danger">Error loading rules. Please try again.</div>';
        });
}

// Display rules in the UI
function displayRules(rules) {
    const container = document.getElementById('rules-container');
    
    if (rules.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No rules defined. Click "Add New Rule" to create one.</div>';
        return;
    }
    
    let html = '';
    rules.forEach(rule => {
        const activeClass = rule.active ? 'success' : 'secondary';
        const activeText = rule.active ? 'Active' : 'Inactive';
        const conditionText = formatCondition(rule.condition);
        const actionText = formatAction(rule.action);
        
        html += `
            <div class="card mb-3 rule-card" data-id="${rule.id}">
                <div class="card-header bg-${activeClass} text-white d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">${rule.name}</h5>
                    <div>
                        <span class="badge badge-light">${activeText}</span>
                    </div>
                </div>
                <div class="card-body">
                    <p><strong>If:</strong> ${conditionText}</p>
                    <p><strong>Then:</strong> ${actionText}</p>
                    <div class="btn-group" role="group">
                        <button class="btn btn-sm btn-primary edit-rule" data-id="${rule.id}">Edit</button>
                        <button class="btn btn-sm btn-${rule.active ? 'warning' : 'success'} toggle-rule" data-id="${rule.id}">
                            ${rule.active ? 'Disable' : 'Enable'}
                        </button>
                        <button class="btn btn-sm btn-danger delete-rule" data-id="${rule.id}">Delete</button>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // Add event listeners to buttons
    document.querySelectorAll('.edit-rule').forEach(button => {
        button.addEventListener('click', function() {
            editRule(this.getAttribute('data-id'));
        });
    });
    
    document.querySelectorAll('.toggle-rule').forEach(button => {
        button.addEventListener('click', function() {
            const ruleId = this.getAttribute('data-id');
            const active = this.textContent.trim() === 'Enable';
            toggleRule(ruleId, active);
        });
    });
    
    document.querySelectorAll('.delete-rule').forEach(button => {
        button.addEventListener('click', function() {
            const ruleId = this.getAttribute('data-id');
            deleteRule(ruleId);
        });
    });
}

// Format condition for display
function formatCondition(condition) {
    let text = '';
    
    switch (condition.type) {
        case 'temperature':
            text = `Temperature ${formatOperator(condition.operator)} ${condition.value}°C`;
            break;
        case 'humidity':
            text = `Humidity ${formatOperator(condition.operator)} ${condition.value}%`;
            break;
        case 'motion':
            const location = condition.location === 'any' ? 'any room' : formatLocation(condition.location);
            text = `Motion detected in ${location} ${formatOperator(condition.operator)} ${condition.value ? 'Yes' : 'No'}`;
            break;
        case 'gas':
            text = `Gas leak detected ${formatOperator(condition.operator)} ${condition.value ? 'Yes' : 'No'}`;
            break;
        case 'time':
            text = `Time ${formatOperator(condition.operator)} ${condition.value}`;
            break;
        default:
            text = 'Unknown condition';
    }
    
    return text;
}

// Format action for display
function formatAction(action) {
    let text = '';
    
    switch (action.type) {
        case 'fan':
            text = `${action.command === 'on' ? 'Turn on' : action.command === 'off' ? 'Turn off' : 'Toggle'} fans`;
            break;
        case 'light':
            const location = action.location === 'all' ? 'all rooms' : 
                            action.location === 'same' ? 'the same room' : 
                            formatLocation(action.location);
            text = `${action.command === 'on' ? 'Turn on' : action.command === 'off' ? 'Turn off' : 'Set to auto mode'} lights in ${location}`;
            break;
        case 'door':
            text = `${action.command === 'lock' ? 'Lock' : action.command === 'unlock' ? 'Unlock' : 'Set to auto mode'} door`;
            break;
        case 'alert':
            if (action.command === 'emergency') {
                text = 'Trigger emergency alert';
            } else if (action.command === 'sound') {
                text = `Play ${action.alert_type} sound alert`;
            } else {
                text = 'Unknown alert action';
            }
            break;
        default:
            text = 'Unknown action';
    }
    
    return text;
}

// Format operator for display
function formatOperator(operator) {
    switch (operator) {
        case '==': return 'equals';
        case '!=': return 'does not equal';
        case '>': return 'is greater than';
        case '<': return 'is less than';
        case '>=': return 'is greater than or equal to';
        case '<=': return 'is less than or equal to';
        default: return operator;
    }
}

// Format location for display
function formatLocation(location) {
    return location.replace(/([A-Z])/g, ' $1').trim();
}

// Edit an existing rule
function editRule(ruleId) {
    fetch(`/api/rules/${ruleId}`)
        .then(response => response.json())
        .then(rule => {
            if (rule.error) {
                alert('Error: ' + rule.error);
                return;
            }
            
            // Fill the form with rule data
            document.getElementById('rule-id').value = rule.id;
            document.getElementById('rule-name').value = rule.name;
            
            // Set condition fields
            document.getElementById('condition-type').value = rule.condition.type;
            updateConditionFields();
            
            if (rule.condition.type === 'motion' && rule.condition.location) {
                document.getElementById('condition-location').value = rule.condition.location;
            }
            
            document.getElementById('condition-operator').value = rule.condition.operator;
            document.getElementById('condition-value').value = rule.condition.value;
            
            // Set action fields
            document.getElementById('action-type').value = rule.action.type;
            updateActionFields();
            
            if (rule.action.type === 'light' && rule.action.location) {
                document.getElementById('action-location').value = rule.action.location;
            }
            
            document.getElementById('action-command').value = rule.action.command;
            
            if (rule.action.type === 'alert' && rule.action.command === 'sound' && rule.action.alert_type) {
                document.getElementById('alert-type').value = rule.action.alert_type;
            }
            
            // Update modal title
            document.getElementById('ruleModalLabel').textContent = 'Edit Rule';
            
            // Show modal
            $('#ruleModal').modal('show');
        })
        .catch(error => {
            console.error('Error loading rule:', error);
            alert('Failed to load rule details. Please try again.');
        });
}

// Save rule (create new or update existing)
function saveRule() {
    // Validate form
    const form = document.getElementById('rule-form');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    // Get form data
    const ruleId = document.getElementById('rule-id').value;
    const ruleName = document.getElementById('rule-name').value;
    
    // Build condition object
    const conditionType = document.getElementById('condition-type').value;
    const conditionOperator = document.getElementById('condition-operator').value;
    const conditionValue = document.getElementById('condition-value').value;
    
    let condition = {
        type: conditionType,
        operator: conditionOperator
    };
    
    // Handle different value types
    if (conditionType === 'temperature' || conditionType === 'humidity') {
        condition.value = parseFloat(conditionValue);
    } else if (conditionType === 'motion' || conditionType === 'gas') {
        condition.value = conditionValue === 'true';
    } else {
        condition.value = conditionValue;
    }
    
    // Add location for motion condition
    if (conditionType === 'motion') {
        condition.location = document.getElementById('condition-location').value;
    }
    
    // Build action object
    const actionType = document.getElementById('action-type').value;
    const actionCommand = document.getElementById('action-command').value;
    
    let action = {
        type: actionType,
        command: actionCommand
    };
    
    // Add location for light action
    if (actionType === 'light') {
        action.location = document.getElementById('action-location').value;
    }
    
    // Add alert type for sound alerts
    if (actionType === 'alert' && actionCommand === 'sound') {
        action.alert_type = document.getElementById('alert-type').value;
    }
    
    // Build complete rule object
    const rule = {
        name: ruleName,
        condition: condition,
        action: action,
        active: true
    };
    
    // Create new rule or update existing one
    const url = ruleId ? `/api/rules/${ruleId}` : '/api/rules';
    const method = ruleId ? 'PUT' : 'POST';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(rule)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        // Close modal and reload rules
        $('#ruleModal').modal('hide');
        loadRules();
    })
    .catch(error => {
        console.error('Error saving rule:', error);
        alert('Failed to save rule. Please try again.');
    });
}

// Toggle rule active state
function toggleRule(ruleId, active) {
    fetch(`/api/rules/${ruleId}/toggle`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ active: active })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        // Reload rules
        loadRules();
    })
    .catch(error => {
        console.error('Error toggling rule:', error);
        alert('Failed to toggle rule. Please try again.');
    });
}

// Delete a rule
function deleteRule(ruleId) {
    if (!confirm('Are you sure you want to delete this rule?')) {
        return;
    }
    
    fetch(`/api/rules/${ruleId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        // Reload rules
        loadRules();
    })
    .catch(error => {
        console.error('Error deleting rule:', error);
        alert('Failed to delete rule. Please try again.');
    });
}

// Reset all rules to default
function resetRules() {
    fetch('/api/rules/reset', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        // Reload rules
        loadRules();
    })
    .catch(error => {
        console.error('Error resetting rules:', error);
        alert('Failed to reset rules. Please try again.');
    });
}

// Reset the rule form
function resetRuleForm() {
    document.getElementById('rule-form').reset();
    document.getElementById('rule-id').value = '';
    document.getElementById('ruleModalLabel').textContent = 'Add New Rule';
    
    // Reset dynamic fields
    updateConditionFields();
    updateActionFields();
}

// Setup dynamic form behavior
function setupDynamicForm() {
    // Condition type changes
    document.getElementById('condition-type').addEventListener('change', updateConditionFields);
    
    // Action type changes
    document.getElementById('action-type').addEventListener('change', updateActionFields);
}

// Update condition fields based on selected type
function updateConditionFields() {
    const conditionType = document.getElementById('condition-type').value;
    const locationField = document.getElementById('location-field');
    const valueField = document.getElementById('condition-value');
    const valueHelp = document.getElementById('value-help');
    
    // Reset value field
    valueField.type = 'text';
    valueField.value = '';
    
    // Show/hide and configure fields based on condition type
    if (conditionType === 'motion') {
        locationField.style.display = 'block';
        valueField.type = 'select';
        
        // Replace input with select for boolean values
        let selectHTML = `
            <select class="form-control" id="condition-value" required>
                <option value="true">Yes (Detected)</option>
                <option value="false">No (Not Detected)</option>
            </select>
        `;
        
        // Replace input with select
        const valueContainer = valueField.parentElement;
        valueContainer.innerHTML = selectHTML + `<small class="form-text text-muted" id="value-help">
            Whether motion is detected or not
        </small>`;
        
    } else if (conditionType === 'gas') {
        locationField.style.display = 'none';
        valueField.type = 'select';
        
        // Replace input with select for boolean values
        let selectHTML = `
            <select class="form-control" id="condition-value" required>
                <option value="true">Yes (Detected)</option>
                <option value="false">No (Not Detected)</option>
            </select>
        `;
        
        // Replace input with select
        const valueContainer = valueField.parentElement;
        valueContainer.innerHTML = selectHTML + `<small class="form-text text-muted" id="value-help">
            Whether gas is detected or not
        </small>`;
        
    } else if (conditionType === 'temperature') {
        locationField.style.display = 'none';
        valueField.type = 'number';
        valueField.min = '0';
        valueField.max = '50';
        valueField.step = '0.1';
        valueHelp.textContent = 'Temperature value in °C';
        
    } else if (conditionType === 'humidity') {
        locationField.style.display = 'none';
        valueField.type = 'number';
        valueField.min = '0';
        valueField.max = '100';
        valueField.step = '0.1';
        valueHelp.textContent = 'Humidity value in %';
        
    } else if (conditionType === 'time') {
        locationField.style.display = 'none';
        valueField.type = 'time';
        valueHelp.textContent = 'Time in 24-hour format (HH:MM)';
        
    } else {
        locationField.style.display = 'none';
        valueHelp.textContent = '';
    }
}

// Update action fields based on selected type
function updateActionFields() {
    const actionType = document.getElementById('action-type').value;
    const locationField = document.getElementById('action-location-field');
    const commandSelect = document.getElementById('action-command');
    const alertTypeField = document.getElementById('alert-type-field');
    
    // Reset command options
    commandSelect.innerHTML = '<option value="">Select Command</option>';
    
    // Show/hide and configure fields based on action type
    if (actionType === 'fan') {
        locationField.style.display = 'none';
        alertTypeField.style.display = 'none';
        
        // Add command options
        commandSelect.innerHTML += `
            <option value="on">Turn On</option>
            <option value="off">Turn Off</option>
            <option value="toggle">Toggle</option>
        `;
        
    } else if (actionType === 'light') {
        locationField.style.display = 'block';
        alertTypeField.style.display = 'none';
        
        // Add command options
        commandSelect.innerHTML += `
            <option value="on">Turn On</option>
            <option value="off">Turn Off</option>
            <option value="auto">Auto (Motion Based)</option>
        `;
        
    } else if (actionType === 'door') {
        locationField.style.display = 'none';
        alertTypeField.style.display = 'none';
        
        // Add command options
        commandSelect.innerHTML += `
            <option value="lock">Lock</option>
            <option value="unlock">Unlock</option>
            <option value="auto">Auto (Face Recognition)</option>
        `;
        
    } else if (actionType === 'alert') {
        locationField.style.display = 'none';
        
        // Add command options
        commandSelect.innerHTML += `
            <option value="emergency">Emergency Alert</option>
            <option value="sound">Play Sound</option>
        `;
        
        // Show alert type field for sound action
        commandSelect.addEventListener('change', function() {
            alertTypeField.style.display = this.value === 'sound' ? 'block' : 'none';
        });
        
    } else {
        locationField.style.display = 'none';
        alertTypeField.style.display = 'none';
    }
}

// Function to populate action commands based on type
function updateActionCommands() {
    const actionType = document.getElementById('action-type').value;
    const actionCommand = document.getElementById('action-command');
    const actionLocationField = document.getElementById('action-location-field');
    const alertTypeField = document.getElementById('alert-type-field');
    
    // Clear previous options
    actionCommand.innerHTML = '<option value="">Select Command</option>';
    
    // Hide additional fields by default
    actionLocationField.style.display = 'none';
    alertTypeField.style.display = 'none';
    
    // Add commands based on action type
    if (actionType === 'fan') {
        actionCommand.innerHTML += `
            <option value="on">Turn On</option>
            <option value="off">Turn Off</option>
            <option value="toggle">Toggle</option>
            <option value="auto">Auto (Temperature Control)</option>
        `;
    } else if (actionType === 'light') {
        actionCommand.innerHTML += `
            <option value="on">Turn On</option>
            <option value="off">Turn Off</option>
            <option value="auto">Auto (Motion Control)</option>
        `;
        actionLocationField.style.display = 'block';
    } else if (actionType === 'door') {
        actionCommand.innerHTML += `
            <option value="lock">Lock</option>
            <option value="unlock">Unlock</option>
            <option value="auto">Auto Control</option>
        `;
    } else if (actionType === 'garage') {
        actionCommand.innerHTML += `
            <option value="open">Open</option>
            <option value="close">Close</option>
            <option value="auto">Auto Control</option>
        `;
    } else if (actionType === 'alert') {
        actionCommand.innerHTML += `
            <option value="emergency">Emergency Alert</option>
            <option value="sound">Sound Alert</option>
        `;
    }
    
    // Show alert type field if action is sound alert
    if (actionType === 'alert') {
        actionCommand.addEventListener('change', function() {
            if (this.value === 'sound') {
                alertTypeField.style.display = 'block';
            } else {
                alertTypeField.style.display = 'none';
            }
        });
    }
}

// Populate form fields from rule data
function populateForm(rule) {
    document.getElementById('rule-id').value = rule.id;
    document.getElementById('rule-name').value = rule.name;
    document.getElementById('condition-type').value = rule.condition.type;
    document.getElementById('condition-operator').value = rule.condition.operator;
    
    // Handle condition value based on type
    if (rule.condition.type === 'temperature' || rule.condition.type === 'humidity') {
        document.getElementById('condition-value').value = rule.condition.value;
    } else if (rule.condition.type === 'motion' || rule.condition.type === 'gas') {
        document.getElementById('condition-value').value = rule.condition.value.toString();
    } else if (rule.condition.type === 'time') {
        document.getElementById('condition-value').value = rule.condition.value;
    }
    
    // Handle location for motion condition
    if (rule.condition.type === 'motion' && rule.condition.location) {
        document.getElementById('condition-location').value = rule.condition.location;
        document.getElementById('location-field').style.display = 'block';
    }
    
    // Trigger condition type change event to update UI
    const conditionTypeEvent = new Event('change');
    document.getElementById('condition-type').dispatchEvent(conditionTypeEvent);
    
    // Set action type and update UI
    document.getElementById('action-type').value = rule.action.type;
    const actionTypeEvent = new Event('change');
    document.getElementById('action-type').dispatchEvent(actionTypeEvent);
    
    // Set action command
    document.getElementById('action-command').value = rule.action.command;
    
    // Set location for light action
    if (rule.action.type === 'light' && rule.action.location) {
        document.getElementById('action-location').value = rule.action.location;
    }
    
    // Set alert type for sound alert
    if (rule.action.type === 'alert' && rule.action.command === 'sound' && rule.action.alert_type) {
        document.getElementById('alert-type').value = rule.action.alert_type;
        document.getElementById('alert-type-field').style.display = 'block';
    }
} 