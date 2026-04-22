(function () {
    const KEY = 'prefs';

    function sync() {
        try {
            const raw = localStorage.getItem(KEY);
            const prefs = raw ? JSON.parse(raw) : null;
            if (prefs) chrome.storage.local.set({ prefs }).catch(() => {});
            else chrome.storage.local.remove(KEY).catch(() => {});
        } catch {
            /* storage unavailable (e.g. incognito), ignore */
        }
    }

    sync();

    window.addEventListener('storage', (e) => {
        if (e.key === KEY || e.key === null) sync();
    });
})();
