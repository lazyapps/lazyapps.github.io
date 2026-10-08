export function googleAnalytics(measurementId) {
  return {
    name: 'lazyapps-google-analytics',
    hooks: {
      'astro:config:setup': ({ command, config, injectScript }) => {
        if (command !== 'build' || !measurementId) return;
        if (!/^G-[A-Z0-9]+$/.test(measurementId)) {
          throw new Error('Invalid Google Analytics measurement ID');
        }

        const hostname = new URL(config.site).hostname;
        injectScript('head-inline', `
          (() => {
            if (window.location.hostname !== ${JSON.stringify(hostname)}) return;
            window.dataLayer = window.dataLayer || [];
            function gtag() { window.dataLayer.push(arguments); }
            gtag('js', new Date());
            gtag('config', ${JSON.stringify(measurementId)}, {
              allow_google_signals: false,
              allow_ad_personalization_signals: false,
              page_location: window.location.origin + window.location.pathname,
              page_referrer: document.referrer ? document.referrer.split(/[?#]/)[0] : ''
            });
            const script = document.createElement('script');
            script.async = true;
            script.src = 'https://www.googletagmanager.com/gtag/js?id=${measurementId}';
            document.head.appendChild(script);
          })();
        `);
      },
    },
  };
}
