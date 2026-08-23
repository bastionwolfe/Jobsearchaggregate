import requests


GREENHOUSE_API = (
    "https://boards-api.greenhouse.io/v1/boards/"
)


def fetch_greenhouse_jobs(board_token):
    """
    Fetch publicly published jobs from a Greenhouse job board.

    Greenhouse's public Job Board API does not require
    authentication for GET requests.

    content=true includes the job description,
    departments, and offices.
    """

    url = (
        f"{GREENHOUSE_API}"
        f"{board_token}/jobs"
        f"?content=true"
    )

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data.get("jobs", [])