#!/usr/bin/env python3
"""
PDF Document Processor for Marine Corps News Aggregator
Processes MARADMIN documents and other Marine Corps PDF publications
"""

import re
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logging_config import setup_logging
from src.utils.config_manager import config

logger = setup_logging("pdf_processor")


class MARADMINProcessor:
    """
    Process MARADMIN (Marine Administrative Message) documents.

    MARADMINs are official Marine Corps administrative messages that cover
    policies, programs, promotions, and other administrative matters.
    """

    # MARADMIN message sources
    MARADMIN_URLS = {
        'current': 'https://www.marines.mil/News/Messages/MARADMINS/',
        'archive': 'https://www.marines.mil/News/Messages/MARADMINS/Archive/',
    }

    # ALNAV (All Navy) messages that may affect Marines
    ALNAV_URL = 'https://www.marines.mil/News/Messages/ALNAVS/'

    def __init__(self, temp_dir: str = None):
        """
        Initialize the MARADMIN processor.

        Args:
            temp_dir: Directory for temporary PDF files
        """
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir()) / 'maradmin_pdfs'
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; MarineCorpsAggregator/2.0)'
        })
        logger.info(f"MARADMIN processor initialized. Temp dir: {self.temp_dir}")

    def fetch_maradmin_list(self, limit: int = 50) -> List[Dict]:
        """
        Fetch list of recent MARADMIN messages.

        Args:
            limit: Maximum number of messages to fetch

        Returns:
            List of message dictionaries with title, url, date
        """
        messages = []

        try:
            logger.info("Fetching MARADMIN list...")
            response = self.session.get(
                self.MARADMIN_URLS['current'],
                timeout=30
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find message links
            # Marines.mil uses various selectors for messages
            message_selectors = [
                'table.messages-table tr',
                '.dgov-list-item',
                'ul.messages-list li',
                '.message-item',
            ]

            for selector in message_selectors:
                items = soup.select(selector)
                if items:
                    for item in items[:limit]:
                        message = self._parse_message_item(item)
                        if message:
                            messages.append(message)
                    break

            # If no structured list found, look for links
            if not messages:
                links = soup.find_all('a', href=re.compile(r'MARADMIN|maradmin', re.I))
                for link in links[:limit]:
                    href = link.get('href', '')
                    title = link.get_text(strip=True)
                    if title and href:
                        messages.append({
                            'title': title,
                            'url': urljoin(self.MARADMIN_URLS['current'], href),
                            'date': None,
                            'number': self._extract_maradmin_number(title),
                        })

            logger.info(f"Found {len(messages)} MARADMIN messages")

        except Exception as e:
            logger.error(f"Error fetching MARADMIN list: {e}", exc_info=True)

        return messages

    def _parse_message_item(self, item) -> Optional[Dict]:
        """Parse a message item from the HTML"""
        try:
            link = item.find('a')
            if not link:
                return None

            title = link.get_text(strip=True)
            url = link.get('href', '')

            # Look for date
            date_text = None
            date_elem = item.find(['span', 'td'], class_=re.compile(r'date', re.I))
            if date_elem:
                date_text = date_elem.get_text(strip=True)

            return {
                'title': title,
                'url': urljoin(self.MARADMIN_URLS['current'], url),
                'date': date_text,
                'number': self._extract_maradmin_number(title),
            }
        except Exception:
            return None

    def _extract_maradmin_number(self, text: str) -> Optional[str]:
        """Extract MARADMIN number from text (e.g., 'MARADMIN 001/24')"""
        match = re.search(r'MARADMIN\s*(\d+/\d+)', text, re.I)
        if match:
            return match.group(1)
        return None

    def fetch_message_content(self, url: str) -> Optional[Dict]:
        """
        Fetch and parse the content of a MARADMIN message.

        Args:
            url: URL of the message page

        Returns:
            Dict with parsed message content
        """
        try:
            logger.info(f"Fetching message: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find message content
            content_selectors = [
                '.message-content',
                '.dgov-body',
                'article',
                '.content',
                'main',
            ]

            content = None
            for selector in content_selectors:
                elem = soup.select_one(selector)
                if elem:
                    content = elem.get_text(strip=True)
                    break

            if not content:
                # Fallback: get all text from body
                content = soup.body.get_text(strip=True) if soup.body else ''

            # Parse MARADMIN structure
            parsed = self._parse_maradmin_content(content)
            parsed['url'] = url
            parsed['raw_content'] = content[:5000]  # Store first 5000 chars

            return parsed

        except Exception as e:
            logger.error(f"Error fetching message content: {e}", exc_info=True)
            return None

    def _parse_maradmin_content(self, content: str) -> Dict:
        """
        Parse MARADMIN message content into structured data.

        MARADMIN format typically includes:
        - SUBJ: Subject line
        - REF: References
        - RMKS: Remarks (main content)
        - POC: Point of contact
        """
        parsed = {
            'subject': None,
            'references': [],
            'summary': None,
            'point_of_contact': None,
            'effective_date': None,
            'cancellation_date': None,
        }

        # Extract subject
        subj_match = re.search(r'SUBJ[:/]\s*(.+?)(?:\n|REF|RMKS|$)', content, re.I | re.S)
        if subj_match:
            parsed['subject'] = subj_match.group(1).strip()

        # Extract references
        ref_match = re.search(r'REF[:/]\s*(.+?)(?:\n\n|RMKS|$)', content, re.I | re.S)
        if ref_match:
            refs = ref_match.group(1).strip()
            parsed['references'] = [r.strip() for r in refs.split('\n') if r.strip()]

        # Extract remarks/summary (first paragraph)
        rmks_match = re.search(r'RMKS[:/]\s*1\.\s*(.+?)(?:\n\n|2\.|$)', content, re.I | re.S)
        if rmks_match:
            parsed['summary'] = rmks_match.group(1).strip()[:500]

        # Extract POC
        poc_match = re.search(r'POC[:/]\s*(.+?)(?:\n\n|$)', content, re.I | re.S)
        if poc_match:
            parsed['point_of_contact'] = poc_match.group(1).strip()

        # Extract effective date
        eff_match = re.search(r'EFFECTIVE\s*(?:DATE)?[:/]?\s*(\d{1,2}\s+\w+\s+\d{4}|\d+\s+\w+\s+\d{2})', content, re.I)
        if eff_match:
            parsed['effective_date'] = eff_match.group(1)

        return parsed

    def process_pdf_url(self, pdf_url: str) -> Optional[Dict]:
        """
        Download and process a PDF document.

        Note: This requires a PDF processing library or external service.
        Currently uses basic text extraction via the MarkItDown MCP if available.

        Args:
            pdf_url: URL of the PDF to process

        Returns:
            Dict with extracted content or None if processing fails
        """
        try:
            logger.info(f"Downloading PDF: {pdf_url}")
            response = self.session.get(pdf_url, timeout=60)
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' not in content_type.lower():
                logger.warning(f"URL does not appear to be a PDF: {content_type}")
                return None

            # Save to temp file
            filename = pdf_url.split('/')[-1] or 'document.pdf'
            filepath = self.temp_dir / filename
            filepath.write_bytes(response.content)

            logger.info(f"PDF saved to: {filepath}")

            # Note: Actual PDF text extraction would require additional libraries
            # like PyPDF2, pdfplumber, or calling the MarkItDown MCP server
            return {
                'filepath': str(filepath),
                'url': pdf_url,
                'size_bytes': len(response.content),
                'content': None,  # Placeholder for extracted text
            }

        except Exception as e:
            logger.error(f"Error processing PDF: {e}", exc_info=True)
            return None

    def get_recent_maradmins_as_news(self, limit: int = 20) -> List[Dict]:
        """
        Get recent MARADMINs formatted as news items.

        Args:
            limit: Maximum number of messages

        Returns:
            List of news item dictionaries compatible with NewsItem
        """
        news_items = []
        messages = self.fetch_maradmin_list(limit=limit)

        for message in messages:
            # Fetch full content
            content = self.fetch_message_content(message['url'])

            if content and content.get('subject'):
                title = content['subject']
                if message.get('number'):
                    title = f"MARADMIN {message['number']}: {title}"

                news_items.append({
                    'title': title,
                    'url': message['url'],
                    'source': 'MARADMIN',
                    'published_date': message.get('date') or datetime.now().isoformat(),
                    'description': content.get('summary', '')[:500],
                    'category': 'general',  # Could be categorized based on content
                    'tags': ['MARADMIN', 'official', 'policy'],
                    'author': content.get('point_of_contact'),
                    'featured_image_url': None,
                })

        logger.info(f"Processed {len(news_items)} MARADMINs as news items")
        return news_items

    def cleanup_temp_files(self, max_age_hours: int = 24):
        """
        Clean up old temporary PDF files.

        Args:
            max_age_hours: Delete files older than this
        """
        import time as time_module

        current_time = time_module.time()
        max_age_seconds = max_age_hours * 3600

        for filepath in self.temp_dir.glob('*.pdf'):
            file_age = current_time - filepath.stat().st_mtime
            if file_age > max_age_seconds:
                try:
                    filepath.unlink()
                    logger.debug(f"Deleted old temp file: {filepath}")
                except Exception as e:
                    logger.warning(f"Could not delete {filepath}: {e}")


# Singleton instance
_processor = None


def get_maradmin_processor() -> MARADMINProcessor:
    """Get or create the singleton MARADMIN processor instance"""
    global _processor
    if _processor is None:
        _processor = MARADMINProcessor()
    return _processor


if __name__ == "__main__":
    # Test the MARADMIN processor
    print("Testing MARADMIN Processor")
    print("=" * 60)

    processor = MARADMINProcessor()

    # Fetch recent messages
    print("\nFetching MARADMIN list...")
    messages = processor.fetch_maradmin_list(limit=5)

    print(f"\nFound {len(messages)} messages:")
    for msg in messages:
        print(f"  - {msg['title'][:60]}...")
        print(f"    URL: {msg['url']}")
        if msg.get('number'):
            print(f"    Number: {msg['number']}")
        print()

    # Try to fetch content for first message
    if messages:
        print("Fetching content for first message...")
        content = processor.fetch_message_content(messages[0]['url'])
        if content:
            print(f"\nSubject: {content.get('subject', 'N/A')}")
            print(f"Summary: {content.get('summary', 'N/A')[:200]}...")
            print(f"POC: {content.get('point_of_contact', 'N/A')}")

    # Get as news items
    print("\n" + "=" * 60)
    print("Getting MARADMINs as news items...")
    news = processor.get_recent_maradmins_as_news(limit=3)
    print(f"Generated {len(news)} news items")
