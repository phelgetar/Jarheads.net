<?php
/**
 * Template Name: Marine Corps News
 * Description: Custom template for displaying Marine Corps news aggregator content
 *
 * Place this file in your WordPress theme directory:
 * wp-content/themes/YOUR-THEME-NAME/template-marine-corps-news.php
 */

// Remove theme styling (optional - comment out if you want to keep some theme elements)
// remove_all_actions('wp_head');
// remove_all_actions('wp_footer');

// Re-add essential WordPress hooks if removed above
// add_action('wp_head', 'wp_enqueue_scripts', 1);
// add_action('wp_head', 'wp_print_styles', 8);
// add_action('wp_head', 'wp_print_head_scripts', 9);

get_header(); // Remove this line if you want completely independent styling
?>

<div class="marine-corps-news-container">
    <style>
        /* Inline styles - move to separate CSS file for production */
        /* Twenty Fourteen caps #page at 1260px, which would clamp the grid.
           Lift it (and drop the sidebar) on this template only. */
        #page { max-width: min(2200px, 96vw) !important; }
        #secondary { display: none !important; }
        #primary { width: 100% !important; float: none !important; margin: 0 !important; }
        .site-content { margin: 0 !important; width: 100% !important; }

        .marine-corps-news-container {
            /* Fluid up to ultrawide: use the viewport but keep a margin and a
               sane upper bound so cards never stretch absurdly wide. */
            max-width: min(2200px, 95vw);
            margin: 0 auto;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
        }

        .news-header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #C41E3A; /* Marine Corps red */
        }

        .news-header h1 {
            color: #1A1A1A;
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .news-filters {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            justify-content: center;
        }

        .filter-btn {
            padding: 10px 20px;
            background: #f4f4f4;
            border: 2px solid #ddd;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .filter-btn:hover, .filter-btn.active {
            background: #C41E3A;
            color: white;
            border-color: #C41E3A;
        }

        .news-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }

        .news-article {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .news-article:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }

        .article-category {
            display: inline-block;
            padding: 5px 12px;
            background: #C41E3A;
            color: white;
            font-size: 0.75em;
            text-transform: uppercase;
            border-radius: 3px;
            margin-bottom: 10px;
            font-weight: bold;
        }

        .article-category.podcast {
            background: #9C27B0; /* Purple for podcasts */
        }

        .article-category.podcast::before {
            content: '🎙️ ';
        }

        .news-article.podcast-article {
            border-left: 4px solid #9C27B0;
        }

        .article-title {
            font-size: 1.3em;
            margin: 10px 0;
            color: #1A1A1A;
        }

        .article-title a {
            color: inherit;
            text-decoration: none;
        }

        .article-title a:hover {
            color: #C41E3A;
        }

        .article-meta {
            font-size: 0.85em;
            color: #666;
            margin: 10px 0;
        }

        .article-excerpt {
            color: #444;
            line-height: 1.6;
            margin: 15px 0;
        }

        .article-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e0e0e0;
        }

        .read-more {
            display: inline-block;
            padding: 8px 16px;
            background: #C41E3A;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.9em;
            transition: background 0.3s;
        }

        .read-more:hover {
            background: #9A1830;
        }

        .comment-count {
            color: #666;
            font-size: 0.9em;
        }

        .no-results {
            text-align: center;
            padding: 60px 20px;
            color: #666;
            font-size: 1.2em;
        }

        /* Mobile Responsive Styles */
        @media (max-width: 768px) {
            .news-grid {
                grid-template-columns: 1fr;
            }

            .search-podcast-section {
                padding: 0 10px;
            }

            .search-container form {
                flex-direction: column;
            }

            .search-container input[type="text"] {
                min-width: 100% !important;
            }

            .search-btn, .clear-btn {
                width: 100%;
                justify-content: center;
            }

            .podcast-filter {
                flex-direction: column;
                align-items: stretch !important;
            }

            .podcast-filter label {
                text-align: center;
            }

            .news-filters {
                justify-content: flex-start;
            }

            .filter-btn {
                font-size: 0.9em;
                padding: 8px 15px;
            }

            .active-filters {
                font-size: 0.85em !important;
            }
        }

        @media (max-width: 480px) {
            .news-header h1 {
                font-size: 1.8em;
            }

            .article-title {
                font-size: 1.1em;
            }
        }
    </style>

    <div class="news-header">
        <h1>Marine Corps News</h1>
        <p>Latest updates from Marines.mil, Marine Corps Times, Podcasts, and official sources</p>
    </div>

    <!-- Search and Podcast Filter Section -->
    <div class="search-podcast-section" style="max-width: 900px; margin: 0 auto 30px;">
        <!-- Search Bar -->
        <div class="search-container" style="margin-bottom: 15px;">
            <form method="get" action="" style="display: flex; gap: 10px; flex-wrap: wrap;">
                <input type="text"
                       name="search"
                       id="search-input"
                       placeholder="🔍 Search Marine Corps news and podcasts..."
                       value="<?php echo isset($_GET['search']) ? esc_attr($_GET['search']) : ''; ?>"
                       style="flex: 1; min-width: 250px; padding: 14px 18px; border: 2px solid #ddd; border-radius: 5px; font-size: 1em;">
                <?php if (isset($_GET['category'])) : ?>
                    <input type="hidden" name="category" value="<?php echo esc_attr($_GET['category']); ?>">
                <?php endif; ?>
                <?php if (isset($_GET['podcast_filter'])) : ?>
                    <input type="hidden" name="podcast_filter" value="<?php echo esc_attr($_GET['podcast_filter']); ?>">
                <?php endif; ?>
                <button type="submit"
                        class="search-btn"
                        style="padding: 14px 32px; background: #C41E3A; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; font-weight: bold; transition: all 0.3s; white-space: nowrap;"
                        onmouseover="this.style.background='#9A1830'; this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 8px rgba(196,30,58,0.3)'"
                        onmouseout="this.style.background='#C41E3A'; this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                    🔍 Search
                </button>
                <?php if (isset($_GET['search']) && !empty($_GET['search'])) : ?>
                    <a href="<?php echo esc_url(remove_query_arg('search')); ?>"
                       class="clear-btn"
                       style="padding: 14px 24px; background: #666; color: white; text-decoration: none; border-radius: 5px; display: inline-flex; align-items: center; gap: 5px; font-size: 1em; transition: all 0.3s; white-space: nowrap;"
                       onmouseover="this.style.background='#555'; this.style.transform='translateY(-2px)'"
                       onmouseout="this.style.background='#666'; this.style.transform='translateY(0)'">
                        ✕ Clear Search
                    </a>
                <?php endif; ?>
            </form>
        </div>

        <!-- Podcast Filter Dropdown -->
        <div class="podcast-filter" style="display: flex; gap: 10px; align-items: center; justify-content: center;">
            <label for="podcast-selector" style="font-weight: bold; color: #333; white-space: nowrap;">
                Filter Content:
            </label>
            <select id="podcast-selector"
                    onchange="window.location.href=this.value"
                    style="flex: 1; max-width: 300px; padding: 12px 15px; border: 2px solid #ddd; border-radius: 5px; font-size: 1em; cursor: pointer; background: white; transition: border-color 0.3s;"
                    onfocus="this.style.borderColor='#C41E3A'"
                    onblur="this.style.borderColor='#ddd'">
                <?php
                // Build URLs that preserve current search and category
                $current_params = array_filter($_GET, function($key) {
                    return !in_array($key, ['podcast_filter']);
                }, ARRAY_FILTER_USE_KEY);

                $all_url = add_query_arg($current_params, strtok($_SERVER['REQUEST_URI'], '?'));
                $podcast_only_url = add_query_arg(array_merge($current_params, ['podcast_filter' => 'only']), strtok($_SERVER['REQUEST_URI'], '?'));
                $news_only_url = add_query_arg(array_merge($current_params, ['podcast_filter' => 'exclude']), strtok($_SERVER['REQUEST_URI'], '?'));
                ?>
                <option value="<?php echo esc_url($all_url); ?>">
                    📰 All Content Types
                </option>
                <option value="<?php echo esc_url($podcast_only_url); ?>"
                        <?php echo (isset($_GET['podcast_filter']) && $_GET['podcast_filter'] === 'only') ? 'selected' : ''; ?>>
                    🎙️ Podcasts Only
                </option>
                <option value="<?php echo esc_url($news_only_url); ?>"
                        <?php echo (isset($_GET['podcast_filter']) && $_GET['podcast_filter'] === 'exclude') ? 'selected' : ''; ?>>
                    📰 News Only (No Podcasts)
                </option>
            </select>
        </div>

        <?php if (isset($_GET['search']) || isset($_GET['podcast_filter']) || isset($_GET['category'])) : ?>
        <div class="active-filters" style="margin-top: 15px; padding: 15px; background: #f0f0f0; border-radius: 5px; font-size: 0.9em; display: flex; flex-wrap: wrap; align-items: center; gap: 10px;">
            <strong style="color: #333;">Active Filters:</strong>
            <?php if (isset($_GET['search']) && !empty($_GET['search'])) : ?>
                <span style="display: inline-block; padding: 6px 12px; background: white; border-radius: 3px; border: 1px solid #ddd;">
                    🔍 Search: "<?php echo esc_html($_GET['search']); ?>"
                </span>
            <?php endif; ?>
            <?php if (isset($_GET['podcast_filter'])) : ?>
                <span style="display: inline-block; padding: 6px 12px; background: white; border-radius: 3px; border: 1px solid #ddd;">
                    <?php
                    if ($_GET['podcast_filter'] === 'only') echo '🎙️ Podcasts Only';
                    elseif ($_GET['podcast_filter'] === 'exclude') echo '📰 News Only';
                    ?>
                </span>
            <?php endif; ?>
            <?php if (!empty($category_filter)) : ?>
                <span style="display: inline-block; padding: 6px 12px; background: white; border-radius: 3px; border: 1px solid #ddd;">
                    📂 Category: <?php echo esc_html(ucfirst($category_filter)); ?>
                </span>
            <?php endif; ?>
            <?php
            // Show reset button if multiple filters or any filter is active
            $filter_count = 0;
            if (isset($_GET['search']) && !empty($_GET['search'])) $filter_count++;
            if (isset($_GET['podcast_filter'])) $filter_count++;
            if (isset($_GET['category'])) $filter_count++;
            if ($filter_count >= 1) :
            ?>
                <a href="<?php echo esc_url(strtok($_SERVER['REQUEST_URI'], '?')); ?>"
                   style="margin-left: auto; padding: 8px 16px; background: #C41E3A; color: white; text-decoration: none; border-radius: 4px; font-weight: bold; transition: background 0.3s;"
                   onmouseover="this.style.background='#9A1830'"
                   onmouseout="this.style.background='#C41E3A'">
                    ✕ Reset All Filters
                </a>
            <?php endif; ?>
        </div>
        <?php endif; ?>
    </div>

    <?php
    // Query parameters for filtering
    $paged = (get_query_var('paged')) ? get_query_var('paged') : 1;
    $category_filter = isset($_GET['category']) ? sanitize_text_field($_GET['category']) : '';
    $podcast_filter = isset($_GET['podcast_filter']) ? sanitize_text_field($_GET['podcast_filter']) : '';
    $search_query = isset($_GET['search']) ? sanitize_text_field($_GET['search']) : '';

    // Query arguments
    $args = array(
        'post_type' => 'marine_news', // Custom post type - created by importer
        'posts_per_page' => 12,
        'paged' => $paged,
        'orderby' => 'date',
        'order' => 'DESC'
    );

    // Enhanced search - search in title, content, excerpt, and custom fields
    if (!empty($search_query)) {
        $args['s'] = $search_query;

        // Also search in custom fields (source, author, tags)
        add_filter('posts_search', function($search, $wp_query) use ($search_query) {
            global $wpdb;
            if (!empty($search_query)) {
                $search .= " OR (";
                $search .= "({$wpdb->postmeta}.meta_key = 'news_source' AND {$wpdb->postmeta}.meta_value LIKE '%" . esc_sql($wpdb->esc_like($search_query)) . "%')";
                $search .= " OR ({$wpdb->postmeta}.meta_key = 'news_author' AND {$wpdb->postmeta}.meta_value LIKE '%" . esc_sql($wpdb->esc_like($search_query)) . "%')";
                $search .= " OR ({$wpdb->postmeta}.meta_key = 'news_tags' AND {$wpdb->postmeta}.meta_value LIKE '%" . esc_sql($wpdb->esc_like($search_query)) . "%')";
                $search .= ")";
            }
            return $search;
        }, 10, 2);

        add_filter('posts_join', function($join) use ($search_query) {
            global $wpdb;
            if (!empty($search_query)) {
                $join .= " LEFT JOIN {$wpdb->postmeta} ON {$wpdb->posts}.ID = {$wpdb->postmeta}.post_id";
            }
            return $join;
        });

        add_filter('posts_groupby', function($groupby) use ($search_query) {
            global $wpdb;
            if (!empty($search_query)) {
                $groupby = "{$wpdb->posts}.ID";
            }
            return $groupby;
        });
    }

    // Add category/podcast filter
    $tax_query = array();

    // Handle podcast filtering
    if ($podcast_filter === 'only') {
        $tax_query[] = array(
            'taxonomy' => 'news_category',
            'field' => 'slug',
            'terms' => 'podcast'
        );
    } elseif ($podcast_filter === 'exclude') {
        $tax_query[] = array(
            'taxonomy' => 'news_category',
            'field' => 'slug',
            'terms' => 'podcast',
            'operator' => 'NOT IN'
        );
    }

    // Handle category filter
    if (!empty($category_filter)) {
        $tax_query[] = array(
            'taxonomy' => 'news_category',
            'field' => 'slug',
            'terms' => $category_filter
        );
    }

    // Apply tax query if filters exist
    if (!empty($tax_query)) {
        $args['tax_query'] = array_merge(
            array('relation' => 'AND'),
            $tax_query
        );
    }

    $news_query = new WP_Query($args);

    // Get available categories for filters
    $categories = get_terms(array(
        'taxonomy' => 'news_category',
        'hide_empty' => true
    ));
    ?>

    <!-- Category Filters -->
    <?php if (!empty($categories) && !is_wp_error($categories)) : ?>
    <div class="news-filters">
        <?php
        // Build category URLs that preserve search and podcast filter
        $current_search_params = array_filter($_GET, function($key) {
            return !in_array($key, ['category']);
        }, ARRAY_FILTER_USE_KEY);
        ?>
        <button class="filter-btn <?php echo empty($category_filter) ? 'active' : ''; ?>"
                onclick="window.location.href='<?php echo esc_url(add_query_arg($current_search_params, strtok($_SERVER['REQUEST_URI'], '?'))); ?>'">
            All Categories
        </button>
        <?php foreach ($categories as $category) : ?>
        <?php
        $category_url = add_query_arg(array_merge($current_search_params, ['category' => $category->slug]), strtok($_SERVER['REQUEST_URI'], '?'));
        ?>
        <button class="filter-btn <?php echo ($category_filter === $category->slug) ? 'active' : ''; ?>"
                onclick="window.location.href='<?php echo esc_url($category_url); ?>'">
            <?php echo esc_html($category->name); ?> (<?php echo $category->count; ?>)
        </button>
        <?php endforeach; ?>
    </div>
    <?php endif; ?>

    <!-- Results Count -->
    <?php if ($news_query->have_posts()) : ?>
    <div class="results-count" style="text-align: center; margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 5px;">
        <strong style="color: #C41E3A; font-size: 1.1em;">
            <?php
            $total_results = $news_query->found_posts;
            echo number_format($total_results) . ' ' . ($total_results === 1 ? 'Article' : 'Articles');
            if (!empty($search_query)) {
                echo ' found for "' . esc_html($search_query) . '"';
            }
            ?>
        </strong>
        <?php if ($news_query->max_num_pages > 1) : ?>
            <span style="color: #666; margin-left: 10px;">
                (Page <?php echo $paged; ?> of <?php echo $news_query->max_num_pages; ?>)
            </span>
        <?php endif; ?>
    </div>
    <?php endif; ?>

    <!-- News Grid -->
    <div class="news-grid">
        <?php if ($news_query->have_posts()) : ?>
            <?php while ($news_query->have_posts()) : $news_query->the_post(); ?>
                <?php
                // Get category terms
                $terms = get_the_terms(get_the_ID(), 'news_category');
                $category_slug = !empty($terms) ? $terms[0]->slug : 'general';
                $is_podcast = ($category_slug === 'podcast');
                ?>
                <article class="news-article <?php echo $is_podcast ? 'podcast-article' : ''; ?>" data-category="<?php echo esc_attr($category_slug); ?>">
                    <?php if (has_post_thumbnail()) : ?>
                    <a href="<?php the_permalink(); ?>" class="article-thumb">
                        <?php the_post_thumbnail('medium_large', array('loading' => 'lazy', 'style' => 'width:100%;height:200px;object-fit:cover;display:block;')); ?>
                    </a>
                    <?php endif; ?>

                    <?php
                    // Display category badge
                    if (!empty($terms)) :
                    ?>
                    <span class="article-category <?php echo $is_podcast ? 'podcast' : ''; ?>"><?php echo esc_html($terms[0]->name); ?></span>
                    <?php endif; ?>

                    <h2 class="article-title">
                        <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
                    </h2>

                    <div class="article-meta">
                        <?php
                        $source = get_post_meta(get_the_ID(), 'news_source', true);
                        $author = get_post_meta(get_the_ID(), 'news_author', true);
                        ?>
                        <span class="source"><?php echo esc_html($source ?: 'Unknown Source'); ?></span>
                        <?php if ($author) : ?>
                        | <span class="author">By <?php echo esc_html($author); ?></span>
                        <?php endif; ?>
                        | <time><?php echo get_the_date('F j, Y'); ?></time>
                    </div>

                    <div class="article-excerpt">
                        <?php echo wp_trim_words(get_the_excerpt(), 30); ?>
                    </div>

                    <div class="article-footer">
                        <a href="<?php the_permalink(); ?>" class="read-more">Read More &rarr;</a>
                        <span class="comment-count">
                            <?php
                            $comment_count = get_comments_number();
                            echo $comment_count . ' ' . ($comment_count === 1 ? 'Comment' : 'Comments');
                            ?>
                        </span>
                    </div>
                </article>
            <?php endwhile; ?>
        <?php else : ?>
            <div class="no-results">
                <p>No articles found. Please run the importer script to import news from your JSON file.</p>
            </div>
        <?php endif; ?>
    </div>

    <!-- Pagination -->
    <?php if ($news_query->max_num_pages > 1) : ?>
    <div class="pagination" style="text-align: center; margin: 40px 0;">
        <?php
        echo paginate_links(array(
            'total' => $news_query->max_num_pages,
            'current' => $paged,
            'prev_text' => '&laquo; Previous',
            'next_text' => 'Next &raquo;',
        ));
        ?>
    </div>
    <?php endif; ?>

    <?php wp_reset_postdata(); ?>

    <?php
    // Clean up filters to prevent affecting other queries
    if (!empty($search_query)) {
        remove_all_filters('posts_search');
        remove_all_filters('posts_join');
        remove_all_filters('posts_groupby');
    }
    ?>

    <!-- Analytics Tracking -->
    <script>
        var jhAnalyticsData = {
            postId: null,
            postType: 'template',
            pageUrl: '<?php echo esc_js($_SERVER['REQUEST_URI']); ?>',
            pageTitle: 'Marine Corps News',
            ajaxUrl: '<?php echo admin_url('admin-ajax.php'); ?>',
            nonce: '<?php echo wp_create_nonce('jh_analytics_track'); ?>'
        };
    </script>
    <script src="<?php echo get_template_directory_uri(); ?>/jh-analytics-tracker.js" async></script>
</div>

<?php get_footer(); // Remove this line if you want completely independent styling ?>
