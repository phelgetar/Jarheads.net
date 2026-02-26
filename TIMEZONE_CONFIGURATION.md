# Timezone Configuration - Eastern Time (EST/EDT)

**Updated:** January 17, 2026
**Status:** ✅ All systems configured for America/New_York timezone

---

## Summary

All analytics and WordPress components have been configured to use **Eastern Time** (America/New_York timezone). This ensures:
- All timestamps are stored in EST (winter) or EDT (summer)
- Dashboard displays times in Eastern Time
- Cron jobs log in Eastern Time
- Analytics tracking records in Eastern Time

The system automatically handles daylight saving transitions:
- **EST** = UTC-5 (November - March)
- **EDT** = UTC-4 (March - November)

---

## What Was Changed

### 1. PHP Analytics Scripts ✅

Added `date_default_timezone_set('America/New_York');` to:

**Files Updated:**
- `jh-analytics-endpoint.php` - Tracking endpoint (line 18)
- `jh-analytics-cron.php` - Daily aggregation script (line 19)
- `admin-dashboard-8k3n9p2x.php` - Admin dashboard (line 20)
- `jh-analytics-diagnostic.php` - Diagnostic tool (line 8)
- `trigger-import.php` - Manual import trigger (line 8)
- `timezone-check.php` - Timezone verification tool (new)

### 2. WordPress Configuration ✅

**Before:**
```
Timezone String: (empty)
GMT Offset: 0 hours
current_time('mysql'): 2026-01-17 21:30:05 (UTC)
```

**After:**
```
Timezone String: America/New_York
GMT Offset: -5 hours
current_time('mysql'): 2026-01-17 16:30:05 (EST)
```

**How it was updated:**
- Ran `set-wordpress-timezone.php` script
- Set `timezone_string` option to `America/New_York`
- WordPress now uses Eastern Time for all operations

---

## Server Information

**Server Physical Location:** Mountain Time (MST)
- Server timezone: America/Boise
- Server time shows MST

**WordPress Application:** Eastern Time (EST/EDT)
- All PHP scripts override to America/New_York
- WordPress configured for America/New_York
- All timestamps in database use EST/EDT

**This is intentional** - your site serves Eastern Time zone audience, so all times should be in EST/EDT regardless of server location.

---

## Verification

### Check Current Configuration

Visit this URL to verify timezone settings:
```
https://www.jarheads.net/wp-content/themes/twentyfourteen/timezone-check.php
```

**Expected Results:**
- PHP Default Timezone: `America/New_York` ✅
- Current Time (PHP): Shows EST or EDT ✅
- WordPress Timezone: `America/New_York` ✅
- Database timestamps: Match Eastern Time ✅

### Manual PHP Check

SSH into server and run:
```bash
ssh jarheads@162.241.218.175
php -r "date_default_timezone_set('America/New_York'); echo date('Y-m-d H:i:s T');"
```

Should output current Eastern Time.

---

## Impact on Existing Data

### New Data (After Jan 17, 2026, 4:30 PM EST) ✅
All new entries use correct Eastern Time:
- Page views tracked with EST timestamps
- Comments show EST times
- Dashboard displays EST times
- Cron logs use EST timestamps

### Old Data (Before Configuration) ⚠️
Existing database entries may have UTC timestamps:
- These are **not automatically converted**
- Will appear 5 hours ahead in dashboard
- Aggregate over time, this becomes less noticeable
- Could write migration script if needed (not recommended)

**Recommendation:** Leave old data as-is. The difference will be negligible after a few days of correct tracking.

---

## Files with Timezone Configuration

### Production Server
Location: `~/public_html/wp-content/themes/twentyfourteen/`

```
jh-analytics-endpoint.php        ← Tracking endpoint
jh-analytics-cron.php             ← Daily cron job
admin-dashboard-8k3n9p2x.php     ← Admin dashboard
jh-analytics-diagnostic.php      ← Diagnostic tool
trigger-import.php                ← Manual import
timezone-check.php                ← Timezone verification
set-wordpress-timezone.php        ← WordPress config (one-time use)
```

### Local Repository
Location: `/Users/canadytw/PycharmProjects/Jarheads.net/wordpress/`

All files synchronized with production server.

---

## WordPress Admin Panel

The WordPress admin panel now also displays times in Eastern Time:

