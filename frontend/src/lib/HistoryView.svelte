<script lang="ts">
	import { m } from './paraglide/messages';

	let { historicals } = $props();
</script>

<table class="w-full table-auto text-center">
	<tbody>
		<tr>
			<th>User</th><th>{m.super_agent_pigeon_aim()}</th><th>Changes</th><th>Reason</th>
		</tr>
		{#each historicals as entry, i (i)}
			<tr
				><td>
					<a href="/profile/{entry.user}">{entry.user}</a>
				</td><td>
					{new Date(entry.date).toLocaleDateString()}
				</td><td
					>{#each entry.delta as d, i (i)}<div class="flex flex-row gap-2 p-2">
							<!-- eslint-disable-next-line svelte/no-at-html-tags -->
							<span>{d.field}:</span>{@html d.html}
						</div>{/each}</td
				><td>
					{entry.reason}
				</td></tr
			>
		{/each}
	</tbody>
</table>
