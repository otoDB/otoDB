import client from '$lib/api';
import { m } from '$lib/paraglide/messages';
import type { PageServerLoad } from './$types';
import { postCategory } from '$lib/enums/PostCategory';
import { error, redirect } from '@sveltejs/kit';
import * as v from 'valibot';

const batch_size = 20;

type CategoryId = (typeof postCategory)[keyof typeof postCategory]['id'];
const validCategoryIds = Object.values(postCategory).map((c) => c.id) as CategoryId[];

const SearchParamsSchema = v.object({
	page: v.fallback(
		v.pipe(
			v.string(),
			v.transform((s) => parseInt(s, 10)),
			v.integer(),
			v.minValue(1)
		),
		1
	),
	query: v.optional(v.string(), ''),
	category: v.fallback(
		v.optional(
			v.pipe(
				v.string(),
				v.transform((s) => parseInt(s, 10) as CategoryId),
				v.check((n) => validCategoryIds.includes(n), 'Invalid category ID')
			)
		),
		undefined
	)
});

export const load: PageServerLoad = async ({ url, fetch }) => {
	const parsedParams = v.safeParse(SearchParamsSchema, Object.fromEntries(url.searchParams));
	if (!parsedParams.success) {
		redirect(302, '/post');
	}

	const { page, query, category } = parsedParams.output;
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
