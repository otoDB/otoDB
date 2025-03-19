import client from "$lib/api";
import { UserLevel } from "$lib/enums";
import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "../$types";
import { base } from "$app/paths";

export const load: PageServerLoad = async ({ fetch, params, locals, parent }) => {
    if (!locals.user || locals.user.level < UserLevel.MEMBER)
        redirect(303, `${base}/login`);

    let tags = (await parent()).tags;
    const { data: scores } = await client.GET('/api/work/tag_scores', { fetch, params: { query: { work_id: +params.work_id }}});
    tags.forEach((tag, i) => {
        tags[i] = { ...tags[i], ...scores?.find(e => e.tag_slug === tag.slug) };
    });
    return { tags };
};
