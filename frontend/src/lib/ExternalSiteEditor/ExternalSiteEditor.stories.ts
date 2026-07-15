import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { expect, userEvent, within } from 'storybook/test';
import ExternalSiteEditor from './ExternalSiteEditor.svelte';

const meta = {
	component: ExternalSiteEditor
} satisfies Meta<ComponentProps<typeof ExternalSiteEditor>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof ExternalSiteEditor>>;

export const Empty: Story = {
	args: { urls: [] }
};

export const WithUrls: Story = {
	args: {
		urls: [
			'https://bsky.app/profile/example.bsky.social',
			'https://twitter.com/example/',
			'https://www.youtube.com/@example',
			'https://www.nicovideo.jp/user/12345/',
			'https://soundcloud.com/example',
			'https://vgmdb.net/album/12345',
			'https://example.com/profile/example'
		]
	}
};

export const AddingUrlConfirmsIt: Story = {
	args: { urls: [] },
	play: async ({ canvasElement }) => {
		const canvas = within(canvasElement);
		const url = 'https://bsky.app/profile/example.bsky.social';

		const draftInput = canvas.getByRole('textbox');
		await userEvent.type(draftInput, url);
		await userEvent.click(canvas.getByRole('button', { name: 'Add' }));

		const confirmedInput = canvas.getByDisplayValue(url);
		await expect(confirmedInput).toHaveAttribute('readonly');

		const textboxes = canvas.getAllByRole('textbox');
		const newDraftInput = textboxes[textboxes.length - 1];
		await expect(newDraftInput).not.toHaveAttribute('readonly');
		await expect(newDraftInput).toHaveValue('');
	}
};

export const AddIsDisabledForInvalidInput: Story = {
	args: { urls: [] },
	play: async ({ canvasElement }) => {
		const canvas = within(canvasElement);
		const draftInput = canvas.getByRole('textbox');
		const addButton = canvas.getByRole('button', { name: 'Add' });

		await expect(addButton).toBeDisabled();

		await userEvent.type(draftInput, 'not a url');
		await expect(addButton).toBeDisabled();

		await userEvent.clear(draftInput);
		await userEvent.type(draftInput, '   ');
		await expect(addButton).toBeDisabled();

		await userEvent.clear(draftInput);
		await userEvent.type(draftInput, 'https://bsky.app/profile/example.bsky.social');
		await expect(addButton).toBeEnabled();
	}
};

export const RemovingExistingUrlFlagsItForRemoval: Story = {
	args: {
		urls: ['https://bsky.app/profile/example.bsky.social', 'https://twitter.com/example/']
	},
	play: async ({ canvasElement }) => {
		const canvas = within(canvasElement);
		const value = 'https://twitter.com/example/';
		const row = canvas.getByDisplayValue(value).closest('div');
		if (!row) throw new Error('row element not found');
		const rowCanvas = within(row);

		await userEvent.click(rowCanvas.getByRole('button', { name: 'Remove' }));

		// flagged, not deleted: the row survives with a strikethrough and an Undo button
		await expect(canvas.getByDisplayValue(value)).toHaveClass('line-through');
		await expect(rowCanvas.getByRole('button', { name: 'Undo' })).toBeInTheDocument();
		expect(rowCanvas.queryByRole('button', { name: 'Remove' })).not.toBeInTheDocument();

		await userEvent.click(rowCanvas.getByRole('button', { name: 'Undo' }));

		await expect(canvas.getByDisplayValue(value)).not.toHaveClass('line-through');
		await expect(rowCanvas.getByRole('button', { name: 'Remove' })).toBeInTheDocument();
	}
};

export const RemovingNewlyAddedUrlDeletesItOutright: Story = {
	args: { urls: [] },
	play: async ({ canvasElement }) => {
		const canvas = within(canvasElement);
		const url = 'https://bsky.app/profile/example.bsky.social';

		await userEvent.type(canvas.getByRole('textbox'), url);
		await userEvent.click(canvas.getByRole('button', { name: 'Add' }));

		const row = canvas.getByDisplayValue(url).closest('div');
		if (!row) throw new Error('row element not found');

		await userEvent.click(within(row).getByRole('button', { name: 'Remove' }));

		// a newly added row is deleted outright, with no flag/undo step
		expect(canvas.queryByDisplayValue(url)).not.toBeInTheDocument();
	}
};
