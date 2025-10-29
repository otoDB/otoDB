import pytest

from otodb.models import MediaWork, TagWork, TagWorkInstance, TagWorkParenthood
from otodb.models.enums import WorkTagCategory


# Tests
@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestTagLanguagePreference:
	"""Test that language preference slugs (including aliases) work correctly without data loss"""

	def test_setting_tags_with_alias_slug_preserves_creator_roles_and_sample(
		self, editor, work_client
	):
		"""
		Test that when a work has tags set using an alias slug (e.g., from language preference),
		the creator_roles and used_as_source data is preserved on the base tag.
		"""
		# Create a work
		work = MediaWork.objects.create(title='Test Work')

		# Create base tag and alias
		base_tag = TagWork.objects.create(
			name='attack_on_titan', category=WorkTagCategory.CREATOR
		)
		alias_tag = TagWork.objects.create(name='shingeki_no_kyojin')
		alias_tag.aliased_to = base_tag
		alias_tag.save()

		# Add base tag to work with creator roles and sample data
		work.tags.add(base_tag)
		twi = TagWorkInstance.objects.get(work=work, work_tag=base_tag)
		twi.set_creator_roles([1, 2])  # Audio, Visuals
		twi.used_as_source = True
		twi.save()

		# Now set tags using the alias slug (simulating language preference usage)
		response = work_client.put(
			f'/set_tags?work_id={work.id}',
			json=['shingeki_no_kyojin'],
			user=editor,
		)
		assert response.status_code == 200

		# Verify the base tag is still on the work (not the alias)
		work.refresh_from_db()
		assert base_tag in work.tags.all()
		assert alias_tag not in work.tags.all()

		# Verify creator_roles and used_as_source are preserved
		twi = TagWorkInstance.objects.get(work=work, work_tag=base_tag)
		assert twi.creator_roles == 3  # 1|2 = 3
		assert twi.used_as_source is True

	def test_updating_tag_parents_with_alias_slug(self, editor, tag_client):
		"""
		Test that when updating a tag's parents using an alias slug (e.g., from language preference),
		the parent relationship is correctly established with the base tag.
		"""
		# Create tags
		child_tag = TagWork.objects.create(name='specific_anime')
		parent_base = TagWork.objects.create(name='anime')
		parent_alias = TagWork.objects.create(name='アニメ')
		parent_alias.aliased_to = parent_base
		parent_alias.save()

		# Update child tag with parent using alias slug
		response = tag_client.put(
			f'/tag?tag_slug={child_tag.slug}',
			json={
				'payload': {
					'parent_slugs': ['アニメ'],  # Using alias slug
					'category': WorkTagCategory.GENERAL,
					'deprecated': False,
					'media_type': [],
					'primary': None,
				},
				'song_payload': None,
			},
			user=editor,
		)
		assert response.status_code == 200

		# Verify parent relationship is with base tag, not alias
		parenthood = TagWorkParenthood.objects.filter(tag=child_tag).first()
		assert parenthood is not None
		assert parenthood.parent == parent_base
		assert parenthood.parent != parent_alias

	def test_alias_slug_resolves_to_base_before_adding_to_work(
		self, editor, work_client
	):
		"""
		Test that alias slugs are resolved to base tags before being added to works,
		preventing the signal from needing to do complex data transfers.
		"""
		work = MediaWork.objects.create(title='Test Work')
		base_tag = TagWork.objects.create(name='base_tag')
		alias_tag = TagWork.objects.create(name='alias_tag')
		alias_tag.aliased_to = base_tag
		alias_tag.save()

		# Set tags using alias slug
		response = work_client.put(
			f'/set_tags?work_id={work.id}',
			json=['alias_tag'],
			user=editor,
		)
		assert response.status_code == 200

		# Verify only base tag is in work.tags (alias was resolved before adding)
		work.refresh_from_db()
		assert work.tags.count() == 1
		assert base_tag in work.tags.all()
		assert alias_tag not in work.tags.all()

		# Verify TagWorkInstance was created with base tag directly
		assert TagWorkInstance.objects.filter(
			work=work, work_tag=base_tag
		).exists()
		assert not TagWorkInstance.objects.filter(
			work=work, work_tag=alias_tag
		).exists()
