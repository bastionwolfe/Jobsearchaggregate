import re
from datetime import datetime, timezone
from html import unescape


def clean_text(text):
    """
    Clean HTML and normalize whitespace.
    """

    if not text:
        return ""

    if not isinstance(text, str):
        return ""

    # Decode HTML entities
    text = unescape(text)

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# SOURCE HELPERS

def is_jobicy_source(source):
    return source.startswith("Jobicy")


def is_wwr_source(source):
    return source.startswith("We Work Remotely")


def is_remote_first_source(source):
    return source.startswith("Remote First Jobs")


def is_higheredjobs_source(source):
    return source.startswith("HigherEdJobs")


# RSS DESCRIPTION

def get_description(entry, source=None):
    """
    Get the best available description from an RSS entry.

    Different RSS feeds use different fields.

    Priority:
        1. content
        2. summary
        3. description
    """

    # HigherEdJobs

    if is_higheredjobs_source(source):
        return ""

    # Jobicy

    content = entry.get("content", "")

    if isinstance(content, list):

        parts = []

        for item in content:

            if isinstance(item, dict):

                value = item.get(
                    "value",
                    ""
                )

                if value:
                    parts.append(value)

        if parts:
            return clean_text(
                " ".join(parts)
            )

    elif isinstance(content, str):

        if content:
            return clean_text(content)

    # Standard RSS summary

    description = entry.get(
        "summary",
        ""
    )

    if description:
        return clean_text(description)

    # Some RSS feeds use description

    description = entry.get(
        "description",
        ""
    )

    if description:
        return clean_text(description)

    return ""


# HIGHEREDJOBS

def get_higheredjobs_company_location(entry):

    summary = entry.get(
        "summary",
        ""
    )

    if not isinstance(summary, str):
        return "", ""

    summary = clean_text(summary)

    if not summary:
        return "", ""

    match = re.match(
        r"^(.*?)\s*\(([^()]*)\)\s*$",
        summary
    )

    if match:

        company = match.group(1).strip()
        location = match.group(2).strip()

        return company, location

    return summary, ""


# RSS TITLE + COMPANY

def get_title_and_company(entry, source):


    raw_title = clean_text(
        entry.get(
            "title",
            "Untitled"
        )
    )

    company = ""

    # Python Jobs

    if source == "Python Jobs":

        if "," in raw_title:

            title, company = raw_title.rsplit(
                ",",
                1
            )

            return (
                title.strip(),
                company.strip()
            )

    # Jobicy

    if is_jobicy_source(source):

        company = entry.get(
            "job_listing_company",
            ""
        )

        if isinstance(company, str):
            company = clean_text(company)

        return raw_title, company

    # We Work Remotely

    if is_wwr_source(source):

        company = entry.get(
            "company",
            ""
        )

        if isinstance(company, str):
            company = clean_text(company)

        return raw_title, company

    # Remote First Jobs

    if is_remote_first_source(source):

        match = re.match(
            r"^(.*?)\s+at\s+(.+)$",
            raw_title,
            re.IGNORECASE
        )

        if match:

            title = match.group(1).strip()
            company = match.group(2).strip()

            return title, company

    # Foss Jobs

    if source == "Foss Jobs":

        company = entry.get(
            "company",
            ""
        )

        if isinstance(company, str):

            return (
                raw_title,
                clean_text(company)
            )

        return raw_title, ""

    # HigherEdJobs

    if is_higheredjobs_source(source):

        company, _ = (
            get_higheredjobs_company_location(
                entry
            )
        )

        return raw_title, company

    # Generic fallback

    company = entry.get(
        "company",
        ""
    )

    if isinstance(company, str):
        company = clean_text(company)

    return raw_title, company


# RSS LOCATION