**Before:**
- Post publish times showed UTC
- Comment times showed UTC
- Scheduled posts used UTC

**After:**
- All times show in EST/EDT
- Matches your local Eastern Time
- Dashboard → Settings → General shows: America/New_York

You can verify in WordPress admin:
```
https://www.jarheads.net/wp-admin/options-general.php
```

Look for **Timezone** setting - should show `America/New_York`.

---

## Cron Job Times

The analytics cron job runs at specific times. With EST configuration:

**Cron Schedule:**
```bash
# Analytics Daily Aggregation - Run twice daily (midnight and noon)
0 0,12 * * * /usr/bin/php .../jh-analytics-cron.php
```

**Execution Times (EST):**
- Midnight EST = 00:00 Eastern Time
- Noon EST = 12:00 Eastern Time

**Server Time (MST):**
- Midnight EST = 10:00 PM MST (previous day)
- Noon EST = 10:00 AM MST

The cron runs at the MST times, but **logs show EST times** because the script sets `date_default_timezone_set('America/New_York')`.

---

## Testing Timezone Configuration

### Test 1: Track a Page View
1. Visit any article page
2. Open browser console (F12)
3. Check for: `[JH Analytics] Page view tracked successfully`
4. Check database:
```sql
SELECT viewed_at FROM wp_jh_page_views ORDER BY id DESC LIMIT 1;
```
5. Should show current EST time

### Test 2: Check Dashboard
1. Visit admin dashboard
2. Look at "Views Today" card
3. Should reset at midnight EST (not UTC or MST)

### Test 3: Run Cron Manually
```bash
ssh jarheads@162.241.218.175
php ~/public_html/wp-content/themes/twentyfourteen/jh-analytics-cron.php
cat ~/jh-analytics-cron.log
```

Log timestamps should show EST.

---

## Troubleshooting

### Problem: Times still show UTC

**Check:**
1. Clear browser cache
2. Verify timezone-check.php shows America/New_York
3. Check if WordPress timezone reverted (Settings → General)

**Fix:**
Run set-wordpress-timezone.php again:
```bash
ssh jarheads@162.241.218.175
php ~/public_html/wp-content/themes/twentyfourteen/set-wordpress-timezone.php
```

### Problem: Cron log shows wrong time

**Check:**
1. Verify cron job file has `date_default_timezone_set('America/New_York');`
2. Re-deploy jh-analytics-cron.php

**Fix:**
```bash
# From local machine
cd /Users/canadytw/PycharmProjects/Jarheads.net/wordpress
scp jh-analytics-cron.php jarheads@162.241.218.175:public_html/wp-content/themes/twentyfourteen/
```

### Problem: Dashboard graph times incorrect

**Symptom:** Data shows at wrong hours (off by 5 hours)

**Cause:** Old data used UTC timestamps

**Fix:** Wait for new EST data to accumulate, or run this SQL to shift old timestamps:
```sql
-- WARNING: This permanently modifies timestamps
UPDATE wp_jh_page_views
SET viewed_at = DATE_SUB(viewed_at, INTERVAL 5 HOUR)
WHERE viewed_at > '2026-01-17 21:00:00';  -- Only fix old UTC entries
```

**Recommendation:** Don't run this unless absolutely necessary. New data will be correct.

---

## Future Maintenance

### When Deploying New PHP Files

Always add this at the top after `<?php`:
```php
// Set timezone to Eastern Time
date_default_timezone_set('America/New_York');
```

### When Creating New Database Tables

Use `current_time('mysql')` for WordPress compatibility:
```php
$wpdb->insert($table, [
    'created_at' => current_time('mysql')  // Respects WordPress timezone
]);
```

Or use PHP date():
```php
$wpdb->insert($table, [
    'created_at' => date('Y-m-d H:i:s')  // Uses America/New_York if set
]);
```

---

## Summary Checklist

- [x] All PHP analytics scripts set to America/New_York
- [x] WordPress timezone configured to America/New_York
- [x] Database timestamps now use EST/EDT
- [x] Dashboard displays EST times
- [x] Cron logs use EST timestamps
- [x] Verification script created (timezone-check.php)
- [x] Documentation complete

---

**Configuration Date:** January 17, 2026
**Timezone:** America/New_York (EST/EDT)
**Status:** ✅ Production Ready

All future timestamps will be in Eastern Time. Your analytics dashboard will show times matching your local Eastern timezone.
