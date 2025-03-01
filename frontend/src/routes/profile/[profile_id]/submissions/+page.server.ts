import client from "$lib/api";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ fetch, params }) => {
    const { data: submissions } = await client.GET('/api/profile/submissions', { fetch,
        params: {
            query: {
                user_id: +params.profile_id
            }
        }
    });
    return {
        approved: submissions?.items.filter(s => s.media),
        pending: submissions?.items.filter(s => !s.media)
    };
}
