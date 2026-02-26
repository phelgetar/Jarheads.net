# WordPress Custom Template Installation Guide

This guide will help you install the custom Marine Corps News template system with individual comment sections for jarheads.net.

## What You'll Get

- **Custom news listing page** with category filters
- **Individual article pages** with separate comment sections for each article
- **Import tool** to bring your aggregated news into WordPress
- **Independent styling** that works with any WordPress theme

---

## Installation Steps

### Step 1: Upload Template Files to WordPress Theme

1. **Connect to your WordPress site** via FTP/SFTP or cPanel File Manager

2. **Navigate to your theme directory:**
   ```
   wp-content/themes/YOUR-ACTIVE-THEME-NAME/
   ```

   > **Finding your theme name:** In WordPress admin, go to Appearance → Themes. Your active theme is highlighted.

3. **Upload these files** from the `wordpress/` folder to your theme directory:
   - `template-marine-corps-news.php` (main news listing page)
   - `single-marine_news.php` (individual article template)

   Final location should be:
   ```
   wp-content/themes/YOUR-THEME-NAME/template-marine-corps-news.php
   wp-content/themes/YOUR-THEME-NAME/single-marine_news.php
   ```

### Step 2: Upload Importer Script

1. **Upload `import-marine-news.php`** to your **WordPress root directory** (same level as wp-config.php)

   ```
   public_html/
   ├── wp-config.php
   ├── wp-load.php
   ├── import-marine-news.php  ← Upload here
   └── ...
   ```

2. **Upload your JSON data file** to WordPress:

   Option A: Create a `data/` folder in WordPress root and upload `marine_corps_news.json`:
   ```
   public_html/
   ├── data/
   │   └── marine_corps_news.json
   └── import-marine-news.php
   ```

   Option B: The importer will automatically search common locations for the JSON file.

### Step 3: Create WordPress Page

1. **Log into WordPress Admin** (`yoursite.com/wp-admin`)

2. **Go to Pages → Add New**

3. **Create a new page:**
   - Title: "Marine Corps News" (or whatever you prefer)
   - Content: Leave blank or add intro text
   - Don't publish yet

4. **Assign the custom template:**
   - **Block Editor (Gutenberg):**
     - Click the Settings icon (⚙️) in top-right
     - Click the "Page" tab
     - Scroll down to "Template" section
     - Select **"Marine Corps News"** from dropdown

   - **Classic Editor:**
     - Look for "Page Attributes" box on right sidebar
     - Under "Template" dropdown, select **"Marine Corps News"**

5. **Publish the page**

6. **Note the page URL** - you'll use this to view your news

### Step 4: Import Your News Articles

1. **Make sure you're logged into WordPress as an Administrator**

2. **Run the importer** by visiting:
   ```
   https://yoursite.com/import-marine-news.php
   ```

3. **The importer will:**
   - Register the `marine_news` custom post type
   - Create news categories (awards, promotions, equipment, etc.)
   - Import all articles from your JSON file
   - Enable comments on each article
   - Show you import statistics

4. **Review the import results** - it will show:
   - Number of articles imported
   - Number updated (if re-running)
   - Any errors

5. **IMPORTANT:** After successful import, **DELETE** `import-marine-news.php` from your server for security

### Step 5: Verify Everything Works

1. **Visit your news page** (the one you created in Step 3)
   - You should see all imported articles in a grid layout
   - Category filters should appear at the top
   - Articles should be sorted by date

2. **Click on an article** to view the single page
   - Should display full article content
   - Comment section should appear at the bottom
   - "Back to All News" button should work

3. **Test commenting:**
   - Scroll to comments section
   - Leave a test comment
   - Verify it appears correctly

### Step 6: Set Up Permalink Structure (Optional but Recommended)

1. **Go to Settings → Permalinks** in WordPress admin

2. **Choose a permalink structure:**
   - Recommended: "Post name" or "Custom Structure"
   - This makes URLs cleaner: `yoursite.com/marine-news/article-title`

3. **Click "Save Changes"**

---

## Ongoing Usage

### Regular Updates

To add new articles from your aggregator:

1. **Run the aggregator** to update `marine_corps_news.json`:
   ```bash
   python src/aggregators/enhanced_aggregator.py
   ```

2. **Upload updated JSON** to WordPress `data/` folder

3. **Re-run the importer:**
   ```
   https://yoursite.com/import-marine-news.php
   ```

   - It will skip duplicate articles (checks by URL)
   - Only imports new articles
   - Updates existing articles if needed

