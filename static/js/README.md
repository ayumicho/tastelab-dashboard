# JavaScript Directory

This directory contains all JavaScript files for the TasteLab Dashboard, providing client-side functionality, interactive components, and dynamic data visualization.

## Overview

The JavaScript architecture follows a modular approach with ES6+ syntax, organizing code into reusable components and page-specific scripts for maintainability and scalability.

## File Structure

```
js/
├── main.js                    # Main application entry point
├── config.js                  # Configuration and constants
├── components/                # Reusable UI components
│   ├── charts.js              # Chart initialization and updates
│   ├── modals.js              # Modal dialog handlers
│   ├── forms.js               # Form validation and submission
│   ├── notifications.js       # Toast/alert notifications
│   └── table.js               # Data table functionality
├── pages/                     # Page-specific scripts
│   ├── home.js                # Dashboard home interactions
│   ├── experiments.js         # Experiment management
│   ├── profile.js             # User profile features
│   └── auth.js                # Login/signup validation
├── utils/                     # Utility functions
│   ├── api.js                 # API request helpers
│   ├── validators.js          # Input validation functions
│   ├── formatters.js          # Data formatting utilities
│   └── helpers.js             # General helper functions
└── vendor/                    # Third-party libraries
    ├── chart.min.js           # Chart.js library
    └── datatables.min.js      # DataTables library
```

## Core Files

### `main.js`
Main application entry point that initializes core functionality:

```javascript
// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    initializeCharts();
});

function initializeApp() {
    console.log('TasteLab Dashboard initialized');
    // Core initialization logic
}
```

**Include in templates:**
```html
<script src="{{ url_for('static', filename='js/main.js') }}" defer></script>
```

### `config.js`
Application configuration and constants:

```javascript
const CONFIG = {
    API_BASE_URL: '/api',
    CHART_COLORS: {
        primary: '#2563eb',
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444'
    },
    ANIMATION_DURATION: 300,
    MAX_UPLOAD_SIZE: 10485760, // 10MB
    SUPPORTED_FILE_TYPES: ['jpg', 'jpeg', 'png', 'pdf']
};
```

## Component Scripts

### `charts.js`
Chart initialization and data visualization:

```javascript
/**
 * Initialize emotion analysis chart
 * @param {string} elementId - Canvas element ID
 * @param {Object} data - Chart data
 */
function initEmotionChart(elementId, data) {
    const ctx = document.getElementById(elementId).getContext('2d');
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Emotion Intensity',
                data: data.values,
                backgroundColor: CONFIG.CHART_COLORS.primary
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
    return chart;
}

/**
 * Update chart with new data
 * @param {Chart} chart - Chart instance
 * @param {Object} newData - Updated data
 */
function updateChart(chart, newData) {
    chart.data.datasets[0].data = newData.values;
    chart.update();
}
```

### `forms.js`
Form validation and submission handling:

```javascript
/**
 * Validate experiment form
 * @param {HTMLFormElement} form - Form element
 * @returns {boolean} Validation result
 */
function validateExperimentForm(form) {
    const name = form.querySelector('#experiment-name').value;
    const participants = form.querySelector('#participants').value;
    
    if (name.trim() === '') {
        showNotification('Experiment name is required', 'error');
        return false;
    }
    
    if (participants < 1) {
        showNotification('At least one participant is required', 'error');
        return false;
    }
    
    return true;
}

/**
 * Submit form via AJAX
 * @param {HTMLFormElement} form - Form element
 * @param {string} url - Submission URL
 */
async function submitForm(form, url) {
    const formData = new FormData(form);
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification('Form submitted successfully', 'success');
            return result;
        } else {
            throw new Error('Submission failed');
        }
    } catch (error) {
        showNotification('Error submitting form', 'error');
        console.error(error);
    }
}
```

### `modals.js`
Modal dialog management:

