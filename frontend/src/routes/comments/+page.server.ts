import client from '$lib/api';
import { parseMentions, renderMarkdown } from '$lib/markdown';
import { fail } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import type { PageServerLoad } from './$types';
import type { Actions } from './$types';
import { m } from '$lib/paraglide/messages';
import type { components } from '$lib/schema';

export const load: PageServerLoad = async ({ fetch, url }) => {
	const batch_size = 20;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const { data: comments } = await client.GET('/api/comment/recent', {
		params: { query: { limit: batch_size, offset: (page - 1) * batch_size } },
		fetch
	});
	return {
		comments,
		page,
		batch_size,
		head: { title: m.same_broad_haddock_pinch() }
	};
};

export const actions = {
	create: async ({ request, fetch }) => {
		const data = await request.formData();

		const model = data.get('model') as components['schemas']['CommentInSchema']['model'];
		const pk = parseInt(data.get('pk') as string, 10);
		const comment_text = data.get('comment') as string;
		const reply_to = parseInt(data.get('reply_to') as string, 10);
		if (renderMarkdown(comment_text).trim() === '') return fail(400);

		await client.POST('/api/comment/comment', {
			fetch,
			params: {
				header: {
					'otodb-internal-secret': env.OTODB_INTERNAL_API_SECRET
				}
			},
			body: {
				model,
				pk,
				comment_text,
				parent_id: reply_to,
				mentioned_users: parseMentions(comment_text)
			}
		});
	},
	edit: async ({ request, fetch }) => {
		const data = await request.formData();
		const comment_id = parseInt(data.get('comment_id') as string, 10),
			comment_text = data.get('comment') as string;
		if (renderMarkdown(comment_text).trim() === '') return fail(400);

		await client.PUT('/api/comment/comment', {
			fetch,
			params: { header: { 'otodb-internal-secret': env.OTODB_INTERNAL_API_SECRET } },
			body: { comment_id, comment_text }
		});
	}
} satisfies Actions;
