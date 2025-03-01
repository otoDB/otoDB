import type { LayoutServerLoad } from "./$types";
import client from "$lib/api";
import * as m from '$lib/paraglide/messages.js';

export const load: LayoutServerLoad = async ({ params, fetch }) => {
    const { data, error } = await client.GET('/api/profile/profile', { fetch,
        params: {
            query: {
                user_id: +params.profile_id
            }
        }
    });
    if (error)
        return; // TODO
    
    return {
        links: [
            { pathname: `profile/${params.profile_id}`, title: m.frail_maroon_tadpole_inspire() + " " + params.profile_id },
            { pathname: `profile/${params.profile_id}/lists`, title: m.stale_loose_squid_cut() },
            { pathname: `profile/${params.profile_id}/submissions`, title: "Submissions" }
        ],
        profile: data
    };
};
