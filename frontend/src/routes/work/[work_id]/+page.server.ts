import client from "$lib/api";
import type { PageServerLoad } from "./$types";


export const load: PageServerLoad = async ({ params, fetch }) => {
    const { data, error } = await client.GET('/api/work/sources', { params: {
        query: {
            work_id: +params.work_id
        }
    }, fetch });

    if (error)
        return; // TODO

    return {
        sources: data 
    };
};

