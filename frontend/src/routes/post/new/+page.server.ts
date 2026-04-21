import { env } from '$env/dynamic/private';
import client from '$lib/api.server';
import { get_entity, parseMentions, renderMarkdown } from '$lib/markdown';
import { m } from '$lib/paraglide/messages';
import { userLevelGuard } from '$lib/route_guard';
import { Levels, PostCategory, type components } from '$lib/schema';
import { asEnum } from '$lib/enums';
import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { getLanguageId, languages } from '$lib/enums/language';

export const load: PageServerLoad = ({ locals, url }) => {
	userLevelGuard(locals.user, Levels.Member);
	const paramCategory = parseInt(url.searchParams.get('category') as string, 10);
	const category = asEnum(PostCategory, paramCategory);
	const entity = url.searchParams.get('entity');
	const title = url.searchParams.get('title');
	return { category, entity, title, head: { title: m.antsy_aloof_horse_grace() } };
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
		type Category = components['schemas']['PostCategory'];
		const category = paramCategory as Category;

		const paramLang = data.get('lang') as string;
		const language = getLanguageId(
			paramLang as keyof typeof languages
		) as components['schemas']['LanguageTypes'];

		if (renderMarkdown(post).trim() === '') return fail(400);

		let post_id: number | null = null;
		try {
			({ data: post_id } = await client.POST('/api/post/post', {
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
			}));
		} catch {
			return fail(400);
		}
		redirect(303, `/post/${post_id}`);
	}
} satisfies Actions;
