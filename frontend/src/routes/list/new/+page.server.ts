import { base } from "$app/paths";
import client from "$lib/api";
import { fail, redirect, type Actions } from "@sveltejs/kit";

export const actions = {
    default: async ({ request, fetch }) => {
        const data = await request.formData();
        const name = data.get('name') as string,
            description = data.get('description') as string;

        const { error, data: list_id } = await client.POST('/api/list/list', { fetch, body: {
            name, description
        }});
        if (error)
            return fail(400, { name, description, failed: true });

        redirect(303, `${base}/list/${list_id}`);
    }
} satisfies Actions;
