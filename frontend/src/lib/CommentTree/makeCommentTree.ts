import type { components } from '$lib/schema';

type Comment = components['schemas']['CommentSchema'];
type CommentTreeNodeWIP = Omit<Comment, 'submit_date'> & { time: Date };
type CommentTreeNode = CommentTreeNodeWIP & { children: CommentTreeNode[] };

export const makeCommentTree = (comments: Comment[]): CommentTreeNode[] => {
	if (comments.length === 0) return [];

	return Object.entries(
		Object.groupBy(
			comments.map(({ submit_date, ...rest }) => ({ time: new Date(submit_date), ...rest })),
			(e) => e.level
		)
	)
		.map(([level, comments]) => [parseInt(level, 10), comments] as const)
		.toSorted(([a], [b]) => b - a)
		.map(([_, v]) => v as CommentTreeNodeWIP[])
		.reduce((acc, cur, i) => {
			if (i === 0) return [cur.map((c) => ({ ...c, children: [] }))];
			else
				return [
					...acc,
					cur.map((c) => ({
						...c,
						children: acc.at(i - 1)!.filter((e) => e.parent_id === c.id)
					}))
				];
		}, [] as CommentTreeNode[][])
		.at(-1)!;
};
