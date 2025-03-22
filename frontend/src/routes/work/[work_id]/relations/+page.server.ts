import type { PageServerLoad } from "./$types";
import client from "$lib/api";
import { D2 } from '@terrastruct/d2';
import { WorkRelationTypes } from "$lib/enums";

const d2 = new D2();

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { data } = await client.GET('/api/work/relations', { params: {
        query: {
            work_id: +params.work_id
        }
    }, fetch });
    
    const [relations, works] = data!;
    if (relations.length === 0)
        return;

    const source = `direction: right
    ${
        works.map(w => `${w.id}: ${w.title} {
             shape: image
             icon: ${w.thumbnail}
             link: ${`/work/${w.id}`}
             ${+params.work_id === w.id ? 'style: { font-color: red }' : ''}
        }`).join('\n')
    }
    ${
        relations.map(r => `${r.A__id} -> ${r.B__id}: ${WorkRelationTypes[r.relation]()}`).join('\n')
    }`;
    
    const result = await d2.compile(source);
    let svg = await d2.render(result.diagram, { ...result.renderOptions, darkThemeID: 200, noXMLTag: true});

    svg = svg.replace(/\.appendix-icon {.*?}/gs, '.appendix-icon{display:none;}');

    return {
        relations_svg: svg
    };
};
