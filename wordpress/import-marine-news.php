<?php
/**
 * Marine Corps News Importer for WordPress
 *
 * This script imports articles from marine_corps_news.json into WordPress
 * as custom posts with individual comment sections.
 *
 * USAGE:
 * 1. Upload this file to your WordPress root directory
 * 2. Run once: https://yoursite.com/import-marine-news.php
 * 3. Delete this file after import for security
 *
 * Or run via WP-CLI:
 * wp eval-file import-marine-news.php
 */

// Load WordPress
require_once('wp-load.php');

// Security: Only allow admin users or CLI
if (!is_user_logged_in() || !current_user_can('manage_options')) {
    if (php_sapi_name() !== 'cli') {
        die('Unauthorized. You must be logged in as an administrator.');
    }
}

if (!function_exists('marine_news_set_featured_image')) {
    /**
     * Download an external image into the WordPress Media Library and set it as
     * the given post's featured thumbnail. No-op if the post already has a
     * thumbnail, so re-running the importer doesn't re-download or duplicate media.
     *
     * @param int    $post_id   Target post ID.
     * @param string $image_url Remote image URL (e.g. featured_image_url).
     * @param string $desc      Description / alt text for the attachment.
     */
    function marine_news_set_featured_image($post_id, $image_url, $desc = '') {
        if (empty($image_url) || has_post_thumbnail($post_id)
            || get_post_meta($post_id, '_featured_image_failed', true)) {
            return;
        }

        require_once ABSPATH . 'wp-admin/includes/media.php';
        require_once ABSPATH . 'wp-admin/includes/file.php';
        require_once ABSPATH . 'wp-admin/includes/image.php';

        $attachment_id = media_sideload_image($image_url, $post_id, $desc, 'id');

        if (is_wp_error($attachment_id)) {
            update_post_meta($post_id, '_featured_image_failed', time());
            error_log('Marine News: featured image sideload failed for post ' . $post_id . ' (' . $image_url . '): ' . $attachment_id->get_error_message());
            return;
        }

        set_post_thumbnail($post_id, $attachment_id);
    }
}

class MarineCorpsNewsImporter {

    private $json_file_path;
    private $imported_count = 0;
    private $updated_count = 0;
    private $skipped_count = 0;
    private $errors = array();

    public function __construct($json_file_path) {
        $this->json_file_path = $json_file_path;
    }

    /**
     * Main import function
     */
    public function import() {
        echo "<h1>Marine Corps News Importer</h1>\n";
        echo "<p>Starting import process...</p>\n";

        // Step 1: Register custom post type and taxonomy
        $this->register_custom_types();

        // Step 2: Load JSON data
        $articles = $this->load_json();
        if (empty($articles)) {
            echo "<p style='color: red;'>Error: No articles found in JSON file.</p>\n";
            return false;
        }

        echo "<p>Found " . count($articles) . " articles in JSON file.</p>\n";

        // Step 3: Import each article
        foreach ($articles as $article) {
            $this->import_article($article);
        }

        // Step 4: Display results
        $this->display_results();

        return true;
    }

    /**
     * Register custom post type and taxonomy
     */
    private function register_custom_types() {
        // Register Custom Post Type: marine_news
        register_post_type('marine_news', array(
            'labels' => array(
                'name' => 'Marine Corps News',
                'singular_name' => 'News Article',
                'add_new' => 'Add New Article',
                'add_new_item' => 'Add New Article',
                'edit_item' => 'Edit Article',
                'new_item' => 'New Article',
                'view_item' => 'View Article',
                'search_items' => 'Search Articles',
                'not_found' => 'No articles found',
                'not_found_in_trash' => 'No articles found in trash'
            ),
            'public' => true,
            'has_archive' => true,
            'show_in_rest' => true,
            'supports' => array('title', 'editor', 'excerpt', 'comments', 'custom-fields', 'thumbnail'),
            'rewrite' => array('slug' => 'marine-news'),
            'menu_icon' => 'dashicons-megaphone',
            'capability_type' => 'post',
        ));

        // Register Custom Taxonomy: news_category
        register_taxonomy('news_category', 'marine_news', array(
            'labels' => array(
                'name' => 'News Categories',
                'singular_name' => 'News Category',
                'search_items' => 'Search Categories',
                'all_items' => 'All Categories',
                'edit_item' => 'Edit Category',
                'update_item' => 'Update Category',
                'add_new_item' => 'Add New Category',
                'new_item_name' => 'New Category Name',
                'menu_name' => 'Categories',
            ),
            'hierarchical' => true,
            'show_ui' => true,
            'show_in_rest' => true,
            'rewrite' => array('slug' => 'news-category'),
        ));

        flush_rewrite_rules();
        echo "<p>✓ Custom post types and taxonomies registered.</p>\n";
    }

