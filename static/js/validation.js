/**
 * Room Dekho - Strict Form Validation & Input Sanitization
 */

document.addEventListener('DOMContentLoaded', () => {
    initFormValidation();
    
    // Set minimum date for available_from to today
    const availableFromInput = document.getElementById('p_available_from');
    if (availableFromInput) {
        const today = new Date().toISOString().split('T')[0];
        availableFromInput.min = today;
    }
});

/**
 * Global password visibility toggle helper
 */
window.togglePasswordVisibility = function(inputId, btn) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    if (input.type === 'password') {
        input.type = 'text';
        btn.innerHTML = '<i data-lucide="eye-off" style="width: 16px; height: 16px;"></i>';
    } else {
        input.type = 'password';
        btn.innerHTML = '<i data-lucide="eye" style="width: 16px; height: 16px;"></i>';
    }
    
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
};

function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        const submitBtn = form.querySelector('button[type="submit"]');
        
        // Initial validation check to disable button
        checkFormValidity(form, inputs, submitBtn);
        
        inputs.forEach(input => {
            // Apply sanitization on input
            input.addEventListener('input', () => {
                sanitizeInputElement(input);
                validateInputElement(input);
                checkFormValidity(form, inputs, submitBtn);
            });
            
            // Apply validation on blur
            input.addEventListener('blur', () => {
                validateInputElement(input);
                checkFormValidity(form, inputs, submitBtn);
            });
            
            // Special handler for date inputs to trigger validation on change
            if (input.type === 'date' || input.tagName === 'SELECT') {
                input.addEventListener('change', () => {
                    validateInputElement(input);
                    checkFormValidity(form, inputs, submitBtn);
                });
            }
        });
    });
}

/**
 * 1. Input Sanitization
 */
