import { env } from '$env/dynamic/private';
import client from '$lib/api.server';
import { languages } from '$lib/enums/language';
import { get_entity, renderMarkdown } from '$lib/markdown';
import { ModelsWithComments } from '$lib/schema';
import { fail } from '@sveltejs/kit';
import type { Actions, LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ fetch, params }) => {
	const { data: comments } = await client.GET('/api/comment/comments', {
		fetch,
		params: {
			query: {
				model: ModelsWithComments.post,
				pk: +params.post_id
			}
		}
	});

	return { comments };
};

export const actions = {
	edit: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const title = data.get('title') as string;
		const post = data.get('post') as string;
		const lang = data.get('lang') as keyof typeof languages;
		const entities_raw = data.get('entities') as string | null;
		const entities = (entities_raw ?? '')
			.split('\n')
			.map(get_entity)
			.filter((x) => !!x);

		if (renderMarkdown(post).trim() === '') return fail(400);

		await client.PUT('/api/post/post', {
			fetch,
			params: { header: { 'otodb-internal-secret': env.INTERNAL_API_SECRET } },
			body: {
				post_id: params.post_id,
				title,
				post,
				lang: languages[lang].id,
				entities
			}
		});
	}
} satisfies Actions;
