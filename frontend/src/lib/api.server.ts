import { browser } from '$app/environment';
import { env } from '$env/dynamic/private';
import { error, type Cookies } from '@sveltejs/kit';
import type { CookieSerializeOptions } from 'cookie';
import createClient, {
	type ClientRequestMethod,
	type MaybeOptionalInit,
	type Middleware,
	type ParseAsResponse
} from 'openapi-fetch';
import type { InitParam } from 'openapi-fetch/src/index.js';
import type {
	HttpMethod,
	MediaType,
	PathsWithMethod,
	ResponseObjectMap,
	SuccessResponse
} from 'openapi-typescript-helpers';
import setCookie from 'set-cookie-parser';
import type { paths } from './schema';

// The following types are re-specializations lifted from openapi-typescript-helpers with a custom FetchResponse.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type FetchResponse<T extends Record<string | number, any>, Options, Media extends MediaType> = {
	data: ParseAsResponse<SuccessResponse<ResponseObjectMap<T>, Media>, Options>;
	response: Response;
};
type ClientMethod<
	// eslint-disable-next-line @typescript-eslint/no-empty-object-type
	Paths extends Record<string, Record<HttpMethod, {}>>,
	Method extends HttpMethod,
	Media extends MediaType
> = <
	Path extends PathsWithMethod<Paths, Method>,
	Init extends MaybeOptionalInit<Paths[Path], Method>
>(
	url: Path,
	...init: InitParam<Init>
) => Promise<FetchResponse<Paths[Path][Method], Init, Media>>;
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
interface Client<Paths extends {}, Media extends MediaType = MediaType> {
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
const client = createClient<paths>({
	baseUrl: env.INTERNAL_API_ENDPOINT,
	credentials: 'include'
});
client.use({
	onResponse: async ({ response }) => {
		if (!response.ok) {
			const content = await response.json();
			error(response.status, {
				message: content.details ?? content.data?.message ?? 'Bad Request'
			});
		}
		return response;
	}
});
export default client as Client<paths>;

export const rawClient = createClient<paths>({
	baseUrl: env.INTERNAL_API_ENDPOINT,
	credentials: 'include'
});

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
