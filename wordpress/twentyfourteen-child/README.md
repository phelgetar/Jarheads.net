# Twenty Fourteen Child — Jarheads Marine News

A child theme of **Twenty Fourteen** that adds the full-width, responsive
Marine Corps News layout without modifying the parent theme (so Twenty
Fourteen updates won't erase the customizations).

## Contents
- `style.css` — required child-theme header (`Template: twentyfourteen`)
- `functions.php` — enqueues parent + child stylesheets
- `archive-marine_news.php` — full-width responsive grid for `/marine-news/`
- `single-marine_news.php` — single article template with comments + hero image

## Install

### Option A — Upload via wp-admin (no FTP)
1. Zip this folder so the archive contains `twentyfourteen-child/...`.
2. WordPress admin → **Appearance → Themes → Add New → Upload Theme**.
3. Choose the zip → **Install Now** → **Activate**.

### Option B — FTP/SFTP
1. Upload the whole `twentyfourteen-child/` folder to:
   `wp-content/themes/twentyfourteen-child/`
2. WordPress admin → **Appearance → Themes** → activate
   **"Twenty Fourteen Child (Jarheads Marine News)"**.

## After activating
- The parent **Twenty Fourteen** must remain installed (do not delete it).
- Make sure the **Marine Corps News** plugin (`marine-news-plugin.php`) is
  active — it registers the `marine_news` post type and imports articles,
  including sideloading featured images as post thumbnails.
- Visit `/marine-news/` — it now renders the responsive card grid. Featured
  images appear after the importer runs (hourly cron, or trigger it manually).

## Notes
- Because the templates fully replace the default layout, the temporary
  "Additional CSS" grid hack (Appearance → Customize) becomes a harmless
  no-op and can be removed.
- Menus/widgets assigned to the parent theme may need to be re-assigned after
  switching themes (WordPress ties some of these to the active theme).
