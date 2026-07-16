import type { Meta, StoryObj } from '@storybook/sveltekit';
import { http, HttpResponse } from 'msw';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import {
	Levels,
	ModelsWithComments,
	NotificationReason,
	Route,
	type components
} from '$lib/schema';
import Page from './+page.svelte';

type Notification = components['schemas']['NotificationSchema'];

const handlers = [
	http.put('*/api/profile/notification', () => new HttpResponse(null, { status: 200 })),
	http.delete('*/api/profile/notification', () => new HttpResponse(null, { status: 200 }))
];

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const head = { title: m.free_keen_wren_exhale() };

const loggedInMember = {
	csrf: 'csrf-token',
	user_id: '1',
	username: 'member_user',
	level: Levels.Member,
	prefs: {
		THEME: 0,
		VIDEO_PLATFORM: 0,
		PREFER_AUTHOR_UPLOAD: false
	},
	notifs_count: 0,
	notifs_nonsub_count: 0
};

const baseData = {
	stats,
	head,
	user: loggedInMember,
	batch_size: 20
};

const commentNotification: Notification = {
	id: 'notif-1',
	comment: [ModelsWithComments.tagwork, 'tagwork-1'],
	threadpost: null,
	reason: NotificationReason.Reply,
	revision_user: null,
	revision_route: null,
	dismissed: false,
	revision: null,
	created_at: '2024-06-01T10:00:00Z'
};

const threadMentionNotification: Notification = {
	id: 'notif-2',
	comment: null,
	threadpost: ['example-thread', 3],
	reason: NotificationReason.Mention,
	revision_user: null,
	revision_route: null,
	dismissed: true,
	revision: null,
	created_at: '2024-06-02T10:00:00Z'
};

const threadLinkedNotification: Notification = {
	id: 'notif-3',
	comment: null,
	threadpost: ['example-thread', 5],
	reason: NotificationReason.Thread_Linked,
	revision_user: null,
	revision_route: null,
	dismissed: false,
	revision: null,
	created_at: '2024-06-03T10:00:00Z'
};

const revisionNotification: Notification = {
	id: 'notif-4',
	comment: null,
	threadpost: null,
	reason: NotificationReason.Reply,
	revision_user: 'editor_user',
	revision_route: Route.Tag_Work_Update,
	dismissed: false,
	revision: 100,
	created_at: '2024-06-04T10:00:00Z'
};

const dismissedRevisionNotification: Notification = {
	id: 'notif-5',
	comment: null,
	threadpost: null,
	reason: NotificationReason.Reply,
	revision_user: 'editor_user',
	revision_route: Route.Tag_Work_Alias,
	dismissed: true,
	revision: 101,
	created_at: '2024-06-05T10:00:00Z'
};

const meta = {
	component: Page,
	args: {
		data: {
			...baseData,
			nonsub_notifications: { items: [], count: 0 },
			sub_notifications: { items: [], count: 0 }
		}
	},
	parameters: {
		msw: { handlers }
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const Empty: Story = {};

export const WithNonSubNotifications: Story = {
	args: {
		data: {
			...baseData,
			nonsub_notifications: {
				items: [commentNotification, threadMentionNotification, threadLinkedNotification],
				count: 3
			},
			sub_notifications: { items: [], count: 0 }
		}
	}
};

export const WithSubNotifications: Story = {
	args: {
		data: {
			...baseData,
			nonsub_notifications: { items: [], count: 0 },
			sub_notifications: {
				items: [revisionNotification, dismissedRevisionNotification],
				count: 2
			}
		}
	}
};

export const Populated: Story = {
	args: {
		data: {
			...baseData,
			nonsub_notifications: {
				items: [commentNotification, threadMentionNotification, threadLinkedNotification],
				count: 45
			},
			sub_notifications: {
				items: [revisionNotification, dismissedRevisionNotification],
				count: 30
			}
		}
	}
};
