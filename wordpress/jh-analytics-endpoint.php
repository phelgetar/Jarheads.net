<?php
/**
 * Jarheads.net Analytics Tracking Endpoint
 * Receives and processes visitor tracking beacons
 * Version: 1.0.0
 * Created: January 17, 2026
 *
 * This file handles AJAX requests from the JavaScript tracking beacon,
 * processes user agent and IP data, performs geolocation, and stores
 * visitor information in the analytics database.
 *
 * Register in functions.php or plugin:
 * add_action('wp_ajax_jh_track_page', 'jh_handle_tracking');
 * add_action('wp_ajax_nopriv_jh_track_page', 'jh_handle_tracking');
 */

// Set timezone to Eastern Time
date_default_timezone_set('America/New_York');

// Prevent direct access
if (!defined('ABSPATH')) {
    // Try to load WordPress
    $wp_load_path = dirname(__FILE__) . '/../../../../wp-load.php';
    if (file_exists($wp_load_path)) {
        require_once($wp_load_path);
    } else {
        die('WordPress not found');
    }
}

/**
 * Main tracking handler function
 * Called via WordPress AJAX
 */
function jh_handle_tracking() {
    global $wpdb;

    // Verify nonce for security (comment out if causing issues during testing)
    // if (!isset($_POST['nonce']) || !wp_verify_nonce($_POST['nonce'], 'jh_analytics_track')) {
    //     wp_send_json_error(['message' => 'Invalid nonce']);
    //     return;
    // }

    // Collect and sanitize input data
    $session_id = isset($_POST['session_id']) ? sanitize_text_field($_POST['session_id']) : null;
    $post_id = isset($_POST['post_id']) ? intval($_POST['post_id']) : null;
    $post_type = isset($_POST['post_type']) ? sanitize_text_field($_POST['post_type']) : 'unknown';
    $page_url = isset($_POST['page_url']) ? esc_url_raw($_POST['page_url']) : '';
    $page_title = isset($_POST['page_title']) ? sanitize_text_field($_POST['page_title']) : '';
    $referrer_url = isset($_POST['referrer_url']) ? esc_url_raw($_POST['referrer_url']) : null;
    $search_terms = isset($_POST['search_terms']) ? sanitize_text_field($_POST['search_terms']) : null;
    $device_type = isset($_POST['device_type']) ? sanitize_text_field($_POST['device_type']) : 'unknown';
    $user_agent = isset($_POST['user_agent']) ? sanitize_text_field($_POST['user_agent']) : $_SERVER['HTTP_USER_AGENT'];

    // Validate required fields
    if (empty($session_id) || empty($page_url)) {
        wp_send_json_error(['message' => 'Missing required fields']);
        return;
    }

    // Get visitor IP address
    $ip_address = jh_get_client_ip();

    // Parse user agent for browser and OS
    $ua_info = jh_parse_user_agent($user_agent);

    // Get geographic location from IP
    $geo_info = jh_get_geolocation($ip_address);

    // Prepare data for insertion
    $page_view_data = [
        'visitor_session_id' => $session_id,
        'post_id' => $post_id,
        'post_type' => $post_type,
        'page_title' => $page_title,
        'page_url' => $page_url,
        'referrer_url' => $referrer_url,
        'search_terms' => $search_terms,
        'viewed_at' => current_time('mysql'),
        'user_agent' => substr($user_agent, 0, 500), // Truncate to prevent issues
        'device_type' => $device_type,
        'browser' => $ua_info['browser'],
        'os' => $ua_info['os'],
        'ip_address' => $ip_address,
        'country_code' => $geo_info['country_code'],
        'country_name' => $geo_info['country_name'],
        'region' => $geo_info['region'],
        'city' => $geo_info['city']
    ];

    // Insert page view record
    $inserted = $wpdb->insert(
        $wpdb->prefix . 'jh_page_views',
        $page_view_data,
        ['%s', '%d', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s']
    );

    if ($inserted === false) {
        wp_send_json_error(['message' => 'Database insert failed: ' . $wpdb->last_error]);
        return;
    }

    // Update or insert visitor session
    jh_update_visitor_session($session_id, $device_type, $ua_info, $geo_info, $ip_address);

    // Update referrer stats
    if (!empty($referrer_url)) {
        jh_update_referrer_stats($referrer_url, $search_terms);
    }

    // Return success
    wp_send_json_success(['message' => 'Page view tracked', 'session_id' => $session_id]);
}

/**
 * Get client IP address (handles proxies and load balancers)
 *
 * @return string IP address
 */
function jh_get_client_ip() {
    $ip_keys = [
        'HTTP_CF_CONNECTING_IP', // Cloudflare
        'HTTP_X_FORWARDED_FOR',  // Proxy
        'HTTP_X_REAL_IP',        // Nginx proxy
        'REMOTE_ADDR'            // Direct connection
    ];

    foreach ($ip_keys as $key) {
        if (!empty($_SERVER[$key])) {
            $ip_list = explode(',', $_SERVER[$key]);
            $ip = trim($ip_list[0]);

            if (filter_var($ip, FILTER_VALIDATE_IP)) {
                return $ip;
            }
        }
    }

    return '0.0.0.0'; // Fallback
}

/**
 * Parse user agent string to extract browser and OS
 *
 * @param string $ua User agent string
 * @return array ['browser' => string, 'os' => string]
 */
function jh_parse_user_agent($ua) {
    $browser = 'Unknown';
    $os = 'Unknown';

    // Detect browser
    if (preg_match('/Edg\//i', $ua)) {
        $browser = 'Edge';
    } elseif (preg_match('/Chrome\//i', $ua) && !preg_match('/Edg\//i', $ua)) {
        $browser = 'Chrome';
    } elseif (preg_match('/Safari\//i', $ua) && !preg_match('/Chrome\//i', $ua)) {
        $browser = 'Safari';
    } elseif (preg_match('/Firefox\//i', $ua)) {
        $browser = 'Firefox';
    } elseif (preg_match('/MSIE|Trident\//i', $ua)) {
        $browser = 'Internet Explorer';
    } elseif (preg_match('/Opera|OPR\//i', $ua)) {
        $browser = 'Opera';
    }

    // Detect OS
    if (preg_match('/Windows NT 10/i', $ua)) {
        $os = 'Windows 10';
    } elseif (preg_match('/Windows NT 11/i', $ua)) {
        $os = 'Windows 11';
    } elseif (preg_match('/Windows NT 6.3/i', $ua)) {
        $os = 'Windows 8.1';
    } elseif (preg_match('/Windows NT 6.2/i', $ua)) {
        $os = 'Windows 8';
    } elseif (preg_match('/Windows NT 6.1/i', $ua)) {
        $os = 'Windows 7';
    } elseif (preg_match('/Windows/i', $ua)) {
        $os = 'Windows';
    } elseif (preg_match('/Macintosh|Mac OS X/i', $ua)) {
        if (preg_match('/Mac OS X (10[._]\d+)/i', $ua, $matches)) {
            $os = 'macOS ' . str_replace('_', '.', $matches[1]);
        } else {
            $os = 'macOS';
        }
    } elseif (preg_match('/iPhone|iPad|iPod/i', $ua)) {
        if (preg_match('/OS (\d+[._]\d+)/i', $ua, $matches)) {
            $os = 'iOS ' . str_replace('_', '.', $matches[1]);
        } else {
            $os = 'iOS';
        }
    } elseif (preg_match('/Android/i', $ua)) {
        if (preg_match('/Android (\d+[._]\d+)/i', $ua, $matches)) {
            $os = 'Android ' . str_replace('_', '.', $matches[1]);
        } else {
            $os = 'Android';
        }
    } elseif (preg_match('/Linux/i', $ua)) {
        $os = 'Linux';
    }

    return [
        'browser' => substr($browser, 0, 50),
        'os' => substr($os, 0, 50)
    ];
}

/**
 * Get geographic location from IP address using IP-API.com
 * Results are cached for 24 hours
 *
 * @param string $ip IP address
 * @return array Geographic information
 */
function jh_get_geolocation($ip) {
    // Default values
    $default = [
        'country_code' => null,
        'country_name' => null,
        'region' => null,
        'city' => null
    ];

    // Skip geolocation for local/private IPs
    if (empty($ip) || $ip === '0.0.0.0' || filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE) === false) {
        return $default;
    }

    // Check cache first (WordPress transient)
    $cache_key = 'jh_geo_' . md5($ip);
    $cached = get_transient($cache_key);

    if ($cached !== false) {
        return $cached;
    }

    // Call IP-API.com (free tier: 45 requests/minute)
    $api_url = 'http://ip-api.com/json/' . $ip . '?fields=status,country,countryCode,region,regionName,city';
    $response = wp_remote_get($api_url, [
        'timeout' => 3,
        'user-agent' => 'Jarheads.net Analytics/1.0'
    ]);

    // Handle API errors gracefully
    if (is_wp_error($response)) {
        return $default;
    }

    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);

    if (empty($data) || $data['status'] !== 'success') {
        return $default;
    }

    // Extract geographic data
    $geo_data = [
        'country_code' => isset($data['countryCode']) ? substr($data['countryCode'], 0, 2) : null,
        'country_name' => isset($data['country']) ? substr($data['country'], 0, 100) : null,
        'region' => isset($data['regionName']) ? substr($data['regionName'], 0, 100) : null,
        'city' => isset($data['city']) ? substr($data['city'], 0, 100) : null
    ];

    // Cache for 24 hours
    set_transient($cache_key, $geo_data, 24 * HOUR_IN_SECONDS);

    return $geo_data;
}

