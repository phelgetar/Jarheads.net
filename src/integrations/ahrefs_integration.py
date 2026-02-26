#!/usr/bin/env python3
"""
Ahrefs SEO Integration for Marine Corps News Aggregator
Fetches domain authority and SEO metrics for news sources
"""

import time
import sys
from pathlib import Path
from typing import Dict, Optional, List
from urllib.parse import urlparse
from datetime import datetime, timedelta

import requests

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logging_config import setup_logging
from src.utils.config_manager import config

logger = setup_logging("ahrefs_integration")


class AhrefsClient:
    """
    Client for Ahrefs API to fetch domain authority and SEO metrics.

    Note: Ahrefs API requires a paid subscription. This client provides
    a fallback with estimated domain authority for common news sources
    when API access is not available.
    """

    BASE_URL = "https://api.ahrefs.com/v3"

    # Fallback domain authority estimates for known news sources
    KNOWN_DOMAIN_AUTHORITIES = {
        'marines.mil': 85,
        'defense.gov': 90,
        'marinecorpstimes.com': 65,
        'stripes.com': 70,
        'dvidshub.net': 75,
        'military.com': 80,
        'militarytimes.com': 70,
        'usni.org': 65,
        'sandboxx.us': 55,
        'sofrep.com': 60,
        'coffeeordie.com': 55,
        'taskandpurpose.com': 60,
        'news.google.com': 95,
        'apnews.com': 92,
        'reuters.com': 94,
        'cnn.com': 93,
        'foxnews.com': 92,
    }

    def __init__(self):
        """Initialize the Ahrefs client"""
        self.api_key = config.ahrefs_api_key
        self.available = self.api_key is not None
        self._cache: Dict[str, Dict] = {}  # domain -> {authority, timestamp}
        self._cache_ttl = timedelta(hours=24)
        self._rate_limit_delay = 0.5  # seconds between API calls

        if self.available:
            logger.info("Ahrefs API client initialized")
        else:
            logger.warning("Ahrefs API key not configured. Using estimated domain authorities.")

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        domain = parsed.netloc
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain

    def _is_cache_valid(self, domain: str) -> bool:
        """Check if cached data is still valid"""
        if domain not in self._cache:
            return False
        cached = self._cache[domain]
        return datetime.now() - cached['timestamp'] < self._cache_ttl

    def get_domain_authority(self, url: str) -> Optional[float]:
        """
        Get domain authority (rating) for a URL's domain.

        Args:
            url: URL to check

        Returns:
            Domain authority score (0-100) or None if unavailable
        """
        domain = self._get_domain(url)

        # Check cache first
        if self._is_cache_valid(domain):
            return self._cache[domain]['authority']

        # Try API if available
        if self.available:
            authority = self._fetch_from_api(domain)
            if authority is not None:
                self._cache[domain] = {
                    'authority': authority,
                    'timestamp': datetime.now()
                }
                return authority

        # Fallback to known domains
        if domain in self.KNOWN_DOMAIN_AUTHORITIES:
            authority = float(self.KNOWN_DOMAIN_AUTHORITIES[domain])
            self._cache[domain] = {
                'authority': authority,
                'timestamp': datetime.now()
            }
            return authority

        # Check for partial matches (e.g., subdomains)
        for known_domain, known_authority in self.KNOWN_DOMAIN_AUTHORITIES.items():
            if known_domain in domain or domain in known_domain:
                authority = float(known_authority)
                self._cache[domain] = {
                    'authority': authority,
                    'timestamp': datetime.now()
                }
                return authority

        # Unknown domain
        logger.debug(f"No domain authority data for: {domain}")
        return None

    def _fetch_from_api(self, domain: str) -> Optional[float]:
        """
        Fetch domain rating from Ahrefs API.

        Args:
            domain: Domain to check

        Returns:
            Domain rating or None if request fails
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/site-explorer/domain-rating",
                headers={"Authorization": f"Bearer {self.api_key}"},
                params={
                    "target": domain,
                    "mode": "domain"
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            authority = data.get('domain_rating', data.get('domain_rating_score'))

            time.sleep(self._rate_limit_delay)
            logger.debug(f"Fetched DA for {domain}: {authority}")
            return float(authority) if authority is not None else None

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.error("Ahrefs API authentication failed. Check your API key.")
                self.available = False
            elif e.response.status_code == 429:
                logger.warning("Ahrefs API rate limit reached. Using cached/fallback data.")
            else:
                logger.error(f"Ahrefs API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching domain authority: {e}")
            return None

    def get_metrics(self, url: str) -> Dict:
        """
        Get all available SEO metrics for a URL.

        Args:
            url: URL to analyze

        Returns:
            Dict with domain_authority and other metrics
        """
        domain = self._get_domain(url)
        authority = self.get_domain_authority(url)

        return {
            'domain': domain,
            'domain_authority': authority,
            'is_official': domain.endswith('.mil') or domain.endswith('.gov'),
            'source_tier': self._classify_source_tier(authority),
        }

    def _classify_source_tier(self, authority: Optional[float]) -> str:
        """
        Classify source into tiers based on domain authority.

        Args:
            authority: Domain authority score

        Returns:
            Tier classification (primary, secondary, tertiary, unknown)
        """
        if authority is None:
            return 'unknown'
        elif authority >= 80:
            return 'primary'  # Official/major sources
        elif authority >= 60:
            return 'secondary'  # Established news sources
        elif authority >= 40:
            return 'tertiary'  # Smaller/niche sources
        else:
            return 'minor'

    def enrich_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Add domain authority to a list of articles.

        Args:
            articles: List of article dictionaries with 'url' key

        Returns:
            Articles with 'domain_authority' added
        """
        for article in articles:
            if 'url' in article:
                article['domain_authority'] = self.get_domain_authority(article['url'])
        return articles

    def calculate_engagement_score(self, article: Dict) -> float:
        """
        Calculate an engagement/priority score for an article.

        Factors in:
        - Domain authority
        - Whether source is official (.mil/.gov)
        - Content freshness (if published_date available)
        - Category importance

        Args:
            article: Article dictionary

        Returns:
            Engagement score (0-100)
        """
        score = 50.0  # Base score

        # Domain authority factor (0-30 points)
        da = article.get('domain_authority')
        if da is not None:
            score += (da / 100) * 30

        # Official source bonus (10 points)
        url = article.get('url', '')
        if '.mil' in url or '.gov' in url:
            score += 10

        # Category importance (0-10 points)
        category_weights = {
            'awards': 8,
            'promotions': 7,
            'operations': 9,
            'equipment': 8,
            'training': 6,
            'podcast': 5,
            'general': 5,
        }
        category = article.get('category', 'general')
        score += category_weights.get(category, 5)

        # Freshness bonus (if published within last 24 hours)
        try:
            pub_date = article.get('published_date')
            if pub_date:
                pub_datetime = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                age_hours = (datetime.now() - pub_datetime.replace(tzinfo=None)).total_seconds() / 3600
                if age_hours < 24:
                    score += 10 * (1 - age_hours / 24)
        except (ValueError, TypeError):
            pass

        return min(100.0, max(0.0, score))

    def get_cache_stats(self) -> Dict:
        """Get statistics about the cache"""
        valid_entries = sum(1 for d in self._cache if self._is_cache_valid(d))
        return {
            'total_entries': len(self._cache),
            'valid_entries': valid_entries,
            'known_domains': len(self.KNOWN_DOMAIN_AUTHORITIES),
            'api_available': self.available,
        }


