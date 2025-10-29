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
		assert TagWorkInstance.objects.filter(work=work, work_tag=base_tag).exists()
		assert not TagWorkInstance.objects.filter(
			work=work, work_tag=alias_tag
		).exists()

	def test_aliasing_into_alias_tag_resolves_to_base(self, editor, tag_client):
		"""
		Test that when aliasing tags into another alias tag, the system resolves
		to the base tag to prevent creating an alias chain.
		"""
		# Create base tag and an alias to it
		base_tag = TagWork.objects.create(name='base_tag')
		existing_alias = TagWork.objects.create(name='existing_alias')
		existing_alias.aliased_to = base_tag
		existing_alias.save()

		# Create a tag that we want to alias
		tag_to_alias = TagWork.objects.create(name='tag_to_alias')

		# Try to alias into the alias tag (should resolve to base_tag)
		response = tag_client.post(
			'/alias?into_tag=existing_alias&delete=false',
			json=['tag_to_alias'],
			user=editor,
		)
		assert response.status_code == 200

		# Verify the tag was aliased to the base tag, not the alias
		tag_to_alias.refresh_from_db()
		assert tag_to_alias.aliased_to == base_tag
		assert tag_to_alias.aliased_to != existing_alias

		# Verify we don't have an alias chain
		assert existing_alias.aliased_to == base_tag
		assert base_tag.aliased_to is None


@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestTagSearch:
	"""Test tag search endpoint sorting behavior"""

	def test_exact_alias_match_sorting(self, tag_client):
		"""
		Test that tags with exact alias matches are prioritized correctly.
		Exact alias matches should come after exact name matches but before partial matches.
		"""
		# Search term: 'mmo'

		# 1. Base tag with alias that exactly matches 'mmo' - high usage (3 works)
		base_tag = TagWork.objects.create(
			name='massively_multiplayer_online', category=WorkTagCategory.GENERAL
		)
		alias_mmo = TagWork.objects.create(name='mmo')
		alias_mmo.aliased_to = base_tag
		alias_mmo.save()

		work1 = MediaWork.objects.create(title='Work 1')
		work2 = MediaWork.objects.create(title='Work 2')
		work3 = MediaWork.objects.create(title='Work 3')
		work1.tags.add(base_tag)
		work2.tags.add(base_tag)
		work3.tags.add(base_tag)

		# 2. Partial match with very high usage (5 works)
		partial_high = TagWork.objects.create(
			name='mmorpg', category=WorkTagCategory.GENERAL
		)
		for i in range(5):
			w = MediaWork.objects.create(title=f'Work Partial {i}')
			w.tags.add(partial_high)

		# 3. Partial match with low usage (1 work)
		partial_low = TagWork.objects.create(
			name='mmo_strategy', category=WorkTagCategory.GENERAL
		)
		work4 = MediaWork.objects.create(title='Work 4')
		work4.tags.add(partial_low)

		# Search for 'mmo'
		response = tag_client.get('/search?query=mmo')
		assert response.status_code == 200
		results = response.json()['items']
		result_names = [tag['name'] for tag in results]

		# Assertions:
		# 1. Exact alias match comes first (massively_multiplayer_online has alias 'mmo')
		assert result_names[0] == 'massively_multiplayer_online'

		# 2. Partial matches follow, sorted by usage (mmorpg with 5, mmo_strategy with 1)
		assert result_names[1] == 'mmorpg'
		assert result_names[2] == 'mmo_strategy'

	def test_exact_match_case_insensitive(self, tag_client):
		"""Test that exact matching is case-insensitive"""
		work1 = MediaWork.objects.create(title='Work 1')
		work2 = MediaWork.objects.create(title='Work 2')

		# Create tags with different cases
		tag1 = TagWork.objects.create(name='anime', category=WorkTagCategory.GENERAL)
		tag2 = TagWork.objects.create(
			name='ANIME_SERIES', category=WorkTagCategory.GENERAL
		)

		work1.tags.add(tag1)
		work2.tags.add(tag2)

		# Search with different case
		response = tag_client.get('/search?query=ANIME')
		assert response.status_code == 200
		results = response.json()['items']

		# 'anime' should be first as an exact match
		assert results[0]['name'] == 'anime'
		# 'anime_series' should be second as a partial match
		assert results[1]['name'] == 'anime_series'
