# Enhanced Marine Corps News Aggregator - Updated Guide

## What's New in Version 2.0

### 🏷️ **Tag Extraction**
- Automatically extracts tags from RSS feeds
- Scrapes tags from article pages (especially marines.mil)
- Uses tags for better categorization
- Stores all tags with each article

### 📅 **Smart Date Filtering**
- Default: Only collects articles from last 90 days
- **Incremental Updates**: After first run, only collects articles since last successful run
- Prevents duplicate work and keeps database current
- Configurable time window

### 👤 **Author Information**
- Extracts author names when available
- Supports both RSS feed authors and webpage bylines
- Helps track who's writing about Marine Corps topics

### 🔄 **Run History Tracking**
- Tracks every aggregation run
- Records success/failure status
- Enables incremental updates
- Shows when last successful run occurred

---

## Quick Start

### First Run (Collects Last 90 Days)

```bash
python enhanced_aggregator.py
```

This will:
1. Collect all Marine Corps articles from the last 90 days
2. Extract tags, authors, and metadata
3. Save everything to the database
4. Show you a sample of articles with full details

### Subsequent Runs (Incremental Updates)

Just run the same command:
```bash
python enhanced_aggregator.py
```

Now it will:
1. Check when the last successful run was
2. Only collect NEW articles since then
3. Still respects 90-day maximum age
4. Much faster than re-scanning everything

---

## Inspecting Your Articles

### Interactive Inspector

```bash
python article_inspector.py
```

This launches an interactive menu where you can:
- View database overview
- Browse recent articles
- Filter by category or source
- Analyze tag usage
- Search for keywords
- Export to JSON

### Command Line Inspection

```bash
# Database overview
python article_inspector.py overview

# Recent articles (last 7 days)
python article_inspector.py recent 7

# Tag analysis (last 30 days)
python article_inspector.py tags 30

# Search for keyword
python article_inspector.py search "JLTV"

# Export to JSON
python article_inspector.py export 30
```

---

## Article Structure

Each article now includes:

```json
{
  "title": "Marine Corps Announces New Equipment",
  "url": "https://www.marines.mil/News/...",
  "source": "USMC Official",
  "published_date": "2026-01-04T10:00:00",
  "description": "The Marine Corps has announced...",
  "category": "equipment",
  "tags": [
    "Equipment",
    "Modernization",
    "JLTV",
    "Force Design"
  ],
  "author": "Cpl. John Smith",
  "scraped_at": "2026-01-04T14:30:00"
}
```

---

## Tag Examples from Real Sources

### Marines.mil Articles
Marines.mil articles typically include official tags like:
- Equipment
- Force Design 2030
- Training
- Commandant
- Pacific
- Europe
- MEU (Marine Expeditionary Unit)
- Recruitment
- Leadership

### How Tags Are Used

1. **Better Categorization**: Tags help the system categorize articles more accurately
2. **Trending Topics**: See what topics are most common
3. **Content Discovery**: Filter articles by specific tags
4. **Website Integration**: Use tags for organizing content on jarheads.net

---

## Configuration

### Change Maximum Article Age

Edit `enhanced_aggregator.py` or pass parameter:

```python
# Collect last 30 days only
aggregator = EnhancedMarineCorpsAggregator(max_age_days=30)

# Collect last 180 days (6 months)
aggregator = EnhancedMarineCorpsAggregator(max_age_days=180)
```

### Customize for jarheads.net

```python
# In your code
from enhanced_aggregator import EnhancedMarineCorpsAggregator

# Run aggregator
aggregator = EnhancedMarineCorpsAggregator(max_age_days=90)
stats = aggregator.run_full_crawl()

# Get articles with tags
articles = aggregator.get_recent_items(days=7, limit=50)

# Each article has tags you can display
for article in articles:
    print(f"Title: {article['title']}")
    print(f"Tags: {', '.join(article['tags'])}")
```

---

## Database Schema

### news_items table
```sql
CREATE TABLE news_items (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    source TEXT NOT NULL,
    published_date TEXT,
    description TEXT,
    category TEXT,
    tags TEXT,              -- JSON array of tags
    author TEXT,            -- Author name if available
    content_hash TEXT UNIQUE,
    scraped_at TEXT NOT NULL,
    posted_to_site BOOLEAN DEFAULT 0
);
```

### run_history table
```sql
CREATE TABLE run_history (
    id INTEGER PRIMARY KEY,
    run_time TEXT NOT NULL,
    items_collected INTEGER,
    status TEXT,
    notes TEXT
);
```

---

## Examples

### Example 1: Daily Automated Run

```bash
#!/bin/bash
# daily_update.sh

cd /path/to/aggregator

# Run aggregator (incremental update)
python enhanced_aggregator.py

# Generate summary of new articles
python news_summarizer.py

# Copy to website
cp marine_corps_news.json /var/www/jarheads.net/data/
cp news_summary_7days.txt /var/www/jarheads.net/reports/

echo "Update complete at $(date)"
```

Add to crontab:
```bash
0 6 * * * /path/to/daily_update.sh
```

### Example 2: View Articles with Most Tags

