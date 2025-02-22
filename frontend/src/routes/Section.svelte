<script lang="ts">
    let { title, children, menu = null } = $props();
</script>

{#if menu}
{@render menu()}
{/if}

<section>
    <h1>{title}</h1>
    {@render children()}
</section>

<style>
section {
    background-color: var(--otodb-faint-bg);
    border: 1px solid var(--otodb-faint-content);
    padding: 0 1rem 1rem 1rem;
    margin-bottom: 1rem;
	& > h1 {
        font-size: x-large;
        font-weight: 600;
		text-align: initial;
	}
}
</style>
