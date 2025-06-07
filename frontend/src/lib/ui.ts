// eslint-disable-next-line @typescript-eslint/no-unsafe-function-type
export const debounce = (callback: Function, wait = 300) => {
	let timeout: ReturnType<typeof setTimeout> | null = null;
	return (...args: any[]) => {
		if (timeout) clearTimeout(timeout);
		timeout = setTimeout(() => callback(...args), wait);
	};
};

export const once = (fn) => {
    return function (event) {
        if (fn) fn.call(this, event);
        fn = null;
    };
};

export const clickOutside = (node: HTMLElement) => {
	const handleClick = (event: MouseEvent) => {
		if (!node.contains(event.target as Node)) {
			node.dispatchEvent(new CustomEvent('Outclick'));
		}
	};

	document.addEventListener('click', handleClick, true);

	return {
		destroy() {
			document.removeEventListener('click', handleClick, true);
		}
	};
};

export const isSVO = (lang: 'en' | 'zh-cn' | 'ko' | 'ja') => lang === 'en' || lang === 'zh-cn';
export const isSOV = (lang: 'en' | 'zh-cn' | 'ko' | 'ja') => lang === 'ko' || lang === 'ja';
