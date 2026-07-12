import client from '$lib/api.server';
import { m } from '$lib/paraglide/messages';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const batch_size = 20;
	const query = url.searchParams.get('query') ?? '';
	const category = parseInt(url.searchParams.get('category') ?? '-1', 10);
	const { data } = await client.GET('/api/tag/song_tag_search', {
		fetch,
		params: {
			query: {
				query: query,
				limit: batch_size,
				offset: 0,
				category: category === -1 ? null : category
			}
		}
	});
	return {
		query,
		category,
		results: data,
		batch_size,
		head: {
			title: m.mild_loud_shad_enchant({
				type: m.mean_top_antelope_love(),
				name: m.dull_plain_angelfish_cuddle()
			})
		}
	};
};
