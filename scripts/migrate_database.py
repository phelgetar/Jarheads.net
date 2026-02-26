#!/usr/bin/env python3
"""
Database Migration Script
Upgrades existing marine_corps_news.db to the new enhanced schema

Migrations:
- v1: Add tags, author, featured_image_url columns
- v2: Add entities, sentiment, domain_authority, engagement_score, read_time_minutes columns
"""

import sqlite3
import os
import shutil
from datetime import datetime
from pathlib import Path

# Determine paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / 'data'
BACKUP_DIR = SCRIPT_DIR / 'backups'
DEFAULT_DB_PATH = DATA_DIR / 'marine_corps_news.db'


def backup_database(db_path: str):
    """Create a backup of the existing database"""
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Created backup: {backup_path}")
        return backup_path
    return None


def migrate_database(db_path: str = None):
    """Migrate database to new schema (v1 - tags, author, featured_image_url)"""
    if db_path is None:
        db_path = str(DEFAULT_DB_PATH)

    print("=" * 80)
    print("MARINE CORPS NEWS DATABASE MIGRATION - V1")
    print("=" * 80)

    if not os.path.exists(db_path):
        print(f"\n[X] Database not found: {db_path}")
        print("No migration needed - enhanced_aggregator.py will create new database")
        return
    
    # Backup first
    print(f"\n[*] Backing up database...")
    BACKUP_DIR.mkdir(exist_ok=True)
    backup_path = backup_database(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current schema
    cursor.execute("PRAGMA table_info(news_items)")
    columns = {row[1] for row in cursor.fetchall()}
    
    print(f"\n🔍 Current columns: {', '.join(sorted(columns))}")
    
    migrations_needed = []
    
    # Check for missing columns
    if 'tags' not in columns:
        migrations_needed.append('tags')
    if 'author' not in columns:
        migrations_needed.append('author')
    if 'featured_image_url' not in columns:
        migrations_needed.append('featured_image_url')

    if not migrations_needed:
        print("\n✅ Database is already up to date! No migration needed.")
        conn.close()
        return

    print(f"\n🔧 Need to add columns: {', '.join(migrations_needed)}")

    try:
        # Add tags column
        if 'tags' in migrations_needed:
            print("   Adding 'tags' column...")
            cursor.execute('ALTER TABLE news_items ADD COLUMN tags TEXT DEFAULT "[]"')
            print("   ✅ Added 'tags' column")

        # Add author column
        if 'author' in migrations_needed:
            print("   Adding 'author' column...")
            cursor.execute('ALTER TABLE news_items ADD COLUMN author TEXT')
            print("   ✅ Added 'author' column")

        # Add featured_image_url column
        if 'featured_image_url' in migrations_needed:
            print("   Adding 'featured_image_url' column...")
            cursor.execute('ALTER TABLE news_items ADD COLUMN featured_image_url TEXT')
            print("   ✅ Added 'featured_image_url' column")
        
        # Create run_history table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS run_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_time TEXT NOT NULL,
                items_collected INTEGER,
                status TEXT,
                notes TEXT
            )
        ''')
        print("   ✅ Created/verified 'run_history' table")
        
        # Create indexes if they don't exist
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_published_date ON news_items(published_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON news_items(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scraped_at ON news_items(scraped_at)')
        print("   ✅ Created/verified indexes")
        
        conn.commit()
        
        # Verify migration
        cursor.execute("PRAGMA table_info(news_items)")
        new_columns = {row[1] for row in cursor.fetchall()}
        
        print(f"\n🔍 Updated columns: {', '.join(sorted(new_columns))}")
        
        # Get row count
        cursor.execute("SELECT COUNT(*) FROM news_items")
        count = cursor.fetchone()[0]
        
        print(f"\n✅ Migration successful!")
        print(f"   Database has {count} existing articles")
        print(f"   All articles now have 'tags', 'author', and 'featured_image_url' columns")
        print(f"\n💡 You can now run: python enhanced_aggregator.py")
        print(f"   New articles will have featured images extracted automatically")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print(f"\n🔄 Restoring from backup...")
        conn.close()
        if backup_path and os.path.exists(backup_path):
            import shutil
            shutil.copy2(backup_path, db_path)
            print(f"   ✅ Restored from {backup_path}")
        raise
    
    finally:
        conn.close()


def migrate_to_v2(db_path: str = None):
    """
    Migrate database to v2 schema with NLP and SEO columns.

    New columns:
    - entities: JSON-serialized extracted entities (people, units, locations)
    - sentiment: Sentiment score (-1.0 to 1.0)
    - domain_authority: Ahrefs domain authority (0-100)
    - engagement_score: Calculated priority score
    - read_time_minutes: Estimated reading time
    """
    if db_path is None:
        db_path = str(DEFAULT_DB_PATH)

    print("=" * 80)
    print("MARINE CORPS NEWS DATABASE MIGRATION - V2 (NLP & SEO)")
    print("=" * 80)

    if not os.path.exists(db_path):
        print(f"\n[X] Database not found: {db_path}")
        print("No migration needed - enhanced_aggregator.py will create new database")
        return

    # Backup first
    print(f"\n[*] Backing up database...")
    BACKUP_DIR.mkdir(exist_ok=True)
    backup_path = backup_database(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check current schema
    cursor.execute("PRAGMA table_info(news_items)")
    columns = {row[1] for row in cursor.fetchall()}

    print(f"\n[*] Current columns: {len(columns)} columns")

    # V2 columns to add
    v2_columns = [
        ('entities', 'TEXT', None),
        ('sentiment', 'REAL', None),
        ('domain_authority', 'REAL', None),
        ('engagement_score', 'REAL', '0.0'),
        ('read_time_minutes', 'INTEGER', None),
    ]

    migrations_needed = [(col, typ, default) for col, typ, default in v2_columns if col not in columns]

    if not migrations_needed:
        print("\n[OK] Database already has v2 schema! No migration needed.")
        conn.close()
        return

    print(f"\n[*] Need to add columns: {', '.join(col for col, _, _ in migrations_needed)}")

    try:
        for col_name, col_type, default in migrations_needed:
            print(f"   Adding '{col_name}' column...")
            if default:
                cursor.execute(f'ALTER TABLE news_items ADD COLUMN {col_name} {col_type} DEFAULT {default}')
            else:
                cursor.execute(f'ALTER TABLE news_items ADD COLUMN {col_name} {col_type}')
            print(f"   [OK] Added '{col_name}' column")

        # Create new index for domain_authority
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_domain_authority ON news_items(domain_authority)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_engagement_score ON news_items(engagement_score)')
        print("   [OK] Created new indexes")

        conn.commit()

        # Verify migration
        cursor.execute("PRAGMA table_info(news_items)")
        new_columns = {row[1] for row in cursor.fetchall()}

        # Get row count
        cursor.execute("SELECT COUNT(*) FROM news_items")
        count = cursor.fetchone()[0]

        print(f"\n[OK] Migration to v2 successful!")
        print(f"   Database has {count} existing articles")
        print(f"   Total columns: {len(new_columns)}")
        print(f"\n[*] New columns are ready for NLP entity extraction and SEO data")
        print(f"   Run the enhanced_aggregator.py to populate the new fields")

    except Exception as e:
        print(f"\n[X] Migration failed: {e}")
        print(f"\n[*] Restoring from backup...")
        conn.close()
        if backup_path and os.path.exists(backup_path):
            shutil.copy2(backup_path, db_path)
            print(f"   [OK] Restored from {backup_path}")
        raise

    finally:
        conn.close()


def check_database_status(db_path: str = None):
    """Check the current database status"""
    if db_path is None:
        db_path = str(DEFAULT_DB_PATH)

    if not os.path.exists(db_path):
        print(f"[X] Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "=" * 80)
    print("DATABASE STATUS")
    print("=" * 80)
    
    # Check schema
    cursor.execute("PRAGMA table_info(news_items)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"\nColumns: {', '.join(columns)}")
    
    # Check for required columns
    required = ['tags', 'author', 'featured_image_url']
    has_all = all(col in columns for col in required)

    if has_all:
        print("✅ Schema is compatible with enhanced_aggregator.py")
    else:
        missing = [col for col in required if col not in columns]
        print(f"⚠️  Missing columns: {', '.join(missing)}")
        print("   Run migration to upgrade database")

    # Count articles
    cursor.execute("SELECT COUNT(*) FROM news_items")
    total = cursor.fetchone()[0]
    print(f"\nTotal articles: {total}")

    # Check if tags are populated
    if 'tags' in columns:
        cursor.execute('SELECT COUNT(*) FROM news_items WHERE tags IS NOT NULL AND tags != "[]"')
        with_tags = cursor.fetchone()[0]
        print(f"Articles with tags: {with_tags} ({with_tags/max(total,1)*100:.1f}%)")

    # Check if authors are populated
    if 'author' in columns:
        cursor.execute('SELECT COUNT(*) FROM news_items WHERE author IS NOT NULL AND author != ""')
        with_authors = cursor.fetchone()[0]
        print(f"Articles with authors: {with_authors} ({with_authors/max(total,1)*100:.1f}%)")

    # Check if featured images are populated
    if 'featured_image_url' in columns:
        cursor.execute('SELECT COUNT(*) FROM news_items WHERE featured_image_url IS NOT NULL AND featured_image_url != ""')
        with_images = cursor.fetchone()[0]
        print(f"Articles with images: {with_images} ({with_images/max(total,1)*100:.1f}%)")
    
    # Check run history
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='run_history'")
    if cursor.fetchone():
        cursor.execute("SELECT COUNT(*) FROM run_history")
        runs = cursor.fetchone()[0]
        print(f"\nCrawl runs recorded: {runs}")
        
        if runs > 0:
            cursor.execute("SELECT run_time, items_collected FROM run_history ORDER BY run_time DESC LIMIT 1")
            last_run, last_count = cursor.fetchone()
            print(f"Last run: {last_run}")
            print(f"Last run collected: {last_count} items")
    
    conn.close()


if __name__ == "__main__":
    import sys

    db_path = str(DEFAULT_DB_PATH)

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == 'check':
            check_database_status(db_path)
        elif command == 'v2':
            # Run v2 migration only
            migrate_to_v2(db_path)
            print("\n" + "=" * 80)
            check_database_status(db_path)
        elif command == 'full':
            # Run all migrations
            migrate_database(db_path)
            migrate_to_v2(db_path)
            print("\n" + "=" * 80)
            check_database_status(db_path)
        elif command == 'help':
            print("Usage: python migrate_database.py [command]")
            print()
            print("Commands:")
            print("  check  - Check current database status")
            print("  v2     - Run v2 migration (NLP & SEO columns)")
            print("  full   - Run all migrations (v1 + v2)")
            print("  help   - Show this help message")
            print()
            print("Default (no command): Run v1 migration only")
        else:
            print(f"Unknown command: {command}")
            print("Use 'help' for available commands")
    else:
        # Default: run both migrations
        migrate_database(db_path)
        migrate_to_v2(db_path)
        print("\n" + "=" * 80)
        check_database_status(db_path)
