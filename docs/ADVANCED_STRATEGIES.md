# Advanced Crawling Strategies for Marine Corps Content

This document provides detailed strategies and code snippets for expanding your Marine Corps news aggregator.

## 1. Social Media Monitoring

### Twitter/X Integration

```python
# Install: pip install tweepy
import tweepy

class TwitterMonitor:
    def __init__(self, api_key, api_secret, access_token, access_secret):
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_secret)
        self.api = tweepy.API(auth)
    
    def monitor_usmc_accounts(self):
        """Monitor official USMC Twitter accounts"""
        accounts = [
            'USMC',
            'MarinesMedia', 
            'MCRDParrisIsland',
            'MCRD_SD',
            'HQMC',
            '1stMarineDiv',
            '2ndMarineDiv',
            '3rdMarineDiv'
        ]
        
        items = []
        for account in accounts:
            tweets = self.api.user_timeline(screen_name=account, count=20)
            for tweet in tweets:
                items.append({
                    'title': tweet.text[:100],
                    'url': f'https://twitter.com/{account}/status/{tweet.id}',
                    'source': f'Twitter/@{account}',
                    'published_date': tweet.created_at.isoformat(),
                    'description': tweet.text,
                    'category': 'social_media'
                })
        return items
```

### Reddit Monitoring

```python
# Install: pip install praw
import praw

class RedditMonitor:
    def __init__(self, client_id, client_secret, user_agent):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
    
    def monitor_usmc_subreddits(self):
        """Monitor Marine Corps related subreddits"""
        subreddits = ['USMC', 'Military', 'Veterans', 'nationalguard']
        items = []
        
        for sub_name in subreddits:
            subreddit = self.reddit.subreddit(sub_name)
            
            # Search for Marine Corps content
            for submission in subreddit.search('Marine Corps OR USMC', 
                                              time_filter='week', 
                                              limit=25):
                items.append({
                    'title': submission.title,
                    'url': submission.url,
                    'source': f'Reddit r/{sub_name}',
                    'published_date': datetime.fromtimestamp(submission.created_utc).isoformat(),
                    'description': submission.selftext[:500] if submission.selftext else submission.title,
                    'category': 'social_media',
                    'upvotes': submission.score
                })
        
        return items
```

## 2. YouTube Monitoring

```python
# Install: pip install google-api-python-client
from googleapiclient.discovery import build

class YouTubeMonitor:
    def __init__(self, api_key):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def monitor_usmc_channels(self):
        """Monitor official USMC YouTube channels"""
        channels = {
            'Marines': 'UCURRx8NlDUBFGxmBISHGQVA',  # Example channel ID
            'Marine Corps Recruiting': 'UC8mrvKLLVPVF3O1K0MEKX5Q'
        }
        
        items = []
        for channel_name, channel_id in channels.items():
            request = self.youtube.search().list(
                part='snippet',
                channelId=channel_id,
                maxResults=10,
                order='date',
                type='video'
            )
            response = request.execute()
            
            for video in response['items']:
                snippet = video['snippet']
                video_id = video['id']['videoId']
                
                items.append({
                    'title': snippet['title'],
                    'url': f'https://www.youtube.com/watch?v={video_id}',
                    'source': f'YouTube/{channel_name}',
                    'published_date': snippet['publishedAt'],
                    'description': snippet['description'],
                    'category': 'video'
                })
        
        return items
```

## 3. Defense Contract Monitoring

```python
import requests
from datetime import datetime, timedelta

class ContractMonitor:
    """Monitor defense contract awards related to Marine Corps"""
    
    def search_sam_gov(self):
        """Search SAM.gov for Marine Corps contracts"""
        # SAM.gov API endpoint (requires API key)
        api_url = "https://api.sam.gov/opportunities/v2/search"
        
        params = {
            'postedFrom': (datetime.now() - timedelta(days=30)).strftime('%m/%d/%Y'),
            'keywords': 'Marine Corps',
            'limit': 100
        }
        
        # Note: Requires API key from sam.gov
        headers = {'X-Api-Key': 'your-api-key'}
        
        response = requests.get(api_url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return self.parse_contracts(data)
        
        return []
    
    def parse_contracts(self, data):
        """Parse contract data"""
        items = []
        for contract in data.get('opportunitiesData', []):
            items.append({
                'title': contract.get('title'),
                'url': contract.get('uiLink'),
                'source': 'SAM.gov',
                'published_date': contract.get('postedDate'),
                'description': contract.get('description', '')[:500],
                'category': 'contracts',
                'value': contract.get('award', {}).get('amount')
            })
        return items
```

