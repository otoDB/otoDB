import client from "$lib/api";
import { getAuth } from "$lib/api";
import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ request, cookies, fetch }) => {
	const r = await getAuth(cookies, fetch);
	if (!r)
		redirect(307, '/');

	await client.POST('/api/auth/logout', { fetch });

	cookies.delete('csrftoken', {path: '/'});
	cookies.delete('sessionid', {path: '/'});

	redirect(307, '/');
}
