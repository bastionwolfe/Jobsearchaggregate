import requests
from greenhouse import fetch_greenhouse_jobs
from lever import fetch_lever_jobs


GREENHOUSE_BOARDS = {
    "Gusto": "gusto",
    "True Anomaly": "trueanomalyinc",
}

LEVER_SITES = {
    "Palantir": "palantir",
}


def test_greenhouse():
    print("       GREENHOUSE TEST")

    for company, board_token in GREENHOUSE_BOARDS.items():

        print(f"\nTesting: {company}")
        print(f"Board token: {board_token}")

        try:
            jobs = fetch_greenhouse_jobs(board_token)

            print(f"SUCCESS")
            print(f"Jobs returned: {len(jobs)}")

            for job in jobs[:3]:
                print(
                    f"  - {job.get('title', 'Unknown')} "
                    f"| {job.get('location', {}).get('name', '')}"
                )

        except Exception as error:
            print(f"FAILED: {error}")


def test_lever():
    print("          LEVER TEST")

    for company, site in LEVER_SITES.items():

        print(f"\nTesting: {company}")
        print(f"Site: {site}")

        try:
            jobs = fetch_lever_jobs(site)

            print("SUCCESS")
            print(f"Jobs returned: {len(jobs)}")

            for job in jobs[:3]:

                categories = job.get(
                    "categories",
                    {}
                )

                location = ""

                if isinstance(categories, dict):
                    location = categories.get(
                        "location",
                        ""
                    )

                print(
                    f"  - {job.get('text', 'Unknown')} "
                    f"| {location}"
                )

        except Exception as error:
            print(f"FAILED: {error}")


if __name__ == "__main__":

    print("        ATS CONNECTION TEST")

    test_greenhouse()
    test_lever()

    print("             DONE")









url = "https://www.higheredjobs.com/rss/categoryFeed.cfm?catID=161"

headers = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(url, headers=headers, timeout=20)

print("Status:", r.status_code)
print("Content-Type:", r.headers.get("Content-Type"))
print("Length:", len(r.content))
print(r.text[:500])

