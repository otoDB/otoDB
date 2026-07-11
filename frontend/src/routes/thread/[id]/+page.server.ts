import { env } from '$env/dynamic/private';
import client, { rawClient } from '$lib/api.server';
import { apiFail } from '$lib/errors';
import { get_entity, markdownExcerpt, parseMentions, renderMarkdown } from '$lib/markdown';
import { m } from '$lib/paraglide/messages';
import { fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

// Get thread ID from /thread/{id}.{num} permalinks
const threadIdOf = (id: string) => id.split('.')[0];

export const load: PageServerLoad = async ({ params, fetch, url }) => {
	const batch_size = 25;
	// /thread/{id}.{num} is a permalink; render in place and highlight #num
	const dotted = params.id.includes('.');
	const [thread_id, numStr] = dotted ? params.id.split('.') : [params.id, null];
	const n = numStr !== null ? parseInt(numStr, 10) : NaN;
	const highlight_num = Number.isInteger(n) ? n : null;

	let page = Math.max(1, parseInt(url.searchParams.get('page') ?? '1', 10) || 1);
	if (highlight_num !== null) {
		// Page the post falls on, from its 1-based position (accurate across deleted
		// posts) divided by the client-owned page size
		const { data: pos } = await client.GET('/api/thread/position', {
			fetch,
			params: { query: { thread_id, num: highlight_num } }
		});
		page = Math.max(1, Math.ceil((pos ?? 1) / batch_size));
	}

	const [{ data: thread }, { data: posts }] = await Promise.all([
		client.GET('/api/thread/thread', {
			fetch,
			params: { query: { thread_id } }
		}),
		client.GET('/api/thread/posts', {
			fetch,
			params: {
				query: {
					thread_id,
					limit: batch_size,
					offset: (page - 1) * batch_size
				}
			}
		})
	]);

	const items = posts?.items ?? [];
	const permalinkedPost =
		(highlight_num !== null ? items.find((p) => p.num === highlight_num) : null) ?? items[0];

	return {
		thread,
		batch_size,
		posts: items,
		post_count: posts?.count ?? 0,
		head: {
			title: thread?.title,
			description: permalinkedPost ? markdownExcerpt(permalinkedPost.body) : null,
			ogType: 'article',
			breadcrumbs: [
				{ name: m.fine_late_chicken_quiz(), url: '/' },
				{
					name: m.just_salty_anaconda_nourish(),
					url: '/thread/overview'
				},
				{ name: thread?.title ?? '', url: `/thread/${thread_id}` }
			]
		}
	};
};

export const actions = {
	reply: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const body = data.get('body') as string;
		if (renderMarkdown(body).trim() === '') return fail(400);
		const { error, data: num } = await rawClient.POST('/api/thread/post', {
			fetch,
			params: {
				header: { 'otodb-internal-secret': env.INTERNAL_API_SECRET }
			},
			body: {
				thread_id: threadIdOf(params.id),
				body,
				mentioned_users: parseMentions(body)
			}
		});
		if (error) return apiFail(error);
		return num;
	},
	editPost: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const num = parseInt(data.get('num') as string, 10);
		const body = data.get('body') as string;
		if (renderMarkdown(body).trim() === '') return fail(400);
		const { error } = await rawClient.PUT('/api/thread/post', {
			fetch,
			params: {
				header: { 'otodb-internal-secret': env.INTERNAL_API_SECRET }
			},
			body: { thread_id: threadIdOf(params.id), num, body }
		});
		if (error) return apiFail(error);
	},
	editThread: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const title = data.get('title') as string;
		const post = data.get('post') as string;
		const entities_raw = data.get('entities') as string | null;
		const entities = (entities_raw ?? '')
			.split('\n')
			.map(get_entity)
			.filter((x) => !!x);

		if (renderMarkdown(post).trim() === '') return fail(400);

		// The opening-post edit form updates both thread metadata and post #1's body.
		const [{ error: threadError }, { error: postError }] = await Promise.all([
			rawClient.PUT('/api/thread/thread', {
				fetch,
				params: {
					header: { 'otodb-internal-secret': env.INTERNAL_API_SECRET }
				},
				body: { thread_id: threadIdOf(params.id), title, entities }
			}),
			rawClient.PUT('/api/thread/post', {
				fetch,
				params: {
					header: { 'otodb-internal-secret': env.INTERNAL_API_SECRET }
				},
				body: { thread_id: threadIdOf(params.id), num: 1, body: post }
			})
		]);
		if (threadError) return apiFail(threadError);
		if (postError) return apiFail(postError);
	}
} satisfies Actions;
