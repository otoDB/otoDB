<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import client from '$lib/api';
	import { m } from '$lib/paraglide/messages.js';
	import { toast } from 'svelte-sonner';

	let { source, ...props } = $props();
	let clicked = $state(false);
	const action = async () => {
		clicked = true;
		const p = client.POST('/api/upload/refresh', {
			fetch,
			params: { query: { source_id: source.id } }
		});
		toast.promise(p, {
			loading: m.only_moving_cat_hint(),
			success: m.sound_careful_falcon_grow(),
			error: m.green_due_javelina_pop()
		});
		const { error } = await props;
		if (!error) invalidateAll();
	};
</script>

{#if !clicked}
	<button {...props} type="button" class="whitespace-nowrap" onclick={action}
		>{m.mushy_proof_hornet_dig()}</button
	>
{/if}
