# TROUBLESHOOTING: "table news_items has no column named tags"

## Problem

You ran `enhanced_aggregator.py` but got this error:
```
OperationalError: table news_items has no column named tags
```

## What Happened

You have an **existing database** from the old version of the aggregator (without tags/author support), but you're trying to run the **new enhanced version** which expects those columns.

## Solution (Choose One)

### Option 1: Quick Fix (Easiest) ⚡

Run this one command to upgrade your existing database:

```bash
python quick_fix.py
```

This will:
- Add the `tags` column to your existing articles
- Add the `author` column
- Keep all your existing data
- Take about 2 seconds

Then run the enhanced aggregator normally:
```bash
python enhanced_aggregator.py
```

---

### Option 2: Full Migration (Recommended) 🔧

Run the complete migration with backup:

```bash
python migrate_database.py
```

This will:
- Create a backup of your database first
- Add all missing columns
- Create indexes for better performance
- Verify the migration was successful
- Show you database statistics

Then run:
```bash
python enhanced_aggregator.py
```

---

### Option 3: Fresh Start 🆕

If you want to start completely fresh:

```bash
# Backup your old database (optional)
mv marine_corps_news.db marine_corps_news.db.old

# Run the enhanced aggregator - it will create a new database
python enhanced_aggregator.py
```

This will collect articles from the last 90 days with full tag support.

---

## Verification

After running the fix, verify it worked:

```bash
python migrate_database.py check
```

This shows:
- Current database schema
- Whether all required columns exist
- How many articles you have
- How many have tags/authors

---

## What's Different in Your Existing Articles

**Before migration:**
```json
{
  "title": "Article Title",
  "url": "...",
  "source": "...",
  "category": "equipment"
}
```

**After migration:**
```json
{
  "title": "Article Title", 
  "url": "...",
  "source": "...",
  "category": "equipment",
  "tags": [],        // Empty for old articles
  "author": null     // Null for old articles
}
```

**New articles** collected after migration will have tags and authors populated!

---

## FAQ

**Q: Will I lose my existing articles?**  
A: No! The migration adds columns but keeps all existing data.

**Q: Will my old articles get tags?**  
A: Old articles will have empty tags `[]`. Only newly collected articles will have tags.

**Q: Can I re-collect old articles to get their tags?**  
A: Yes! Delete specific articles and re-run the aggregator, or just wait - the enhanced aggregator only goes back 90 days anyway.

**Q: What if the migration fails?**  
A: The full migration creates a backup first. You can restore it if needed.

**Q: Can I use both aggregators?**  
A: After migration, use only `enhanced_aggregator.py`. The old one won't know about tags/authors.

---

## Still Having Issues?

1. **Check database location:**
   ```bash
   ls -la marine_corps_news.db
   ```

2. **Check database schema:**
   ```bash
   sqlite3 marine_corps_news.db "PRAGMA table_info(news_items)"
   ```

3. **Check for database locks:**
   - Close any SQLite browsers
   - Make sure no other scripts are running

4. **Try a fresh database:**
   ```bash
   mv marine_corps_news.db marine_corps_news.db.backup
   python enhanced_aggregator.py
   ```

---

## Command Reference

```bash
# Quick fix (fastest)
python quick_fix.py

# Full migration with backup
python migrate_database.py

# Check database status
python migrate_database.py check

# Run enhanced aggregator
python enhanced_aggregator.py

# Inspect articles
python article_inspector.py
```

---

## Summary

The error happens because you're upgrading from the old system to the new enhanced system. Just run `python quick_fix.py` and you're good to go! 

🎯 **Next Steps:**
1. Run `python quick_fix.py`
2. Run `python enhanced_aggregator.py`
3. Enjoy tag support and incremental updates!
