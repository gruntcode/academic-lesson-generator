document.addEventListener('DOMContentLoaded', function() {
    const lessonForm = document.getElementById('lessonForm');
    const generateBtn = document.getElementById('generateBtn');
    const loadingElement = document.getElementById('loading');
    
    // Hide loading spinner on page load
    loadingElement.classList.add('hidden');
    
    lessonForm.addEventListener('submit', function(e) {
        // Show loading spinner
        loadingElement.classList.remove('hidden');
        
        // Disable the button to prevent multiple submissions
        generateBtn.disabled = true;
        
        // Create a hidden iframe to handle the file download
        // This allows us to detect when the download is complete
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        document.body.appendChild(iframe);
        
        // Store the original form target and action
        const originalTarget = lessonForm.target;
        const originalAction = lessonForm.action;
        
        // Set the form to target our hidden iframe
        lessonForm.target = iframe.name = 'download_iframe';
        
        // Let the form submit normally
        
        // Listen for the iframe to load, which indicates the response has been received
        iframe.addEventListener('load', function() {
            // Reset the loading state
            loadingElement.classList.add('hidden');
            generateBtn.disabled = false;
            
            // Reset form
            lessonForm.reset();
            
            // Restore original form target and action
            lessonForm.target = originalTarget;
            lessonForm.action = originalAction;
            
            // Clean up the iframe after a delay to ensure download starts
            setTimeout(function() {
                document.body.removeChild(iframe);
            }, 1000);
        });
    });
    
    // Reset form when page loads (in case of back navigation after download)
    lessonForm.reset();
});
