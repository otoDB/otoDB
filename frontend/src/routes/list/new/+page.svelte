<script lang="ts">
	import Section from "$lib/Section.svelte";
	import type { PageProps } from "./$types";
  import { m } from '$lib/paraglide/messages.js';
	import { enhance } from "$app/forms";

  let { form }: PageProps = $props();
</script>

<svelte:head>
    <title>New List</title>
</svelte:head>

<Section title="New List" menuLinks={[{pathname: 'list/new', title: 'New'}, {pathname: 'list/import', title: 'Import'}]}>
<form use:enhance method="POST">
  {#if form?.failed}<p class="error">Failed!</p>{/if}
  <table><tbody>
    <tr><th><label for="name">Name</label></th><td><input type="text" name="name" value={form?.name ?? ''}/></td></tr>
    <tr><th><label for="description">Description</label></th><td><textarea name="description" value={form?.description ?? ''}></textarea></td></tr>
  </tbody></table>
  <input type="submit"/>
</form>
</Section>
