(function () {
    const KEY = 'prefs';

    function sync() {
        try {
            const raw = localStorage.getItem(KEY);
            const prefs = raw ? JSON.parse(raw) : null;
            const p = prefs
                ? chrome.storage.local.set({ prefs })
                : chrome.storage.local.remove(KEY);
            p.catch((err) => console.error('otoDB: prefs sync failed', err));
        } catch (err) {
            console.error('otoDB: prefs sync threw', err);
        }
    }

    sync();

    window.addEventListener('storage', (e) => {
        if (e.key === KEY || e.key === null) sync();
    });
})();
