<?php
/**
 * Jarheads.net Admin Dashboard
 * Custom analytics dashboard with visitor tracking and comment management
 * Version: 1.0.0
 * Created: January 17, 2026
 *
 * URL: https://jarheads.net/wp-content/themes/twentyfourteen/admin-dashboard-8k3n9p2x.php
 * Security: Obscure URL only (no links in public templates)
 *
 * Features:
 * - Interactive analytics graphs with Chart.js
 * - Time range filtering (Day/Week/Month/Year/All Time)
 * - Recent comments management with delete capability
 * - Quick statistics and top articles
 * - Geographic and device breakdowns
 */

// Set timezone to Eastern Time
date_default_timezone_set('America/New_York');

// Load WordPress
require_once(dirname(__FILE__) . '/../../../wp-load.php');

// Optional: Require admin login (uncomment to enable)
// if (!current_user_can('manage_options')) {
//     wp_die('Unauthorized access. You must be logged in as an administrator.');
// }

global $wpdb;

// ============================================
// AJAX HANDLERS
// ============================================

if (isset($_GET['action'])) {
    header('Content-Type: application/json');

    switch ($_GET['action']) {
        case 'get_analytics':
            $range = isset($_GET['range']) ? sanitize_text_field($_GET['range']) : 'week';
            echo json_encode(get_analytics_data($range));
            exit;

        case 'delete_comment':
            $comment_id = isset($_GET['id']) ? intval($_GET['id']) : 0;
            if ($comment_id > 0) {
                $result = wp_delete_comment($comment_id, true); // Force delete
                echo json_encode(['success' => $result]);
            } else {
                echo json_encode(['success' => false, 'message' => 'Invalid comment ID']);
            }
            exit;

        default:
            echo json_encode(['error' => 'Unknown action']);
            exit;
    }
}

// ============================================
// DATA QUERY FUNCTIONS
// ============================================

/**
 * Get current time in EST timezone
 */
function get_current_est_datetime() {
    return date('Y-m-d H:i:s');
}

/**
 * Get current date in EST timezone
 */
function get_current_est_date() {
    return date('Y-m-d');
}

/**
 * Get analytics data for specified time range
 *
 * @param string $range Time range: 'day', 'week', 'month', 'year', 'all'
 * @return array Chart.js compatible data
 */
function get_analytics_data($range) {
    switch ($range) {
        case 'day':
            return get_hourly_stats_today();
        case 'week':
            return get_daily_stats_week();
        case 'month':
            return get_daily_stats_month();
        case 'year':
            return get_weekly_stats_year();
        case 'all':
            return get_monthly_stats_all();
        default:
            return get_daily_stats_week();
    }
}

/**
 * Get hourly statistics for today
 */
