import { writable } from 'svelte/store';
import { browser } from '$app/environment';

const storedBackground: string = browser ? localStorage.getItem('background') || 'none' : 'none';

export const background = writable<string>(storedBackground);

background.subscribe((value) => {
	if (browser) localStorage.setItem('background', value || 'none');
});
