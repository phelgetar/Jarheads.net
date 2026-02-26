# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Marine Corps News Aggregator for jarheads.net - A comprehensive web crawler and aggregator that collects Marine Corps-related content from official sources, news outlets, and podcasts. The system uses SQLite for storage, provides JSON exports, and supports scheduled crawling with optional WordPress integration.

## Common Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Create/activate virtual environment (if needed)
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
```

### Running the Aggregator
```bash
# One-time manual crawl
python src/aggregators/marine_corps_aggregator.py

# Enhanced crawl with tag extraction and incremental updates
python src/aggregators/enhanced_aggregator.py

# Automated scheduled crawling (every 6 hours)
python src/scheduler.py
```

### Database Operations
```bash
# Check database status
python scripts/migrate_database.py check

# Migrate database to enhanced schema
python scripts/migrate_database.py

# Inspect collected articles
python src/utils/article_inspector.py

# Query database directly
sqlite3 data/marine_corps_news.db "SELECT COUNT(*) FROM news_items"
sqlite3 data/marine_corps_news.db "SELECT category, COUNT(*) FROM news_items GROUP BY category"
```

### Generating Reports
```bash
# Generate summary report (last 7 days)
python src/utils/news_summarizer.py
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f marine-corps-aggregator

# Access dashboard
# Navigate to http://localhost:8080
```

## Project Structure

```
Jarheads.net/
├── src/                          # Main application code
│   ├── aggregators/             # Core news aggregation modules
│   │   ├── marine_corps_aggregator.py
│   │   └── enhanced_aggregator.py
│   ├── utils/                   # Utility tools
│   │   ├── article_inspector.py
│   │   └── news_summarizer.py
│   └── scheduler.py             # Automated crawling scheduler
├── scripts/                      # Maintenance and utility scripts
│   ├── migrate_database.py      # Database migration tool
│   ├── quick_fix.py             # Quick fixes
│   └── backups/                 # Backup files
├── data/                         # Data storage
│   ├── marine_corps_news.db     # SQLite database
│   ├── marine_corps_news.json   # JSON export
│   ├── dashboard.html           # Web dashboard
│   └── summary_report.html      # Generated reports
├── config/                       # Configuration files
│   └── config.ini               # Application configuration
├── docs/                         # Documentation
│   ├── QUICKSTART.md
│   ├── ENHANCED_GUIDE.md
│   ├── SUMMARIZER_GUIDE.md
│   ├── TROUBLESHOOTING.md
│   └── ADVANCED_STRATEGIES.md
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker container definition
├── docker-compose.yml           # Docker Compose configuration
├── README.md                     # Project overview
└── CLAUDE.md                     # This file
```

## Code Architecture

### Core Components

**1. Aggregator System (Two Versions)**
- `src/aggregators/marine_corps_aggregator.py` - Basic aggregator with RSS feeds, web scraping, and Google News integration
- `src/aggregators/enhanced_aggregator.py` - Enhanced version with tag extraction, author attribution, and incremental updates based on last run time

Both aggregators follow the same pattern:
- `NewsItem` dataclass: Represents a single article with metadata
- `MarineCorpsAggregator`/`EnhancedMarineCorpsAggregator` class: Main orchestrator
- Content categorization: Automatic classification into awards, promotions, equipment, operations, training, podcasts, or general news
- Deduplication: Uses content hashing and URL uniqueness

**2. Database Layer**
- SQLite database (`data/marine_corps_news.db`)
- Schema managed through init_database() methods
- Key tables:
  - `news_items`: Stores all crawled articles with metadata
  - `run_history`: Tracks crawl execution history (enhanced version only)
- Indexes on: published_date, category, scraped_at

**3. Scheduler and Integration**
- `src/scheduler.py` - Automated crawling using the `schedule` library
- `JarheadsNetPoster` class: Handles posting to jarheads.net via WordPress API or email
- Default schedule: Every 6 hours + daily at 6 AM/PM

**4. Analysis and Reporting Tools**
- `src/utils/news_summarizer.py` - Generates executive summaries and comprehensive reports
- `src/utils/article_inspector.py` - Interactive tool to view, filter, and analyze articles
- `data/dashboard.html` - Static HTML dashboard for visualizing collected news

### Data Flow

1. **Collection**: Aggregators fetch from RSS feeds → scrape news sites → search Google News
2. **Processing**: Extract metadata → categorize content → generate content hash
3. **Storage**: Check for duplicates → insert into SQLite → update run history
4. **Export**: Generate JSON files → create HTML reports → (optional) post to website
5. **Scheduling**: Automated runs via scheduler.py → email/API integration

### Content Sources

**RSS Feeds** (primary sources):
- Marines.mil (official USMC news and press releases)
- Defense.gov
- Marine Corps Times
- Stars and Stripes
- Podcast feeds (MCA Podcast, Warfighter Podcast)

**Web Scraping** (secondary sources):
- DVIDS
- Individual Marine Corps base websites (Camp Pendleton, Camp Lejeune, Miramar, MCRD San Diego, Parris Island)

**Google News** (tertiary):
- Keyword-based searches for Marine Corps topics

### Categorization Logic

The `categorize_content()` method analyzes article text for keywords:
- **awards**: Medal, award, honor, citation patterns
- **promotions**: Rank changes, promotion announcements
- **equipment**: Vehicle names (JLTV, ACV, MRAP), weapons systems
- **podcast**: Audio content, podcast metadata
- **operations**: Deployment, exercise, training operation keywords
- **training**: Boot camp, OCS, professional development
- **general**: Fallback category

### Configuration

Configuration managed through `config/config.ini`:
- Database and output paths
- Website/API credentials for jarheads.net integration
- Crawling intervals and limits
- Source enable/disable flags
- Filtering and notification settings

## Development Notes

### Adding New Sources

Add RSS feed to appropriate dictionary in aggregator classes:
```python
RSS_FEEDS = {
    'Source Name': 'https://example.com/rss'
}
```

### Adding New Categories

Update `categorize_content()` method with new keyword patterns and add to category handling throughout the codebase.

### Database Schema Changes

Use `scripts/migrate_database.py` as a template for migrations. Always:
1. Create backup before migration (saved to `scripts/backups/`)
2. Use ALTER TABLE for existing databases
3. Update both aggregator versions
4. Test migration on a copy first

### Testing

The codebase doesn't have formal unit tests. To test:
1. Run manual crawl with a small limit
2. Inspect database output: `python src/utils/article_inspector.py`
3. Check JSON export validity
4. Verify dashboard renders correctly

### Key Dependencies

- `feedparser`: RSS/Atom feed parsing
- `requests`: HTTP operations
- `beautifulsoup4` + `lxml`: HTML parsing and scraping
- `schedule`: Task scheduling
- `python-dateutil`: Date parsing from various formats

## Important Patterns

**Politeness in Scraping**: All scraping includes delays (`time.sleep()`) to avoid overwhelming sources. Respect robots.txt and rate limits.

**Error Handling**: Most methods use try/except blocks to prevent single source failures from stopping entire crawl. Errors are logged but don't halt execution.

**Incremental Updates**: Enhanced aggregator tracks last run time and only processes articles published since then, reducing redundant processing.

**Content Hashing**: Uses MD5 hash of title + URL to detect true duplicates even if URLs differ slightly.

## Integration with jarheads.net

Configure in `src/scheduler.py` or `config/config.ini`:
- **WordPress API**: Set API URL and key, uncomment posting code
- **Email**: Configure SMTP settings for email-based content delivery
- **JSON Export**: Default method - generates `data/marine_corps_news.json` for manual or automated import

The system is designed to run independently and export data, rather than being tightly coupled to the website.
