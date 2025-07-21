import client from '$lib/api';
import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import {
	Languages,
	ProfileConnectionParsers,
	SongConnectionParsers,
	SourceConnectionParsers,
	TagWorkConnectionParsers,
	UserLevel
} from '$lib/enums';
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
			parent_slug = data.get('parent') as string,
			deprecated = !!data.get('deprecated');

		const title = data.get('song_title') as string,
			author = data.get('song_author') as string,
			bpm = data.get('song_bpm') as string,
			variable_bpm = !!data.get('song_variable_bpm');

		const song =
			+category === 2
				? {
						title,
						author,
						bpm: +bpm,
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
					category: +category,
					parent_slug,
					deprecated
				},
				song_payload: song
			}
		});

		if (error) return fail(400, { category, parent_slug, deprecated, failed: true });

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
					lang: Languages[data.get('lang') as string]
				}
			}
		});
		redirect(303, `/tag/${params.tag_slug}`);
	},
	connections: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const { data: tag, error: e } = await client.GET('/api/tag/tag', {
			params: {
				query: {
					tag_slug: params.tag_slug!
				}
			},
			fetch
		});
		if (e) fail(400);

		const urls = (data.get('urls') as string) ?? '';
		const category = tag.category;

		let parsers = Object.entries(TagWorkConnectionParsers);
		const n_general_parsers = parsers.length;
		if (category === 2) parsers = [...parsers, ...Object.entries(SongConnectionParsers)];
		else if (category === 3) parsers = [...parsers, ...Object.entries(SourceConnectionParsers)];
		else if (category === 4)
			parsers = [...parsers, ...Array.from(ProfileConnectionParsers.entries()).slice(1)];
		const connections = [...new Set(urls.split('\n'))]
			.filter((x) => x.trim() !== '')
			.map(
				(url) =>
					parsers
						.map((p, i) => ({
							site: +p[0],
							content_id: p[1](url),
							t: i >= n_general_parsers ? category : 0
						}))
						.filter((v) => !!v.content_id)
						.at(-1) // !!! Attention here
			)
			.filter((v) => !!v);

		const pings = [
			client.PUT('/api/tag/connection', {
				fetch,
				body: connections
					.filter((c) => c.t === 0)
					.map(({ content_id, site }) => ({ content_id: content_id, site })),
				params: { query: { tag_slug: params.tag_slug!, t: 0 } }
			})
		];
		if (category >= 2 && category <= 4)
			pings.push(
				client.PUT('/api/tag/connection', {
					fetch,
					body: connections
						.filter((c) => c.t === category)
						.map(({ content_id, site }) => ({ content_id, site })),
					params: { query: { tag_slug: params.tag_slug!, t: category } }
				})
			);
		await Promise.all(pings);
		redirect(303, `/tag/${params.tag_slug}`);
	}
} satisfies Actions;
