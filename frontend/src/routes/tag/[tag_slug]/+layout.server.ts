import * as m from '$lib/paraglide/messages.js';
import client from "$lib/api";
import type { LayoutServerLoad } from '../../$types';

export const load: LayoutServerLoad = async ({ params, fetch }) => {
    const { data, error } = await client.GET('/api/tag/tag', { params: {
        query: {
            tag_slug: params.tag_slug!
        }
    }, fetch });
    if (error)
        return; // TODO

    return {
        links: [
            { pathname: `tag/${params.tag_slug}`, title: m.empty_legal_chicken_taste() + " " + params.tag_slug },
            { pathname: `tag/${params.tag_slug}/edit`, title: m.minor_crisp_cobra_list() }
        ],
        tag: data
    };
};
