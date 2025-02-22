import type { PageServerLoad } from "./$types";
import client from "$lib/api";

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { data, error } = await client.GET('/api/work/relations', { params: {
        query: {
            work_id: +params.work_id
        }
    }, fetch });

    return {
        relations_html: data
    };
};
