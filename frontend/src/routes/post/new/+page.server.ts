import client from '$lib/api';
import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { Languages } from '$lib/enums';
import userLevelGuard from '$lib/route_guard';
import { m } from '$lib/paraglide/messages';
import { env } from '$env/dynamic/private';
import { get_entity, parseMentions, renderMarkdown } from '$lib/markdown';

export const load: PageServerLoad = ({ locals, url }) => {
	userLevelGuard(locals.user);
	const category = url.searchParams.get('category');
	const entity = url.searchParams.get('entity');
	return { category, entity, head: { title: m.antsy_aloof_horse_grace() } };
};

export const actions = {
	default: async ({ request, fetch }) => {
		const data = await request.formData();
		const category = data.get('category') as string;
		const post = data.get('post') as string;
		const lang = data.get('lang') as string;
		const title = data.get('title') as string;
		const entities_raw = data.get('entities') as string | null;
		const entities = (entities_raw ?? '')
			.split('\n')
			.map(get_entity)
			.filter((x) => x);

		if (renderMarkdown(post).trim() === '') return fail(400);
		const { data: r, error } = await client.POST('/api/post/post', {
			fetch,
			params: { header: { 'otodb-internal-secret': env.OTODB_INTERNAL_API_SECRET } },
			body: {
				category: +category,
				post,
				lang: Languages[lang],
				title,
				target_users: parseMentions(post),
				entities
			}
		});
		if (error) return fail(400);
		else redirect(303, `/post/${r}`);
	}
} satisfies Actions;
