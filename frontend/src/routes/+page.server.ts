// since there's no dynamic data here, we can prerender
// it so that it gets served as a static asset in production
import client from "$lib/api";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ fetch }) => {
    const work = await client.GET('/api/random_work', { fetch });

    return {
        work: {
            data: work.data,
            error: work.error
        }
    };
}
