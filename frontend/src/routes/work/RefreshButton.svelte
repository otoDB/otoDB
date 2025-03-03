<script lang="ts">
	import { invalidateAll } from "$app/navigation";
	import client from "$lib/api";
    import * as m from '$lib/paraglide/messages.js';

    let { source, ...props } = $props();
    let clicked = $state(false);
    const action = async () => {
        clicked = true;
        const { error } = await client.POST('/api/work/refresh_source', { fetch, params: { query: { source_id: source.id } } });
        if (!error)
            invalidateAll();
    };
</script>

{#if !clicked} 
<button {...props} type="button" class="whitespace-nowrap" onclick={action}>{m.mushy_proof_hornet_dig()}</button>
{/if}