/**
 * Update or insert visitor session record
 *
 * @param string $session_id Session UUID
 * @param string $device_type Device type
 * @param array $ua_info User agent info
 * @param array $geo_info Geographic info
 * @param string $ip_address IP address
 */
function jh_update_visitor_session($session_id, $device_type, $ua_info, $geo_info, $ip_address) {
    global $wpdb;

    $table = $wpdb->prefix . 'jh_visitor_sessions';

    // Check if session exists
    $existing = $wpdb->get_row($wpdb->prepare(
        "SELECT session_id, page_views_count FROM {$table} WHERE session_id = %s",
        $session_id
    ));

    if ($existing) {
        // Update existing session
        $wpdb->update(
            $table,
            [
                'last_seen' => current_time('mysql'),
                'page_views_count' => $existing->page_views_count + 1
            ],
            ['session_id' => $session_id],
            ['%s', '%d'],
            ['%s']
        );
    } else {
        // Insert new session
        $wpdb->insert(
            $table,
            [
                'session_id' => $session_id,
                'first_seen' => current_time('mysql'),
                'last_seen' => current_time('mysql'),
                'page_views_count' => 1,
                'device_type' => $device_type,
                'browser' => $ua_info['browser'],
                'os' => $ua_info['os'],
                'country_code' => $geo_info['country_code'],
                'country_name' => $geo_info['country_name'],
                'ip_hash' => hash('sha256', $ip_address . 'jh-salt-' . wp_salt())
            ],
            ['%s', '%s', '%s', '%d', '%s', '%s', '%s', '%s', '%s', '%s']
        );
    }
}

