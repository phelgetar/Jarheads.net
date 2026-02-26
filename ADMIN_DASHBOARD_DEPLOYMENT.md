# Jarheads.net Admin Dashboard - Deployment Guide

**Created:** January 17, 2026
**Status:** ✅ Files deployed to production server
**Next Steps:** Database setup, testing, and cron job configuration

---

## ✅ What's Been Completed

### Files Created and Deployed

All files have been uploaded to: `public_html/wp-content/themes/twentyfourteen/`

**New Files (5 total):**
1. **jh-analytics-install.sql** (7.1 KB) - Database schema
2. **jh-analytics-tracker.js** (7.7 KB) - Client-side tracking beacon
3. **jh-analytics-endpoint.php** (13 KB) - Server-side tracking handler
4. **admin-dashboard-8k3n9p2x.php** (32 KB) - Admin dashboard interface
5. **jh-analytics-cron.php** (8.0 KB) - Daily aggregation script

**Modified Template Files (3 total):**
1. **single-marine_news.php** - Added tracking to individual article pages
2. **archive-marine_news.php** - Added tracking to main news archive
3. **template-marine-corps-news.php** - Added tracking to template page

---

## 🔧 Manual Steps Required

### Step 1: Execute SQL Migration (Create Database Tables)

You need to run the SQL script to create the 4 analytics tables in your WordPress database.

**Option A: Using phpMyAdmin (Recommended)**

1. Log into your hosting control panel (cPanel)
2. Open **phpMyAdmin**
3. Select your WordPress database from the left sidebar
4. Click the **SQL** tab at the top
5. Copy the contents from the file below:
   ```
   ~/public_html/wp-content/themes/twentyfourteen/jh-analytics-install.sql
   ```
6. Paste into the SQL query box
7. Click **Go** to execute
8. Verify success: You should see "4 rows affected" or similar

**Option B: Using SSH/MySQL Command Line**

```bash
# SSH into your server
ssh jarheads@162.241.218.175

# Navigate to the theme directory
cd ~/public_html/wp-content/themes/twentyfourteen/

# Execute the SQL file (replace DATABASE_NAME with your actual database name)
mysql -u your_db_user -p your_database_name < jh-analytics-install.sql
```

**Expected Result:** 4 new tables created:
- `wp_jh_page_views`
- `wp_jh_visitor_sessions`
- `wp_jh_daily_stats`
- `wp_jh_referrer_stats`

**Verification Query (run in phpMyAdmin SQL tab):**
```sql
SHOW TABLES LIKE 'wp_jh_%';
```
Should return 4 tables.

---

### Step 2: Register AJAX Handlers in WordPress

The tracking endpoint needs to be registered with WordPress to handle AJAX requests.

**Add to your theme's `functions.php` file:**