    /**
     * Load and parse JSON file
     */
    private function load_json() {
        if (!file_exists($this->json_file_path)) {
            $this->errors[] = "JSON file not found: {$this->json_file_path}";
            return array();
        }

        $json_content = file_get_contents($this->json_file_path);
        $data = json_decode($json_content, true);

        if (json_last_error() !== JSON_ERROR_NONE) {
            $this->errors[] = "JSON decode error: " . json_last_error_msg();
            return array();
        }

        // Handle different JSON structures
        if (isset($data['items'])) {
            return $data['items'];
        } elseif (isset($data['articles'])) {
            return $data['articles'];
        } elseif (isset($data['news_items'])) {
            return $data['news_items'];
        } else {
            return $data;
        }
    }

    /**
     * Import a single article
     */
    private function import_article($article) {
        // Validate required fields
        if (empty($article['title']) || empty($article['url'])) {
            $this->skipped_count++;
            return;
        }

        // Check if article already exists by URL
        $existing_post = $this->find_existing_post($article['url']);

        // Prepare post data
        $post_data = array(
            'post_type' => 'marine_news',
            'post_title' => sanitize_text_field($article['title']),
            'post_content' => $this->prepare_content($article),
            'post_excerpt' => !empty($article['description']) ? sanitize_text_field($article['description']) : (!empty($article['summary']) ? sanitize_text_field($article['summary']) : ''),
            'post_status' => 'publish',
            'post_date' => $this->parse_date($article),
            'comment_status' => 'open', // Enable comments
            'ping_status' => 'closed',
        );

        // Update or insert
        if ($existing_post) {
            $post_data['ID'] = $existing_post->ID;
            $post_id = wp_update_post($post_data, true);
            if (!is_wp_error($post_id)) {
                $this->updated_count++;
            }
        } else {
            $post_id = wp_insert_post($post_data, true);
            if (!is_wp_error($post_id)) {
                $this->imported_count++;
            }
        }

        // Handle errors
        if (is_wp_error($post_id)) {
            $this->errors[] = "Failed to import '{$article['title']}': " . $post_id->get_error_message();
            return;
        }

        // Add custom fields (metadata)
        update_post_meta($post_id, 'news_url', esc_url($article['url']));
        update_post_meta($post_id, 'news_source', sanitize_text_field($article['source'] ?? 'Unknown'));
        update_post_meta($post_id, 'news_author', sanitize_text_field($article['author'] ?? ''));
        update_post_meta($post_id, 'original_published_date', $article['published_date'] ?? $article['published'] ?? '');

        // Sideload the article's featured image and set it as the post thumbnail.
        if (!empty($article['featured_image_url'])) {
            marine_news_set_featured_image($post_id, $article['featured_image_url'], $article['title']);
        }

        // Add tags if present
        if (!empty($article['tags']) && is_array($article['tags'])) {
            wp_set_post_tags($post_id, $article['tags'], false);
        }

        // Set category
        $category = !empty($article['category']) ? $article['category'] : 'general';
        $term = term_exists($category, 'news_category');
        if (!$term) {
            $term = wp_insert_term($category, 'news_category');
        }
        if (!is_wp_error($term)) {
            wp_set_object_terms($post_id, (int)$term['term_id'], 'news_category');
        }
    }

