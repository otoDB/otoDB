<script lang="ts">
	import { m } from '$lib/paraglide/messages.js';
	const { text, cutoff = 25 } = $props();
</script>

<label>
	<input type="checkbox" />
	<span>
		[{m.tough_early_sparrow_bask()}]
	</span>
	<span>{text}</span>
</label>

<style>
	input {
		display: none;
		& + span {
			display: inline;
		}
		& + span + span {
			display: none;
		}
		&:checked + span {
			display: none;
		}
		&:checked + span + span {
			display: inline;
		}
	}
</style>
