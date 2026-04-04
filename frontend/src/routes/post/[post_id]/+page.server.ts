import client from '$lib/api';
import { Languages } from '$lib/enums';
import { get_entity, renderMarkdown } from '$lib/markdown';
import { fail } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import type { Actions } from './$types';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ fetch, params }) => {
	const { data: comments } = await client.GET('/api/comment/comments', {
		fetch,
		params: { query: { model: 'post', pk: +params.post_id } }
	});
	return { comments };
};

export const actions = {
	edit: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const title = data.get('title') as string;
		const post = data.get('post') as string;
		const lang = data.get('lang') as string;
		const entities_raw = data.get('entities') as string | null;
		const entities = (entities_raw ?? '')
			.split('\n')
			.map(get_entity)
			.filter((x) => x);

		if (renderMarkdown(post).trim() === '') return fail(400);
		await client.PUT('/api/post/post', {
			fetch,
			headers: { 'otodb-internal-secret': env.OTODB_INTERNAL_API_SECRET },
			body: {
				post_id: +params.post_id,
				title,
				post,
				lang: Languages[lang],
				entities
			}
		});
	},
	close: async ({ request, fetch, params }) => {
		await client.PUT('/api/post/close', {
			fetch,
			headers: { 'otodb-internal-secret': env.OTODB_INTERNAL_API_SECRET },
			body: {
				post_id: parseInt(params.post_id, 10)
			}
		});
	}
} satisfies Actions;
