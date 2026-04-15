import client from '$lib/api';
import { m } from '$lib/paraglide/messages';
import type { PageServerLoad } from './$types';
import { postCategory } from '$lib/enums/PostCategory';
import { error } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const batch_size = 20;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const query = url.searchParams.get('query') ?? '';

	const paramCategory = parseInt(url.searchParams.get('category') as string, 10);
	type Category = (typeof postCategory)[keyof typeof postCategory]['id'];
	const category =
		paramCategory &&
		!Object.values(postCategory)
			.map((v) => v.id)
			.includes(paramCategory as Category)
			? (paramCategory as Category)
			: null;

	const { data } = await client.GET('/api/post/search', {
		fetch,
		params: {
			query: {
				query,
				category,
				limit: batch_size,
				offset: (page - 1) * batch_size
			}
		}
	});

	if (!data) error(500, 'Failed to fetch search results.');

	return {
		query,
		category,
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
