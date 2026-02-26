# News Summarizer Guide

## Quick Start

### Generate Summaries from Collected Stories

After running the news aggregator, generate summaries with:

```bash
python news_summarizer.py
```

This automatically creates:
- **news_summary_7days.txt** - Last week's stories in text format
- **news_summary_30days.txt** - Last month's stories in text format  
- **news_summary_7days.json** - Last week's stories as structured data
- **news_summary_30days.json** - Last month's stories as structured data

---

## What's Included in the Summary

### 1. Executive Summary
- Total stories collected
- Number of unique sources
- Categories covered
- Stories by category breakdown
- Top contributing sources

### 2. Highlights Section
Featuring the most notable stories in:
- 🎖️ Awards and Honors
- ⭐ Promotions
- 🔧 Equipment and Technology
- ⚔️ Operations and Exercises

### 3. Category Summaries
Detailed listings organized by:
- Awards
- Promotions
- Equipment
- Podcasts
- Operations
- Training
- General News

Each category shows:
- Total count
- Story titles
- Sources
- Descriptions
- Direct links

### 4. Chronological Timeline
Day-by-day breakdown showing:
- Date
- Number of stories per day
- Stories grouped by category
- Quick overview of daily activity

### 5. Source Analysis
Complete breakdown by source showing:
- Story count per source
- Categories covered by each source
- Recent stories from each source

---

## Using the HTML Report

### View the Visual Report

1. Open `summary_report.html` in your browser
2. It automatically loads data from:
   - `news_summary_7days.json` (preferred)
   - `marine_corps_news.json` (fallback)

### Features:
- ✅ Beautiful, professional formatting
- ✅ Print-ready layout
- ✅ Organized by category
- ✅ Quick statistics overview
- ✅ Timeline view
- ✅ Source breakdown
- ✅ Direct links to stories

### Print or Save as PDF:
Click the "🖨️ Print Report" button or use Ctrl+P (Cmd+P on Mac)

---

## Customizing the Summary

### Generate Custom Time Periods

```python
from news_summarizer import NewsStorySummarizer

summarizer = NewsStorySummarizer()

# Last 3 days
summarizer.generate_complete_summary(days=3, output_file='summary_3days.txt')

# Last 90 days
summarizer.generate_complete_summary(days=90, output_file='summary_quarterly.txt')

# All time
stories = summarizer.get_all_stories(days=None)
```

### Generate Specific Sections Only

```python
# Just the executive summary
exec_summary = summarizer.generate_executive_summary(days=7)
print(exec_summary)

# Just highlights
highlights = summarizer.generate_highlights(days=7)
print(highlights)

# Just category summaries
categories = summarizer.generate_category_summaries(days=7)
print(categories)

# Just timeline
timeline = summarizer.generate_timeline_summary(days=30)
print(timeline)

# Just source summaries
sources = summarizer.generate_source_summaries(days=7)
print(sources)
```

---

## Use Cases for jarheads.net

### 1. Weekly Digest Posts
Generate a weekly summary every Monday:

```bash
# Run this in a cron job every Monday at 6 AM
0 6 * * 1 cd /path/to/aggregator && python news_summarizer.py
```

Then copy the highlights from `news_summary_7days.txt` to post on jarheads.net

### 2. Monthly Newsletter
Use the 30-day summary for monthly email newsletters:

```python
summarizer = NewsStorySummarizer()
summary = summarizer.generate_highlights(days=30)
# Email this to subscribers
```

### 3. Category-Specific Pages
Create dedicated pages for each category:

```python
stories = summarizer.get_all_stories(days=30)
equipment_stories = [s for s in stories if s['category'] == 'equipment']
```

### 4. Trending Topics
Identify what's being covered most:

```python
from collections import Counter

stories = summarizer.get_all_stories(days=7)

# Most active sources
sources = Counter(s['source'] for s in stories)
print(sources.most_common(5))

# Most active categories  
categories = Counter(s['category'] for s in stories)
print(categories.most_common())
```

---

## Summary Output Formats

### Text Format (.txt)
- Easy to read
- Copy-paste friendly
- Email-ready
- Good for newsletters

### JSON Format (.json)
- Machine-readable
- Structured data
- Easy to integrate with websites
- Good for APIs

### HTML Format (.html)
- Visual presentation
- Print-ready
- Professional appearance
- Good for reports and presentations

---

## Example Integration with jarheads.net

### Option 1: Weekly Digest Post

```bash
# 1. Run the summarizer
python news_summarizer.py

# 2. Open news_summary_7days.txt

# 3. Copy the "Highlights" section

# 4. Create a new post on jarheads.net with:
#    Title: "Marine Corps News Roundup - [Week of Date]"
#    Content: Paste the highlights section
```

