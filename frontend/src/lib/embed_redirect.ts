import { redirect } from '@sveltejs/kit';
import client from '$lib/api.server';
import { Platform, WorkStatus, type components } from '$lib/schema';

type WorkSource = components['schemas']['WorkSourceSchema'];

const UNFURLER_UA =
	/Discordbot|Twitterbot|Slackbot|TelegramBot|WhatsApp|facebookexternalhit|redditbot|Pinterest|vkShare|Mastodon|Pleroma|Misskey|Akkoma|Bluesky/i;

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

export async function redirectToEmbedSource(
	workId: string,
	request: Request,
	fetch: typeof globalThis.fetch,
	predicate: (s: WorkSource) => boolean = () => true
): Promise<never> {
	const workPath = `/work/${workId}`;

	const { data: sources } = await client.GET('/api/work/sources', {
		params: { query: { work_id: workId } },
		fetch
	});

	const source = sources?.find((s) => s.work_status !== WorkStatus.Down && predicate(s));
	if (!source) redirect(302, workPath);

	const ua = request.headers.get('user-agent') ?? '';
	if (UNFURLER_UA.test(ua)) {
		redirect(302, rewriteForEmbed(source.platform, source.url));
	}
	redirect(302, workPath);
}
