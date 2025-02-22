<script lang="ts">
	import { base } from "$app/paths";
	import { page } from "$app/state";

    let { links } = $props();
</script>

<menu>
    <ul>
        {#each links as {pathname, title}}
        <li aria-current={page.url.pathname.endsWith(encodeURI(pathname))}>
            <a href="{base}/{pathname}">{title}</a>
        </li>
        {/each}
    </ul>
</menu>

<style>
menu {
    position: relative;
    top: 1px;
    &> ul {
    display: flex;
	margin: -.5rem 0 0 auto;
	gap: .3rem;
	width: max-content;
    list-style: none;
    flex-direction: row;
        &> li {
            background-color: var(--otodb-faint-bg);
            border: 1px solid var(--otodb-faint-content);
            padding-left: .2rem;
            padding-right: .2rem;
            &[aria-current="true"] {
                border-bottom: none;
                pointer-events: none;
            }
            &> a {
                text-decoration: none;
            }
        }
    }
}
</style>
