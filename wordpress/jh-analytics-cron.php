<?php
/**
 * Jarheads.net Analytics Cron Job
 * Daily aggregation and maintenance tasks
 * Version: 1.0.0
 * Created: January 17, 2026
 *
 * This script should run daily (recommended: 2 AM) via system crontab:
 * 0 2 * * * /usr/bin/php /path/to/jh-analytics-cron.php >> /var/log/jh-analytics-cron.log 2>&1
 *
 * Tasks performed:
 * 1. Aggregate yesterday's page views into daily stats table
 * 2. Anonymize IP addresses older than 30 days
 * 3. Delete page view records older than 90 days (after aggregation)
 * 4. Update referrer statistics
 */

// Set timezone to Eastern Time
date_default_timezone_set('America/New_York');

// Load WordPress
require_once(dirname(__FILE__) . '/../../../wp-load.php');

global $wpdb;

// Start logging
$log_file = dirname(__FILE__) . '/jh-analytics-cron.log';
$start_time = microtime(true);

log_message("=== Jarheads.net Analytics Cron Job Started ===");
log_message("Start time: " . date('Y-m-d H:i:s'));

// ============================================
// TASK 1: Aggregate Daily Statistics
// ============================================

log_message("\n[Task 1] Aggregating daily statistics...");

