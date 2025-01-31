import requests
from django.conf import settings

APP_ID = settings.ADZUNA_APP_ID
APP_KEY = settings.ADZUNA_APP_KEY

class AdzunaAPIManager:

    def __init__(self, country: str = "us"):
        """
        Initialize the Adzuna API Manager.

        :param country: The country for job search (default is 'us').
        """
        self.base_url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/"
        self.app_id = APP_ID
        self.app_key = APP_KEY



    def search_jobs(self, query: str, location: str = "", results_per_page: int = 10, page: int = 1) -> dict:
        """
        Search for jobs using the Adzuna API.

        :param query: The job title or keywords to search for.
        :param location: The location to filter jobs (optional).
        :param results_per_page: Number of results per page (default is 10).
        :param page: The page number to fetch (default is 1).
        :return: A dictionary containing the API response.
        """
        url = f"{self.base_url}{page}"
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            # "what": query,
            "what": "Software Developer",
            # "where": location,
            "where": "United States",
            "results_per_page": results_per_page
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error during Adzuna API request: {e}")
            return {"error": str(e)}



    def extract_job_data(self, api_response: dict) -> list:
        """
        Extract relevant job data from the API response.

        :param api_response: The raw response from the Adzuna API.
        :return: A list of dictionaries containing job details.
        """
        jobs = []
        if "results" in api_response and isinstance(api_response["results"], list):
            for job in api_response["results"]:
                jobs.append({
                    "title": job.get("title", "No title provided"),
                    "company": job.get("company", {}).get("display_name", "Unknown company"),
                    "location": job.get("location", {}).get("display_name", "Unknown location"),
                    "latitude": job.get("location", {}).get("latitude"),
                    "longitude": job.get("location", {}).get("longitude"),
                    "category": job.get("category", {}).get("label", "Unknown category"),
                    "salary_min": job.get("salary_min", "Salary not provided"),
                    "salary_max": job.get("salary_max", "Salary not provided"),
                    "salary_is_predicted": "Yes" if job.get("salary_is_predicted") == "1" else "No",
                    "description": job.get("description", "")[:300] + "..." if len(job.get("description", "")) > 300 else job.get("description"),
                    "redirect_url": job.get("redirect_url", "#"),
                    "created": job.get("created", "Unknown date")
                })
        else:
            print("No results found in the API response.")
        return jobs


# Example usage:
# adzuna = AdzunaAPIManager()
# response = adzuna.search_jobs(query="Software Developer", location="New York", results_per_page=5)
# jobs = adzuna.extract_job_data(response)
# print(jobs)
