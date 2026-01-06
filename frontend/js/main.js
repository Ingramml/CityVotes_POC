/**
 * CityVotes POC - Main JavaScript
 * Handles drag-and-drop file upload, form interactions, and chart utilities
 */

// Global utilities
const CityVotes = {
    // Chart color schemes for different cities
    colorSchemes: {
        santa_ana: {
            primary: '#1f4e79',
            secondary: '#f4b942',
            success: '#28a745',
            danger: '#dc3545'
        },
        pomona: {
            primary: '#2c5530',
            secondary: '#ffd700',
            success: '#28a745',
            danger: '#dc3545'
        },
        default: {
            primary: '#6c757d',
            secondary: '#e9ecef',
            success: '#28a745',
            danger: '#dc3545'
        }
    },

    // Get colors for a city
    getColors: function(cityKey) {
        return this.colorSchemes[cityKey] || this.colorSchemes.default;
    },

    // Format numbers with commas
    formatNumber: function(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },

    // Format percentage
    formatPercent: function(num) {
        return Math.round(num * 10) / 10 + '%';
    }
};

// Document ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🏛️ CityVotes POC - JavaScript Loaded');

    // Initialize drag-and-drop upload
    initDragAndDrop();

    // Initialize city selection
    initCitySelection();

    // Initialize tooltips
    initTooltips();

    // Auto-hide alerts after 5 seconds
    autoHideAlerts();
});

/**
 * Initialize drag-and-drop file upload
 */
function initDragAndDrop() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');

    if (!uploadZone || !fileInput) return;

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadZone.addEventListener(eventName, () => {
            uploadZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, () => {
            uploadZone.classList.remove('dragover');
        }, false);
    });

    // Handle dropped files
    uploadZone.addEventListener('drop', handleDrop, false);

    // Handle click to open file dialog
    uploadZone.addEventListener('click', () => {
        fileInput.click();
    });

    // Handle file input change
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

function handleFiles(files) {
    if (files.length === 0) return;

    const file = files[0];
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.json')) {
        showAlert('Please select a JSON file (.json)', 'error');
        return;
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
        showAlert('File size must be less than 10MB', 'error');
        return;
    }

    // Update file input
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    fileInput.files = dataTransfer.files;

    // Update upload zone text
    const uploadText = document.querySelector('.upload-text');
    if (uploadText) {
        uploadText.innerHTML = `
            <strong>File ready:</strong> ${file.name}<br>
            <small>Size: ${formatFileSize(file.size)}</small>
        `;
    }

    // Show upload button
    const uploadBtn = document.getElementById('uploadBtn');
    if (uploadBtn) {
        uploadBtn.style.display = 'inline-block';
        uploadBtn.disabled = false;
    }

    console.log('📁 File selected:', file.name);
}

/**
 * Initialize city selection
 */
function initCitySelection() {
    const cityOptions = document.querySelectorAll('.city-option');

    cityOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove selected class from all options
            cityOptions.forEach(opt => opt.classList.remove('selected'));

            // Add selected class to clicked option
            this.classList.add('selected');

            // Update radio button
            const radio = this.querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;
            }

            // Enable upload if file is also selected
            updateUploadButton();
        });
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Auto-hide alert messages after 5 seconds
 */
function autoHideAlerts() {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

/**
 * Update upload button state
 */
function updateUploadButton() {
    const fileInput = document.getElementById('fileInput');
    const cityInput = document.querySelector('input[name="city"]:checked');
    const uploadBtn = document.getElementById('uploadBtn');

    if (uploadBtn) {
        uploadBtn.disabled = !fileInput.files.length || !cityInput;
    }
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container');
    const alertDiv = document.createElement('div');

    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    alertContainer.insertBefore(alertDiv, alertContainer.firstChild);

    // Auto-hide after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

/**
 * Format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

/**
 * Chart utilities
 */
const ChartUtils = {
    // Create pie chart for vote outcomes
    createVoteOutcomeChart: function(canvasId, data, cityKey = 'default') {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        // Color mapping for each outcome type
        const outcomeColors = {
            'PASS': '#28a745',      // Green
            'FAIL': '#dc3545',      // Red
            'FLAG': '#fd7e14',      // Orange
            'CONTINUED': '#6c757d', // Gray
            'REMOVED': '#adb5bd',   // Light gray
            'TIE': '#ffc107'        // Yellow
        };

        // Filter out outcomes with 0 count
        const filteredOutcomes = Object.entries(data.outcomes)
            .filter(([key, val]) => val.count > 0);

        const labels = filteredOutcomes.map(([key]) => key);
        const values = filteredOutcomes.map(([key, val]) => val.count);
        const colors = filteredOutcomes.map(([key]) => outcomeColors[key] || '#6c757d');

        return new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const key = labels[context.dataIndex];
                                const outcome = data.outcomes[key];
                                return `${context.label}: ${outcome.count} (${outcome.percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    },

    // Create bar chart for member voting
    createMemberVotingChart: function(canvasId, memberData, cityKey = 'default') {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        const colors = CityVotes.getColors(cityKey);

        // Sort members by total votes
        const sortedMembers = Object.entries(memberData)
            .sort(([,a], [,b]) => b.total_votes - a.total_votes)
            .slice(0, 10); // Top 10 most active

        const labels = sortedMembers.map(([name]) => name);
        const ayeData = sortedMembers.map(([,data]) => data.vote_breakdown.Aye);
        const nayData = sortedMembers.map(([,data]) => data.vote_breakdown.Nay);

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Aye Votes',
                        data: ayeData,
                        backgroundColor: colors.success,
                        borderColor: colors.success,
                        borderWidth: 1
                    },
                    {
                        label: 'Nay Votes',
                        data: nayData,
                        backgroundColor: colors.danger,
                        borderColor: colors.danger,
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    },

    // Create comparison chart
    createComparisonChart: function(canvasId, comparisonData) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        const cities = Object.keys(comparisonData);
        const passRates = cities.map(city => {
            const data = comparisonData[city];
            const total = data.vote_summary.total_votes;
            const pass = data.vote_summary.outcomes.Pass?.count || 0;
            return total > 0 ? (pass / total) * 100 : 0;
        });

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: cities.map(city => comparisonData[city].display_name),
                datasets: [{
                    label: 'Pass Rate (%)',
                    data: passRates,
                    backgroundColor: cities.map(city => {
                        const colors = CityVotes.getColors(city);
                        return colors.primary;
                    }),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Pass Rate: ${context.parsed.y.toFixed(1)}%`;
                            }
                        }
                    }
                }
            }
        });
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CityVotes, ChartUtils };
}