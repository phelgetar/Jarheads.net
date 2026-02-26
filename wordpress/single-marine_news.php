<?php
/**
 * Single Post Template for Marine News
 *
 * Displays individual Marine Corps news articles with comments
 * File name: single-marine_news.php
 *
 * Place this file in your WordPress theme directory:
 * wp-content/themes/YOUR-THEME-NAME/single-marine_news.php
 */

get_header(); // Remove if you want independent styling
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

    .marine-news-single {
        max-width: 900px;
        margin: 0 auto;
        padding: 40px 20px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
        background: white;
        position: relative;
        z-index: 999;
    }

    .news-article-header {
        margin-bottom: 30px;
        padding-bottom: 20px;
        border-bottom: 3px solid #C41E3A;
    }

    .article-category-badge {
        display: inline-block;
        padding: 8px 16px;
        background: #C41E3A;
        color: white;
        font-size: 0.85em;
        text-transform: uppercase;
        border-radius: 4px;
        margin-bottom: 15px;
        font-weight: bold;
    }

    .article-main-title {
        font-size: 2.5em;
        color: #1A1A1A;
        margin: 15px 0;
        line-height: 1.2;
    }

    .article-meta-info {
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
        color: #666;
        font-size: 0.95em;
        margin: 20px 0;
    }

    .article-meta-info > span {
        display: flex;
        align-items: center;
        gap: 5px;
    }

    .article-content {
        font-size: 1.1em;
        line-height: 1.8;
        color: #333;
        margin: 30px 0;
    }

    .article-content p {
        margin-bottom: 20px;
    }

    .original-source-box {
        background: #f8f9fa;
        border-left: 4px solid #C41E3A;
        padding: 20px;
        margin: 30px 0;
        border-radius: 4px;
    }

    .original-source-box a {
        color: #C41E3A;
        text-decoration: none;
        font-weight: bold;
        font-size: 1.1em;
    }

    .original-source-box a:hover {
        text-decoration: underline;
    }

    .article-tags {
        margin: 30px 0;
        padding: 20px 0;
        border-top: 1px solid #e0e0e0;
    }

    .tag-item {
        display: inline-block;
        background: #f0f0f0;
        padding: 6px 12px;
        margin: 5px;
        border-radius: 3px;
        font-size: 0.9em;
        color: #555;
    }

    .back-to-news {
        display: inline-block;
        padding: 12px 24px;
        background: #C41E3A;
        color: white;
        text-decoration: none;
        border-radius: 5px;
        margin: 20px 0;
        transition: background 0.3s;
    }

    .back-to-news:hover {
        background: #9A1830;
        color: white;
    }

    .comments-section {
        margin-top: 60px;
        padding-top: 40px;
        border-top: 2px solid #e0e0e0;
    }

    .comments-section h2 {
        color: #1A1A1A;
        margin-bottom: 30px;
    }

    /* Override some default WordPress comment styles */
    .comment-list {
        list-style: none;
        padding: 0;
    }

    .comment-body {
        background: #f8f9fa;
        padding: 20px;
        margin-bottom: 20px;
        border-radius: 8px;
        border-left: 3px solid #C41E3A;
    }

    .comment-author {
        font-weight: bold;
        color: #1A1A1A;
    }

    .comment-meta {
        color: #666;
        font-size: 0.9em;
        margin: 5px 0;
    }

    .comment-content {
        margin-top: 15px;
        line-height: 1.6;
    }

    .comment-reply-link {
        color: #C41E3A;
        text-decoration: none;
        font-size: 0.9em;
    }

    .comment-reply-link:hover {
        text-decoration: underline;
    }
</style>

<div class="marine-news-single">
    <?php while (have_posts()) : the_post(); ?>

        <article class="news-article-single">
            <header class="news-article-header">
                <?php
                // Display category
                $terms = get_the_terms(get_the_ID(), 'news_category');
                if (!empty($terms) && !is_wp_error($terms)) :
                ?>
                <span class="article-category-badge">
                    <?php echo esc_html($terms[0]->name); ?>
                </span>
                <?php endif; ?>

                <h1 class="article-main-title"><?php the_title(); ?></h1>

                <div class="article-meta-info">
                    <?php
                    $source = get_post_meta(get_the_ID(), 'news_source', true);
                    $author = get_post_meta(get_the_ID(), 'news_author', true);
                    $original_date = get_post_meta(get_the_ID(), 'original_published_date', true);
                    ?>

                    <?php if ($source) : ?>
                    <span class="meta-source">
                        <strong>Source:</strong> <?php echo esc_html($source); ?>
                    </span>
                    <?php endif; ?>

                    <?php if ($author) : ?>
                    <span class="meta-author">
                        <strong>By:</strong> <?php echo esc_html($author); ?>
                    </span>
                    <?php endif; ?>

                    <span class="meta-date">
                        <strong>Published:</strong> <?php echo get_the_date('F j, Y'); ?>
                    </span>

                    <span class="meta-comments">
                        <strong>Comments:</strong> <?php echo get_comments_number(); ?>
                    </span>
                </div>
            </header>

            <div class="article-content">
                <?php the_content(); ?>
            </div>

            <?php
            // Display link to original source
            $original_url = get_post_meta(get_the_ID(), 'news_url', true);
            if ($original_url) :
            ?>
            <div class="original-source-box">
                <p><strong>Read the full article at the original source:</strong></p>
                <a href="<?php echo esc_url($original_url); ?>" target="_blank" rel="noopener noreferrer">
                    <?php echo esc_html($source ?: 'View Original Article'); ?> &rarr;
                </a>
            </div>
            <?php endif; ?>

            <?php
            // Display tags
            $tags = get_the_tags();
            if ($tags && !is_wp_error($tags)) :
            ?>
            <div class="article-tags">
                <strong>Tags:</strong>
                <?php foreach ($tags as $tag) : ?>
                <span class="tag-item"><?php echo esc_html($tag->name); ?></span>
                <?php endforeach; ?>
            </div>
            <?php endif; ?>

            <a href="<?php echo get_post_type_archive_link('marine_news'); ?>" class="back-to-news">
                &larr; Back to All News
            </a>
        </article>

        <?php
        // Display Comments Section
        if (comments_open() || get_comments_number()) :
        ?>
        <div class="comments-section">
            <?php comments_template(); ?>
        </div>
        <?php endif; ?>

    <?php endwhile; ?>

    <!-- Analytics Tracking -->
    <script>
        var jhAnalyticsData = {
            postId: <?php echo get_the_ID(); ?>,
            postType: 'marine_news',
            pageUrl: '<?php echo esc_js(get_permalink()); ?>',
            pageTitle: '<?php echo esc_js(get_the_title()); ?>',
            ajaxUrl: '<?php echo admin_url('admin-ajax.php'); ?>',
            nonce: '<?php echo wp_create_nonce('jh_analytics_track'); ?>'
        };
    </script>
    <script src="<?php echo get_template_directory_uri(); ?>/jh-analytics-tracker.js" async></script>
</div>

<?php get_footer(); // Remove if you want independent styling ?>
