## What are bulk requests

Bulk requests are used to perform multiple different actions at once.

They also allow users to preemptively add tags to submissions that are pending approval.

## Available commands in bulk requests

Variables between [square_brackets] represent tag slugs, or numeric identifiers for videos or sources. Bulk requests are written without those square brackets.

### Tag-editing

- worktag:alias [tag A] [tags]
    - Aliases one or many tags to tag_A
- worktag:unalias [tag]
    - Removes the alias of a tag
- worktag:deprecate [tag]
- worktag:undeprecate [tag]
- worktag:parent [tag_A] [tag_B]
    - Sets tag_B as the parent of tag_A
- worktag:unparent [tag_A] [tag_B]
    - Removes tag_B from tag_A's parent tags

### Tagging works

- source:attach-tag [source_id] [tags]
    - Adds one or many tags to a submission pending approval
- work:attach-tag [work_id] [tags]
    - Adds one or many tags to a work

## Example of a bulk request

```
worktag:alias tag_jp tag_en_translation tag_cn_translation
worktag:parent tag_jp tag_parent
source:attach-tag 5 tag_jp unrelated_tag
```

This bulk request will alias `tag_cn_translation` and `tag_en_translation` to `tag_jp`. It will then parent `tag_jp` to `tag_parent` and finally, attach `tag_jp` and `unrelated_tag` to the pending submission of id=`5`.

## Where to find a work id?

For works, the ID can be consulted in the address bar of your browser:

Ex. otodb.net/work/[work_ID]

## Where to find a source id?

To find the ID of a pending submission, go to your [Submissions Page](/profile/test/submissions) and click on the "Add tags" link for the submission you want to tag.

## Current limitations

As of now, tags need to exist for any bulk action to be performed on them.
