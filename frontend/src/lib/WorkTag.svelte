<script lang="ts">
	import { getTagDisplayName } from '$lib/api';
	import { creatorRole, resolveCreatorRoleKeyById } from '$lib/enums/creatorRole';
	import { WorkTagCategory } from '$lib/schema';
	import { WorkTagCategoryMap } from '$lib/enums/workTagCategory';

	interface Props {
		tag: {
			id: number;
			slug: string;
			category: WorkTagCategory;
			sample?: boolean;
			creator_roles?: Parameters<typeof resolveCreatorRoleKeyById>[0][] | null;
			lang_prefs: { lang: number; tag: string; slug: string }[];
			name: string;
		};
		selected?: boolean;
		onclick?: (tag: Props['tag']) => void;
		fade?: boolean;

		forTree?: boolean;
	}
	const { tag, onclick, selected = false, fade = false, forTree = false }: Props = $props();

	const category = $derived(tag.category);
	const sampleOverride = $derived(WorkTagCategoryMap[category].canSetAsSource && tag.sample);
	const isTemporary = $derived(tag.id === 0);
</script>

<a
	href="/tag/{tag.slug}"
	class={[
		'rounded-xl px-2',
		forTree ? 'border' : 'border-2',
		isTemporary ? 'border-dashed' : 'border-solid',
		{ 'opacity-50': fade || (onclick && !selected) }
	]}
	style="border-color: {WorkTagCategoryMap[sampleOverride ? WorkTagCategory.Source : category]
		.color};"
	data-sveltekit-preload-data={onclick ? 'off' : undefined}
	onclick={(e) => {
		if (onclick) {
			e.preventDefault();
			onclick(tag);
		}
	}}
	>{getTagDisplayName(tag)}
</a>
{#if category === WorkTagCategory.Creator && tag.creator_roles?.length}
	<address class="text-otodb-content-fainter inline px-1 text-xs">
		{#each tag.creator_roles as role, i (i)}{creatorRole[
				resolveCreatorRoleKeyById(role)
			].nameFn()}
			{#if i < tag.creator_roles.length - 1},&nbsp{/if}
		{/each}
	</address>
{/if}

<style>
	a {
		text-decoration: none;
	}
</style>