## 4. FOIA Request Monitoring

```python
class FOIAMonitor:
    """Monitor FOIA requests and releases"""
    
    def monitor_foia_gov(self):
        """Check FOIA.gov for Marine Corps related requests"""
        # FOIA.gov API
        api_url = "https://api.foia.gov/api/requests"
        
        params = {
            'agency': 'USMC',
            'limit': 50
        }
        
        items = []
        response = requests.get(api_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            for request in data.get('results', []):
                items.append({
                    'title': request.get('title', 'FOIA Request'),
                    'url': request.get('url'),
                    'source': 'FOIA.gov',
                    'published_date': request.get('date_received'),
                    'description': request.get('description', ''),
                    'category': 'foia'
                })
        
        return items
```

## 5. Podcast Aggregation

```python
import feedparser

class PodcastAggregator:
    """Comprehensive podcast monitoring"""
    
    PODCAST_SOURCES = {
        # Military/Marine Corps specific podcasts
        'Marine Corps Association': 'https://mca-marines.org/podcast/feed/',
        'Zero Blog Thirty': 'https://feeds.megaphone.fm/zeroblogthirty',
        'Cleared Hot Podcast': 'https://feeds.simplecast.com/vg3bH_Az',
        'Team House Podcast': 'https://feeds.simplecast.com/Pp7oYFZH',
        'Danger Close Podcast': 'https://feeds.megaphone.fm/dangerclose',
        'The Warfighter Podcast': 'https://feeds.simplecast.com/vg3bH_Az',
        
        # Defense/Military general
        'Military Times Podcast': 'https://www.militarytimes.com/podcasts/rss/',
        'Defense One Radio': 'https://www.defenseone.com/podcasts/rss/',
        'War on the Rocks': 'https://warontherocks.com/category/podcasts/feed/',
    }
    
    def crawl_podcasts(self):
        """Crawl all podcast feeds"""
        items = []
        
        for podcast_name, feed_url in self.PODCAST_SOURCES.items():
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:5]:  # Latest 5 episodes
                # Check if Marine Corps related
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                
                if self.is_marine_corps_content(title, summary):
                    items.append({
                        'title': title,
                        'url': entry.get('link'),
                        'source': podcast_name,
                        'published_date': entry.get('published'),
                        'description': summary,
                        'category': 'podcast',
                        'duration': entry.get('itunes_duration', 'Unknown')
                    })
        
        return items
    
    def is_marine_corps_content(self, title, summary):
        """Check if episode mentions Marine Corps"""
        text = f"{title} {summary}".lower()
        keywords = ['marine', 'usmc', 'jarhead', 'leatherneck', 'semper fi']
        return any(keyword in text for keyword in keywords)
```

## 6. Think Tank & Research Monitoring

```python
class ThinkTankMonitor:
    """Monitor military think tanks and research institutions"""
    
    SOURCES = {
        'CSIS': 'https://www.csis.org/feeds/all.xml',
        'RAND': 'https://www.rand.org/news/rss.xml',
        'Marine Corps University Press': 'https://www.usmcu.edu/MCUPress/',
        'War on the Rocks': 'https://warontherocks.com/feed/',
        'Modern War Institute': 'https://mwi.usma.edu/feed/',
        'Center for a New American Security': 'https://www.cnas.org/rss.xml'
    }
    
    def crawl_research(self):
        """Crawl think tank publications"""
        items = []
        
        for source_name, feed_url in self.SOURCES.items():
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:10]:
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                
                # Filter for Marine Corps or amphibious warfare content
                if self.is_relevant_research(title, summary):
                    items.append({
                        'title': title,
                        'url': entry.get('link'),
                        'source': source_name,
                        'published_date': entry.get('published'),
                        'description': summary,
                        'category': 'research'
                    })
        
        return items
    
    def is_relevant_research(self, title, summary):
        """Check if research is relevant to Marine Corps"""
        text = f"{title} {summary}".lower()
        keywords = [
            'marine corps', 'usmc', 'amphibious', 'expeditionary',
            'naval infantry', 'littoral', 'marine expeditionary'
        ]
        return any(keyword in text for keyword in keywords)
```

