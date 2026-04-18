import client from '$lib/api';
import { m } from '$lib/paraglide/messages';
import { PathsApiWorkSearchGetParametersQueryOrderAnyOf0 } from '$lib/schema';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const batch_size = 20;
	const query = url.searchParams.get('query') ?? '';
	const tags = url.searchParams.get('tags') ?? '';

	const paramDir = url.searchParams.get('dir') === '-' ? '-' : '';
	const paramOrder = `${paramDir}${url.searchParams.get('order')}`;

	type Order = PathsApiWorkSearchGetParametersQueryOrderAnyOf0;
	const order: Order | null =
		paramOrder && Object.values(PathsApiWorkSearchGetParametersQueryOrderAnyOf0).includes(paramOrder as Order) ? (paramOrder as Order) : null;

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
