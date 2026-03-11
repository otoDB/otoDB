import client from '$lib/api';
import { parseMentions, renderMarkdown } from '$lib/markdown';
import { fail } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import type { Actions } from './$types';

export const load: PageServerLoad = async ({ fetch, url }) => {
	const batch_size = 20;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const { data: comments } = await client.GET('/api/comment/recent', {
		params: { query: { limit: batch_size, offset: (page - 1) * batch_size } },
		fetch
	});
	return { comments, page, batch_size };
};

export const actions = {
	default: async ({ request, fetch }) => {
		const data = await request.formData();
		const model = data.get('model') as string,
			pk = parseInt(data.get('pk') as string, 10),
			comment_text = data.get('comment') as string,
			reply_to = parseInt(data.get('reply_to') as string, 10);
		if (renderMarkdown(comment_text).trim() === '') return fail(400);
		await client.POST('/api/comment/comment', {
			fetch,
			body: {
				model,
				pk,
				comment_text,
				parent_id: reply_to,
				mentioned_users: parseMentions(comment_text)
			},
			params: { query: { secret: '' } }
		});
	}
} satisfies Actions;
