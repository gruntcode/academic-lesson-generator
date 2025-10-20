document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const lessonForm = document.getElementById('lessonForm');
    const generateBtn = document.getElementById('generateBtn');
    const mainPage = document.getElementById('main-page');
    const generatingPage = document.getElementById('generating-page');
    const topicInput = document.getElementById('topic');
    const gradeLevelSelect = document.getElementById('grade_level');
    
    // Make sure main page is visible and generating page is hidden on load
    mainPage.style.display = 'block';
    generatingPage.style.display = 'none';
    
    // Client-side validation
    function validateForm() {
        const topic = topicInput.value.trim();
        const gradeLevel = gradeLevelSelect.value;
        
        // Clear previous errors
        clearErrors();
        
        let isValid = true;
        
        // Validate topic
        if (!topic) {
            showError(topicInput, 'Topic is required');
            isValid = false;
        } else if (topic.length < 3) {
            showError(topicInput, 'Topic must be at least 3 characters long');
            isValid = false;
        } else if (topic.length > 200) {
            showError(topicInput, 'Topic must be less than 200 characters');
            isValid = false;
        } else if (/[<>{}]/.test(topic)) {
            showError(topicInput, 'Topic contains invalid characters');
            isValid = false;
        }
        
        // Validate grade level
        if (!gradeLevel) {
            showError(gradeLevelSelect, 'Please select a grade level');
            isValid = false;
        }
        
        return isValid;
    }
    
    function showError(element, message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        errorDiv.setAttribute('role', 'alert');
        element.parentNode.appendChild(errorDiv);
        element.classList.add('error');
        element.setAttribute('aria-invalid', 'true');
    }
    
    function clearErrors() {
        const errors = document.querySelectorAll('.error-message');
        errors.forEach(error => error.remove());
        
        const errorInputs = document.querySelectorAll('.error');
        errorInputs.forEach(input => {
            input.classList.remove('error');
            input.removeAttribute('aria-invalid');
        });
    }
    
    function showNotification(message, type = 'error') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.setAttribute('role', 'alert');
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }
    
    // Handle form submission with AJAX for better error handling
    lessonForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate form
        if (!validateForm()) {
            return;
        }
        
        // Show generating page and hide main page
        mainPage.style.display = 'none';
        generatingPage.style.display = 'block';
        
        // Disable the button to prevent multiple submissions
        generateBtn.disabled = true;
        
        // Create FormData from the form
        const formData = new FormData(lessonForm);
        
        // Send AJAX request
        fetch('/generate-lesson', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.status === 429) {
                throw new Error('Rate limit exceeded. Please try again in a few minutes.');
            }
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to generate lesson');
                });
            }
            return response.blob();
        })
        .then(blob => {
            // Create a download link for the PDF
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${formData.get('topic').replace(/\s+/g, '_')}_lesson.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
            
            // Show success notification
            showNotification('Lesson generated successfully!', 'success');
            
            // Return to main page after short delay
            setTimeout(() => {
                returnToMainPage();
            }, 1500);
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification(error.message, 'error');
            returnToMainPage();
        });
    });
    
    // Function to return to main page
    function returnToMainPage() {
        // Return to main page
        generatingPage.style.display = 'none';
        mainPage.style.display = 'block';
        
        // Re-enable the button
        generateBtn.disabled = false;
        
        // Reset the form
        lessonForm.reset();
    }
    
    // Add input event listeners for real-time validation feedback
    topicInput.addEventListener('input', function() {
        if (this.classList.contains('error')) {
            clearErrors();
        }
    });
    
    gradeLevelSelect.addEventListener('change', function() {
        if (this.classList.contains('error')) {
            clearErrors();
        }
    });
    
    // Reset form when page loads
    lessonForm.reset();
});
