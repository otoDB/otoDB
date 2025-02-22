import client from "$lib/api";
import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "../../$types";
import { base } from "$app/paths";

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { data, error } = await client.GET('/api/work/work', { params: {
        query: {
            work_id: params.work_id
        }
    }, fetch });
    if (error)
        return; // TODO
    return data;
};
