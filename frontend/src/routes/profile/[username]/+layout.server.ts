import type { LayoutServerLoad } from "./$types";
import client from "$lib/api";
import * as m from '$lib/paraglide/messages.js';
import { error } from "@sveltejs/kit";

export const load: LayoutServerLoad = async ({ params, fetch }) => {
    const { data, error: e } = await client.GET('/api/profile/profile', { fetch,
        params: {
            query: {
                username: params.username
            }
        }
    });
    if (e)
        error(404, { message: 'Not found' });
    
    return {
        links: [
            { pathname: `profile/${params.username}`, title: m.frail_maroon_tadpole_inspire() + " " + params.username },
            { pathname: `profile/${params.username}/lists`, title: m.stale_loose_squid_cut() },
            { pathname: `profile/${params.username}/submissions`, title: "Submissions" }
        ],
        profile: data
    };
};
