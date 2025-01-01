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
        console.log('Modal content loaded and resized!');
    });
}




// Get Page AJAX

function getPage(url, callback) {
    // Perform an AJAX request using fetch
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text(); // Get the response as text (e.g., HTML, JSON, etc.)
        })
        .then(data => {
            callback(data); // Pass the data to the callback function
            console.log(data);
        })
        .catch(error => {
            callback(error); // Pass the error to the callback function
        });
}

function submitFormAjax(formId, successCallback = null, errorCallback = null) {
    const form = document.getElementById(formId);
    if (!form) {
        console.error(`Form with id '${formId}' not found.`);
        return;
    }

    form.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent the default form submission behavior

        const formData = new FormData(form);
        const actionUrl = form.action; // The form's 'action' attribute

        fetch(actionUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value, // Include the CSRF token
            },
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    if (successCallback && typeof successCallback === 'function') {
                        successCallback(data); // Call the success callback
                    } else {
                        console.log('Success:', data);
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
                console.error('AJAX Error:', error);
            });
    });
}
