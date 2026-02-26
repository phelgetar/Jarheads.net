#!/usr/bin/env python3
"""
Article Inspector - View and analyze ingested Marine Corps articles
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import List, Dict
import sys

# Get project root directory (two levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'data'


class ArticleInspector:
    """Inspect and analyze collected articles"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(DATA_DIR / 'marine_corps_news.db')
        self.db_path = db_path
    
    def get_articles(self, days: int = None, category: str = None, 
                     source: str = None, limit: int = None) -> List[Dict]:
        """Get articles with optional filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, title, url, source, published_date, description, 
                   category, tags, author, scraped_at
            FROM news_items
            WHERE 1=1
        '''
        params = []
        
        if days:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            query += ' AND scraped_at > ?'
            params.append(cutoff)
        
        if category:
            query += ' AND category = ?'
            params.append(category)
        
        if source:
            query += ' AND source = ?'
            params.append(source)
        
        query += ' ORDER BY published_date DESC'

        if limit:
            query += ' LIMIT ?'
            params.append(int(limit))  # Ensure limit is an integer for safety

        cursor.execute(query, params)
        
        columns = ['id', 'title', 'url', 'source', 'published_date', 
                   'description', 'category', 'tags', 'author', 'scraped_at']
        
        articles = []
        for row in cursor.fetchall():
            article = dict(zip(columns, row))
            # Parse tags
            if article['tags']:
                try:
                    article['tags'] = json.loads(article['tags'])
                except:
                    article['tags'] = []
            else:
                article['tags'] = []
            articles.append(article)
        
        conn.close()
        return articles
    
    def get_database_stats(self) -> Dict:
        """Get overall database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total articles
        cursor.execute('SELECT COUNT(*) FROM news_items')
        stats['total_articles'] = cursor.fetchone()[0]
        
        # Articles by category
        cursor.execute('SELECT category, COUNT(*) FROM news_items GROUP BY category')
        stats['by_category'] = dict(cursor.fetchall())
        
        # Articles by source
        cursor.execute('SELECT source, COUNT(*) FROM news_items GROUP BY source')
        stats['by_source'] = dict(cursor.fetchall())
        
        # Date range
        cursor.execute('SELECT MIN(published_date), MAX(published_date) FROM news_items')
        min_date, max_date = cursor.fetchone()
        stats['date_range'] = {'earliest': min_date, 'latest': max_date}
        
        # Articles with tags
        cursor.execute('SELECT COUNT(*) FROM news_items WHERE tags IS NOT NULL AND tags != "[]"')
        stats['articles_with_tags'] = cursor.fetchone()[0]
        
        # Articles with authors
        cursor.execute('SELECT COUNT(*) FROM news_items WHERE author IS NOT NULL AND author != ""')
        stats['articles_with_authors'] = cursor.fetchone()[0]
        
        # Recent activity (last 7 days)
        cutoff = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('SELECT COUNT(*) FROM news_items WHERE scraped_at > ?', (cutoff,))
        stats['last_7_days'] = cursor.fetchone()[0]
        
        # Recent activity (last 30 days)
        cutoff = (datetime.now() - timedelta(days=30)).isoformat()
        cursor.execute('SELECT COUNT(*) FROM news_items WHERE scraped_at > ?', (cutoff,))
        stats['last_30_days'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    def analyze_tags(self, days: int = 30) -> Dict:
        """Analyze tag usage"""
        articles = self.get_articles(days=days)
        
        tag_counter = Counter()
        articles_with_tags = 0
        
        for article in articles:
            if article['tags']:
                articles_with_tags += 1
                for tag in article['tags']:
                    tag_counter[tag] += 1
        
        return {
            'total_unique_tags': len(tag_counter),
            'articles_with_tags': articles_with_tags,
            'total_articles': len(articles),
            'top_tags': tag_counter.most_common(20),
            'tag_distribution': dict(tag_counter)
        }
    
    def print_database_overview(self):
        """Print comprehensive database overview"""
        stats = self.get_database_stats()
        
        print("=" * 80)
        print("DATABASE OVERVIEW")
        print("=" * 80)
        print(f"\nTotal Articles: {stats['total_articles']}")
        print(f"Articles with Tags: {stats['articles_with_tags']}")
        print(f"Articles with Authors: {stats['articles_with_authors']}")
        print(f"\nDate Range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
        print(f"\nRecent Activity:")
        print(f"  Last 7 days: {stats['last_7_days']} articles")
        print(f"  Last 30 days: {stats['last_30_days']} articles")
        
        print(f"\n{'='*80}")
        print("ARTICLES BY CATEGORY")
        print("=" * 80)
        for category, count in sorted(stats['by_category'].items(), 
                                      key=lambda x: x[1], reverse=True):
            print(f"  {category:20s}: {count:4d} articles")
        
        print(f"\n{'='*80}")
        print("ARTICLES BY SOURCE")
        print("=" * 80)
        for source, count in sorted(stats['by_source'].items(), 
                                    key=lambda x: x[1], reverse=True):
            print(f"  {source:40s}: {count:4d} articles")
    
    def print_tag_analysis(self, days: int = 30):
        """Print tag usage analysis"""
        analysis = self.analyze_tags(days=days)
        
        print(f"\n{'='*80}")
        print(f"TAG ANALYSIS (Last {days} days)")
        print("=" * 80)
        print(f"Total Articles: {analysis['total_articles']}")
        print(f"Articles with Tags: {analysis['articles_with_tags']} "
              f"({analysis['articles_with_tags']/max(analysis['total_articles'],1)*100:.1f}%)")
        print(f"Unique Tags: {analysis['total_unique_tags']}")
        
        print(f"\nTop 20 Tags:")
        for tag, count in analysis['top_tags']:
            print(f"  {tag:30s}: {count:3d} articles")
    
    def display_article_details(self, article: Dict, show_full_description: bool = False):
        """Display detailed information about an article"""
        print("\n" + "=" * 80)
        print(f"ARTICLE #{article['id']}")
        print("=" * 80)
        print(f"Title: {article['title']}")
        print(f"URL: {article['url']}")
        print(f"\nSource: {article['source']}")
        print(f"Category: {article['category']}")
        print(f"Published: {article['published_date']}")
        print(f"Scraped: {article['scraped_at']}")
        
        if article['author']:
            print(f"Author: {article['author']}")
        
        if article['tags']:
            print(f"\nTags ({len(article['tags'])}):")
            for tag in article['tags']:
                print(f"  • {tag}")
        else:
            print("\nTags: None")
        
        print(f"\nDescription:")
        if show_full_description:
            print(article['description'])
        else:
            print(article['description'][:300] + "..." if len(article['description']) > 300 
                  else article['description'])
    
    def print_recent_articles(self, days: int = 7, limit: int = 10, 
                             category: str = None, show_full: bool = False):
        """Print recent articles with details"""
        articles = self.get_articles(days=days, category=category, limit=limit)
        
        filter_str = f" ({category})" if category else ""
        print(f"\n{'='*80}")
        print(f"RECENT ARTICLES{filter_str} (Last {days} days)")
        print("=" * 80)
        print(f"Showing {len(articles)} articles\n")
        
        for article in articles:
            self.display_article_details(article, show_full_description=show_full)
    
    def print_articles_by_source(self, source: str, limit: int = 10):
        """Print articles from a specific source"""
        articles = self.get_articles(source=source, limit=limit)
        
        print(f"\n{'='*80}")
        print(f"ARTICLES FROM: {source}")
        print("=" * 80)
        print(f"Showing {len(articles)} articles\n")
        
        for article in articles:
            self.display_article_details(article, show_full_description=False)
    
    def export_articles_to_json(self, output_file: str = None,
                                days: int = None, category: str = None):
        if output_file is None:
            output_file = str(DATA_DIR / 'articles_export.json')
        """Export articles to JSON file"""
        articles = self.get_articles(days=days, category=category)
        
        data = {
            'exported_at': datetime.now().isoformat(),
            'total_articles': len(articles),
            'filters': {
                'days': days,
                'category': category
            },
            'articles': articles
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\nExported {len(articles)} articles to {output_file}")
    
    def search_articles(self, keyword: str, limit: int = 20) -> List[Dict]:
        """Search articles by keyword in title or description"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, title, url, source, published_date, description, 
                   category, tags, author, scraped_at
            FROM news_items
            WHERE title LIKE ? OR description LIKE ?
            ORDER BY published_date DESC
            LIMIT ?
        '''
        
        search_term = f"%{keyword}%"
        cursor.execute(query, (search_term, search_term, limit))
        
        columns = ['id', 'title', 'url', 'source', 'published_date', 
                   'description', 'category', 'tags', 'author', 'scraped_at']
        
        articles = []
        for row in cursor.fetchall():
            article = dict(zip(columns, row))
            if article['tags']:
                try:
                    article['tags'] = json.loads(article['tags'])
                except:
                    article['tags'] = []
            else:
                article['tags'] = []
            articles.append(article)
        
        conn.close()
        return articles
    
    def print_search_results(self, keyword: str, limit: int = 20):
        """Search and print results"""
        articles = self.search_articles(keyword, limit)
        
        print(f"\n{'='*80}")
        print(f"SEARCH RESULTS FOR: '{keyword}'")
        print("=" * 80)
        print(f"Found {len(articles)} articles\n")
        
        for article in articles:
            self.display_article_details(article, show_full_description=False)


def interactive_menu():
    """Interactive menu for exploring articles"""
    inspector = ArticleInspector()
    
    while True:
        print("\n" + "=" * 80)
        print("MARINE CORPS ARTICLE INSPECTOR")
        print("=" * 80)
        print("\n1. Database Overview")
        print("2. View Recent Articles (7 days)")
        print("3. View Recent Articles (30 days)")
        print("4. View Articles by Category")
        print("5. View Articles by Source")
        print("6. Tag Analysis")
        print("7. Search Articles")
        print("8. Export Articles to JSON")
        print("9. Exit")
        
        choice = input("\nSelect option (1-9): ").strip()
        
        if choice == '1':
            inspector.print_database_overview()
            inspector.print_tag_analysis(days=30)
        
        elif choice == '2':
            inspector.print_recent_articles(days=7, limit=20)
        
        elif choice == '3':
            inspector.print_recent_articles(days=30, limit=20)
        
        elif choice == '4':
            print("\nCategories: awards, promotions, equipment, podcast, operations, training, general")
            category = input("Enter category: ").strip()
            inspector.print_recent_articles(days=30, category=category, limit=20)
        
        elif choice == '5':
            stats = inspector.get_database_stats()
            print("\nAvailable sources:")
            for source in sorted(stats['by_source'].keys()):
                print(f"  • {source}")
            source = input("\nEnter source name: ").strip()
            inspector.print_articles_by_source(source, limit=10)
        
        elif choice == '6':
            days = input("Analyze tags for how many days? (default 30): ").strip()
            days = int(days) if days else 30
            inspector.print_tag_analysis(days=days)
        
        elif choice == '7':
            keyword = input("Enter search keyword: ").strip()
            limit = input("Max results (default 20): ").strip()
            limit = int(limit) if limit else 20
            inspector.print_search_results(keyword, limit)
        
        elif choice == '8':
            days = input("Export articles from last X days (blank for all): ").strip()
            days = int(days) if days else None
            category = input("Filter by category (blank for all): ").strip() or None
            filename = input(f"Output filename (default {DATA_DIR / 'articles_export.json'}): ").strip()
            filename = filename if filename else str(DATA_DIR / 'articles_export.json')
            inspector.export_articles_to_json(filename, days=days, category=category)
        
        elif choice == '9':
            print("\nExiting...")
            break
        
        else:
            print("\nInvalid option. Please try again.")


def main():
    """Main function with command line arguments"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        inspector = ArticleInspector()
        
        if command == 'overview':
            inspector.print_database_overview()
            inspector.print_tag_analysis(days=30)
        
        elif command == 'recent':
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            inspector.print_recent_articles(days=days, limit=20)
        
        elif command == 'tags':
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            inspector.print_tag_analysis(days=days)
        
        elif command == 'search':
            if len(sys.argv) > 2:
                keyword = sys.argv[2]
                inspector.print_search_results(keyword)
            else:
                print("Usage: python article_inspector.py search <keyword>")
        
        elif command == 'export':
            days = int(sys.argv[2]) if len(sys.argv) > 2 else None
            inspector.export_articles_to_json(days=days)
        
        else:
            print("Unknown command. Available commands:")
            print("  overview - Show database overview")
            print("  recent [days] - Show recent articles")
            print("  tags [days] - Analyze tag usage")
            print("  search <keyword> - Search articles")
            print("  export [days] - Export to JSON")
    else:
        # Interactive mode
        interactive_menu()


if __name__ == "__main__":
    main()
