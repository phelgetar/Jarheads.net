# Marine Corps News - Full Automation Guide

## 🎯 Overview

Your Marine Corps news system is now **fully automated**! Here's how it works:

```
Python Aggregator → JSON File → Auto-Upload → WordPress → Auto-Import → Live Website
    (Every 6hrs)      (Local)      (Instant)    (Server)    (Hourly)    (jarheads.net)
```

## ✅ What's Currently Running

### 1. **Python Scheduler** (Local - Your Mac)
- **Status**: ✅ Running since Thursday 7PM
- **Location**: `/Users/canadytw/PycharmProjects/Jarheads.net/src/scheduler.py`
- **Schedule**:
  - Every 6 hours
  - Daily at 6:00 AM
  - Daily at 6:00 PM
- **What it does**:
  1. Crawls Marine Corps news sources
  2. Updates `data/marine_corps_news.json`
  3. **Auto-uploads JSON to WordPress server**
  4. Logs activity

### 2. **WordPress Auto-Importer** (Server - jarheads.net)
- **Status**: ✅ Active (plugin installed)
- **Schedule**: Every hour (WordPress cron)
- **What it does**:
  1. Checks for updated JSON file
  2. Imports new articles automatically
  3. Updates existing articles if changed
  4. Enables comments on all articles
  5. Logs import statistics

## 📊 Complete Workflow

### Automatic Daily Flow:

```
6:00 AM:
├── Python aggregator runs
├── Collects latest Marine Corps news
├── Updates marine_corps_news.json
├── Uploads to jarheads.net server
└── Logs: "✓ Upload successful!"

7:00 AM (next hour):
├── WordPress cron runs
├── Detects updated JSON
├── Imports new articles
├── Logs: "Imported X, Updated Y"
└── Articles live on jarheads.net

Every 6 hours:
└── Process repeats
```

## 🔍 Monitoring

### Check Scheduler Status (Local):
```bash
# See if scheduler is running
ps aux | grep scheduler.py

# View scheduler logs (if running in terminal)
tail -f /path/to/scheduler/output.log
```

### Check WordPress Import Logs (Server):
```bash
# SSH into server
ssh jarheads@162.241.218.175

# View WordPress debug log
tail -f ~/public_html/wp-content/debug.log | grep "Marine News Auto-Import"
```

### Check Import Statistics:
Look for entries like:
```
Marine News Auto-Import: Imported 5, Updated 12
```

## 🛠️ Manual Operations

### Manually Upload JSON:
```bash
cd /Users/canadytw/PycharmProjects/Jarheads.net
./upload_to_wordpress.sh
```

### Manually Trigger WordPress Import:
WordPress automatically imports every hour, but you can force it:
1. Go to WordPress Admin
2. Navigate to Tools → Site Health → Info
3. WordPress will run pending cron jobs

### Run Aggregator Manually:
```bash
cd /Users/canadytw/PycharmProjects/Jarheads.net
python src/aggregators/enhanced_aggregator.py
./upload_to_wordpress.sh  # Then upload
```

## 📁 Important Files

| File | Location | Purpose |
|------|----------|---------|
| `scheduler.py` | Local `/src/scheduler.py` | Automated crawling |
| `enhanced_aggregator.py` | Local `/src/aggregators/` | News collection |
| `marine_corps_news.json` | Local `/data/` | Data export |
| `upload_to_wordpress.sh` | Local `/` | Auto-upload script |
| `marine-news-plugin.php` | Server WP plugins | WordPress integration |
| `archive-marine_news.php` | Server WP theme | Archive display |
| `single-marine_news.php` | Server WP theme | Single article + comments |
| `taxonomy-news_category.php` | Server WP theme | Category filtering |

## 🎛️ Configuration

### Change Upload Schedule:
Edit `/Users/canadytw/PycharmProjects/Jarheads.net/src/scheduler.py`:

```python
# Line ~190-194
schedule.every(6).hours.do(poster.check_and_post_new_items)  # Change 6 to desired hours
schedule.every().day.at("06:00").do(poster.check_and_post_new_items)  # Change time
```

### Change WordPress Import Frequency:
Edit `wordpress/marine-news-plugin.php` line 90:

```php
wp_schedule_event(time(), 'hourly', 'marine_news_auto_import');
// Options: 'hourly', 'twicedaily', 'daily'
```

## 🚨 Troubleshooting

### Articles Not Updating:

**1. Check if scheduler is running:**
```bash
ps aux | grep scheduler.py
```
If not running:
```bash
cd /Users/canadytw/PycharmProjects/Jarheads.net
nohup python src/scheduler.py > scheduler.log 2>&1 &
```

**2. Check if JSON uploaded:**
```bash
ssh jarheads@162.241.218.175 "ls -lh ~/public_html/data/marine_corps_news.json"
# Should show recent timestamp
```

**3. Check WordPress plugin active:**
- Go to WordPress Admin → Plugins
- Ensure "Marine Corps News" is activated

**4. Check WordPress import logs:**
```bash
ssh jarheads@162.241.218.175 "tail -50 ~/public_html/wp-content/debug.log"
```

### SSH Upload Fails:

**Check SSH key authentication:**
```bash
ssh jarheads@162.241.218.175 "echo test"
# Should not ask for password
```

If password required, set up SSH keys or edit `upload_to_wordpress.sh` to use password auth.

## 📈 Performance

- **Aggregator runtime**: ~2-5 minutes per crawl
- **Upload time**: < 5 seconds
- **WordPress import**: ~30-60 seconds for 137 articles
- **Total automation delay**: < 1 hour from news source to website

## 🔒 Security Notes

- ✅ Import script deleted from public WordPress directory
- ✅ JSON file in `/data/` directory (not web accessible)
- ✅ WordPress plugin uses secure sanitization
- ✅ SSH key authentication for uploads
- ✅ Comments require user login/approval (configure in WP settings)

## 🎉 Success Indicators

Your automation is working if:
- ✅ Scheduler shows "✓ Upload successful!"
- ✅ WordPress logs show "Marine News Auto-Import: Imported X"
- ✅ New articles appear on jarheads.net within 1 hour
- ✅ Article count increases on category filters
- ✅ Comment sections available on all new articles

## 🔗 Quick Links

- **Live Site**: https://jarheads.net/
- **News Archive**: https://jarheads.net/marine-news/
- **WordPress Admin**: https://jarheads.net/wp-admin
- **Plugin**: WP Admin → Plugins → Marine Corps News

## 📞 Support

For issues:
1. Check this guide's troubleshooting section
2. Review log files mentioned above
3. Verify all components are running/active
4. Check file permissions and paths

---

**Last Updated**: January 11, 2026
**Version**: 1.0 - Full Automation Active
