import { browser } from '$app/environment';
import { env } from '$env/dynamic/public';
import { error, type Cookies } from '@sveltejs/kit';
import type { CookieSerializeOptions } from 'cookie';
import createClient, {
	type ClientRequestMethod,
	type MaybeOptionalInit,
	type Middleware,
	type ParseAsResponse
} from 'openapi-fetch';
import setCookie from 'set-cookie-parser';
import { languages } from './enums/Languages';
import { m } from './paraglide/messages';
import { getLocale } from './paraglide/runtime';
import type { paths } from './schema';
import type {
	HttpMethod,
	MediaType,
	PathsWithMethod,
	ResponseObjectMap,
	SuccessResponse
} from 'openapi-typescript-helpers';
import type { InitParam } from 'openapi-fetch/src/index.js';

const backend = browser
	? (env.PUBLIC_BACKEND_URL_EXTERNAL ?? '')
	: (env.PUBLIC_BACKEND_URL_INTERNAL ?? env.PUBLIC_BACKEND_URL_EXTERNAL ?? '');

export const clientRaw = createClient<paths>({ baseUrl: backend, credentials: 'include' });

type FetchResponse<T extends Record<string | number, any>, Options, Media extends MediaType> = {
	data: ParseAsResponse<SuccessResponse<ResponseObjectMap<T>, Media>, Options>;
	response: Response;
};
type ClientMethod<
	Paths extends Record<string, Record<HttpMethod, object>>,
	Method extends HttpMethod,
	Media extends MediaType
> = <
	Path extends PathsWithMethod<Paths, Method>,
	Init extends MaybeOptionalInit<Paths[Path], Method>
>(
	url: Path,
	...init: InitParam<Init>
) => Promise<FetchResponse<Paths[Path][Method], Init, Media>>;
interface Client<
	Paths extends Record<string, Record<HttpMethod, object>>,
	Media extends MediaType = MediaType
> {
	request: ClientRequestMethod<Paths, Media>;
	GET: ClientMethod<Paths, 'get', Media>;
	PUT: ClientMethod<Paths, 'put', Media>;
	POST: ClientMethod<Paths, 'post', Media>;
	DELETE: ClientMethod<Paths, 'delete', Media>;
	OPTIONS: ClientMethod<Paths, 'options', Media>;
	HEAD: ClientMethod<Paths, 'head', Media>;
	PATCH: ClientMethod<Paths, 'patch', Media>;
	TRACE: ClientMethod<Paths, 'trace', Media>;
	use(...middleware: Middleware[]): void;
	eject(...middleware: Middleware[]): void;
}
const client = createClient<paths>({ baseUrl: backend, credentials: 'include' });
client.use({
	onResponse: async ({ response }) => {
		if (!response.ok) {
			const content = await response.json();
			error(response.status, content.details);
		}
		return response;
	}
});
export default client as Client<paths>;

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
