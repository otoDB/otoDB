from itertools import repeat, chain

from otodb.models import TagWork, SourceWork, MediaWork

def validate(model, field):
    return lambda value: model.objects.get(**{ field: value })

TAGWORK_SLUG_VALIDATOR = validate(TagWork, 'slug')
MEDIAWORK_ID_VALIDATOR = validate(MediaWork, 'id')
SOURCEWORK_ID_VALIDATOR = validate(SourceWork, 'id')

# Numbers to be replaced by an enum
COMMANDS = {
    'worktag:alias': (0, chain(TAGWORK_SLUG_VALIDATOR, repeat(TAGWORK_SLUG_VALIDATOR))),
    'worktag:deprecate': (1, (TAGWORK_SLUG_VALIDATOR,)),
    'worktag:parent': (2, chain(TAGWORK_SLUG_VALIDATOR, repeat(TAGWORK_SLUG_VALIDATOR))),

    'source:attach-tag': (3, chain(SOURCEWORK_ID_VALIDATOR, repeat(TAGWORK_SLUG_VALIDATOR))),
    'work:attach-tag': (4, chain(MEDIAWORK_ID_VALIDATOR, repeat(TAGWORK_SLUG_VALIDATOR))),
}

def parse_command(s: str):
    c = s.split()
    cmd, validators = COMMANDS[c[0]]
    args = s[1:]
    for a, v in zip(args, validators):
        assert(v(a))
