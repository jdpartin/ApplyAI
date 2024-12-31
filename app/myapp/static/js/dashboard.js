// Global functions for handling modals and form submissions

// Show Add Education Modal
function showAddEducationModal() {
    const modal = new bootstrap.Modal(document.getElementById('educationModal'));
    clearModalFields('educationForm');
    modal.show();
}

// Show Edit Education Modal
function showEditEducationModal(id) {
    fetch(`/api/education/${id}/`)
        .then(response => response.json())
        .then(data => {
            populateModalFields('educationForm', data);
            const modal = new bootstrap.Modal(document.getElementById('educationModal'));
            modal.show();
        })
        .catch(error => console.error('Error fetching education:', error));
}

// Show Add Work Experience Modal
function showAddWorkExperienceModal() {
    const modal = new bootstrap.Modal(document.getElementById('workExperienceModal'));
    clearModalFields('workExperienceForm');
    modal.show();
}

// Show Edit Work Experience Modal
function showEditWorkExperienceModal(id) {
    fetch(`/api/work-experience/${id}/`)
        .then(response => response.json())
        .then(data => {
            populateModalFields('workExperienceForm', data);
            const modal = new bootstrap.Modal(document.getElementById('workExperienceModal'));
            modal.show();
        })
        .catch(error => console.error('Error fetching work experience:', error));
}

// Submit Form
function submitForm(formId, actionUrl, method = 'POST') {
    const form = document.getElementById(formId);
    const formData = new FormData(form);

    fetch(actionUrl, {
        method: method,
        body: JSON.stringify(Object.fromEntries(formData)),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
    })
        .then(response => {
            if (response.ok) {
                window.location.reload();
            } else {
                return response.json();
            }
        })
        .then(data => {
            if (data && data.error) {
                console.error(data.error);
            }
        })
        .catch(error => console.error('Error submitting form:', error));
}

// Utility: Populate modal fields with data
function populateModalFields(formId, data) {
    const form = document.getElementById(formId);
    Object.keys(data).forEach(key => {
        const input = form.querySelector(`[name="${key}"]`);
        if (input) input.value = data[key];
    });
}

// Utility: Clear modal fields
function clearModalFields(formId) {
    const form = document.getElementById(formId);
    form.reset();
}

// Utility: Get CSRF Token
function getCSRFToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfToken ? csrfToken.value : '';
}


// Delete Education
function deleteEducation(id) {
    if (confirm('Are you sure you want to delete this education record?')) {
        fetch(`/api/education/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCSRFToken(),
            },
        })
            .then(response => {
                if (response.ok) {
                    window.location.reload();
                } else {
                    return response.json();
                }
            })
            .then(data => {
                if (data && data.error) {
                    console.error(data.error);
                }
            })
            .catch(error => console.error('Error deleting education:', error));
    }
}

// Delete Work Experience
function deleteWorkExperience(id) {
    if (confirm('Are you sure you want to delete this work experience?')) {
        fetch(`/api/work-experience/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCSRFToken(),
            },
        })
            .then(response => {
                if (response.ok) {
                    window.location.reload();
                } else {
                    return response.json();
                }
            })
            .then(data => {
                if (data && data.error) {
                    console.error(data.error);
                }
            })
            .catch(error => console.error('Error deleting work experience:', error));
    }
}

// Show Add Skill Modal
function showAddSkillModal() {
    const modal = new bootstrap.Modal(document.getElementById('skillModal'));
    clearModalFields('skillForm');
    modal.show();
}

// Show Edit Skill Modal
function showEditSkillModal(id) {
    fetch(`/api/skill/${id}/`)
        .then(response => response.json())
        .then(data => {
            populateModalFields('skillForm', data);
            const modal = new bootstrap.Modal(document.getElementById('skillModal'));
            modal.show();
        })
        .catch(error => console.error('Error fetching skill:', error));
}

