-- ============================================
-- Jarheads.net Analytics Database Schema
-- Installation Script for WordPress MySQL
-- ============================================
-- Created: January 17, 2026
-- Description: Creates 4 tables for visitor tracking, analytics, and referrer statistics
--
-- IMPORTANT: Replace 'wp_' prefix with your actual WordPress database prefix if different
-- Execute via phpMyAdmin, MySQL command line, or WP-CLI
-- ============================================

-- Table 1: Page Views - Stores individual page view events
-- ============================================
CREATE TABLE IF NOT EXISTS wp_jh_page_views (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

  -- Visitor identification
  visitor_session_id VARCHAR(64) NOT NULL COMMENT 'UUID from cookie for unique visitor tracking',

  -- Page information
  post_id BIGINT UNSIGNED NULL COMMENT 'WordPress post ID, NULL for archive/template pages',
  post_type VARCHAR(32) NULL DEFAULT 'marine_news' COMMENT 'Post type or page type',
  page_title VARCHAR(255) NULL COMMENT 'Page title for reference',
  page_url VARCHAR(512) NOT NULL COMMENT 'Full URL of the viewed page',

  -- Traffic source tracking
  referrer_url VARCHAR(512) NULL COMMENT 'HTTP referrer URL',
  search_terms VARCHAR(255) NULL COMMENT 'Extracted search terms from referrer',

  -- Timestamp
  viewed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'When the page was viewed',

  -- User agent information (parsed server-side)
  user_agent TEXT NULL COMMENT 'Full user agent string',
  device_type ENUM('mobile', 'tablet', 'desktop', 'bot', 'unknown') DEFAULT 'unknown' COMMENT 'Device type',
  browser VARCHAR(50) NULL COMMENT 'Browser name (Chrome, Firefox, Safari, etc.)',
  os VARCHAR(50) NULL COMMENT 'Operating system (Windows, macOS, iOS, Android, etc.)',

  -- Geographic information (from IP geolocation)
  ip_address VARCHAR(45) NULL COMMENT 'IPv4 or IPv6 address (anonymized after 30 days)',
  country_code VARCHAR(2) NULL COMMENT 'ISO 3166-1 alpha-2 country code',
  country_name VARCHAR(100) NULL COMMENT 'Full country name',
  region VARCHAR(100) NULL COMMENT 'State or region name',
  city VARCHAR(100) NULL COMMENT 'City name',

  PRIMARY KEY (id),
  INDEX idx_visitor_session (visitor_session_id),
  INDEX idx_post_id (post_id),
  INDEX idx_viewed_at (viewed_at),
  INDEX idx_device_type (device_type),
  INDEX idx_country (country_code),
  INDEX idx_composite_date_post (viewed_at, post_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Individual page view events with full visitor context';


-- Table 2: Visitor Sessions - Aggregates unique visitor sessions
-- ============================================
CREATE TABLE IF NOT EXISTS wp_jh_visitor_sessions (
  session_id VARCHAR(64) NOT NULL COMMENT 'Unique session identifier (UUID)',

  -- Session tracking
  first_seen DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'First page view in session',
  last_seen DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Most recent page view',
  page_views_count INT UNSIGNED DEFAULT 1 COMMENT 'Total page views in this session',

  -- Visitor characteristics (from first visit)
  device_type ENUM('mobile', 'tablet', 'desktop', 'bot', 'unknown') DEFAULT 'unknown',
  browser VARCHAR(50) NULL,
  os VARCHAR(50) NULL,
  country_code VARCHAR(2) NULL,
  country_name VARCHAR(100) NULL,

  -- Privacy-preserving identifier
  ip_hash VARCHAR(64) NULL COMMENT 'SHA-256 hash of IP for deduplication without storing raw IP',

  PRIMARY KEY (session_id),
  INDEX idx_first_seen (first_seen),
  INDEX idx_last_seen (last_seen),
  INDEX idx_country (country_code),
  INDEX idx_device (device_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Aggregated visitor sessions for unique visitor counting';


-- Table 3: Daily Stats - Pre-aggregated statistics for performance
-- ============================================
CREATE TABLE IF NOT EXISTS wp_jh_daily_stats (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

  -- Date and scope
  stat_date DATE NOT NULL COMMENT 'Date for these statistics',
  post_id BIGINT UNSIGNED NULL COMMENT 'Post ID for article-specific stats, NULL for site-wide',

  -- View statistics
  total_views INT UNSIGNED DEFAULT 0 COMMENT 'Total page views on this date',
  unique_visitors INT UNSIGNED DEFAULT 0 COMMENT 'Unique visitors on this date',

  -- Device breakdown
  mobile_views INT UNSIGNED DEFAULT 0,
  tablet_views INT UNSIGNED DEFAULT 0,
  desktop_views INT UNSIGNED DEFAULT 0,

  -- Top traffic sources
  top_country_code VARCHAR(2) NULL COMMENT 'Country with most visits',
  top_referrer VARCHAR(512) NULL COMMENT 'Most common referrer URL',

  -- Metadata
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (id),
  UNIQUE KEY unique_stat (stat_date, post_id) COMMENT 'One row per date per post',
  INDEX idx_stat_date (stat_date),
  INDEX idx_post_id (post_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Pre-aggregated daily statistics for fast dashboard queries';


-- Table 4: Referrer Stats - Tracks traffic sources
-- ============================================
CREATE TABLE IF NOT EXISTS wp_jh_referrer_stats (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

  -- Referrer information
  referrer_domain VARCHAR(255) NOT NULL COMMENT 'Domain of referring site',
  referrer_url VARCHAR(512) NULL COMMENT 'Full referrer URL (if tracked)',

  -- Search engine classification
  search_engine ENUM('google', 'bing', 'yahoo', 'duckduckgo', 'other', 'direct') DEFAULT 'direct',
  search_terms VARCHAR(255) NULL COMMENT 'Extracted search keywords',

  -- Visit tracking
  visit_count INT UNSIGNED DEFAULT 1 COMMENT 'Number of visits from this referrer',
  last_visit DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (id),
  INDEX idx_referrer_domain (referrer_domain),
  INDEX idx_search_engine (search_engine),
  INDEX idx_last_visit (last_visit),
  UNIQUE KEY unique_referrer (referrer_domain, search_engine, search_terms(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Aggregated referrer and search engine statistics';


-- ============================================
-- Initial Configuration & Sample Data
-- ============================================

-- Note: Tables are created with IF NOT EXISTS, safe to run multiple times
-- No sample data inserted - will be populated by tracking system

-- Verification Query (run after installation):
-- SHOW TABLES LIKE 'wp_jh_%';
-- Expected output: 4 tables (wp_jh_page_views, wp_jh_visitor_sessions, wp_jh_daily_stats, wp_jh_referrer_stats)

-- ============================================
-- Installation Complete
-- ============================================
-- Next steps:
-- 1. Upload jh-analytics-tracker.js and jh-analytics-endpoint.php
-- 2. Modify WordPress templates to include tracking code
-- 3. Test tracking by visiting a page and checking wp_jh_page_views table
-- 4. Setup daily cron job to run jh-analytics-cron.php
-- ============================================
