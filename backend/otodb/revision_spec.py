"""Django-free source of truth for the revision-capture triggers.

The trigger codegen (``revision_codegen.py``) reads ONLY this file, so trigger
generation never imports Django and survives the migration off it. While Django still
exists, ``tests/test_revision_spec_parity.py`` asserts this spec matches the models'
``RevisionMeta`` + field types, so it can't silently drift; that test is deleted with
Django, leaving this spec as the sole authority.

Each table entry:
  table     -- Postgres table name
  app/model -- content-type (app_label, model) used by the trigger's otodb_ct() lookups
  pk        -- primary-key column
  tracked   -- (revision field NAME, db column, kind) per tracked field.
               kind: 'str' | 'int' | 'float' | 'bool' | 'date' | 'fk'
               (drives serialization to match Django str()); FK value = str(pk).
  entities  -- (kind, app, model, id_column) routing targets per change.
               kind 'self' -> this row (id_column = pk); 'fk' -> the FK's target.

To add a tracked field/model: edit here and regenerate
(``python -m otodb.revision_codegen > otodb/sql/revision_triggers.sql``).
"""

TABLES = [
	{
		'table': 'otodb_mediasong',
		'app': 'otodb',
		'model': 'mediasong',
		'pk': 'id',
		'tracked': [
			('title', 'title', 'str'),
			('bpm', 'bpm', 'float'),
			('variable_bpm', 'variable_bpm', 'bool'),
			('work_tag', 'work_tag_id', 'fk'),
			('author', 'author', 'str'),
		],
		'entities': [
			('self', 'otodb', 'mediasong', 'id'),
			('fk', 'otodb', 'tagwork', 'work_tag_id'),
		],
	},
	{
		'table': 'otodb_mediasongconnection',
		'app': 'otodb',
		'model': 'mediasongconnection',
		'pk': 'id',
		'tracked': [
			('song', 'song_id', 'fk'),
			('site', 'site', 'int'),
			('content_id', 'content_id', 'str'),
		],
		'entities': [('fk', 'otodb', 'mediasong', 'song_id')],
	},
	{
		'table': 'otodb_mediawork',
		'app': 'otodb',
		'model': 'mediawork',
		'pk': 'id',
		'tracked': [
			('title', 'title', 'str'),
			('description', 'description', 'str'),
			('rating', 'rating', 'int'),
			('moved_to', 'moved_to_id', 'fk'),
		],
		'entities': [
			('self', 'otodb', 'mediawork', 'id'),
			('fk', 'otodb', 'mediawork', 'moved_to_id'),
		],
	},
	{
		'table': 'otodb_songrelation',
		'app': 'otodb',
		'model': 'songrelation',
		'pk': 'id',
		'tracked': [
			('A', 'A_id', 'fk'),
			('B', 'B_id', 'fk'),
			('relation', 'relation', 'int'),
		],
		'entities': [
			('fk', 'otodb', 'mediasong', 'A_id'),
			('fk', 'otodb', 'mediasong', 'B_id'),
		],
	},
	{
		'table': 'otodb_tagsong',
		'app': 'otodb',
		'model': 'tagsong',
		'pk': 'id',
		'tracked': [
			('name', 'name', 'str'),
			('slug', 'slug', 'str'),
			('aliased_to', 'aliased_to_id', 'fk'),
			('category', 'category', 'int'),
			('parent', 'parent_id', 'fk'),
		],
		'entities': [('self', 'otodb', 'tagsong', 'id')],
	},
	{
		'table': 'otodb_tagsonginstance',
		'app': 'otodb',
		'model': 'tagsonginstance',
		'pk': 'id',
		'tracked': [('song', 'song_id', 'fk'), ('song_tag', 'song_tag_id', 'fk')],
		'entities': [('fk', 'otodb', 'mediasong', 'song_id')],
	},
	{
		'table': 'otodb_tagsonglangpreference',
		'app': 'otodb',
		'model': 'tagsonglangpreference',
		'pk': 'id',
		'tracked': [('lang', 'lang', 'int'), ('tag', 'tag_id', 'fk')],
		'entities': [('fk', 'otodb', 'tagsong', 'tag_id')],
	},
	{
		'table': 'otodb_tagwork',
		'app': 'otodb',
		'model': 'tagwork',
		'pk': 'id',
		'tracked': [
			('name', 'name', 'str'),
			('slug', 'slug', 'str'),
			('aliased_to', 'aliased_to_id', 'fk'),
			('deprecated', 'deprecated', 'bool'),
			('category', 'category', 'int'),
			('media_type', 'media_type', 'int'),
		],
		'entities': [
			('self', 'otodb', 'tagwork', 'id'),
			('fk', 'otodb', 'tagwork', 'aliased_to_id'),
		],
	},
	{
		'table': 'otodb_tagworkconnection',
		'app': 'otodb',
		'model': 'tagworkconnection',
		'pk': 'id',
		'tracked': [
			('tag', 'tag_id', 'fk'),
			('site', 'site', 'int'),
			('content_id', 'content_id', 'str'),
		],
		'entities': [('fk', 'otodb', 'tagwork', 'tag_id')],
	},
	{
		'table': 'otodb_tagworkcreatorconnection',
		'app': 'otodb',
		'model': 'tagworkcreatorconnection',
		'pk': 'id',
		'tracked': [
			('tag', 'tag_id', 'fk'),
			('site', 'site', 'int'),
			('content_id', 'content_id', 'str'),
			('dead', 'dead', 'bool'),
		],
		'entities': [('fk', 'otodb', 'tagwork', 'tag_id')],
	},
	{
		'table': 'otodb_tagworkinstance',
		'app': 'otodb',
		'model': 'tagworkinstance',
		'pk': 'id',
		'tracked': [
			('work', 'work_id', 'fk'),
			('work_tag', 'work_tag_id', 'fk'),
			('used_as_source', 'used_as_source', 'bool'),
			('creator_roles', 'creator_roles', 'int'),
		],
		'entities': [('fk', 'otodb', 'mediawork', 'work_id')],
	},
	{
		'table': 'otodb_tagworklangpreference',
		'app': 'otodb',
		'model': 'tagworklangpreference',
		'pk': 'id',
		'tracked': [('lang', 'lang', 'int'), ('tag', 'tag_id', 'fk')],
		'entities': [('fk', 'otodb', 'tagwork', 'tag_id')],
	},
	{
		'table': 'otodb_tagworkmediaconnection',
		'app': 'otodb',
		'model': 'tagworkmediaconnection',
		'pk': 'id',
		'tracked': [
			('tag', 'tag_id', 'fk'),
			('site', 'site', 'int'),
			('content_id', 'content_id', 'str'),
		],
		'entities': [('fk', 'otodb', 'tagwork', 'tag_id')],
	},
	{
		'table': 'otodb_tagworkparenthood',
		'app': 'otodb',
		'model': 'tagworkparenthood',
		'pk': 'id',
		'tracked': [
			('tag', 'tag_id', 'fk'),
			('parent', 'parent_id', 'fk'),
			('primary', 'primary', 'bool'),
		],
		'entities': [
			('fk', 'otodb', 'tagwork', 'tag_id'),
			('fk', 'otodb', 'tagwork', 'parent_id'),
		],
	},
	{
		'table': 'otodb_wikipage',
		'app': 'otodb',
		'model': 'wikipage',
		'pk': 'id',
		'tracked': [
			('lang', 'lang', 'int'),
			('tag', 'tag_id', 'fk'),
			('work', 'work_id', 'fk'),
			('slug', 'slug', 'str'),
			('title', 'title', 'str'),
			('page', 'page', 'str'),
		],
		'entities': [
			('self', 'otodb', 'wikipage', 'id'),
			('fk', 'otodb', 'tagwork', 'tag_id'),
			('fk', 'otodb', 'mediawork', 'work_id'),
		],
	},
	{
		'table': 'otodb_workrelation',
		'app': 'otodb',
		'model': 'workrelation',
		'pk': 'id',
		'tracked': [
			('A', 'A_id', 'fk'),
			('B', 'B_id', 'fk'),
			('relation', 'relation', 'int'),
		],
		'entities': [
			('fk', 'otodb', 'mediawork', 'A_id'),
			('fk', 'otodb', 'mediawork', 'B_id'),
		],
	},
	{
		'table': 'otodb_worksource',
		'app': 'otodb',
		'model': 'worksource',
		'pk': 'id',
		'tracked': [
			('media', 'media_id', 'fk'),
			('platform', 'platform', 'int'),
			('source_id', 'source_id', 'str'),
			('url', 'url', 'str'),
			('published_date', 'published_date', 'date'),
			('work_origin', 'work_origin', 'int'),
			('work_status', 'work_status', 'int'),
			('work_width', 'work_width', 'int'),
			('work_height', 'work_height', 'int'),
			('work_duration', 'work_duration', 'int'),
			('title', 'title', 'str'),
			('description', 'description', 'str'),
			('thumbnail_url', 'thumbnail_url', 'str'),
			('thumbnail_mime', 'thumbnail_mime', 'int'),
			('thumbnail_hash', 'thumbnail_hash', 'str'),
			('uploader_id', 'uploader_id', 'str'),
			('added_by', 'added_by_id', 'fk'),
		],
		'entities': [
			('self', 'otodb', 'worksource', 'id'),
			('fk', 'otodb', 'mediawork', 'media_id'),
		],
	},
]
