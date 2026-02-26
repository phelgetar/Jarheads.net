<?php
/**
 * Marine Corps News Auto-Poster for WordPress
 *
 * This script reads the marine_corps_news.json file and automatically
 * creates WordPress posts for new Marine Corps news items.
 *
 * Usage: Run via cron or manually
 *   php wordpress_auto_poster.php
 */

// WordPress configuration
define('WP_PATH', '/home1/jarheads/public_html');
define('JSON_FILE', '/home1/jarheads/public_html/marines/marine_corps_news.json');
define('LAST_RUN_FILE', '/home1/jarheads/logs/last_wp_post_id.txt');

// Load WordPress
require_once(WP_PATH . '/wp-load.php');

// Read JSON data
if (!file_exists(JSON_FILE)) {
    die("Error: JSON file not found at " . JSON_FILE . "\n");
}

$json_data = json_decode(file_get_contents(JSON_FILE), true);
$news_items = $json_data['items'] ?? [];

// Get last posted item (to avoid duplicates)
$last_posted_url = '';
if (file_exists(LAST_RUN_FILE)) {
    $last_posted_url = trim(file_get_contents(LAST_RUN_FILE));
}

$posted_count = 0;
$new_items = [];

// Process items (newest first)
foreach ($news_items as $item) {
    // Stop if we reach an item we've already posted
    if ($item['url'] === $last_posted_url) {
        break;
    }

    $new_items[] = $item;
}

// Reverse to post oldest-to-newest
$new_items = array_reverse($new_items);

foreach ($new_items as $item) {
    // Check if post already exists by URL (custom field)
    $existing = get_posts([
        'post_type' => 'post',
        'meta_key' => 'marine_corps_source_url',
        'meta_value' => $item['url'],
        'posts_per_page' => 1
    ]);

    if (!empty($existing)) {
        continue; // Skip if already posted
    }

    // Map categories
    $category_map = [
        'awards' => 'Marine Corps Awards',
        'promotions' => 'Marine Corps Promotions',
        'equipment' => 'Marine Corps Equipment',
        'podcast' => 'Marine Corps Podcasts',
        'operations' => 'Marine Corps Operations',
        'training' => 'Marine Corps Training',
        'general' => 'Marine Corps News'
    ];

    $category_name = $category_map[$item['category']] ?? 'Marine Corps News';

    // Get or create category
    $category_id = get_cat_ID($category_name);
    if ($category_id == 0) {
        $category_id = wp_create_category($category_name);
    }

    // Prepare post content
    $content = '<p>' . esc_html($item['description']) . '</p>';
    $content .= '<p><strong>Source:</strong> ' . esc_html($item['source']) . '</p>';

    if (!empty($item['author'])) {
        $content .= '<p><strong>Author:</strong> ' . esc_html($item['author']) . '</p>';
    }

    if (!empty($item['tags'])) {
        $tags_list = is_array($item['tags']) ? implode(', ', $item['tags']) : $item['tags'];
        $content .= '<p><strong>Tags:</strong> ' . esc_html($tags_list) . '</p>';
    }

    $content .= '<p><a href="' . esc_url($item['url']) . '" target="_blank" rel="noopener">Read full article →</a></p>';

    // Create post
    $post_data = [
        'post_title'    => wp_strip_all_tags($item['title']),
        'post_content'  => $content,
        'post_status'   => 'publish',
        'post_category' => [$category_id],
        'post_date'     => date('Y-m-d H:i:s', strtotime($item['published_date'] ?? $item['scraped_at'])),
        'meta_input'    => [
            'marine_corps_source_url' => $item['url'],
            'marine_corps_source' => $item['source'],
            'marine_corps_category' => $item['category']
        ]
    ];

    // Insert post
    $post_id = wp_insert_post($post_data);

    if ($post_id && !is_wp_error($post_id)) {
        $posted_count++;
        echo "Posted: {$item['title']} (ID: $post_id)\n";

        // Update last posted URL
        file_put_contents(LAST_RUN_FILE, $item['url']);
    }
}

echo "\n";
echo "========================================\n";
echo "Auto-posting complete\n";
echo "New posts created: $posted_count\n";
echo "========================================\n";
