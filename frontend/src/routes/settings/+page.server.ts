import { m } from '$lib/paraglide/messages';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = () => ({
	head: { title: m.flat_small_kitten_race(), noindex: true }
});
