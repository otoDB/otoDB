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

    // D2.js Currently has issues with unicode among other things
    const placeholderTitle = (id: string, n: number) => {
        const s = `!WT_${id}`;
        return s + '_'.repeat(Math.max(0, n - s.length));
    };
    const placeholderRelation = n => `____REL_${n}`;
    const placeholderLink = n => `https://@WL_${n}`;

    const source = `direction: right
    ${
        works.map(w => `${w.id}: ${placeholderTitle(w.id, w.title.length)} {
             shape: image
             icon: ${w.thumbnail}
             link: ${placeholderLink(w.id)}
             ${+params.work_id === w.id ? 'style: { font-color: red }' : ''}
        }`).join('\n')
    }
    ${
        relations.map((r, i) => `${r.A.id} -> ${r.B.id}: ${placeholderRelation(i)}`).join('\n')
    }`;
    
    const result = await d2.compile(source);
    let svg = await d2.render(result.diagram);

    svg = svg.slice(38); // kill XML processor tag
    svg = svg.replace(/<!\[CDATA\[.*?]]>/gs, '<![CDATA[.appendix-icon{display:none;}]]>');

    for (const work of works) {
        svg = svg.replace(placeholderTitle(work.id, work.title.length), work.title);
        svg = svg.replace(placeholderLink(work.id), `${base}/work/${work.id}`);
    }
    for (let i = 0; i < relations.length; i++)
        svg = svg.replace(placeholderRelation(i), WorkRelationTypes[relations[i].relation]());

    return {
        relations_svg: svg
    };
};
