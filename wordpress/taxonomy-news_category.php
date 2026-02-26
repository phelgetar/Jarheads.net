<?php
/**
 * Taxonomy Template for News Categories
 *
 * Displays filtered Marine Corps news articles by category
 * File name: taxonomy-news_category.php
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
        max-width: 1200px;
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

    .category-badge {
        display: inline-block;
        padding: 8px 16px;
        background: #C41E3A;
        color: white;
        font-size: 0.9em;
        text-transform: uppercase;
        border-radius: 4px;
        margin-bottom: 15px;
        font-weight: bold;
    }

    .news-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
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
        background: #f0f0f0;
        border: 2px solid #ddd;
        border-radius: 25px;
        cursor: pointer;
        transition: all 0.3s;
        text-decoration: none;
        color: #333;
        font-weight: 500;
        font-size: 0.95em;
    }

    .filter-button:hover {
        background: #C41E3A;
        color: white;
        border-color: #C41E3A;
        transform: translateY(-2px);
    }

    .filter-button.active {
        background: #C41E3A;
        color: white;
        border-color: #C41E3A;
    }

    .filter-count {
        display: inline-block;
        margin-left: 5px;
        padding: 2px 8px;
        background: rgba(255,255,255,0.2);
        border-radius: 12px;
        font-size: 0.85em;
    }
</style>

<div class="marine-news-archive">
    <?php
    $current_term = get_queried_object();
    ?>

    <header class="archive-header">
        <span class="category-badge"><?php echo esc_html(ucfirst($current_term->name)); ?></span>
        <h1><?php echo esc_html(ucfirst($current_term->name)); ?> News</h1>
        <p><?php echo $current_term->count; ?> articles in this category</p>
    </header>

    <?php
    // Get all categories with counts
    $categories = get_terms(array(
        'taxonomy' => 'news_category',
        'hide_empty' => true,
        'orderby' => 'name',
        'order' => 'ASC'
    ));
    ?>

    <!-- Category Filter Buttons -->
    <div class="category-filters">
        <a href="<?php echo get_post_type_archive_link('marine_news'); ?>"
           class="filter-button">
            All News
        </a>

        <?php if (!empty($categories) && !is_wp_error($categories)) : ?>
            <?php foreach ($categories as $category) : ?>
                <a href="<?php echo get_term_link($category); ?>"
                   class="filter-button <?php echo ($current_term->slug === $category->slug) ? 'active' : ''; ?>">
                    <?php echo esc_html(ucfirst($category->name)); ?>
                    <span class="filter-count"><?php echo $category->count; ?></span>
                </a>
            <?php endforeach; ?>
        <?php endif; ?>
    </div>

    <?php if (have_posts()) : ?>
        <div class="news-grid">
            <?php while (have_posts()) : the_post(); ?>
                <article class="news-article-card">
                    <?php
                    // Display category badge
                    $terms = get_the_terms(get_the_ID(), 'news_category');
                    if (!empty($terms) && !is_wp_error($terms)) :
                    ?>
                    <span class="article-category-badge">
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
                'prev_text' => '&laquo; Previous',
                'next_text' => 'Next &raquo;',
            ));
            ?>
        </div>
    <?php else : ?>
        <p>No articles found in this category.</p>
    <?php endif; ?>
</div>

<?php get_footer(); ?>
