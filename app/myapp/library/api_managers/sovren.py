import requests
from django.conf import settings


SOVREN_ACCOUNT_ID = settings.SOVREN_ACCOUNT_ID
SOVREN_SERVICE_KEY = settings.SOVREN_SERVICE_KEY


class SovrenAPIManager:
    def __init__(self, base_url: str = "https://api.sovren.com/"):
        """
        Initialize the Sovren ATS Manager.

        :param base_url: The base URL for Sovren API (default is production URL).
        """
        global SOVREN_ACCOUNT_ID, SOVREN_SERVICE_KEY

        self.account_id = SOVREN_ACCOUNT_ID
        self.service_key = SOVREN_SERVICE_KEY
        self.base_url = base_url.rstrip('/') + '/v10/'
        self.headers = {
            "Sovren-AccountId": self.account_id,
            "Sovren-ServiceKey": self.service_key,
            "Content-Type": "application/json"
        }

    def parse_job(self, job_description: str) -> dict:
        """
        Parse a job description using the Sovren API.

        :param job_description: The job description text.
        :return: Parsed job data as a dictionary.
        """
        url = f"{self.base_url}joborderparser"
        payload = {
            "DocumentAsString": job_description,
            "OutputHtml": False
        }
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error parsing job description: {e}")
            return {"error": str(e)}

    def parse_resume(self, resume_text: str) -> dict:
        """
        Parse a resume using the Sovren API.

        :param resume_text: The resume text.
        :return: Parsed resume data as a dictionary.
        """
        url = f"{self.base_url}resumeparser"
        payload = {
            "DocumentAsString": resume_text,
            "OutputHtml": False
        }
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error parsing resume: {e}")
            return {"error": str(e)}

    def match_job_to_resume(self, parsed_job: dict, parsed_resume: dict) -> dict:
        """
        Match a parsed job to a parsed resume using the Sovren API.

        :param parsed_job: Parsed job data from parse_job.
        :param parsed_resume: Parsed resume data from parse_resume.
        :return: Matching score and details as a dictionary.
        """
        url = f"{self.base_url}matcher/match"
        payload = {
            "Jobs": [parsed_job],
            "Candidates": [parsed_resume]
        }
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error matching job to resume: {e}")
            return {"error": str(e)}

    def get_score(self, job_description: str, resume_text: str) -> dict:
        """
        High-level method to parse a job and resume, and get a matching score.

        :param job_description: The job description text.
        :param resume_text: The resume text.
        :return: Matching score and details as a dictionary.
        """
        parsed_job = self.parse_job(job_description)
        parsed_resume = self.parse_resume(resume_text)

        if "error" in parsed_job or "error" in parsed_resume:
            return {
                "error": "Failed to parse job or resume.",
                "job_error": parsed_job.get("error"),
                "resume_error": parsed_resume.get("error")
            }

        return self.match_job_to_resume(parsed_job.get("Value"), parsed_resume.get("Value"))

# Example usage:
# sovren = SovrenAPIManager()
# job_description = "Job description text here."
# resume_text = "Resume text here."
# result = sovren.get_score(job_description, resume_text)
# print(result)
