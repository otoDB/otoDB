import { setToken } from "$lib/api";
import type { LayoutLoad } from "./$types";

export const load: LayoutLoad = ({ data }) => {
	if (data?.user?.csrf)
		setToken(data.user.csrf)
	return data;
};
