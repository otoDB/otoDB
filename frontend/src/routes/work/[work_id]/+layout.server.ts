import type { LayoutServerLoad } from "./$types";
import * as m from '$lib/paraglide/messages.js';
import client from "$lib/api";

export const load: LayoutServerLoad = async ({ params, fetch }) => {
    const { data, error } = await client.GET('/api/work/work', { params: {
        query: {
            work_id: +params.work_id
        }
    }, fetch });
    if (error)
        return; // TODO

    return {
        links: [
            { pathname: `work/${params.work_id}`, title: m.grand_merry_fly_succeed() + " " + params.work_id },
            { pathname: `work/${params.work_id}/relations`, title: m.alive_these_jay_pick() },
            { pathname: `work/${params.work_id}/edit`, title: m.minor_crisp_cobra_list() }
        ],
        ...data
    };
};
