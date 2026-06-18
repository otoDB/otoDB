import client from '$lib/api.server';
import { m } from '$lib/paraglide/messages';
import type { HistoricalEntities, Route } from '$lib/schema';
import type { PageServerLoad } from './$types';

const str = (sp: URLSearchParams, k: string) => sp.get(k) || undefined;
const bool = (sp: URLSearchParams, k: string) => {
	const v = sp.get(k);
	if (v === 'true' || v === 'on') return true;
	if (v === 'false') return false;
	return undefined;
};
const slugs = (sp: URLSearchParams, k: string) => {
	const v = sp
		.get(k)
		?.split(/[\s,]+/)
		.filter(Boolean);
	return v?.length ? v : undefined;
};

export const load: PageServerLoad = async ({ url, fetch }) => {
	const batch_size = 20;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const sp = url.searchParams;

	const routes = sp.getAll('routes').map(Number).filter(Number.isFinite) as Route[];
	const filters = {
		username: str(sp, 'username'),
		routes: routes.length ? routes : undefined,
		entity: str(sp, 'entity') as HistoricalEntities | undefined,
		reason: str(sp, 'reason'),
		since: str(sp, 'since'),
		until: str(sp, 'until'),
		is_new: bool(sp, 'is_new'),
		is_deleted: bool(sp, 'is_deleted'),
		added_tags: slugs(sp, 'added_tags'),
		removed_tags: slugs(sp, 'removed_tags'),
		changed_tags: slugs(sp, 'changed_tags'),
		changed_field: str(sp, 'changed_field'),
		changed_value: str(sp, 'changed_value'),
		changed_from: str(sp, 'changed_from')
	};

	const { data } = await client.GET('/api/history/search', {
		fetch,
		params: {
			query: { ...filters, limit: batch_size, offset: batch_size * (page - 1) }
		}
	});

	return {
		results: data,
		filters,
		batch_size,
		page,
		head: { title: m.giant_away_scallop_hike() }
	};
};
