// JavaScript for popup functionality using Bootstrap modal
function popup(html = '') {
    const modal = document.getElementById('popupModal'); // Ensure the correct modal ID is used

    // Check if the modal is already visible
    const isModalVisible = modal.classList.contains('show');

    if (html == false) {
        closeCurrentModal();
        return;
    }

    // If modal is already shown, just update the HTML
    if (isModalVisible) {
        if (html !== '') {
            modal.querySelector('.modal-body').innerHTML = html;
        }
        return; // Exit as the modal is already visible
    }

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

function submitFormAjax(formId, successCallback = null, errorCallback = null, loadingMessage = '', minLoadTime = 0) {
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

    toggleLoading(true, loadingMessage, minLoadTime);

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


// Loading 

// Global variables
let loadingStartTime = null;
let minLoadingEndTime = null;
let adRefreshTime = null;     // Tracks the last ad load time
let closeRequested = false;
let closing = false;
let adsRefreshing = null; // Interval for refreshing ads

// Settings for different account tiers
let eliminateFalseLoadingDelay = false;
let removeAds = false;

async function toggleLoading(show, text = '', minLoadTime = 0) {

    const adRefreshInterval = 5000;
    const minAdDisplayTime = 3000;

    const overlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    const adContainer = document.getElementById('adContainer');
    const minLoadingDuration = minLoadTime * 1000;

    if (eliminateFalseLoadingDelay) {
        minLoadingDuration = 0;
    }

    if (show) {
        // ----- Showing the overlay -----
        closeRequested = false;

        loadingStartTime = Date.now();
        minLoadingEndTime = loadingStartTime + minLoadingDuration;

        if (loadingText)
            loadingText.textContent = text;

        overlay.classList.add('active');

        // Start ad-refresh logic if it's not running
        if (removeAds) {
            adRefreshTime = Date.now() - minAdDisplayTime;
        } else {
            if (!adsRefreshing) {
                adsRefreshing = setInterval(() => {
                    // Only refresh ads if we haven't requested to close
                    if (!closeRequested) {
                        refreshLoadingAds();
                    }
                }, adRefreshInterval);
            }
        }

        setTimeout(() => {
            if (closeRequested == true) {
                toggleLoading(false);
            }
        }, minLoadingEndTime - Date.now());

        refreshLoadingAds();

    } else {
        // ----- Requesting to hide the overlay -----

        function close() {
            clearInterval(adsRefreshing);
            adsRefreshing = null;
            overlay.classList.remove('active');

            if (adContainer) {
                adContainer.innerHTML = '';
            }
        }

        closeRequested = true;

        // If the ads havent been loaded yet check again in 1 second
        if (adRefreshTime == null) {
            setTimeout(() => {
                toggleLoading(false);
            }, 1000);
            return;
        }

        if (Date.now() >= minLoadingEndTime) {
            if (Date.now() - adRefreshTime >= minAdDisplayTime) {
                close();
            } else if (!closing) {
                // Ensure we wait until 3 seconds have elapsed since the last ad refresh
                closing = true;

                const remainingTime = minAdDisplayTime - (Date.now() - adRefreshTime);
                setTimeout(() => {
                    close();
                }, remainingTime);
            }
        }
    }
}

async function refreshLoadingAds() {
    await loadMockAds();
    adRefreshTime = Date.now();
}

// Mock function to simulate loading ads
async function loadMockAds() {
    const adContainer = document.getElementById('adContainer');
    if (!adContainer) {
        console.error('Ad container not found.');
        return;
    }

    adContainer.innerHTML = ''; // Clear old ads

    for (let i = 0; i < 3; i++) {
        const ad = document.createElement('div');
        ad.className = 'mock-ad';
        ad.textContent = `Ad Slot ${i + 1}`;
        adContainer.appendChild(ad);
    }
}
