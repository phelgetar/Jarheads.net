<?php
/**
 * Twenty Fourteen Child (Jarheads Marine News) — functions.php
 *
 * Loads the parent Twenty Fourteen stylesheet, then the child stylesheet.
 * WordPress automatically uses this theme's archive-marine_news.php and
 * single-marine_news.php for the marine_news custom post type, overriding the
 * parent theme without touching it.
 */

if (!defined('ABSPATH')) {
    exit; // No direct access.
}

add_action('wp_enqueue_scripts', 'jarheads_child_enqueue_styles');
function jarheads_child_enqueue_styles() {
    // Parent theme stylesheet.
    wp_enqueue_style(
        'twentyfourteen-parent-style',
        get_template_directory_uri() . '/style.css',
        array(),
        wp_get_theme(get_template())->get('Version')
    );

    // Child theme stylesheet (depends on the parent so it loads after).
    wp_enqueue_style(
        'twentyfourteen-child-style',
        get_stylesheet_uri(),
        array('twentyfourteen-parent-style'),
        wp_get_theme()->get('Version')
    );
}
