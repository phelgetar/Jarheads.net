# Marine Corps News Aggregator for jarheads.net

A comprehensive web crawler and aggregator specifically designed to find and collect Marine Corps-related content from across the internet.

## Features

### Content Types Tracked
- ✅ **Official USMC News** - Press releases, announcements
- ✅ **Awards and Honors** - Medals, commendations, unit citations
- ✅ **Promotions** - Officer and enlisted promotions
- ✅ **Equipment & Hardware** - New vehicles (HMMWV, MRAP, JLTV, ACV), weapons, technology
- ✅ **Podcasts** - Marine Corps related podcasts and interviews
- ✅ **Operations** - Deployments, exercises, training operations
- ✅ **Training** - Boot camp graduations, OCS, professional development

### Data Sources

#### Official Sources (RSS Feeds)
- Marines.mil (official USMC website)
- Defense.gov
- DVIDS (Defense Visual Information Distribution Service)
- Marine Corps Times
- Stars and Stripes

#### Podcast Sources
- Marine Corps Association Podcast
- The Warfighter Podcast
- (Easy to add more)

#### News Aggregation
- Google News search for Marine Corps topics
- Major defense news outlets
- Base-specific news (Camp Pendleton, Camp Lejeune, etc.)

## Installation

### Requirements
- Python 3.8 or higher
- Internet connection
- ~50MB disk space

### Setup

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run initial crawl:**
```bash
python src/aggregators/marine_corps_aggregator.py
```

3. **For scheduled/automated crawling:**
```bash
python src/scheduler.py
```

## Usage

### One-Time Crawl
```python
from src.aggregators.marine_corps_aggregator import MarineCorpsAggregator

aggregator = MarineCorpsAggregator()
stats = aggregator.run_full_crawl()
aggregator.export_to_json('data/output.json')
```

### Automated Scheduled Crawling
The `src/scheduler.py` script runs crawls automatically:
- Every 6 hours
- Daily at 6:00 AM and 6:00 PM

Modify the schedule in `src/scheduler.py` as needed.

### Running locally without Docker

The docker-compose setup (crawler + nginx dashboard) needs a Docker daemon.
On a machine without one, the same two services run natively:

```bash
# Dashboard on http://127.0.0.1:8080/dashboard.html
# (dashboard.html and the JSON files it fetches all live in data/, so serving
# that folder reproduces the compose nginx web root exactly)
python3 -m http.server 8080 --bind 127.0.0.1 --directory data

# Scheduler (crawls every 6 hours, runs until stopped)
./.venv/bin/python src/scheduler.py
```

Both are managed by the machine-wide dev-services script, which is the normal
way to run them:

```bash
~/PycharmProjects/start-services.sh start dashboard    # or: scheduler
~/PycharmProjects/start-services.sh status
```

Logs land in `~/Library/Logs/dev-services/jarheads-*.log`. Note: WordPress
posting stays disabled until `JARHEADS_API_KEY` is set in `.env`; the scheduler
says so at startup and crawls normally otherwise.

### Getting Recent Items
```python
# Get items from last 7 days
items = aggregator.get_recent_items(days=7, limit=100)

# Export to JSON
aggregator.export_to_json('data/marine_corps_news.json')
```

## Integration with jarheads.net

### Option 1: WordPress REST API
If jarheads.net runs on WordPress, configure in `src/scheduler.py`:

```python
poster = JarheadsNetPoster(
    api_url="https://jarheads.net",
    api_key="your-wordpress-api-key"
)
```

### Option 2: Email Updates
Send formatted content via email for manual posting:
```python
poster.post_via_email(content, "Marine Corps News Update")
```

### Option 3: JSON Export
Export data as JSON and integrate with your existing CMS:
```python
aggregator.export_to_json('data/marine_corps_news.json')
```

The JSON file can be:
- Uploaded to your server
- Processed by a PHP/JavaScript script
- Imported into your CMS

### Option 4: Custom Integration
Modify the `post_to_wordpress()` function to work with your specific CMS API.

## Database

The system uses SQLite to track all crawled items and prevent duplicates.

**Database file:** `data/marine_corps_news.db`

**Schema:**
- title
- url (unique)
- source
- published_date
- description
- category
- content_hash (unique)
- scraped_at
- posted_to_site (boolean flag)

## Customization

### Adding New Sources

#### Add RSS Feed:
```python
RSS_FEEDS = {
    'Your Source Name': 'https://example.com/rss',
}
```

#### Add Website to Scrape:
```python
NEWS_SITES = {
    'Site Name': 'https://example.com/news',
}
```

### Adding Keywords
Edit the `KEYWORDS` and `EQUIPMENT_KEYWORDS` lists in the `MarineCorpsAggregator` class:

```python
KEYWORDS = [
    'marine corps', 'usmc', 'your-new-keyword'
]

EQUIPMENT_KEYWORDS = [
    'jltv', 'your-new-equipment'
]
```

### Modifying Categories
Update the `categorize_content()` method to add new categories:

