import { m } from '$lib/paraglide/messages';

const c = (type: () => string, action: () => string) => () =>
	m.mild_loud_shad_enchant({ type: type(), name: action() });

export const Route = {
	UNKNOWN: { id: 0, title: () => 'Unknown' },

	TAGWORK_ALIAS: { id: 1, title: c(m.empty_legal_chicken_taste, () => 'Alias') },
	TAGWORK_UNALIAS: { id: 2, title: c(m.empty_legal_chicken_taste, () => 'Alias Control') },
	TAGWORK_DELETE: { id: 3, title: c(m.empty_legal_chicken_taste, m.real_born_goat_snap) },
	TAGWORK_UPDATE: { id: 4, title: c(m.empty_legal_chicken_taste, () => 'Update') },

	TAGWORK_EDIT_WIKI: { id: 7, title: c(m.empty_legal_chicken_taste, () => 'Edit Wiki') },
	TAGWORK_EDIT_CONNECTIONS: {
		id: 8,
		title: c(m.empty_legal_chicken_taste, () => 'Edit Connections')
	},

	SONGTAG_UPDATE: { id: 20, title: c(m.dull_plain_angelfish_cuddle, () => 'Update') },
	SONGTAG_SET_TAGS: { id: 21, title: c(m.grand_nice_pony_belong, () => 'Tag Control') },
	SONGTAG_ALIAS: { id: 22, title: c(m.dull_plain_angelfish_cuddle, () => 'Alias') },
	SONGTAG_UNALIAS: { id: 23, title: c(m.dull_plain_angelfish_cuddle, () => 'Alias Control') },
	SONGTAG_DELETE: { id: 24, title: c(m.dull_plain_angelfish_cuddle, m.real_born_goat_snap) },

	SONGRELATION_CREATE: { id: 30, title: c(m.grand_nice_pony_belong, () => 'Relation Control') },

	MEDIAWORK_DELETE: { id: 40, title: c(m.grand_merry_fly_succeed, m.real_born_goat_snap) },
	MEDIAWORK_SET_TAGS: { id: 41, title: c(m.grand_merry_fly_succeed, () => 'Tag Control') },

	MEDIAWORK_UPDATE: { id: 45, title: c(m.grand_merry_fly_succeed, () => 'Update') },
	MEDIAWORK_MERGE: { id: 46, title: c(m.grand_merry_fly_succeed, () => 'Merge') },
	MEDIAWORK_CREATE: { id: 47, title: c(m.grand_merry_fly_succeed, () => 'Create') },

	WORKRELATION_CREATE: { id: 50, title: c(m.grand_merry_fly_succeed, () => 'Relation Control') },

	WORKSOURCE_CREATE: { id: 60, title: c(m.extra_brave_tapir_skip, () => 'Create') },
	WORKSOURCE_UNBIND: { id: 61, title: c(m.extra_brave_tapir_skip, m.sour_lime_shad_edit) },
	WORKSOURCE_SET_ORIGIN: { id: 62, title: c(m.extra_brave_tapir_skip, () => 'Set Origin') },
	WORKSOURCE_REFRESH: { id: 63, title: c(m.extra_brave_tapir_skip, m.mushy_proof_hornet_dig) },
	WORKSOURCE_ASSIGN: { id: 64, title: c(m.extra_brave_tapir_skip, () => 'Assign') },
	WORKSOURCE_REJECT: { id: 65, title: c(m.extra_brave_tapir_skip, m.alive_blue_marlin_push) },
	WORKSOURCE_UPDATE: { id: 66, title: c(m.extra_brave_tapir_skip, () => 'Update') },

	ROLLBACK: { id: 100, title: m.legal_mean_slug_link }
} as const satisfies Record<string, { id: number; title: () => string }>;

/**
 * @deprecated
 */
export function resolveRouteKeyById(id: number): keyof typeof Route {
	return Object.entries(Route).find(([_, value]) => value.id === id)?.[0] as keyof typeof Route;
}
