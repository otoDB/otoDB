<script lang="ts">
	import { buildEntityRoutes, type EntityModelType } from './enums';
	import { postCategory, resolvePostCategoryKeyById } from '$lib/enums/PostCategory';
	import { m } from './paraglide/messages';
	import TimeAgo from './TimeAgo.svelte';

	interface Post {
		id: number | string;
		title: string;
		entities?: { id: string | number; entity: EntityModelType }[];
		category: number;
		added_by: { username: string };
		modified: string;
		last_post_by?: string | null;
		last_post_at?: string | null;
	}

	interface Props {
		posts: Post[];
		showCategory?: boolean;
		showAuthor?: boolean;
		entityFilter?: (entity: { id: string | number; entity: EntityModelType }) => boolean;
	}

	let { posts, showCategory = false, showAuthor = true, entityFilter }: Props = $props();
</script>

<table class="w-full table-fixed">
	<thead>
		<tr>
			<th class="text-left">{m.large_factual_octopus_exhale()}</th>
			{#if showCategory}<th class="w-32 text-left">{m.plane_awful_bobcat_spark()}</th>{/if}
			{#if showAuthor}<th class="w-32 text-left">{m.crisp_red_canary_tickle()}</th>{/if}
			<th class="w-64 text-right">{m.plain_polite_eagle_build()}</th>
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
				<td>
					<a href="/post/{post.id}">{post.title}</a>
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
					<td>{postCategory[resolvePostCategoryKeyById(post.category)].nameFn()}</td>
				{/if}
				{#if showAuthor}
					<td><a href="/profile/{post.added_by.username}">{post.added_by.username}</a></td
					>
				{/if}
				<td class="text-right">
					<a href="/profile/{lastUser}">{lastUser}</a>
					@
					<TimeAgo date={lastTime} />
				</td>
			</tr>
		{/each}
	</tbody>
</table>
