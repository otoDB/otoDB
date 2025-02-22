<script lang="ts">
	import Section from "../../Section.svelte";
	import CollapsibleText from "./CollapsibleText.svelte";
    let { data } = $props();

</script>

<svelte:head>
	<title>Work: {data.title}</title>
</svelte:head>

<Section title="Work: {data.title}">
    <div id="infobox">
      <img src="{data.thumbnail}" alt="{data.title}">
      <div>
        <table>
        <tbody>
            <tr><th>Title</th><td>{data.title}</td></tr>
            <tr><th>Description</th><td>{@html data.description}</td></tr>
            <tr><th>Rating</th><td>{data.rating}</td></tr>
        </tbody>
        </table>
{#if data.user}
        <h2>User options</h2>
        <table>
        <tbody>
            <tr>
                <th>Lists</th>
                <td>
                    <button>Add/Remove...</button>
                </td>
            </tr>
        </tbody>
        </table>
{/if} 
        </div>
        <ul id="work-tags">
            {#each data.tags as tag}
                <li><a href="#{tag.slug}">{tag.name}</a></li>
            {/each}
        </ul>
    </div>
</Section>

<Section title="Work Sources">
    {#snippet menu()}
    <a href="#TODO">Add source</a>
    {/snippet}
    <table class="w-full">
        <thead><tr>
            <th>Title</th>
            <th>Desciption</th>
            <th>Platform</th>
            <th>Date</th>
            <th>Official</th>
            <th>Available</th>
            <th>Resolution</th>
            <th>Link</th>
{#if data.user}
            <th>Refresh</th>
{/if}
        </tr></thead>
    <tbody>
        {#each data.sources as src}
        <tr>
            <td>{src.title}</td>
            <td><CollapsibleText text={src.description}></CollapsibleText></td>
            <td>{src.platform}</td><td>{src.published_date}</td>
            <td>{src.work_origin}</td><td>{src.work_status}</td>
            <td>{src.work_width}x{src.work_height}</td><td><a href="{src.url}" target="_blank" rel="noopener noreferrer">Link</a></td>
{#if data.user}
            <td><button type="submit">Refresh</button></td>
{/if}
        </tr>
        {/each}
      </tbody>
    </table>
</Section>
<Section title="Comments">
     include 'comments.html' with object=work 
</Section>

<style>
#infobox {
    display: grid;
    grid-template-columns: 1fr 2fr;
    column-gap: 2rem;
    align-items: center;
}
#work-tags {
    grid-column: 1 / span 2;
    border-top: var(--otodb-faint-content) 1px solid;
    margin-top: 2rem;
    display: flex;
    gap: .3rem 2rem;
    flex-wrap: wrap;
    &> li {
        margin: 0;
    }
}
</style>
