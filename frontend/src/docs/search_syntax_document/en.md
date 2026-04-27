## ! Syntax and documentation still a work in progress !

---

This page documents how to search for works and songs with tags.

## Basic queries

| Query               | Result                                                                                        |
| ------------------- | --------------------------------------------------------------------------------------------- |
| {{yamas touhou}}    | Works tagged with `yamas` AND `touhou`                                                        |
| {{yamas \| touhou}} | Works tagged with `yamas` OR `touhou`                                                         |
| {{-yamas}}          | Works that are not tagged with `yamas`                                                        |
| {{^yamas}}          | Works that are tagged with `yamas` exactly (do not consider child tags)                       |
| {{-^yamas}}         | Works that are not tagged with `yamas` exactly (still allow child tags)                       |
| {{-(yamas touhou)}} | Works that are not tagged with both `yamas` and `touhou` (but may have either one or neither) |

## Metatags

Metatags are `key:value` pairs that filter on a non-tag field.

### Users

| Query            | Result                                         |
| ---------------- | ---------------------------------------------- |
| {{user:mmaker}}  | Works whose initial contributor is @mmaker     |
| {{-user:mmaker}} | Works whose initial contributor is not @mmaker |

### Range qualifiers

| Query                          | Result                                            |
| ------------------------------ | ------------------------------------------------- |
| {{id:1}}                       | Work whose ID is exactly equal to 1               |
| {{id:>=1000}} or {{id:1000..}} | Works whose ID is greater than or equal to 1000   |
| {{id:>1000}}                   | Works whose ID is greater than 1000               |
| {{id:<=1000}} or {{id:..1000}} | Works whose ID is less than or equal to 1000      |
| {{id:<1000}}                   | Works whose ID is less than 1000                  |
| {{id:114..514}}                | Works whose ID is between 114 and 514 (inclusive) |

### Work qualifiers

| Metatag                                                                                                                                                     | Values                                                                                                                    |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `rating:`                                                                                                                                                   | `general` `sensitive` `explicit`                                                                                          |
| `status:`                                                                                                                                                   | `pending` `approved` `unapproved`                                                                                         |
| `availability:`                                                                                                                                             | `available` `down`                                                                                                        |
| `platform:`                                                                                                                                                 | `youtube` `niconico` `bilibili` `soundcloud` `twitter` `acfun`                                                            |
| `origin:`                                                                                                                                                   | `author` `reupload`                                                                                                       |
| `relation:`                                                                                                                                                 | `sequel` `respect` `collab_part` `sample`                                                                                 |
| `mediatype:`                                                                                                                                                | `anime` `show` `film` `game`                                                                                              |
| `role:`                                                                                                                                                     | `audio` `visuals` `director` `music` `artwork` `thanks`                                                                   |
| `id:` `width:` `height:` `duration:` `comments:` `bpm:` `sources:` `origins:` `reuploads:` `available_sources:` `available_origins:` `available_reuploads:` | Numeric range                                                                                                             |
| `tagcount:` `eventtags:` `creatortags:` `mediatags:` `sourcetags:` `songtags:` `gentags:` `metatags:` `uncattags:`                                          | Tag count range                                                                                                           |
| `relations:` `sequels:` `prequels:` `samples:` `sampled_by:` `respects:` `respected_by:` `collabs:` `collab_parts:`                                         | Relation count range                                                                                                      |
| `sequel:` `sample:` `respect:` `collab:`                                                                                                                    | Related work ID                                                                                                           |
| `order:`                                                                                                                                                    | `random` `id` `id_desc` `submitted`(`_asc`) `published`(`_asc`) `comment`(`_asc`) `resolution`(`_asc`) `duration`(`_asc`) |

## Tag attributes

Per-instance attributes on a tag are written in square brackets immediately after
the tag, with no space. Multiple brackets on the same tag are merged.

### `[sample]` (Creator/Media/Song tags only)

Whether this tag is treated as a _sample_ on the work (i.e. the work is a sample of this tag).

| Query               | Result                                                               |
| ------------------- | -------------------------------------------------------------------- |
| {{mmaker[sample]}}  | Works where the creator `mmaker` is marked as being used as a sample |
| {{mmaker[-sample]}} | Works where the creator `mmaker` is present but not used as a sample |

### `[role:...]` (Creator tags only)

| Query                           | Result                                                                |
| ------------------------------- | --------------------------------------------------------------------- |
| {{mmaker[role:visuals]}}        | Works where `mmaker` is credited with visuals                         |
| {{mmaker[role:audio,-visuals]}} | Works where `mmaker` is credited with audio but NOT visuals           |
| {{mmaker[role:any]}}            | Works where `mmaker` has any role assigned                            |
| {{mmaker[role:none]}}           | Works where `mmaker` has no role assigned                             |
| {{mmaker[role:none][-sample]}}  | Works where `mmaker` has no role assigned and is not used as a sample |

Available values:

- `audio`
- `visuals`,
- `director`
- `music`
- `artwork`
- `thanks`
- `any`
- `none`

Can be combined with commas. Prefix a value with `-` to require the bit be unset.

## Boolean composition

- **AND** - separate terms with spaces. `yamas touhou` requires both tags be present.
- **OR** - separate terms with `|`. Whitespace around it is optional. OR has lower precedence than AND, so `a b | c d` means `(a AND b) OR (c AND d)`.
- **NOT** - prefix any atom with `-`: `-touhou`, `-rating:general`, `-(a b)`.
- **Grouping** - parentheses can wrap any expression, including OR chains.

## Notes

- A query that fails to parse silently returns no results.
- The search query (separate from tags) does case insensitive matching over title, description, and source titles, with results being scored and sorted based on these fields. When tags are included in a search, the aforementioned fields are still searched, but the scored sorting is ignored.
