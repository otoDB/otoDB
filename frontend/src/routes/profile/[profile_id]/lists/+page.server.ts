import client from "$lib/api";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ fetch, params }) => {
    const { data: lists } = await client.GET('/api/profile/lists', { fetch,
        params: {
            query: {
                user_id: +params.profile_id
            }
        }
    });
    return {
        lists
    };
}