## 7. Congressional Record Monitoring

```python
class CongressionalMonitor:
    """Monitor Congressional hearings and records"""
    
    def monitor_armed_services_committee(self):
        """Monitor House and Senate Armed Services Committees"""
        items = []
        
        # House Armed Services Committee
        hasc_rss = 'https://armedservices.house.gov/rss.xml'
        feed = feedparser.parse(hasc_rss)
        
        for entry in feed.entries:
            if 'marine' in entry.get('title', '').lower():
                items.append({
                    'title': entry.get('title'),
                    'url': entry.get('link'),
                    'source': 'House Armed Services Committee',
                    'published_date': entry.get('published'),
                    'description': entry.get('summary', ''),
                    'category': 'congressional'
                })
        
        return items
```

## 8. Job Posting Monitoring

```python
class JobMonitor:
    """Monitor USMC job postings"""
    
    def monitor_usajobs(self):
        """Monitor USAJOBS for Marine Corps positions"""
        # USAJOBS API
        api_url = "https://data.usajobs.gov/api/search"
        
        headers = {
            'Authorization-Key': 'your-api-key',
            'User-Agent': 'your-email@example.com'
        }
        
        params = {
            'Keyword': 'Marine Corps',
            'ResultsPerPage': 50
        }
        
        response = requests.get(api_url, headers=headers, params=params)
        
        items = []
        if response.status_code == 200:
            data = response.json()
            
            for job in data.get('SearchResult', {}).get('SearchResultItems', []):
                match = job.get('MatchedObjectDescriptor', {})
                items.append({
                    'title': match.get('PositionTitle'),
                    'url': match.get('PositionURI'),
                    'source': 'USAJOBS',
                    'published_date': match.get('PublicationStartDate'),
                    'description': match.get('UserArea', {}).get('Details', {}).get('JobSummary', ''),
                    'category': 'employment',
                    'location': match.get('PositionLocation', [{}])[0].get('LocationName')
                })
        
        return items
```

## 9. Press Release Aggregation

```python
class PressReleaseMonitor:
    """Monitor press releases from various sources"""
    
    PRESS_RELEASE_FEEDS = {
        'Department of Defense': 'https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx',
        'Marines.mil': 'https://www.marines.mil/RSS/News-Feeds/All-News/',
        'Secretary of the Navy': 'https://www.navy.mil/Press-Office/RSS-Feeds/',
        'Marine Corps Base Quantico': 'https://www.quantico.marines.mil/News/RSS/',
        'Marine Corps Base Camp Pendleton': 'https://www.pendleton.marines.mil/News/RSS/',
        'Marine Corps Air Station Miramar': 'https://www.miramar.marines.mil/News/RSS/',
    }
    
    def crawl_press_releases(self):
        """Crawl all press release feeds"""
        items = []
        
        for source, feed_url in self.PRESS_RELEASE_FEEDS.items():
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:15]:
                items.append({
                    'title': entry.get('title'),
                    'url': entry.get('link'),
                    'source': source,
                    'published_date': entry.get('published'),
                    'description': entry.get('summary', ''),
                    'category': 'press_release'
                })
        
        return items
```

## 10. Image and Video Recognition

