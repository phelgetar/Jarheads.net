# WordPress Integration for Marine Corps News Aggregator

This folder contains everything you need to display your aggregated Marine Corps news on a WordPress site with individual comment sections for each article.

## 📦 What's Included

| File | Description |
|------|-------------|
| `template-marine-corps-news.php` | Custom page template for displaying news in a grid with category filters |
| `single-marine_news.php` | Template for individual article pages with comments |
| `import-marine-news.php` | Script to import articles from JSON into WordPress as posts |
| `INSTALLATION.md` | Complete step-by-step installation guide |

## 🚀 Quick Start

1. **Upload template files** to your WordPress theme folder:
   - `template-marine-corps-news.php`
   - `single-marine_news.php`

2. **Upload importer** to WordPress root directory:
   - `import-marine-news.php`

3. **Create a new WordPress page** and assign the "Marine Corps News" template

4. **Run the importer** at `yoursite.com/import-marine-news.php` (then delete it)

5. **View your news page** and enjoy individual comment sections per article!

## 📖 Full Documentation

See **[INSTALLATION.md](INSTALLATION.md)** for detailed instructions, troubleshooting, and customization options.

## ✨ Features

- ✅ Custom news listing page independent of theme styling
- ✅ Separate comment sections for each article
- ✅ Category filtering (awards, promotions, equipment, operations, etc.)
- ✅ Responsive grid layout
- ✅ Automatic deduplication on import
- ✅ Marine Corps themed colors and styling
- ✅ Link to original article sources
- ✅ Author and metadata display
- ✅ Tag support
- ✅ Pagination for large article collections

## 🔄 Workflow

```
Python Aggregator → JSON File → WordPress Importer → Custom Templates → User Comments
```

1. Run your aggregator: `python src/aggregators/enhanced_aggregator.py`
2. Upload updated `marine_corps_news.json` to WordPress
3. Run importer to add new articles
4. Viewers see news and can comment on individual articles

## 🎨 Customization

All styling is included inline in the templates for easy customization:
- Marine Corps red: `#C41E3A`
- Grid layout, spacing, fonts all easily adjustable
- Can remove `get_header()` and `get_footer()` for complete independence from theme

## 🔒 Security Notes

- Always delete `import-marine-news.php` after running it
- Importer requires admin login
- Enable comment moderation in WordPress settings
- Keep WordPress updated

## 📊 WordPress Admin

After import, manage your news in WordPress:
- **Marine Corps News** menu appears in admin sidebar
- Edit articles, manage categories, moderate comments
- All standard WordPress features available

## 🤝 Support

For installation help, see **INSTALLATION.md**

For aggregator issues, see main project documentation in `../docs/`

---

Created for jarheads.net Marine Corps News Aggregator
