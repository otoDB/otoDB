import client from '$lib/api';
import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { Languages } from '$lib/enums';

export const load: PageServerLoad = ({ url }) => {
	const category = url.searchParams.get('category');
	return { category };
};

export const actions = {
	default: async ({ request, fetch }) => {
		const data = await request.formData();
		const category = data.get('category') as string;
		const post = data.get('post') as string;
		const lang = data.get('lang') as string;
		const title = data.get('title') as string;
		const { data: r, error } = await client.POST('/api/post/post', {
			fetch,
			params: {
				query: {
					category: +category,
					post,
					lang: Languages[lang],
					title
				}
			}
		});
		if (error) fail(400);
		else redirect(303, `/post/${r}`);
	}
} satisfies Actions;
