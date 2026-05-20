import { redirect } from '@sveltejs/kit';
import client from '$lib/api.server';
import { PlatformNames } from '$lib/enums';
import { Platform, WorkStatus } from '$lib/schema';
import type { RequestHandler } from './$types';

const UNFURLER_UA =
	/Discordbot|Twitterbot|Slackbot|TelegramBot|WhatsApp|facebookexternalhit|redditbot|Pinterest|vkShare|Mastodon|Pleroma|Misskey|Akkoma|Bluesky/i;

const PLATFORM_BY_NAME = new Map<string, Platform>(
	Object.entries(PlatformNames).map(([k, v]) => [v.toLowerCase(), Number(k) as Platform])
);

const EMBED_FIXER_HOSTNAMES: Partial<Record<Platform, string>> = {
	[Platform.Niconico]: 'nicovideo.gay',
	[Platform.Bilibili]: 'vxbilibili.com',
	[Platform.Twitter]: 'fixupx.com'
};

function rewriteForEmbed(platform: Platform, rawUrl: string): string {
	const u = new URL(rawUrl);
	const newHost = EMBED_FIXER_HOSTNAMES[platform];
	if (newHost) u.hostname = newHost;
	return u.toString();
}

export const GET: RequestHandler = async ({ params, request, fetch }) => {
	const workPath = `/work/${params.work_id}`;
	const platform = PLATFORM_BY_NAME.get(params.platform.toLowerCase());
	if (platform === undefined) redirect(302, workPath);

	const { data: sources } = await client.GET('/api/work/sources', {
		params: { query: { work_id: params.work_id } },
		fetch
	});

	const source = sources?.find((s) => s.platform === platform && s.work_status !== WorkStatus.Down);
	if (!source) redirect(302, workPath);

	const ua = request.headers.get('user-agent') ?? '';
	if (UNFURLER_UA.test(ua)) {
		redirect(302, rewriteForEmbed(platform, source.url));
	}
	redirect(302, workPath);
};
