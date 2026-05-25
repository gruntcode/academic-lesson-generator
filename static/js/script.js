document.addEventListener('DOMContentLoaded', function () {
    const lessonForm = document.getElementById('lessonForm');
    const generateBtn = document.getElementById('generateBtn');
    const mainPage = document.getElementById('main-page');
    const generatingPage = document.getElementById('generating-page');
    const topicInput = document.getElementById('topic');
    const gradeLevelSelect = document.getElementById('grade_level');

    function showMain() {
        mainPage.classList.remove('hidden');
        generatingPage.classList.add('hidden');
    }

    function showGenerating() {
        mainPage.classList.add('hidden');
        generatingPage.classList.remove('hidden');
    }

    showMain();

    function validateForm() {
        const topic = topicInput.value.trim();
        const gradeLevel = gradeLevelSelect.value;

        clearErrors();

        let isValid = true;

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
        document.querySelectorAll('.error-message').forEach((el) => el.remove());
        document.querySelectorAll('.error').forEach((el) => {
            el.classList.remove('error');
            el.removeAttribute('aria-invalid');
        });
    }

    function showNotification(message, type = 'error') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.setAttribute('role', 'alert');
        document.body.appendChild(notification);

        setTimeout(() => notification.classList.add('show'), 100);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    lessonForm.addEventListener('submit', function (e) {
        e.preventDefault();

        if (!validateForm()) return;

        showGenerating();
        generateBtn.disabled = true;

        const formData = new FormData(lessonForm);

        fetch('/generate-lesson', {
            method: 'POST',
            body: formData,
        })
            .then((response) => {
                if (response.status === 429) {
                    throw new Error('Rate limit exceeded. Please try again in a few minutes.');
                }
                if (!response.ok) {
                    return response.json().then((data) => {
                        throw new Error(data.error || 'Failed to generate lesson');
                    });
                }
                return response.blob();
            })
            .then((blob) => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${formData.get('topic').replace(/\s+/g, '_')}_lesson.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();

                showNotification('Lesson generated successfully!', 'success');
                setTimeout(returnToMainPage, 1500);
            })
            .catch((error) => {
                console.error('Error:', error);
                showNotification(error.message, 'error');
                returnToMainPage();
            });
    });

    function returnToMainPage() {
        showMain();
        generateBtn.disabled = false;
        lessonForm.reset();
    }

    topicInput.addEventListener('input', function () {
        if (this.classList.contains('error')) clearErrors();
    });

    gradeLevelSelect.addEventListener('change', function () {
        if (this.classList.contains('error')) clearErrors();
    });

    lessonForm.reset();
});