4. **Delete importer file** after each run

### Automated Importing (Advanced)

You can automate the import process:

**Option A: WP-CLI (if available)**
```bash
wp eval-file import-marine-news.php
```

**Option B: Cron Job**
Create a scheduled task that:
1. Uploads new JSON file
2. Runs WP-CLI import command
3. Cleans up

**Option C: WordPress Plugin**
Convert the importer into a proper WordPress plugin with admin interface.

---

## Customization

### Change Colors

Edit the template files and update these color codes:
- `#C41E3A` - Marine Corps red (primary)
- `#9A1830` - Darker red (hover states)
- `#1A1A1A` - Dark text
- `#f8f9fa` - Light background

### Modify Layout

**News grid layout** - `template-marine-corps-news.php:152`
```css
.news-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    /* Change 350px to adjust card width */
}
```

**Articles per page** - `template-marine-corps-news.php:162`
```php
'posts_per_page' => 12,  // Change to show more/fewer articles
```

### Add/Remove Categories

Categories are automatically created from your JSON data. To manually manage:
1. Go to WordPress Admin
2. Navigate to **Marine Corps News → Categories**
3. Add, edit, or delete categories

### Disable Comments on Specific Articles

In WordPress admin:
1. Go to **Marine Corps News → All Articles**
2. Edit the article
3. In the right sidebar, find "Discussion"
4. Uncheck "Allow comments"

---

## Troubleshooting

### "Template not showing in dropdown"

**Solutions:**
1. Verify template file is in the **active theme directory**
2. Check file name is exactly `template-marine-corps-news.php`
3. Ensure file has proper opening PHP tag and Template Name comment
4. Try switching to a default theme temporarily to test

### "Import page shows 'Unauthorized'"

**Solutions:**
1. Make sure you're logged into WordPress as Administrator
2. Try accessing while logged in
3. Check file permissions (should be 644)

### "No articles showing on page"

**Solutions:**
1. Verify importer ran successfully
2. Check WordPress admin → Marine Corps News → All Articles
3. Ensure articles are published (not drafts)
4. Check that template is assigned to the page

### "Comments not appearing"

**Solutions:**
1. Go to Settings → Discussion
2. Enable "Allow people to submit comments on new posts"
3. Check individual articles have comments enabled
4. Verify no caching plugin is interfering

### "Page looks like theme, not custom design"

**Solutions:**
1. In template files, comment out or remove:
   ```php
   get_header();
   get_footer();
   ```
2. Add complete HTML structure at top and bottom of template

### "404 errors on article links"

**Solutions:**
1. Go to Settings → Permalinks
2. Click "Save Changes" (don't change anything)
3. This flushes rewrite rules
4. Test article links again

---

## File Reference

| File | Location | Purpose |
|------|----------|---------|
| `template-marine-corps-news.php` | Theme folder | Main news listing page template |
| `single-marine_news.php` | Theme folder | Individual article display template |
| `import-marine-news.php` | WordPress root | Importer script (delete after use) |
| `marine_corps_news.json` | `data/` folder | Your aggregated news data |

---

## Support and Next Steps

### Recommended Enhancements

1. **Featured Images:** Modify importer to extract/download article images
2. **Search Functionality:** Add search box to filter articles
3. **Email Notifications:** Set up comment notifications for new discussions
4. **Social Sharing:** Add share buttons to articles
5. **Related Articles:** Show similar articles at bottom of single posts

### Additional WordPress Settings

**Recommended plugins:**
- **Akismet** - Spam comment filtering
- **Yoast SEO** - Better SEO for articles
- **W3 Total Cache** - Speed optimization
- **Wordfence** - Security

**Discussion settings:**
- Settings → Discussion → Check moderation preferences
- Consider requiring approval for first-time commenters

---

## Security Checklist

- [ ] Delete `import-marine-news.php` after each use
- [ ] Keep WordPress and plugins updated
- [ ] Use strong admin passwords
- [ ] Enable comment moderation
- [ ] Install security plugin (Wordfence, Sucuri, etc.)
- [ ] Regular backups of WordPress database

---

## Questions?

Common issues and solutions are in the Troubleshooting section above. For WordPress-specific help, consult the [WordPress Codex](https://codex.wordpress.org/).

For issues with the news aggregator itself, refer to the main project documentation in `docs/` folder.
