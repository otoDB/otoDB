import { env } from '$env/dynamic/public';
import createClient from 'openapi-fetch';
import type { paths } from '$lib/schema';

export const client = createClient<paths>({
	baseUrl: env.PUBLIC_API_ENDPOINT,
	credentials: 'include'
});
export default client;