```python
if any(word in text for word in ['your', 'keywords']):
    return 'your_category'
```

## Suggestions for Enhanced Crawling

### 1. Social Media Integration
Add official USMC social media:
- Twitter/X: @USMC
- Instagram: @usmc
- Facebook: Marines
- LinkedIn: United States Marine Corps

**Tools:** tweepy (Twitter), instaloader (Instagram)

### 2. YouTube Channels
Monitor for new videos:
- Marines Official Channel
- Individual Marine Corps bases
- Marine Corps Recruiting

**Tool:** YouTube Data API v3

### 3. Reddit Monitoring
Track subreddits:
- r/USMC
- r/Military
- r/veterans

**Tool:** PRAW (Python Reddit API Wrapper)

### 4. Defense Industry News
- Defense News
- Jane's Defence
- Breaking Defense
- The War Zone

### 5. Think Tanks & Research
- Center for Strategic and International Studies (CSIS)
- RAND Corporation
- Marine Corps University Press

### 6. Congressional Records
- House Armed Services Committee
- Senate Armed Services Committee
- Defense appropriations hearings

### 7. Freedom of Information Act (FOIA) Databases
- FOIA.gov Marine Corps requests
- MuckRock

### 8. Job Postings
- USAJOBS for civilian Marine Corps positions
- Military.com job board

### 9. Contracts and Acquisitions
- SAM.gov (contract awards)
- Defense contract announcements

### 10. Local News Near Bases
- San Diego Union-Tribune (Camp Pendleton)
- Jacksonville Daily News (Camp Lejeune)
- Washington Post (Pentagon)

## Advanced Features to Consider

### 1. Natural Language Processing
Use NLP to better categorize and extract key information:
```bash
pip install spacy transformers
```

### 2. Sentiment Analysis
Track positive/negative news trends

### 3. Image Recognition
Identify equipment in photos using computer vision

### 4. Notification System
- Email alerts for breaking news
- SMS for urgent updates
- Slack/Discord webhooks

### 5. Analytics Dashboard
Build a web dashboard showing:
- News trends over time
- Most active sources
- Category breakdowns
- Equipment mentions frequency

### 6. Duplicate Detection (Enhanced)
Use fuzzy matching for similar stories from different sources:
```bash
pip install fuzzywuzzy python-Levenshtein
```

## Example Cron Jobs

Run automatically on a server:

```cron
# Run every 6 hours
0 */6 * * * cd /path/to/Jarheads.net && /usr/bin/python3 src/aggregators/marine_corps_aggregator.py

# Run daily at 6 AM
0 6 * * * cd /path/to/Jarheads.net && /usr/bin/python3 src/scheduler.py
```

## Monitoring and Logs

Add logging to track performance:

```python
import logging

logging.basicConfig(
    filename='marine_corps_crawler.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

## Ethical Considerations

- **Respect robots.txt** - The code includes delays between requests
- **Rate limiting** - Avoid overwhelming sources
- **Attribution** - Always link back to original sources
- **Terms of Service** - Review ToS for each source
- **Copyright** - Respect copyright on scraped content

## Troubleshooting

### "No items found"
- Check internet connection
- Verify RSS feed URLs are still valid
- Check if keywords need updating

### "Database locked"
- Close other programs accessing the database
- Use connection pooling for concurrent access

### "HTTP errors"
- Some sites may block scrapers
- Add/update User-Agent header
- Consider using proxy rotation for large-scale scraping

## Performance Tips

1. **Parallel Processing:**
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(scrape_function, url_list)
```

2. **Caching:**
Use Redis or memcached for frequently accessed data

3. **Database Optimization:**
Add indexes for common queries:
```sql
CREATE INDEX idx_scraped_at ON news_items(scraped_at);
CREATE INDEX idx_category ON news_items(category);
```

## Contributing

To add more sources or improve the aggregator:

1. Test new sources thoroughly
2. Ensure deduplication works
3. Update documentation
4. Add appropriate categorization

## Support

For issues or questions about integrating with jarheads.net, consider:
- Checking your CMS documentation
- Testing with small batches first
- Reviewing API rate limits
- Implementing error handling

## License

This code is provided as-is for your use with jarheads.net.

## Project Structure

The project follows a standard Python application structure:
- `src/` - Main application code
  - `aggregators/` - Core news aggregation modules
  - `utils/` - Utility tools (inspector, summarizer)
  - `scheduler.py` - Automated crawling scheduler
- `scripts/` - Maintenance scripts and backups
- `data/` - Database, JSON exports, and generated reports
- `config/` - Configuration files
- `docs/` - Additional documentation

## Next Steps

1. **Run initial test:** `python src/aggregators/marine_corps_aggregator.py`
2. **Review results:** Check `data/marine_corps_news.json`
3. **Configure posting:** Update `src/scheduler.py` with your jarheads.net credentials
4. **Add sources:** Customize RSS feeds and websites to match your needs
5. **Deploy:** Set up on a server with cron jobs or use a cloud service

---

**Semper Fi!** 🇺🇸
