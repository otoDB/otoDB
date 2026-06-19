import { m } from "$lib/paraglide/messages";

export default {
	"thread-closed": {
		icon: "icon-[gravity-ui--check]",
		label: m.topical_small_alligator_aspire(),
	},
	"thread-opened": {
		icon: "icon-[gravity-ui--comment]",
		label: m.flat_tasty_okapi_cut(),
	},
} as const satisfies Record<string, { icon: string; label: string }>;
