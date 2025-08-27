import client from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const batch_size = 20;
	const query = url.searchParams.get('query') ?? '';
	const author = url.searchParams.get('author') ?? '';
	const tags = url.searchParams.get('tags') ?? '';
	const bpm_min = url.searchParams.get('bpm_min') ?? '';
	const bpm_max = url.searchParams.get('bpm_max') ?? '';
	const bpm_range = bpm_min && bpm_max ? [+bpm_min, +bpm_max] : null;
	const { data } = await client.GET('/api/tag/song_search', {
		fetch,
		params: {
			query: {
				query,
				tags,
				author,
				limit: batch_size,
				offset: 0,
				bpm_range
			}
		}
	});
	return {
		query: query,
		query_tags: tags,
		results: data,
		batch_size
	};
};
