// EpiPred - Main JavaScript Functions

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize file upload handler
    initFileUpload();
    
    // Initialize form validation
    initFormValidation();
    
    // Initialize sequence analysis
    initSequenceAnalysis();
});

// File Upload Functionality
function initFileUpload() {
    const fileInput = document.getElementById('sequence_file');
    const fileInfo = document.getElementById('file-info');
    
    if (fileInput && fileInfo) {
        fileInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                const file = e.target.files[0];
                const size = (file.size / 1024 / 1024).toFixed(2);
                const maxSize = 16; // MB
                
                if (file.size > maxSize * 1024 * 1024) {
                    showAlert('File size exceeds 16MB limit. Please choose a smaller file.', 'error');
                    e.target.value = '';
                    fileInfo.innerHTML = '';
                    return;
                }
                
                // Check file extension
                const allowedExtensions = ['txt', 'fasta', 'fa', 'fas'];
                const fileExtension = file.name.split('.').pop().toLowerCase();
                
                if (!allowedExtensions.includes(fileExtension)) {
                    showAlert('Invalid file format. Please upload a .txt, .fasta, .fa, or .fas file.', 'error');
                    e.target.value = '';
                    fileInfo.innerHTML = '';
                    return;
                }
                
                fileInfo.innerHTML = `<i class="fas fa-file me-1"></i>Selected: ${file.name} (${size} MB)`;
                fileInfo.className = 'mt-2 text-info';
                
                // Preview file content if small enough
                if (file.size < 1024 * 1024) { // 1MB
                    previewFile(file);
                }
            } else {
                fileInfo.innerHTML = '';
            }
        });
    }
}

// Preview uploaded file content
function previewFile(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const content = e.target.result;
        const lines = content.split('\n').slice(0, 10); // First 10 lines
        
        if (lines.some(line => line.startsWith('>'))) {
            showAlert('FASTA file detected. Preview looks good!', 'success');
        } else {
            showAlert('Warning: File may not be in FASTA format. Please check your file.', 'warning');
        }
    };
    reader.readAsText(file);
}

// Form Validation
function initFormValidation() {
    const form = document.getElementById('predictionForm');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            const sequenceText = document.getElementById('sequence_text').value.trim();
            const sequenceFile = document.getElementById('sequence_file').files.length > 0;
            
            // Check if at least one input method is provided
            if (!sequenceText && !sequenceFile) {
                e.preventDefault();
                showAlert('Please provide protein sequences either by pasting text or uploading a file.', 'error');
                return false;
            }
            
            // Validate sequence text if provided
            if (sequenceText) {
                const validation = validateFastaText(sequenceText);
                if (!validation.valid) {
                    e.preventDefault();
                    showAlert(validation.message, 'error');
                    return false;
                }
            }
            
            // Show loading state
            showLoadingState();
        });
    }
}

// Validate FASTA text format
function validateFastaText(text) {
    const lines = text.split('\n').filter(line => line.trim());
    
    if (lines.length === 0) {
        return { valid: false, message: 'Please enter some sequence data.' };
    }
    
    let hasHeader = false;
    let hasSequence = false;
    let sequenceCount = 0;
    let totalLength = 0;
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        if (line.startsWith('>')) {
            hasHeader = true;
            sequenceCount++;
            
            if (sequenceCount > 50) {
                return { valid: false, message: 'Maximum 50 sequences allowed per submission.' };
            }
        } else if (line.length > 0) {
            hasSequence = true;
            totalLength += line.length;
            
            // Check for invalid characters
            const validAA = /^[ACDEFGHIKLMNPQRSTVWY]+$/i;
            if (!validAA.test(line)) {
                return { valid: false, message: `Invalid amino acid characters found in sequence. Only standard amino acids are allowed.` };
            }
        }
    }
    
    if (!hasHeader) {
        return { valid: false, message: 'FASTA format requires header lines starting with ">". Please check your format.' };
    }
    
    if (!hasSequence) {
        return { valid: false, message: 'No sequence data found. Please provide amino acid sequences.' };
    }
    
    if (totalLength > 300000) {
        return { valid: false, message: 'Total sequence length exceeds 300,000 amino acids limit.' };
    }
    
    return { valid: true, message: 'Validation passed.' };
}

