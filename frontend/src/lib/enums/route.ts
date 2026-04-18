import { m } from '$lib/paraglide/messages';
import { Route } from '$lib/schema';

const c = (type: () => string, action: () => string) => () =>
	m.mild_loud_shad_enchant({ type: type(), name: action() });

export const routeNames: Record<Route, () => string> = {
	[Route.Unknown]: () => 'Unknown',

	[Route.Tag_Work_Alias]: c(m.empty_legal_chicken_taste, m.civil_civil_ray_forgive),
	[Route.Tag_Work_Alias_Control]: c(m.empty_legal_chicken_taste, m.good_vivid_weasel_launch),
	[Route.Tag_Work_Delete]: c(m.empty_legal_chicken_taste, m.real_born_goat_snap),
	[Route.Tag_Work_Update]: c(m.empty_legal_chicken_taste, m.dry_raw_finch_devour),

	[Route.Tag_Work_Edit_Wiki]: c(m.empty_legal_chicken_taste, m.male_known_pony_rise),
	[Route.Tag_Work_Edit_Connections]: c(m.empty_legal_chicken_taste, m.plane_heavy_gorilla_grip),

	[Route.Song_Tag_Update]: c(m.dull_plain_angelfish_cuddle, m.dry_raw_finch_devour),
	[Route.Song_Tag_Set_Tags]: c(m.grand_nice_pony_belong, m.agent_cuddly_robin_succeed),
	[Route.Song_Tag_Alias]: c(m.dull_plain_angelfish_cuddle, m.civil_civil_ray_forgive),
	[Route.Song_Tag_Alias_Control]: c(m.dull_plain_angelfish_cuddle, m.good_vivid_weasel_launch),
	[Route.Song_Tag_Delete]: c(m.dull_plain_angelfish_cuddle, m.real_born_goat_snap),

	[Route.Song_Relation_Control]: c(m.grand_nice_pony_belong, m.few_misty_jurgen_roam),

	[Route.Media_Work_Delete]: c(m.grand_merry_fly_succeed, m.real_born_goat_snap),
	[Route.Media_Work_Set_Tags]: c(m.grand_merry_fly_succeed, m.agent_cuddly_robin_succeed),

	[Route.Media_Work_Update]: c(m.grand_merry_fly_succeed, m.dry_raw_finch_devour),
	[Route.Media_Work_Merge]: c(m.grand_merry_fly_succeed, m.noisy_fluffy_shrike_wish),
	[Route.Media_Work_Create]: c(m.grand_merry_fly_succeed, m.pretty_heroic_buzzard_splash),

	[Route.Work_Relation_Control]: c(m.grand_merry_fly_succeed, m.few_misty_jurgen_roam),

	[Route.Work_Source_Create]: c(m.extra_brave_tapir_skip, m.pretty_heroic_buzzard_splash),
	[Route.Work_Source_Unbind]: c(m.extra_brave_tapir_skip, m.sour_lime_shad_edit),
	[Route.Work_Source_Set_Origin]: c(m.extra_brave_tapir_skip, m.lofty_calm_dingo_zip),
	[Route.Work_Source_Refresh]: c(m.extra_brave_tapir_skip, m.mushy_proof_hornet_dig),
	[Route.Work_Source_Assign]: c(m.extra_brave_tapir_skip, m.small_fair_lark_savor),
	[Route.Work_Source_Reject]: c(m.extra_brave_tapir_skip, m.alive_blue_marlin_push),
	[Route.Work_Source_Update]: c(m.extra_brave_tapir_skip, m.dry_raw_finch_devour),

	[Route.Rollback]: m.legal_mean_slug_link
};
