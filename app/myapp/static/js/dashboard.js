function fetchAllData() {
    fetchUserInfo();
    fetchEducationData();
    fetchWorkExperienceData();
    fetchSkillData();
    fetchProjectData();
    fetchCertificationData();
    fetchResumeInfo();
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
                <td>${data.linkedin_url}</td>
                <td>${data.github_url}</td>
                <td>${data.portfolio_url}</td>
                <!--<td>${data.summary}</td>-->
            </tr>`;
            tbody.innerHTML = row;
        });
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
                    <td>${edu.graduation_year}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editEducation(${edu.id})">Edit</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteEducation(${edu.id})">Delete</button>
                    </td>
                </tr>
            `).join('');
        });
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
                    <td>${exp.job_description}</td>
                    <td>${exp.start_date}</td>
                    <td>${exp.end_date}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editWorkExperience(${exp.id})">Edit</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteWorkExperience(${exp.id})">Delete</button>
                    </td>
                </tr>
            `).join('');
        });
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
                        <button class="btn btn-sm btn-primary" onclick="editSkill(${skill.id})">Edit</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteSkill(${skill.id})">Delete</button>
                    </td>
                </tr>
            `).join('');
        });
}

function fetchProjectData() {
    fetch('/project-json/')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('projectsTableBody');
            tbody.innerHTML = data.map(project => `
                <tr>
                    <td>${project.project_title}</td>
                    <td>${project.description}</td>
                    <td>${project.technologies_used}</td>
                    <td>${project.project_url}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editProject(${project.id})">Edit</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteProject(${project.id})">Delete</button>
                    </td>
                </tr>
            `).join('');
        });
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
                        <button class="btn btn-sm btn-primary" onclick="editCertification(${cert.id})">Edit</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteCertification(${cert.id})">Delete</button>
                    </td>
                </tr>
            `).join('');
        });
}

function editUserInfo() {
    getPage('/templates/frontend/modals/user_info_modal', popup);
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
    fetch('/resume-json/') // Replace with the actual endpoint for fetching resume info
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('resumeTableBody'); // Replace with your table body ID
            tbody.innerHTML = data.map(resume => `
                <tr>
                    <td>${resume.name}</td>
                    <td>${resume.purpose || 'No purpose provided'}</td>
                    <td>${resume.created_date}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editResume(${resume.id})">Edit</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteResume(${resume.id})">Delete</button>
                    </td>
                </tr>
            `).join('');
        })
        .catch(error => {
            console.error('Error fetching resume info:', error);
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
                    fetchResumeInfo(); // Refresh the resume info after deletion
                } else {
                    alert('Failed to delete resume.');
                    fetchResumeInfo();
                }
            })
            .catch(error => {
                console.error('Error deleting resume:', error);
                fetchResumeInfo();
            });
    }
}