```python
# For identifying equipment in images
# Install: pip install pillow transformers torch

from transformers import pipeline
from PIL import Image

class ImageAnalyzer:
    """Analyze images for Marine Corps equipment"""
    
    def __init__(self):
        self.classifier = pipeline("image-classification", 
                                   model="google/vit-base-patch16-224")
    
    def identify_equipment(self, image_url):
        """Identify military equipment in images"""
        try:
            image = Image.open(requests.get(image_url, stream=True).raw)
            results = self.classifier(image)
            
            # Filter for military equipment
            equipment_keywords = ['tank', 'vehicle', 'aircraft', 'helicopter', 'ship']
            relevant = [r for r in results if any(kw in r['label'].lower() for kw in equipment_keywords)]
            
            return relevant
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return []
```

## 11. Deployment Tracking

```python
class DeploymentTracker:
    """Track Marine Corps deployments and exercises"""
    
    def monitor_deployments(self):
        """Monitor deployment news from multiple sources"""
        items = []
        
        # DVIDS deployment news
        dvids_url = "https://www.dvidshub.net/rss/news/unit/usmc"
        feed = feedparser.parse(dvids_url)
        
        deployment_keywords = [
            'deploy', 'deployment', 'exercise', 'meu', 
            'expeditionary', 'rotation', 'forward deployed'
        ]
        
        for entry in feed.entries:
            title = entry.get('title', '').lower()
            if any(keyword in title for keyword in deployment_keywords):
                items.append({
                    'title': entry.get('title'),
                    'url': entry.get('link'),
                    'source': 'DVIDS',
                    'published_date': entry.get('published'),
                    'description': entry.get('summary', ''),
                    'category': 'deployment'
                })
        
        return items
```

## 12. Comprehensive Monitoring Strategy

Here's how to combine all these sources into your main aggregator:

```python
class ComprehensiveMarineCorpsAggregator(MarineCorpsAggregator):
    """Extended aggregator with all monitoring capabilities"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        # Initialize monitors
        if config.get('enable_twitter'):
            self.twitter = TwitterMonitor(
                config['twitter_api_key'],
                config['twitter_api_secret'],
                config['twitter_access_token'],
                config['twitter_access_secret']
            )
        
        if config.get('enable_reddit'):
            self.reddit = RedditMonitor(
                config['reddit_client_id'],
                config['reddit_client_secret'],
                config['reddit_user_agent']
            )
        
        if config.get('enable_youtube'):
            self.youtube = YouTubeMonitor(config['youtube_api_key'])
        
        # Add other monitors as needed
    
    def run_comprehensive_crawl(self):
        """Run all monitoring tasks"""
        all_items = []
        
        # Original sources
        all_items.extend(super().run_full_crawl())
        
        # Social media
        if hasattr(self, 'twitter'):
            all_items.extend(self.twitter.monitor_usmc_accounts())
        
        if hasattr(self, 'reddit'):
            all_items.extend(self.reddit.monitor_usmc_subreddits())
        
        if hasattr(self, 'youtube'):
            all_items.extend(self.youtube.monitor_usmc_channels())
        
        # Additional sources
        podcast_agg = PodcastAggregator()
        all_items.extend(podcast_agg.crawl_podcasts())
        
        think_tank = ThinkTankMonitor()
        all_items.extend(think_tank.crawl_research())
        
        press_release = PressReleaseMonitor()
        all_items.extend(press_release.crawl_press_releases())
        
        # Save all items
        for item in all_items:
            self.save_item(NewsItem(**item))
        
        return len(all_items)
```

## Best Practices

1. **Rate Limiting**: Always respect API rate limits
2. **Caching**: Cache responses to avoid redundant requests
3. **Error Handling**: Implement robust error handling
4. **Logging**: Log all activities for debugging
5. **Data Quality**: Validate and clean data before storage
6. **Privacy**: Respect privacy and terms of service
7. **Attribution**: Always attribute sources properly

## Performance Optimization

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def parallel_crawl(sources, crawl_function):
    """Crawl multiple sources in parallel"""
    results = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_source = {
            executor.submit(crawl_function, source): source 
            for source in sources
        }
        
        for future in as_completed(future_to_source):
            source = future_to_source[future]
            try:
                data = future.result()
                results.extend(data)
            except Exception as e:
                print(f"Error crawling {source}: {e}")
    
    return results
```

This comprehensive approach will give you maximum coverage of Marine Corps-related content across the internet!
