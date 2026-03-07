import client from '$lib/api';
import { m } from '$lib/paraglide/messages';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const batch_size = 20;
	const query = url.searchParams.get('query') ?? '';
	const tags = url.searchParams.get('tags') ?? '';
	const order = url.searchParams.get('order'),
		dir = url.searchParams.get('dir');
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const queue = url.searchParams.get('queue') || null;
	const { data } = await client.GET('/api/work/search', {
		fetch,
		params: {
			query: {
				query,
				tags,
				limit: batch_size,
				offset: batch_size * (page - 1),
				order: order ? (dir === '-' ? '-' : '') + order : null,
				...(queue ? { queue } : {})
			}
		}
	});
	return {
		query: query,
		query_tags: tags,
		results: data,
		batch_size,
		order,
		dir,
		page,
		queue,
		head: {
			title: queue
				? 'Moderation Queue'
				: m.mild_loud_shad_enchant({
						type: m.mean_top_antelope_love(),
						name: m.grand_merry_fly_succeed()
					})
		}
	};
};