def get_location(entry, source):
    """
    Extract a normalized location from an RSS entry.
    """

    # Jobicy

    if is_jobicy_source(source):

        location = entry.get(
            "job_listing_location",
            ""
        )

        return clean_text(location)

    # We Work Remotely

    if is_wwr_source(source):

        region = clean_text(
            entry.get(
                "region",
                ""
            )
        )

        country = clean_text(
            entry.get(
                "country",
                ""
            )
        )

        state = clean_text(
            entry.get(
                "state",
                ""
            )
        )

        parts = []

        if region:
            parts.append(region)

        if state and state not in parts:
            parts.append(state)

        if country and country not in parts:
            parts.append(country)

        return ", ".join(parts)

    # HigherEdJobs

    if is_higheredjobs_source(source):

        _, location = (
            get_higheredjobs_company_location(
                entry
            )
        )

        return location

    # Generic location

    location = entry.get(
        "location",
        ""
    )

    if isinstance(location, str) and location:

        return clean_text(location)

    # Python Jobs

    if source == "Python Jobs":

        raw_summary = entry.get(
            "summary",
            ""
        )

        if raw_summary:

            first_part = raw_summary.split(
                "<p>",
                1
            )[0]

            first_part = clean_text(
                first_part
            )

            if first_part:
                return first_part

        return ""

    # Remote First Jobs

    if is_remote_first_source(source):
        return ""

    # Foss Jobs

    if source == "Foss Jobs":
        return ""

    return ""


# RSS URL

def get_url(entry):
    """
    Get the job URL from an RSS entry.
    """

    url = entry.get(
        "link",
        ""
    )

    if isinstance(url, str):
        return url.strip()

    return ""


# RSS PUBLISHED DATE

def get_published(entry):
    """
    Get the raw publication/update date from an RSS entry.

    app.py handles the actual date parsing.
    """

    published = entry.get(
        "published",
        entry.get(
            "updated",
            ""
        )
    )

    if isinstance(published, str):
        return published.strip()

    return ""


# RSS NORMALIZER

def normalize_job(entry, source):
    """
    Convert a raw RSS entry into the standard job format.
    """

    title, company = get_title_and_company(
        entry,
        source
    )

    location = get_location(
        entry,
        source
    )

    description = get_description(
        entry,
        source
    )

    url = get_url(entry)

    published = get_published(entry)

    return {
        "title": title,
        "company": company,
        "location": location,
        "description": description,
        "url": url,
        "published": published,
        "source": source,
        "source_id": "",
    }


# GREENHOUSE NORMALIZER

def normalize_greenhouse_job(job, company):
    """
    Convert a Greenhouse API job into our standard format.

    The Greenhouse list endpoint provides updated_at.
    We use that for the ingestion date window.
    """

    title = clean_text(
        job.get(
            "title",
            ""
        )
    )

    location_data = job.get(
        "location",
        {}
    )

    location = ""

    if isinstance(location_data, dict):

        location = clean_text(
            location_data.get(
                "name",
                ""
            )
        )

    description = clean_text(
        job.get(
            "content",
            ""
        )
    )

    url = job.get(
        "absolute_url",
        ""
    )

    if isinstance(url, str):
        url = url.strip()

    published = job.get(
        "updated_at",
        ""
    )

    if not isinstance(published, str):
        published = ""

    return {
        "title": title,
        "company": company,
        "location": location,
        "description": description,
        "url": url,
        "published": published,
        "source": f"Greenhouse - {company}",
        "source_id": str(
            job.get(
                "id",
                ""
            )
        ),
    }


# LEVER NORMALIZER

def normalize_lever_job(job, company):
    """
    Convert a Lever API job into our standard format.
    """

    title = clean_text(
        job.get(
            "text",
            ""
        )
    )

    categories = job.get(
        "categories",
        {}
    )

    location = ""

    if isinstance(categories, dict):

        location = clean_text(
            categories.get(
                "location",
                ""
            )
        )

        if not location:

            all_locations = categories.get(
                "allLocations",
                []
            )

            if isinstance(
                all_locations,
                list
            ):

                locations = [
                    clean_text(str(item))
                    for item in all_locations
                    if item
                ]

                location = ", ".join(
                    dict.fromkeys(
                        locations
                    )
                )

    description = clean_text(
        job.get(
            "descriptionPlain",
            ""
        )
    )

    url = job.get(
        "hostedUrl",
        ""
    )

    if isinstance(url, str):
        url = url.strip()

    published = ""

    created_at = job.get(
        "createdAt"
    )

    if created_at is not None:

        try:

            timestamp = (
                int(created_at) / 1000
            )

            published = datetime.fromtimestamp(
                timestamp,
                tz=timezone.utc
            ).isoformat()

        except (
            ValueError,
            TypeError,
            OverflowError
        ):

            published = ""

    return {
        "title": title,
        "company": company,
        "location": location,
        "description": description,
        "url": url,
        "published": published,
        "source": f"Lever - {company}",
        "source_id": str(
            job.get(
                "id",
                ""
            )
        ),
    }