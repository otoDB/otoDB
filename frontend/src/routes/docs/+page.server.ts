import { languages } from '$lib/enums/language';
import type { PageServerLoad } from './$types';

const docs = import.meta.glob('../../docs/**/*.md', { query: '?raw', import: 'default' });

export const load: PageServerLoad = async () => {
	const slugMap = new Map<string, (keyof typeof languages)[]>();

	for (const key of Object.keys(docs)) {
		const match = key.match(/^\.\.\/\.\.\/docs\/([^/]+)\/([^/]+)\.md$/);
		if (!match) continue;
		const [, slug, lang] = match;
		if (!slugMap.has(slug)) slugMap.set(slug, []);
		slugMap.get(slug)!.push(lang as keyof typeof languages);
	}

	const entries = Array.from(slugMap.entries()).map(([slug, langs]) => ({ slug, langs }));

	return { entries };
};
