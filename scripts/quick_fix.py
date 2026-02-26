#!/usr/bin/env python3
"""
Quick Fix - Add missing columns to existing database
Run this if you get "table news_items has no column named tags" error
"""

import sqlite3
import os

db_path = 'marine_corps_news.db'

if not os.path.exists(db_path):
    print("No existing database found - you're good to go!")
    print("Just run: python enhanced_aggregator.py")
else:
    print("Fixing database schema...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add tags column
        cursor.execute('ALTER TABLE news_items ADD COLUMN tags TEXT DEFAULT "[]"')
        print("✅ Added 'tags' column")
    except:
        print("   'tags' column already exists")
    
    try:
        # Add author column
        cursor.execute('ALTER TABLE news_items ADD COLUMN author TEXT')
        print("✅ Added 'author' column")
    except:
        print("   'author' column already exists")
    
    try:
        # Create run_history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS run_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_time TEXT NOT NULL,
                items_collected INTEGER,
                status TEXT,
                notes TEXT
            )
        ''')
        print("✅ Created 'run_history' table")
    except:
        print("   'run_history' table already exists")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database fixed! Now run: python enhanced_aggregator.py")
