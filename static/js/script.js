document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const lessonForm = document.getElementById('lessonForm');
    const generateBtn = document.getElementById('generateBtn');
    const mainPage = document.getElementById('main-page');
    const generatingPage = document.getElementById('generating-page');
    const hiddenIframe = document.getElementById('hidden_iframe');
    
    // Make sure main page is visible and generating page is hidden on load
    mainPage.style.display = 'block';
    generatingPage.style.display = 'none';
    
    // Handle form submission
    lessonForm.addEventListener('submit', function(e) {
        // Show generating page and hide main page
        mainPage.style.display = 'none';
        generatingPage.style.display = 'block';
        
        // Disable the button to prevent multiple submissions
        generateBtn.disabled = true;
        
        // Set a 5-second timer to return to main page regardless of iframe load
        setTimeout(function() {
            returnToMainPage();
        }, 5000);
    });
    
    // Listen for the hidden iframe to load (which happens when the PDF is generated)
    hiddenIframe.addEventListener('load', function() {
        // Only process if generating page is visible (means we're in the middle of generation)
        if (generatingPage.style.display === 'block') {
            // Small delay to ensure the PDF download has started
            setTimeout(function() {
                returnToMainPage();
            }, 1000);
        }
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
    
    // Reset form when page loads
    lessonForm.reset();
});
