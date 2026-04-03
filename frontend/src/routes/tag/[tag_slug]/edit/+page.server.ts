import client from '$lib/api';
import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { UserLevel } from '$lib/enums';
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
		parents: details?.paths[1][params.tag_slug]?.map((s) =>
			details?.paths[0].find((t) => t.slug === s)
		),
		details,
		connections,
		song_connections
	};
};

export const actions = {
	edit: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const category = data.get('category') as string,
			primary = data.get('primary') as string,
			parent_slugs = (data.get('parents') as string).split(/\s+/).filter((s) => s.length),
			deprecated = !!data.get('deprecated');

		const title = data.get('song_title') as string,
			author = data.get('song_author') as string,
			bpm = data.get('song_bpm') as string,
			variable_bpm = !!data.get('song_variable_bpm');

		const media_type = (data.getAll('media_type') as string[]).map((s) => +s);

		const song =
			+category === 2
				? {
						title,
						author,
						bpm: +bpm || null,
						variable_bpm
					}
				: null;

		const { error } = await client.PUT('/api/tag/tag', {
			fetch,
			params: {
				query: {
					tag_slug: params.tag_slug!
				}
			},
			body: {
				payload: {
					parent_slugs,
					category: +category,
					deprecated,
					media_type,
					primary: +primary === -1 ? null : +primary
				},
				song_payload: song
			}
		});

		if (error)
			return fail(400, {
				category,
				parent_slugs,
				deprecated,
				failed: true,
				primary: +primary
			});

		redirect(303, `/tag/${params.tag_slug}`);
	},
	wiki_page: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const pages: { lang: number; md: string }[] = JSON.parse(data.get('wiki_pages') as string);
		if (pages.length === 0) {
			redirect(303, `/tag/${params.tag_slug}`);
		}
		await client.POST('/api/tag/wiki_page', {
			fetch,
			params: { query: { tag_slug: params.tag_slug! } },
			body: pages
		});
		redirect(303, `/tag/${params.tag_slug}`);
	},
	connections: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const urls = (data.get('urls') as string) ?? '';

		await client.PUT('/api/tag/connection', {
			fetch,
			params: { query: { tag_slug: params.tag_slug!, urls } }
		});
		redirect(303, `/tag/${params.tag_slug}`);
	}
} satisfies Actions;
