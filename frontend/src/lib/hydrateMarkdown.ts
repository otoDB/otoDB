import { rawClient } from '$lib/api';
import WorkTag from '$lib/WorkTag.svelte';
import { mount, unmount } from 'svelte';

/**
 * Hydrate otoDB markdown
 *
 *  - `<a data-worktag-slug="...">` (a tag link, SSR'd from `<otodb-worktag>`) is upgraded
 *    in place to a rich `WorkTag` element fetched via `/api/tag/tag`
 *  - `<a data-postref-num>` (a `t{thread}.{num}` reference) becomes
 *    "#num by <author>" (same thread) / "t{thread}.{num} by <author>" (cross-thread),
 *    with the author fetched via `/api/thread/post`
 */
export function hydrate(root: HTMLElement, thread?: string): () => void {
	const mounted: ReturnType<typeof mount>[] = [];
	const hidden: HTMLElement[] = [];
	let cancelled = false;

	for (const link of root.querySelectorAll<HTMLAnchorElement>('a[data-worktag-slug]')) {
		rawClient
			.GET('/api/tag/tag', {
				fetch,
				params: { query: { tag_slug: link.dataset.worktagSlug! } }
			})
			.then((r) => {
				const parent = link.parentElement;
				if (cancelled || !r.data || !parent) return;
				mounted.push(
					mount(WorkTag, {
						target: parent,
						anchor: link,
						props: { tag: r.data }
					})
				);
				link.style.display = 'none';
				hidden.push(link);
			});
	}

	for (const a of root.querySelectorAll<HTMLAnchorElement>('a[data-postref-num]')) {
		const t = a.dataset.postrefThread!;
		const n = a.dataset.postrefNum!;
		rawClient
			.GET('/api/thread/post', {
				fetch,
				params: { query: { thread_id: t, num: +n } }
			})
			.then((r) => {
				if (!cancelled && r.data)
					a.textContent = `${t === thread ? `#${n}` : `t${t}.${n}`} by ${r.data.user.username}`;
			});
	}

	return () => {
		cancelled = true;
		mounted.forEach((c) => unmount(c));
		hidden.forEach((l) => (l.style.display = ''));
	};
}
