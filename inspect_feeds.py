import feedparser


RSS_FEEDS = {
    "Python Jobs": "https://www.python.org/jobs/feed/rss/",
    "Foss Jobs": "https://www.fossjobs.net/rss/programmers/",
    "Remote First Jobs Entry": "https://remotefirstjobs.com/rss/jobs/entry-level.rss",
    "Remote First Jobs Software": "https://remotefirstjobs.com/rss/jobs/software-development.rss",
    "Remote First Jobs Python": "https://remotefirstjobs.com/rss/jobs/python.rss",
    "We Work Remotely": "https://weworkremotely.com/remote-jobs.rss",
    "Jobicy": "https://jobicy.com/jobs/feed",
    "higher edjobs": "https://www.higheredjobs.com/rss/categoryFeed.cfm?catID=161",
}


for feed_name, feed_url in RSS_FEEDS.items():

    print("\n")
    print("=" * 80)
    print(feed_name)
    print("=" * 80)

    feed = feedparser.parse(feed_url)

    print(f"Entries: {len(feed.entries)}")

    if not feed.entries:
        print("NO ENTRIES")
        continue

    entry = feed.entries[0]

    print("\nFields provided by this feed:")

    for key in entry.keys():
        print(f"  - {key}")

    print("\nExample values:")

    for key, value in entry.items():
        print(f"\n{key}:")
        print(value)