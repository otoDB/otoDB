<script lang="ts">
	import { languages } from '$lib/enums/language';
	import { set_lang } from '$lib/languages';
	import { m } from '$lib/paraglide/messages.js';
	import { getLocale, locales } from '$lib/paraglide/runtime';
	import type { ClassValue } from 'svelte/elements';

	let {
		class: className,
		user
	}: {
		class?: ClassValue;

		user: null | { username: string };
	} = $props();

	let query = $state('');
	let showDropdown = $derived(query.trim().length > 0);
</script>

<nav
	class={[
		className,
		'bg-otodb-bg-faint/85 border-b-otodb-content-faint h-[64px] border-b px-4 py-2'
	]}
>
	<div class="container mx-auto flex h-full items-center gap-8">
		<div class="flex-shrink-0">
			<a href="/" class="text-md font-mono italic no-underline!">
				{m.mild_loud_shad_enchant({ type: 'otoDB', name: m.glad_born_mouse_taste() })}
			</a>
		</div>
		<div class="flex flex-grow gap-x-4">
			<div class="relative w-full">
				<div
					class="bg-otodb-bg-faint/75 border-otodb-content-faint bg-otodb-bg-fainter/75 flex h-full w-full items-center border px-2"
				>
					<div class="icon-[gravity-ui--magnifier] text-base"></div>
					<input
						type="text"
						name="query"
						placeholder="{m.mean_top_antelope_love()}..."
						class="ml-2 w-full border-none bg-transparent py-1 text-lg outline-none"
						bind:value={query}
					/>
				</div>
				{#if showDropdown}
					<ul
						class="bg-otodb-bg-faint border-otodb-content-faint absolute top-full left-0 z-10 w-full list-none border"
					>
						<li>
							<a
								href="/work?query={encodeURIComponent(query)}"
								class="hover:bg-otodb-bg-fainter block px-3 py-2 no-underline"
							>
								{m.glad_front_stork_hop({ query })}
							</a>
						</li>
						<li>
							<a
								href="/tag?query={encodeURIComponent(query)}"
								class="hover:bg-otodb-bg-fainter block px-3 py-2 no-underline"
							>
								{m.glad_front_stork_tag({ query })}
							</a>
						</li>
						<li>
							<a
								href="/list?query={encodeURIComponent(query)}"
								class="hover:bg-otodb-bg-fainter block px-3 py-2 no-underline"
							>
								{m.glad_front_stork_list({ query })}
							</a>
						</li>
					</ul>
				{/if}
			</div>
		</div>
		<div class="flex flex-shrink-0 items-center">
			<span class="icon-[gravity-ui--globe] text-otodb-content-faint text-base"></span>
			<select
				onchange={(e) => {
					set_lang(e.currentTarget.value as (typeof locales)[number], !!user);
				}}
				value={getLocale()}
				class="ml-2 text-sm"
			>
				{#each locales as l (l)}
					<option value={l}>{languages[l].name}</option>
				{/each}
			</select>
		</div>
	</div>
</nav>
