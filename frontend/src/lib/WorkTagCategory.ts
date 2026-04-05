import { m } from '$lib/paraglide/messages.js';

export const WorkTagCategory = {
	EVENT: {
		id: 1,
		nameFn: m.next_bland_goldfish_heart,
		color: 'rgb(8,145,178)',
		settable: false
	},
	CREATOR: {
		id: 4,
		nameFn: m.empty_fresh_mare_jump,
		color: 'rgb(220,38,38)',
		settable: true
	},
	MEDIA: {
		id: 6,
		nameFn: m.wise_keen_beaver_pick,
		color: 'rgb(112,26,117)',

		settable: true
	},
	SOURCE: {
		id: 3,
		nameFn: m.knotty_due_hamster_wave,
		color: 'rgb(101,163,13)',
		settable: false
	},
	SONG: {
		id: 2,
		nameFn: m.grand_nice_pony_belong,
		color: 'rgb(232,121,249)',
		settable: true
	},
	GENERAL: {
		id: 0,
		nameFn: m.fresh_lower_rook_trip,
		color: 'rgb(159,163,169)',
		settable: false
	},
	META: {
		id: 5,
		nameFn: m.sad_next_jaguar_renew,
		color: 'rgb(251,191,36)',
		settable: false
	}
} as const;

/**
 * @deprecated
 */
export const resolveWorkTagCategoryKeyById = (
	id: number // (typeof WorkTagCategory)[keyof typeof WorkTagCategory]['id']
): keyof typeof WorkTagCategory => {
	return Object.entries(WorkTagCategory).find(
		([, c]) => c.id === id
	)![0] as keyof typeof WorkTagCategory;
};
