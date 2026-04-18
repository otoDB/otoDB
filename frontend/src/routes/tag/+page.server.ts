import client from '$lib/api';
import { m } from '$lib/paraglide/messages';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const batch_size = 20;
	const query = url.searchParams.get('query') ?? '';
	const category = parseInt(url.searchParams.get('category') ?? '-1', 10);
	const media_type = (url.searchParams.getAll('media_type') as string[]).map((s) => +s);
	const order = url.searchParams.get('order') ?? 'newest';
	const deprecated_only = url.searchParams.get('deprecated_only') === 'on';
	const hide_orphans_vals = url.searchParams.getAll('hide_orphans');
	const hide_orphans = hide_orphans_vals.length === 0 || hide_orphans_vals.includes('on');
	const wiki_lang = (url.searchParams.getAll('wiki_lang') as string[]).map((s) => +s);
	const wiki_lang_missing = (url.searchParams.getAll('wiki_lang_missing') as string[]).map(
		(s) => +s
	);
	const lang_pref = (url.searchParams.getAll('lang_pref') as string[]).map((s) => +s);
	const lang_pref_missing = (url.searchParams.getAll('lang_pref_missing') as string[]).map(
		(s) => +s
	);
	const has_connections = url.searchParams.get('has_connections');
	const page = parseInt(url.searchParams.get('page') ?? '1', 10) || 1;

	const { data } = await client.GET('/api/tag/search', {
		fetch,
		params: {
			query: {
				query,
				limit: batch_size,
				offset: batch_size * (page - 1),
				category: category === -1 ? null : category,
				media_type,
				order,
				deprecated_only,
				hide_orphans: hide_orphans,
				wiki_lang,
				wiki_lang_missing,
				lang_pref,
				lang_pref_missing,
				has_connections: has_connections ? has_connections === 'true' : undefined
			}
		}
	});

	return {
		query,
		category,
		results: data,
		batch_size,
		media_type,
		order,
		deprecated_only,
		hide_orphans: hide_orphans,
		wiki_lang,
		wiki_lang_missing,
		lang_pref,
		lang_pref_missing,
		has_connections,
		page,
		head: {
			title: m.mild_loud_shad_enchant({
				type: m.mean_top_antelope_love(),
				name: m.empty_legal_chicken_taste()
			})
		}
	};
};
