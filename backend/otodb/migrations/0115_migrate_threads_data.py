from django.db import migrations

# LanguageTypes labels, inlined so the migration is independent of the enum.
LANG_LABEL = {0: 'N/A', 1: 'en', 2: 'ja', 3: 'zh-cn', 4: 'ko'}


def forward(apps, schema_editor):
	"""Fold each thread's multilingual opening body + its XtdComments into a flat
	list of ThreadPosts (OP = num 1), and repoint notifications at those posts."""
	Thread = apps.get_model('otodb', 'Thread')
	ThreadPost = apps.get_model('otodb', 'ThreadPost')
	PostContent = apps.get_model('otodb', 'PostContent')
	Notification = apps.get_model('otodb', 'Notification')
	CommentMeta = apps.get_model('otodb', 'CommentMeta')
	ContentType = apps.get_model('contenttypes', 'ContentType')
	XtdComment = apps.get_model('django_comments_xtd', 'xtdcomment')

	thread_ct = ContentType.objects.filter(app_label='otodb', model='thread').first()

	for thread in Thread.objects.all().iterator():
		pcs = list(
			PostContent.objects.filter(post_id=thread.id).order_by('modified', 'id')
		)
		if pcs:
			if len(pcs) == 1:
				body = pcs[0].page
			else:
				# Combine all languages into the single opening post.
				body = '\n\n---\n\n'.join(
					f'**[{LANG_LABEL.get(pc.lang, pc.lang)}]**\n\n{pc.page}'
					for pc in pcs
				)
			op_created = pcs[0].modified
			thread.lang = pcs[0].lang
			thread.created_at = pcs[0].modified
			thread.save(update_fields=['lang', 'created_at'])
		else:
			body = ''
			op_created = thread.created_at

		op = ThreadPost.objects.create(
			thread_id=thread.id,
			num=1,
			user_id=thread.added_by_id,
			body=body,
			created_at=op_created,
			edited_at=thread.edited_at,
			edited_by_id=thread.edited_by_id,
		)
		# Thread-level notifications (mentions / thread-linked) -> the opening post.
		Notification.objects.filter(post_id=thread.id).update(
			post=None, threadpost_id=op.id
		)

		if thread_ct is None:
			continue
		comments = list(
			XtdComment.objects.filter(
				content_type_id=thread_ct.id, object_pk=str(thread.id)
			).order_by('submit_date', 'id')
		)
		if not comments:
			continue

		# Replies are numbered from 2 (the OP is 1).
		id_to_num = {c.id: i for i, c in enumerate(comments, start=2)}
		metas = {
			m.comment_id: m
			for m in CommentMeta.objects.filter(comment_id__in=[c.id for c in comments])
		}
		new_posts = []
		for c in comments:
			cbody = c.comment
			# Re-express a genuine nested reply as a post reference. django-comments-xtd
			# stores a top-level comment's parent_id as its own id (self-parent), so only
			# prepend a reference when the parent is a different comment.
			if c.parent_id and c.parent_id != c.id and c.parent_id in id_to_num:
				cbody = f't{thread.id}.{id_to_num[c.parent_id]}: \n\n{cbody}'
			meta = metas.get(c.id)
			new_posts.append(
				ThreadPost(
					thread_id=thread.id,
					num=id_to_num[c.id],
					user_id=(c.user_id or thread.added_by_id),
					body=cbody,
					created_at=c.submit_date,
					is_removed=c.is_removed,
					edited_at=meta.edited_at if meta else None,
					edited_by_id=meta.edited_by_id if meta else None,
				)
			)
		created = ThreadPost.objects.bulk_create(new_posts)
		for c, tp in zip(comments, created):
			Notification.objects.filter(comment_id=c.id).update(
				comment=None, threadpost_id=tp.id
			)

	if thread_ct is not None:
		XtdComment.objects.filter(content_type_id=thread_ct.id).delete()


def reverse(apps, schema_editor):
	ThreadPost = apps.get_model('otodb', 'ThreadPost')
	Notification = apps.get_model('otodb', 'Notification')
	Notification.objects.filter(threadpost__isnull=False).update(threadpost=None)
	ThreadPost.objects.all().delete()


class Migration(migrations.Migration):
	dependencies = [
		('otodb', '0114_thread_refactor'),
	]

	operations = [
		migrations.RunPython(forward, reverse),
	]
