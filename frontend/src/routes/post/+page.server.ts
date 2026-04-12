import client from '$lib/api';
import { m } from '$lib/paraglide/messages';
import type { PageServerLoad } from './$types';
import { postCategory } from '$lib/enums/PostCategory';
import { error } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const batch_size = 20;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const query = url.searchParams.get('query') ?? '';

	const paramCategory = url.searchParams.get('category');
	const category = paramCategory ? parseInt(paramCategory, 10) : -1;

	const { data } = await client.GET('/api/post/search', {
		fetch,
		params: {
			query: {
				query,
				category: (() => {
					switch (category) {
						// TODO: later rewrite e.g. `PostCategory.BUG_REPORT.id`.
						case postCategory.ANNOUNCEMENT.id:
						case postCategory.FEATURE_REQUEST.id:
						case postCategory.BUG_REPORT.id:
						case postCategory.GARDENING.id:
						case postCategory.GENERAL.id:
							return category;
						default:
							return null;
					}
				})(),
				limit: batch_size,
				offset: (page - 1) * batch_size
			}
		}
	});

	if (!data) error(500, 'Failed to fetch search results.');

	return {
		query,
		category: ((): (typeof postCategory)[keyof typeof postCategory]['id'] | -1 => {
			switch (category) {
				case postCategory.ANNOUNCEMENT.id:
				case postCategory.FEATURE_REQUEST.id:
				case postCategory.BUG_REPORT.id:
				case postCategory.GARDENING.id:
				case postCategory.GENERAL.id:
					return category;
				default:
					return -1;
			}
		})(),
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
