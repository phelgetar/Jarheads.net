# Marine Corps News Aggregator - Current Sources List

**Last Updated:** January 15, 2026

## 📰 RSS News Feeds (5 sources)

1. **USMC Official** - Official Marine Corps news and announcements
   - URL: `https://www.marines.mil/RSS/News-Feeds/All-News/`

2. **USMC Press Releases** - Official Marine Corps press releases
   - URL: `https://www.marines.mil/RSS/News-Feeds/Press-Releases/`

3. **Defense.gov** - Department of Defense news (filtered for Marines)
   - URL: `https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx?max=100&ContentType=1`

4. **Marine Corps Times** - Primary Marine Corps news publication
   - URL: `https://www.marinecorpstimes.com/arc/outboundfeeds/rss/`

5. **Stars and Stripes Marines** - Military newspaper Marine Corps section
   - URL: `https://www.stripes.com/RSS/marine_corps`

## 🎙️ Podcast Feeds (11 sources) - **NEW: 8 Added!**

### Official Marine Corps Association (2)
1. **Marine Corps Association Podcast** - Official MCA podcast
   - URL: `https://mca-marines.org/podcast/feed/`
   - Topics: Leadership, professional development

2. **MCA Scuttlebutt Podcast** ⭐ NEW
   - URL: `https://www.mca-marines.org/feed/mca-scuttlebutt/`
   - Topics: Current Marine Corps issues and community
   - Episodes: 276+

### Marine Corps History (1)
3. **History of the Marine Corps** ⭐ NEW
   - Host: Robert Estrada
   - URL: `https://rss.libsyn.com/shows/167873/destinations/1119545.xml`
   - Topics: Long-form Marine Corps history
   - Episodes: 163+

### Military/Veteran Podcasts (5)
4. **The Warfighter Podcast**
   - URL: `https://feeds.simplecast.com/vg3bH_Az`
   - Topics: Military strategy and leadership

5. **Jocko Podcast**
   - Host: Jocko Willink (Former Navy SEAL, frequently features Marines)
   - URL: `https://feeds.redcircle.com/64a89f88-a245-4098-8d8d-496325ec4f74`
   - Topics: Leadership, discipline, history, military operations
   - Episodes: 827+

6. **Zero Blog Thirty**
   - Host: Barstool Sports
   - URL: `https://mcsorleys.barstoolsports.com/feed/zero-blog-thirty`
   - Topics: Military culture, veteran life, humor
   - Episodes: 684+

7. **The Team House**
   - Hosts: Jack (SF/Ranger) & Dave (Ranger/Contractor)
   - URL: `https://www.spreaker.com/show/5960890/episodes/feed`
   - Topics: Special ops, intelligence community, military stories
   - Episodes: 542+

8. **The Smoke Pit** ⭐ NEW
   - Host: Daniel Sharp
   - URL: `https://feeds.acast.com/public/shows/5bddd6bc31355f1367f4a5dc`
   - Topics: Marine veteran discussions, comedy
   - Seasons: 6

### Navy/Marine Corps National Security (1)
9. **Midrats** ⭐ NEW
   - Hosts: CDR Salamander & EagleOne
   - URL: `https://www.spreaker.com/show/3270000/episodes/feed`
   - Topics: Navy and Marine Corps national security policy

### Marine Corps Acquisition (1)
10. **Equipping the Corps** ⭐ NEW
    - Host: Morgan Blackstock (MCSC Public Affairs)
    - URL: `https://anchor.fm/s/6aa53e5c/podcast/rss`
    - Topics: Marine Corps Systems Command, acquisition, innovation
    - Producer: Official USMC Systems Command

## 🏢 News Sites (6 sources)

1. **DVIDS Marines** - Defense Visual Information Distribution Service
   - URL: `https://www.dvidshub.net/unit/USMC`

2. **Marine Corps Base Camp Pendleton** - West Coast base news
   - URL: `https://www.pendleton.marines.mil/News/`

3. **Marine Corps Base Camp Lejeune** - East Coast base news
   - URL: `https://www.lejeune.marines.mil/News/`

4. **Marine Corps Air Station Miramar** - Aviation news
   - URL: `https://www.miramar.marines.mil/News/`

5. **Marine Corps Recruit Depot San Diego** - West Coast recruit training
   - URL: `https://www.mcrdsd.marines.mil/News/`

6. **Marine Corps Recruit Depot Parris Island** - East Coast recruit training
   - URL: `https://www.mcrdpi.marines.mil/News/`

## 📊 Total Sources

- **22 Total Sources** (5 RSS + 11 Podcasts + 6 News Sites)
- **8 New Podcast Sources Added Today**
- All sources actively crawled every 6 hours
- **2,800+ podcast episodes** available to search through

## 🔍 Content Filtering

The aggregator automatically filters content for Marine Corps relevance using these keywords:
- Marine Corps, USMC, Marines, Jarhead, Leatherneck
- Semper Fi, Semper Fidelis, Devil Dog
- Military equipment (HMMWV, MRAP, Amphibious)
- Units (MEU, Marine Expeditionary)
- Awards (Navy Cross, Purple Heart, MSM)
- Ranks and positions
- Equipment (F-35B, MV-22, CH-53, AAV)
- Specialties (Infantry, Artillery, Aviation, Logistics)

## 📝 Categories

Articles are automatically categorized into:
- **Awards** - Medals, honors, citations
- **Promotions** - Rank changes, leadership appointments
- **Equipment** - Vehicles, weapons, technology
- **Podcast** - Audio content and interviews
- **Operations** - Deployments, exercises, training ops
- **Training** - Boot camp, professional development
- **General** - All other Marine Corps news

## 🔄 Update Schedule

- **Automatic Crawl:** Every 6 hours (00:00, 06:00, 12:00, 18:00)
- **Data Retention:** 90 days
- **Incremental Updates:** Only new content since last run
- **Output:** JSON exported to `/public_html/data/marine_corps_news.json`

## 📍 Additional Sources Available (Commented Out)

### Suggested Bases to Add:
- Marine Corps Base Hawaii
- Marine Corps Base Quantico
- Marine Corps Air Station Beaufort
- Marine Corps Air Station Iwakuni
- Marine Corps Base Camp Butler (Okinawa)

### Suggested Podcasts to Add (Need RSS URLs):
- Cleared Hot (Andy Stumpf)
- Mike Drop (Mike Ritland)
- Veteran On The Move
- Defense News Weekly

## 🛠️ How to Add More Sources

See `/docs/ADDING_SOURCES.md` for detailed instructions on:
- Finding podcast RSS feeds
- Adding news sources
- Testing new sources
- Deploying changes to the server

## 📈 Performance Notes

- Each crawl processes ~100-500 articles depending on activity
- Deduplication prevents duplicate entries
- Politeness delays (1-2 seconds) between requests
- Incremental updates reduce server load
- Only Marine Corps-related content is saved

## 🌐 Web Integration

All collected articles are available at:
- **JSON API:** `https://jarheads.net/data/marine_corps_news.json`
- **Database:** Server-side SQLite at `~/Jarheads.net/data/marine_corps_news.db`

---

**Need to add a new source?** Edit `/src/aggregators/enhanced_aggregator.py` and follow the guide in `/docs/ADDING_SOURCES.md`