```javascript
/**
 * Show modal dialog
 * @param {string} modalId - Modal element ID
 */
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.style.display = 'block';
    modal.classList.add('show');
    document.body.classList.add('modal-open');
}

/**
 * Hide modal dialog
 * @param {string} modalId - Modal element ID
 */
function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.style.display = 'none';
    modal.classList.remove('show');
    document.body.classList.remove('modal-open');
}

/**
 * Confirm action with modal
 * @param {string} message - Confirmation message
 * @returns {Promise<boolean>} User confirmation
 */
function confirmAction(message) {
    return new Promise((resolve) => {
        const modal = document.getElementById('confirm-modal');
        const messageEl = modal.querySelector('.modal-message');
        const confirmBtn = modal.querySelector('.confirm-btn');
        const cancelBtn = modal.querySelector('.cancel-btn');
        
        messageEl.textContent = message;
        showModal('confirm-modal');
        
        confirmBtn.onclick = () => {
            hideModal('confirm-modal');
            resolve(true);
        };
        
        cancelBtn.onclick = () => {
            hideModal('confirm-modal');
            resolve(false);
        };
    });
}
```

### `notifications.js`
Toast notifications and alerts:

```javascript
/**
 * Show notification message
 * @param {string} message - Notification text
 * @param {string} type - Notification type (success, error, warning, info)
 * @param {number} duration - Display duration in ms
 */
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Auto-hide
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, duration);
}
```

## Page-Specific Scripts

### `experiments.js`
Experiment management functionality:

```javascript
// Handle experiment deletion
document.querySelectorAll('.delete-experiment').forEach(button => {
    button.addEventListener('click', async function() {
        const experimentId = this.dataset.experimentId;
        const confirmed = await confirmAction('Delete this experiment?');
        
        if (confirmed) {
            await deleteExperiment(experimentId);
        }
    });
});

// Load experiment details
async function loadExperimentDetails(experimentId) {
    try {
        const response = await fetch(`/api/experiments/${experimentId}`);
        const data = await response.json();
        
        updateExperimentView(data);
        initEmotionChart('emotion-chart', data.emotions);
    } catch (error) {
        showNotification('Failed to load experiment', 'error');
    }
}

// Export experiment data
function exportExperimentData(experimentId) {
    window.location.href = `/api/experiments/${experimentId}/export`;
}
```

### `auth.js`
Authentication page validation:

```javascript
// Login form validation
const loginForm = document.getElementById('login-form');
loginForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    if (!validateEmail(email)) {
        showNotification('Invalid email format', 'error');
        return;
    }
    
    if (password.length < 8) {
        showNotification('Password must be at least 8 characters', 'error');
        return;
    }
    
    this.submit();
});

// Password strength indicator
const passwordInput = document.getElementById('password');
passwordInput.addEventListener('input', function() {
    const strength = calculatePasswordStrength(this.value);
    updatePasswordStrengthIndicator(strength);
});
```

## Utility Functions

### `api.js`
API request helpers:

```javascript
/**
 * Make GET request
 * @param {string} endpoint - API endpoint
 * @returns {Promise<Object>} Response data
 */
async function get(endpoint) {
    const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

/**
 * Make POST request
 * @param {string} endpoint - API endpoint
 * @param {Object} data - Request body
 * @returns {Promise<Object>} Response data
 */
async function post(endpoint, data) {
    const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}
```

### `validators.js`
Input validation functions:

```javascript
/**
 * Validate email format
 * @param {string} email - Email address
 * @returns {boolean} Validation result
 */
function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * Validate file size
 * @param {File} file - File object
 * @param {number} maxSize - Maximum size in bytes
 * @returns {boolean} Validation result
 */
function validateFileSize(file, maxSize = CONFIG.MAX_UPLOAD_SIZE) {
    return file.size <= maxSize;
}

/**
 * Validate file type
 * @param {File} file - File object
 * @param {Array<string>} allowedTypes - Allowed file extensions
 * @returns {boolean} Validation result
 */
function validateFileType(file, allowedTypes = CONFIG.SUPPORTED_FILE_TYPES) {
    const extension = file.name.split('.').pop().toLowerCase();
    return allowedTypes.includes(extension);
}
```

