(function() {
    const errorScript = document.querySelector('script[src*="js/error_"]');
    if (!errorScript) {
        return;
    }

    const script = document.createElement('script');
    script.src = chrome.runtime.getURL('niconico-embed-injected.js');
    (document.head || document.documentElement).appendChild(script);
    script.remove();
})();
