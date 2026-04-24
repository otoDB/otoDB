import { setToken } from '$lib/api.server';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = ({ data }) => {
	if (data?.user?.csrf) setToken(data.user.csrf);
	return data;
};
