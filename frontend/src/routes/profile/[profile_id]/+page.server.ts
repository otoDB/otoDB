import client from "$lib/api";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ fetch, params }) => {
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
        profile: data
    };
}
