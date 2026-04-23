import { m } from '$lib/paraglide/messages.js';
import { WorkTagCategory } from '$lib/schema';

export const WorkTagCategoryMap: Record<
	WorkTagCategory,
	{
		nameFn: () => string;
		color: string;
		canSetAsSource: boolean;
		order: number;
	}
> = {
	[WorkTagCategory.Event]: {
		nameFn: m.next_bland_goldfish_heart,
		color: 'rgb(8,145,178)',
		canSetAsSource: false,
		order: 0
	},
	[WorkTagCategory.Creator]: {
		nameFn: m.empty_fresh_mare_jump,
		color: 'rgb(220,38,38)',
		canSetAsSource: true,
		order: 1
	},
	[WorkTagCategory.Media]: {
		nameFn: m.wise_keen_beaver_pick,
		color: 'rgb(112,26,117)',
		canSetAsSource: true,
		order: 2
	},
	[WorkTagCategory.Source]: {
		nameFn: m.knotty_due_hamster_wave,
		color: 'rgb(101,163,13)',
		canSetAsSource: false,
		order: 3
	},
	[WorkTagCategory.Song]: {
		nameFn: m.grand_nice_pony_belong,
		color: 'rgb(232,121,249)',
		canSetAsSource: true,
		order: 4
	},
	[WorkTagCategory.General]: {
		nameFn: m.fresh_lower_rook_trip,
		color: 'rgb(30,144,255)',
		canSetAsSource: false,
		order: 5
	},
	[WorkTagCategory.Meta]: {
		nameFn: m.sad_next_jaguar_renew,
		color: 'rgb(251,191,36)',
		canSetAsSource: false,
		order: 6
	},
	[WorkTagCategory.Uncategorized]: {
		nameFn: m.careful_close_shad_achieve,
		color: 'rgb(159,163,169)',
		canSetAsSource: false,
		order: 7
	}
};