function sanitizeInputElement(input) {
    let val = input.value;
    
    // Skip sanitization for file inputs and date inputs
    if (input.type === 'file' || input.type === 'date') {
        return;
    }
    
    // A. Remove Emojis from all input fields
    val = val.replace(/[\uE000-\uF8FF]|\uD83C[\uDC00-\uDFFF]|\uD83D[\uDC00-\uDFFF]|[\u2011-\u26FF]|\uD83E[\uDD10-\uDDFF]/g, '');
    
    // B. Strip HTML and script tags to prevent XSS
    val = val.replace(/<[^>]*>/g, '');
    
    // C. Prevent multiple consecutive spaces
    val = val.replace(/\s{2,}/g, ' ');
    
    // D. Name Field Specifics (only letters and spaces, auto-capitalize words)
    if (input.id === 'name') {
        val = val.replace(/[^A-Za-z\s]/g, '');
        val = capitalizeWords(val);
    }
    
    // E. Phone Number Specifics (only digits, max 10)
    if (input.id === 'mobile') {
        val = val.replace(/\D/g, '').slice(0, 10);
    }
    
    // F. OTP Specifics (only digits, max 6)
    if (input.id === 'otpCode') {
        val = val.replace(/\D/g, '').slice(0, 6);
    }
    
    // G. Email Specifics (convert to lowercase, remove spaces)
    if (input.type === 'email') {
        val = val.trim().toLowerCase();
    }
    
    // H. Price / Rent Specifics (only digits)
    if (input.id === 'p_price') {
        if (input.type === 'text') {
            const rawVal = val.replace(/\D/g, '');
            val = formatCurrency(rawVal);
            input.dataset.rawValue = rawVal;
        } else {
            val = val.replace(/\D/g, '');
        }
    }
    
    // I. Property Title Specifics (no emojis or unsupported characters)
    if (input.id === 'p_title') {
        val = val.replace(/[^A-Za-z0-9\s.,'\"\-?!()]/g, '');
    }
    
    // J. Floor Specifics (no special characters or emojis)
    if (input.id === 'p_floor') {
        val = val.replace(/[^A-Za-z0-9\s]/g, '');
    }
    
    // K. Room Size Specifics (accept digits only, automatically append ' sq.ft')
    if (input.id === 'p_room_size') {
        let digits = val.replace(/\D/g, '');
        if (digits) {
            val = digits + ' sq.ft';
            input.dataset.rawValue = digits;
        } else {
            val = '';
            input.dataset.rawValue = '';
        }
    }

    if (input.value !== val) {
        input.value = val;
    }
}

/**
 * 2. Input Validation Rules
 */
function validateInputElement(input) {
    const val = input.value.trim();
    let isValid = true;
    let errorMsg = '';
    
    // If field is required and empty
    if (input.hasAttribute('required') && val === '') {
        isValid = false;
        errorMsg = 'This field is required.';
    } else if (val !== '') {
        // A. Name validation
        if (input.id === 'name') {
            const nameRegex = /^[A-Za-z]+(\s[A-Za-z]+)*$/;
            if (!nameRegex.test(val)) {
                isValid = false;
                errorMsg = 'Please enter a valid name (letters and spaces only).';
            }
        }
        
        // B. Phone validation
        if (input.id === 'mobile') {
            if (val.length !== 10) {
                isValid = false;
                errorMsg = 'Phone number must be exactly 10 digits.';
            }
        }
        
        // C. Email validation
        if (input.type === 'email') {
            const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            if (!emailRegex.test(val)) {
                isValid = false;
                errorMsg = 'Please enter a valid email address.';
            }
        }
        
        // D. Password validation (Signup page only)
        if (input.id === 'password' && window.location.pathname.includes('/signup')) {
            const passwordRules = validatePasswordStrength(val);
            if (!passwordRules.isValid) {
                isValid = false;
                errorMsg = passwordRules.errors.join(' ');
            }
            updatePasswordStrengthUI(val);
        }
        
        // E. OTP validation
        if (input.id === 'otpCode') {
            if (val.length !== 6) {
                isValid = false;
                errorMsg = 'OTP must be exactly 6 digits.';
            }
        }
        
        // F. Price validation
        if (input.id === 'p_price') {
            const raw = input.type === 'text' ? (input.dataset.rawValue || '') : val;
            if (raw === '' || parseInt(raw) <= 0) {
                isValid = false;
                errorMsg = 'Please enter a valid price greater than 0.';
            }
        }
        
        // G. Floor validation
        if (input.id === 'p_floor') {
            const floorRegex = /^(Ground|Basement|Terrace|([1-9][0-9]?|100)(st|nd|rd|th))(\s*Floor)?$/i;
            if (!floorRegex.test(val)) {
                isValid = false;
                errorMsg = 'Must be Ground, Basement, Terrace, or a number 1st to 100th (e.g., 1st, 2nd).';
            }
        }
        
        // H. Room Size validation
        if (input.id === 'p_room_size') {
            const raw = input.dataset.rawValue || '';
            const size = parseInt(raw);
            if (isNaN(size) || size < 50 || size > 5000) {
                isValid = false;
                errorMsg = 'Room size must be between 50 and 5000 sq.ft.';
            }
        }
        
        // I. Available From validation (no past dates)
        if (input.id === 'p_available_from') {
            const selectedDate = new Date(val);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            if (selectedDate < today) {
                isValid = false;
                errorMsg = 'Available date cannot be in the past.';
            }
        }
    }
    
    // Apply styling and error feedback
    applyValidationFeedback(input, isValid, errorMsg);
    return isValid;
}

/**
 * Helper to apply green/red borders and show inline error message
 */
function applyValidationFeedback(input, isValid, errorMsg) {
    const group = input.closest('.form-group');
    if (!group) return;
    
    // Clear existing feedback
    input.classList.remove('is-valid', 'is-invalid');
    let feedback = group.querySelector('.error-feedback');
    if (feedback) feedback.remove();
    
    if (input.value.trim() === '') {
        // If empty and not required, don't show red or green borders
        if (!input.hasAttribute('required')) {
            return;
        }
    }
    
    if (isValid) {
        input.classList.add('is-valid');
    } else {
        input.classList.add('is-invalid');
        
        // Append error message
        feedback = document.createElement('span');
        feedback.className = 'error-feedback';
        feedback.style.color = '#EF4444';
        feedback.style.fontSize = '0.75rem';
        feedback.style.fontWeight = '600';
        feedback.style.marginTop = '0.25rem';
        feedback.style.textAlign = 'left';
        feedback.textContent = errorMsg;
        
        group.appendChild(feedback);
    }
}

/**
 * Check if the entire form is valid to toggle submit button
 */
function checkFormValidity(form, inputs, submitBtn) {
    if (!submitBtn) return;
    
    let isFormValid = true;
    
    inputs.forEach(input => {
        const val = input.value.trim();
        
        // If required and empty
        if (input.hasAttribute('required') && val === '') {
            isFormValid = false;
        }
        
        // If has invalid class
        if (input.classList.contains('is-invalid')) {
            isFormValid = false;
        }
    });
    
    submitBtn.disabled = !isFormValid;
}

/**
 * Helper: Capitalize first letter of each word
 */
function capitalizeWords(str) {
    return str.replace(/\b\w/g, char => char.toUpperCase());
}

/**
 * Helper: Format currency with Indian Comma grouping
 */
function formatCurrency(amount) {
    if (amount === '') return '';
    const num = parseInt(amount);
    if (isNaN(num)) return '';
    return '₹' + num.toLocaleString('en-IN');
}

/**
 * Helper: Validate password strength rules
 */
function validatePasswordStrength(password) {
    const errors = [];
    if (password.length < 8) {
        errors.push('Min 8 characters.');
    }
    if (!/[A-Z]/.test(password)) {
        errors.push('At least one uppercase letter.');
    }
    if (!/[a-z]/.test(password)) {
        errors.push('At least one lowercase letter.');
    }
    if (!/[0-9]/.test(password)) {
        errors.push('At least one number.');
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        errors.push('At least one special character.');
    }
    
    return {
        isValid: errors.length === 0,
        errors: errors
    };
}

/**
 * Helper: Update Password Strength Bar UI
 */
function updatePasswordStrengthUI(password) {
    const bar = document.getElementById('passwordStrengthBar');
    const text = document.getElementById('passwordStrengthText');
    if (!bar || !text) return;
    
    if (password === '') {
        bar.style.width = '0%';
        text.textContent = '';
        return;
    }
    
    let score = 0;
    if (password.length >= 8) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score++;
    
    let color = '#EF4444'; // Red
    let strength = 'Weak';
    let width = '20%';
    
    if (score >= 4) {
        color = '#10B981'; // Green
        strength = 'Strong';
        width = '100%';
    } else if (score >= 2) {
        color = '#F59E0B'; // Amber
        strength = 'Medium';
        width = '60%';
    }
    
    bar.style.width = width;
    bar.style.backgroundColor = color;
    text.textContent = `Strength: ${strength}`;
    text.style.color = color;
}