### Option 2: Automated API Posting

```python
from news_summarizer import NewsStorySummarizer
import requests

summarizer = NewsStorySummarizer()

# Get highlights
data = summarizer.export_summary_json(days=7, output_file='temp.json')
highlights = data['highlights']

# Format for your CMS
post_content = format_highlights_for_wordpress(highlights)

# Post to WordPress API
response = requests.post(
    'https://jarheads.net/wp-json/wp/v2/posts',
    headers={'Authorization': 'Bearer YOUR_API_KEY'},
    json={
        'title': f'Marine Corps Weekly Roundup',
        'content': post_content,
        'status': 'publish'
    }
)
```

### Option 3: Embed Summary Widget

Add this to any page on jarheads.net:

```html
<iframe src="summary_report.html" width="100%" height="800px"></iframe>
```

Or load the JSON and display:

```javascript
fetch('news_summary_7days.json')
    .then(r => r.json())
    .then(data => {
        // Display highlights on your page
        displayHighlights(data.highlights);
    });
```

---

## Advanced Features

### Filter by Keywords

```python
def filter_by_keyword(stories, keyword):
    """Find stories mentioning specific topics"""
    return [
        s for s in stories 
        if keyword.lower() in s['title'].lower() 
        or keyword.lower() in s['description'].lower()
    ]

stories = summarizer.get_all_stories(days=30)
mrap_stories = filter_by_keyword(stories, 'MRAP')
promotion_stories = filter_by_keyword(stories, 'general')
```

### Generate Statistics

```python
from collections import defaultdict
from datetime import datetime

stories = summarizer.get_all_stories(days=30)

# Stories per day
by_date = defaultdict(int)
for story in stories:
    date = story['scraped_at'][:10]
    by_date[date] += 1

print("Daily story count:")
for date in sorted(by_date.keys()):
    print(f"{date}: {by_date[date]} stories")

# Average per day
avg = sum(by_date.values()) / len(by_date)
print(f"\nAverage: {avg:.1f} stories per day")
```

### Export for Excel

```python
import csv

stories = summarizer.get_all_stories(days=30)

with open('stories_export.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['title', 'source', 'category', 'url', 'scraped_at'])
    writer.writeheader()
    writer.writerows(stories)
```

---

## Automation Scripts

### Daily Summary Email

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_daily_summary():
    summarizer = NewsStorySummarizer()
    
    # Generate summary
    summary = summarizer.generate_highlights(days=1)
    
    # Setup email
    msg = MIMEMultipart()
    msg['Subject'] = f'Daily Marine Corps News - {datetime.now().strftime("%B %d, %Y")}'
    msg['From'] = 'aggregator@jarheads.net'
    msg['To'] = 'admin@jarheads.net'
    
    msg.attach(MIMEText(summary, 'plain'))
    
    # Send
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('your-email@gmail.com', 'your-password')
        smtp.send_message(msg)

# Run daily
send_daily_summary()
```

### Weekly Report Generation

```bash
#!/bin/bash
# weekly_report.sh

cd /path/to/aggregator

# Run aggregator
python marine_corps_aggregator.py

# Generate summary
python news_summarizer.py

# Copy to web directory
cp news_summary_7days.txt /var/www/jarheads.net/reports/
cp summary_report.html /var/www/jarheads.net/reports/

echo "Weekly report generated at $(date)"
```

Add to crontab:
```bash
0 6 * * 1 /path/to/weekly_report.sh
```

---

## Tips and Best Practices

1. **Run summaries regularly** - Weekly is ideal for most use cases

2. **Review before posting** - Always check the highlights for relevance

3. **Customize categories** - Edit the categorization logic to match your needs

4. **Archive old summaries** - Keep monthly archives for reference

5. **Track metrics** - Monitor which sources and categories are most popular

6. **Use filters** - Focus on specific topics when needed

7. **Automate distribution** - Set up automated emails or posts

---

## Troubleshooting

### "No stories found"
- Run `python marine_corps_aggregator.py` first
- Check that `marine_corps_news.db` exists

### HTML report shows "Loading..."
- Ensure JSON files are in the same directory
- Check browser console for errors
- Verify JSON files are valid

### Empty categories
- This is normal if no stories match that category
- Try a longer time period (30+ days)

### Formatting issues
- Check that all stories have required fields
- Validate JSON format
- Ensure UTF-8 encoding

---

## Next Steps

1. ✅ Run the aggregator to collect stories
2. ✅ Generate your first summary
3. ✅ Review the HTML report
4. ✅ Post highlights to jarheads.net
5. ✅ Set up automation for weekly digests

For questions or issues, refer to README.md or ADVANCED_STRATEGIES.md

**Semper Fi!** 🇺🇸