// Delete Skill
function deleteSkill(id) {
    if (confirm('Are you sure you want to delete this skill?')) {
        fetch(`/api/skill/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCSRFToken(),
            },
        })
            .then(response => {
                if (response.ok) {
                    window.location.reload();
                } else {
                    return response.json();
                }
            })
            .then(data => {
                if (data && data.error) {
                    console.error(data.error);
                }
            })
            .catch(error => console.error('Error deleting skill:', error));
    }
}

function showError(message) {
    const errorContainer = document.getElementById('errorContainer');
    if (errorContainer) {
        errorContainer.innerText = message;
        errorContainer.style.display = 'block';
        setTimeout(() => {
            errorContainer.style.display = 'none';
        }, 5000);
    } else {
        alert(message); // Fallback if no error container exists
    }
}

// Show the modal for editing personal information
function showEditPersonalInfoModal(field) {
    const modal = new bootstrap.Modal(document.getElementById('personalInfoModal'));
    clearModalFields('personalInfoForm');
    document.getElementById('personalInfoField').value = field;
    modal.show();
}

// Save personal information changes
function savePersonalInfo() {
    const form = document.getElementById('personalInfoForm');
    const formData = new FormData(form);

    fetch('/api/user-info/update/', {
        method: 'POST',
        body: JSON.stringify(Object.fromEntries(formData)),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
    })
        .then(response => {
            if (response.ok) window.location.reload();
            else return response.json();
        })
        .then(data => {
            if (data?.error) console.error(data.error);
        })
        .catch(error => console.error('Error updating personal information:', error));
}

// Delete an education entry
function deleteEducation(id) {
    fetch(`/api/education/${id}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
    })
        .then(response => {
            if (response.ok) window.location.reload();
            else console.error('Error deleting education.');
        })
        .catch(error => console.error('Error deleting education:', error));
}

// Show the modal for adding a new work experience
function showAddWorkExperienceModal() {
    const modal = new bootstrap.Modal(document.getElementById('workExperienceModal'));
    clearModalFields('workExperienceForm');
    modal.show();
}

// Show the modal for editing a work experience entry
function showEditWorkExperienceModal(id) {
    fetch(`/api/work-experience/${id}/`)
        .then(response => response.json())
        .then(data => {
            populateModalFields('workExperienceForm', data);
            const modal = new bootstrap.Modal(document.getElementById('workExperienceModal'));
            modal.show();
        })
        .catch(error => console.error('Error fetching work experience:', error));
}

// Delete a work experience entry
function deleteWorkExperience(id) {
    fetch(`/api/work-experience/${id}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
    })
        .then(response => {
            if (response.ok) window.location.reload();
            else console.error('Error deleting work experience.');
        })
        .catch(error => console.error('Error deleting work experience:', error));
}

// Show the modal for adding a skill
function showAddSkillModal() {
    const modal = new bootstrap.Modal(document.getElementById('skillModal'));
    clearModalFields('skillForm');
    modal.show();
}

// Show the modal for editing a skill
function showEditSkillModal(id) {
    fetch(`/api/skills/${id}/`)
        .then(response => response.json())
        .then(data => {
            populateModalFields('skillForm', data);
            const modal = new bootstrap.Modal(document.getElementById('skillModal'));
            modal.show();
        })
        .catch(error => console.error('Error fetching skill:', error));
}

// Delete a skill entry
function deleteSkill(id) {
    fetch(`/api/skills/${id}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
    })
        .then(response => {
            if (response.ok) window.location.reload();
            else console.error('Error deleting skill.');
        })
        .catch(error => console.error('Error deleting skill:', error));
}

// Show the modal for adding a project
function showAddProjectModal() {
    const modal = new bootstrap.Modal(document.getElementById('projectModal'));
    clearModalFields('projectForm');
    modal.show();
}

// Show the modal for editing a project
function showEditProjectModal(id) {
    fetch(`/api/projects/${id}/`)
        .then(response => response.json())
        .then(data => {
            populateModalFields('projectForm', data);
            const modal = new bootstrap.Modal(document.getElementById('projectModal'));
            modal.show();
        })
        .catch(error => console.error('Error fetching project:', error));
}

// Delete a project entry
function deleteProject(id) {
    fetch(`/api/projects/${id}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
    })
        .then(response => {
            if (response.ok) window.location.reload();
            else console.error('Error deleting project.');
        })
        .catch(error => console.error('Error deleting project:', error));
}

// Show the modal for adding a certification
function showAddCertificationModal() {
    const modal = new bootstrap.Modal(document.getElementById('certificationModal'));
    clearModalFields('certificationForm');
    modal.show();
}

// Show the modal for editing a certification
function showEditCertificationModal(id) {
    fetch(`/api/certifications/${id}/`)
        .then(response => response.json())
        .then(data => {
            populateModalFields('certificationForm', data);
            const modal = new bootstrap.Modal(document.getElementById('certificationModal'));
            modal.show();
        })
        .catch(error => console.error('Error fetching certification:', error));
}

// Delete a certification entry
function deleteCertification(id) {
    fetch(`/api/certifications/${id}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
    })
        .then(response => {
            if (response.ok) window.location.reload();
            else console.error('Error deleting certification.');
        })
        .catch(error => console.error('Error deleting certification:', error));
}
