import { base } from "$app/paths";
import client from "$lib/api";
import { fail, redirect, type Actions } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { UserLevel } from "$lib/enums";

export const load: PageServerLoad = async ({ fetch, locals }) => {
    const { data, error } = await client.GET('/api/work/unbound', { fetch, params: { query: { pending: false }}});
    return { sources: data };
};
