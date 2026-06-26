<?php
/**
 * Plugin Name: Marine Corps News
 * Description: Registers marine_news custom post type and taxonomy for jarheads.net
 * Version: 1.0
 * Author: Marine Corps News Team
 */

// Register Custom Post Type and Taxonomy on WordPress init
add_action('init', 'register_marine_news_post_type');

function register_marine_news_post_type() {
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
        'show_ui' => true,
        'show_in_menu' => true,
        'menu_position' => 5,
        'publicly_queryable' => true,
        'query_var' => true,
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
        'show_admin_column' => true,
        'query_var' => true,
        'rewrite' => array('slug' => 'news-category'),
        'public' => true,
    ));
}

// Flush rewrite rules on activation
register_activation_hook(__FILE__, 'marine_news_activation');
function marine_news_activation() {
    register_marine_news_post_type();
    flush_rewrite_rules();
}

// Flush rewrite rules on deactivation
register_deactivation_hook(__FILE__, 'marine_news_deactivation');
function marine_news_deactivation() {
    flush_rewrite_rules();
}

// Redirect homepage to Marine News archive
add_action('template_redirect', 'redirect_home_to_marine_news');
function redirect_home_to_marine_news() {
    if (is_home() || is_front_page()) {
        wp_redirect(get_post_type_archive_link('marine_news'), 301);
        exit;
    }
}

// Schedule automatic import from JSON
add_action('wp', 'schedule_marine_news_import');
function schedule_marine_news_import() {
    if (!wp_next_scheduled('marine_news_auto_import')) {
        wp_schedule_event(time(), 'hourly', 'marine_news_auto_import');
    }
}

// Auto-import function
add_action('marine_news_auto_import', 'auto_import_marine_news');
function auto_import_marine_news() {
    $json_file = ABSPATH . 'data/marine_corps_news.json';

    if (!file_exists($json_file)) {
        error_log('Marine News Auto-Import: JSON file not found');
        return;
    }

    $json_content = file_get_contents($json_file);
    $data = json_decode($json_content, true);

    if (json_last_error() !== JSON_ERROR_NONE) {
        error_log('Marine News Auto-Import: JSON decode error');
        return;
    }

    $articles = $data['items'] ?? $data['articles'] ?? $data['news_items'] ?? $data;

    if (empty($articles)) {
        error_log('Marine News Auto-Import: No articles found');
        return;
    }

    $imported = 0;
    $updated = 0;

    foreach ($articles as $article) {
        if (empty($article['title']) || empty($article['url'])) {
            continue;
        }

        // Check if article exists
        global $wpdb;
        $post_id = $wpdb->get_var($wpdb->prepare(
            "SELECT post_id FROM {$wpdb->postmeta} WHERE meta_key = 'news_url' AND meta_value = %s LIMIT 1",
            $article['url']
        ));

        $post_data = array(
            'post_type' => 'marine_news',
            'post_title' => sanitize_text_field($article['title']),
            'post_content' => wp_kses_post(prepare_article_content($article)),
            'post_excerpt' => sanitize_text_field($article['description'] ?? $article['summary'] ?? ''),
            'post_status' => 'publish',
            'post_date' => parse_article_date($article),
            'comment_status' => 'open',
            'ping_status' => 'closed',
        );

        if ($post_id) {
            $post_data['ID'] = $post_id;
            wp_update_post($post_data);
            $updated++;
        } else {
            $post_id = wp_insert_post($post_data);
            $imported++;
        }

        if (!is_wp_error($post_id)) {
            update_post_meta($post_id, 'news_url', esc_url($article['url']));
            update_post_meta($post_id, 'news_source', sanitize_text_field($article['source'] ?? 'Unknown'));
            update_post_meta($post_id, 'news_author', sanitize_text_field($article['author'] ?? ''));
            update_post_meta($post_id, 'original_published_date', $article['published_date'] ?? $article['published'] ?? '');

            // Sideload the article's featured image into the Media Library and
            // set it as the post thumbnail (skips if one is already attached).
            if (!empty($article['featured_image_url'])) {
                marine_news_set_featured_image($post_id, $article['featured_image_url'], $article['title']);
            }

            if (!empty($article['tags']) && is_array($article['tags'])) {
                wp_set_post_tags($post_id, $article['tags'], false);
            }

            $category = !empty($article['category']) ? $article['category'] : 'general';
            $term = term_exists($category, 'news_category');
            if (!$term) {
                $term = wp_insert_term($category, 'news_category');
            }
            if (!is_wp_error($term)) {
                wp_set_object_terms($post_id, (int)$term['term_id'], 'news_category');
            }
        }
    }

    error_log("Marine News Auto-Import: Imported {$imported}, Updated {$updated}");
}

function prepare_article_content($article) {
    $content = '';

    if (!empty($article['description'])) {
        $content .= wpautop(sanitize_textarea_field($article['description']));
    } elseif (!empty($article['summary'])) {
        $content .= wpautop(sanitize_textarea_field($article['summary']));
    }

    if (!empty($article['url'])) {
        $content .= "<p><a href='" . esc_url($article['url']) . "' target='_blank' rel='noopener'>Read full article &rarr;</a></p>";
    }

    $content .= "<hr><p><small>";
    if (!empty($article['source'])) {
        $content .= "<strong>Source:</strong> " . esc_html($article['source']) . " | ";
    }
    if (!empty($article['author'])) {
        $content .= "<strong>Author:</strong> " . esc_html($article['author']) . " | ";
    }
    $content .= "<strong>Published:</strong> " . esc_html($article['published_date'] ?? $article['published'] ?? 'Unknown');
    $content .= "</small></p>";

    return $content;
}

function parse_article_date($article) {
    $date_string = $article['published_date'] ?? $article['published'] ?? $article['scraped_at'] ?? '';

    if (empty($date_string)) {
        return current_time('mysql');
    }

    $timestamp = strtotime($date_string);
    if ($timestamp === false) {
        return current_time('mysql');
    }

    return date('Y-m-d H:i:s', $timestamp);
}

if (!function_exists('marine_news_set_featured_image')) {
    /**
     * Download an external image into the WordPress Media Library and set it as
     * the given post's featured thumbnail. No-op if the post already has a
     * thumbnail, so repeated cron imports don't re-download or duplicate media.
     *
     * @param int    $post_id   Target post ID.
     * @param string $image_url Remote image URL (e.g. featured_image_url).
     * @param string $desc      Description / alt text for the attachment.
     */
    function marine_news_set_featured_image($post_id, $image_url, $desc = '') {
        // Skip if there's no URL, a thumbnail already exists, or a prior attempt
        // failed. Some sources (e.g. media.defense.gov) block our server with a
        // 403, and without this the hourly cron would re-fetch known-bad URLs
        // on every run. Clear the '_featured_image_failed' meta to force a retry.
        if (empty($image_url) || has_post_thumbnail($post_id)
            || get_post_meta($post_id, '_featured_image_failed', true)) {
            return;
        }

        // media_sideload_image() and its dependencies live in wp-admin and are
        // not loaded on front-end / WP-Cron requests, so pull them in here.
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
