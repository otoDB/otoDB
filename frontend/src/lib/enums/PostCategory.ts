import { m } from '$lib/paraglide/messages.js';

export const postCategory = {
	ANNOUNCEMENT: {
		id: 0,
		nameFn: m.livid_loose_eel_pop
	},
	FEATURE_REQUEST: {
		id: 1,
		nameFn: m.crazy_loud_trout_peek
	},
	BUG_REPORT: {
		id: 2,
		nameFn: m.new_honest_tapir_endure
	},
	GARDENING: {
		id: 3,
		nameFn: m.moving_trick_piranha_thrive
	},
	GENERAL: {
		id: 4,
		nameFn: m.fresh_lower_rook_trip
	}
} as const;

export const allPostCategories = Object.keys(postCategory) as (keyof typeof postCategory)[];

/**
 * @deprecated
 */
export const resolvePostCategoryKeyById = (
	id: number // (typeof postCategory)[keyof typeof postCategory]['id']
): keyof typeof postCategory => {
	return Object.entries(postCategory).find(
		([_, v]) => v.id === id
	)?.[0] as keyof typeof postCategory;
};
