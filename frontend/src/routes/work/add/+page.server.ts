import { error, fail, redirect, type Actions } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import client from "$lib/api";
import { base } from "$app/paths";
import { UserLevel } from "$lib/enums";

export const load: PageServerLoad = async ({ fetch, url, locals }) => {
    if (!locals.user || locals.user.level < UserLevel.MEMBER)
        redirect(303, `${base}/login`);
    
    const work = url.searchParams.get('for_work');
    if (work && !isNaN(+work)) {
        const { data, error: e } = await client.GET('/api/work/work', { params: {
            query: {
                work_id: +work
            }
        }, fetch });
        if (e)
            error(404, { message: 'Not found' });

        return {
            title: data.title
        };
    }
}

export const actions = {
    default: async ({ request, fetch, url, locals }) => {
        const data = await request.formData();
        const link = data.get('url') as string,
            is_official = !!data.get('origin');
        const work = url.searchParams.get('for_work');

        const { error, data: source_id } = await client.POST('/api/work/source', { fetch, params: { query: { url: link, is_reupload: !is_official }} });
        if (error)
            return fail(400, { url: link, origin: is_official, failed: true });

        if (work && !isNaN(+work)) {
            const { data: final_work_id } = await client.POST('/api/work/assign_source', { fetch, params: { query: {
                source_id: source_id, work_id: +work
            }}});
            redirect(303, `${base}/work/${+final_work_id!}`);
        }
        else {
            redirect(303, `${base}/profile/${locals.user.username}/submissions`);
        }
    }
} satisfies Actions;
