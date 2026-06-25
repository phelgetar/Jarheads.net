<?php
/**
 * Archive Template for Marine News
 *
 * Displays list of Marine Corps news articles
 * File name: archive-marine_news.php
 */

get_header();
?>

<style>
    /* Override theme sidebar */
    #secondary {
        display: none !important;
    }

    #primary {
        width: 100% !important;
        float: none !important;
        margin: 0 !important;
    }

    .site-content {
        margin-left: 0 !important;
        width: 100% !important;
    }

    body {
        margin: 0;
        padding: 0;
    }

    .marine-news-archive {
        /* Fluid up to ultrawide: use the viewport but keep a margin and a
           sane upper bound so cards never stretch absurdly wide. */
        max-width: min(2200px, 95vw);
        margin: 0 auto;
        padding: 40px 20px;
        background: white;
        position: relative;
        z-index: 999;
    }

    .archive-header {
        text-align: center;
        margin-bottom: 40px;
        padding-bottom: 20px;
        border-bottom: 3px solid #C41E3A;
    }

    .archive-header h1 {
        color: #1A1A1A;
        font-size: 2.5em;
        margin-bottom: 10px;
    }

    .news-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 25px;
        margin-bottom: 40px;
    }

    .news-article-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .news-article-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }

    .news-article-card.podcast-article {
        border-left: 4px solid #9C27B0;
    }

    .article-category-badge {
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

    .article-category-badge.podcast {
        background: #9C27B0;
    }

    .article-category-badge.podcast::before {
        content: '🎙️ ';
    }

    .article-title {
        font-size: 1.3em;
        margin: 10px 0;
    }

    .article-title a {
        color: #1A1A1A;
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

    .read-more-link {
        display: inline-block;
        padding: 8px 16px;
        background: #C41E3A;
        color: white;
        text-decoration: none;
        border-radius: 4px;
        font-size: 0.9em;
        transition: background 0.3s;
    }

    .read-more-link:hover {
        background: #9A1830;
        color: white;
    }

    .pagination {
        text-align: center;
        margin: 40px 0;
    }

    .pagination a,
    .pagination span {
        display: inline-block;
        padding: 10px 15px;
        margin: 0 5px;
        background: #f0f0f0;
        border-radius: 4px;
        text-decoration: none;
        color: #333;
    }

    .pagination a:hover {
        background: #C41E3A;
        color: white;
    }

    .pagination .current {
        background: #C41E3A;
        color: white;
    }

    /* Category Filter Buttons */
    .category-filters {
        display: flex;
        gap: 15px;
        margin-bottom: 40px;
        flex-wrap: wrap;
        justify-content: center;
    }

    .filter-button {
        padding: 12px 24px;
        background: #ffffff;
        border: 2px solid #C41E3A;
        border-radius: 25px;
        cursor: pointer;
        transition: all 0.3s;
        text-decoration: none;
        color: #C41E3A;
        font-weight: 600;
        font-size: 0.95em;
    }

    .filter-button:hover {
        background: #C41E3A;
        color: white;
        border-color: #C41E3A;
        transform: translateY(-2px);
        box-shadow: 0 3px 8px rgba(196, 30, 58, 0.3);
    }

    .filter-button.active {
        background: #C41E3A;
        color: white;
        border-color: #C41E3A;
        box-shadow: 0 2px 6px rgba(196, 30, 58, 0.4);
    }

    .filter-count {
        display: inline-block;
        margin-left: 5px;
        padding: 2px 8px;
        background: rgba(255,255,255,0.2);
        border-radius: 12px;
        font-size: 0.85em;
    }

    /* Search and Filter Section */
    .search-podcast-section {
        max-width: 900px;
        margin: 0 auto 30px;
    }

    .search-container {
        margin-bottom: 15px;
    }

    .search-container input[type="text"] {
        flex: 1;
        min-width: 250px;
        padding: 14px 18px;
        border: 2px solid #ddd;
        border-radius: 5px;
        font-size: 1em;
    }

    .search-btn {
        padding: 14px 32px;
        background: #C41E3A;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 1em;
        font-weight: bold;
        transition: all 0.3s;
        white-space: nowrap;
    }

    .search-btn:hover {
        background: #9A1830;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(196,30,58,0.3);
    }

    .clear-btn {
        padding: 14px 24px;
        background: #666;
        color: white;
        text-decoration: none;
        border-radius: 5px;
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 1em;
        transition: all 0.3s;
        white-space: nowrap;
    }

    .clear-btn:hover {
        background: #555;
        transform: translateY(-2px);
    }

    .podcast-filter {
        display: flex;
        gap: 10px;
        align-items: center;
        justify-content: center;
    }

    .podcast-filter label {
        font-weight: bold;
        color: #333;
        white-space: nowrap;
    }

    .podcast-filter select {
        flex: 1;
        max-width: 300px;
        padding: 12px 15px;
        border: 2px solid #ddd;
        border-radius: 5px;
        font-size: 1em;
        cursor: pointer;
        background: white;
        transition: border-color 0.3s;
    }

    .podcast-filter select:focus {
        border-color: #C41E3A;
        outline: none;
    }

    .active-filters {
        margin-top: 15px;
        padding: 15px;
        background: #f0f0f0;
        border-radius: 5px;
        font-size: 0.9em;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 10px;
    }

    .active-filters span {
        display: inline-block;
        padding: 6px 12px;
        background: white;
        border-radius: 3px;
        border: 1px solid #ddd;
    }

    .reset-filters-btn {
        margin-left: auto;
        padding: 8px 16px;
        background: #C41E3A;
        color: white;
        text-decoration: none;
        border-radius: 4px;
        font-weight: bold;
        transition: background 0.3s;
    }

    .reset-filters-btn:hover {
        background: #9A1830;
    }

    .results-count {
        text-align: center;
        margin: 20px 0;
        padding: 15px;
        background: #f9f9f9;
        border-radius: 5px;
    }

    .results-count strong {
        color: #C41E3A;
        font-size: 1.1em;
    }

    /* Mobile Responsive */
    @media (max-width: 768px) {
        .news-grid {
            grid-template-columns: 1fr;
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

        .category-filters {
            justify-content: flex-start;
        }

        .filter-button {
            font-size: 0.9em;
            padding: 10px 18px;
        }
    }

    @media (max-width: 480px) {
        .archive-header h1 {
            font-size: 1.8em;
        }

        .article-title {
            font-size: 1.1em;
        }
    }
</style>

<div class="marine-news-archive">
    <header class="archive-header">
        <h1>Marine Corps News Archive</h1>
        <p>Latest updates from Marines.mil, Marine Corps Times, Podcasts, and official sources</p>
    </header>

    <?php
    // Get search and filter parameters
    $search_query = isset($_GET['search']) ? sanitize_text_field($_GET['search']) : '';
    $podcast_filter = isset($_GET['podcast_filter']) ? sanitize_text_field($_GET['podcast_filter']) : '';
    $current_category = get_query_var('news_category');
    ?>

    <!-- Search and Podcast Filter Section -->
    <div class="search-podcast-section">
        <!-- Search Bar -->
        <div class="search-container">
            <form method="get" action="" style="display: flex; gap: 10px; flex-wrap: wrap;">
                <input type="text"
                       name="search"
                       id="search-input"
                       placeholder="🔍 Search Marine Corps news and podcasts..."
                       value="<?php echo esc_attr($search_query); ?>">
                <?php if ($current_category) : ?>
                    <input type="hidden" name="news_category" value="<?php echo esc_attr($current_category); ?>">
                <?php endif; ?>
                <?php if ($podcast_filter) : ?>
                    <input type="hidden" name="podcast_filter" value="<?php echo esc_attr($podcast_filter); ?>">
                <?php endif; ?>
                <button type="submit" class="search-btn">
                    🔍 Search
                </button>
                <?php if (!empty($search_query)) : ?>
                    <a href="<?php echo esc_url(remove_query_arg('search')); ?>" class="clear-btn">
                        ✕ Clear Search
                    </a>
                <?php endif; ?>
            </form>
        </div>

        <!-- Category and Content Filter Dropdown -->
        <div class="podcast-filter">
            <label for="podcast-selector">Filter Content:</label>
            <select id="podcast-selector" onchange="window.location.href=this.value">
                <?php
                $current_params = array_filter($_GET, function($key) {
                    return !in_array($key, ['podcast_filter', 'news_category']);
                }, ARRAY_FILTER_USE_KEY);

                $base_url = strtok($_SERVER['REQUEST_URI'], '?');
                $all_url = add_query_arg($current_params, $base_url);
                $podcast_only_url = add_query_arg(array_merge($current_params, ['podcast_filter' => 'only']), $base_url);
                $news_only_url = add_query_arg(array_merge($current_params, ['podcast_filter' => 'exclude']), $base_url);

                // Get all categories for dropdown
                $all_categories = get_terms(array(
                    'taxonomy' => 'news_category',
                    'hide_empty' => false,
                    'orderby' => 'name',
                    'order' => 'ASC'
                ));
                ?>

                <optgroup label="Content Type">
                    <option value="<?php echo esc_url($all_url); ?>"
                            <?php echo (empty($podcast_filter) && empty($current_category)) ? 'selected' : ''; ?>>
                        📰 All Content Types
                    </option>
                    <option value="<?php echo esc_url($podcast_only_url); ?>"
                            <?php echo ($podcast_filter === 'only') ? 'selected' : ''; ?>>
                        🎙️ Podcasts Only
                    </option>
                    <option value="<?php echo esc_url($news_only_url); ?>"
                            <?php echo ($podcast_filter === 'exclude') ? 'selected' : ''; ?>>
                        📰 News Only (No Podcasts)
                    </option>
                </optgroup>

                <?php if (!empty($all_categories) && !is_wp_error($all_categories)) : ?>
                <optgroup label="By Category">
                    <?php foreach ($all_categories as $cat) : ?>
                        <?php
                        $cat_url = add_query_arg($current_params, get_term_link($cat));
                        $emoji = ($cat->slug === 'podcast') ? '🎙️' : '📂';
                        ?>
                        <option value="<?php echo esc_url($cat_url); ?>"
                                <?php echo ($current_category === $cat->slug) ? 'selected' : ''; ?>>
                            <?php echo $emoji; ?> <?php echo esc_html(ucfirst($cat->name)); ?> (<?php echo $cat->count; ?>)
                        </option>
                    <?php endforeach; ?>
                </optgroup>
                <?php endif; ?>
            </select>
        </div>

        <!-- Active Filters Display -->
        <?php if ($search_query || $podcast_filter || $current_category) : ?>
        <div class="active-filters">
            <strong>Active Filters:</strong>
            <?php if ($search_query) : ?>
                <span>🔍 Search: "<?php echo esc_html($search_query); ?>"</span>
            <?php endif; ?>
            <?php if ($podcast_filter) : ?>
                <span>
                    <?php
                    if ($podcast_filter === 'only') echo '🎙️ Podcasts Only';
                    elseif ($podcast_filter === 'exclude') echo '📰 News Only';
                    ?>
                </span>
            <?php endif; ?>
            <?php if ($current_category) : ?>
                <span>📂 Category: <?php echo esc_html(ucfirst($current_category)); ?></span>
            <?php endif; ?>
            <a href="<?php echo get_post_type_archive_link('marine_news'); ?>" class="reset-filters-btn">
                ✕ Reset All Filters
            </a>
        </div>
        <?php endif; ?>
    </div>

    <?php
    // Build query args with filters
    global $wp_query;
    $args = $wp_query->query_vars;

    // Add search
    if (!empty($search_query)) {
        $args['s'] = $search_query;
    }

    // Add podcast filter
    if ($podcast_filter) {
        $tax_query = isset($args['tax_query']) ? $args['tax_query'] : array();

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

        if (!empty($tax_query)) {
            $args['tax_query'] = $tax_query;
        }
    }

    // Re-query with filters
    $filtered_query = new WP_Query($args);

    // Get all categories with counts (including empty ones)
    $categories = get_terms(array(
        'taxonomy' => 'news_category',
        'hide_empty' => false,
        'orderby' => 'name',
        'order' => 'ASC'
    ));
    ?>

    <!-- Category Filter Buttons -->
    <div class="category-filters">
        <?php
        $current_search_params = array_filter($_GET, function($key) {
            return $key !== 'news_category';
        }, ARRAY_FILTER_USE_KEY);
        ?>
        <a href="<?php echo esc_url(add_query_arg($current_search_params, get_post_type_archive_link('marine_news'))); ?>"
           class="filter-button <?php echo empty($current_category) ? 'active' : ''; ?>">
            All Categories
        </a>

        <?php if (!empty($categories) && !is_wp_error($categories)) : ?>
            <?php foreach ($categories as $category) : ?>
                <?php
                $cat_url = add_query_arg($current_search_params, get_term_link($category));
                ?>
                <a href="<?php echo esc_url($cat_url); ?>"
                   class="filter-button <?php echo ($current_category === $category->slug) ? 'active' : ''; ?>">
                    <?php echo esc_html(ucfirst($category->name)); ?>
                    <span class="filter-count"><?php echo $category->count; ?></span>
                </a>
            <?php endforeach; ?>
        <?php endif; ?>
    </div>

    <!-- Results Count -->
    <?php if ($filtered_query->have_posts()) : ?>
    <div class="results-count">
        <strong>
            <?php
            $total = $filtered_query->found_posts;
            echo number_format($total) . ' ' . ($total === 1 ? 'Article' : 'Articles');
            if ($search_query) {
                echo ' found for "' . esc_html($search_query) . '"';
            }
            ?>
        </strong>
        <?php if ($filtered_query->max_num_pages > 1) : ?>
            <span style="color: #666; margin-left: 10px;">
                (Page <?php echo max(1, get_query_var('paged')); ?> of <?php echo $filtered_query->max_num_pages; ?>)
            </span>
        <?php endif; ?>
    </div>

    <div class="news-grid">
        <?php while ($filtered_query->have_posts()) : $filtered_query->the_post(); ?>
            <?php
            $terms = get_the_terms(get_the_ID(), 'news_category');
            $category_slug = !empty($terms) ? $terms[0]->slug : 'general';
            $is_podcast = ($category_slug === 'podcast');
            ?>
            <article class="news-article-card <?php echo $is_podcast ? 'podcast-article' : ''; ?>">
                <?php if (has_post_thumbnail()) : ?>
                <a href="<?php the_permalink(); ?>" class="article-thumb">
                    <?php the_post_thumbnail('medium_large', array('loading' => 'lazy', 'style' => 'width:100%;height:200px;object-fit:cover;display:block;')); ?>
                </a>
                <?php endif; ?>

                <?php if (!empty($terms) && !is_wp_error($terms)) : ?>
                <span class="article-category-badge <?php echo $is_podcast ? 'podcast' : ''; ?>">
                    <?php echo esc_html($terms[0]->name); ?>
                </span>
                <?php endif; ?>

                <h2 class="article-title">
                    <a href="<?php the_permalink(); ?>">
                        <?php the_title(); ?>
                    </a>
                </h2>

                <div class="article-meta">
                    <?php
                    $source = get_post_meta(get_the_ID(), 'news_source', true);
                    $author = get_post_meta(get_the_ID(), 'news_author', true);
                    ?>
                    <?php if ($source) : ?>
                    <span class="source"><?php echo esc_html($source); ?></span> |
                    <?php endif; ?>
                    <time><?php echo get_the_date('F j, Y'); ?></time>
                    <?php if ($author) : ?>
                    | By <?php echo esc_html($author); ?>
                    <?php endif; ?>
                </div>

                <div class="article-excerpt">
                    <?php echo wp_trim_words(get_the_excerpt(), 25); ?>
                </div>

                <a href="<?php the_permalink(); ?>" class="read-more-link">
                    Read More & Comment →
                </a>
            </article>
        <?php endwhile; ?>
    </div>

    <div class="pagination">
        <?php
        echo paginate_links(array(
            'total' => $filtered_query->max_num_pages,
            'prev_text' => '&laquo; Previous',
            'next_text' => 'Next &raquo;',
        ));
        ?>
    </div>
    <?php else : ?>
        <p style="text-align: center; padding: 60px 20px; color: #666; font-size: 1.2em;">
            No articles found.
            <?php if ($search_query || $podcast_filter) : ?>
                <br><a href="<?php echo get_post_type_archive_link('marine_news'); ?>" style="color: #C41E3A;">Clear filters to see all articles</a>
            <?php endif; ?>
        </p>
    <?php endif; ?>

    <?php wp_reset_postdata(); ?>

    <!-- Analytics Tracking -->
    <script>
        var jhAnalyticsData = {
            postId: null,
            postType: 'archive',
            pageUrl: '<?php echo esc_js($_SERVER['REQUEST_URI']); ?>',
            pageTitle: 'Marine Corps News Archive',
            ajaxUrl: '<?php echo admin_url('admin-ajax.php'); ?>',
            nonce: '<?php echo wp_create_nonce('jh_analytics_track'); ?>'
        };
    </script>
    <script src="<?php echo get_template_directory_uri(); ?>/jh-analytics-tracker.js" async></script>
</div>

<?php get_footer(); ?>
