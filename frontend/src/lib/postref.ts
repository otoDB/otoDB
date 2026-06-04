/**
 * Delegated click handler for post references
 */
export function postRefNav(threadId: string) {
	return (node: HTMLElement) => {
		const onClick = (event: MouseEvent) => {
			if (
				event.defaultPrevented ||
				event.button !== 0 ||
				event.metaKey ||
				event.ctrlKey ||
				event.shiftKey ||
				event.altKey
			)
				return;
			const anchor = (event.target as HTMLElement).closest('a');
			const href = anchor?.getAttribute('href');
			const match = href?.match(/^\/thread\/(\d+)\.(\d+)$/);
			if (!match) return;
			const [, tid, num] = match;
			// Different thread -> let it navigate to the canonical permalink
			if (tid !== threadId) return;
			const target = document.getElementById(`p${num}`);
			// Not on this page -> let it navigate (load resolves the right page)
			if (!target) return;
			event.preventDefault();
			// Real fragment navigation (not pushState) so the :target highlight
			// updates and the browser scrolls to the post; all without a reload.
			location.hash = `p${num}`;
		};
		node.addEventListener('click', onClick);
		return () => node.removeEventListener('click', onClick);
	};
}
