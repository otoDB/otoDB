import type { PageServerLoad } from "./$types";
import client from "$lib/api";
import { D2 } from '@terrastruct/d2';
import { base } from "$app/paths";
import { WorkRelationTypes } from "$lib/enums";

const d2 = new D2();

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { data, error } = await client.GET('/api/work/relations', { params: {
        query: {
            work_id: +params.work_id
        }
    }, fetch });

    if (error)
        return; // TODO
    
    const [relations, works] = data;
    if (relations.length === 0)
        return;

    // TODO temporary workaround https://github.com/terrastruct/d2/issues/2357
    const placeholderLink = (n: number) => `https://@WL_${n}`;

    const source = `direction: right
    ${
        works.map(w => `${w.id}: ${w.title} {
             shape: image
             icon: ${w.thumbnail}
             link: ${placeholderLink(w.id!)}
             ${+params.work_id === w.id ? 'style: { font-color: red }' : ''}
        }`).join('\n')
    }
    ${
        relations.map(r => `${r.A.id} -> ${r.B.id}: ${WorkRelationTypes[r.relation]()}`).join('\n')
    }`;
    
    const result = await d2.compile(source);
    let svg = await d2.render(result.diagram, { ...result.renderOptions, darkThemeID: 200, noXMLTag: true});

    svg = svg.replace(/<!\[CDATA\[.*?]]>/gs, '<![CDATA[.appendix-icon{display:none;}]]>');

    for (const work of works)
        svg = svg.replace(placeholderLink(work.id!), `${base}/work/${work.id}`);

    return {
        relations_svg: svg
    };
};
