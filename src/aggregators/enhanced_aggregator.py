#!/usr/bin/env python3
"""
Enhanced Marine Corps News Aggregator
Features:
- Extracts tags from articles
- Filters to last 90 days (or since last run)
- Incremental updates based on last run time
- Enhanced metadata extraction
- NLP entity extraction
- Parallel processing support
- SEO integration (Ahrefs)
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import time
import re
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Set
import sqlite3
from dataclasses import dataclass, asdict, field
from urllib.parse import urljoin, urlparse
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logging_config import setup_logging
from src.utils.config_manager import config

# Setup logging
logger = setup_logging("aggregator")

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
    category: str
    tags: List[str]  # Article tags
    author: Optional[str]  # Article author
    featured_image_url: Optional[str]  # Featured/main image URL
    content_hash: str
    scraped_at: str
    # New fields for enhanced data
    entities: Optional[Dict[str, List[str]]] = None  # NLP extracted entities
    sentiment: Optional[float] = None  # Sentiment score (-1.0 to 1.0)
    domain_authority: Optional[float] = None  # Ahrefs domain authority
    engagement_score: float = 0.0  # Content priority score
    read_time_minutes: Optional[int] = None  # Estimated read time

    def to_dict(self):
        data = asdict(self)
        # Convert tags list to JSON string for database storage
        data['tags'] = json.dumps(data['tags']) if data['tags'] else '[]'
        # Convert entities dict to JSON string
        data['entities'] = json.dumps(data['entities']) if data['entities'] else None
        return data


class EnhancedMarineCorpsAggregator:
    """Enhanced aggregator with tag support and incremental updates"""
    
    # Official USMC and DoD RSS Feeds
    RSS_FEEDS = {
        'USMC Official': 'https://www.marines.mil/DesktopModules/ArticleCS/RSS.ashx?ContentType=1&Site=1&max=50',
        'Defense.gov': 'https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx?max=100&ContentType=1',
        'Marine Corps Times': 'https://www.marinecorpstimes.com/arc/outboundfeeds/rss/',
        'Stars and Stripes Marines': 'https://www.stripes.com/rss/branches/marines',
        'DVIDS Marines': 'https://www.dvidshub.net/rss/news?unit=USMC',
    }
    
    # Podcast RSS Feeds
    PODCAST_FEEDS = {
        # Official Marine Corps Association Podcasts
        'Marine Corps Association Podcast': 'https://mca-marines.org/podcast/feed/',
        'MCA Scuttlebutt Podcast': 'https://www.mca-marines.org/feed/mca-scuttlebutt/',

        # Marine Corps History and Culture
        'History of the Marine Corps': 'https://rss.libsyn.com/shows/167873/destinations/1119545.xml',

        # Military/Veteran Podcasts (includes Marines)
        'The Warfighter Podcast': 'https://feeds.simplecast.com/vg3bH_Az',
        'Jocko Podcast': 'https://feeds.redcircle.com/64a89f88-a245-4098-8d8d-496325ec4f74',
        'Zero Blog Thirty': 'https://mcsorleys.barstoolsports.com/feed/zero-blog-thirty',
        'The Team House': 'https://www.spreaker.com/show/5960890/episodes/feed',
        'The Smoke Pit': 'https://feeds.acast.com/public/shows/5bddd6bc31355f1367f4a5dc',

        # Navy/Marine Corps National Security
        'Midrats': 'https://www.spreaker.com/show/3270000/episodes/feed',

        # Marine Corps Acquisition and Innovation
        'Equipping the Corps': 'https://anchor.fm/s/6aa53e5c/podcast/rss',

        # Additional Marine Corps Podcasts - FOUND AND ACTIVE
        'Behind the Camouflage Podcast': 'https://www.mca-marines.org/feed/behind-the-camouflage-podcast/',  # MCA - USMC spouses
        'The Quarter Deck with Gunny Saenz': 'https://anchor.fm/s/eb1d52cc/podcast/rss',  # Life after USMC
        'Tracking Our History': 'https://anchor.fm/s/1e0c99dc/podcast/rss',  # Vietnam-era tank crews
        'Semper Sometimes': 'https://anchor.fm/s/60807054/podcast/rss',  # USMC culture and humor
        'Stories With a Marine Corps Dad': 'https://feeds.buzzsprout.com/1835241.rss',  # Family storytelling
        'The Marine Corps Movie Minute': 'https://pinecast.com/feed/the-marine-corps-movie-minute',  # Marines in film
        'STRAT – Strategic Risk Assessment Talk': 'https://feeds.captivate.fm/strat/',  # Hal Kempfer

        # Pending - RSS Feeds Not Found Yet
        # 'Corps Voices': 'RSS_FEED_URL_HERE',  # MCA - Direct audio files only, no RSS feed
        # 'Tavern Talk by Belleau Wood Tavern': 'RSS_FEED_URL_HERE',  # Only on iHeart
        # 'Constant Combat': 'RSS_FEED_URL_HERE',  # 2/4 Marines Ramadi - Not found
    }
    
    # News sites to scrape
    NEWS_SITES = {
        'DVIDS Marines': 'https://www.dvidshub.net/unit/USMC',
        'Marine Corps Base Camp Pendleton': 'https://www.pendleton.marines.mil/News/',
        'Marine Corps Base Camp Lejeune': 'https://www.lejeune.marines.mil/News/',
        'Marine Corps Air Station Miramar': 'https://www.miramar.marines.mil/News/',
        'Marine Corps Recruit Depot San Diego': 'https://www.mcrdsd.marines.mil/News/',
        'Marine Corps Recruit Depot Parris Island': 'https://www.mcrdpi.marines.mil/News/',
        # Additional bases and units you can add:
        # 'Marine Corps Base Hawaii': 'https://www.mcbhawaii.marines.mil/News/',
        # 'Marine Corps Base Quantico': 'https://www.quantico.marines.mil/News/',
        # 'Marine Corps Air Station Beaufort': 'https://www.beaufort.marines.mil/News/',
        # 'Marine Corps Air Station Iwakuni': 'https://www.mcasiwakuni.marines.mil/News/',
        # 'Marine Corps Base Camp Butler': 'https://www.mccsokinawa.com/news/',
    }
    
    # Keywords for filtering and categorization
    KEYWORDS = [
        'marine corps', 'usmc', 'marines', 'jarhead', 'leatherneck',
        'semper fi', 'semper fidelis', 'devil dog', 'humvee', 'hmmwv', 
        'mrap', 'amphibious', 'meu', 'marine expeditionary',
        'navy cross', 'purple heart', 'meritorious service medal',
        'promotion', 'general', 'sergeant major', 'commandant',
        'f-35b', 'mv-22', 'osprey', 'ch-53', 'aav', 'lcac',
        'infantry', 'artillery', 'aviation', 'logistics'
    ]
    
    EQUIPMENT_KEYWORDS = [
        'jltv', 'acv', 'amphibious combat vehicle', 'light armored vehicle',
        'lav', 'm1a1', 'abrams', 'howitzer', 'm777', 'himars',
        'javelin', 'stinger', 'nlaw', 'nmesis', 'rogue fires'
    ]
    
    def __init__(self, db_path: str = None, max_age_days: int = 90, max_workers: int = None):
        """Initialize the aggregator with parallel processing support"""
        if db_path is None:
            db_path = str(DATA_DIR / 'marine_corps_news.db')
        self.db_path = db_path
        self.max_age_days = max_age_days
        # Cached per-crawl cutoff date; computed once and reused for every
        # article so we don't reopen the DB (and re-log) on each check.
        self._cutoff_date = None
        self.max_workers = max_workers or config.max_workers
        self.rate_limiter = Semaphore(self.max_workers)

        # Setup HTTP session with connection pooling
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=requests.adapters.Retry(
                total=3,
                backoff_factor=0.5,
                status_forcelist=[429, 500, 502, 503, 504]
            )
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        self.init_database()
        logger.info(f"Aggregator initialized with {self.max_workers} workers")
        
    def init_database(self):
        """Initialize SQLite database with enhanced schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Main news items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL,
                published_date TEXT,
                description TEXT,
                category TEXT,
                tags TEXT,
                author TEXT,
                featured_image_url TEXT,
                content_hash TEXT UNIQUE,
                scraped_at TEXT NOT NULL,
                posted_to_site BOOLEAN DEFAULT 0,
                entities TEXT,
                sentiment REAL,
                domain_authority REAL,
                engagement_score REAL DEFAULT 0.0,
                read_time_minutes INTEGER
            )
        ''')

        # Add new columns if they don't exist (for existing databases)
        new_columns = [
            ('featured_image_url', 'TEXT', None),
            ('entities', 'TEXT', None),
            ('sentiment', 'REAL', None),
            ('domain_authority', 'REAL', None),
            ('engagement_score', 'REAL', '0.0'),
            ('read_time_minutes', 'INTEGER', None),
        ]

        for col_name, col_type, default in new_columns:
            try:
                if default:
                    cursor.execute(f'ALTER TABLE news_items ADD COLUMN {col_name} {col_type} DEFAULT {default}')
                else:
                    cursor.execute(f'ALTER TABLE news_items ADD COLUMN {col_name} {col_type}')
            except sqlite3.OperationalError:
                pass  # Column already exists

        # Track last successful run
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS run_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_time TEXT NOT NULL,
                items_collected INTEGER,
                status TEXT,
                notes TEXT
            )
        ''')

        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_published_date ON news_items(published_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON news_items(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scraped_at ON news_items(scraped_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_domain_authority ON news_items(domain_authority)')

        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
        
    def get_last_run_time(self) -> Optional[datetime]:
        """Get the timestamp of the last successful run"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT run_time FROM run_history 
            WHERE status = 'success' 
            ORDER BY run_time DESC LIMIT 1
        ''')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return datetime.fromisoformat(result[0])
        return None
    
    def record_run(self, items_collected: int, status: str = 'success', notes: str = ''):
        """Record this run in the history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO run_history (run_time, items_collected, status, notes)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().isoformat(), items_collected, status, notes))
        conn.commit()
        conn.close()
    
    def get_cutoff_date(self) -> datetime:
        """Get the cutoff date for article collection.

        Memoized per crawl: the first call computes the cutoff (one DB read,
        one log line) and caches it. ``run_full_crawl`` clears the cache so each
        scheduled run recomputes a fresh cutoff.
        """
        if self._cutoff_date is not None:
            return self._cutoff_date

        last_run = self.get_last_run_time()

        if last_run:
            # Use last run time if it's within the max age
            max_cutoff = datetime.now() - timedelta(days=self.max_age_days)
            cutoff = max(last_run, max_cutoff)
            logger.info(f"Using incremental update since: {cutoff.strftime('%Y-%m-%d %H:%M')}")
        else:
            # First run: go back 90 days
            cutoff = datetime.now() - timedelta(days=self.max_age_days)
            logger.info(f"First run: collecting articles from last {self.max_age_days} days")

        self._cutoff_date = cutoff
        return cutoff
    
    def is_within_date_range(self, date_str: str) -> bool:
        """Check if a date is within our acceptable range"""
        if not date_str:
            return True  # Include if no date (will be marked with scraped_at)
        
        try:
            cutoff = self.get_cutoff_date()
            article_date = self.parse_date(date_str)
            
            if article_date:
                return article_date >= cutoff
            return True
        except Exception as e:
            logger.debug(f"Date parsing error: {e}")
            return True
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats"""
        if not date_str:
            return None
            
        # Try common formats
        formats = [
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%a, %d %b %Y %H:%M:%S %Z',
            '%a, %d %b %Y %H:%M:%S %z',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str[:19], fmt[:19])
            except ValueError:
                continue
        
        return None
    
    def extract_tags_from_feed_entry(self, entry: dict) -> List[str]:
        """Extract tags from RSS feed entry"""
        tags = set()
        
        # Check for standard RSS tags
        if 'tags' in entry:
            for tag in entry['tags']:
                if 'term' in tag:
                    tags.add(tag['term'])
        
        # Check for categories
        if 'categories' in entry:
            for cat in entry['categories']:
                if isinstance(cat, str):
                    tags.add(cat)
                elif isinstance(cat, dict) and 'term' in cat:
                    tags.add(cat['term'])
        
        # Check media namespace tags
        if 'media_keywords' in entry:
            tags.update(entry['media_keywords'].split(','))
        
        return [tag.strip() for tag in tags if tag.strip()]
    
    def extract_tags_from_webpage(self, soup: BeautifulSoup) -> List[str]:
        """Extract tags from webpage HTML"""
        tags = set()
        
        # Look for common tag patterns
        # Meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            tags.update([t.strip() for t in meta_keywords['content'].split(',')])
        
        # Article tags (common in news sites)
        tag_containers = soup.find_all(['div', 'ul'], class_=re.compile(r'tag|category|topic', re.I))
        for container in tag_containers:
            tag_links = container.find_all('a')
            for link in tag_links:
                tag_text = link.get_text(strip=True)
                if tag_text and len(tag_text) < 30:  # Reasonable tag length
                    tags.add(tag_text)
        
        # Marines.mil specific tag extraction
        tag_elements = soup.find_all('a', href=re.compile(r'/Topics/'))
        for elem in tag_elements:
            tags.add(elem.get_text(strip=True))
        
        return [tag.strip() for tag in tags if tag.strip()]
    
    def extract_image_from_feed_entry(self, entry: dict) -> Optional[str]:
        """Extract featured image URL from RSS feed entry"""
        # Check media_content (common in RSS 2.0 with media namespace)
        if 'media_content' in entry:
            for media in entry.get('media_content', []):
                media_type = media.get('type', '')
                if media_type.startswith('image/') or not media_type:
                    url = media.get('url')
                    if url:
                        return url

        # Check media_thumbnail
        if 'media_thumbnail' in entry:
            thumbs = entry.get('media_thumbnail', [])
            if thumbs:
                # Get the largest thumbnail if multiple exist
                if isinstance(thumbs, list) and len(thumbs) > 0:
                    # Sort by width if available, otherwise take first
                    sorted_thumbs = sorted(
                        thumbs,
                        key=lambda x: int(x.get('width', 0)),
                        reverse=True
                    )
                    return sorted_thumbs[0].get('url')

        # Check enclosures (common for podcasts, sometimes has images)
        if 'enclosures' in entry:
            for encl in entry.get('enclosures', []):
                encl_type = encl.get('type', '')
                if 'image' in encl_type:
                    return encl.get('url')

        # Check for image in links
        if 'links' in entry:
            for link in entry.get('links', []):
                link_type = link.get('type', '')
                if link_type.startswith('image/'):
                    return link.get('href')

        # Check itunes:image (common in podcast feeds)
        if 'image' in entry:
            img = entry.get('image')
            if isinstance(img, dict):
                return img.get('href') or img.get('url')
            elif isinstance(img, str):
                return img

        return None

    def extract_image_from_webpage(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract featured image URL from webpage HTML"""
        # 1. Open Graph image (most reliable for featured/social images)
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            img_url = og_image['content']
            return urljoin(base_url, img_url)

        # 2. Twitter card image
        tw_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if tw_image and tw_image.get('content'):
            img_url = tw_image['content']
            return urljoin(base_url, img_url)

        # 3. Schema.org image
        schema_image = soup.find('meta', attrs={'itemprop': 'image'})
        if schema_image and schema_image.get('content'):
            img_url = schema_image['content']
            return urljoin(base_url, img_url)

        # 4. Look for featured image with common class names
        featured_classes = ['featured-image', 'hero-image', 'main-image',
                          'article-image', 'post-thumbnail', 'entry-image']
        for class_name in featured_classes:
            img = soup.find('img', class_=re.compile(class_name, re.I))
            if img:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src:
                    return urljoin(base_url, src)

        # 5. First image in article/main content
        article = soup.find(['article', 'main', 'div'], class_=re.compile(r'article|content|post', re.I))
        if article:
            img = article.find('img')
            if img:
                src = img.get('src') or img.get('data-src')
                if src and not self._is_icon_or_logo(src):
                    return urljoin(base_url, src)

        # 6. Marines.mil specific: look for news image
        marines_img = soup.find('img', class_=re.compile(r'news|story', re.I))
        if marines_img:
            src = marines_img.get('src') or marines_img.get('data-src')
            if src:
                return urljoin(base_url, src)

        return None

    def _is_icon_or_logo(self, url: str) -> bool:
        """Check if URL appears to be an icon or logo rather than content image"""
        url_lower = url.lower()
        skip_patterns = ['logo', 'icon', 'avatar', 'badge', 'button',
                        'sprite', 'pixel', '1x1', 'tracking', 'ad-']
        return any(pattern in url_lower for pattern in skip_patterns)

    def extract_author(self, entry: dict = None, soup: BeautifulSoup = None) -> Optional[str]:
        """Extract author information"""
        if entry:
            # From RSS feed
            if 'author' in entry:
                return entry['author']
            if 'authors' in entry and entry['authors']:
                return entry['authors'][0].get('name', '')
        
        if soup:
            # From webpage
            author_meta = soup.find('meta', attrs={'name': re.compile(r'author', re.I)})
            if author_meta and author_meta.get('content'):
                return author_meta['content']
            
            # Look for byline
            byline = soup.find(['span', 'div', 'p'], class_=re.compile(r'author|byline', re.I))
            if byline:
                return byline.get_text(strip=True)
        
        return None
    
    def enrich_article_metadata(self, url: str, existing_tags: List[str], existing_image: Optional[str] = None) -> Dict:
        """Fetch article page and extract additional metadata including featured image"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; MarineCorpsAggregator/2.0)'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract additional tags
            page_tags = self.extract_tags_from_webpage(soup)
            all_tags = list(set(existing_tags + page_tags))

            # Extract author
            author = self.extract_author(soup=soup)

            # Extract featured image (only if not already found from RSS)
            featured_image = existing_image
            if not featured_image:
                featured_image = self.extract_image_from_webpage(soup, url)

            return {
                'tags': all_tags,
                'author': author,
                'featured_image_url': featured_image
            }

        except Exception as e:
            logger.warning(f"Error enriching metadata for {url}: {e}")
            return {'tags': existing_tags, 'author': None, 'featured_image_url': existing_image}
    
    def is_duplicate(self, content_hash: str) -> bool:
        """Check if item already exists in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM news_items WHERE content_hash = ?', (content_hash,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def save_item(self, item: NewsItem) -> bool:
        """Save news item to database with all enhanced fields"""
        if self.is_duplicate(item.content_hash):
            return False

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            item_dict = item.to_dict()
            cursor.execute('''
                INSERT INTO news_items
                (title, url, source, published_date, description, category, tags, author,
                 featured_image_url, content_hash, scraped_at, entities, sentiment,
                 domain_authority, engagement_score, read_time_minutes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (item_dict['title'], item_dict['url'], item_dict['source'],
                  item_dict['published_date'], item_dict['description'],
                  item_dict['category'], item_dict['tags'], item_dict['author'],
                  item_dict['featured_image_url'], item_dict['content_hash'],
                  item_dict['scraped_at'], item_dict.get('entities'),
                  item_dict.get('sentiment'), item_dict.get('domain_authority'),
                  item_dict.get('engagement_score', 0.0), item_dict.get('read_time_minutes')))
            conn.commit()
            logger.debug(f"Saved article: {item.title[:50]}...")
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def generate_hash(self, title: str, url: str) -> str:
        """Generate unique hash for content"""
        content = f"{title}{url}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def categorize_content(self, title: str, description: str, tags: List[str]) -> str:
        """Categorize content based on keywords and tags"""
        text = f"{title} {description} {' '.join(tags)}".lower()
        
        # Check tags first for more accurate categorization
        tag_text = ' '.join(tags).lower()
        
        if any(word in text for word in ['award', 'medal', 'decoration', 'honor', 'citation']):
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
        """Crawl RSS feeds with enhanced metadata extraction including images"""
        items = []

        for source_name, feed_url in feeds_dict.items():
            try:
                logger.info(f"Crawling RSS feed: {source_name}")
                feed = feedparser.parse(feed_url)

                for entry in feed.entries:
                    # Check date first
                    published = entry.get('published', entry.get('updated', ''))
                    if not self.is_within_date_range(published):
                        continue

                    title = entry.get('title', '')
                    link = entry.get('link', '')
                    description = entry.get('description', '') or entry.get('summary', '')

                    # Check if content is Marine Corps related
                    if not self.is_marine_corps_related(title, description):
                        continue

                    # Extract tags from feed
                    tags = self.extract_tags_from_feed_entry(entry)

                    # Extract author
                    author = self.extract_author(entry=entry)

                    # Extract featured image from RSS entry
                    featured_image = self.extract_image_from_feed_entry(entry)

                    # For marines.mil articles, enrich with page data (including image if not found)
                    if 'marines.mil' in link and (len(tags) < 3 or not featured_image):
                        metadata = self.enrich_article_metadata(link, tags, featured_image)
                        tags = metadata['tags']
                        if not author:
                            author = metadata['author']
                        if not featured_image:
                            featured_image = metadata.get('featured_image_url')

                    # Categorize
                    category = self.categorize_content(title, description, tags)
                    content_hash = self.generate_hash(title, link)

                    item = NewsItem(
                        title=title,
                        url=link,
                        source=source_name,
                        published_date=published or datetime.now().isoformat(),
                        description=description,
                        category=category,
                        tags=tags,
                        author=author,
                        featured_image_url=featured_image,
                        content_hash=content_hash,
                        scraped_at=datetime.now().isoformat()
                    )
                    items.append(item)

                time.sleep(1)  # Be polite

            except Exception as e:
                logger.error(f"Error crawling {source_name}: {str(e)}", exc_info=True)

        return items
    
    def is_marine_corps_related(self, title: str, description: str) -> bool:
        """Check if content is related to Marine Corps"""
        text = f"{title} {description}".lower()
        return any(keyword in text for keyword in self.KEYWORDS)
    
    def run_full_crawl(self) -> Dict[str, int]:
        """Run complete crawl of all sources"""
        logger.info("=" * 60)
        logger.info("Enhanced Marine Corps News Aggregation")
        logger.info(f"Max article age: {self.max_age_days} days")
        logger.info("=" * 60)

        # Recompute the cutoff once for this crawl (the scheduler reuses one
        # aggregator instance across runs).
        self._cutoff_date = None

        stats = {
            'total_found': 0,
            'new_items': 0,
            'duplicates': 0,
            'filtered_by_date': 0,
            'by_category': {}
        }
        
        all_items = []

        # Crawl RSS feeds
        logger.info("=== Crawling RSS Feeds ===")
        all_items.extend(self.crawl_rss_feeds(self.RSS_FEEDS))

        # Crawl podcast feeds
        logger.info("=== Crawling Podcast Feeds ===")
        all_items.extend(self.crawl_rss_feeds(self.PODCAST_FEEDS))

        # Save items
        logger.info(f"=== Processing {len(all_items)} items ===")
        stats['total_found'] = len(all_items)
        
        for item in all_items:
            if self.save_item(item):
                stats['new_items'] += 1
                stats['by_category'][item.category] = stats['by_category'].get(item.category, 0) + 1
            else:
                stats['duplicates'] += 1
        
        # Record this run
        self.record_run(stats['new_items'])
        
        return stats
    
    def get_recent_items(self, days: int = 7, limit: int = 100) -> List[Dict]:
        """Get recent items from database with tags and featured image"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute('''
            SELECT title, url, source, published_date, description, category, tags, author, featured_image_url, scraped_at
            FROM news_items
            WHERE scraped_at > ?
            ORDER BY published_date DESC
            LIMIT ?
        ''', (cutoff_date, limit))

        columns = ['title', 'url', 'source', 'published_date', 'description', 'category', 'tags', 'author', 'featured_image_url', 'scraped_at']
        items = []
        for row in cursor.fetchall():
            item = dict(zip(columns, row))
            # Parse tags from JSON string
            item['tags'] = json.loads(item['tags']) if item['tags'] else []
            items.append(item)

        conn.close()
        return items
    
    def export_to_json(self, output_file: str = None):
        """Export recent items to JSON"""
        if output_file is None:
            output_file = str(DATA_DIR / 'marine_corps_news.json')
        items = self.get_recent_items(days=self.max_age_days, limit=5000)
        
        with open(output_file, 'w') as f:
            json.dump({
                'generated_at': datetime.now().isoformat(),
                'total_items': len(items),
                'max_age_days': self.max_age_days,
                'items': items
            }, f, indent=2)
        
        logger.info(f"Exported {len(items)} items to {output_file}")
        return output_file
    
    def print_sample_articles(self, limit: int = 5):
        """Print sample of recent articles with full details"""
        items = self.get_recent_items(days=7, limit=limit)

        logger.info("=" * 60)
        logger.info(f"SAMPLE OF {len(items)} RECENT ARTICLES")
        logger.info("=" * 60)

        for i, item in enumerate(items, 1):
            logger.info(f"{i}. {item['title']}")
            logger.info(f"   Source: {item['source']} | Category: {item['category']}")
            logger.info(f"   Published: {item['published_date']}")
            if item['author']:
                logger.info(f"   Author: {item['author']}")
            if item['tags']:
                logger.info(f"   Tags: {', '.join(item['tags'][:5])}")
            logger.info(f"   URL: {item['url']}")
            logger.info("-" * 60)


def main():
    """Main execution function"""
    # Use 90 days for max age
    aggregator = EnhancedMarineCorpsAggregator(max_age_days=90)

    # Run full crawl
    stats = aggregator.run_full_crawl()

    # Log statistics
    logger.info("=" * 60)
    logger.info("CRAWL COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total items found: {stats['total_found']}")
    logger.info(f"New items saved: {stats['new_items']}")
    logger.info(f"Duplicates skipped: {stats['duplicates']}")
    logger.info("Items by category:")
    for category, count in stats['by_category'].items():
        logger.info(f"  {category}: {count}")

    # Export to JSON
    logger.info("=" * 60)
    aggregator.export_to_json()

    # Show sample of articles with full details
    aggregator.print_sample_articles(limit=10)


if __name__ == "__main__":
    main()
