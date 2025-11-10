# Generated migration for tag search materialized view optimization

from django.db import migrations


def create_materialized_view(apps, schema_editor):
	if schema_editor.connection.vendor != 'postgresql':
		return  # Skip for SQLite

	schema_editor.execute("""
        --begin-sql
        CREATE MATERIALIZED VIEW otodb_tagwork_search_mv AS
        WITH tag_lang_prefs AS (
            -- Pre-aggregate language preferences for each tag
            SELECT
                tw.id as tag_id,
                COALESCE(
                    jsonb_agg(
                        jsonb_build_object(
                            'lang', lp.lang,
                            'tag', lp_tag.name,
                            'slug', lp_tag.slug
                        ) ORDER BY lp.lang
                    ) FILTER (WHERE lp.lang IS NOT NULL),
                    '[]'::jsonb
                ) as lang_prefs
            FROM otodb_tagwork tw
            LEFT JOIN otodb_tagworklangpreference lp ON lp.tag_id = tw.id
            LEFT JOIN otodb_tagwork lp_tag ON lp.tag_id = lp_tag.id
            GROUP BY tw.id
        ),
        tag_with_alias_prefs AS (
            -- Merge lang prefs from tag + all its aliases
            SELECT
                tw.id as tag_id,
                COALESCE(
                    (
                        SELECT jsonb_agg(DISTINCT elem)
                        FROM (
                            SELECT jsonb_array_elements(tlp.lang_prefs) as elem
                            FROM tag_lang_prefs tlp
                            WHERE tlp.tag_id = tw.id
                            UNION
                            SELECT jsonb_array_elements(tlp_alias.lang_prefs) as elem
                            FROM otodb_tagwork alias_tag
                            JOIN tag_lang_prefs tlp_alias ON tlp_alias.tag_id = alias_tag.id
                            WHERE alias_tag.aliased_to_id = tw.id
                        ) combined
                    ),
                    '[]'::jsonb
                ) as merged_lang_prefs
            FROM otodb_tagwork tw
            GROUP BY tw.id
        )
        SELECT
            tw.id,
            tw.name,
            tw.slug,
            tw.category,
            tw.deprecated,
            tw.media_type,
            tw.aliased_to_id,

            -- Pre-compute instance count (use parent count if aliased)
            CASE
                WHEN tw.aliased_to_id IS NOT NULL THEN
                    (SELECT COUNT(*) FROM otodb_tagworkinstance WHERE work_tag_id = tw.aliased_to_id)
                ELSE
                    (SELECT COUNT(*) FROM otodb_tagworkinstance WHERE work_tag_id = tw.id)
            END as n_instance,

            -- Lang prefs (use parent's if aliased, else merged prefs from self + aliases)
            CASE
                WHEN tw.aliased_to_id IS NOT NULL THEN
                    (SELECT merged_lang_prefs FROM tag_with_alias_prefs WHERE tag_id = tw.aliased_to_id)
                ELSE
                    (SELECT merged_lang_prefs FROM tag_with_alias_prefs WHERE tag_id = tw.id)
            END as lang_prefs_json,

            -- Aliased_to parent data (complete TagWorkSchema structure)
            CASE
                WHEN tw.aliased_to_id IS NOT NULL THEN
                    jsonb_build_object(
                        'id', parent.id,
                        'name', parent.name,
                        'slug', parent.slug,
                        'category', parent.category,
                        'n_instance', (SELECT COUNT(*) FROM otodb_tagworkinstance WHERE work_tag_id = parent.id),
                        'lang_prefs', (SELECT merged_lang_prefs FROM tag_with_alias_prefs WHERE tag_id = parent.id),
                        'aliased_to', NULL
                    )
                ELSE NULL
            END as aliased_to_json,

            -- Alias names array for exact match detection
            COALESCE(
                (SELECT array_agg(name) FROM otodb_tagwork WHERE aliased_to_id = tw.id),
                ARRAY[]::text[]
            ) as alias_names

        FROM otodb_tagwork tw
        LEFT JOIN otodb_tagwork parent ON tw.aliased_to_id = parent.id;
        --end-sql
    """)

	# Create indexes for fast search
	schema_editor.execute("""
        CREATE UNIQUE INDEX otodb_tagwork_search_mv_id_idx
            ON otodb_tagwork_search_mv (id);
    """)

	schema_editor.execute("""
        CREATE INDEX otodb_tagwork_search_mv_name_idx
            ON otodb_tagwork_search_mv (name);
    """)

	schema_editor.execute("""
        CREATE INDEX otodb_tagwork_search_mv_name_pattern_idx
            ON otodb_tagwork_search_mv (name text_pattern_ops);
    """)

	schema_editor.execute("""
        CREATE INDEX otodb_tagwork_search_mv_slug_idx
            ON otodb_tagwork_search_mv (slug);
    """)

	schema_editor.execute("""
        CREATE INDEX otodb_tagwork_search_mv_category_idx
            ON otodb_tagwork_search_mv (deprecated, category);
    """)

	schema_editor.execute("""
        CREATE INDEX otodb_tagwork_search_mv_alias_names_idx
            ON otodb_tagwork_search_mv USING GIN (alias_names);
    """)

	schema_editor.execute("""
        CREATE INDEX otodb_tagwork_search_mv_media_type_idx
            ON otodb_tagwork_search_mv (media_type)
            WHERE category = 6;
    """)


def drop_materialized_view(apps, schema_editor):
	if schema_editor.connection.vendor != 'postgresql':
		return  # Skip for SQLite

	schema_editor.execute("""
        DROP MATERIALIZED VIEW IF EXISTS otodb_tagwork_search_mv CASCADE;
    """)


class Migration(migrations.Migration):
	dependencies = [
		('otodb', '0071_allow_null_and_blank_source_title'),
	]

	operations = [
		migrations.RunPython(
			create_materialized_view, reverse_code=drop_materialized_view
		),
	]