/**
 * Update referrer statistics
 *
 * @param string $referrer_url Full referrer URL
 * @param string|null $search_terms Search terms if applicable
 */
function jh_update_referrer_stats($referrer_url, $search_terms) {
    global $wpdb;

    $table = $wpdb->prefix . 'jh_referrer_stats';

    // Extract domain from referrer
    $parsed = parse_url($referrer_url);
    $domain = isset($parsed['host']) ? $parsed['host'] : 'direct';

    // Classify search engine
    $search_engine = 'direct';
    if (stripos($domain, 'google') !== false) {
        $search_engine = 'google';
    } elseif (stripos($domain, 'bing') !== false) {
        $search_engine = 'bing';
    } elseif (stripos($domain, 'yahoo') !== false) {
        $search_engine = 'yahoo';
    } elseif (stripos($domain, 'duckduckgo') !== false) {
        $search_engine = 'duckduckgo';
    } elseif (!empty($search_terms)) {
        $search_engine = 'other';
    }

    // Check if referrer exists
    $existing = $wpdb->get_row($wpdb->prepare(
        "SELECT id, visit_count FROM {$table}
         WHERE referrer_domain = %s AND search_engine = %s AND search_terms <=> %s",
        $domain,
        $search_engine,
        $search_terms
    ));

    if ($existing) {
        // Update count
        $wpdb->update(
            $table,
            [
                'visit_count' => $existing->visit_count + 1,
                'last_visit' => current_time('mysql')
            ],
            ['id' => $existing->id],
            ['%d', '%s'],
            ['%d']
        );
    } else {
        // Insert new referrer
        $wpdb->insert(
            $table,
            [
                'referrer_domain' => substr($domain, 0, 255),
                'referrer_url' => substr($referrer_url, 0, 512),
                'search_engine' => $search_engine,
                'search_terms' => $search_terms,
                'visit_count' => 1,
                'last_visit' => current_time('mysql')
            ],
            ['%s', '%s', '%s', '%s', '%d', '%s']
        );
    }
}

// Register AJAX handlers if not already registered
// (Add to functions.php or as plugin activation hook)
if (!has_action('wp_ajax_jh_track_page')) {
    add_action('wp_ajax_jh_track_page', 'jh_handle_tracking');
    add_action('wp_ajax_nopriv_jh_track_page', 'jh_handle_tracking');
}
