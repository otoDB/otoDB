import createClient from 'openapi-fetch';
import type { components, paths } from './schema';
import { env } from '$env/dynamic/public';
import { browser } from '$app/environment';
import type { Cookies } from '@sveltejs/kit';
import setCookie from 'set-cookie-parser';
import { Languages } from './enums';
import { getLocale } from './paraglide/runtime';
import { m } from './paraglide/messages';

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
		cookies.set(name, value, { path: '/', expires, maxAge, sameSite });
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

export const getTagDisplayName = (tag) =>
	tag.lang_prefs.find(({ lang }) => lang === Languages[getLocale()])?.tag ?? tag.name;

export const getTagDisplaySlug = (tag) =>
	tag.lang_prefs.find(({ lang }) => lang === Languages[getLocale()])?.slug ?? tag.slug;

export function getDisplayText(
	value: string | null | undefined,
	placeholder: string | undefined = undefined
): string {
	return value ?? placeholder ?? m.lost_game_mink_loop();
}
