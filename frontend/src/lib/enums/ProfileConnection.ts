/**
 * Profile Connection
 */

export const ProfileConnection = {
	WEBSITE: {
		id: 0,
		name: 'Website',
		linkFn: (id: string) => id
	},
	NICONICO: {
		id: 1,
		name: 'Niconico',
		linkFn: (id: string) => `https://www.nicovideo.jp/user/${id}/`
	},
	YOUTUBE: {
		id: 2,
		name: 'YouTube',
		linkFn: (id: string) => `https://www.youtube.com/${id}`
	},
	BILIBILI: {
		id: 3,
		name: 'Bilibili',
		linkFn: (id: string) => `https://space.bilibili.com/${id}`
	},
	TWITTER: {
		id: 4,
		name: 'Twitter',
		linkFn: (id: string) => `https://twitter.com/${id}/`
	},
	BLUESKY: {
		id: 5,
		name: 'Bluesky',
		linkFn: (id: string) => `https://bsky.app/profile/${id}`
	},
	SOUNDCLOUD: {
		id: 6,
		name: 'Soundcloud',
		linkFn: (id: string) => `https://soundcloud.com/${id}`
	}
} as const satisfies Record<string, { id: number; name: string; linkFn: (id: string) => string }>;

export const allProfileConnectionKeys = Object.keys(
	ProfileConnection
) as (keyof typeof ProfileConnection)[];

/**
 * @deprecated
 */
export const resolveProfileConnectionNameById = (id: number): keyof typeof ProfileConnection => {
	return Object.entries(ProfileConnection).find(
		([_, value]) => value.id === id
	)?.[0] as keyof typeof ProfileConnection;
};
