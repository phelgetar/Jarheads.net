# Adding New Sources to the Marine Corps News Aggregator

## Quick Start

To add new sources, edit: `/src/aggregators/enhanced_aggregator.py`

There are three types of sources you can add:
1. **RSS_FEEDS** (lines 56-62) - News RSS feeds
2. **PODCAST_FEEDS** (lines 65-74) - Podcast RSS feeds
3. **NEWS_SITES** (lines 77-90) - Websites to scrape (no RSS needed)

## Finding Podcast RSS Feeds

### Method 1: Check the Podcast Website
Most podcasts have an RSS feed link on their website, usually in the footer or "Subscribe" section.

### Method 2: Use Podcast Directories

**Apple Podcasts:**
1. Search for the podcast at https://podcasts.apple.com
2. Click on the podcast
3. Right-click anywhere and "View Page Source"
4. Search for "rss" or "feed" in the source code
5. Copy the RSS feed URL

**Spotify:**
Many Spotify podcasts also have RSS feeds. Use third-party tools like:
- https://spotifeed.timdorr.com/
- Enter the Spotify podcast URL to get the RSS feed

**Common Podcast Hosts (Direct RSS):**
- **Simplecast**: Look for `https://feeds.simplecast.com/[ID]`
- **Libsyn**: Look for `https://[name].libsyn.com/rss`
- **Buzzsprout**: Look for `https://feeds.buzzsprout.com/[ID].rss`
- **Podbean**: Look for `https://feed.podbean.com/[name]/feed.xml`
- **Anchor**: Look for `https://anchor.fm/s/[ID]/podcast/rss`

### Method 3: Use Online Tools
- **GetRSSFeed.com** - Enter podcast name or URL
- **Podcast RSS Finder** - Browser extensions available

## How to Add a Podcast Feed

1. Find the RSS feed URL using methods above
2. Open `/src/aggregators/enhanced_aggregator.py`
3. Locate the `PODCAST_FEEDS` dictionary (around line 65)
4. Add a new line:

```python
PODCAST_FEEDS = {
    'Marine Corps Association Podcast': 'https://mca-marines.org/podcast/feed/',
    'The Warfighter Podcast': 'https://feeds.simplecast.com/vg3bH_Az',
    'Your New Podcast Name': 'RSS_FEED_URL_HERE',  # Add this line
}
```

## Recommended Marine Corps Podcasts

### Podcasts to Find RSS Feeds For:

**Direct Marine Corps Focus:**
1. **Zero Blog Thirty** (Barstool Sports)
   - Platform: Various
   - Topic: Military lifestyle, veteran stories

2. **Devil Dog Radio**
   - Check: https://www.devildogradio.com/

3. **The Scuttlebutt Podcast**
   - Marine Corps history and stories

**Military/Veteran (Includes Marines):**
4. **Jocko Podcast** (Jocko Willink)
   - Hosted by former Navy SEAL, frequently features Marines
   - Platform: Apple Podcasts, Spotify

5. **Team House Podcast**
   - Veterans from all branches

6. **Cleared Hot** (Andy Stumpf)
   - Military and veteran content

7. **Mike Drop** (Mike Ritland)
   - Former Navy SEAL, military topics

8. **Veteran On The Move**
   - Multi-branch veteran stories

**Defense/Military News:**
9. **Defense News Weekly**
10. **The Cipher Brief Podcast** (national security)

## How to Add a News RSS Feed

Same process, but edit the `RSS_FEEDS` dictionary:

```python
RSS_FEEDS = {
    'USMC Official': 'https://www.marines.mil/RSS/News-Feeds/All-News/',
    # ... existing feeds ...
    'Your News Site': 'https://example.com/rss',  # Add here
}
```

### Suggested News Sources to Add:

1. **Task & Purpose** - `https://taskandpurpose.com/feed/`
2. **Military.com Marine Corps** - Check for RSS feed
3. **Navy Times** (covers Marines) - Check for RSS feed
4. **The War Zone** - Military aviation news
5. **Breaking Defense** - Defense industry news

## How to Add a Website to Scrape

If a site doesn't have RSS but has regular news updates:

```python
NEWS_SITES = {
    'DVIDS Marines': 'https://www.dvidshub.net/unit/USMC',
    # ... existing sites ...
    'New Site Name': 'https://example.com/news/',  # Add here
}
```

### Additional Marine Corps Bases:

Already commented in the code, just uncomment to enable:
- Marine Corps Base Hawaii
- Marine Corps Base Quantico
- Marine Corps Air Station Beaufort
- Marine Corps Air Station Iwakuni
- Marine Corps Base Camp Butler (Okinawa)

## Testing Your Changes

After adding new sources:

### 1. Test Locally First
```bash
cd /Users/canadytw/PycharmProjects/Jarheads.net
python3 src/aggregators/enhanced_aggregator.py
```

### 2. Check the Output
Look for your new source in the console output:
```
Crawling RSS feed: Your New Podcast Name
```

### 3. Verify Database
```bash
python3 src/utils/article_inspector.py
```

### 4. Deploy to Server
```bash
rsync -avz --exclude='.venv' --exclude='__pycache__' --exclude='.git' --exclude='data/' \
  /Users/canadytw/PycharmProjects/Jarheads.net/ \
  jarheads@162.241.218.175:~/Jarheads.net/
```

### 5. Test on Server
```bash
ssh jarheads@162.241.218.175 "~/Jarheads.net/run_aggregator.sh"
```

## Filtering and Categorization

The aggregator automatically:
- **Filters** content for Marine Corps keywords (see `KEYWORDS` list at line 92)
- **Categorizes** into: awards, promotions, equipment, podcast, operations, training, general
- **Deduplicates** using content hashing
- **Date filters** to only collect recent articles

If your podcast/feed isn't Marine Corps exclusive, the aggregator will automatically filter to only Marine Corps-related episodes.

## Troubleshooting

### Feed Not Working?
1. Verify the RSS URL works in a browser
2. Check for authentication requirements (some feeds are private)
3. Look for rate limiting (add delays in code if needed)
4. Check error logs: `~/Jarheads.net/data/cron.log` on server

### No Articles Collected?
1. Check if articles contain Marine Corps keywords
2. Verify date range (only collects last 90 days)
3. Ensure RSS feed format is standard

### Duplicate Articles?
This is normal - the aggregator uses content hashing to prevent duplicates from being saved.

## Getting Help

If you need help finding RSS feeds or adding sources, you can:
1. Check podcast hosting platform documentation
2. Use browser "View Source" to find feed URLs
3. Contact the podcast/website directly
4. Use RSS feed discovery tools online

## Keywords List

The aggregator searches for these keywords (customizable at line 92):
- marine corps, usmc, marines, jarhead, leatherneck
- semper fi, semper fidelis, devil dog
- Military equipment: humvee, hmmwv, mrap, amphibious
- Units: meu, marine expeditionary
- Awards: navy cross, purple heart, meritorious service medal
- Ranks: promotion, general, sergeant major, commandant
- Equipment: f-35b, mv-22, osprey, ch-53, aav, lcac
- Specialties: infantry, artillery, aviation, logistics

Add more keywords if needed to capture content from your new sources.
