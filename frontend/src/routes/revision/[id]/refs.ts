import { getContext, setContext } from 'svelte';
import type { components } from '$lib/schema';

/** Lookup maps a revision's changes reference, shared via context so leaf
 *  components (RefValue/Value) can resolve refs without prop-drilling. */
export interface RevisionRefs {
	/** Keyed by work id -> slim work data, for rendering mediawork cards. */
	readonly works: Record<string, components['schemas']['SlimWorkSchema']>;
	/** Keyed by `model:id` -> display label for non-work FK refs. */
	readonly labels: Record<string, string>;
}

const REVISION_REFS = Symbol('revision-refs');

export const setRevisionRefs = (refs: RevisionRefs): RevisionRefs =>
	setContext(REVISION_REFS, refs);

export const getRevisionRefs = (): RevisionRefs => getContext(REVISION_REFS);
