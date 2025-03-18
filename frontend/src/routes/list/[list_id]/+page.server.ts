import { commentClient } from "$lib/api";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ fetch, params }) => {
    const comments = await commentClient.GET('pool', +params.list_id, fetch);
    return { comments };
};
