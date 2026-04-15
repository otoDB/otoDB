import { env } from '$env/dynamic/private';
import client from '$lib/api';
import { get_entity, parseMentions, renderMarkdown } from '$lib/markdown';
import { m } from '$lib/paraglide/messages';
import { userLevelGuard } from '$lib/route_guard';
import type { components } from '$lib/schema';
import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { getLanguageId, languages } from '$lib/enums/Languages';

export const load: PageServerLoad = ({ locals, url }) => {
	userLevelGuard(locals.user, 'MEMBER');
	const category = url.searchParams.get('category');
	const entity = url.searchParams.get('entity');
	return { category, entity, head: { title: m.antsy_aloof_horse_grace() } };
};

export const actions = {
	default: async ({ request, fetch }) => {
		const data = await request.formData();
		const post = data.get('post') as string;
		const title = data.get('title') as string;
		const entities_raw = data.get('entities') as string | null;
		const entities = (entities_raw ?? '')
			.split('\n')
			.map(get_entity)
			.filter((x) => !!x);

		const paramCategory = parseInt(data.get('category') as string, 10);
		// TODO: Remove when error forwarding is complete
		if (![0, 1, 2, 3, 4].includes(paramCategory)) return fail(400);
		type Category = components['schemas']['PostCategory'];
		const category = paramCategory as Category;

		const paramLang = data.get('lang') as string;
		const language = getLanguageId(
			paramLang as keyof typeof languages
		) as components['schemas']['LanguageTypes'];

		if (renderMarkdown(post).trim() === '') return fail(400);

		const { data: r, error } = await client.POST('/api/post/post', {
			fetch,
			params: { header: { 'otodb-internal-secret': env.OTODB_INTERNAL_API_SECRET } },
			body: {
				category: category,
				post,
				lang: language,
				title,
				target_users: parseMentions(post),
				entities
			}
		});
		if (error) return fail(400);
		else redirect(303, `/post/${r}`);
	}
} satisfies Actions;
