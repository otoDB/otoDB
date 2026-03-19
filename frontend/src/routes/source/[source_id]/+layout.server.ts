import type { LayoutServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import client from '$lib/api';
import { m } from '$lib/paraglide/messages';

export const load: LayoutServerLoad = async ({ params, fetch }) => {
	const sourceId = +params.source_id;
	if (isNaN(sourceId)) error(400, { message: 'Bad request' });

	const { data: source, error: e } = await client.GET('/api/source/source', {
		fetch,
		params: { query: { source_id: sourceId } }
	});

	if (e) error(404, { message: 'Source not found' });

	return {
		source,
		sourceId,
		links: [
			{
				pathname: `source/${sourceId}`,
				title: m.whole_male_cow_mix({ id: String(sourceId) })
			}
		],
		head: {
			title: source.title || m.whole_male_cow_mix({ id: String(sourceId) })
		}
	};
};
