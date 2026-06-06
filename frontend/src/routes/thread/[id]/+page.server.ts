import { env } from '$env/dynamic/private';
import client from '$lib/api.server';
import { get_entity, parseMentions, renderMarkdown } from '$lib/markdown';
import { m } from '$lib/paraglide/messages';
import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

const PAGE_SIZE = 25;
const secret = () => ({
	header: { 'otodb-internal-secret': env.INTERNAL_API_SECRET }
});

export const load: PageServerLoad = async ({ params, fetch, url }) => {
	// Dot-form permalink (/thread/{id}.{num}) -> resolve to the page + anchor.
	if (params.id.includes('.')) {
		const [tid, num] = params.id.split('.');
		const { data: page } = await client.GET('/api/thread/locate', {
			fetch,
			params: { query: { thread_id: tid, num: parseInt(num, 10) } }
		});
		redirect(307, `/thread/${tid}?page=${page ?? 1}#p${num}`);
	}

	const thread_id = params.id;
	const page = parseInt(url.searchParams.get('page') ?? '1', 10) || 1;

	const [{ data: thread }, { data: posts }] = await Promise.all([
		client.GET('/api/thread/thread', {
			fetch,
			params: { query: { thread_id } }
		}),
		client.GET('/api/thread/posts', {
			fetch,
			params: { query: { thread_id, page } }
		})
	]);

	return {
		thread,
		thread_id,
		page,
		batch_size: PAGE_SIZE,
		posts: posts?.posts ?? [],
		post_count: posts?.count ?? 0,
		ref_authors: posts?.ref_authors ?? {},
		head: {
			title: thread?.title,
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
		await client.POST('/api/thread/post', {
			fetch,
			params: secret(),
			body: {
				thread_id: params.id,
				body,
				mentioned_users: parseMentions(body)
			}
		});
	},
	editPost: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const num = parseInt(data.get('num') as string, 10);
		const body = data.get('body') as string;
		if (renderMarkdown(body).trim() === '') return fail(400);
		await client.PUT('/api/thread/post', {
			fetch,
			params: secret(),
			body: { thread_id: params.id, num, body }
		});
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
		await client.PUT('/api/thread/thread', {
			fetch,
			params: secret(),
			body: { thread_id: params.id, title, entities }
		});
		await client.PUT('/api/thread/post', {
			fetch,
			params: secret(),
			body: { thread_id: params.id, num: 1, body: post }
		});
	},
} satisfies Actions;
