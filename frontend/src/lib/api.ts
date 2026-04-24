import { browser } from '$app/environment';
import { PUBLIC_BACKEND_URL_EXTERNAL, PUBLIC_BACKEND_URL_INTERNAL } from '$env/static/public';
import { type Cookies } from '@sveltejs/kit';
import type { CookieSerializeOptions } from 'cookie';
import createClient from 'openapi-fetch';
import setCookie from 'set-cookie-parser';
import { languages } from '$lib/enums/language';
import { m } from '$lib/paraglide/messages';
import { getLocale } from '$lib/paraglide/runtime';
import type { paths } from '$lib/schema';

const backend = browser
	? (PUBLIC_BACKEND_URL_EXTERNAL ?? '')
	: (PUBLIC_BACKEND_URL_INTERNAL ?? PUBLIC_BACKEND_URL_EXTERNAL ?? '');

export const client = createClient<paths>({ baseUrl: backend, credentials: 'include' });
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
			sameSite: sameSite as CookieSerializeOptions['sameSite']
		});
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
