import { redirect } from '@sveltejs/kit';
import { redirectToEmbedSource } from '$lib/embed_redirect';
import { PlatformNames } from '$lib/enums';
import { Platform } from '$lib/schema';
import type { RequestHandler } from './$types';

const PLATFORM_BY_NAME = new Map<string, Platform>(
	Object.entries(PlatformNames).map(([k, v]) => [v.toLowerCase(), Number(k) as Platform])
);

export const GET: RequestHandler = async ({ params, request, fetch }) => {
	const workPath = `/work/${params.work_id}`;
	const platform = PLATFORM_BY_NAME.get(params.platform.toLowerCase());
	if (platform === undefined) redirect(302, workPath);

	return redirectToEmbedSource(params.work_id, request, fetch, (s) => s.platform === platform);
};