    /**
     * Find existing post by URL
     */
    private function find_existing_post($url) {
        global $wpdb;
        $post_id = $wpdb->get_var($wpdb->prepare(
            "SELECT post_id FROM {$wpdb->postmeta} WHERE meta_key = 'news_url' AND meta_value = %s LIMIT 1",
            $url
        ));

        if ($post_id) {
            return get_post($post_id);
        }

        return null;
    }

    /**
     * Prepare post content from article data
     */
    private function prepare_content($article) {
        $content = '';

        // Add summary/description
        if (!empty($article['summary'])) {
            $content .= wpautop(sanitize_textarea_field($article['summary']));
        } elseif (!empty($article['description'])) {
            $content .= wpautop(sanitize_textarea_field($article['description']));
        }

        // Add link to original article
        if (!empty($article['url'])) {
            $content .= "<p><a href='" . esc_url($article['url']) . "' target='_blank' rel='noopener'>Read full article &rarr;</a></p>";
        }

        // Add metadata section
        $content .= "<hr>";
        $content .= "<p><small>";
        if (!empty($article['source'])) {
            $content .= "<strong>Source:</strong> " . esc_html($article['source']) . " | ";
        }
        if (!empty($article['author'])) {
            $content .= "<strong>Author:</strong> " . esc_html($article['author']) . " | ";
        }
        $content .= "<strong>Published:</strong> " . esc_html($article['published_date'] ?? $article['published'] ?? 'Unknown');
        $content .= "</small></p>";

        return wp_kses_post($content);
    }

    /**
     * Parse and format date
     */
    private function parse_date($article) {
        $date_string = $article['published_date'] ?? $article['published'] ?? $article['scraped_at'] ?? '';

        if (empty($date_string)) {
            return current_time('mysql');
        }

        // Try to parse various date formats
        $timestamp = strtotime($date_string);
        if ($timestamp === false) {
            return current_time('mysql');
        }

        return date('Y-m-d H:i:s', $timestamp);
    }

    /**
     * Display import results
     */
    private function display_results() {
        echo "<hr>\n";
        echo "<h2>Import Complete!</h2>\n";
        echo "<ul>\n";
        echo "<li><strong>Imported:</strong> {$this->imported_count} new articles</li>\n";
        echo "<li><strong>Updated:</strong> {$this->updated_count} existing articles</li>\n";
        echo "<li><strong>Skipped:</strong> {$this->skipped_count} articles</li>\n";
        echo "</ul>\n";

        if (!empty($this->errors)) {
            echo "<h3 style='color: red;'>Errors:</h3>\n";
            echo "<ul>\n";
            foreach ($this->errors as $error) {
                echo "<li>" . esc_html($error) . "</li>\n";
            }
            echo "</ul>\n";
        }

        echo "<p><a href='/wp-admin/edit.php?post_type=marine_news'>View Imported Articles in WordPress &rarr;</a></p>\n";
        echo "<p style='color: orange;'><strong>Security Notice:</strong> Please delete this import script file after use.</p>\n";
    }
}

// ========================================
// CONFIGURATION
// ========================================

// Path to your JSON file - adjust as needed
$json_file_path = __DIR__ . '/data/marine_corps_news.json';

// Alternative paths to try
$alternative_paths = array(
    __DIR__ . '/../data/marine_corps_news.json',
    ABSPATH . '../data/marine_corps_news.json',
    ABSPATH . 'data/marine_corps_news.json',
);

// Find the JSON file
if (!file_exists($json_file_path)) {
    foreach ($alternative_paths as $path) {
        if (file_exists($path)) {
            $json_file_path = $path;
            break;
        }
    }
}

// ========================================
// RUN IMPORTER
// ========================================

$importer = new MarineCorpsNewsImporter($json_file_path);
$importer->import();

echo "<p><em>Import process finished at " . date('Y-m-d H:i:s') . "</em></p>\n";
