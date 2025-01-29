from myapp.library.aiworkflows.generate_jobsearchstring import ai_generate_jobsearchstring_workflow
from myapp.library.api_managers.adzuna import AdzunaAPIManager
from myapp.library.aiworkflows.simulate_ats import ai_simulate_ats_workflow
import json


def jobsearch_workflow(request, search_string, custom_filters):
    """
    Executes a job search workflow using AI-generated search strings, job search APIs, 
    and an ATS simulation to filter and rank jobs based on relevance.

    :param request: User-specific information (skills, experience, career goals).
    :param custom_filters: Custom filters for job search (e.g., location, salary, etc.).
    :return: A ranked list of jobs sorted by relevance score.
    """
    job_search_manager = AdzunaAPIManager()
    job_api_response = job_search_manager.search_jobs(query=search_string, results_per_page=10)
    job_list = job_search_manager.extract_job_data(job_api_response)

    ranked_jobs = []

    for job in job_list:
        # Simulate ATS to obtain a relevance score (0-100)
        relevance_score = ai_simulate_ats_workflow(request, custom_filters, json.dumps(job))

        # Only include jobs with a relevance score greater than 50
        if relevance_score > 50:
            job["relevance_score"] = relevance_score
            ranked_jobs.append(job)

    # Step 4: Sort jobs by relevance score in descending order
    ranked_jobs.sort(key=lambda x: x["relevance_score"], reverse=True)

    return ranked_jobs
