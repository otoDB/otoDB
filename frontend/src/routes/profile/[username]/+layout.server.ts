import type { LayoutServerLoad } from './$types';
import client from '$lib/api';
import { m } from '$lib/paraglide/messages.js';

export const load: LayoutServerLoad = async ({ params, fetch, locals }) => {
	const { data } = await client.GET('/api/profile/profile', {
		fetch,
		params: {
			query: {
				username: params.username
			}
		}
	});

	return {
		links: [
			{
				pathname: `profile/${params.username}`,
				title: m.frail_maroon_tadpole_inspire() + ' ' + data.username
			},
			{ pathname: `profile/${params.username}/lists`, title: m.stale_loose_squid_cut() },
			{
				pathname: `profile/${params.username}/submissions`,
				title: m.active_front_anteater_cry()
			},
			{
				pathname: `profile/${params.username}/revisions`,
				title: m.house_patient_cuckoo_trust()
			},
			...(params.username !== locals.user?.username
				? []
				: [
						{
							pathname: `profile/${params.username}/edit`,
							title: m.minor_crisp_cobra_list()
						}
					])
		],
		profile: data,
		head: {
			title: m.mild_loud_shad_enchant({
				type: m.fuzzy_crazy_cobra_lead(),
				name: data.username
			}),
			breadcrumbs: [
				{ name: m.fine_late_chicken_quiz(), url: '/' },
				{ name: data.username, url: `/profile/${params.username}` }
			]
		}
	};
};
