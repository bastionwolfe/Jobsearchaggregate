import requests


LEVER_API = (
    "https://api.lever.co/v0/postings/"
)


def fetch_lever_jobs(site):


    url = (
        f"{LEVER_API}"
        f"{site}?mode=json"
    )

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    return response.json()