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
