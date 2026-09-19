import client from '$lib/api.server';
import { m } from '$lib/paraglide/messages';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	const { data: history } = await client.GET('/api/stats/works/history', { fetch });

	return {
		history,
		head: { title: m.proud_bold_gecko_thrive() }
	};
};
