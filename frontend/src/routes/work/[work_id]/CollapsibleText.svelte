<script lang="ts">
    const { text, cutoff = 25 } = $props();
</script>

<label>
    <input type="checkbox">
    <span>
        {#if text.length > cutoff}
        {text.slice(0, cutoff) + '...(click to expand)'}
        {:else}
        {text}
        {/if}
    </span>
    <span>{text}</span>
</label>

<style>
    input {
        display: none;
        &+ span {
            display: inline;
        }
        &+ span + span {
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
