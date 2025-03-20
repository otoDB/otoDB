import { error, fail, redirect, type Actions } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import client from "$lib/api";
import { UserLevel } from "$lib/enums";
import userLevelGuard from "$lib/route_guard";

export const load: PageServerLoad = async ({ fetch, url, locals }) => {
    userLevelGuard(locals.user, UserLevel.MEMBER, url.pathname);
    
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

        const { error, data: source_id } = await client.POST('/api/work/source', { fetch, params: { query: { url: link, is_reupload: !is_official, for_work: work ? +work : null }} });
        if (error)
            return fail(400, { url: link, origin: is_official, failed: true });

        if (locals.user.level >= UserLevel.MODERATOR)
            redirect(303, '/work/unbound');
        else
            redirect(303, `/profile/${locals.user.username}/submissions`);
    }
} satisfies Actions;
