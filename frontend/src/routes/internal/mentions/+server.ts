import { json, error } from '@sveltejs/kit';
import { parseMentions } from '$lib/markdown';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request }) => {
	const { text } = await request.json();
	if (typeof text !== 'string') {
		error(400, 'text must be a string');
	}

	return json({ data: parseMentions(text) });
};
