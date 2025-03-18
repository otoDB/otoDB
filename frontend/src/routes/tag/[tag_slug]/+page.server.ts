import client from "$lib/api";
import { commentClient } from "$lib/api";
import type { PageServerLoad } from "./$types";


export const load: PageServerLoad = async ({ params, fetch, parent }) => {
    const data = await parent();

    const [{ data: details }, { data: works }] = await Promise.all([client.GET('/api/tag/details', { fetch, params: { query: {
        tag_slug: params.tag_slug
    }}}), client.GET('/api/tag/works', { fetch, params: { query: {
        tag_slug: params.tag_slug
    }}})]);
    
    const comments = await commentClient.GET('tagwork', data.tag.id!, fetch);
    
    return {
        ...details,
        works,
        comments
    };
};
