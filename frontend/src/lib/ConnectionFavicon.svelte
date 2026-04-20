<script lang="ts">
	import faviconAniDB from '$lib/connection_favicon/AniDB.png';
	import faviconAniKore from '$lib/connection_favicon/AniKore.png';
	import faviconAniList from '$lib/connection_favicon/AniList.png';
	import faviconAnimePlanet from '$lib/connection_favicon/Anime-Planet.png';
	import faviconBangumi from '$lib/connection_favicon/Bangumi.png';
	import faviconBilibili from '$lib/connection_favicon/Bilibili.png';
	import faviconBluesky from '$lib/connection_favicon/Bluesky.png';
	import faviconDiscogs from '$lib/connection_favicon/Discogs.png';
	import faviconErogameScape from '$lib/connection_favicon/ErogameScape.png';
	import faviconIMDb from '$lib/connection_favicon/IMDb.png';
	import faviconKitsu from '$lib/connection_favicon/Kitsu.png';
	import faviconKnowYourMeme from '$lib/connection_favicon/Know Your Meme.png';
	import faviconLetterboxd from '$lib/connection_favicon/Letterboxd.png';
	import faviconMusicBrainz from '$lib/connection_favicon/MusicBrainz.png';
	import faviconMyAnimeList from '$lib/connection_favicon/MyAnimeList.png';
	import faviconNNDMedleyWiki from '$lib/connection_favicon/NND Medley Wiki.png';
	import faviconNamuWiki from '$lib/connection_favicon/Namu Wiki.png';
	import faviconNiconicoEncyclopedia from '$lib/connection_favicon/Niconico Encyclopedia.png';
	import faviconNiconico from '$lib/connection_favicon/Niconico.png';
	import faviconPixivDictionary from '$lib/connection_favicon/Pixiv Dictionary.png';
	import faviconRateYourMusic from '$lib/connection_favicon/Rate Your Music.png';
	import faviconRemyWiki from '$lib/connection_favicon/RemyWiki.png';
	import faviconSilentBlue from '$lib/connection_favicon/Silent Blue.png';
	import faviconSoundcloud from '$lib/connection_favicon/Soundcloud.png';
	import faviconModArchive from '$lib/connection_favicon/The Mod Archive.png';
	import faviconTouhouDB from '$lib/connection_favicon/TouhouDB.png';
	import faviconTwitter from '$lib/connection_favicon/Twitter.png';
	import faviconVGMdb from '$lib/connection_favicon/VGMdb.png';
	import faviconVocaDB from '$lib/connection_favicon/VocaDB.png';
	import faviconWebsite from '$lib/connection_favicon/Website.png';
	import faviconWikipediaEn from '$lib/connection_favicon/Wikipedia (en).png';
	import faviconYouTube from '$lib/connection_favicon/YouTube.png';
	import faviconZenius from '$lib/connection_favicon/Zenius -I- vanisher.com.png';
	import faviconOtomadWiki from '$lib/connection_favicon/otomad.wiki.png';
	import faviconVndb from '$lib/connection_favicon/vndb.png';
	import faviconDoujinMusicInfo from '$lib/connection_favicon/同人音楽info.png';
	import faviconOtomadWiki2 from '$lib/connection_favicon/音MAD Wiki 2.png';
	import type { mediaConnectionMap } from '$lib/enums/mediaConnection';
	import type { profileConnectionMap } from '$lib/enums/profileConnection';
	import type { songConnectionMap } from '$lib/enums/songConnection';
	import type { TagWorkConnectionMap } from '$lib/enums/tagWorkConnection';

	type FaviconKey =
		| (typeof TagWorkConnectionMap)[keyof typeof TagWorkConnectionMap]['name']
		| (typeof mediaConnectionMap)[keyof typeof mediaConnectionMap]['name']
		| (typeof songConnectionMap)[keyof typeof songConnectionMap]['name']
		| (typeof profileConnectionMap)[keyof typeof profileConnectionMap]['name'];

	const img: Record<FaviconKey, string> = {
		'AniDB': faviconAniDB,
		'AniKore': faviconAniKore,
		'AniList': faviconAniList,
		'Anime-Planet': faviconAnimePlanet,
		'Bangumi': faviconBangumi,
		'Bilibili': faviconBilibili,
		'Bluesky': faviconBluesky,
		'Discogs': faviconDiscogs,
		'ErogameScape': faviconErogameScape,
		'IMDb': faviconIMDb,
		'Kitsu': faviconKitsu,
		'Know Your Meme': faviconKnowYourMeme,
		'Letterboxd': faviconLetterboxd,
		'The Mod Archive': faviconModArchive,
		'MusicBrainz': faviconMusicBrainz,
		'MyAnimeList': faviconMyAnimeList,
		'NND Medley Wiki': faviconNNDMedleyWiki,
		'Namu Wiki': faviconNamuWiki,
		'Niconico Encyclopedia': faviconNiconicoEncyclopedia,
		'Niconico': faviconNiconico,
		'Pixiv Dictionary': faviconPixivDictionary,
		'Rate Your Music': faviconRateYourMusic,
		'RemyWiki': faviconRemyWiki,
		'Silent Blue': faviconSilentBlue,
		'Soundcloud': faviconSoundcloud,
		'TouhouDB': faviconTouhouDB,
		'Twitter': faviconTwitter,
		'VGMdb': faviconVGMdb,
		'VocaDB': faviconVocaDB,
		'Wikipedia (en)': faviconWikipediaEn,
		'YouTube': faviconYouTube,
		'Zenius -I- vanisher.com': faviconZenius,
		'otomad.wiki': faviconOtomadWiki,
		'vndb': faviconVndb,
		'同人音楽info': faviconDoujinMusicInfo,
		'音MAD Wiki 2': faviconOtomadWiki2,
		'Website': faviconWebsite
	};

	let { type, ...props }: { type: FaviconKey; class?: string } = $props();
</script>

<img alt={type} src={img[type]} class={[props.class]} />
