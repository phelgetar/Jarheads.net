/**
 * Jarheads.net Analytics Tracker
 * Client-side tracking beacon for visitor analytics
 * Version: 1.0.0
 * Created: January 17, 2026
 */

(function() {
    'use strict';

    // Respect Do Not Track
    if (navigator.doNotTrack === '1' || window.doNotTrack === '1') {
        console.log('[JH Analytics] Do Not Track enabled, skipping analytics');
        return;
    }

    // Check for tracking exclusion cookie (for site owner/admins)
    if (document.cookie.indexOf('jh_exclude_tracking=1') !== -1) {
        console.log('[JH Analytics] Tracking excluded by cookie, skipping analytics');
        return;
    }

    // Check if analytics data is available
    if (typeof jhAnalyticsData === 'undefined') {
        console.warn('[JH Analytics] jhAnalyticsData not defined');
        return;
    }

    /**
     * Generate UUID v4 for session identification
     * @returns {string} UUID string
     */
    function generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0;
            var v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    /**
     * Get or create visitor session ID from cookie
     * @returns {string} Session ID (UUID)
     */
    function getOrCreateSessionId() {
        var cookieName = 'jh_visitor_session';
        var cookies = document.cookie.split(';');

        // Search for existing session cookie
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.indexOf(cookieName + '=') === 0) {
                return cookie.substring(cookieName.length + 1);
            }
        }

        // Create new session ID
        var sessionId = generateUUID();
        var expiryDate = new Date();
        expiryDate.setFullYear(expiryDate.getFullYear() + 1); // 365 days

        // Set cookie with secure attributes
        var cookieValue = cookieName + '=' + sessionId + '; ' +
                         'expires=' + expiryDate.toUTCString() + '; ' +
                         'path=/; ' +
                         'SameSite=Lax';

        // Add Secure flag if on HTTPS
        if (window.location.protocol === 'https:') {
            cookieValue += '; Secure';
        }

        document.cookie = cookieValue;
        return sessionId;
    }

    /**
     * Detect device type from user agent
     * @returns {string} 'mobile', 'tablet', or 'desktop'
     */
    function detectDevice() {
        var ua = navigator.userAgent;

        // Tablet detection
        if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) {
            return 'tablet';
        }

        // Mobile detection
        if (/Mobile|Android|iP(hone|od)|IEMobile|BlackBerry|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/.test(ua)) {
            return 'mobile';
        }

        return 'desktop';
    }

    /**
     * Extract search terms from referrer URL
     * @param {string} referrerURL - The HTTP referrer
     * @returns {string|null} Search terms or null
     */
    function extractSearchTerms(referrerURL) {
        if (!referrerURL || referrerURL === '') {
            return null;
        }

        try {
            var url = new URL(referrerURL);
            var hostname = url.hostname.toLowerCase();

            // Google search
            if (hostname.includes('google')) {
                return url.searchParams.get('q');
            }

            // Bing search
            if (hostname.includes('bing')) {
                return url.searchParams.get('q');
            }

            // Yahoo search
            if (hostname.includes('yahoo')) {
                return url.searchParams.get('p');
            }

            // DuckDuckGo search
            if (hostname.includes('duckduckgo')) {
                return url.searchParams.get('q');
            }

            return null;
        } catch (e) {
            return null;
        }
    }

    /**
     * Collect all page tracking data
     * @returns {object} Tracking data payload
     */
    function collectPageData() {
        var sessionId = getOrCreateSessionId();
        var deviceType = detectDevice();
        var referrer = document.referrer || '';
        var searchTerms = extractSearchTerms(referrer);

        return {
            session_id: sessionId,
            post_id: jhAnalyticsData.postId || null,
            post_type: jhAnalyticsData.postType || 'unknown',
            page_url: jhAnalyticsData.pageUrl || window.location.href,
            page_title: jhAnalyticsData.pageTitle || document.title,
            referrer_url: referrer,
            search_terms: searchTerms,
            device_type: deviceType,
            user_agent: navigator.userAgent,
            screen_resolution: screen.width + 'x' + screen.height,
            timestamp: Math.floor(Date.now() / 1000),
            nonce: jhAnalyticsData.nonce
        };
    }

    /**
     * Send tracking beacon to server
     * @param {object} data - Tracking data
     * @param {number} retryCount - Current retry attempt
     */
    function sendBeacon(data, retryCount) {
        retryCount = retryCount || 0;
        var maxRetries = 3;

        // Prepare form data
        var formData = new FormData();
        formData.append('action', 'jh_track_page');

        for (var key in data) {
            if (data.hasOwnProperty(key) && data[key] !== null) {
                formData.append(key, data[key]);
            }
        }

        // Send via fetch API
        fetch(jhAnalyticsData.ajaxUrl, {
            method: 'POST',
            body: formData,
            credentials: 'same-origin',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(function(response) {
            if (!response.ok) {
                throw new Error('HTTP ' + response.status);
            }
            return response.json();
        })
        .then(function(result) {
            if (result.success) {
                console.log('[JH Analytics] Page view tracked successfully');
            } else {
                console.warn('[JH Analytics] Tracking failed:', result.message);
            }
        })
        .catch(function(error) {
            console.error('[JH Analytics] Beacon error:', error);

            // Retry with exponential backoff
            if (retryCount < maxRetries) {
                var delay = Math.pow(2, retryCount) * 1000; // 1s, 2s, 4s
                console.log('[JH Analytics] Retrying in ' + delay + 'ms...');

                setTimeout(function() {
                    sendBeacon(data, retryCount + 1);
                }, delay);
            }
        });
    }

    /**
     * Alternative beacon using Image pixel (fallback)
     * @param {object} data - Tracking data
     */
    function sendPixelBeacon(data) {
        var params = [];
        for (var key in data) {
            if (data.hasOwnProperty(key) && data[key] !== null) {
                params.push(encodeURIComponent(key) + '=' + encodeURIComponent(data[key]));
            }
        }

        var img = new Image(1, 1);
        img.src = jhAnalyticsData.ajaxUrl + '?action=jh_track_page&' + params.join('&');
    }

    /**
     * Initialize tracking on page load
     */
    function init() {
        try {
            var trackingData = collectPageData();

            // Use fetch if available, fallback to pixel beacon
            if (typeof fetch !== 'undefined') {
                sendBeacon(trackingData);
            } else {
                sendPixelBeacon(trackingData);
            }
        } catch (error) {
            console.error('[JH Analytics] Initialization error:', error);
        }
    }

    // Track page view when DOM is fully loaded
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        // DOM is already ready, execute immediately
        setTimeout(init, 1);
    } else {
        // Wait for DOM ready
        document.addEventListener('DOMContentLoaded', init);
    }

})();
