<script lang="ts">
	import Section from "$lib/Section.svelte";
	import type { PageProps } from "./$types";
  import { m } from '$lib/paraglide/messages.js';
	import { enhance } from "$app/forms";

  let { form }: PageProps = $props();
</script>

<svelte:head>
    <title>Import List</title>
</svelte:head>

<Section title="Import List" menuLinks={[{pathname: 'list/new', title: 'New'}, {pathname: 'list/import', title: 'Import'}]}>
  <p>Currently accepted types of lists:</p>
<ul>
  <li>YouTube Playlists</li>
  <li>Niconico Mylists</li>
  <li>Bilibili Playlists</li>
</ul>
<form use:enhance method="POST">
  {#if form?.failed}<p class="error">Failed!</p>{/if}
  <table><tbody>
    <tr><th><label for="url">URL</label></th><td><input type="text" name="url" value={form?.url ?? ''}></td></tr>
  </tbody></table>
  <input type="submit"/>
  </form>
</Section>
