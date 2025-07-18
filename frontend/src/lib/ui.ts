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

export const mermaid_BFS = (ns, ls, start: number, distance: number, allowed_types: boolean[]) => {
	const nodes = structuredClone(ns),
		links = structuredClone(ls);
	let queue = [start];
	for (let i = 0; i <= distance; i++) {
		const next_queue = [];
		for (const n of queue) {
			nodes.find((nn) => nn.id === n)!.visited = true;
			next_queue.push(
				...[
					...new Set(
						links
							.filter(
								(v) =>
									(v.A_id === n || v.B_id === n) &&
									(!nodes.find((w) => w.id === v.A_id).visited ||
										!nodes.find((w) => w.id === v.B_id).visited) &&
									allowed_types[v.relation]
							)
							.flatMap((v) => [v.A_id, v.B_id])
					)
				]
			);
		}
		queue = next_queue;
	}
	return [
		nodes.filter((v) => v.visited),
		links.filter(
			(v) =>
				nodes.find((w) => w.id === v.A_id).visited &&
				nodes.find((w) => w.id === v.B_id).visited
		)
	];
};