# Singleton instance
_client = None


def get_ahrefs_client() -> AhrefsClient:
    """Get or create the singleton Ahrefs client instance"""
    global _client
    if _client is None:
        _client = AhrefsClient()
    return _client


if __name__ == "__main__":
    # Test the Ahrefs integration
    client = AhrefsClient()

    test_urls = [
        "https://www.marines.mil/News/Article/12345",
        "https://www.marinecorpstimes.com/news/your-marine-corps/2024/01/15/test",
        "https://www.dvidshub.net/news/123456/test-article",
        "https://www.defense.gov/News/Article/12345",
        "https://www.stripes.com/branches/marines/test",
        "https://www.unknown-source.com/article",
    ]

    print("Testing Ahrefs Integration")
    print("=" * 60)
    print(f"API Available: {client.available}")
    print()

    for url in test_urls:
        metrics = client.get_metrics(url)
        print(f"URL: {url[:50]}...")
        print(f"  Domain: {metrics['domain']}")
        print(f"  Authority: {metrics['domain_authority']}")
        print(f"  Tier: {metrics['source_tier']}")
        print(f"  Official: {metrics['is_official']}")
        print()

    # Test engagement score
    test_article = {
        'url': 'https://www.marines.mil/News/Test',
        'category': 'operations',
        'published_date': datetime.now().isoformat(),
        'domain_authority': 85,
    }
    score = client.calculate_engagement_score(test_article)
    print(f"Engagement score for test article: {score:.1f}")

    print("\nCache Stats:", client.get_cache_stats())