```python
from article_inspector import ArticleInspector

inspector = ArticleInspector()
articles = inspector.get_articles(days=30)

# Sort by number of tags
articles_with_tags = [(a, len(a['tags'])) for a in articles if a['tags']]
articles_with_tags.sort(key=lambda x: x[1], reverse=True)

print("Articles with most tags:")
for article, tag_count in articles_with_tags[:10]:
    print(f"{article['title']} ({tag_count} tags)")
    print(f"  Tags: {', '.join(article['tags'])}")
```

### Example 3: Find Articles by Tag

```python
from article_inspector import ArticleInspector

inspector = ArticleInspector()
articles = inspector.get_articles(days=90)

# Find all equipment-related articles
equipment_articles = [
    a for a in articles 
    if any('equipment' in tag.lower() for tag in a['tags'])
]

print(f"Found {len(equipment_articles)} equipment articles")
```

### Example 4: Export Tagged Articles for Website

```python
from enhanced_aggregator import EnhancedMarineCorpsAggregator

aggregator = EnhancedMarineCorpsAggregator()
articles = aggregator.get_recent_items(days=7)

# Group by tags
by_tag = {}
for article in articles:
    for tag in article['tags']:
        if tag not in by_tag:
            by_tag[tag] = []
        by_tag[tag].append(article)

# Now you can create tag-based pages on jarheads.net
for tag, tag_articles in by_tag.items():
    print(f"\n{tag}: {len(tag_articles)} articles")
```

---

## Tag Analysis Features

### View Most Popular Tags

```bash
python article_inspector.py tags 30
```

This shows:
- Total unique tags
- How many articles have tags
- Top 20 most used tags
- Tag distribution

### Example Output:
```
TAG ANALYSIS (Last 30 days)
================================================================================
Total Articles: 156
Articles with Tags: 143 (91.7%)
Unique Tags: 87

Top 20 Tags:
  Training                      : 45 articles
  Equipment                     : 38 articles
  Force Design 2030             : 28 articles
  Pacific                       : 24 articles
  Leadership                    : 22 articles
  MEU                          : 18 articles
  ...
```

---

## Integration with jarheads.net

### Option 1: Display Articles with Tags

```html
<!-- On your website -->
<div class="article">
  <h3>{{ article.title }}</h3>
  <div class="tags">
    {% for tag in article.tags %}
      <span class="tag">{{ tag }}</span>
    {% endfor %}
  </div>
  <p>{{ article.description }}</p>
</div>
```

### Option 2: Tag-Based Navigation

```python
# Generate tag cloud data
from collections import Counter
from article_inspector import ArticleInspector

inspector = ArticleInspector()
articles = inspector.get_articles(days=30)

all_tags = []
for article in articles:
    all_tags.extend(article['tags'])

tag_counts = Counter(all_tags)

# Use for tag cloud on jarheads.net
tag_cloud = [
    {'tag': tag, 'count': count, 'size': min(count * 2, 50)}
    for tag, count in tag_counts.most_common(30)
]
```

### Option 3: Automatic Category Pages

```python
# Create separate pages for major topics
major_tags = ['Equipment', 'Training', 'Force Design 2030', 'Leadership']

for tag in major_tags:
    articles = [
        a for a in all_articles 
        if tag in a['tags']
    ]
    # Generate page for this tag
    create_tag_page(tag, articles)
```

---

## Troubleshooting

### "No articles found"
- Make sure you've run `enhanced_aggregator.py` first
- Check if database file exists: `ls -la marine_corps_news.db`
- RSS feeds may be temporarily down

### "Few articles have tags"
- Normal for some sources (not all provide tags)
- Marines.mil articles should have tags
- Consider adding custom tag extraction rules

### "Incremental update not working"
- Check run_history table: `sqlite3 marine_corps_news.db "SELECT * FROM run_history"`
- Ensure last run was marked as successful
- Delete run_history to force full 90-day scan

### "Date filtering too restrictive"
- Increase max_age_days parameter
- Check article published dates in database
- Some feeds may have incorrect dates

---

## Performance Tips

1. **First run takes longer**: Collecting 90 days of articles
2. **Subsequent runs are fast**: Only new articles since last run
3. **Tag enrichment adds time**: Fetching article pages for tags
4. **Disable tag enrichment** for faster runs:
   ```python
   # In enhanced_aggregator.py, comment out:
   # if 'marines.mil' in link and len(tags) < 3:
   #     metadata = self.enrich_article_metadata(link, tags)
   ```

---

## Comparison: Old vs New

### Old Aggregator
- ❌ No tags
- ❌ No author info
- ❌ No date filtering
- ❌ Re-scans everything every time
- ❌ No incremental updates

### Enhanced Aggregator
- ✅ Extracts tags from feeds and pages
- ✅ Captures author information
- ✅ 90-day maximum age by default
- ✅ Incremental updates after first run
- ✅ Run history tracking
- ✅ Better metadata extraction

---

## Files Included

1. **enhanced_aggregator.py** - Main crawler with tag support
2. **article_inspector.py** - Tool to view and analyze articles
3. **news_summarizer.py** - Generate summaries (works with new schema)
4. **requirements.txt** - Python dependencies

---

## Next Steps

1. ✅ Run first collection: `python enhanced_aggregator.py`
2. ✅ Inspect articles: `python article_inspector.py`
3. ✅ Analyze tags: `python article_inspector.py tags 30`
4. ✅ Set up daily automation
5. ✅ Integrate tags into jarheads.net

**Semper Fi!** 🇺🇸
