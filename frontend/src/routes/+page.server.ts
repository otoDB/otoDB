import client from "$lib/api";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ fetch }) => {
    const work = await client.GET('/api/work/random', { fetch });

    return {
        work: {
            data: work.data,
            error: work.error
        }
    };
}
