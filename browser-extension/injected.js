(function() {
    function tryUncensor(obj) {
        if (typeof obj !== 'object' || obj === null) {
            return obj;
        }

        if (Array.isArray(obj)) {
            return obj.map(item => tryUncensor(item));
        } else {
            const result = {};
            for (const key in obj) {
                if (key === 'requireSensitiveMasking') {
                    result[key] = false;
                } else {
                    result[key] = tryUncensor(obj[key]);
                }
            }
            return result;
        }
    }

    const originalJSONParse = JSON.parse;
    const originalFetch = window.fetch;

    JSON.parse = function(...args) {
        let result = originalJSONParse.call(JSON, ...args);
        if (result && typeof result === 'object') {
            try {
                result = tryUncensor(result);
            } catch (e) {
                console.error("Error attempting to modify data in JSON.parse():", e);
            }
        }
        return result;
    };

    window.fetch = async function(...args) {
        const response = await originalFetch(...args);
        if (response.ok && response.headers.get('Content-Type').split(';')[0] === 'application/json') {
            const clonedResponseText = response.clone();
            const clonedResponseJson = response.clone();
            try {
                const text = await clonedResponseText.text();
                if (!text) {
                    return response;
                }
                const data = await clonedResponseJson.json();
                const result = tryUncensor(data);
                return new Response(JSON.stringify(result), {
                    status: response.status,
                    statusText: response.statusText,
                    headers: response.headers
                });
            } catch (e) {
                console.error("Error attempting to modify data in fetch():", e);
                const rawResponse = response.clone();
                const rawText = await rawResponse.text();
                console.error("Raw response body:", rawText);
            }
        }
        return response;
    };
})();