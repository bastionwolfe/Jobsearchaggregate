import sqlite3
import feedparser

from datetime import (
    datetime,
    timedelta,
    timezone
)

from normalizer import (
    normalize_job,
    normalize_greenhouse_job,
    normalize_lever_job,
)

from greenhouse import (
    fetch_greenhouse_jobs
)

from lever import (
    fetch_lever_jobs
)

from sources import (
    RSS_FEEDS,
    GREENHOUSE_BOARDS,
    LEVER_SITES,
)


DB_FILE = "jobs.db"

DAYS_TO_KEEP = 14


# DATABASE

def init_database():

    conn = sqlite3.connect(
        DB_FILE
    )

    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            company TEXT,

            location TEXT,

            description TEXT,

            url TEXT UNIQUE NOT NULL,

            published TEXT,

            discovered_at TEXT NOT NULL,

            source TEXT,

            source_id TEXT

        )
    """)

    conn.commit()

    return conn


def migrate_database(conn):
    """
    Add columns that may not exist in an older jobs.db.
    SQLite CREATE TABLE IF NOT EXISTS does not modify
    an existing table.
    """

    columns = conn.execute(
        "PRAGMA table_info(jobs)"
    ).fetchall()

    column_names = {
        column[1]
        for column in columns
    }

    if "source_id" not in column_names:

        print(
            "Migrating database: "
            "adding source_id"
        )

        conn.execute("""
            ALTER TABLE jobs
            ADD COLUMN source_id TEXT
        """)

        conn.commit()

    if "applied" not in column_names:

        print(
            "Migrating database: "
            "adding applied"
        )

        conn.execute("""
            ALTER TABLE jobs
            ADD COLUMN applied INTEGER NOT NULL DEFAULT 0
        """)

        conn.commit()


# RSS DATE PARSING

def parse_published_date(entry):
    """
    Parse the publication/update date from an RSS entry.

    Returns a timezone-aware datetime or None.
    """

    if entry.get(
        "published_parsed"
    ):

        return datetime(
            *entry.published_parsed[:6],
            tzinfo=timezone.utc
        )

    if entry.get(
        "updated_parsed"
    ):

        return datetime(
            *entry.updated_parsed[:6],
            tzinfo=timezone.utc
        )

    return None


# API DATE PARSING

def parse_api_date(value):
    """
    Parse an ISO-8601 date returned by an API.

    Returns a timezone-aware datetime or None.
    """

    if not value:
        return None

    if not isinstance(
        value,
        str
    ):
        return None

    try:

        parsed = datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00"
            )
        )

        if parsed.tzinfo is None:

            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed

    except ValueError:

        return None


# RSS FETCHING

def fetch_feed(
    feed_name,
    feed_url
):

    print(
        f"\nFetching: {feed_name}"
    )

    print(
        f"URL: {feed_url}"
    )

    feed = feedparser.parse(
        feed_url
    )

    if feed.bozo:

        print(
            "Warning: Feed may be malformed: "
            f"{feed.bozo_exception}"
        )

    entries = feed.entries

    print(
        f"Feed returned "
        f"{len(entries)} entries"
    )

    return entries


# SAVE RSS JOB

def save_job(
    conn,
    entry,
    source
):

    job = normalize_job(
        entry,
        source
    )

    title = job["title"]
    url = job["url"]

    if not url:
        return False

    published_date = parse_published_date(
        entry
    )

    if published_date is None:

        print(
            f"Skipping job with unknown date: "
            f"{title}"
        )

        return False

    cutoff_date = (
        datetime.now(timezone.utc)
        - timedelta(
            days=DAYS_TO_KEEP
        )
    )

    if published_date < cutoff_date:
        return False

    published = (
        published_date.isoformat()
    )

    conn.execute("""
        INSERT OR IGNORE INTO jobs
        (
            title,
            company,
            location,
            description,
            url,
            published,
            discovered_at,
            source,
            source_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        job["title"],

        job["company"],

        job["location"],

        job["description"],

        job["url"],

        published,

        datetime.now(
            timezone.utc
        ).isoformat(),

        job["source"],

        job.get(
            "source_id",
            ""
        )

    ))

    return (
        conn.execute(
            "SELECT changes()"
        ).fetchone()[0] > 0
    )


# SAVE API JOB

