import { browser } from '$app/environment';
import { env } from '$env/dynamic/public';
import { type Cookies } from '@sveltejs/kit';
import type { CookieSerializeOptions } from 'cookie';
import createClient from 'openapi-fetch';
import setCookie from 'set-cookie-parser';
import type { paths } from '$lib/schema';

const backend = browser
	? (env.PUBLIC_BACKEND_URL_EXTERNAL ?? '')
	: (env.PUBLIC_BACKEND_URL_INTERNAL ?? env.PUBLIC_BACKEND_URL_EXTERNAL ?? '');

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