try {
    $yesterday = date('Y-m-d', strtotime('-1 day'));
    $page_views_table = $wpdb->prefix . 'jh_page_views';
    $daily_stats_table = $wpdb->prefix . 'jh_daily_stats';

    // Aggregate site-wide stats for yesterday
    $site_wide = $wpdb->get_row($wpdb->prepare("
        SELECT
            COUNT(*) as total_views,
            COUNT(DISTINCT visitor_session_id) as unique_visitors,
            SUM(CASE WHEN device_type = 'mobile' THEN 1 ELSE 0 END) as mobile_views,
            SUM(CASE WHEN device_type = 'tablet' THEN 1 ELSE 0 END) as tablet_views,
            SUM(CASE WHEN device_type = 'desktop' THEN 1 ELSE 0 END) as desktop_views,
            (SELECT country_code FROM {$page_views_table} WHERE DATE(viewed_at) = %s AND country_code IS NOT NULL GROUP BY country_code ORDER BY COUNT(*) DESC LIMIT 1) as top_country,
            (SELECT referrer_url FROM {$page_views_table} WHERE DATE(viewed_at) = %s AND referrer_url IS NOT NULL GROUP BY referrer_url ORDER BY COUNT(*) DESC LIMIT 1) as top_referrer
        FROM {$page_views_table}
        WHERE DATE(viewed_at) = %s
    ", $yesterday, $yesterday, $yesterday));

    if ($site_wide && $site_wide->total_views > 0) {
        // Insert or update site-wide stats
        $wpdb->replace(
            $daily_stats_table,
            [
                'stat_date' => $yesterday,
                'post_id' => null,
                'total_views' => $site_wide->total_views,
                'unique_visitors' => $site_wide->unique_visitors,
                'mobile_views' => $site_wide->mobile_views,
                'tablet_views' => $site_wide->tablet_views,
                'desktop_views' => $site_wide->desktop_views,
                'top_country_code' => $site_wide->top_country,
                'top_referrer' => $site_wide->top_referrer
            ],
            ['%s', '%d', '%d', '%d', '%d', '%d', '%d', '%s', '%s']
        );

        log_message("Site-wide stats: {$site_wide->total_views} views, {$site_wide->unique_visitors} unique visitors");
    } else {
        log_message("No page views for {$yesterday}");
    }

    // Aggregate per-article stats for yesterday
    $articles = $wpdb->get_results($wpdb->prepare("
        SELECT
            post_id,
            COUNT(*) as total_views,
            COUNT(DISTINCT visitor_session_id) as unique_visitors,
            SUM(CASE WHEN device_type = 'mobile' THEN 1 ELSE 0 END) as mobile_views,
            SUM(CASE WHEN device_type = 'tablet' THEN 1 ELSE 0 END) as tablet_views,
            SUM(CASE WHEN device_type = 'desktop' THEN 1 ELSE 0 END) as desktop_views
        FROM {$page_views_table}
        WHERE DATE(viewed_at) = %s
          AND post_id IS NOT NULL
        GROUP BY post_id
    ", $yesterday));

    $article_count = 0;
    foreach ($articles as $article) {
        $wpdb->replace(
            $daily_stats_table,
            [
                'stat_date' => $yesterday,
                'post_id' => $article->post_id,
                'total_views' => $article->total_views,
                'unique_visitors' => $article->unique_visitors,
                'mobile_views' => $article->mobile_views,
                'tablet_views' => $article->tablet_views,
                'desktop_views' => $article->desktop_views
            ],
            ['%s', '%d', '%d', '%d', '%d', '%d', '%d']
        );
        $article_count++;
    }

    log_message("Aggregated stats for {$article_count} articles");

} catch (Exception $e) {
    log_message("ERROR in Task 1: " . $e->getMessage());
}

// ============================================
// TASK 2: Anonymize Old IP Addresses
// ============================================

log_message("\n[Task 2] Anonymizing IP addresses older than 30 days...");

try {
    $cutoff_date = date('Y-m-d', strtotime('-30 days'));

    // Anonymize IPv4 addresses (set last octet to 0)
    $result = $wpdb->query($wpdb->prepare("
        UPDATE {$page_views_table}
        SET ip_address = CONCAT(SUBSTRING_INDEX(ip_address, '.', 3), '.0')
        WHERE DATE(viewed_at) < %s
          AND ip_address IS NOT NULL
          AND ip_address NOT LIKE '%.0'
          AND ip_address LIKE '%.%.%.%'
    ", $cutoff_date));

    if ($result !== false) {
        log_message("Anonymized {$result} IPv4 addresses");
    } else {
        log_message("No IPv4 addresses to anonymize or query failed");
    }

    // Anonymize IPv6 addresses (set last segment to ::0)
    $result_ipv6 = $wpdb->query($wpdb->prepare("
        UPDATE {$page_views_table}
        SET ip_address = CONCAT(SUBSTRING_INDEX(ip_address, ':', 7), '::0')
        WHERE DATE(viewed_at) < %s
          AND ip_address IS NOT NULL
          AND ip_address NOT LIKE '%::0'
          AND ip_address LIKE '%:%'
    ", $cutoff_date));

    if ($result_ipv6 !== false && $result_ipv6 > 0) {
        log_message("Anonymized {$result_ipv6} IPv6 addresses");
    }

} catch (Exception $e) {
    log_message("ERROR in Task 2: " . $e->getMessage());
}

// ============================================
// TASK 3: Delete Old Page View Records
// ============================================

log_message("\n[Task 3] Deleting page view records older than 90 days...");

try {
    $delete_cutoff = date('Y-m-d', strtotime('-90 days'));

    $deleted = $wpdb->query($wpdb->prepare("
        DELETE FROM {$page_views_table}
        WHERE DATE(viewed_at) < %s
    ", $delete_cutoff));

    if ($deleted !== false) {
        log_message("Deleted {$deleted} old page view records");
    } else {
        log_message("No old records to delete or query failed");
    }

} catch (Exception $e) {
    log_message("ERROR in Task 3: " . $e->getMessage());
}

// ============================================
// TASK 4: Optimize Database Tables
// ============================================

log_message("\n[Task 4] Optimizing database tables...");

try {
    $tables = [
        $wpdb->prefix . 'jh_page_views',
        $wpdb->prefix . 'jh_visitor_sessions',
        $wpdb->prefix . 'jh_daily_stats',
        $wpdb->prefix . 'jh_referrer_stats'
    ];

    foreach ($tables as $table) {
        $wpdb->query("OPTIMIZE TABLE {$table}");
        log_message("Optimized table: {$table}");
    }

} catch (Exception $e) {
    log_message("ERROR in Task 4: " . $e->getMessage());
}

// ============================================
// Finish and Log Summary
// ============================================

$end_time = microtime(true);
$duration = round($end_time - $start_time, 2);

log_message("\n=== Cron Job Completed ===");
log_message("End time: " . date('Y-m-d H:i:s'));
log_message("Duration: {$duration} seconds");
log_message("====================================\n");

/**
 * Log message to file and console
 *
 * @param string $message Message to log
 */
function log_message($message) {
    global $log_file;

    $timestamp = date('Y-m-d H:i:s');
    $log_entry = "[{$timestamp}] {$message}\n";

    // Write to log file
    file_put_contents($log_file, $log_entry, FILE_APPEND);

    // Also output to console
    echo $log_entry;
}
