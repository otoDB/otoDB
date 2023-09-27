from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import Category


def create_category(**kwargs):
    default_kwargs = {
        'label': 'Foo',
        'title_singular': 'Foo',
        'title_plural': 'Foos',
        'shortcut': 'f',
        'color': 'fff',
    }
    return Category(**{**default_kwargs, **kwargs})


class CategoryModelTests(TestCase):
    def test_add(self):
        category = create_category()
        self.assertIsNone(category.clean())

    def test_invalid_shortcut_space(self):
        with self.assertRaises(ValidationError):
            category = create_category(shortcut='asdf ')
            category.clean()

    def test_invalid_shortcut_uppercase(self):
        with self.assertRaises(ValidationError):
            category = create_category(shortcut='ASDF')
            category.clean()

    def test_invalid_color_length(self):
        with self.assertRaises(ValidationError):
            category = create_category(color='ffff')
            category.clean()

    def test_invalid_color_str(self):
        with self.assertRaises(ValidationError):
            category = create_category(color='zzzzzz')
            category.clean()
