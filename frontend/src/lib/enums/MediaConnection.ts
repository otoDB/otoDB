import { MediaConnectionTypes } from '$lib/schema';

export const MediaConnectionMap = {
	[MediaConnectionTypes.AniKore]: {
		name: 'AniKore',
		linkFn: (id: string) => `https://www.anikore.jp/anime/${id}/`
	},
	[MediaConnectionTypes.Bangumi]: {
		name: 'Bangumi',
		linkFn: (id: string) => `https://bangumi.tv/subject/${id}`
	},
	[MediaConnectionTypes.AniDB]: {
		name: 'AniDB',
		linkFn: (id: string) => `https://anidb.net/anime/${id}`
	},
	[MediaConnectionTypes.MyAnimeList]: {
		name: 'MyAnimeList',
		linkFn: (id: string) => `https://myanimelist.net/anime/${id}`
	},
	[MediaConnectionTypes.AniList]: {
		name: 'AniList',
		linkFn: (id: string) => `https://anilist.co/anime/${id}`
	},
	[MediaConnectionTypes.Kitsu]: {
		name: 'Kitsu',
		linkFn: (id: string) => `https://kitsu.io/anime/${id}`
	},
	[MediaConnectionTypes.Anime_Planet]: {
		name: 'Anime-Planet',
		linkFn: (id: string) => `https://www.anime-planet.com/anime/${id}`
	},
	[MediaConnectionTypes.IMDb]: {
		name: 'IMDb',
		linkFn: (id: string) => `https://www.imdb.com/title/${id}/`
	},
	[MediaConnectionTypes.Letterboxd]: {
		name: 'Letterboxd',
		linkFn: (id: string) => `https://letterboxd.com/film/${id}/`
	},
	[MediaConnectionTypes.vndb]: {
		name: 'vndb',
		linkFn: (id: string) => `https://vndb.org/${id}`
	},
	[MediaConnectionTypes.ErogameScape]: {
		name: 'ErogameScape',
		linkFn: (id: string) =>
			`https://erogamescape.dyndns.org/~ap2/ero/toukei_kaiseki/game.php?game=${id}`
	},
	[MediaConnectionTypes.VGMdb]: {
		name: 'VGMdb',
		linkFn: (id: string) => `https://vgmdb.net/product/${id}`
	}
} as const satisfies Record<MediaConnectionTypes, { name: string; linkFn: (id: string) => string }>;
