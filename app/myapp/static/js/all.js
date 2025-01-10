// JavaScript for popup functionality using Bootstrap modal
function popup(html = '') {
    const modal = document.getElementById('popupModal'); // Ensure the correct modal ID is used

    // Update the modal body content if HTML is provided
    if (html !== '') {
        modal.querySelector('.modal-body').innerHTML = html;
    }

    // Initialize the modal with Bootstrap's JavaScript API
    const bootstrapModal = new bootstrap.Modal(modal);

    // Show the modal
    bootstrapModal.show();

    // Trigger a reflow to ensure proper resizing and visibility
    modal.addEventListener('shown.bs.modal', () => {
        modal.offsetHeight; // Forces a reflow
    });
}

function closeCurrentModal(txt = '') {
    if (txt != '') {
        console.log(txt);
    }

    const modal = document.querySelector('.modal.show'); // Get the currently visible modal

    if (modal) {
        const modalInstance = bootstrap.Modal.getInstance(modal); // Get the modal instance
        if (modalInstance) {
            modalInstance.hide(); // Close the modal
        }
    }
}


function getPage(url, callback, showLoading = false, loadingMessage = '') {
    // Perform an AJAX request using fetch

    if (showLoading) {
        toggleLoading(true, loadingMessage);
    }

    fetch(url)
        .then(response => {
            toggleLoading(false);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text(); // Get the response as text (e.g., HTML, JSON, etc.)
        })
        .then(data => {
            callback(data); // Pass the data to the callback function
        })
        .catch(error => {
            toggleLoading(false);
            console.log(error);
            callback(error); // Pass the error to the callback function
        });
}

function submitFormAjax(formId, successCallback = null, errorCallback = null, loadingMessage = '') {
    const form = document.getElementById(formId);

    if (!form) {
        console.error(`Form with id '${formId}' not found.`);
        return;
    }

    const formData = new FormData(form);
    const actionUrl = form.action; // The form's 'action' attribute

    // Log all key-value pairs in the FormData
    console.log('FormData Contents:');
    for (let [key, value] of formData.entries()) {
        console.log(`${key}: ${value}`);
    }

    toggleLoading(true, loadingMessage);

    fetch(actionUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value, // Include the CSRF token
        },
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            toggleLoading(false);

            if (data.status === 'success') {
                if (successCallback && typeof successCallback === 'function') {
                    successCallback(data); // Call the success callback
                }
            } else {
                if (errorCallback && typeof errorCallback === 'function') {
                    errorCallback(data); // Call the error callback
                } else {
                    console.error('Error:', data);
                }
            }
        })
        .catch(error => {
            toggleLoading(false);
            console.error('AJAX Error:', error);
        });
}


// Loading Overlay
function toggleLoading(show, text = '') {
    const overlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    if (show) {
        loadingText.textContent = text;
        overlay.classList.add('active');
    } else {
        overlay.classList.remove('active');
    }
}