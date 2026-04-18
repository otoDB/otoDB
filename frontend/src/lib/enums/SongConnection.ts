import { SongConnectionTypes } from '$lib/schema';

export const SongConnectionMap = {
	[SongConnectionTypes.VGMdb]: {
		name: 'VGMdb',
		linkFn: (id: string) => `https://vgmdb.net/album/${id}`
	},
	[SongConnectionTypes.VocaDB]: {
		name: 'VocaDB',
		linkFn: (id: string) => `https://vocadb.net/S/${id}`
	},
	[SongConnectionTypes.Discogs]: {
		name: 'Discogs',
		linkFn: (id: string) => `https://www.discogs.com/master/${id}`
	},
	[SongConnectionTypes.MusicBrainz]: {
		name: 'MusicBrainz',
		linkFn: (id: string) => `https://musicbrainz.org/recording/${id}`
	},
	[SongConnectionTypes.Rate_Your_Music]: {
		name: 'Rate Your Music',
		linkFn: (id: string) => `https://rateyourmusic.com/song/${id}/`
	},
	[SongConnectionTypes.dojin_music_info]: {
		name: '同人音楽info',
		linkFn: (id: string) => `https://www.dojin-music.info/song/${id}`
	},
	[SongConnectionTypes.TouhouDB]: {
		name: 'TouhouDB',
		linkFn: (id: string) => `https://touhoudb.com/S/${id}`
	},
	[SongConnectionTypes.RemyWiki]: {
		name: 'RemyWiki',
		linkFn: (id: string) => `https://remywiki.com/${id}`
	},
	[SongConnectionTypes.Silent_Blue]: {
		name: 'Silent Blue',
		linkFn: (id: string) => `https://silentblue.remywiki.com/${id}`
	},
	[SongConnectionTypes.Zenius_I_vanisher_com]: {
		name: 'Zenius -I- vanisher.com',
		linkFn: (id: string) => `https://zenius-i-vanisher.com/v5.2/songdb.php?songid=${id}`
	},
	[SongConnectionTypes.NND_Medley_Wiki]: {
		name: 'NND Medley Wiki',
		linkFn: (id: string) => `https://medley.bepis.io/wiki/${id}`
	},
	[SongConnectionTypes.The_Mod_Archive]: {
		name: 'The Mod Archive',
		linkFn: (id: string) =>
			`https://modarchive.org/index.php?request=view_by_moduleid&query=${id}`
	}
} as const satisfies Record<SongConnectionTypes, { name: string; linkFn: (id: string) => string }>;
