import client from '$lib/api.server';
import { enumValues } from '$lib/enums';
import { m } from '$lib/paraglide/messages';
import { PostCategory } from '$lib/schema';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const batch_size = 20;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const query = url.searchParams.get('query') ?? '';

	const paramCategory = parseInt(url.searchParams.get('category') as string, 10);
	const category: PostCategory | null =
		paramCategory && (enumValues(PostCategory).includes(paramCategory) ? paramCategory : null);

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
