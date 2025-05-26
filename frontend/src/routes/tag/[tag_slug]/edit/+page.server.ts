import client from '$lib/api';
import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { Languages, UserLevel } from '$lib/enums';
import userLevelGuard from '$lib/route_guard';

export const load: PageServerLoad = async ({ params, fetch, locals, url, parent }) => {
	userLevelGuard(locals.user, UserLevel.MEMBER, url.pathname);

	const [{ data: wiki_page }, { data: details }, { data: connections }] = await Promise.all([
		client.GET('/api/tag/wiki_page', {
			fetch,
			params: {
				query: {
					tag_slug: params.tag_slug
				}
			}
		}),
		client.GET('/api/tag/details', {
			fetch,
			params: {
				query: {
					tag_slug: params.tag_slug
				}
			}
		}),
		client.GET('/api/tag/connection', {
			fetch,
			params: {
				query: {
					tag_slug: params.tag_slug
				}
			}
		})
	]);

	const p = await parent();
	// FIXME This is kind of waterfall but whatever...
	const song_connections = p.tag.song
		? (
				await client.GET('/api/tag/song_connection', {
					fetch,
					params: { query: { song_id: p.tag.song.id } }
				})
			).data
		: null;

	return {
		wiki_page,
		parent_slug: details?.tree[0]?.slug,
		details,
		connections,
		song_connections
	};
};

export const actions = {
	edit: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const category = data.get('category') as string,
			parent_slug = data.get('parent') as string;

		if (+category == 2) {
			const title = data.get('song_title') as string,
				author = data.get('song_author') as string,
				bpm = data.get('song_bpm') as string;
			const { error } = await client.POST('/api/tag/song', {
				fetch,
				params: {
					query: {
						tag_slug: params.tag_slug!
					}
				},
				body: {
					title,
					author,
					bpm: +bpm
				}
			});
			if (error) return fail(400, { category, parent_slug, failed: true });
		}

		const { error } = await client.PUT('/api/tag/tag', {
			fetch,
			params: {
				query: {
					tag_slug: params.tag_slug!
				}
			},
			body: {
				category: +category,
				parent_slug
			}
		});

		if (error) return fail(400, { category, parent_slug, failed: true });

		redirect(303, `/tag/${params.tag_slug}`);
	},
	wiki_page: async ({ request, fetch, params }) => {
		const data = await request.formData();
		await client.POST('/api/tag/wiki_page', {
			fetch,
			params: {
				query: {
					tag_slug: params.tag_slug!,
					md: data.get('md') as string,
					lang: Languages[data.get('lang')]
				}
			}
		});
		redirect(303, `/tag/${params.tag_slug}`);
	}
} satisfies Actions;
