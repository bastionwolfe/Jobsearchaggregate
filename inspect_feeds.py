import feedparser


RSS_FEEDS = {

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
