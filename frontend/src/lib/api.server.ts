import createClient, {
	type ClientRequestMethod,
	type MaybeOptionalInit,
	type Middleware,
	type ParseAsResponse
} from 'openapi-fetch';
import type {
	HttpMethod,
	MediaType,
	PathsWithMethod,
	ResponseObjectMap,
	SuccessResponse
} from 'openapi-typescript-helpers';
import type { InitParam } from 'openapi-fetch/src/index.js';
import { error } from '@sveltejs/kit';
import type { paths } from './schema';
import { env } from '$env/dynamic/public';

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
	baseUrl: env.PUBLIC_BACKEND_URL_INTERNAL,
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
