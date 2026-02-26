#!/usr/bin/env python3
"""
Marine Corps News Summarizer
Generates comprehensive summaries of collected news stories
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict
import textwrap

# Get project root directory (two levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'data'


class NewsStorySummarizer:
    """Generate summaries of collected Marine Corps news"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(DATA_DIR / 'marine_corps_news.db')
        self.db_path = db_path
        
    def get_all_stories(self, days: int = None) -> List[Dict]:
        """Get all stories from database, optionally filtered by days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if days:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            query = '''
                SELECT title, url, source, published_date, description, 
                       category, scraped_at
                FROM news_items
                WHERE scraped_at > ?
                ORDER BY scraped_at DESC
            '''
            cursor.execute(query, (cutoff_date,))
        else:
            query = '''
                SELECT title, url, source, published_date, description, 
                       category, scraped_at
                FROM news_items
                ORDER BY scraped_at DESC
            '''
            cursor.execute(query)
        
        columns = ['title', 'url', 'source', 'published_date', 
                   'description', 'category', 'scraped_at']
        stories = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return stories
    
    def generate_executive_summary(self, days: int = 7) -> str:
        """Generate executive summary of recent news"""
        stories = self.get_all_stories(days=days)
        
        if not stories:
            return "No stories found in the specified time period."
        
        # Count by category
        by_category = defaultdict(list)
        by_source = defaultdict(int)
        
        for story in stories:
            by_category[story['category']].append(story)
            by_source[story['source']] += 1
        
        # Build summary
        summary = []
        summary.append("=" * 80)
        summary.append("MARINE CORPS NEWS EXECUTIVE SUMMARY")
        summary.append("=" * 80)
        summary.append(f"Period: Last {days} days")
        summary.append(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        summary.append(f"Total Stories: {len(stories)}")
        summary.append("")
        
        # Summary statistics
        summary.append("OVERVIEW")
        summary.append("-" * 80)
        summary.append(f"• Total stories collected: {len(stories)}")
        summary.append(f"• Unique sources: {len(by_source)}")
        summary.append(f"• Categories covered: {len(by_category)}")
        summary.append("")
        
        # Stories by category
        summary.append("BREAKDOWN BY CATEGORY")
        summary.append("-" * 80)
        category_names = {
            'awards': '🎖️  Awards and Honors',
            'promotions': '⭐ Promotions',
            'equipment': '🔧 Equipment and Hardware',
            'podcast': '🎙️  Podcasts',
            'operations': '⚔️  Operations and Training',
            'training': '🎓 Training and Education',
            'general': '📰 General News'
        }
        
        for category, count_stories in sorted(by_category.items(), 
                                               key=lambda x: len(x[1]), 
                                               reverse=True):
            cat_name = category_names.get(category, category.title())
            summary.append(f"{cat_name}: {len(count_stories)} stories")
        
        summary.append("")
        
        # Top sources
        summary.append("TOP SOURCES")
        summary.append("-" * 80)
        sorted_sources = sorted(by_source.items(), key=lambda x: x[1], reverse=True)
        for source, count in sorted_sources[:10]:
            summary.append(f"• {source}: {count} stories")
        
        summary.append("")
        summary.append("=" * 80)
        
        return "\n".join(summary)
    
    def generate_category_summaries(self, days: int = 7) -> str:
        """Generate detailed summaries by category"""
        stories = self.get_all_stories(days=days)
        
        if not stories:
            return "No stories found."
        
        by_category = defaultdict(list)
        for story in stories:
            by_category[story['category']].append(story)
        
        output = []
        output.append("=" * 80)
        output.append("DETAILED CATEGORY SUMMARIES")
        output.append("=" * 80)
        output.append("")
        
        category_info = {
            'awards': {
                'emoji': '🎖️',
                'title': 'Awards and Honors',
                'description': 'Medals, commendations, and unit citations'
            },
            'promotions': {
                'emoji': '⭐',
                'title': 'Promotions',
                'description': 'Officer and enlisted rank advancements'
            },
            'equipment': {
                'emoji': '🔧',
                'title': 'Equipment and Hardware',
                'description': 'New vehicles, weapons, and technology'
            },
            'podcast': {
                'emoji': '🎙️',
                'title': 'Podcasts and Interviews',
                'description': 'Audio content and discussions'
            },
            'operations': {
                'emoji': '⚔️',
                'title': 'Operations and Exercises',
                'description': 'Deployments, training exercises, and operations'
            },
            'training': {
                'emoji': '🎓',
                'title': 'Training and Education',
                'description': 'Boot camp, OCS, and professional development'
            },
            'general': {
                'emoji': '📰',
                'title': 'General News',
                'description': 'Other Marine Corps related news'
            }
        }
        
        for category, category_stories in sorted(by_category.items(), 
                                                  key=lambda x: len(x[1]), 
                                                  reverse=True):
            info = category_info.get(category, {
                'emoji': '📌',
                'title': category.title(),
                'description': ''
            })
            
            output.append(f"{info['emoji']} {info['title'].upper()}")
            output.append("=" * 80)
            if info['description']:
                output.append(f"{info['description']}")
                output.append("")
            output.append(f"Total stories: {len(category_stories)}")
            output.append("")
            
            # List all stories in this category
            for i, story in enumerate(category_stories[:20], 1):  # Limit to 20 per category
                output.append(f"{i}. {story['title']}")
                output.append(f"   Source: {story['source']}")
                if story['description']:
                    # Wrap description text
                    desc = story['description'][:200]
                    if len(story['description']) > 200:
                        desc += "..."
                    wrapped = textwrap.fill(desc, width=76, 
                                           initial_indent='   ',
                                           subsequent_indent='   ')
                    output.append(wrapped)
                output.append(f"   URL: {story['url']}")
                output.append("")
            
            if len(category_stories) > 20:
                output.append(f"   ... and {len(category_stories) - 20} more stories")
                output.append("")
            
            output.append("")
        
        return "\n".join(output)
    
    def generate_source_summaries(self, days: int = 7) -> str:
        """Generate summaries organized by source"""
        stories = self.get_all_stories(days=days)
        
        if not stories:
            return "No stories found."
        
        by_source = defaultdict(list)
        for story in stories:
            by_source[story['source']].append(story)
        
        output = []
        output.append("=" * 80)
        output.append("SUMMARIES BY SOURCE")
        output.append("=" * 80)
        output.append("")
        
        for source, source_stories in sorted(by_source.items(), 
                                             key=lambda x: len(x[1]), 
                                             reverse=True):
            output.append(f"SOURCE: {source}")
            output.append("-" * 80)
            output.append(f"Stories collected: {len(source_stories)}")
            output.append("")
            
            # Group by category for this source
            source_categories = defaultdict(int)
            for story in source_stories:
                source_categories[story['category']] += 1
            
            output.append("Categories:")
            for cat, count in sorted(source_categories.items(), 
                                    key=lambda x: x[1], 
                                    reverse=True):
                output.append(f"  • {cat}: {count}")
            output.append("")
            
            # List recent stories from this source
            output.append("Recent stories:")
            for i, story in enumerate(source_stories[:10], 1):
                output.append(f"{i}. [{story['category'].upper()}] {story['title']}")
                output.append(f"   {story['url']}")
            
            if len(source_stories) > 10:
                output.append(f"   ... and {len(source_stories) - 10} more")
            
            output.append("")
            output.append("")
        
        return "\n".join(output)
    
    def generate_timeline_summary(self, days: int = 30) -> str:
        """Generate chronological timeline of stories"""
        stories = self.get_all_stories(days=days)
        
        if not stories:
            return "No stories found."
        
        # Sort by date
        stories_by_date = defaultdict(list)
        for story in stories:
            date_str = story['scraped_at'][:10]  # Get YYYY-MM-DD
            stories_by_date[date_str].append(story)
        
        output = []
        output.append("=" * 80)
        output.append("CHRONOLOGICAL TIMELINE")
        output.append("=" * 80)
        output.append("")
        
        for date_str in sorted(stories_by_date.keys(), reverse=True):
            date_obj = datetime.fromisoformat(date_str)
            date_formatted = date_obj.strftime('%A, %B %d, %Y')
            day_stories = stories_by_date[date_str]
            
            output.append(f"📅 {date_formatted}")
            output.append("-" * 80)
            output.append(f"{len(day_stories)} stories collected")
            output.append("")
            
            # Group by category for the day
            by_category = defaultdict(list)
            for story in day_stories:
                by_category[story['category']].append(story)
            
            for category, cat_stories in sorted(by_category.items()):
                output.append(f"  {category.upper()} ({len(cat_stories)} stories):")
                for story in cat_stories[:5]:  # Show first 5 per category per day
                    output.append(f"    • {story['title']}")
                    output.append(f"      ({story['source']})")
                if len(cat_stories) > 5:
                    output.append(f"    ... and {len(cat_stories) - 5} more")
                output.append("")
            
            output.append("")
        
        return "\n".join(output)
    
    def generate_highlights(self, days: int = 7) -> str:
        """Generate highlights and notable stories"""
        stories = self.get_all_stories(days=days)
        
        if not stories:
            return "No stories found."
        
        output = []
        output.append("=" * 80)
        output.append("HIGHLIGHTS AND NOTABLE STORIES")
        output.append("=" * 80)
        output.append("")
        
        # Highlight awards
        awards = [s for s in stories if s['category'] == 'awards']
        if awards:
            output.append("🎖️  NOTABLE AWARDS AND HONORS")
            output.append("-" * 80)
            for story in awards[:5]:
                output.append(f"• {story['title']}")
                output.append(f"  Source: {story['source']}")
                if story['description']:
                    desc = story['description'][:150]
                    if len(story['description']) > 150:
                        desc += "..."
                    output.append(f"  {desc}")
                output.append(f"  {story['url']}")
                output.append("")
        
        # Highlight promotions
        promotions = [s for s in stories if s['category'] == 'promotions']
        if promotions:
            output.append("⭐ NOTABLE PROMOTIONS")
            output.append("-" * 80)
            for story in promotions[:5]:
                output.append(f"• {story['title']}")
                output.append(f"  Source: {story['source']}")
                output.append(f"  {story['url']}")
                output.append("")
        
        # Highlight equipment
        equipment = [s for s in stories if s['category'] == 'equipment']
        if equipment:
            output.append("🔧 NEW EQUIPMENT AND TECHNOLOGY")
            output.append("-" * 80)
            for story in equipment[:5]:
                output.append(f"• {story['title']}")
                output.append(f"  Source: {story['source']}")
                if story['description']:
                    desc = story['description'][:150]
                    if len(story['description']) > 150:
                        desc += "..."
                    output.append(f"  {desc}")
                output.append(f"  {story['url']}")
                output.append("")
        
        # Highlight operations
        operations = [s for s in stories if s['category'] == 'operations']
        if operations:
            output.append("⚔️  OPERATIONS AND EXERCISES")
            output.append("-" * 80)
            for story in operations[:5]:
                output.append(f"• {story['title']}")
                output.append(f"  Source: {story['source']}")
                if story['description']:
                    desc = story['description'][:150]
                    if len(story['description']) > 150:
                        desc += "..."
                    output.append(f"  {desc}")
                output.append(f"  {story['url']}")
                output.append("")
        
        return "\n".join(output)
    
    def generate_complete_summary(self, days: int = 7, 
                                  output_file: str = 'news_summary.txt') -> str:
        """Generate complete summary with all sections"""
        sections = []
        
        # Title page
        sections.append("=" * 80)
        sections.append("MARINE CORPS NEWS AGGREGATOR")
        sections.append("COMPREHENSIVE SUMMARY REPORT")
        sections.append("=" * 80)
        sections.append(f"Report Period: Last {days} days")
        sections.append(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        sections.append(f"For: jarheads.net")
        sections.append("=" * 80)
        sections.append("\n\n")
        
        # Executive summary
        sections.append(self.generate_executive_summary(days))
        sections.append("\n\n")
        
        # Highlights
        sections.append(self.generate_highlights(days))
        sections.append("\n\n")
        
        # Category summaries
        sections.append(self.generate_category_summaries(days))
        sections.append("\n\n")
        
        # Timeline
        sections.append(self.generate_timeline_summary(days))
        sections.append("\n\n")
        
        # Source summaries
        sections.append(self.generate_source_summaries(days))
        sections.append("\n\n")
        
        # Footer
        sections.append("=" * 80)
        sections.append("END OF REPORT")
        sections.append("Semper Fidelis")
        sections.append("=" * 80)
        
        full_summary = "\n".join(sections)
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_summary)
        
        print(f"Summary saved to: {output_file}")
        return full_summary
    
    def export_summary_json(self, days: int = 7,
                           output_file: str = None):
        if output_file is None:
            output_file = str(DATA_DIR / 'news_summary.json')
        """Export structured summary as JSON"""
        stories = self.get_all_stories(days=days)
        
        by_category = defaultdict(list)
        by_source = defaultdict(list)
        by_date = defaultdict(list)
        
        for story in stories:
            by_category[story['category']].append(story)
            by_source[story['source']].append(story)
            date_str = story['scraped_at'][:10]
            by_date[date_str].append(story)
        
        summary = {
            'generated_at': datetime.now().isoformat(),
            'period_days': days,
            'total_stories': len(stories),
            'total_sources': len(by_source),
            'total_categories': len(by_category),
            'statistics': {
                'by_category': {cat: len(items) for cat, items in by_category.items()},
                'by_source': {src: len(items) for src, items in by_source.items()},
                'by_date': {date: len(items) for date, items in by_date.items()}
            },
            'highlights': {
                'awards': [s for s in stories if s['category'] == 'awards'][:10],
                'promotions': [s for s in stories if s['category'] == 'promotions'][:10],
                'equipment': [s for s in stories if s['category'] == 'equipment'][:10],
                'operations': [s for s in stories if s['category'] == 'operations'][:10]
            },
            'all_stories': stories
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print(f"JSON summary saved to: {output_file}")
        return summary


def main():
    """Main execution function"""
    print("Marine Corps News Summarizer")
    print("=" * 80)
    print()
    
    summarizer = NewsStorySummarizer()
    
    # Check if database exists
    import os
    if not os.path.exists(summarizer.db_path):
        print(f"Error: Database '{summarizer.db_path}' not found.")
        print("Please run marine_corps_aggregator.py first to collect news.")
        return
    
    # Generate complete summary
    print("Generating comprehensive summary...")
    summarizer.generate_complete_summary(days=7, output_file='news_summary_7days.txt')
    
    print("\nGenerating 30-day summary...")
    summarizer.generate_complete_summary(days=30, output_file='news_summary_30days.txt')
    
    # Export JSON
    print("\nExporting JSON summaries...")
    summarizer.export_summary_json(days=7, output_file=str(DATA_DIR / 'news_summary_7days.json'))
    summarizer.export_summary_json(days=30, output_file=str(DATA_DIR / 'news_summary_30days.json'))

    print("\n" + "=" * 80)
    print("Summary generation complete!")
    print("\nFiles created:")
    print("  • data/news_summary_7days.txt  - Last 7 days text summary")
    print("  • data/news_summary_30days.txt - Last 30 days text summary")
    print("  • data/news_summary_7days.json - Last 7 days JSON data")
    print("  • data/news_summary_30days.json - Last 30 days JSON data")
    print("\nYou can now review these summaries or use them on jarheads.net!")


if __name__ == "__main__":
    main()
