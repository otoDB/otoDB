<script lang="ts">
	import { postCategoryNames } from '$lib/enums/postCategory';
	import type { PostCategory } from '$lib/schema';
	import { buildEntityRoutes, type EntityModelType } from './enums';
	import Icon from '$lib/Icon/Icon.svelte';
	import { m } from './paraglide/messages';
	import Time from '$lib/Time.svelte';
	import { ParaglideMessage } from '@inlang/paraglide-js-svelte';

	interface Post {
		id: string;
		title: string;
		entities?: { id: string; entity: EntityModelType }[];
		category: PostCategory;
		added_by: { username: string };
		modified: string;
		last_post_by?: string | null;
		last_post_at?: string | null;
		closed_at?: string | null;
		post_count?: number;
	}

	interface Props {
		posts: Post[];
		showCategory?: boolean;
		entityFilter?: (entity: { id: string; entity: EntityModelType }) => boolean;
	}

	let { posts, showCategory = false, entityFilter }: Props = $props();
</script>

<table class="w-full table-fixed">
	<thead>
		<tr>
			<th class="w-6"></th>
			<th class="text-left">{m.large_factual_octopus_exhale()}</th>
			{#if showCategory}<th class="w-32 text-left">{m.plane_awful_bobcat_spark()}</th>{/if}
			<th class="w-20 text-left">{m.these_full_lion_exhale()}</th>
			<th class="w-32 text-left">{m.funny_heroic_whale_gleam()}</th>
			<th class="w-64 text-left">{m.plain_polite_eagle_build()}</th>
		</tr>
	</thead>
	<tbody>
		{#each posts as post, i (i)}
			{@const entities = entityFilter
				? (post.entities?.filter(entityFilter) ?? [])
				: (post.entities ?? [])}
			{@const lastUser = post.last_post_by ?? post.added_by.username}
			{@const lastTime = post.last_post_at ?? post.modified}
			<tr>
				<td class="text-center">
					{#if post.closed_at}
						<Icon key="thread-closed" class="mx-auto block size-4" />
					{:else}
						<Icon key="thread-opened" class="mx-auto block size-4" />
					{/if}
				</td>
				<td>
					<a href="/thread/{post.id}">{post.title}</a>
					{#if entities.length}
						<span class="text-otodb-content-fainter ml-3 text-xs">
							{#each entities as { id, entity }, j (j)}
								{#if j > 0},{/if}
								<a href={buildEntityRoutes(entity, id)}>
									{buildEntityRoutes(entity, id)}
								</a>
							{/each}
						</span>
					{/if}
				</td>
				{#if showCategory}
					<td>{postCategoryNames[post.category]()}</td>
				{/if}
				<td class="text-left">{Math.max(0, (post.post_count ?? 0) - 1)}</td>
				<td><a href="/user/{post.added_by.username}">{post.added_by.username}</a></td>
				<td class="text-left">
					<Time format="relative" date={lastTime} />
					<ParaglideMessage message={m.noble_tidy_boar_lock} inputs={{}}>
						{#snippet content()}
							<a href="/user/{lastUser}">{lastUser}</a>
						{/snippet}
					</ParaglideMessage>
				</td>
			</tr>
		{/each}
	</tbody>
</table>
