# Job Finder

A desktop job-search aggregator built with Python that collects job postings from RSS feeds and public ATS APIs, normalizes them into a common format, stores them in SQLite, and provides a desktop interface for searching and tracking applications.

The project was built to make job searching less repetitive by bringing listings from multiple sources into a single local application.

## Features

* Aggregate job postings from multiple sources

  * RSS feeds
  * Greenhouse public job board API
  * Lever public postings API
* Normalize different job formats into a consistent schema
* Store job postings locally with SQLite
* Automatically filter incoming jobs to a configurable 14-day window
* Prevent duplicate listings using unique job URLs
* Search across:

  * Job title
  * Company
  * Location
  * Description
  * Source
  * URL
* Filter jobs by location
* Sort jobs by:

  * Newest
  * Oldest
  * Location
* Track application status
* Separate views for:

  * Active jobs
  * Older jobs
  * Applied jobs
* Open the original job posting directly from the application
* Handle source-specific data differences through normalization
* Preserve older jobs in the database instead of deleting them when they age out of the active window

## How It Works

The application collects job postings from RSS feeds, Greenhouse, and Lever.

Each source provides job data in a different format. The normalization layer converts these formats into a common structure containing fields such as:

* Title
* Company
* Location
* Description
* URL
* Publication date
* Source
* Source ID

The normalized jobs are stored in a local SQLite database. The query layer handles searching, filtering, sorting, and application status. The Tkinter GUI provides the interface for reviewing and managing the collected jobs.

## Architecture

### Data Collection

`app.py` is responsible for running the import process.

It:

1. Initializes the SQLite database.
2. Performs database migrations when necessary.
3. Fetches jobs from configured RSS feeds.
4. Fetches jobs from configured Greenhouse boards.
5. Fetches jobs from configured Lever sites.
6. Normalizes incoming data.
7. Filters out jobs outside the configured date window.
8. Inserts new jobs into SQLite.
9. Reports import statistics.

The default import window is **14 days**.

### Source Adapters

Source-specific API logic is kept separate from the main application.

#### Greenhouse

`greenhouse.py` communicates with Greenhouse's public job board API and retrieves available job postings.

#### Lever

`lever.py` communicates with Lever's public postings API and retrieves available job postings.

Keeping these integrations in separate modules makes it easier to add additional job sources without changing the core application.

### Normalization

`normalizer.py` handles differences between job sources.

RSS feeds can have substantially different field names and structures. The normalizer contains source-specific handling while producing the same internal job structure.

It also:

* Removes HTML tags
* Decodes HTML entities
* Normalizes whitespace
* Extracts company names
* Extracts locations
* Extracts descriptions
* Converts source-specific timestamps
* Handles missing fields

This keeps source-specific parsing logic out of the database and GUI layers.

### Database

Jobs are stored in a local SQLite database (`jobs.db`).

Each job record contains:

* ID
* Title
* Company
* Location
* Description
* URL
* Publication date
* Discovery date
* Source
* Source ID
* Applied status

Job URLs are unique, allowing SQLite to prevent the same posting from being inserted multiple times.

The application also includes basic database migration logic so existing databases can be updated when new columns are introduced.

### Search and Filtering

`filter.py` provides the application's database query layer.

Search terms can match against:

* Title
* Company
* Location
* Description
* Source
* URL

Jobs can also be filtered by location and sorted by publication date or location.

The query layer separates database operations from the GUI, allowing the interface to focus on presentation and user interaction.

## Desktop Interface

The graphical interface is built with Python's built-in Tkinter toolkit.

The application provides three main sections.

### Active Jobs

Jobs that are within the current 14-day active window and have not been marked as applied.

### Applied Jobs

Jobs that have been marked as applied. Applied jobs remain available regardless of their age.

### Older Jobs

Previously imported jobs that have aged beyond the active 14-day window but have not been marked as applied.

The interface also provides:

* Search
* Sorting
* Job details
* Full job descriptions
* Application status tracking
* Direct links to the original posting
* Job counts for each section
* Refresh functionality

## Requirements

* Python 3
* `requests`
* `feedparser`
* Tkinter

Tkinter is included with many Python installations. On some Linux distributions it may need to be installed separately.

## Installation

Clone the repository:

```bash
git clone https://github.com/bastionwolfe/Jobsearchaggregate.git
cd Jobsearchaggregate
```

Install the Python dependencies:

```bash
pip install requests feedparser
```

If a `requirements.txt` file is added to the project, dependencies can instead be installed with:

```bash
pip install -r requirements.txt
```

## Configuration

Job sources are configured in `sources.py`.

RSS sources:

```python
RSS_FEEDS = {
    # "Source Name": "RSS URL"
}
```

Greenhouse boards:

```python
GREENHOUSE_BOARDS = {
    # "Company Name": "board-token"
}
```

Lever sites:

```python
LEVER_SITES = {
    # "Company Name": "site-name"
}
```

This keeps source configuration separate from the application's core ingestion logic.

## Running the Application

### Import Jobs

Run the importer:

```bash
python app.py
```

This initializes the database, fetches configured sources, normalizes the results, and stores new postings.

### Launch the GUI

Run:

```bash
python gui.py
```

The desktop Job Finder application will open and load the jobs stored in `jobs.db`.

A typical workflow is:

1. Configure job sources in `sources.py`
2. Run `app.py` to collect jobs
3. Run `gui.py` to open the desktop application
4. Search and review job postings
5. Mark applications as applied

## Design Decisions

### Local SQLite Database

SQLite was chosen because the application is intended to run locally and does not require a separate database server.

It provides persistent storage while keeping the project simple to deploy.

### Normalization Layer

Different job sources expose different schemas and conventions.

Rather than allowing those differences to spread throughout the application, source-specific parsing is handled in `normalizer.py`.

This makes the database and GUI independent of the original source format.

### 14-Day Active Window

New imports are limited to jobs published or updated within the configured 14-day window.

Older jobs are retained in the database rather than immediately deleted. This allows the application to distinguish between current and older opportunities while preserving historical records.

### Duplicate Prevention

The job URL is stored as a unique field in SQLite.

New records use `INSERT OR IGNORE`, allowing repeated imports without continually creating duplicate listings.

### Timezone-Aware Dates

Dates from RSS feeds and APIs are converted into timezone-aware `datetime` objects before being compared.

This helps prevent timestamps from different sources from being incorrectly compared as if they were all using the same local timezone.

### Source Isolation

Errors from individual Greenhouse and Lever sources are caught independently during import.

A failure from one configured company does not prevent the remaining sources from being processed.

## Future Improvements

Potential areas for future development include:

* Add more job sources
* Improve duplicate detection beyond URL matching
* Add automated tests
* Add background or scheduled imports
* Add configurable search filters
* Add salary information when available
* Add remote/hybrid/on-site filtering
* Improve job ranking
* Add export functionality
* Improve the GUI
* Add structured logging
* Package the application for easier installation

## Project Goals

This project was built as a practical exploration of:

* Python application architecture
* API integration
* RSS parsing
* Data normalization
* SQLite database design
* Database migrations
* Search and filtering
* Desktop GUI development
* Error handling
* Working with inconsistent external data

The main goal was to build a useful application while keeping the different data sources separated from the application's core logic.

## License

No open-source license is currently provided.

This repository is public as a portfolio project, but the absence of a license does not grant permission to reuse, modify, or redistribute the source code beyond the rights provided by applicable law.
