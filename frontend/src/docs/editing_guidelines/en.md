## Contributor License Agreement

See [Contributor License Agreement](/post/6).

## User levels

There are 4 user levels:

- Restricted
- Member
- Editor
- Admin

Admin team:

- [Brando](/profile/Brando)
- [chfr](/profile/chfr)
- [lachrymal](/profile/lachrymal)
- [mmaker](/profile/mmaker)
- [SnO2WMaN](/profile/SnO2WMaN)

## Unbound uploads

Members can submit new works from uploads available on external sites. Such submissions are called “unbound”, and they will be put in an approval pool, from which Editors are able to either approve the addition of a new work, add the upload to an existing work, or reject the submission outright. In case that two works are created for different uploads of the same work, Editors can rectify this issue by performing a merge. Note:

- Members may attach new uploads to existing works without additional approval.
- Editors can add new works directly.

## Tag categories

There are currently 7 categories for work tags, colour-coded as follows:

- General
- Creator: <otodb-worktag slug="yamas" ></otodb-worktag>
- Event: <otodb-worktag slug="realsample" ></otodb-worktag>
- Song: <otodb-worktag slug="red_zone" ></otodb-worktag>
- Source: <otodb-worktag slug="膳" ></otodb-worktag>
- Media: <otodb-worktag slug="キルミーベイベー" ></otodb-worktag>
- Meta: <otodb-worktag slug="本人巡回済み" ></otodb-worktag>

Boundary cases:

- `siivagunner` should be a Creator tag

There are currently 4 categories for song attributes:

- General
- Genre
- Author
- Meta

## Tag Parenting

Parent-child relations can be established between tags. A tag can have multiple parents. Cyclic hierarchies are not allowed.

- As a general rule of thumb, the vast majority of tags should only have at most one parent.
- Tags should VERY rarely have more than 2 parents.
- Tags should basically never have more than 3 parents, except for a select handful across the entire database.
- Avoid using parent relationships for categorization, prioritize clear semantic entailment. Consider writing a wiki page or adding connections instead if the parent tag represents an overly broad concept.

The primary purpose of having multiple parents is to accommodate "combination tags" prevalent on certain platforms, here is a canonical example:

- <otodb-worktag slug="東方壊鍵盤" ></otodb-worktag> descends from <otodb-worktag slug="キーボードクラッシャー" ></otodb-worktag> and <otodb-worktag slug="東方project" ></otodb-worktag>.

In such cases of "combination tags", where the tag introduces no additional semantics beyond the sum of its parents and one of its parent tags is in the Source category, the child tag should also be in the Source category as a general rule, even if the tag may have other parents that are Media tags or Meta tags. Rare exceptions may exist.

The notable exception to this are tags which express that the theme is combined with Otomad/YTPMV. In such cases they should be merged directly. For example, `フォニイ音madリンク` should instead be aliased to `フォニイ`.

## Wiki pages

- Be concise -- include only the minimal level of information necessary for a visitor with no prior background. The vast majority of wiki pages should not extend beyond 1 or 2 short paragraphs; most tags can and should be adequately explained within 3 or 4 short sentences. Provide a link to external sources and add external connections for more in-depth descriptions when appropriate.
- Wiki pages are written in Markdown. Please use appropriate formatting for headings, links, etc.
- Try to avoid being subjective or biased. Avoid descriptions like "stupid", "annoying", or "awesome". Do not editorialize.
- If you sense that you may not properly understand the usage of a tag, hold off from providing further information. Misleading information is much worse than absence of information.
- Maintain standard formatting. Avoid elements in non-expository tones, as much as it may be tempting to insert sections in a comedic or emphatic voice.
- Link to other tags when a related tag exists for the subject mentioned.

## Songs

Tags in the Song category are each associated with an additional song object, which contains metadata related to the song, such as title, author, BPM. If a song has a variable BPM, it can be marked as such, and the numerical value will instead serve as a reference. Song objects can be further extended with song attributes (which exist in a separate namespace from work tags), and relations can be established between songs, similar to works.

## Work tag merging and deprecation

This site leverages existing tags from external sites. But this poses some issues:

1. The same concept may exist under different names, and they can even be in different languages.
    - To address this, tags can be merged, effectively establishing aliases in the database. Merged tags will have a “base” tag, whose information is used as the canonical reference to the tag.
    - Display preferences can be set so that tags appear translated via an alias for each supported interface language.
    - When a language preference is not specified for the user’s interface language, the base tag is used for display.
2. Some tags may not make sense or may be irrelevant for our database.
    - To address this, tags can be marked as deprecated. They are hidden from the regular interface. An entry is kept for deprecated tags so that future imports can be automatically hidden.
    - Example: <otodb-worktag slug="もっと評価されるべき" ></otodb-worktag>

