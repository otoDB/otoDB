import client from '$lib/api';
import { m } from '$lib/paraglide/messages';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const batch_size = 20;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const query = url.searchParams.get('query') ?? '';
	const category = parseInt(url.searchParams.get('category') ?? '');
	const { data } = await client.GET('/api/post/search', {
		fetch,
		params: {
			query: {
				query,
				category: !isNaN(category) && category >= 0 ? category : undefined,
				limit: batch_size,
				offset: (page - 1) * batch_size
			}
		}
	});
	return {
		query,
		category: isNaN(category) ? -1 : category,
		results: data,
		batch_size,
		page,
		head: {
			title: m.mild_loud_shad_enchant({
				type: m.mean_top_antelope_love(),
				name: m.just_salty_anaconda_nourish()
			})
		}
	};
};
