import client from '$lib/api';
import { m } from '$lib/paraglide/messages';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const batch_size = 20;
	const query = url.searchParams.get('query') ?? '';
	const author = url.searchParams.get('author') ?? '';
	const tags = url.searchParams.get('tags') ?? '';

	const bpm_min = url.searchParams.get('bpm_min') ?? '';
	const bpm_max = url.searchParams.get('bpm_max') ?? '';
	const bpm_range: [number, number] | null = bpm_min && bpm_max ? [+bpm_min, +bpm_max] : null;

	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const { data } = await client.GET('/api/tag/song_search', {
		fetch,
		params: {
			query: {
				query,
				tags,
				author,
				limit: batch_size,
				offset: (page - 1) * batch_size,
				bpm_range
			}
		}
	});
	return {
		query: query,
		query_tags: tags,
		results: data,
		batch_size,
		bpm_range,
		author,
		page,
		head: {
			title: m.mild_loud_shad_enchant({
				type: m.mean_top_antelope_love(),
				name: m.grand_nice_pony_belong()
			})
		}
	};
};
