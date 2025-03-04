import type { LayoutServerLoad } from "./$types";
import * as m from '$lib/paraglide/messages.js';
import client from "$lib/api";
import { error } from "@sveltejs/kit";

export const load: LayoutServerLoad = async ({ params, fetch }) => {
    if (isNaN(+params.work_id))
        error(400, { message: 'Bad request' });

    const { data, error: e } = await client.GET('/api/work/work', { params: {
        query: {
            work_id: +params.work_id
        }
    }, fetch });
    if (e)
        error(404, { message: 'Not found' });

    return {
        links: [
            { pathname: `work/${params.work_id}`, title: m.grand_merry_fly_succeed() + " " + params.work_id },
            { pathname: `work/${params.work_id}/relations`, title: m.alive_these_jay_pick() },
            { pathname: `work/${params.work_id}/edit`, title: m.minor_crisp_cobra_list() }
        ],
        ...data
    };
};
