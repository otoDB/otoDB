import client from "$lib/api";
import type { PageServerLoad } from "./$types";


export const load: PageServerLoad = async ({ params, fetch }) => {
    const { data } = await client.GET('/api/work/sources', { params: {
        query: {
            work_id: +params.work_id
        }
    }, fetch });

    return {
        sources: data 
    };
};

