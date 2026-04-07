import { browser } from '$app/environment';
import { env } from '$env/dynamic/public';
import type { Cookies } from '@sveltejs/kit';
import type { CookieSerializeOptions } from 'cookie';
import createClient from 'openapi-fetch';
import setCookie from 'set-cookie-parser';
import { languages } from './enums/Languages';
import { m } from './paraglide/messages';
import { getLocale } from './paraglide/runtime';
import type { components, paths } from './schema';

const backend = browser
	? (env.PUBLIC_BACKEND_URL_EXTERNAL ?? '')
	: (env.PUBLIC_BACKEND_URL_INTERNAL ?? env.PUBLIC_BACKEND_URL_EXTERNAL ?? '');

const client = createClient<paths>({ baseUrl: backend, credentials: 'include' });
export default client;

export const setToken = (token: string) => {
	if (browser)
		client.use({
			async onRequest({ request }) {
				request.headers.set('X-CSRFToken', token);
				return request;
			}
		});
};

export const forwardCookies = (cookies: Cookies, response: Response) => {
	for (const { name, value, expires, maxAge, sameSite } of setCookie.parse(
		response.headers.getSetCookie()
	))
		cookies.set(name, value, {
			path: '/',
			expires,
			maxAge,
			sameSite: sameSite as CookieSerializeOptions['sameSite'] // MEMO: 流石にそうだとは思うが，変だったら修正すること．
		});
};

export type CommentModels =
	| 'mediawork'
	| 'account'
	| 'pool'
	| 'tagwork'
	| 'tagsong'
	| 'post'
	| 'bulkrequest';

export const makeCommentTree = (comments: components['schemas']['CommentSchema'][]) => {
	if (comments.length === 0) return [];
	else {
		const keep = Object.entries(
			Object.groupBy(
				comments.map(({ submit_date, ...rest }) => ({
					time: new Date(submit_date),
					...rest
				})),
				(e) => e.level
			)
		)
			.toSorted((a, b) => b[0] - a[0])
			.map((v) => v[1]);
		keep.slice(1).forEach(
			(_, i) =>
				(keep[i + 1] = keep[i + 1].map((c) => ({
					...c,
					children: keep[i]?.filter((e) => e.parent_id === c.id) ?? []
				})))
		);
		return keep.at(-1);
	}
};

export const getTagDisplayName = (tag: {
	name: string;
	lang_prefs: { lang: number; tag: string }[];
}) => tag.lang_prefs.find(({ lang }) => lang === languages[getLocale()].id)?.tag ?? tag.name;

export const getTagDisplaySlug = (tag: {
	slug: string;
	lang_prefs: { lang: number; slug: string }[];
}) => tag.lang_prefs.find(({ lang }) => lang === languages[getLocale()].id)?.slug ?? tag.slug;

export function getDisplayText(
	value: string | null | undefined,
	placeholder: string | undefined = undefined
): string {
	return value ?? placeholder ?? m.lost_game_mink_loop();
}
