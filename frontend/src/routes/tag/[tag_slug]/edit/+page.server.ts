import { base } from "$app/paths";
import client from "$lib/api";
import { fail, redirect, type Actions } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ params, fetch }) => {
    const [{ data: wiki_page }, { data: details }] = await Promise.all([client.GET('/api/tag/wiki_page', { fetch, params: { query: {
        tag_slug: params.tag_slug
    }}}), client.GET('/api/tag/details', { fetch, params: { query: {
        tag_slug: params.tag_slug
    }}})]);
    
    return {
        wiki_page,
        parent_slug: details?.tree[0]?.slug
    };
};

export const actions = {
    edit: async ({ request, fetch, params }) => {
        const data = await request.formData();
        const category = data.get('category') as string,
            parent_slug = data.get('parent') as string;

        const { error } = await client.PUT('/api/tag/tag', { fetch, params: { query: {
            tag_slug: params.tag_slug!
        }}, body: {
            category: +category,
            parent_slug
        }});

        if (error)
            return fail(400, { category, parent_slug, failed: true });

        if (+category == 2) {
            const title = data.get('song') as string,
                author = data.get('category') as string,
                bpm = data.get('song_bpm') as string;
            client.POST('/api/tag/song', { fetch, params: { query: {
                tag_slug: params.tag_slug!
            }}, body: {
                title, author, bpm: +bpm
            }});
        }
        redirect(303, `${base}/tag/${params.tag_slug}`);
    },
    delete_song: async ({ request, fetch, params }) => {
        await client.DELETE('/api/tag/song', { fetch, params: { query: {
            tag_slug: params.tag_slug!
        }}});
    },
    wiki_page: async ({ request, fetch, params }) => {
        const data = await request.formData();
        await client.POST('/api/tag/wiki_page', { fetch, params: { query: {
            tag_slug: params.tag_slug!,
            md: data.get('md') as string
        }}});
    }
} satisfies Actions;
