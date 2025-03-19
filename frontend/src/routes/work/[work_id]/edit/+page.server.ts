import { base } from "$app/paths";
import client from "$lib/api";
import { fail, redirect, type Actions } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { UserLevel } from "$lib/enums";

export const load: PageServerLoad = async ({ params, fetch, locals }) => {
    if (!locals.user || locals.user.level < UserLevel.MEMBER)
        redirect(303, `${base}/login`);

    const { data } = await client.GET('/api/work/sources', { params: {
        query: {
            work_id: +params.work_id
        }
    }, fetch });

    return {
        sources: data 
    };
};

export const actions = {
    edit: async ({ request, fetch, params }) => {
        const data = await request.formData();
        const title = data.get('title') as string,
            description = data.get('description') as string,
            rating = data.get('rating') as string,
            thumbnail = data.get('thumbnail') as string,
            reason = data.get('reason') as string;

        const { error } = await client.PUT('/api/work/work', { fetch, params: { query: {
            work_id: +params.work_id!, reason
        }}, body: {
            title, description, rating: +rating, thumbnail
        }});

        if (error)
            return fail(400, { title, description, rating, thumbnail, reason, failed: true });
        redirect(303, `${base}/work/${params.work_id}`);
    },
    relations: async ({ request, fetch, params }) => {
        const data = await request.formData();
        // todo
    }
} satisfies Actions;