1. SSH into your server or use cPanel File Manager
2. Navigate to: `~/public_html/wp-content/themes/twentyfourteen/`
3. Edit `functions.php` (or create if it doesn't exist)
4. Add this code at the end:

```php
<?php
/**
 * Jarheads.net Analytics AJAX Handler Registration
 */

// Load the tracking endpoint
require_once(get_template_directory() . '/jh-analytics-endpoint.php');

// Register AJAX actions for tracking
add_action('wp_ajax_jh_track_page', 'jh_handle_tracking');
add_action('wp_ajax_nopriv_jh_track_page', 'jh_handle_tracking');
```

**Save the file.**

---

### Step 3: Test the Tracking System

Once the database tables are created and AJAX handlers are registered, test that tracking is working.

**Test Procedure:**

1. **Visit an article page:**
   ```
   https://www.jarheads.net/marine-news/
   ```

2. **Open browser Developer Tools** (F12 or Right-click → Inspect)

3. **Check Console tab for tracking confirmation:**
   - Should see: `[JH Analytics] Page view tracked successfully`
   - If you see errors, check the Console tab for details

4. **Check Network tab:**
   - Look for a POST request to `admin-ajax.php`
   - Should show status 200 OK

5. **Verify database insert (using phpMyAdmin):**
   ```sql
   SELECT * FROM wp_jh_page_views ORDER BY id DESC LIMIT 5;
   ```
   - Should show your recent page view with IP, country, device type, etc.

6. **Check visitor session:**
   ```sql
   SELECT * FROM wp_jh_visitor_sessions ORDER BY first_seen DESC LIMIT 5;
   ```
   - Should show your session with page_views_count = 1

**Troubleshooting:**

- **No tracking message in console**: Check that JavaScript file loaded (Network tab)
- **AJAX error 400/403**: AJAX handlers not registered correctly in functions.php
- **AJAX error 500**: Check PHP error logs, likely database connection issue
- **Empty database**: Tables not created or tracking code not added to templates

---

### Step 4: Access the Admin Dashboard

Once tracking is working, you can access your custom admin dashboard.

**Dashboard URL:**
```
https://www.jarheads.net/wp-content/themes/twentyfourteen/admin-dashboard-8k3n9p2x.php
```

**⚠️ IMPORTANT: Keep this URL private!** This is your secret admin URL. Bookmark it but don't share it.

**What You'll See:**

1. **Quick Statistics Cards:**
   - Total Articles, Comments, Visitors (30 days), Views Today

2. **Analytics Graph:**
   - Interactive Chart.js line graph
   - Time range buttons: Day, Week, Month, Year, All Time
   - Shows Total Views and Unique Visitors

3. **Recent Comments:**
   - Last 20 comments with delete buttons
   - Links to view articles

4. **Top 10 Articles:**
   - Most viewed articles in last 30 days

5. **Visitor Activity:**
   - Geographic breakdown (top 10 countries)
   - Device type percentages (mobile, tablet, desktop)

**Initial State:**
- First visit will show "No analytics data yet" messages
- Once you start getting traffic, graphs and stats will populate
- Takes 24-48 hours to accumulate meaningful data

---

### Step 5: Setup Daily Cron Job (Optional but Recommended)

The cron job aggregates data daily and maintains database performance.

**Add to server crontab:**

```bash
# SSH into your server
ssh jarheads@162.241.218.175

# Edit crontab
crontab -e

# Add this line (runs daily at 2 AM):
0 2 * * * /usr/bin/php ~/public_html/wp-content/themes/twentyfourteen/jh-analytics-cron.php >> ~/jh-analytics-cron.log 2>&1
```

**What the cron job does:**
- Aggregates yesterday's page views into daily stats table
- Anonymizes IP addresses older than 30 days (privacy)
- Deletes detailed page views older than 90 days (keep aggregates only)
- Optimizes database tables for performance

**Verify cron is running** (next day after 2 AM):
```bash
cat ~/jh-analytics-cron.log
```
Should show log entries with timestamps and task results.

---

## 📊 Dashboard Features

### Interactive Graph

**Time Ranges:**
- **Day**: Hourly views for last 24 hours
- **Week**: Daily views for last 7 days
- **Month**: Daily views for last 30 days
- **Year**: Weekly aggregates for last 12 months
- **All Time**: Monthly aggregates for entire history

**Data Displayed:**
- **Total Views** (red line): All page views including repeat visits
- **Unique Visitors** (blue line): Count of unique session IDs

### Comment Management

- **View Recent Comments**: Last 20 comments across all articles
- **Delete Comments**: Click delete button, confirm, comment removed immediately
- **View Article**: Click to open article in new tab

### Quick Statistics

- **Total Articles**: Published marine_news posts
- **Total Comments**: Approved comments site-wide
- **Visitors (30 Days)**: Unique visitors in last 30 days
- **Views Today**: Total page views since midnight

### Geographic Tracking

- **Country Level**: IP-based geolocation via IP-API.com
- **Last 24 Hours**: Shows most recent visitor locations
- **Percentage Breakdown**: % of total traffic from each country

### Device Tracking

- **Device Types**: Mobile 📱, Tablet 📲, Desktop 💻
- **Percentage Display**: Visual breakdown with emojis
- **Last 24 Hours**: Real-time device usage stats

---

## 🔒 Security Features

### Obscure URL Security

- **URL**: `admin-dashboard-8k3n9p2x.php` (random alphanumeric suffix)
- **No Public Links**: Not linked anywhere on the public site
- **Bookmark Only**: Only accessible if you know the exact URL

### Optional Additional Security

**If you want to add authentication later**, edit the dashboard file and uncomment lines 27-29:

```php
// Require admin login (uncomment to enable)
if (!current_user_can('manage_options')) {
    wp_die('Unauthorized access. You must be logged in as an administrator.');
}
```

This will require WordPress admin login before accessing dashboard.

### Privacy Features

- **IP Anonymization**: Last octet set to 0 after 30 days
- **Session IDs**: Random UUIDs, not derived from personal data
- **Data Retention**: Full details deleted after 90 days
- **No Cross-Site Tracking**: Cookies scoped to jarheads.net only
- **Do Not Track**: Respects browser DNT headers

---

## 🧪 Testing Checklist

After completing all setup steps, verify:

- [ ] SQL tables created (4 tables: `wp_jh_%`)
- [ ] AJAX handlers registered in functions.php
- [ ] Visit article page, see tracking console message
- [ ] Check database: `wp_jh_page_views` has new rows
- [ ] Dashboard URL loads without errors
- [ ] Graph displays (may be empty initially)
- [ ] Comments section shows recent comments
- [ ] Can delete a test comment successfully
- [ ] Quick stats cards show correct counts
- [ ] Geographic and device stats display
- [ ] Mobile responsive (test on phone)
- [ ] Cron job scheduled (optional)

---

## 📝 Maintenance

### Daily (Automated via Cron)
- Aggregate previous day's statistics
- Anonymize old IPs
- Clean up old detailed records
- Optimize database tables

### Weekly (Manual)
- Review dashboard for trends
- Check comment moderation needs
- Monitor database size growth

### Monthly (Manual)
- Review top articles for content insights
- Analyze geographic trends for audience understanding
- Check device breakdown for mobile optimization needs

---

## 🐛 Troubleshooting

### Problem: Dashboard shows "No data"
**Solution:**
1. Wait 24-48 hours for traffic to accumulate
2. Verify tracking is working (check browser console)
3. Check database has page view records

### Problem: Tracking not working
**Solution:**
1. Check AJAX handlers registered in functions.php
2. Verify jh-analytics-tracker.js loads (Network tab)
3. Check for JavaScript errors in Console
4. Verify database tables exist

### Problem: Graph not displaying
**Solution:**
1. Check Chart.js loaded from CDN (Network tab)
2. Check browser console for JavaScript errors
3. Try different time range (Day, Week, Month)
4. Clear browser cache (Ctrl+F5)

### Problem: Comment delete not working
**Solution:**
1. Check browser console for errors
2. Verify WordPress user has permission to delete comments
3. Try refreshing page and deleting again

### Problem: Geographic data missing
**Solution:**
1. IP-API.com rate limit may be hit (wait 1 minute)
2. Local/private IP addresses don't get geolocation
3. Check server can make outbound HTTP requests

---

## 🚀 Next Steps After Deployment

1. **Monitor for 24 hours** - Let tracking accumulate data
2. **Bookmark dashboard URL** - Save in password manager for security
3. **Check daily** - Review visitor trends and comment activity
4. **Share insights** - Use data to inform content strategy

---

## 📂 File Locations Reference

### On Production Server:
```
~/public_html/wp-content/themes/twentyfourteen/
├── jh-analytics-install.sql          (SQL schema)
├── jh-analytics-tracker.js           (Client tracking)
├── jh-analytics-endpoint.php         (Server endpoint)
├── admin-dashboard-8k3n9p2x.php      (Dashboard interface)
├── jh-analytics-cron.php             (Daily cron job)
├── single-marine_news.php            (Modified with tracking)
├── archive-marine_news.php           (Modified with tracking)
└── template-marine-corps-news.php    (Modified with tracking)
```

### In Local Repository:
```
/Users/canadytw/PycharmProjects/Jarheads.net/wordpress/
├── jh-analytics-install.sql
├── jh-analytics-tracker.js
├── jh-analytics-endpoint.php
├── admin-dashboard-8k3n9p2x.php
├── jh-analytics-cron.php
├── single-marine_news.php
├── archive-marine_news.php
└── template-marine-corps-news.php
```

---

## 🎯 Success Criteria

✅ **Dashboard is successfully deployed when:**
- SQL tables created and verified
- Tracking beacon collecting page views
- Dashboard accessible at obscure URL
- Graphs display visitor analytics
- Comments can be deleted from dashboard
- Geographic and device stats showing
- Mobile responsive on all devices

---

**Deployment Date:** January 17, 2026
**Dashboard URL:** https://www.jarheads.net/wp-content/themes/twentyfourteen/admin-dashboard-8k3n9p2x.php
**Status:** ✅ Ready for final setup steps (SQL migration and testing)
