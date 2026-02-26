# Marine Corps News Aggregator - Server Deployment

## Deployment Information

**Project Location:** `/home1/jarheads/Jarheads.net/`
**Python Version:** Python 3.9.21
**Deployment Date:** January 15, 2026

## Scheduled Execution

The aggregator runs automatically via cron every 6 hours at:
- 00:00 (Midnight)
- 06:00 (6 AM)
- 12:00 (Noon)
- 18:00 (6 PM)

## File Locations

### Project Files
- **Main script:** `~/Jarheads.net/src/aggregators/enhanced_aggregator.py`
- **Runner script:** `~/Jarheads.net/run_aggregator.sh`
- **Configuration:** `~/Jarheads.net/config/config.ini`

### Data Files
- **Database:** `~/Jarheads.net/data/marine_corps_news.db`
- **JSON Export:** `~/Jarheads.net/data/marine_corps_news.json`
- **Cron Log:** `~/Jarheads.net/data/cron.log`

### Web Files (Public)
- **Public JSON:** `~/public_html/data/marine_corps_news.json`

## Monitoring Commands

### Check cron job status
```bash
crontab -l
```

### View recent log entries
```bash
tail -50 ~/Jarheads.net/data/cron.log
```

### Check database statistics
```bash
cd ~/Jarheads.net
python3 -c "import sqlite3; conn = sqlite3.connect('data/marine_corps_news.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM news_items'); print(f'Total articles: {cursor.fetchone()[0]}'); conn.close()"
```

### View recent articles
```bash
cd ~/Jarheads.net
python3 src/utils/article_inspector.py
```

### Check last update time
```bash
ls -lh ~/public_html/data/marine_corps_news.json
```

## Manual Execution

Run the aggregator manually anytime:
```bash
~/Jarheads.net/run_aggregator.sh
```

Or run just the Python script:
```bash
cd ~/Jarheads.net
python3 src/aggregators/enhanced_aggregator.py
```

## Updating the Code

To update the aggregator code from your local machine:
```bash
# From your local PycharmProjects/Jarheads.net directory
rsync -avz --exclude='.venv' --exclude='__pycache__' --exclude='.git' --exclude='data/' /Users/canadytw/PycharmProjects/Jarheads.net/ jarheads@162.241.218.175:~/Jarheads.net/
```

## Troubleshooting

### Check if cron is sending error emails
Cron output is sent to: canadytw@jarheads.net

### View full cron log
```bash
cat ~/Jarheads.net/data/cron.log
```

### Test Python dependencies
```bash
cd ~/Jarheads.net
python3 -c "import feedparser, requests, bs4, lxml, dateutil, schedule; print('All dependencies OK')"
```

### Check disk space
```bash
df -h ~
```

## Configuration

Edit configuration settings:
```bash
nano ~/Jarheads.net/config/config.ini
```

After editing config, the next scheduled run will use the new settings.

## Stopping Automatic Updates

To temporarily disable automatic updates:
```bash
crontab -e
# Comment out the aggregator line by adding # at the beginning
```

To re-enable, remove the # comment.
