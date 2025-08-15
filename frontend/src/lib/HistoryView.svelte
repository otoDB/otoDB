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
					<a href="/profile/{entry.history_user}">{entry.history_user}</a>
				</td><td>
					{new Date(entry.history_date).toLocaleDateString()}
				</td><td
					>{#each entry.delta as d, i (i)}<div class="flex flex-row gap-2 p-2">
							<span>{d.field}:</span>{@html d.html}
						</div>{/each}</td
				><td>
					{entry.history_reason}
				</td></tr
			>
		{/each}
	</tbody>
</table>
