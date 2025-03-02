export const debounce = (callback: Function, wait = 300) => {
    let timeout: ReturnType<typeof setTimeout> | null = null;
    return (...args: any[]) => {
        if (timeout)
            clearTimeout(timeout);
        timeout = setTimeout(() => callback(...args), wait);
    };
};
