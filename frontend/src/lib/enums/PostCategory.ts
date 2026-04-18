import { m } from '$lib/paraglide/messages.js';
import { PostCategory } from '$lib/schema';

export const PostCategoryNames = {
	[PostCategory.Announcement]: m.livid_loose_eel_pop,
	[PostCategory.Feature_Request]: m.crazy_loud_trout_peek,
	[PostCategory.Bug_Report]: m.new_honest_tapir_endure,
	[PostCategory.Gardening]: m.moving_trick_piranha_thrive,
	[PostCategory.General]: m.fresh_lower_rook_trip
} as const satisfies Record<PostCategory, () => string>;
