"""OpenAPI schema generation extras.

Ninja emits ``x-enum-varnames`` (member labels) on every enum component via
OtodbIntegerEnum's pydantic hook; the frontend's ``openapi-typescript --enum``
uses them for the generated TS enum member names (WorkOrigin.Author, ...).
This plugin makes Litestar emit the same vendor extension natively, so the
merged spec keeps stable enum member names no matter which side owns a
component. Wiring: Litestar consults OpenAPI schema plugins before its
built-in enum handling; vendor extensions are expressed as an aliased field on
a Schema subclass, which BaseSchemaObject.to_schema() serializes by alias.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as dc_field
from typing import TYPE_CHECKING, cast

from litestar.openapi.spec import Schema
from litestar.plugins import OpenAPISchemaPlugin

from otodb_next.enums import OtodbIntegerEnum

if TYPE_CHECKING:
	from litestar._openapi.schema_generation import SchemaCreator
	from litestar.typing import FieldDefinition


@dataclass
class _EnumSchema(Schema):
	enum_varnames: list[str] | None = dc_field(
		default=None, metadata={'alias': 'x-enum-varnames'}
	)


class EnumVarnamesPlugin(OpenAPISchemaPlugin):
	"""Adds x-enum-varnames to every OtodbIntegerEnum schema component."""

	def is_plugin_supported_field(self, field_definition: FieldDefinition) -> bool:
		return isinstance(field_definition.annotation, type) and issubclass(
			field_definition.annotation, OtodbIntegerEnum
		)

	def to_openapi_schema(
		self, field_definition: FieldDefinition, schema_creator: SchemaCreator
	) -> Schema:
		# Let the builtin enum handling do its work (component registration,
		# $ref, type/enum/title) ...
		result = schema_creator.for_enum_field(field_definition)
		# ... then upgrade the REGISTERED component instance so it serializes
		# the vendor extension. Litestar's Schema object has no
		# vendor-extension support and its registry hardcodes plain Schema()
		# instances, so promoting the instance to the aliased subclass is the
		# narrowest way in; to_schema() serializes by the instance's class.
		registered = schema_creator.schema_registry.get_schema_for_field_definition(
			field_definition
		)
		registered.__class__ = _EnumSchema
		promoted = cast('_EnumSchema', registered)
		promoted.enum_varnames = [m.label for m in field_definition.annotation]
		# result may be a Reference to the component we just upgraded; litestar
		# handles both, its protocol annotation is just narrower than reality
		return cast('Schema', result)
