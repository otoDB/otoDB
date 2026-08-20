import { getRequestEvent, query } from '$app/server';
import client from '$lib/api.server';
import { buildGraphView, type GraphOptions, type GraphType, type RelationData } from '$lib/graph';

const relations = query('unchecked', async ({ type, id }: { type: GraphType; id: string }) => {
	const { fetch } = getRequestEvent();

	const { data } =
		type === 'work'
			? await client.GET('/api/work/relations', { fetch, params: { query: { work_id: id } } })
			: await client.GET('/api/tag/song_relations', { fetch, params: { query: { song_id: id } } });

	return data as RelationData;
});

export const graphView = query('unchecked', async (options: GraphOptions) => {
	const { type, id } = options;

	return buildGraphView(options, await relations({ type, id }));
});
