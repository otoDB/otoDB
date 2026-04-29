<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import { isSOV, isSVO } from '$lib/enums/language';
</script>

<h4>
	{#if isSVO(getLocale())}
		{m.born_these_snake_devour()}
	{/if}
	<a href="/docs/editing_guidelines">{m.arable_direct_cougar_win()}</a>
	& <a href="/docs/faq">FAQ</a>
	{#if isSOV(getLocale())}{m.born_these_snake_devour()}{/if}
</h4>
