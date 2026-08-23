import sqlite3

from datetime import datetime, timedelta, timezone


DB_FILE = "jobs.db"

DAYS_TO_KEEP = 14


# DATABASE CONNECTION

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# JOB QUERIES

def search_jobs(
    keywords=None,
    location=None,
    limit=100,
    sort_order="newest"
):
    """
    Search active/unapplied jobs.
    Jobs older than 14 days and applied jobs are excluded.
    """

    conn = get_connection()

    cutoff_date = (
        datetime.now(timezone.utc)
        - timedelta(days=DAYS_TO_KEEP)
    ).isoformat()

    query = """
        SELECT
            id,
            title,
            company,
            location,
            description,
            url,
            published,
            source,
            applied
        FROM jobs
        WHERE applied = 0
        AND published >= ?
    """

    parameters = [cutoff_date]

    if keywords:

        keyword_conditions = []

        for keyword in keywords:

            keyword_conditions.append("""
                (
                    title LIKE ?
                    OR company LIKE ?
                    OR location LIKE ?
                    OR description LIKE ?
                    OR source LIKE ?
                    OR url LIKE ?
                )
            """)

            search_term = f"%{keyword}%"

            parameters.extend([
                search_term,
                search_term,
                search_term,
                search_term,
                search_term,
                search_term
            ])

        query += """
            AND (
        """

        query += " OR ".join(
            keyword_conditions
        )

        query += ")"

    if location:

        query += """
            AND location LIKE ?
        """

        parameters.append(
            f"%{location}%"
        )

    if sort_order == "oldest":

        query += """
            ORDER BY published ASC
        """

    elif sort_order == "location":

        query += """
            ORDER BY location COLLATE NOCASE ASC,
                     published DESC
        """

    else:

        query += """
            ORDER BY published DESC
        """

    query += """
        LIMIT ?
    """

    parameters.append(limit)

    jobs = conn.execute(
        query,
        parameters
    ).fetchall()

    conn.close()

    return jobs


def get_active_jobs(
    keywords=None,
    sort_order="newest"
):
    # Return unapplied jobs that are 14 days old or newer.

    return search_jobs(
        keywords=keywords,
        sort_order=sort_order,
        limit=10000
    )


def get_older_jobs(
    keywords=None,
    sort_order="newest"
):
    """
    Return unapplied jobs that have aged beyond 14 days.
    These jobs were previously imported while they were
    within the 14-day import window.
    """

    conn = get_connection()

    cutoff_date = (
        datetime.now(timezone.utc)
        - timedelta(days=DAYS_TO_KEEP)
    ).isoformat()

    query = """
        SELECT
            id,
            title,
            company,
            location,
            description,
            url,
            published,
            source,
            applied
        FROM jobs
        WHERE applied = 0
        AND published < ?
    """

    parameters = [cutoff_date]

    if keywords:

        keyword_conditions = []

        for keyword in keywords:

            keyword_conditions.append("""
                (
                    title LIKE ?
                    OR company LIKE ?
                    OR location LIKE ?
                    OR description LIKE ?
                    OR source LIKE ?
                    OR url LIKE ?
                )
            """)

            search_term = f"%{keyword}%"

            parameters.extend([
                search_term,
                search_term,
                search_term,
                search_term,
                search_term,
                search_term
            ])

        query += """
            AND (
        """

        query += " OR ".join(
            keyword_conditions
        )

        query += ")"

    if sort_order == "oldest":

        query += """
            ORDER BY published ASC
        """

    elif sort_order == "location":

        query += """
            ORDER BY location COLLATE NOCASE ASC,
                     published DESC
        """

    else:

        query += """
            ORDER BY published DESC
        """

    jobs = conn.execute(
        query,
        parameters
    ).fetchall()

    conn.close()

    return jobs


def get_applied_jobs(
    keywords=None,
    sort_order="newest"
):
    """
    Return all applied jobs regardless of age.
    """

    conn = get_connection()

    query = """
        SELECT
            id,
            title,
            company,
            location,
            description,
            url,
            published,
            source,
            applied
        FROM jobs
        WHERE applied = 1
    """

    parameters = []

    if keywords:

        keyword_conditions = []

        for keyword in keywords:

            keyword_conditions.append("""
                (
                    title LIKE ?
                    OR company LIKE ?
                    OR location LIKE ?
                    OR description LIKE ?
                    OR source LIKE ?
                    OR url LIKE ?
                )
            """)

            search_term = f"%{keyword}%"

            parameters.extend([
                search_term,
                search_term,
                search_term,
                search_term,
                search_term,
                search_term
            ])

        query += """
            AND (
        """

        query += " OR ".join(
            keyword_conditions
        )

        query += ")"

    if sort_order == "oldest":

        query += """
            ORDER BY published ASC
        """

    elif sort_order == "location":

        query += """
            ORDER BY location COLLATE NOCASE ASC,
                     published DESC
        """

    else:

        query += """
            ORDER BY published DESC
        """

    jobs = conn.execute(
        query,
        parameters
    ).fetchall()

    conn.close()

    return jobs


# APPLIED STATUS

def mark_job_applied(job_id):
    """
    Mark a job as applied.
    """

    conn = get_connection()

    conn.execute(
        """
        UPDATE jobs
        SET applied = 1
        WHERE id = ?
        """,
        (job_id,)
    )

    conn.commit()
    conn.close()


def mark_job_unapplied(job_id):


    conn = get_connection()

    conn.execute(
        """
        UPDATE jobs
        SET applied = 0
        WHERE id = ?
        """,
        (job_id,)
    )

    conn.commit()
    conn.close()


# COUNTS

def get_active_job_count():
    return len(
        get_active_jobs()
    )


def get_older_job_count():
    return len(
        get_older_jobs()
    )


def get_applied_job_count():
    return len(
        get_applied_jobs()
    )


def get_job_count():
    """
    Return the total number of jobs in the database.
    """

    conn = get_connection()

    result = conn.execute(
        "SELECT COUNT(*) FROM jobs"
    ).fetchone()

    conn.close()

    return result[0]

# LEGACY FUNCTION

def get_all_jobs(sort_order="newest"):
    """
    Backwards-compatible helper.

    Returns active jobs.
    """

    return get_active_jobs(
        sort_order=sort_order
    )


# TEST

if __name__ == "__main__":

    jobs = get_active_jobs(
        keywords=["Python", "C++"]
    )

    print(
        f"Found {len(jobs)} active jobs:\n"
    )

    for job in jobs:

        print(job["title"])
        print(job["company"])
        print(job["location"])
        print(job["published"])
        print(job["source"])
        print(job["url"])

        print("-" * 60)