import { base } from "$app/paths";
import client from "$lib/api";
import { fail, redirect, type Actions } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { UserLevel } from "$lib/enums";

export const load: PageServerLoad = async ({ locals }) => {
    if (!locals.user || locals.user.level < UserLevel.MEMBER)
        redirect(303, `${base}/login`);
};

export const actions = {
    default: async ({ request, fetch }) => {
        const data = await request.formData();
        const link = data.get('url') as string;

        const { error, data: list_id } = await client.POST('/api/list/import', { fetch, params: { query: { url: link } } });
        if (error)
            return fail(400, { url: link, failed: true });

        redirect(303, `${base}/list/${list_id}`);
    }
} satisfies Actions;
