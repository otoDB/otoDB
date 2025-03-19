<script lang="ts">
	import { page } from "$app/state";
    interface Props {
        title: string;
        menuLinks: { title: string, pathname: string }[] | null
    };
    let { title, children, menuLinks = null } = $props();
</script>

{#if menuLinks}
<menu>
    <ul>
        {#each menuLinks as {pathname, title}}
        <li aria-current={page.url.pathname.endsWith(encodeURI(pathname))}>
            <a href="/{pathname}">{title}</a>
        </li>
        {/each}
    </ul>
</menu>
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
