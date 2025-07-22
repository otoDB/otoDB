<script lang="ts">
	import { page } from '$app/state';
	import { m } from '$lib/paraglide/messages.js';
	import { UserLevel } from '$lib/enums';

	let {
		user,
		close,
		...props
	}: {
		className?: string;
		user: {
			csrf: string;
			user_id: number;
			username: string;
			level: number;
		};
		close: () => void;
	} = $props();

	let search_type = $state('work');
</script>

{#snippet link(pathname: string, title: string)}
	<li>
		<a
			href={pathname}
			class="aria-[current=page]:text-otodb-content-fainter text-xl no-underline"
			aria-current={page.url.pathname === pathname ? 'page' : undefined}
			onclick={close}
		>
			{title}
		</a>
	</li>
{/snippet}

<nav
	class={[
		props.className,
		'bg-otodb-bg-faint flex flex-col gap-y-2 overflow-y-scroll px-8 py-16'
	]}
>
	<div class="border-otodb-content-faint bg-otodb-bg-faint mb-8 border">
		<form target="_self" method="get" action="/{search_type}/search" class="flex w-full">
			<select bind:value={search_type} class="pl-1">
				<option value="work">{m.grand_merry_fly_succeed()}</option>
				<option value="tag">{m.empty_legal_chicken_taste()}</option>
				<option value="list">{m.stale_loose_squid_cut()}</option>
			</select>
			<input
				type="text"
				name="query"
				placeholder="{m.mean_top_antelope_love()}..."
				class="flex-auto px-2 py-1"
			/>
			<button
				type="submit"
				class="hover:bg-otodb-content-primary px-1"
				style="border: none !important;"
				aria-label="Search"
				onclick={close}
			>
				<svg class="h-[16px] w-[16px]">
					<use href="/search.svg#img"></use>
				</svg>
			</button>
		</form>
	</div>

	<div>
		<div class="border-otodb-content-faint mb-2 border-b text-xs">
			{m.clean_kind_stork_affirm()}
		</div>
		<ul class="mt-4 list-none space-y-4">
			{@render link('/', m.fine_late_chicken_quiz())}
			{@render link('/post/2', m.noble_fine_iguana_pull())}
			{@render link('/work/search', m.grand_merry_fly_succeed())}
			{#if user?.level >= UserLevel.MEMBER}
				{@render link('/work/tags_needed', `> ${m.spry_late_kudu_assure()}`)}
			{/if}
			{@render link('/tag/search', m.empty_legal_chicken_taste())}
			{@render link('/list/search', m.stale_loose_squid_cut())}
			{@render link('/work/random', m.fuzzy_chunky_niklas_peek())}
		</ul>
	</div>
	<div class="mt-8">
		<div class="border-otodb-content-faint mb-2 border-b text-xs">
			{m.maroon_least_pony_evoke()}
		</div>
		<ul class="mt-4 list-none space-y-4">
			{#if !user}
				{@render link('/login', m.inner_stale_anteater_walk())}
				{@render link('/register', m.blue_whole_camel_type())}
			{:else}
				{@render link('/post/1', m.bald_ideal_gadfly_jest())}
				{@render link('/work/add', m.fluffy_crisp_horse_imagine())}
				{@render link(`/profile/${user.username}`, m.petty_basic_sheep_win())}
				{@render link(`/profile/${user.username}/lists`, m.jumpy_honest_mole_exhale())}
				{@render link(
					`/profile/${user.username}/submissions`,
					m.flaky_gross_marlin_evoke()
				)}
				{@render link(`/profile/${user.username}/settings`, m.orange_born_seal_ascend())}
				<li
					aria-current={page.url.pathname === `/logout` ? 'page' : undefined}
					class="mt-4"
				>
					<a
						href="/logout"
						data-sveltekit-preload-data="tap"
						data-sveltekit-reload
						class="no-underline">{m.best_front_swallow_play()}</a
					>
				</li>
			{/if}
		</ul>
	</div>
	{#if user?.level >= UserLevel.EDITOR}
		<div class="mt-8">
			<div class="border-otodb-content-faint mb-2 border-b text-xs">
				{m.these_bold_gorilla_flip()}
			</div>
			<ul class="mt-4 list-none space-y-4">
				{@render link('/work/unbound', m.tense_small_firefox_lock())}
				{@render link('/tag/alias', m.front_maroon_hamster_urge())}
				{@render link('/work/merge', m.heroic_same_wasp_conquer())}
			</ul>
		</div>
	{/if}
	{#if user?.level >= UserLevel.ADMIN}
		<div class="mt-8">
			<div class="border-otodb-content-faint mb-2 border-b text-xs">
				{m.mellow_pink_starfish_cuddle()}
			</div>
			<ul class="mt-4 list-none space-y-4">
				<li>
					<a href="/admin" data-sveltekit-reload class="no-underline"
						>{m.simple_few_sheep_lend()}</a
					>
				</li>
			</ul>
		</div>
	{/if}
</nav>
