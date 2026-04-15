<script lang="ts">
	import faviconAniDB from './connection_favicon/AniDB.png';
	import faviconAniKore from './connection_favicon/AniKore.png';
	import faviconAniList from './connection_favicon/AniList.png';
	import faviconAnimePlanet from './connection_favicon/Anime-Planet.png';
	import faviconBangumi from './connection_favicon/Bangumi.png';
	import faviconBilibili from './connection_favicon/Bilibili.png';
	import faviconBluesky from './connection_favicon/Bluesky.png';
	import faviconDiscogs from './connection_favicon/Discogs.png';
	import faviconErogameScape from './connection_favicon/ErogameScape.png';
	import faviconIMDb from './connection_favicon/IMDb.png';
	import faviconKitsu from './connection_favicon/Kitsu.png';
	import faviconKnowYourMeme from './connection_favicon/Know Your Meme.png';
	import faviconLetterboxd from './connection_favicon/Letterboxd.png';
	import faviconModArchive from './connection_favicon/The Mod Archive.png';
	import faviconMusicBrainz from './connection_favicon/MusicBrainz.png';
	import faviconMyAnimeList from './connection_favicon/MyAnimeList.png';
	import faviconNNDMedleyWiki from './connection_favicon/NND Medley Wiki.png';
	import faviconNamuWiki from './connection_favicon/Namu Wiki.png';
	import faviconNiconicoEncyclopedia from './connection_favicon/Niconico Encyclopedia.png';
	import faviconNiconico from './connection_favicon/Niconico.png';
	import faviconPixivDictionary from './connection_favicon/Pixiv Dictionary.png';
	import faviconRateYourMusic from './connection_favicon/Rate Your Music.png';
	import faviconRemyWiki from './connection_favicon/RemyWiki.png';
	import faviconSilentBlue from './connection_favicon/Silent Blue.png';
	import faviconTouhouDB from './connection_favicon/TouhouDB.png';
	import faviconTwitter from './connection_favicon/Twitter.png';
	import faviconVGMdb from './connection_favicon/VGMdb.png';
	import faviconVocaDB from './connection_favicon/VocaDB.png';
	import faviconWebsite from './connection_favicon/Website.png';
	import faviconWikipediaEn from './connection_favicon/Wikipedia (en).png';
	import faviconYouTube from './connection_favicon/YouTube.png';
	import faviconZenius from './connection_favicon/Zenius -I- vanisher.com.png';
	import faviconOtomadWiki from './connection_favicon/otomad.wiki.png';
	import faviconVndb from './connection_favicon/vndb.png';
	import faviconDoujinMusicInfo from './connection_favicon/同人音楽info.png';
	import faviconOtomadWiki2 from './connection_favicon/音MAD Wiki 2.png';
	import faviconSoundcloud from './connection_favicon/Soundcloud.png';
	import type { TagWorkConnection } from '$lib/enums/TagWorkConnection';
	import type { MediaConnection } from '$lib/enums/MediaConnection';
	import type { SongConnection } from '$lib/enums/SongConnection';
	import type { ProfileConnection } from '$lib/enums/ProfileConnection';

	type FaviconKey =
		| (typeof TagWorkConnection)[keyof typeof TagWorkConnection]['name']
		| (typeof MediaConnection)[keyof typeof MediaConnection]['name']
		| (typeof SongConnection)[keyof typeof SongConnection]['name']
		| (typeof ProfileConnection)[keyof typeof ProfileConnection]['name'];

	const img: Record<FaviconKey, string> = {
		AniDB: faviconAniDB,
		AniKore: faviconAniKore,
		AniList: faviconAniList,
		'Anime-Planet': faviconAnimePlanet,
		Bangumi: faviconBangumi,
		Bilibili: faviconBilibili,
		Bluesky: faviconBluesky,
		Discogs: faviconDiscogs,
		ErogameScape: faviconErogameScape,
		IMDb: faviconIMDb,
		Kitsu: faviconKitsu,
		'Know Your Meme': faviconKnowYourMeme,
		Letterboxd: faviconLetterboxd,
		'The Mod Archive': faviconModArchive,
		MusicBrainz: faviconMusicBrainz,
		MyAnimeList: faviconMyAnimeList,
		'NND Medley Wiki': faviconNNDMedleyWiki,
		'Namu Wiki': faviconNamuWiki,
		'Niconico Encyclopedia': faviconNiconicoEncyclopedia,
		Niconico: faviconNiconico,
		'Pixiv Dictionary': faviconPixivDictionary,
		'Rate Your Music': faviconRateYourMusic,
		RemyWiki: faviconRemyWiki,
		'Silent Blue': faviconSilentBlue,
		Soundcloud: faviconSoundcloud,
		TouhouDB: faviconTouhouDB,
		Twitter: faviconTwitter,
		VGMdb: faviconVGMdb,
		VocaDB: faviconVocaDB,
		'Wikipedia (en)': faviconWikipediaEn,
		YouTube: faviconYouTube,
		'Zenius -I- vanisher.com': faviconZenius,
		'otomad.wiki': faviconOtomadWiki,
		vndb: faviconVndb,
		同人音楽info: faviconDoujinMusicInfo,
		'音MAD Wiki 2': faviconOtomadWiki2,
		Website: faviconWebsite
	};

	let { type, ...props }: { type: FaviconKey; class?: string } = $props();
</script>

<img alt={type} src={img[type]} class={[props.class]} />
