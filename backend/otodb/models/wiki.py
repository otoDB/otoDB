from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q

from .enums import LanguageTypes
from .revision import RevisionTrackedModel

WIKI_RESERVED_SLUGS = frozenset({'tag', 'work'})


def _validate_wiki_slug(value: str) -> None:
	if value in WIKI_RESERVED_SLUGS:
		raise ValidationError(f'"{value}" is a reserved wiki slug')


class WikiPage(RevisionTrackedModel):
	tag = models.ForeignKey('TagWork', on_delete=models.CASCADE, null=True, blank=True)
	work = models.ForeignKey(
		'MediaWork', on_delete=models.CASCADE, null=True, blank=True
	)
	slug = models.CharField(
		max_length=255,
		null=True,
		blank=True,
		validators=[
			RegexValidator(
				regex=r'^[a-z0-9_-]+$',
			),
			_validate_wiki_slug,
		],
	)
	title = models.CharField(max_length=255, null=True, blank=True)
	page = models.TextField(null=False)
	lang = models.IntegerField(
		choices=LanguageTypes.choices,
		default=LanguageTypes.NOT_APPLICABLE,
		null=False,
		blank=False,
	)

	class RevisionMeta:
		tracked_fields = ['lang', 'tag', 'work', 'slug', 'title', 'page']
		entity_attrs = ['self', 'tag', 'work']

	class Meta:
		constraints = [
			models.CheckConstraint(
				name='wikipage_exactly_one_attachment',
				condition=(
					Q(tag__isnull=False, work__isnull=True, slug__isnull=True)
					| Q(tag__isnull=True, work__isnull=False, slug__isnull=True)
					| Q(tag__isnull=True, work__isnull=True, slug__isnull=False)
				),
			),
			models.CheckConstraint(
				name='wikipage_title_iff_slug',
				condition=(
					Q(slug__isnull=False, title__isnull=False)
					| Q(slug__isnull=True, title__isnull=True)
				),
			),
			models.UniqueConstraint(
				fields=['tag', 'lang'],
				condition=Q(tag__isnull=False),
				name='unique_wikipage_tag_lang',
			),
			models.UniqueConstraint(
				fields=['work', 'lang'],
				condition=Q(work__isnull=False),
				name='unique_wikipage_work_lang',
			),
			models.UniqueConstraint(
				fields=['slug', 'lang'],
				condition=Q(slug__isnull=False),
				name='unique_wikipage_slug_lang',
			),
		]
