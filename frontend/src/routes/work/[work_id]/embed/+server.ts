import { redirectToEmbedSource } from '$lib/embed_redirect';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = ({ params, request, fetch }) =>
	redirectToEmbedSource(params.work_id, request, fetch);
