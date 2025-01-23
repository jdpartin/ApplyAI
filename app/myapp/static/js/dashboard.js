function fetchAllData() {
    fetchUserInfo();
    fetchEducationData();
    fetchWorkExperienceData();
    fetchSkillData();
    fetchProjectData();
    fetchCertificationData();
    fetchResumeInfo();
    fetchCoverLetterInfo();
}

function fetchUserInfo() {
    fetch('/user-info-json/')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('personalInfoTableBody');
            const row = `<tr>
                <td>${data.first_name} ${data.last_name}</td>
                <td>${data.email}</td>
                <td>${data.phone_number}</td>
                <td>${data.address}</td>
            </tr>`;
            tbody.innerHTML = row;
        });
}

function editUserInfo() {
    getPage(`/templates/frontend/modals/user_info_modal?`, popup);
}

function fetchEducationData() {
    fetch('/education-json/')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('educationTableBody');
            tbody.innerHTML = data.map(edu => `
                <tr>
                    <td>${edu.school_name}</td>
                    <td>${edu.degree}</td>
                    <td>${edu.field_of_study}</td>
                    <td>${edu.start_date}</td>
                    <td>${edu.end_date ? edu.end_date : 'Currently Enrolled'}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editEducation(${edu.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteEducation(${edu.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        });
}


function editEducation(id) {
    getPage(`/templates/frontend/modals/education_modal?id=${id}`, popup);
}

function deleteEducation(id) {
    if (confirm('Are you sure you want to delete this education?')) {
        fetch(`/education-delete/?id=${id}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
                    fetchEducationData();
                } else {
                    alert('Failed to delete education.');
                }
            });
    }
}

function fetchWorkExperienceData() {
    fetch('/work-experience-json/')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('workExperienceTableBody');
            tbody.innerHTML = data.map(exp => `
                <tr>
                    <td>${exp.job_title}</td>
                    <td>${exp.company_name}</td>
                    <td>${exp.start_date}</td>
                    <td>${exp.end_date ? exp.end_date : 'Current Employer'}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editWorkExperience(${exp.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteWorkExperience(${exp.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        });
}

function editWorkExperience(id) {
    getPage(`/templates/frontend/modals/work_experience_modal?id=${id}`, popup);
}

function deleteWorkExperience(id) {
    if (confirm('Are you sure you want to delete this work experience?')) {
        fetch(`/work-experience-delete/?id=${id}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
                    fetchWorkExperienceData();
                } else {
                    alert('Failed to delete work experience.');
                }
            });
    }
}

function fetchSkillData() {
    fetch('/skill-json/')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('skillsTableBody');
            tbody.innerHTML = data.map(skill => `
                <tr>
                    <td>${skill.skill_name}</td>
                    <td>${skill.years_of_experience}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editSkill(${skill.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteSkill(${skill.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        });
}

function editSkill(id) {
    getPage(`/templates/frontend/modals/skill_modal?id=${id}`, popup);
}

function deleteSkill(id) {
    if (confirm('Are you sure you want to delete this skill?')) {
        fetch(`/skill-delete/?id=${id}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
                    fetchSkillData();
                } else {
                    alert('Failed to delete skill.');
                }
            });
    }
}

function fetchProjectData() {
    fetch('/project-json/')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('projectsTableBody');
            tbody.innerHTML = data.map(project => `
                <tr>
                    <td>${project.project_title}</td>
                    <td>${project.project_url}</td>
                    <td>${project.start_date}</td>
                    <td>${project.end_date ? project.end_date : 'In Progress'}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editProject(${project.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteProject(${project.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        });
}

function editProject(id) {
    getPage(`/templates/frontend/modals/project_modal?id=${id}`, popup);
}

function deleteProject(id) {
    if (confirm('Are you sure you want to delete this project?')) {
        fetch(`/project-delete/?id=${id}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
                    fetchProjectData();
                } else {
                    alert('Failed to delete project.');
                }
            });
    }
}

function fetchCertificationData() {
    fetch('/certification-json/')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('certificationsTableBody');
            tbody.innerHTML = data.map(cert => `
                <tr>
                    <td>${cert.certification_name}</td>
                    <td>${cert.issuing_organization}</td>
                    <td>${cert.issue_date}</td>
                    <td>${cert.expiration_date}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editCertification(${cert.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteCertification(${cert.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        });
}

function editCertification(id) {
    getPage(`/templates/frontend/modals/certification_modal?id=${id}`, popup);
}

function deleteCertification(id) {
    if (confirm('Are you sure you want to delete this certification?')) {
        fetch(`/certification-delete/?id=${id}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
                    fetchCertificationData();
                } else {
                    alert('Failed to delete certification.');
                }
            });
    }
}

function fetchResumeInfo() {
    fetch('/resume-json/')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('resumeTableBody');
            tbody.innerHTML = data.map(resume => `
                <tr>
                    <td>${resume.name}</td>
                    <td>${resume.purpose || 'No purpose provided'}</td>
                    <td>${resume.created_date}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editResume(${resume.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteResume(${resume.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                        <button class="btn btn-sm btn-success" onclick="downloadResume(${resume.id})">
                            <i class="fas fa-download"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        });
}

function editResume(id) {
    getPage(`/templates/frontend/modals/resume_modal?id=${id}`, popup);
}

function deleteResume(id) {
    if (confirm('Are you sure you want to delete this resume?')) {
        fetch(`/resume-delete/?id=${id}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
                    fetchResumeInfo();
                } else {
                    alert('Failed to delete resume.');
                }
            });
    }
}

function downloadResume(id) {
    window.location.href = `/resume-download/?id=${id}`;
}

function fetchCoverLetterInfo() {
    fetch('/cover-letter-json/')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('coverLetterTableBody');
            tbody.innerHTML = data.map(coverLetter => `
                <tr>
                    <td>${coverLetter.name}</td>
                    <td>${coverLetter.purpose || 'No purpose provided'}</td>
                    <td>${coverLetter.created_date}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editCoverLetter(${coverLetter.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteCoverLetter(${coverLetter.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                        <button class="btn btn-sm btn-success" onclick="downloadCoverLetter(${coverLetter.id})">
                            <i class="fas fa-download"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        });
}

function editCoverLetter(id) {
    getPage(`/templates/frontend/modals/cover_letter_modal?id=${id}`, popup);
}

function deleteCoverLetter(id) {
    if (confirm('Are you sure you want to delete this cover letter?')) {
        fetch(`/cover-letter-delete/?id=${id}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
                    fetchCoverLetterInfo();
                } else {
                    alert('Failed to delete cover letter.');
                }
            });
    }
}

function downloadCoverLetter(id) {
    window.location.href = `/cover-letter-download/?id=${id}`;
}

function expandSectionAndScroll(sectionId) {
    const section = document.getElementById(sectionId);
    if (!section) return;

    const button = section.previousElementSibling.querySelector('.accordion-button');

    // Ensure the section is expanded
    if (button.classList.contains('collapsed')) {
        button.click(); // Triggers Bootstrap's toggle
    }

    // Scroll into view smoothly after the section expands
    setTimeout(() => {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 300); // Adjust delay to match Bootstrap's collapse animation timing
}
