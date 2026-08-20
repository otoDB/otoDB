import client from '$lib/api';
import { buildGraphView, type GraphOptions, type RelationData } from '$lib/graph';

/**
 * Stands in for `$lib/graph.remote`. Storybook has no SvelteKit server behind it,
 * so the query runs in the browser instead and reads its relations through MSW.
 */
export const graphView = async (options: GraphOptions) => {
	const { data } =
		options.type === 'work'
			? await client.GET('/api/work/relations', {
					fetch,
					params: { query: { work_id: options.id } }
				})
			: await client.GET('/api/tag/song_relations', {
					fetch,
					params: { query: { song_id: options.id } }
				});

	return buildGraphView(options, (data as RelationData | undefined) ?? [[], []]);
};
