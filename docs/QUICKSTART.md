# Quick Start Guide - Marine Corps News Aggregator

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Your First Crawl
```bash
python marine_corps_aggregator.py
```

This will:
- ✅ Crawl 10+ official Marine Corps sources
- ✅ Search Google News for Marine Corps topics
- ✅ Aggregate podcast episodes
- ✅ Save everything to a SQLite database
- ✅ Export to `marine_corps_news.json`

### Step 3: View Results
Open `dashboard.html` in your web browser to see a beautiful visualization of all the news.

---

## 📊 What You'll Get

After running the crawler, you'll have:

1. **marine_corps_news.db** - SQLite database with all items
2. **marine_corps_news.json** - JSON export ready for your website
3. **dashboard.html** - Visual dashboard to browse news

---

## 🌐 Integrate with jarheads.net

### Option A: Manual Upload (Easiest)
1. Run the crawler
2. Review `marine_corps_news.json`
3. Manually post interesting items to jarheads.net

### Option B: Automated JSON Feed
1. Upload `marine_corps_news.json` to your server
2. Add a page on jarheads.net that reads this JSON
3. Set up a cron job to run the crawler daily

```bash
# Add to crontab (runs daily at 6 AM)
0 6 * * * cd /path/to/crawler && python marine_corps_aggregator.py
```

### Option C: WordPress Integration
If jarheads.net uses WordPress:

1. Edit `scheduler.py`
2. Add your WordPress API credentials:
```python
poster = JarheadsNetPoster(
    api_url="https://jarheads.net",
    api_key="your-wordpress-api-key"
)
```
3. Run: `python scheduler.py`

Get your WordPress API key:
- Go to Users → Your Profile
- Scroll to "Application Passwords"
- Create new password

---

## 📁 Sample Output Structure

The JSON file looks like this:
```json
{
  "generated_at": "2026-01-04T02:00:00",
  "total_items": 42,
  "items": [
    {
      "title": "Marine Corps Announces New JLTV Variant",
      "url": "https://...",
      "source": "Marines.mil",
      "published_date": "2026-01-03",
      "description": "The Marine Corps has announced...",
      "category": "equipment"
    }
  ]
}
```

---

## 🔄 Automated Monitoring

For continuous monitoring:

```bash
python scheduler.py
```

This will:
- Run every 6 hours automatically
- Save new content to the database
- Generate updated JSON files
- (Optional) Auto-post to your website

---

## 📋 Example PHP Integration for jarheads.net

Create a file `usmc-news.php` on your server:

```php
<?php
// Load the JSON file
$json_data = file_get_contents('marine_corps_news.json');
$news = json_decode($json_data, true);

// Display news items
foreach ($news['items'] as $item) {
    echo '<div class="news-item">';
    echo '<h3>' . htmlspecialchars($item['title']) . '</h3>';
    echo '<p><strong>Source:</strong> ' . htmlspecialchars($item['source']) . '</p>';
    echo '<p>' . htmlspecialchars($item['description']) . '</p>';
    echo '<a href="' . htmlspecialchars($item['url']) . '">Read More</a>';
    echo '</div>';
}
?>
```

---

## 🎯 Content Categories

The system automatically categorizes content:

- 🎖️ **Awards** - Medals, honors, unit citations
- ⭐ **Promotions** - Officer and enlisted promotions
- 🔧 **Equipment** - New vehicles, weapons, hardware
- 🎙️ **Podcast** - Podcast episodes and interviews
- ⚔️ **Operations** - Deployments, exercises, training
- 🎓 **Training** - Boot camp, OCS, professional development
- 📰 **General** - Other Marine Corps news

---

## 💡 Pro Tips

1. **Run during off-peak hours** - Less server load
2. **Check the database** - `sqlite3 marine_corps_news.db` to query directly
3. **Customize keywords** - Edit `KEYWORDS` in the Python file for better filtering
4. **Add more sources** - See ADVANCED_STRATEGIES.md for 10+ additional sources

---

## 🐛 Troubleshooting

### "No module named feedparser"
```bash
pip install feedparser
```

### "Permission denied"
```bash
chmod +x marine_corps_aggregator.py
```

### "Database is locked"
Close any programs that might be accessing the database

### No items found
- Check your internet connection
- Some RSS feeds may be temporarily down
- Try running with `--verbose` flag

---

## 📞 Next Steps

1. ✅ Run your first crawl
2. ✅ Review the results in the dashboard
3. ✅ Customize the sources (add/remove feeds)
4. ✅ Set up automation with cron or scheduler
5. ✅ Integrate with jarheads.net

For advanced features like social media monitoring, see:
- **ADVANCED_STRATEGIES.md** - 12 additional data sources
- **README.md** - Complete documentation

---

## 🎖️ Semper Fidelis!

Questions? Check the README.md for detailed documentation.
