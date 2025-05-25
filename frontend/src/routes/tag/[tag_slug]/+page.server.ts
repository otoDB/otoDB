import client from '$lib/api';
import { commentClient } from '$lib/api';
import { SongRelationTypes } from '$lib/enums';
import type { PageServerLoad } from './$types';
import { D2 } from '@terrastruct/d2';

const d2 = new D2();

export const load: PageServerLoad = async ({ params, fetch, parent }) => {
	const data = await parent();

	const batch_size = 20;

	const [{ data: details }, { data: works }, { data: connections }] = await Promise.all([
		client.GET('/api/tag/details', {
			fetch,
			params: {
				query: {
					tag_slug: params.tag_slug
				}
			}
		}),
		client.GET('/api/tag/works', {
			fetch,
			params: {
				query: {
					tag_slug: params.tag_slug,
					limit: batch_size,
					offset: 0
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

	const comments = await commentClient.GET('tagwork', data.tag.id, fetch);

	const song_relation_svg = data.song_relations
		? await (async () => {
				const [relations, songs] = data.song_relations!;
				if (relations.length === 0) return null;

				const source = `direction: right
        ${songs
			.map(
				(s) => `${s.id}: ${s.title} {
                link: ${`/tag/${s.work_tag}`}
                ${+data.tag.song?.id === s.id ? 'style: { font-color: red }' : ''}
            }`
			)
			.join('\n')}
        ${relations
			.map((r) => `${r.A_id} -> ${r.B_id}: ${SongRelationTypes[r.relation]()}`)
			.join('\n')}`;

				const result = await d2.compile(source);
				let svg = await d2.render(result.diagram, {
					...result.renderOptions,
					darkThemeID: 200,
					noXMLTag: true
				});

				svg = svg.replace(/\.appendix-icon {.*?}/gs, '.appendix-icon{display:none;}');

				return svg;
			})()
		: null;

	const song_connections = data.tag.song
		? (
				await client.GET('/api/tag/song_connection', {
					fetch,
					params: { query: { song_id: data.tag.song.id } }
				})
			).data
		: null;

	return {
		...details,
		works,
		comments,
		song_relation_svg,
		batch_size,
		connections,
		song_connections
	};
};