### `formatters.js`
Data formatting utilities:

```javascript
/**
 * Format date to readable string
 * @param {Date|string} date - Date object or string
 * @returns {string} Formatted date
 */
function formatDate(date) {
    const d = new Date(date);
    return d.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * Format number with commas
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
function formatNumber(num) {
    return num.toLocaleString('en-US');
}

/**
 * Format file size
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
```

## Event Handling

### Event Delegation

Use event delegation for dynamic elements:

```javascript
// Instead of attaching handlers to each element
document.addEventListener('click', function(e) {
    if (e.target.matches('.delete-btn')) {
        handleDelete(e.target);
    }
    
    if (e.target.matches('.edit-btn')) {
        handleEdit(e.target);
    }
});
```

### Debouncing

Debounce expensive operations:

```javascript
/**
 * Debounce function execution
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in ms
 * @returns {Function} Debounced function
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Usage
const searchInput = document.getElementById('search');
searchInput.addEventListener('input', debounce(function(e) {
    performSearch(e.target.value);
}, 500));
```

## Best Practices

### Code Organization

1. **Use ES6+ syntax** - const/let, arrow functions, template literals
2. **Write modular code** - one function = one responsibility
3. **Add JSDoc comments** for complex functions
4. **Use meaningful variable names** - descriptive and self-documenting
5. **Keep functions small** - aim for < 20 lines

### Performance

1. **Minimize DOM manipulation** - batch updates when possible
2. **Use event delegation** for dynamic elements
3. **Debounce expensive operations** - searches, API calls
4. **Lazy load resources** - load scripts only when needed
5. **Cache DOM queries** - store frequently used elements

### Error Handling

1. **Use try-catch** for async operations
2. **Provide user feedback** on errors
3. **Log errors to console** for debugging
4. **Handle network failures gracefully**
5. **Validate input before processing**

### Security

1. **Sanitize user input** before DOM insertion
2. **Use CSRF tokens** for form submissions
3. **Validate data** on both client and server
4. **Avoid eval()** and similar dangerous functions
5. **Use HTTPS** for all API requests

## Common Patterns

### Loading State

```javascript
function showLoading(element) {
    element.innerHTML = '<div class="spinner">Loading...</div>';
    element.classList.add('loading');
}

function hideLoading(element) {
    element.classList.remove('loading');
}

// Usage
async function loadData() {
    const container = document.getElementById('data-container');
    showLoading(container);
    
    try {
        const data = await fetch('/api/data');
        container.innerHTML = renderData(data);
    } finally {
        hideLoading(container);
    }
}
```

### File Upload with Progress

```javascript
function uploadFile(file, endpoint) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        const formData = new FormData();
        formData.append('file', file);
        
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percent = (e.loaded / e.total) * 100;
                updateProgressBar(percent);
            }
        });
        
        xhr.addEventListener('load', () => {
            if (xhr.status === 200) {
                resolve(JSON.parse(xhr.responseText));
            } else {
                reject(new Error('Upload failed'));
            }
        });
        
        xhr.open('POST', endpoint);
        xhr.send(formData);
    });
}
```

## Browser Compatibility

JavaScript is compatible with:
- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

Use transpilers (Babel) for wider compatibility if needed.

## Adding New Scripts

When adding new JavaScript:

1. **Choose appropriate location** (component, page, or utility)
2. **Follow naming conventions** (camelCase for variables/functions)
3. **Add JSDoc comments** for public functions
4. **Test across browsers** and devices
5. **Handle errors gracefully**
6. **Update this README** if adding new files
7. **Consider performance impact**

## Troubleshooting

### Script not loading
- Check script path in template
- Verify file exists in js directory
- Check browser console for 404 errors
- Ensure script tag has correct `defer` or `async` attribute

### Function not working
- Check browser console for errors
- Verify function is called after DOM loads
- Check for typos in function names
- Ensure dependencies are loaded first

### Performance issues
- Check for memory leaks
- Optimize loops and DOM queries
- Use browser profiling tools
- Reduce API call frequency

---

**Last Updated:** December 2025