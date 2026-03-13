<script lang="ts">
	import { EntityModelRoutes, PostCategories } from './enums';
	import { m } from './paraglide/messages';
	import { timeAgo } from './ui';

	interface Post {
		id: number | string;
		title: string;
		entities?: { id: string | number; entity: string }[];
		category?: number;
		added_by: { username: string };
		modified: string;
	}

	interface Props {
		posts: Post[];
		showCategory?: boolean;
		showAuthor?: boolean;
		entityFilter?: (entity: { id: string | number; entity: string }) => boolean;
	}

	let { posts, showCategory = false, showAuthor = true, entityFilter }: Props = $props();
</script>

<table class="w-full table-fixed">
	<thead>
		<tr>
			<th class="text-left">{m.large_factual_octopus_exhale()}</th>
			{#if showCategory}<th class="w-32 text-left">{m.plane_awful_bobcat_spark()}</th>{/if}
			{#if showAuthor}<th class="w-32 text-left">{m.crisp_red_canary_tickle()}</th>{/if}
			<th class="w-64 text-right">{m.super_agent_pigeon_aim()}</th>
		</tr>
	</thead>
	<tbody>
		{#each posts as post, i (i)}
			{@const entities = entityFilter
				? (post.entities?.filter(entityFilter) ?? [])
				: (post.entities ?? [])}
			<tr>
				<td>
					<a href="/post/{post.id}">{post.title}</a>
					{#if entities.length}
						<span class="text-otodb-content-fainter ml-3 text-xs">
							{#each entities as { id, entity }, j (j)}
								{#if j > 0},{/if}
								<a href="/{EntityModelRoutes[entity]}/{id}"
									>{EntityModelRoutes[entity]}/{id}</a
								>
							{/each}
						</span>
					{/if}
				</td>
				{#if showCategory}<td>{PostCategories[post.category]()}</td>{/if}
				{#if showAuthor}
					<td><a href="/profile/{post.added_by.username}">{post.added_by.username}</a></td
					>
				{/if}
				<td class="text-right">
					<time title={new Date(post.modified).toLocaleString()}
						>{timeAgo(post.modified)}</time
					>
				</td>
			</tr>
		{/each}
	</tbody>
</table>