### Which tags ought to be merged?

Aside from localizations, there are a couple common cases:

1. Tags that are wordplays on a source, song, etc. commonly used to designate the usage of the specific subject should be merged to the more generic name
    - `フォニイ音madリンク` should be aliased to `フォニイ`.
    - `madか☆マギカ` should be aliased to `魔法少女まどか☆マギカ`.
2. Abridged/community media names should be aliased to the complete/official name
    - `ごちうさ` should be aliased to `ご注文はうさぎですか？`.
    - `btr` should be aliased to `bocchi_the_rock`
3. If an author has alt accounts or aliases under which there exists a significant amount of activity, they should be aliased to the author’s primary (most recognizable) name. (Exceptions may apply for drastically different identities.)
    - `coron_3` should be aliased to `yamas`.
    - It's true that determining the 'primary' name can be very subjective, hence there is no strict rule for this aside from being broadly recognizable.

## Romanization

For tags which originate from some sort of media or authority, prefer the localization used by official sources. For common (non-proper) names or phrases, always use semantic translations. Otherwise, for proper names, depending on the language:

- Japanese: [Hepburn](https://en.wikipedia.org/wiki/Hepburn_romanization). Do not use the long vowels marked by macrons in modified Hepburn, duplicate the vowel instead.
- Chinese: [Pinyin](https://en.wikipedia.org/wiki/Pinyin), without diacritics used for tones.
- Korean: [Revised Romanization (RR)](https://en.wikipedia.org/wiki/Revised_Romanization_of_Korean).

Note:

- If an “incorrect” unofficial romanization not following the guidelines above is already in wide use/widely accepted, correcting it may prove counter-productive.
- If an upstream tag does not follow convention in cases of typo or misspelling, a merge can be performed.
- In any case, word boundaries translate to underscores during romanization, unless otherwise marked by an existing symbol, such as a colon or a dash.

## English Dates

As this website appeals to an international audience, dates in English should have the month written out. Example: Jan 10, January 10 are acceptable. Do not use 10/1, 1/10, 1-10, 10-1, etc.  
Please note that an upstream tag from a Japanese, Chinese, or Korean source will likely still be in the format of MM followed by DD. This is the expected format in these languages, we expect you to know this if you are performing localizations, even if you are of anglophone background.

## Disambiguation

In general, when tags designating different subjects have name clashes, use the format `abc_(def)` to disambiguate. For example, if there is a creator named `bocchi_the_rock`: use `bocchi_the_rock_(creator)`.

- When the tags in conflict are of different categories, it’s recommended to add the suffix to Creator and Song tags over adding it to Source tags.
- If the tags are in conflict in the same category, the suffix should still be something obvious and recognizable, for example:
    - For creators, try using the website on which they are primarily active.
    - For songs, use the artist’s name.

### Tag display names

A tag's display name, consisting of a base tag and aliases, can be set and later modified, such as changes to its capitalization, within certain limits.

- **Proper nouns** (Creator, Event, Song, Source, Media) should use correct capitalization, following their official written style.
    - <otodb-worktag slug="jack_black" ></otodb-worktag> (not `jack black`)
    - <otodb-worktag slug="beat_shobon" ></otodb-worktag> (styled lowercase and underscore)
    - <otodb-worktag slug="idolmaster" ></otodb-worktag> (stylized all caps)
- **Acronyms** should always be written in their conventional capitalized and punctuated form.
- General and Meta tags are often not proper nouns nor acronyms, and therefore in most situations do not require special attention.

Changes to a tag's display name that fundamentally would modify the representation of the tag are rejected by the system. If you need to make such a change to a tag, a new tag should be created instead, and aliased or merged as necessary.

### Invalid names

Some creators may choose identifiers on platforms that are become invalid post-normalization. Examples include names that consist exclusively of empty space characters, dots, or underscores that are otherwise illegible. In these cases, use a name that combines the identifier from the platform, with a disambiguate suffix specifying the platform, for example:

- The user has profile `https://www.nicovideo.jp/user/123456`:
    - Use the tag `123456_(niconico)`
- The user has profile `https://www.youtube.com/@asdf__12345`:
    - Use the tag `asdf__12345_(youtube)`

## Relations

Special relations may be established among works, and among songs. This creates directed graphs for works and songs. Relations may be edited from either side of the relationship.  
Currently, there are 4 types of work relations:

- Sequel
- Respect
- Collab part
- Sample

If a separate upload for a collab part A which is a respect of a different work B is registered as a work separate from the collab C:

- A \-\> B: Respect
- A \-\> C: Collab part
- Do not register C -\> B: Respect

Currently, there are 4 types of song relations:

- Remix
- Remaster
- Medley part
- Sequel
