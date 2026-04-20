import { describe, expect, it } from 'bun:test';
import { makeCommentTree } from './makeCommentTree';

type Comment = Parameters<typeof makeCommentTree>[0][number];
const makeComment = (
	overrides: Partial<Comment> & Pick<Comment, 'id' | 'level' | 'parent_id'>
): Comment => ({
	user: {
		id: 1,
		username: 'user',
		level: 20,
		date_created: '2024-01-01T00:00:00Z'
	},
	comment: 'test',
	submit_date: '2024-01-01T00:00:00Z',
	index: overrides.id,
	edited_at: null,
	edited_by: null,
	...overrides
});

describe('makeCommentTree', () => {
	it('return empty array if no comments are provided', () => {
		expect(makeCommentTree([])).toEqual([]);
	});

	it('only root comment have no children', () => {
		const actual = makeCommentTree([makeComment({ id: 1, level: 0, parent_id: 0 })]);

		expect(actual[0].children).toEqual([]);
	});

	it('only root comments', () => {
		const actual = makeCommentTree([
			makeComment({ id: 1, level: 0, parent_id: 0 }),
			makeComment({ id: 2, level: 0, parent_id: 0 })
		]);
		expect(actual).toHaveLength(2);

		expect(actual[0].id).toBe(1);
		expect(actual[1].id).toBe(2);
	});

	it('child comments are correctly attached to their parent', () => {
		const actual = makeCommentTree([
			makeComment({ id: 1, level: 0, parent_id: 0 }),
			makeComment({ id: 2, level: 1, parent_id: 1 })
		]);

		expect(actual).toHaveLength(1);
		expect(actual[0].id).toBe(1);
		expect(actual[0].children).toHaveLength(1);
		expect(actual[0].children[0].id).toBe(2);
	});

	it('multiple child comments are correctly attached to their parent', () => {
		const actual = makeCommentTree([
			makeComment({ id: 1, level: 0, parent_id: 0 }),
			makeComment({ id: 2, level: 1, parent_id: 1 }),
			makeComment({ id: 3, level: 1, parent_id: 1 })
		]);
		expect(actual[0].children).toHaveLength(2);
		expect(actual[0].children[0].id).toBe(2);
		expect(actual[0].children[1].id).toBe(3);
	});

	it('child comments are correctly distributed to their respective parents', () => {
		const actual = makeCommentTree([
			makeComment({ id: 1, level: 0, parent_id: 0 }),
			makeComment({ id: 2, level: 0, parent_id: 0 }),
			makeComment({ id: 3, level: 1, parent_id: 1 }),
			makeComment({ id: 4, level: 1, parent_id: 2 })
		]);

		expect(actual[0].id).toBe(1);
		expect(actual[0].children[0].id).toBe(3);

		expect(actual[1].id).toBe(2);
		expect(actual[1].children[0].id).toBe(4);
	});

	it('3rd level nesting is built correctly', () => {
		const result = makeCommentTree([
			makeComment({ id: 1, level: 0, parent_id: 0 }),
			makeComment({ id: 2, level: 1, parent_id: 1 }),
			makeComment({ id: 3, level: 2, parent_id: 2 })
		]);
		expect(result[0].id).toBe(1);
		expect(result[0].children[0].id).toBe(2);
		expect(result[0].children[0].children[0].id).toBe(3);
	});

	it('submit_date is converted to a Date object', () => {
		const comments = [makeComment({ id: 1, level: 0, parent_id: 0 })];
		const result = makeCommentTree(comments);
		expect(result[0].time).toBeInstanceOf(Date);
	});
});
