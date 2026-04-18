import { ProfileConnectionTypes } from '$lib/schema';

export const ProfileConnectionMap = {
	[ProfileConnectionTypes.Website]: {
		name: 'Website',
		linkFn: (id: string) => id
	},
	[ProfileConnectionTypes.Niconico]: {
		name: 'Niconico',
		linkFn: (id: string) => `https://www.nicovideo.jp/user/${id}/`
	},
	[ProfileConnectionTypes.YouTube]: {
		name: 'YouTube',
		linkFn: (id: string) => `https://www.youtube.com/${id}`
	},
	[ProfileConnectionTypes.Bilibili]: {
		name: 'Bilibili',
		linkFn: (id: string) => `https://space.bilibili.com/${id}`
	},
	[ProfileConnectionTypes.Twitter]: {
		name: 'Twitter',
		linkFn: (id: string) => `https://twitter.com/${id}/`
	},
	[ProfileConnectionTypes.Bluesky]: {
		name: 'Bluesky',
		linkFn: (id: string) => `https://bsky.app/profile/${id}`
	},
	[ProfileConnectionTypes.Soundcloud]: {
		name: 'Soundcloud',
		linkFn: (id: string) => `https://soundcloud.com/${id}`
	}
} as const satisfies Record<
	ProfileConnectionTypes,
	{ name: string; linkFn: (id: string) => string }
>;
