import client from "$lib/api";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ fetch }) => {
    const { data, error } = await client.GET('/api/work/unbound', { fetch, params: { query: { pending: true }}});
    return { sources: data };
};
