import type {Row} from '#lib/data.js';
export function frequencies(rows:Row[],field:string){
 const counts=new Map<string,number>();
 for(const row of rows){const label=row[field]?.trim()||'Não informado';counts.set(label,(counts.get(label)??0)+1);}
 return [...counts].map(([label,count])=>({label,count})).sort((a,b)=>b.count-a.count||a.label.localeCompare(b.label,'pt-BR'));
}
