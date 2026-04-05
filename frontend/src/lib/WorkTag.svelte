<script lang="ts">
	import { getTagDisplayName } from './api';
	import { resolveCreatorRoleById } from './CreatorRole';
	import { resolveWorkTagCategoryKeyById, WorkTagCategory } from './WorkTagCategory';

	interface Props {
		tag: {
			id: number;
			slug: string;
			category: Parameters<typeof resolveWorkTagCategoryKeyById>[0];
			sample: boolean;
			creator_roles: Parameters<typeof resolveCreatorRoleById>[0][] | null;
		};
		selected?: boolean;
		onClick?: (tag: Props['tag']) => void;
	}
	const { tag, selected = false, onClick }: Props = $props();

	const category = $derived(resolveWorkTagCategoryKeyById(tag.category));
	const sampleOverride = $derived(tag.sample);
</script>

<a
	href="/tag/{tag.slug}"
	class={[
		'rounded-xl border-2 px-2',
		category === 'GENERAL' ? 'border-dashed' : 'border-solid',
		{ 'opacity-50': onClick && !selected }
	]}
	style="border-color: {WorkTagCategory[sampleOverride ? 'SOURCE' : category].color};"
	data-sveltekit-preload-data={onClick ? 'off' : undefined}
	onclick={(e) => {
		if (onClick) {
			e.preventDefault();
			onClick(tag);
		}
	}}
	>{getTagDisplayName(tag)}
</a>
{#if category === 'CREATOR' && tag.creator_roles?.length}
	<address class="text-otodb-content-fainter inline px-1 text-xs">
		{#each tag.creator_roles as role, i (i)}{resolveCreatorRoleById(role).nameFn()}
			{#if i < tag.creator_roles.length - 1},&nbsp{/if}
		{/each}
	</address>
{/if}

<style>
	a {
		text-decoration: none;
	}
	ul > li > ul {
		&::before {
			content: '\21B3';
		}
		& > li > ul {
			margin-left: 0.5rem;
		}
	}
</style>