def save_normalized_job(
    conn,
    job
):
    """
    Save a job that has already been normalized
    by a Greenhouse or Lever adapter.
    """

    title = job.get(
        "title",
        ""
    )

    url = job.get(
        "url",
        ""
    )

    if not url:

        print(
            f"Skipping job with no URL: "
            f"{title}"
        )

        return False

    published_date = parse_api_date(
        job.get(
            "published",
            ""
        )
    )

    if published_date is None:

        print(
            f"Skipping job with unknown "
            f"API date: {title}"
        )

        return False

    cutoff_date = (
        datetime.now(timezone.utc)
        - timedelta(
            days=DAYS_TO_KEEP
        )
    )

    if published_date < cutoff_date:
        return False

    published = (
        published_date.isoformat()
    )

    conn.execute("""
        INSERT OR IGNORE INTO jobs
        (
            title,
            company,
            location,
            description,
            url,
            published,
            discovered_at,
            source,
            source_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        job.get(
            "title",
            ""
        ),

        job.get(
            "company",
            ""
        ),

        job.get(
            "location",
            ""
        ),

        job.get(
            "description",
            ""
        ),

        job.get(
            "url",
            ""
        ),

        published,

        datetime.now(
            timezone.utc
        ).isoformat(),

        job.get(
            "source",
            ""
        ),

        job.get(
            "source_id",
            ""
        )

    ))

    return (
        conn.execute(
            "SELECT changes()"
        ).fetchone()[0] > 0
    )


# GREENHOUSE IMPORT

def import_greenhouse(
    conn,
    cutoff_date
):

    total_recent = 0
    total_new = 0

    for company, board_token in (
        GREENHOUSE_BOARDS.items()
    ):

        print(
            "\n-----------------------------------"
        )

        print(
            f"Fetching Greenhouse: {company}"
        )

        print(
            f"Board token: {board_token}"
        )

        try:

            jobs = fetch_greenhouse_jobs(
                board_token
            )

            print(
                f"Greenhouse returned "
                f"{len(jobs)} jobs"
            )

        except Exception as error:

            print(
                f"Greenhouse error for "
                f"{company}: {error}"
            )

            continue

        recent_count = 0
        new_count = 0

        for raw_job in jobs:

            job = normalize_greenhouse_job(
                raw_job,
                company
            )

            published_date = parse_api_date(
                job.get(
                    "published",
                    ""
                )
            )

            if published_date is None:
                continue

            if published_date < cutoff_date:
                continue

            recent_count += 1

            if save_normalized_job(
                conn,
                job
            ):

                new_count += 1

        total_recent += recent_count
        total_new += new_count

        print(
            f"Recent jobs: {recent_count}"
        )

        print(
            f"New jobs saved: {new_count}"
        )

    return total_recent, total_new


# LEVER IMPORT

def import_lever(
    conn,
    cutoff_date
):

    total_recent = 0
    total_new = 0

    for company, site in (
        LEVER_SITES.items()
    ):

        print(
            "\n-----------------------------------"
        )

        print(
            f"Fetching Lever: {company}"
        )

        print(
            f"Site: {site}"
        )

        try:

            jobs = fetch_lever_jobs(
                site
            )

            print(
                f"Lever returned "
                f"{len(jobs)} jobs"
            )

        except Exception as error:

            print(
                f"Lever error for "
                f"{company}: {error}"
            )

            continue

        recent_count = 0
        new_count = 0

        for raw_job in jobs:

            job = normalize_lever_job(
                raw_job,
                company
            )

            published_date = parse_api_date(
                job.get(
                    "published",
                    ""
                )
            )

            if published_date is None:

                # Lever may not provide a usable
                # timestamp on every posting.
                #
                # Do not guess.
                continue

            if published_date < cutoff_date:
                continue

            recent_count += 1

            if save_normalized_job(
                conn,
                job
            ):

                new_count += 1

        total_recent += recent_count
        total_new += new_count

        print(
            f"Recent jobs: {recent_count}"
        )

        print(
            f"New jobs saved: {new_count}"
        )

    return total_recent, total_new


# MAIN

def main():

    conn = init_database()

    migrate_database(
        conn
    )

    total_new = 0
    total_recent = 0

    cutoff_date = (
        datetime.now(timezone.utc)
        - timedelta(
            days=DAYS_TO_KEEP
        )
    )

    print(
        "\n==================================="
    )

    print(
        "       JOB FINDER IMPORT"
    )

    print(
        "==================================="
    )

    print(
        f"Keeping jobs from: "
        f"{cutoff_date.isoformat()}"
    )

    print(
        f"Days: {DAYS_TO_KEEP}"
    )

    # RSS

    for feed_name, feed_url in (
        RSS_FEEDS.items()
    ):

        entries = fetch_feed(
            feed_name,
            feed_url
        )

        recent_count = 0
        new_count = 0

        for entry in entries:

            published_date = (
                parse_published_date(
                    entry
                )
            )

            if published_date is None:
                continue

            if published_date < cutoff_date:
                continue

            recent_count += 1

            if save_job(
                conn,
                entry,
                feed_name
            ):

                new_count += 1

        total_recent += recent_count
        total_new += new_count

        print(
            f"Recent jobs: {recent_count}"
        )

        print(
            f"New jobs saved: {new_count}"
        )

    # GREENHOUSE

    greenhouse_recent, greenhouse_new = (
        import_greenhouse(
            conn,
            cutoff_date
        )
    )

    total_recent += greenhouse_recent
    total_new += greenhouse_new

    # LEVER

    lever_recent, lever_new = (
        import_lever(
            conn,
            cutoff_date
        )
    )

    total_recent += lever_recent
    total_new += lever_new

    # COMMIT

    conn.commit()

    conn.close()

    print(
        "\n==================================="
    )

    print(
        f"Recent jobs found: {total_recent}"
    )

    print(
        f"New jobs saved:    {total_new}"
    )

    print(
        "==================================="
    )


if __name__ == "__main__":
    main()