// Show loading state during form submission
function showLoadingState() {
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) {
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        submitBtn.disabled = true;
        
        // Add progress indicator
        const progressHtml = `
            <div class="mt-3 text-center" id="loadingProgress">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 text-muted">Analyzing sequences... This may take a few minutes.</p>
            </div>
        `;
        
        const form = document.getElementById('predictionForm');
        if (form) {
            form.insertAdjacentHTML('afterend', progressHtml);
        }
    }
}

// Sequence Analysis Functions
function initSequenceAnalysis() {
    // Real-time sequence statistics
    const sequenceTextarea = document.getElementById('sequence_text');
    if (sequenceTextarea) {
        sequenceTextarea.addEventListener('input', function(e) {
            updateSequenceStats(e.target.value);
        });
    }
}

// Update sequence statistics in real-time
function updateSequenceStats(text) {
    const lines = text.split('\n').filter(line => line.trim());
    let sequenceCount = 0;
    let totalLength = 0;
    
    for (const line of lines) {
        if (line.trim().startsWith('>')) {
            sequenceCount++;
        } else if (line.trim().length > 0) {
            totalLength += line.trim().length;
        }
    }
    
    // Update or create stats display
    let statsDiv = document.getElementById('sequence-stats');
    if (!statsDiv && (sequenceCount > 0 || totalLength > 0)) {
        statsDiv = document.createElement('div');
        statsDiv.id = 'sequence-stats';
        statsDiv.className = 'mt-2 p-2 bg-light rounded';
        
        const textarea = document.getElementById('sequence_text');
        textarea.parentNode.insertBefore(statsDiv, textarea.nextSibling);
    }
    
    if (statsDiv) {
        if (sequenceCount > 0 || totalLength > 0) {
            const warningClass = sequenceCount > 50 || totalLength > 300000 ? 'text-danger' : 'text-info';
            statsDiv.innerHTML = `
                <small class="${warningClass}">
                    <i class="fas fa-info-circle me-1"></i>
                    Sequences: ${sequenceCount}/50 | Total length: ${totalLength.toLocaleString()}/300,000 amino acids
                </small>
            `;
            statsDiv.style.display = 'block';
        } else {
            statsDiv.style.display = 'none';
        }
    }
}

// Utility Functions
function showAlert(message, type = 'info') {
    const alertClass = type === 'error' ? 'alert-danger' : 
                      type === 'success' ? 'alert-success' : 
                      type === 'warning' ? 'alert-warning' : 'alert-info';
    
    const iconClass = type === 'error' ? 'fa-exclamation-triangle' : 
                      type === 'success' ? 'fa-check-circle' : 
                      type === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle';
    
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show mt-3" role="alert">
            <i class="fas ${iconClass} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Insert at the top of the main container
    const container = document.querySelector('.container.my-4');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto-dismiss after 5 seconds for success messages
        if (type === 'success') {
            setTimeout(() => {
                const alert = container.querySelector('.alert');
                if (alert) {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }
            }, 5000);
        }
    }
}

// Copy text to clipboard
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showAlert('Copied to clipboard!', 'success');
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

// Fallback copy function for older browsers
function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showAlert('Copied to clipboard!', 'success');
    } catch (err) {
        showAlert('Failed to copy to clipboard. Please copy manually.', 'error');
    }
    
    document.body.removeChild(textArea);
}

// Format confidence score for display
function formatConfidence(confidence) {
    return (confidence * 100).toFixed(1) + '%';
}

// Format position range for display
function formatPositionRange(range) {
    return range.replace('-', ' - ');
}

// Smooth scroll to element
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Export functions for global access
window.EpiPred = {
    showAlert,
    copyToClipboard,
    formatConfidence,
    formatPositionRange,
    scrollToElement,
    validateFastaText
};
