async function submitCreateResumeForm() {
    let resumeData = collectResumeData();

    toggleLoading(true, "Creating resume...");

    try {
        const response = await fetch('/templates/frontend/modals/add_resume_modal/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(resumeData)
        });

        if (response.ok) {
            const data = await response.json();
            console.log("Resume created successfully:", data);

            // Stop loading and close the popup
            window.alert("Resume created successfully.");
            toggleLoading(false);
            popup(false);
        } else {
            // Handle server errors
            let errorResp = await response.text();
            console.error("Error creating resume:", errorResp);
            window.alert("Error creating resume: " + errorResp);
            toggleLoading(false);
        }
    } catch (error) {
        // Handle network errors
        console.error("Network error:", error);
        window.alert("Network error: " + error);
        toggleLoading(false);
    }
}


function submit_ai_add_resume_form() {
    function success(resp) {
        popup(false);
        fetchResumeInfo();
    }

    function failure(resp) {
        fetchResumeInfo();
    }

    submitFormAjax('ai_add_resume_modal', success, failure, "Creating your resume with AI...", minLoadTime = 30);
}



function collectResumeData() {
    const modal = document.getElementById('popupModal'); // Limit scope to the modal
    const resumeData = {};

    // Collect Resume Name and Purpose
    resumeData.name = modal.querySelector('#resumeName').value.trim();
    resumeData.purpose = modal.querySelector('#resumePurpose').value.trim();

    // Collect Personal Information toggles
    resumeData.includePersonalInfo = {
        phone: modal.querySelector('#includePhone').checked,
        email: modal.querySelector('#includeEmail').checked,
        address: modal.querySelector('#includeAddress').checked,
        summary: modal.querySelector('#personalSummary').value.trim()
    };

    // Helper function to collect IDs and tailored summaries
    function collectItems(idPrefix, summaryPrefix = null) {
        const items = [];
        modal.querySelectorAll(`[id^=${idPrefix}]`).forEach(input => {
            if (input.type === 'checkbox' && input.checked) {
                const id = input.id.replace(idPrefix, '');
                const summary = summaryPrefix
                    ? modal.querySelector(`#${summaryPrefix}${id}`)?.value.trim()
                    : null;

                items.push({
                    id: parseInt(id),
                    ...(summary ? { tailoredSummary: summary } : {})
                });
            }
        });
        return items;
    }

    // Collect Education
    resumeData.educations = collectItems('includeEducation');

    // Collect Work Experience
    resumeData.workExperiences = collectItems(
        'includeWorkExperience',
        'workExperienceSummary'
    );

    // Collect Skills
    resumeData.skills = collectItems('includeSkill');

    // Collect Projects
    resumeData.projects = collectItems(
        'includeProject',
        'includeProjectSummary'
    );

    // Collect Certifications
    resumeData.certifications = collectItems('includeCertification');

    return resumeData;
}