import { languages, resolveLanguageKeyById } from '$lib/enums/language';
import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

const docs = import.meta.glob('../../../docs/**/*.md', { query: '?raw', import: 'default' });

export const load: PageServerLoad = async ({ params, url, locals }) => {
	const { slug } = params;
	const langParam = url.searchParams.get('lang');

	const prefix = `../../../docs/${slug}/`;
	const availableLangs = Object.keys(docs)
		.filter((k) => k.startsWith(prefix))
		.map((k) => k.slice(prefix.length).replace('.md', '') as keyof typeof languages);

	if (availableLangs.length === 0) {
		error(404, 'Doc not found');
	}

	const userLang = locals.user?.prefs.LANGUAGE
		? resolveLanguageKeyById(locals.user.prefs.LANGUAGE)
		: undefined;

	const defaultLang =
		(userLang && availableLangs.includes(userLang) ? userLang : null) ??
		(availableLangs.includes('en') ? 'en' : availableLangs[0]);

	if (!langParam || !availableLangs.includes(langParam as keyof typeof languages)) {
		redirect(302, `?lang=${defaultLang}`);
	}

	const lang = langParam as keyof typeof languages;
	const key = `${prefix}${lang}.md`;
	const content = (await docs[key]()) as string;

	return { content, lang, availableLangs };
};
