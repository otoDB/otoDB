import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { Levels, Platform, WorkOrigin, WorkStatus, type components } from '$lib/schema';
import ExternalEmbed from './ExternalEmbed.svelte';

type WorkSourceSchema = components['schemas']['WorkSourceSchema'];

const addedBy = {
	id: '1',
	level: Levels.Member,
	date_created: '2024-01-01T00:00:00Z',
	username: 'member_user'
};

/**
 * The `source_id` values below are placeholders shaped like the real thing, so the
 * players themselves render their "not found" state. What the stories demonstrate is
 * the per-platform iframe each branch builds, not the third party content.
 */
const source = (
	platform: Platform,
	source_id: string,
	overrides: Partial<WorkSourceSchema> = {}
): WorkSourceSchema => ({
	id: '1',
	added_by: addedBy,
	thumbnail: null,
	media_title: null,
	platform,
	work_origin: WorkOrigin.Author,
	work_status: WorkStatus.Available,
	url: 'https://example.com/',
	published_date: '2024-01-05',
	work_width: null,
	work_height: null,
	work_duration: null,
	title: 'A sample work',
	description: null,
	source_id,
	uploader_id: null,
	is_pending: false,
	media: null,
	...overrides
});

const meta = {
	component: ExternalEmbed,
	args: {
		src: source(Platform.YouTube, 'sample12345'),
		width: 560,
		height: 315,
		autoplay: false
	}
} satisfies Meta<ComponentProps<typeof ExternalEmbed>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof ExternalEmbed>>;

/** A YouTube source, embedded through the cookie-less `youtube-nocookie.com` player. */
export const YouTube: Story = {
	args: { src: source(Platform.YouTube, 'sample12345') }
};

/** A Niconico source. */
export const Niconico: Story = {
	args: { src: source(Platform.Niconico, 'sm2057168') }
};

/** A Bilibili source, addressed by its `BV` id. */
export const Bilibili: Story = {
	args: { src: source(Platform.Bilibili, 'BV1sample000') }
};

/** A SoundCloud source, addressed by its numeric track id. */
export const SoundCloud: Story = {
	args: { src: source(Platform.SoundCloud, '123456789') }
};

/**
 * A Twitter source with no known dimensions: the embed falls back to the `height` prop
 * because the aspect ratio cannot be derived.
 */
export const Twitter: Story = {
	args: { src: source(Platform.Twitter, '1234567890123456789') }
};

/**
 * A Twitter source that knows its dimensions: the embed height is derived from the
 * source aspect ratio instead of the `height` prop.
 */
export const TwitterWithKnownAspectRatio: Story = {
	args: {
		src: source(Platform.Twitter, '1234567890123456789', {
			work_width: 1280,
			work_height: 720
		})
	}
};

/** An AcFun source. */
export const AcFun: Story = {
	args: { src: source(Platform.AcFun, 'ac1234567') }
};

/** A Vimeo source, addressed by its numeric video id. */
export const Vimeo: Story = {
	args: { src: source(Platform.Vimeo, '123456789') }
};

/** Autoplay enabled, the default the component ships with. */
export const Autoplay: Story = {
	args: { autoplay: true }
};

/** A smaller player, e.g. an inline preview rather than the main viewer. */
export const CustomSize: Story = {
	args: { width: 320, height: 180 }
};
