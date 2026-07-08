import { m } from '$lib/paraglide/messages';

// Keys must name what the icon means (e.g. 'external-link'), not the icon's shape or name (e.g. 'globe').
export default {
	'thread-closed': {
		icon: 'icon-[gravity-ui--check]',
		label: m.topical_small_alligator_aspire()
	},
	'thread-opened': {
		icon: 'icon-[gravity-ui--comment]',
		label: m.flat_tasty_okapi_cut()
	},
	'external-link': {
		icon: 'icon-[gravity-ui--globe]',
		label: m.plain_wide_globe_open()
	},
	'list-remove': {
		icon: 'icon-[gravity-ui--circle-xmark]',
		label: m.even_alert_grebe_taste()
	},
	'list-add': {
		icon: 'icon-[gravity-ui--circle-plus]',
		label: m.spare_kind_otter_gain()
	},
	'list-restore': {
		icon: 'icon-[gravity-ui--arrow-rotate-left]',
		label: m.quiet_plain_otter_return()
	}
} as const satisfies Record<string, { icon: string; label: string }>;
