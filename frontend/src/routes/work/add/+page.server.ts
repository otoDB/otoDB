import { fail, redirect, type Actions } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import client from "$lib/api";
import { base } from "$app/paths";

export const load: PageServerLoad = async ({ fetch, url }) => {
    const work = url.searchParams.get('for_work');
    if (work && !isNaN(+work)) {
        const { data, error } = await client.GET('/api/work/work', { params: {
            query: {
                work_id: +work
            }
        }, fetch });
        if (error)
            return; // TODO

        return {
            title: data.title
        };
    }
}

export const actions = {
    default: async ({ request, fetch, url }) => {
        const data = await request.formData();
        const link = data.get('url') as string,
            is_official = !!data.get('origin');
        const work = url.searchParams.get('for_work');

        const { error, data: source_id } = await client.POST('/api/work/source', { fetch, params: { query: { url: link, is_reupload: !is_official }} });
        if (error)
            return fail(400, { url: link, origin: is_official, failed: true });

        const { data: final_work_id } = await client.POST('/api/work/assign_source', { fetch, params: { query: {
            source_id: source_id, work_id: (work && !isNaN(+work)) ? +work : null
        }}});
        redirect(303, `${base}/work/${+final_work_id}`);
    }
} satisfies Actions;
