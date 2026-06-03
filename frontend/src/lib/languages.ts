import client from '$lib/api';
import { languages } from '$lib/enums/language';
import { setLocale } from '$lib/paraglide/runtime';

export const set_lang = async (lang: keyof typeof languages, logged_in: boolean) => {
	if (logged_in)
		await client.POST('/api/profile/prefs', { fetch, body: { LANGUAGE: languages[lang].id } });

	setLocale(lang);
};