function get_hourly_stats_today() {
    global $wpdb;
    $table = $wpdb->prefix . 'jh_page_views';
    $today_start = get_current_est_date() . ' 00:00:00';

    $results = $wpdb->get_results($wpdb->prepare("
        SELECT
            DATE_FORMAT(CONVERT_TZ(viewed_at, '+00:00', '-05:00'), '%%H:00') as hour,
            DATE_FORMAT(CONVERT_TZ(viewed_at, '+00:00', '-05:00'), '%%H:00') as hour_label,
            COUNT(*) as total_views,
            COUNT(DISTINCT visitor_session_id) as unique_visitors
        FROM {$table}
        WHERE CONVERT_TZ(viewed_at, '+00:00', '-05:00') >= %s
        GROUP BY DATE_FORMAT(CONVERT_TZ(viewed_at, '+00:00', '-05:00'), '%%Y-%%m-%%d %%H:00:00')
        ORDER BY hour ASC
    ", $today_start));

    return format_for_chartjs($results, 'hour_label', 'hour');
}

/**
 * Get daily statistics for last 7 days
 */
function get_daily_stats_week() {
    global $wpdb;
    $table = $wpdb->prefix . 'jh_page_views';
    $seven_days_ago = date('Y-m-d H:i:s', strtotime('-7 days'));

    $results = $wpdb->get_results($wpdb->prepare("
        SELECT
            DATE_FORMAT(CONVERT_TZ(viewed_at, '+00:00', '-05:00'), '%%Y-%%m-%%d') as day,
            DATE_FORMAT(CONVERT_TZ(viewed_at, '+00:00', '-05:00'), '%%b %%d') as day_label,
            COUNT(*) as total_views,
            COUNT(DISTINCT visitor_session_id) as unique_visitors
        FROM {$table}
        WHERE CONVERT_TZ(viewed_at, '+00:00', '-05:00') >= %s
        GROUP BY DATE_FORMAT(CONVERT_TZ(viewed_at, '+00:00', '-05:00'), '%%Y-%%m-%%d')
        ORDER BY day ASC
    ", $seven_days_ago));

    return format_for_chartjs($results, 'day_label', 'day');
}

/**
 * Get daily statistics for last 30 days
 */
function get_daily_stats_month() {
    global $wpdb;
    $table = $wpdb->prefix . 'jh_page_views';
    $thirty_days_ago = date('Y-m-d H:i:s', strtotime('-30 days'));

    $results = $wpdb->get_results($wpdb->prepare("
        SELECT
            DATE_FORMAT(CONVERT_TZ(viewed_at, '+00:00', '-05:00'), '%%Y-%%m-%%d') as day,
            DATE_FORMAT(CONVERT_TZ(viewed_at, '+00:00', '-05:00'), '%%b %%d') as day_label,
            COUNT(*) as total_views,
            COUNT(DISTINCT visitor_session_id) as unique_visitors
        FROM {$table}
        WHERE CONVERT_TZ(viewed_at, '+00:00', '-05:00') >= %s
        GROUP BY DATE_FORMAT(CONVERT_TZ(viewed_at, '+00:00', '-05:00'), '%%Y-%%m-%%d')
        ORDER BY day ASC
    ", $thirty_days_ago));

    return format_for_chartjs($results, 'day_label', 'day');
}

/**
 * Get weekly statistics for last 12 months
 */
function get_weekly_stats_year() {
    global $wpdb;
    $table = $wpdb->prefix . 'jh_page_views';
    $twelve_months_ago = date('Y-m-d H:i:s', strtotime('-12 months'));

    $results = $wpdb->get_results($wpdb->prepare("
        SELECT
            DATE_FORMAT(CONVERT_TZ(viewed_at, '+00:00', '-05:00'), '%%Y-W%%u') as week,
            DATE_FORMAT(CONVERT_TZ(viewed_at, '+00:00', '-05:00'), '%%b %%d') as week_label,
            COUNT(*) as total_views,
            COUNT(DISTINCT visitor_session_id) as unique_visitors
        FROM {$table}
        WHERE CONVERT_TZ(viewed_at, '+00:00', '-05:00') >= %s
        GROUP BY YEARWEEK(CONVERT_TZ(viewed_at, '+00:00', '-05:00'))
        ORDER BY week ASC
    ", $twelve_months_ago));

    return format_for_chartjs($results, 'week_label', 'week');
}

/**
 * Get monthly statistics for all time
 */
function get_monthly_stats_all() {
    global $wpdb;
    $table = $wpdb->prefix . 'jh_page_views';

    $results = $wpdb->get_results("
        SELECT
            DATE_FORMAT(CONVERT_TZ(viewed_at, '+00:00', '-05:00'), '%%Y-%%m') as month,
            DATE_FORMAT(CONVERT_TZ(viewed_at, '+00:00', '-05:00'), '%%b %%Y') as month_label,
            COUNT(*) as total_views,
            COUNT(DISTINCT visitor_session_id) as unique_visitors
        FROM {$table}
        GROUP BY DATE_FORMAT(CONVERT_TZ(viewed_at, '+00:00', '-05:00'), '%%Y-%%m')
        ORDER BY month ASC
    ");

    return format_for_chartjs($results, 'month_label', 'month');
}

/**
 * Format database results for Chart.js
 *
 * @param array $results Database query results
 * @param string $label_key Key for display labels (hour_label, day_label, etc.)
 * @param string $sort_key Optional key for sorting (hour, day, week, month)
 * @return array Chart.js data format
 */
function format_for_chartjs($results, $label_key, $sort_key = null) {
    $labels = [];
    $views = [];
    $unique = [];

    // If we have a sort key, ensure data is properly ordered
    if ($sort_key !== null) {
        usort($results, function($a, $b) use ($sort_key) {
            return strcmp($a->{$sort_key}, $b->{$sort_key});
        });
    }

    foreach ($results as $row) {
        $labels[] = $row->{$label_key};
        $views[] = (int)$row->total_views;
        $unique[] = (int)$row->unique_visitors;
    }

    return [
        'labels' => $labels,
        'views' => $views,
        'unique' => $unique
    ];
}

/**
 * Get recent comments with article information
 *
 * @param int $limit Number of comments to retrieve
 * @return array Comment data
 */
function get_recent_comments($limit = 20) {
    global $wpdb;

    return $wpdb->get_results($wpdb->prepare("
        SELECT
            c.comment_ID,
            c.comment_author,
            c.comment_author_email,
            c.comment_date,
            c.comment_content,
            c.comment_post_ID,
            p.post_title,
            p.post_name
        FROM {$wpdb->comments} c
        INNER JOIN {$wpdb->posts} p ON c.comment_post_ID = p.ID
        WHERE p.post_type = 'marine_news'
          AND c.comment_approved = '1'
        ORDER BY c.comment_date DESC
        LIMIT %d
    ", $limit));
}

/**
 * Get top articles by views (last 30 days)
 *
 * @param int $limit Number of articles
 * @return array Article data with view counts
 */
function get_top_articles($limit = 10) {
    global $wpdb;
    $table = $wpdb->prefix . 'jh_page_views';

    return $wpdb->get_results($wpdb->prepare("
        SELECT
            p.ID,
            p.post_title,
            COUNT(*) as view_count,
            COUNT(DISTINCT pv.visitor_session_id) as unique_visitors
        FROM {$table} pv
        INNER JOIN {$wpdb->posts} p ON pv.post_id = p.ID
        WHERE pv.viewed_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
          AND p.post_type = 'marine_news'
        GROUP BY p.ID
        ORDER BY view_count DESC
        LIMIT %d
    ", $limit));
}

/**
 * Get geographic breakdown (last 24 hours)
 *
 * @param int $limit Number of countries
 * @return array Geographic statistics
 */
function get_geo_stats($limit = 10) {
    global $wpdb;
    $table = $wpdb->prefix . 'jh_page_views';

    return $wpdb->get_results($wpdb->prepare("
        SELECT
            country_name,
            country_code,
            COUNT(*) as visits,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM {$table} WHERE viewed_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)), 1) as percentage
        FROM {$table}
        WHERE viewed_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
          AND country_name IS NOT NULL
        GROUP BY country_name, country_code
        ORDER BY visits DESC
        LIMIT %d
    ", $limit));
}

/**
 * Get US state/region breakdown (last 24 hours)
 *
 * @param int $limit Number of states
 * @return array State statistics
 */
function get_state_stats($limit = 20) {
    global $wpdb;
    $table = $wpdb->prefix . 'jh_page_views';

    return $wpdb->get_results($wpdb->prepare("
        SELECT
            region,
            country_code,
            COUNT(*) as visits,
            COUNT(DISTINCT visitor_session_id) as unique_visitors,
            ROUND(COUNT(*) * 100.0 / (
                SELECT COUNT(*) FROM {$table}
                WHERE viewed_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
                  AND country_code = 'US'
                  AND region IS NOT NULL
                  AND region != ''
            ), 1) as percentage
        FROM {$table}
        WHERE viewed_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
          AND country_code = 'US'
          AND region IS NOT NULL
          AND region != ''
        GROUP BY region
        ORDER BY visits DESC
        LIMIT %d
    ", $limit));
}

/**
 * Get device type breakdown (last 24 hours)
 *
 * @return array Device statistics
 */
function get_device_stats() {
    global $wpdb;
    $table = $wpdb->prefix . 'jh_page_views';

    return $wpdb->get_results("
        SELECT
            device_type,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM {$table} WHERE viewed_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)), 1) as percentage
        FROM {$table}
        WHERE viewed_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        GROUP BY device_type
        ORDER BY count DESC
    ");
}

/**
 * Get quick statistics
 *
 * @return array Statistics data
 */
function get_quick_stats() {
    global $wpdb;

    $total_articles = wp_count_posts('marine_news')->publish;
    $total_comments = wp_count_comments()->approved;

    $table = $wpdb->prefix . 'jh_page_views';
    $total_visitors = $wpdb->get_var("
        SELECT COUNT(DISTINCT visitor_session_id)
        FROM {$table}
        WHERE viewed_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    ");

    $total_views_today = $wpdb->get_var("
        SELECT COUNT(*)
        FROM {$table}
        WHERE viewed_at >= CURDATE()
    ");

    return [
        'total_articles' => $total_articles,
        'total_comments' => $total_comments,
        'total_visitors' => $total_visitors ?: 0,
        'views_today' => $total_views_today ?: 0
    ];
}

// Fetch data for initial page load
$quick_stats = get_quick_stats();
$recent_comments = get_recent_comments(20);
$top_articles = get_top_articles(10);
$geo_stats = get_geo_stats(10);
$device_stats = get_device_stats();
$state_stats = get_state_stats(20);

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jarheads.net Admin Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        :root {
            --mc-red: #C41E3A;
            --mc-red-dark: #9A1830;
            --mc-red-light: #E84A5F;
            --text-dark: #1A1A1A;
            --text-gray: #666;
            --bg-light: #f8f9fa;
            --border-gray: #e0e0e0;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: var(--bg-light);
            color: var(--text-dark);
            line-height: 1.6;
        }

        .dashboard-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .dashboard-header {
            background: linear-gradient(135deg, var(--mc-red) 0%, var(--mc-red-dark) 100%);
            color: white;
            padding: 30px 40px;
            text-align: center;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(196, 30, 58, 0.3);
            margin-bottom: 30px;
        }

        .dashboard-header h1 {
            font-size: 2.2em;
            margin-bottom: 5px;
        }

        .dashboard-header p {
            opacity: 0.9;
            font-size: 1.1em;
        }

        .stats-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid var(--mc-red);
        }

        .stat-card .label {
            color: var(--text-gray);
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }

        .stat-card .value {
            font-size: 2.5em;
            font-weight: bold;
            color: var(--mc-red);
        }

        .section {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid var(--border-gray);
        }

        .section-header h2 {
            font-size: 1.5em;
            color: var(--mc-red);
        }

        .time-range-buttons {
            display: flex;
            gap: 10px;
        }

        .time-range-buttons button {
            padding: 10px 20px;
            background: white;
            border: 2px solid var(--mc-red);
            color: var(--mc-red);
            border-radius: 5px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }

        .time-range-buttons button:hover,
        .time-range-buttons button.active {
            background: var(--mc-red);
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 3px 8px rgba(196, 30, 58, 0.3);
        }

        .chart-container {
            position: relative;
            height: 400px;
            margin-bottom: 20px;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: var(--text-gray);
        }

        .comment-card {
            background: var(--bg-light);
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 15px;
            border-left: 3px solid var(--mc-red);
        }

        .comment-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 10px;
        }

        .comment-author {
            font-weight: bold;
            color: var(--text-dark);
        }

        .comment-time {
            color: var(--text-gray);
            font-size: 0.85em;
        }

        .comment-article {
            color: var(--mc-red);
            text-decoration: none;
            font-size: 0.95em;
        }

        .comment-article:hover {
            text-decoration: underline;
        }

        .comment-body {
            color: var(--text-gray);
            margin: 10px 0;
            line-height: 1.6;
        }

        .comment-actions {
            display: flex;
            gap: 15px;
            margin-top: 10px;
        }

        .comment-actions a,
        .comment-actions button {
            padding: 6px 14px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9em;
            text-decoration: none;
            transition: all 0.3s;
        }

        .comment-actions a {
            background: var(--mc-red);
            color: white;
        }

        .comment-actions a:hover {
            background: var(--mc-red-dark);
        }

        .comment-actions button {
            background: #dc3545;
            color: white;
        }

        .comment-actions button:hover {
            background: #c82333;
        }

        .top-articles-list {
            list-style: none;
        }

        .top-articles-list li {
            padding: 15px;
            border-bottom: 1px solid var(--border-gray);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .top-articles-list li:last-child {
            border-bottom: none;
        }

        .article-title {
            flex: 1;
            color: var(--text-dark);
            font-weight: 500;
        }

        .article-views {
            color: var(--mc-red);
            font-weight: bold;
            margin-left: 15px;
        }

        .geo-list {
            list-style: none;
        }

        .geo-list li {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid var(--border-gray);
        }

        .geo-list li:last-child {
            border-bottom: none;
        }

        .device-stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .device-stat {
            text-align: center;
            padding: 20px;
            background: var(--bg-light);
            border-radius: 6px;
        }

        .device-stat .icon {
            font-size: 2em;
            margin-bottom: 10px;
        }

        .device-stat .percentage {
            font-size: 2em;
            font-weight: bold;
            color: var(--mc-red);
        }

        .device-stat .label {
            color: var(--text-gray);
            text-transform: capitalize;
        }

        @media (max-width: 768px) {
            .dashboard-header {
                padding: 20px;
            }

            .dashboard-header h1 {
                font-size: 1.6em;
            }

            .time-range-buttons {
                flex-wrap: wrap;
            }

            .time-range-buttons button {
                font-size: 0.85em;
                padding: 8px 14px;
            }

            .chart-container {
                height: 300px;
            }

            .comment-header {
                flex-direction: column;
            }

            .stats-cards {
                grid-template-columns: 1fr;
            }
        }

        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            background: var(--mc-red);
            color: white;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <header class="dashboard-header">
            <h1>📊 Jarheads.net Admin Dashboard</h1>
            <p>Marine Corps Analytics & Comment Management</p>
        </header>

        <!-- Quick Statistics Cards -->
        <div class="stats-cards">
            <div class="stat-card">
                <div class="label">Total Articles</div>
                <div class="value"><?php echo number_format($quick_stats['total_articles']); ?></div>
            </div>
            <div class="stat-card">
                <div class="label">Total Comments</div>
                <div class="value"><?php echo number_format($quick_stats['total_comments']); ?></div>
            </div>
            <div class="stat-card">
                <div class="label">Visitors (30 Days)</div>
                <div class="value"><?php echo number_format($quick_stats['total_visitors']); ?></div>
            </div>
            <div class="stat-card">
                <div class="label">Views Today</div>
                <div class="value"><?php echo number_format($quick_stats['views_today']); ?></div>
            </div>
        </div>

        <!-- Analytics Graph Section -->
        <div class="section">
            <div class="section-header">
                <h2>📈 <span id="graph-title">Page Views Analytics</span></h2>
                <div style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <label for="graph-type" style="color: #666; font-weight: 600;">View:</label>
                        <select id="graph-type" onchange="changeGraphType()" style="padding: 8px 12px; border-radius: 6px; border: 2px solid #e0e0e0; background: white; font-size: 14px; cursor: pointer;">
                            <option value="combined">Total Views & Unique Visitors</option>
                            <option value="views">Total Page Views</option>
                            <option value="visitors">Unique Visitors (Site Visits)</option>
                        </select>
                    </div>
                    <div class="time-range-buttons">
                        <button onclick="loadAnalytics('day')" id="btn-day">Day</button>
                        <button onclick="loadAnalytics('week')" id="btn-week" class="active">Week</button>
                        <button onclick="loadAnalytics('month')" id="btn-month">Month</button>
                        <button onclick="loadAnalytics('year')" id="btn-year">Year</button>
                        <button onclick="loadAnalytics('all')" id="btn-all">All Time</button>
                    </div>
                </div>
            </div>
            <div class="chart-container">
                <canvas id="analyticsChart"></canvas>
            </div>
        </div>

        <!-- Recent Comments Section -->
        <div class="section">
            <div class="section-header">
                <h2>💬 Recent Comments</h2>
            </div>
            <div id="comments-container">
                <?php if (empty($recent_comments)) : ?>
                    <p style="text-align: center; color: var(--text-gray); padding: 40px;">No comments yet.</p>
                <?php else : ?>
                    <?php foreach ($recent_comments as $comment) : ?>
                        <div class="comment-card" id="comment-<?php echo $comment->comment_ID; ?>">
                            <div class="comment-header">
                                <div>
                                    <span class="comment-author"><?php echo esc_html($comment->comment_author); ?></span>
                                    <span class="comment-time"> • <?php echo human_time_diff(strtotime($comment->comment_date)); ?> ago</span>
                                    <br>
                                    <span>on </span>
                                    <a href="<?php echo get_permalink($comment->comment_post_ID); ?>" class="comment-article" target="_blank">
                                        <?php echo esc_html($comment->post_title); ?>
                                    </a>
                                </div>
                            </div>
                            <div class="comment-body">
                                <?php echo esc_html(wp_trim_words($comment->comment_content, 50)); ?>
                            </div>
                            <div class="comment-actions">
                                <a href="<?php echo get_permalink($comment->comment_post_ID); ?>#comment-<?php echo $comment->comment_ID; ?>" target="_blank">View Article</a>
                                <button onclick="deleteComment(<?php echo $comment->comment_ID; ?>)">Delete Comment</button>
                            </div>
                        </div>
                    <?php endforeach; ?>
                <?php endif; ?>
            </div>
        </div>

        <!-- Top Articles Section -->
        <div class="section">
            <div class="section-header">
                <h2>🏆 Top 10 Articles (Last 30 Days)</h2>
            </div>
            <?php if (empty($top_articles)) : ?>
                <p style="text-align: center; color: var(--text-gray); padding: 40px;">No article data yet. Start collecting analytics!</p>
            <?php else : ?>
                <ul class="top-articles-list">
                    <?php $rank = 1; foreach ($top_articles as $article) : ?>
                        <li>
                            <span class="article-rank"><?php echo $rank++; ?>.</span>
                            <span class="article-title"><?php echo esc_html($article->post_title); ?></span>
                            <span class="article-views"><?php echo number_format($article->view_count); ?> views</span>
                        </li>
                    <?php endforeach; ?>
                </ul>
            <?php endif; ?>
        </div>

        <!-- Geographic and Device Stats -->
        <div class="section">
            <div class="section-header">
                <h2>🌍 Visitor Activity (Last 24 Hours)</h2>
            </div>

            <h3 style="margin-bottom: 15px; color: var(--text-dark);">Geographic Breakdown</h3>
            <?php if (empty($geo_stats)) : ?>
                <p style="color: var(--text-gray);">No geographic data available yet.</p>
            <?php else : ?>
                <ul class="geo-list">
                    <?php foreach ($geo_stats as $geo) : ?>
                        <li>
                            <span><?php echo esc_html($geo->country_name); ?></span>
                            <span><strong><?php echo number_format($geo->visits); ?></strong> visits (<?php echo $geo->percentage; ?>%)</span>
                        </li>
                    <?php endforeach; ?>
                </ul>
            <?php endif; ?>

            <h3 style="margin: 30px 0 15px; color: var(--text-dark);">US State Breakdown</h3>
            <?php if (empty($state_stats)) : ?>
                <p style="color: var(--text-gray);">No US state data available yet.</p>
            <?php else : ?>
                <ul class="geo-list">
                    <?php foreach ($state_stats as $state) : ?>
                        <li>
                            <span><?php echo esc_html($state->region); ?></span>
                            <span>
                                <strong><?php echo number_format($state->visits); ?></strong> visits
                                (<?php echo number_format($state->unique_visitors); ?> unique)
                                &mdash; <?php echo $state->percentage; ?>%
                            </span>
                        </li>
                    <?php endforeach; ?>
                </ul>
            <?php endif; ?>

            <h3 style="margin: 30px 0 15px; color: var(--text-dark);">Device Type Breakdown</h3>
            <?php if (empty($device_stats)) : ?>
                <p style="color: var(--text-gray);">No device data available yet.</p>
            <?php else : ?>
                <div class="device-stats-grid">
                    <?php foreach ($device_stats as $device) : ?>
                        <?php if ($device->device_type !== 'unknown' && $device->device_type !== 'bot') : ?>
                            <div class="device-stat">
                                <div class="icon">
                                    <?php
                                    switch ($device->device_type) {
                                        case 'mobile': echo '📱'; break;
                                        case 'tablet': echo '📲'; break;
                                        case 'desktop': echo '💻'; break;
                                        default: echo '🖥️';
                                    }
                                    ?>
                                </div>
                                <div class="percentage"><?php echo $device->percentage; ?>%</div>
                                <div class="label"><?php echo ucfirst($device->device_type); ?></div>
                                <div style="color: var(--text-gray); font-size: 0.9em; margin-top: 5px;">
                                    <?php echo number_format($device->count); ?> visits
                                </div>
                            </div>
                        <?php endif; ?>
                    <?php endforeach; ?>
                </div>
            <?php endif; ?>
        </div>
    </div>

    <script>
        let chart = null;
        let currentRange = 'week';

        // Initialize chart on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadAnalytics('week');
        });

        /**
         * Load analytics data for specified time range
         */
        function loadAnalytics(range) {
            currentRange = range;

            // Update active button
            document.querySelectorAll('.time-range-buttons button').forEach(btn => {
                btn.classList.remove('active');
            });
            document.getElementById('btn-' + range).classList.add('active');

            // Show loading state
            const chartContainer = document.querySelector('.chart-container');
            chartContainer.innerHTML = '<div class="loading">Loading analytics...</div>';

            // Fetch data via AJAX
            fetch('?action=get_analytics&range=' + range)
                .then(response => response.json())
                .then(data => {
                    // Recreate canvas
                    chartContainer.innerHTML = '<canvas id="analyticsChart"></canvas>';

                    // Create chart
                    createChart(data);
                })
                .catch(error => {
                    console.error('Error loading analytics:', error);
                    chartContainer.innerHTML = '<div class="loading" style="color: var(--mc-red);">Error loading data. Please refresh the page.</div>';
                });
        }

        /**
         * Change graph type based on dropdown selection
         */
        function changeGraphType() {
            const graphType = document.getElementById('graph-type').value;
            const titleElement = document.getElementById('graph-title');

            // Update title based on selection
            switch(graphType) {
                case 'combined':
                    titleElement.textContent = 'Page Views Analytics';
                    break;
                case 'views':
                    titleElement.textContent = 'Total Page Views';
                    break;
                case 'visitors':
                    titleElement.textContent = 'Unique Visitors (Site Visits)';
                    break;
            }

            // Reload current range with new graph type
            loadAnalytics(currentRange);
        }

        /**
         * Create Chart.js line graph
         */
        function createChart(data) {
            const ctx = document.getElementById('analyticsChart').getContext('2d');
            const graphType = document.getElementById('graph-type').value;

            if (chart) {
                chart.destroy();
            }

            // Build datasets based on graph type selection
            let datasets = [];

            if (graphType === 'combined') {
                // Show both Total Views and Unique Visitors
                datasets = [
                    {
                        label: 'Total Views',
                        data: data.views,
                        borderColor: '#C41E3A',
                        backgroundColor: 'rgba(196, 30, 58, 0.1)',
                        tension: 0.4,
                        fill: true,
                        borderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Unique Visitors',
                        data: data.unique,
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.4,
                        fill: true,
                        borderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }
                ];
            } else if (graphType === 'views') {
                // Show only Total Page Views
                datasets = [
                    {
                        label: 'Total Page Views',
                        data: data.views,
                        borderColor: '#C41E3A',
                        backgroundColor: 'rgba(196, 30, 58, 0.15)',
                        tension: 0.4,
                        fill: true,
                        borderWidth: 3,
                        pointRadius: 5,
                        pointHoverRadius: 7
                    }
                ];
            } else if (graphType === 'visitors') {
                // Show only Unique Visitors (Site Visits)
                datasets = [
                    {
                        label: 'Unique Visitors (Site Visits)',
                        data: data.unique,
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.15)',
                        tension: 0.4,
                        fill: true,
                        borderWidth: 3,
                        pointRadius: 5,
                        pointHoverRadius: 7
                    }
                ];
            }

            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top',
                            labels: {
                                font: {
                                    size: 13,
                                    weight: 'bold'
                                },
                                padding: 15
                            }
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 12,
                            titleFont: {
                                size: 14,
                                weight: 'bold'
                            },
                            bodyFont: {
                                size: 13
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0,
                                font: {
                                    size: 12
                                }
                            },
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            }
                        },
                        x: {
                            ticks: {
                                maxRotation: window.innerWidth < 768 ? 45 : 0,
                                autoSkip: true,
                                maxTicksLimit: window.innerWidth < 768 ? 6 : 12,
                                font: {
                                    size: 12
                                }
                            },
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            }
                        }
                    },
                    interaction: {
                        mode: 'nearest',
                        axis: 'x',
                        intersect: false
                    }
                }
            });
        }

        /**
         * Delete comment with confirmation
         */
        function deleteComment(commentId) {
            if (!confirm('Are you sure you want to delete this comment? This action cannot be undone.')) {
                return;
            }

            fetch('?action=delete_comment&id=' + commentId)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const commentCard = document.getElementById('comment-' + commentId);
                        commentCard.style.transition = 'opacity 0.3s, transform 0.3s';
                        commentCard.style.opacity = '0';
                        commentCard.style.transform = 'translateX(-20px)';

                        setTimeout(() => {
                            commentCard.remove();
                        }, 300);

                        showNotification('Comment deleted successfully');
                    } else {
                        alert('Failed to delete comment: ' + (data.message || 'Unknown error'));
                    }
                })
                .catch(error => {
                    console.error('Error deleting comment:', error);
                    alert('Error deleting comment. Please try again.');
                });
        }

        /**
         * Show notification message
         */
        function showNotification(message) {
            const notification = document.createElement('div');
            notification.className = 'notification';
            notification.textContent = message;

            document.body.appendChild(notification);

            setTimeout(() => {
                notification.style.opacity = '0';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }
    </script>
</body>
</html>
