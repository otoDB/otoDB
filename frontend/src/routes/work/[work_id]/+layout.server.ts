import client from '$lib/api.server';
import { getDisplayText, getTagDisplayName } from '$lib/ui';
import { hasUserLevel } from '$lib/enums/userLevel';
import { creatorRole } from '$lib/enums/creatorRole';
import { WorkTagCategoryMap } from '$lib/enums/workTagCategory';
import { m } from '$lib/paraglide/messages.js';
import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';
import { Levels, Rating, WorkTagCategory, type components } from '$lib/schema';

type WorkTag = components['schemas']['TagWorkInstanceSchema'];

export const load: LayoutServerLoad = async ({ params, fetch, locals, url }) => {
	const { data } = await client.GET('/api/work/work', {
		params: {
			query: {
				work_id: params.work_id
			}
		},
		fetch
	});

	if (data.id !== params.work_id)
		redirect(
			303,
			url.pathname.replace(encodeURIComponent(params.work_id), encodeURIComponent(data.id))
		);

	const loggedOut = !hasUserLevel(locals.user?.level, Levels.Member);

	const isSampled = (tag: WorkTag) => WorkTagCategoryMap[tag.category].canSetAsSource && tag.sample;
	const isThanksOnly = (tag: WorkTag) =>
		!!tag.creator_roles?.length &&
		tag.creator_roles.every((role) => role === creatorRole.THANKS.id);

	const tagsIn = (category: WorkTagCategory) =>
		data.tags.filter((tag) =>
			category === WorkTagCategory.Source
				? tag.category === WorkTagCategory.Source || isSampled(tag)
				: tag.category === category &&
					!isSampled(tag) &&
					(category !== WorkTagCategory.Creator || !isThanksOnly(tag))
		);

	// Collapse tag set along primary parenthood. For sources over the cap, we
	// keep only the highest-level applied tags, while creators and
	// songs keep only the lowest applied descendants.
	const roots = (tags: WorkTag[]) => {
		const ids = new Set(tags.map((tag) => tag.id));
		return tags.filter((tag) => !tag.primary_path.some((parent) => ids.has(parent.id)));
	};
	const leaves = (tags: WorkTag[]) => {
		const ancestorIds = new Set(tags.flatMap((tag) => tag.primary_path.map((parent) => parent.id)));
		return tags.filter((tag) => !ancestorIds.has(tag.id));
	};

	const creators = leaves(tagsIn(WorkTagCategory.Creator)).map(getTagDisplayName);
	const title = getDisplayText(data.title);
	const headTitle =
		creators.length && creators.length <= 5
			? m.tidy_calm_gecko_sail({ title, creator: creators.join(', ') })
			: title;

	// Categories with more collapsed tags than their cap are left out entirely,
	// and songs are only shown alongside a creator or source.
	const capped = (names: string[], max: number) =>
		names.length && names.length <= max ? names : null;
	const creatorDetail = capped(creators, 5);
	const songDetail = capped(leaves(tagsIn(WorkTagCategory.Song)).map(getTagDisplayName), 2);
	const sourceTags = tagsIn(WorkTagCategory.Source);
	const sourceDetail = capped(
		// If two sources, just show them all, otherwise only the highest-level sources
		(sourceTags.length <= 2 ? sourceTags : roots(sourceTags))
			.toSorted((a, b) => a.primary_path.length - b.primary_path.length)
			.map(getTagDisplayName),
		2
	);

	const entries: [WorkTagCategory, string[] | null][] = [
		[WorkTagCategory.Creator, creatorDetail],
		[WorkTagCategory.Song, creatorDetail || sourceDetail ? songDetail : null],
		[WorkTagCategory.Source, sourceDetail]
	];
	const details = entries
		.filter((entry): entry is [WorkTagCategory, string[]] => !!entry[1])
		.map(([category, names]) => `${WorkTagCategoryMap[category].nameFn()}: ${names.join(', ')}`)
		.join(' · ');
	const headDescription = details
		? m.zesty_brief_mole_chant({ details })
		: m.plain_witty_crane_hum();

	return {
		links: [
			{
				pathname: `work/${params.work_id}`,
				title: m.grand_merry_fly_succeed() + ' ' + params.work_id
			},
			...(loggedOut
				? []
				: [
						{
							pathname: `work/${params.work_id}/tags`,
							title: m.empty_legal_chicken_taste()
						}
					]),
			...(data.relations[0].length
				? [
						{
							pathname: `work/${params.work_id}/relations`,
							title: m.alive_these_jay_pick()
						}
					]
				: []),
			...(loggedOut
				? []
				: [
						{
							pathname: `work/${params.work_id}/edit`,
							title: m.minor_crisp_cobra_list()
						}
					]),
			{
				pathname: `work/${params.work_id}/threads`,
				title: m.big_tiny_kitten_devour()
			},
			{
				pathname: `work/${params.work_id}/history`,
				title: m.giant_away_scallop_hike()
			},
			{
				pathname: `work/${params.work_id}/moderation`,
				title: m.minor_inner_lynx_adapt()
			}
		],
		...data,
		head: {
			title: headTitle,
			description: headDescription,
			image: data.rating <= 1 ? data.thumbnail : null,
			isExplicit: data.rating === Rating.Explicit,
			breadcrumbs: [
				{ name: m.fine_late_chicken_quiz(), url: '/' },
				{ name: m.grand_merry_fly_succeed(), url: '/work' },
				{
					name: getDisplayText(data.title),
					url: `/work/${params.work_id}`
				}
			]
		}
	};
};
