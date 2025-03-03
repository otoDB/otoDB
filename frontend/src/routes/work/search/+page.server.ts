import client from "$lib/api";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ url, fetch }) => {
    const query = url.searchParams.get('query') ?? '';
    const { data } = await client.GET('/api/work/search', { fetch, params: { query: { query: query }} });
    return {
        query: query,
        results: data
    }
}
