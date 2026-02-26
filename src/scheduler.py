#!/usr/bin/env python3
"""
Scheduled runner for Marine Corps news aggregator
Runs crawls at specified intervals and can post to jarheads.net
"""

import schedule
import time
import requests
import json
import os
import subprocess
import mimetypes
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.aggregators.enhanced_aggregator import EnhancedMarineCorpsAggregator
from src.utils.config_manager import config

# Get project root directory (one level up from this file)
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'


class JarheadsNetPoster:
    """
    Posts content to jarheads.net
    Customize this class based on your website's API/posting mechanism
    """
    
    def __init__(self, api_url: str, api_key: str = None):
        self.api_url = api_url
        self.api_key = api_key
        self.aggregator = EnhancedMarineCorpsAggregator()
    
    def format_post_content(self, items: list, include_images: bool = True) -> str:
        """Format items for posting to website with optional inline images"""
        content = f"# Marine Corps News Update - {datetime.now().strftime('%B %d, %Y')}\n\n"

        # Group by category
        by_category = {}
        for item in items:
            category = item['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(item)

        # Format each category
        category_names = {
            'awards': '🎖️ Awards and Honors',
            'promotions': '⭐ Promotions',
            'equipment': '🔧 Equipment and Hardware',
            'podcast': '🎙️ Podcasts',
            'operations': '⚔️ Operations and Training',
            'training': '🎓 Training and Education',
            'general': '📰 General News'
        }

        for category, category_items in sorted(by_category.items()):
            content += f"## {category_names.get(category, category.title())}\n\n"
            for item in category_items:
                content += f"**{item['title']}**\n"
                content += f"*Source: {item['source']}*\n"
                # Include featured image if available
                if include_images and item.get('featured_image_url'):
                    content += f"\n![{item['title']}]({item['featured_image_url']})\n\n"
                if item['description']:
                    content += f"{item['description']}\n"
                content += f"[Read more]({item['url']})\n\n"

        return content

    def format_single_post(self, item: dict) -> str:
        """Format a single item for individual posting with image"""
        content = ""

        # Include featured image at the top if available
        if item.get('featured_image_url'):
            content += f"![{item['title']}]({item['featured_image_url']})\n\n"

        if item.get('description'):
            content += f"{item['description']}\n\n"

        content += f"*Source: {item['source']}*\n\n"
        content += f"[Read the full article]({item['url']})"

        if item.get('tags'):
            content += f"\n\n**Tags:** {', '.join(item['tags'])}"

        return content
    
    def download_image(self, image_url: str) -> tuple:
        """
        Download an image from URL and return (content, filename, content_type)
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; MarineCorpsAggregator/2.0)'
            }
            response = requests.get(image_url, headers=headers, timeout=15, stream=True)
            response.raise_for_status()

            # Get content type
            content_type = response.headers.get('Content-Type', 'image/jpeg')

            # Extract filename from URL or generate one
            parsed_url = urlparse(image_url)
            filename = os.path.basename(parsed_url.path)
            if not filename or '.' not in filename:
                # Generate filename based on content type
                ext = mimetypes.guess_extension(content_type) or '.jpg'
                filename = f"marine_corps_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"

            return response.content, filename, content_type

        except Exception as e:
            print(f"Error downloading image from {image_url}: {e}")
            return None, None, None

    def upload_image_to_wordpress(self, image_url: str, alt_text: str = '') -> int:
        """
        Upload an image to WordPress media library and return the media ID
        Returns 0 if upload fails
        """
        if not self.api_url or not self.api_key:
            print("API credentials not configured for image upload")
            return 0

        # Download the image
        image_content, filename, content_type = self.download_image(image_url)
        if not image_content:
            return 0

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': content_type
            }

            response = requests.post(
                f'{self.api_url}/wp-json/wp/v2/media',
                headers=headers,
                data=image_content,
                timeout=60
            )

            if response.status_code == 201:
                media_data = response.json()
                media_id = media_data.get('id', 0)
                print(f"Successfully uploaded image: {filename} (ID: {media_id})")

                # Optionally set alt text
                if alt_text and media_id:
                    self.update_media_alt_text(media_id, alt_text)

                return media_id
            else:
                print(f"Failed to upload image: {response.status_code} - {response.text}")
                return 0

        except Exception as e:
            print(f"Error uploading image to WordPress: {e}")
            return 0

    def update_media_alt_text(self, media_id: int, alt_text: str) -> bool:
        """Update the alt text for a media item"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            response = requests.post(
                f'{self.api_url}/wp-json/wp/v2/media/{media_id}',
                headers=headers,
                json={'alt_text': alt_text},
                timeout=15
            )
            return response.status_code == 200
        except Exception:
            return False

    def post_to_wordpress(self, content: str, title: str, featured_image_url: str = None) -> bool:
        """
        Post to WordPress REST API with optional featured image
        """
        if not self.api_url or not self.api_key:
            print("API credentials not configured")
            return False

        try:
            # Upload featured image if provided
            featured_media_id = 0
            if featured_image_url:
                print(f"Uploading featured image: {featured_image_url}")
                featured_media_id = self.upload_image_to_wordpress(
                    featured_image_url,
                    alt_text=title  # Use post title as alt text
                )

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            data = {
                'title': title,
                'content': content,
                'status': 'publish',
                'categories': [1],  # Adjust category ID
                'tags': ['Marine Corps', 'USMC', 'Military News']
            }

            # Add featured image if upload succeeded
            if featured_media_id:
                data['featured_media'] = featured_media_id

            response = requests.post(
                f'{self.api_url}/wp-json/wp/v2/posts',
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 201:
                post_data = response.json()
                post_id = post_data.get('id', 'unknown')
                print(f"Successfully posted: {title} (ID: {post_id})")
                if featured_media_id:
                    print(f"  with featured image ID: {featured_media_id}")
                return True
            else:
                print(f"Failed to post: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"Error posting to website: {str(e)}")
            return False
    
    def post_via_email(self, content: str, subject: str) -> bool:
        """
        Alternative: Send content via email for manual posting
        """
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        # Load email settings from secure config
        if not config.has_email_credentials:
            print("Email credentials not configured. Set SENDER_EMAIL and SENDER_PASSWORD in .env")
            return False

        smtp_server = config.smtp_server
        smtp_port = config.smtp_port
        sender_email = config.sender_email
        receiver_email = config.receiver_email
        password = config.sender_password

        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(content, 'plain'))
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, password)
                server.send_message(msg)
            
            print(f"Email sent successfully: {subject}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

    def upload_to_wordpress(self):
        """Upload JSON file to WordPress server"""
        upload_script = PROJECT_ROOT / 'upload_to_wordpress.sh'

        if not upload_script.exists():
            print("Upload script not found, skipping WordPress upload")
            return False

        try:
            print("\nUploading to WordPress server...")
            result = subprocess.run(
                [str(upload_script)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print("✓ Upload successful! WordPress will auto-import new articles.")
                return True
            else:
                print(f"✗ Upload failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"Upload error: {e}")
            return False

    def post_individual_item(self, item: dict) -> bool:
        """Post a single news item with its own featured image"""
        content = self.format_single_post(item)
        title = item['title']
        featured_image = item.get('featured_image_url')

        return self.post_to_wordpress(content, title, featured_image)

    def check_and_post_new_items(self, post_individually: bool = False):
        """
        Check for new items and post them

        Args:
            post_individually: If True, post each article separately with its own
                             featured image. If False, post a combined roundup.
        """
        print(f"\n{'='*50}")
        print(f"Checking for new Marine Corps news - {datetime.now()}")
        print(f"{'='*50}")

        # Run crawl
        stats = self.aggregator.run_full_crawl()

        # Export to JSON to update dashboard
        print("\nExporting to JSON for dashboard...")
        self.aggregator.export_to_json()

        # Auto-upload to WordPress server
        self.upload_to_wordpress()

        if stats['new_items'] > 0:
            print(f"\nFound {stats['new_items']} new items!")

            # Get items from last 24 hours
            recent_items = self.aggregator.get_recent_items(days=1, limit=50)

            if recent_items:
                # Count items with images
                items_with_images = sum(1 for item in recent_items if item.get('featured_image_url'))
                print(f"Items with featured images: {items_with_images}/{len(recent_items)}")

                if post_individually:
                    # Post each item separately with its own featured image
                    print("\nPosting items individually...")
                    for item in recent_items:
                        # Uncomment to enable:
                        # self.post_individual_item(item)
                        pass
                else:
                    # Format combined content
                    content = self.format_post_content(recent_items, include_images=True)
                    title = f"Marine Corps News Roundup - {datetime.now().strftime('%B %d, %Y')}"

                    # Use first item's image as featured image for the roundup
                    featured_image = None
                    for item in recent_items:
                        if item.get('featured_image_url'):
                            featured_image = item['featured_image_url']
                            break

                    # Save to file for review
                    filename = DATA_DIR / f"news_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                    with open(filename, 'w') as f:
                        f.write(content)
                    print(f"Content saved to {filename}")

                    # Uncomment to enable automatic posting:
                    # self.post_to_wordpress(content, title, featured_image)
                    # OR
                    # self.post_via_email(content, title)
        else:
            print("No new items found.")


def run_scheduler():
    """Run the scheduled tasks"""
    # Initialize poster with credentials from secure config
    poster = JarheadsNetPoster(
        api_url=config.api_url,
        api_key=config.api_key  # Loaded from .env file
    )

    # Warn if API credentials are not configured
    if not config.has_api_credentials:
        print("WARNING: WordPress API key not configured. Set JARHEADS_API_KEY in .env")
        print("Posting to WordPress will be disabled.")
    
    # Schedule tasks
    # Run every 6 hours
    schedule.every(6).hours.do(poster.check_and_post_new_items)
    
    # Run daily at specific time
    schedule.every().day.at("06:00").do(poster.check_and_post_new_items)
    schedule.every().day.at("18:00").do(poster.check_and_post_new_items)
    
    # Run once immediately
    print("Running initial crawl...")
    poster.check_and_post_new_items()
    
    # Keep running
    print("\nScheduler started. Press Ctrl+C to stop.")
    print("Schedule:")
    print("  - Every 6 hours")
    print("  - Daily at 06:00 and 18:00")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    run_scheduler()
