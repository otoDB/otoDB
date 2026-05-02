"""Public entry points for revision tracking intended for shell / programmatic use"""

from .api.common import add_revision_message, revision

__all__ = ['add_revision_message', 'revision']
