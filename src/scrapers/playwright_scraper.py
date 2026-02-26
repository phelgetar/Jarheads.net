#!/usr/bin/env python3
"""
Playwright Browser Scraper for Marine Corps News Aggregator
Handles JavaScript-rendered sites like DVIDS and modern military news portals
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logging_config import setup_logging
from src.utils.config_manager import config

logger = setup_logging("playwright_scraper")

# Try to import Playwright
try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not installed. Run: pip install playwright && playwright install chromium")


class PlaywrightScraper:
    """
    Async browser scraper for JavaScript-rendered content.

    Features:
    - Handles cookie consent dialogs
    - Supports infinite scroll and lazy loading
    - Extracts articles from dynamic pages
    - Respects politeness delays
    """

    # Common cookie consent button selectors
    COOKIE_CONSENT_SELECTORS = [
        'button:has-text("Accept")',
        'button:has-text("Accept All")',
        'button:has-text("I Agree")',
        'button:has-text("Agree")',
        'button:has-text("OK")',
        'button:has-text("Got it")',
        '[id*="cookie"] button',
        '[class*="cookie"] button',
        '[id*="consent"] button',
        '[class*="consent"] button',
        '[data-testid*="accept"]',
    ]

    # Site-specific configurations
    SITE_CONFIGS = {
        'dvidshub.net': {
            'article_selector': '.asset-list-item, .news-item, .asset-card',
            'title_selector': 'h3, h4, .title, .asset-title',
            'link_selector': 'a',
            'description_selector': '.description, .summary, p',
            'image_selector': 'img',
            'scroll_count': 3,
            'wait_selector': '.asset-list-item',
        },
        'marines.mil': {
            'article_selector': '.dgov-grid-item, .news-item, article',
            'title_selector': 'h3, h4, .title',
            'link_selector': 'a',
            'description_selector': '.description, .summary',
            'image_selector': 'img',
            'scroll_count': 2,
            'wait_selector': '.dgov-grid-item',
        },
        'default': {
            'article_selector': 'article, .news-item, .post, .story',
            'title_selector': 'h2, h3, h4, .title',
            'link_selector': 'a',
            'description_selector': '.description, .summary, .excerpt, p',
            'image_selector': 'img',
            'scroll_count': 2,
            'wait_selector': 'article',
        }
    }

    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        Initialize the Playwright scraper.

        Args:
            headless: Run browser in headless mode (default: True)
            timeout: Default timeout for page operations in ms (default: 30000)
        """
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not available - browser scraping disabled")
            self.available = False
            return

        self.headless = headless
        self.timeout = timeout
        self.politeness_delay = config.crawl_delay
        self.browser: Optional[Browser] = None
        self.playwright = None
        self.available = True

    async def __aenter__(self):
        """Async context manager entry"""
        if not self.available:
            return self

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        logger.info("Playwright browser started")
        return self

    async def __aexit__(self, *args):
        """Async context manager exit"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Playwright browser closed")

    def _get_site_config(self, url: str) -> Dict:
        """Get configuration for a specific site"""
        for domain, config in self.SITE_CONFIGS.items():
            if domain in url:
                return config
        return self.SITE_CONFIGS['default']

    async def _handle_cookie_consent(self, page: Page) -> bool:
        """
        Handle common cookie consent dialogs.

        Args:
            page: Playwright page object

        Returns:
            True if consent dialog was handled, False otherwise
        """
        for selector in self.COOKIE_CONSENT_SELECTORS:
            try:
                button = page.locator(selector).first
                if await button.count() > 0:
                    await button.click(timeout=2000)
                    logger.debug(f"Clicked cookie consent button: {selector}")
                    await page.wait_for_timeout(500)
                    return True
            except Exception:
                continue
        return False

    async def _scroll_to_load(self, page: Page, scroll_count: int = 3) -> None:
        """
        Scroll page to trigger lazy loading and infinite scroll.

        Args:
            page: Playwright page object
            scroll_count: Number of scroll iterations
        """
        for i in range(scroll_count):
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(1000)
            logger.debug(f"Scroll iteration {i + 1}/{scroll_count}")

    async def scrape_page(self, url: str) -> List[Dict]:
        """
        Scrape articles from a JavaScript-rendered page.

        Args:
            url: URL to scrape

        Returns:
            List of article dictionaries with title, url, description, image
        """
        if not self.available or not self.browser:
            logger.error("Browser not available")
            return []

        site_config = self._get_site_config(url)
        articles = []

        try:
            context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = await context.new_page()

            logger.info(f"Navigating to: {url}")
            await page.goto(url, wait_until='networkidle', timeout=self.timeout)

            # Handle cookie consent
            await self._handle_cookie_consent(page)

            # Wait for content to load
            try:
                await page.wait_for_selector(
                    site_config['wait_selector'],
                    timeout=10000
                )
            except Exception:
                logger.warning(f"Timeout waiting for {site_config['wait_selector']}")

            # Scroll to load more content
            await self._scroll_to_load(page, site_config['scroll_count'])

            # Extract articles using JavaScript
            articles = await page.evaluate('''(config) => {
                const items = [];
                const articles = document.querySelectorAll(config.article_selector);

                articles.forEach(article => {
                    const titleEl = article.querySelector(config.title_selector);
                    const linkEl = article.querySelector(config.link_selector);
                    const descEl = article.querySelector(config.description_selector);
                    const imgEl = article.querySelector(config.image_selector);

                    if (titleEl && linkEl) {
                        items.push({
                            title: titleEl.textContent?.trim() || '',
                            url: linkEl.href || '',
                            description: descEl?.textContent?.trim() || '',
                            image: imgEl?.src || imgEl?.getAttribute('data-src') || ''
                        });
                    }
                });

                return items;
            }''', site_config)

            # Filter valid articles
            articles = [
                a for a in articles
                if a.get('title') and a.get('url') and a['url'].startswith('http')
            ]

            logger.info(f"Extracted {len(articles)} articles from {url}")

            await context.close()

            # Politeness delay
            await asyncio.sleep(self.politeness_delay)

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}", exc_info=True)

        return articles

    async def scrape_dvids(self, unit: str = "USMC") -> List[Dict]:
        """
        Scrape articles from DVIDS for a specific unit.

        Args:
            unit: Military unit to search for (default: USMC)

        Returns:
            List of article dictionaries
        """
        url = f"https://www.dvidshub.net/unit/{unit}"
        return await self.scrape_page(url)

    async def scrape_marines_mil(self, section: str = "News") -> List[Dict]:
        """
        Scrape articles from Marines.mil.

        Args:
            section: Section to scrape (News, Press-Releases, etc.)

        Returns:
            List of article dictionaries
        """
        url = f"https://www.marines.mil/{section}/"
        return await self.scrape_page(url)

    async def scrape_multiple_sites(self, urls: List[str]) -> List[Dict]:
        """
        Scrape multiple sites in sequence.

        Args:
            urls: List of URLs to scrape

        Returns:
            Combined list of all articles
        """
        all_articles = []
        for url in urls:
            articles = await self.scrape_page(url)
            all_articles.extend(articles)
        return all_articles


async def scrape_js_sites() -> List[Dict]:
    """
    Convenience function to scrape all configured JS-rendered sites.

    Returns:
        List of all scraped articles
    """
    if not PLAYWRIGHT_AVAILABLE:
        logger.error("Playwright not available")
        return []

    sites = [
        "https://www.dvidshub.net/unit/USMC",
    ]

    async with PlaywrightScraper() as scraper:
        return await scraper.scrape_multiple_sites(sites)


def run_scraper() -> List[Dict]:
    """
    Synchronous wrapper for running the async scraper.

    Returns:
        List of scraped articles
    """
    return asyncio.run(scrape_js_sites())


if __name__ == "__main__":
    # Test the scraper
    print("Testing Playwright Scraper")
    print("=" * 60)

    if not PLAYWRIGHT_AVAILABLE:
        print("Playwright not installed. Run:")
        print("  pip install playwright")
        print("  playwright install chromium")
        sys.exit(1)

    async def test():
        async with PlaywrightScraper(headless=True) as scraper:
            # Test DVIDS
            print("\nScraping DVIDS Marines...")
            articles = await scraper.scrape_dvids()

            print(f"\nFound {len(articles)} articles:")
            for i, article in enumerate(articles[:5], 1):
                print(f"\n{i}. {article['title'][:60]}...")
                print(f"   URL: {article['url']}")
                if article.get('image'):
                    print(f"   Image: {article['image'][:60]}...")

    asyncio.run(test())
