from typing import TYPE_CHECKING

import diff_match_patch as dmp_mod

from otodb.models import TagWork

if TYPE_CHECKING:
    from ..models import Implication as T_Implication
    from ..models import MediaSong as T_MediaSong
    from ..models import MediaWork as T_MediaWork
    from ..models.base import MediaBase as T_MediaBase

def get_diff(delta):
    dmp = dmp_mod.diff_match_patch()

    def diff_prettyHtml(diffs):
        html = []
        for (op, data) in diffs:
            text = (data.replace("&", "&amp;").replace("<", "&lt;")
                        .replace(">", "&gt;").replace("\n", "&para;<br>"))
            if op == dmp.DIFF_INSERT:
                html.append("<ins>%s</ins>" % text)
            elif op == dmp.DIFF_DELETE:
                html.append("<del>%s</del>" % text)
            elif op == dmp.DIFF_EQUAL:
                html.append("<span>%s</span>" % text)
        return "".join(html)
        
    diffs_html = []

    for change in delta.changes:
        match change.field:
            case 'tags':
                old, new = set([c['tagwork'] for c in change.old]), set([c['tagwork'] for c in change.new])
                old, new = old - new, new - old
                changes = ['- ' + str(TagWork.objects.get(id=id_)) for id_ in old] + ['+ ' + str(TagWork.objects.get(id=id_)) for id_ in new]
                diffs_html.append({'html': ('<br>').join(changes), 'field': change.field})
            case _:
                old, new = change.old, change.new
                diff_field = dmp.diff_main(old, new)
                dmp.diff_cleanupSemantic(diff_field)
                 
                diffs_html.append({'html': diff_prettyHtml(diff_field).replace('&para;', ''), 'field': change.field})

    return diffs_html
