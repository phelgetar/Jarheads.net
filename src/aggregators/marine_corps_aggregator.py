#!/usr/bin/env python3
"""
Marine Corps News Aggregator
Crawls multiple sources for Marine Corps related content including:
- Official USMC sources
- News outlets
- Podcasts
- Social media
- Defense industry news
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import time
import re
import os
from pathlib import Path
from typing import List, Dict, Optional
import sqlite3
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse
import hashlib

# Get project root directory (two levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'data'

@dataclass
class NewsItem:
    """Represents a single news item about the Marine Corps"""
    title: str
    url: str
    source: str
    published_date: Optional[str]
    description: str
    category: str  # e.g., 'awards', 'promotions', 'equipment', 'podcast', 'operations'
    content_hash: str
    scraped_at: str
    
    def to_dict(self):
        return asdict(self)


class MarineCorpsAggregator:
    """Main aggregator class for Marine Corps news"""
    
    # Official USMC and DoD RSS Feeds
    RSS_FEEDS = {
        'USMC Official': 'https://www.marines.mil/RSS/News-Feeds/All-News/',
        'USMC Press Releases': 'https://www.marines.mil/RSS/News-Feeds/Press-Releases/',
        'Defense.gov': 'https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx?max=10&ContentType=1',
        'Marine Corps Times': 'https://www.marinecorpstimes.com/arc/outboundfeeds/rss/',
        'Stars and Stripes Marines': 'https://www.stripes.com/RSS/marine_corps',
    }
    
    # Podcast RSS Feeds
    PODCAST_FEEDS = {
        'Marine Corps Association Podcast': 'https://mca-marines.org/podcast/feed/',
        'The Warfighter Podcast': 'https://feeds.simplecast.com/vg3bH_Az',
    }
    
    # News sites to scrape (when RSS not available)
    NEWS_SITES = {
        'DVIDS Marines': 'https://www.dvidshub.net/unit/USMC',
        'Marine Corps Base Camp Pendleton': 'https://www.pendleton.marines.mil/News/',
        'Marine Corps Base Camp Lejeune': 'https://www.lejeune.marines.mil/News/',
    }
    
    # Keywords to look for
    KEYWORDS = [
        'marine corps', 'usmc', 'marines', 'jarhead', 'leatherneck',
        'semper fi', 'semper fidelis', 'devil dog', 'humvee', 'hmmwv', 
        'mrap', 'amphibious', 'meu', 'marine expeditionary',
        'navy cross', 'purple heart', 'meritorious service medal',
        'promotion', 'general', 'sergeant major', 'commandant',
        'f-35b', 'mv-22', 'osprey', 'ch-53', 'aav', 'lcac',
        'infantry', 'artillery', 'aviation', 'logistics'
    ]
    
    # Equipment-specific keywords
    EQUIPMENT_KEYWORDS = [
        'jltv', 'acv', 'amphibious combat vehicle', 'light armored vehicle',
        'lav', 'm1a1', 'abrams', 'howitzer', 'm777', 'himars',
        'javelin', 'stinger', 'nlaw', 'nmesis', 'rogue fires'
    ]
    
    def __init__(self, db_path: str = None):
        """Initialize the aggregator with database connection"""
        if db_path is None:
            db_path = str(DATA_DIR / 'marine_corps_news.db')
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database to track scraped items"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL,
                published_date TEXT,
                description TEXT,
                category TEXT,
                content_hash TEXT UNIQUE,
                scraped_at TEXT NOT NULL,
                posted_to_site BOOLEAN DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()
        
    def is_duplicate(self, content_hash: str) -> bool:
        """Check if item already exists in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM news_items WHERE content_hash = ?', (content_hash,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def save_item(self, item: NewsItem) -> bool:
        """Save news item to database"""
        if self.is_duplicate(item.content_hash):
            return False
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO news_items 
                (title, url, source, published_date, description, category, content_hash, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (item.title, item.url, item.source, item.published_date, 
                  item.description, item.category, item.content_hash, item.scraped_at))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def generate_hash(self, title: str, url: str) -> str:
        """Generate unique hash for content"""
        content = f"{title}{url}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def categorize_content(self, title: str, description: str) -> str:
        """Categorize content based on keywords"""
        text = f"{title} {description}".lower()
        
        if any(word in text for word in ['award', 'medal', 'decoration', 'honor']):
            return 'awards'
        elif any(word in text for word in ['promotion', 'promoted', 'general', 'colonel', 'sergeant major']):
            return 'promotions'
        elif any(word in text for word in self.EQUIPMENT_KEYWORDS):
            return 'equipment'
        elif any(word in text for word in ['podcast', 'interview', 'episode']):
            return 'podcast'
        elif any(word in text for word in ['exercise', 'deployment', 'operation', 'training']):
            return 'operations'
        elif any(word in text for word in ['recruit', 'graduation', 'boot camp', 'ocs']):
            return 'training'
        else:
            return 'general'
    
    def crawl_rss_feeds(self, feeds_dict: Dict[str, str]) -> List[NewsItem]:
        """Crawl RSS feeds and extract Marine Corps related items"""
        items = []
        
        for source_name, feed_url in feeds_dict.items():
            try:
                print(f"Crawling RSS feed: {source_name}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries:
                    title = entry.get('title', '')
                    link = entry.get('link', '')
                    description = entry.get('description', '') or entry.get('summary', '')
                    published = entry.get('published', datetime.now().isoformat())
                    
                    # Check if content is Marine Corps related
                    if self.is_marine_corps_related(title, description):
                        content_hash = self.generate_hash(title, link)
                        category = self.categorize_content(title, description)
                        
                        item = NewsItem(
                            title=title,
                            url=link,
                            source=source_name,
                            published_date=published,
                            description=description,
                            category=category,
                            content_hash=content_hash,
                            scraped_at=datetime.now().isoformat()
                        )
                        items.append(item)
                
                time.sleep(1)  # Be polite
                
            except Exception as e:
                print(f"Error crawling {source_name}: {str(e)}")
                
        return items
    
    def is_marine_corps_related(self, title: str, description: str) -> bool:
        """Check if content is related to Marine Corps"""
        text = f"{title} {description}".lower()
        return any(keyword in text for keyword in self.KEYWORDS)
    
    def scrape_website(self, url: str, source_name: str) -> List[NewsItem]:
        """Scrape a website for Marine Corps news"""
        items = []
        
        try:
            print(f"Scraping website: {source_name}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; MarineCorpsAggregator/1.0)'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article links (adapt selectors as needed)
            articles = soup.find_all(['article', 'div'], class_=re.compile(r'(article|news|post|story)', re.I))
            
            for article in articles[:20]:  # Limit to 20 per site
                title_elem = article.find(['h1', 'h2', 'h3', 'h4', 'a'])
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                link = article.find('a')
                
                if link:
                    href = link.get('href', '')
                    full_url = urljoin(url, href)
                    
                    # Get description
                    desc_elem = article.find(['p', 'div'], class_=re.compile(r'(description|summary|excerpt)', re.I))
                    description = desc_elem.get_text(strip=True) if desc_elem else title
                    
                    if self.is_marine_corps_related(title, description):
                        content_hash = self.generate_hash(title, full_url)
                        category = self.categorize_content(title, description)
                        
                        item = NewsItem(
                            title=title,
                            url=full_url,
                            source=source_name,
                            published_date=datetime.now().isoformat(),
                            description=description,
                            category=category,
                            content_hash=content_hash,
                            scraped_at=datetime.now().isoformat()
                        )
                        items.append(item)
            
            time.sleep(2)  # Be polite
            
        except Exception as e:
            print(f"Error scraping {source_name}: {str(e)}")
            
        return items
    
    def search_google_news(self, query: str = "US Marine Corps") -> List[NewsItem]:
        """
        Search Google News for Marine Corps content
        Note: For production, consider using Google News RSS or API
        """
        items = []
        try:
            # Google News RSS feed
            rss_url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:15]:  # Limit results
                title = entry.get('title', '')
                link = entry.get('link', '')
                description = entry.get('description', '')
                published = entry.get('published', datetime.now().isoformat())
                
                content_hash = self.generate_hash(title, link)
                category = self.categorize_content(title, description)
                
                item = NewsItem(
                    title=title,
                    url=link,
                    source='Google News',
                    published_date=published,
                    description=description,
                    category=category,
                    content_hash=content_hash,
                    scraped_at=datetime.now().isoformat()
                )
                items.append(item)
                
        except Exception as e:
            print(f"Error searching Google News: {str(e)}")
            
        return items
    
    def run_full_crawl(self) -> Dict[str, int]:
        """Run complete crawl of all sources"""
        print("Starting Marine Corps news aggregation...")
        stats = {
            'total_found': 0,
            'new_items': 0,
            'duplicates': 0,
            'by_category': {}
        }
        
        all_items = []
        
        # Crawl RSS feeds
        print("\n=== Crawling RSS Feeds ===")
        all_items.extend(self.crawl_rss_feeds(self.RSS_FEEDS))
        
        # Crawl podcast feeds
        print("\n=== Crawling Podcast Feeds ===")
        all_items.extend(self.crawl_rss_feeds(self.PODCAST_FEEDS))
        
        # Scrape news websites
        print("\n=== Scraping News Websites ===")
        for site_name, site_url in self.NEWS_SITES.items():
            all_items.extend(self.scrape_website(site_url, site_name))
        
        # Search Google News
        print("\n=== Searching Google News ===")
        all_items.extend(self.search_google_news("US Marine Corps"))
        all_items.extend(self.search_google_news("USMC equipment"))
        all_items.extend(self.search_google_news("Marine Corps promotions"))
        
        # Save items
        print(f"\n=== Processing {len(all_items)} items ===")
        stats['total_found'] = len(all_items)
        
        for item in all_items:
            if self.save_item(item):
                stats['new_items'] += 1
                stats['by_category'][item.category] = stats['by_category'].get(item.category, 0) + 1
            else:
                stats['duplicates'] += 1
        
        return stats
    
    def get_recent_items(self, days: int = 7, limit: int = 100) -> List[Dict]:
        """Get recent items from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT title, url, source, published_date, description, category, scraped_at
            FROM news_items
            WHERE scraped_at > ?
            ORDER BY scraped_at DESC
            LIMIT ?
        ''', (cutoff_date, limit))
        
        columns = ['title', 'url', 'source', 'published_date', 'description', 'category', 'scraped_at']
        items = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return items
    
    def export_to_json(self, output_file: str = None):
        """Export recent items to JSON for website integration"""
        if output_file is None:
            output_file = str(DATA_DIR / 'marine_corps_news.json')
        items = self.get_recent_items(days=30, limit=500)
        
        with open(output_file, 'w') as f:
            json.dump({
                'generated_at': datetime.now().isoformat(),
                'total_items': len(items),
                'items': items
            }, f, indent=2)
        
        print(f"Exported {len(items)} items to {output_file}")
        return output_file


def main():
    """Main execution function"""
    aggregator = MarineCorpsAggregator()
    
    # Run full crawl
    stats = aggregator.run_full_crawl()
    
    # Print statistics
    print("\n" + "="*50)
    print("CRAWL COMPLETE")
    print("="*50)
    print(f"Total items found: {stats['total_found']}")
    print(f"New items saved: {stats['new_items']}")
    print(f"Duplicates skipped: {stats['duplicates']}")
    print("\nItems by category:")
    for category, count in stats['by_category'].items():
        print(f"  {category}: {count}")
    
    # Export to JSON
    print("\n" + "="*50)
    aggregator.export_to_json()
    
    # Show sample of recent items
    print("\n" + "="*50)
    print("RECENT ITEMS SAMPLE")
    print("="*50)
    recent = aggregator.get_recent_items(days=7, limit=5)
    for i, item in enumerate(recent, 1):
        print(f"\n{i}. [{item['category'].upper()}] {item['title']}")
        print(f"   Source: {item['source']}")
        print(f"   URL: {item['url']}")


if __name__ == "__main__":
    main()
