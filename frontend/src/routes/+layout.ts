import { setToken } from "$lib/api";
import type { LayoutLoad } from "./$types";

export const load: LayoutLoad = async ({ data }) => {
    if (data?.csrf)
        setToken(data.csrf);
    if (data?.user)
        return { user: data.user };
}
