// since there's no dynamic data here, we can prerender
// it so that it gets served as a static asset in production
import client from "$lib/api";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ fetch }) => {
    const video = await client.GET('/api/query_video', {
        params: { query: { id: 'sm43808529', platform: 'niconico' } },
        fetch
    });

    return {
        video: {
            data: video.data,
            error: video.error
        }
    };
}
