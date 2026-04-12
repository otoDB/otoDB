import client from '$lib/api';
import { m } from '$lib/paraglide/messages';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const batch_size = 20;
	const query = url.searchParams.get('query') ?? '';
	const tags = url.searchParams.get('tags') ?? '';

	const paramOrder = url.searchParams.get('order');
	const paramDir = url.searchParams.get('dir');

	const order = (() => {
		switch (paramOrder) {
			case 'id':
			case 'pub':
				return `${paramDir === '-' ? '-' : ''}${paramOrder}` as const;
			default:
				return null;
		}
	})();

	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const { data } = await client.GET('/api/work/search', {
		fetch,
		params: {
			query: {
				query,
				tags,
				limit: batch_size,
				offset: batch_size * (page - 1),
				order: order
			}
		}
	});

	// TODO: need payload validation
	if (!data) error(500, 'Failed to fetch search results.');

	return {
		query: query,
		query_tags: tags,
		results: data,
		batch_size,
		order: order,
		dir: paramDir,
		page,
		head: {
			title: m.mild_loud_shad_enchant({
				type: m.mean_top_antelope_love(),
				name: m.grand_merry_fly_succeed()
			})
		}
	};
};
