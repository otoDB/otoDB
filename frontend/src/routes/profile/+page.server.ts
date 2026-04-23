import client from '$lib/api.server';
import { m } from '$lib/paraglide/messages';
import { Levels, PathsApiProfileSearchGetParametersQueryOrder as OrderEnum } from '$lib/schema';
import { asEnum } from '$lib/enums';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const batch_size = 30;
	const username = url.searchParams.get('username') ?? '';
	const levelParam = url.searchParams.get('level');
	const level =
		levelParam !== null && levelParam !== '' ? asEnum(Levels, Number(levelParam)) : null;
	const orderParam = url.searchParams.get('order') ?? OrderEnum.ValueMinusdate_created;
	const order = asEnum(OrderEnum, orderParam) ?? OrderEnum.ValueMinusdate_created;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;

	const { data } = await client.GET('/api/profile/search', {
		fetch,
		params: {
			query: {
				username: username || null,
				level,
				order,
				limit: batch_size,
				offset: (page - 1) * batch_size
			}
		}
	});

	return {
		username,
		level,
		order,
		results: data,
		batch_size,
		page,
		head: {
			title: m.bright_nimble_eagle_glide()
		}
	};
};
