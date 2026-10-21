export type Row = Record<string, string>;
export function parseCSV(text: string): Row[] {
 const records: string[][] = []; let row: string[] = [], value = '', quoted = false;
 for (let i=0;i<text.length;i++) { const c=text[i];
  if(c==='"') { if(quoted && text[i+1]==='"'){value+='"';i++;}else quoted=!quoted; }
  else if(c===','&&!quoted){row.push(value);value='';}
  else if((c==='\n'||c==='\r')&&!quoted){if(c==='\r'&&text[i+1]==='\n')i++;row.push(value);if(row.some(Boolean))records.push(row);row=[];value='';}
  else value+=c;
 } if(value||row.length){row.push(value);records.push(row);} if(quoted)throw new Error('CSV com aspas não fechadas.');
 const headers=records.shift()?.map(s=>s.replace(/^\uFEFF/,''))??[];
 return records.map(r=>{if(r.length!==headers.length)throw new Error('CSV com estrutura inválida.');return Object.fromEntries(headers.map((h,i)=>[h,r[i]]));});
}
export const money=(n:number)=>new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL',maximumFractionDigits:0}).format(n);
export const integer=(n:number)=>new Intl.NumberFormat('pt-BR').format(n);
export const num=(v:string|undefined)=>v?.trim()!==''&&v!==undefined&&Number.isFinite(Number(v))?Number(v):null;
export function health(seller:Row,sales:Row[],calls:Row[],month:string){
 const history=sales.filter(r=>r.seller_id===seller.seller_id&&r.mes<=month).sort((a,b)=>a.mes.localeCompare(b.mes));
 const latest=history.findLast(r=>r.mes===month);const prev=history.findLast(r=>r.mes<month);
 const revenue=num(latest?.faturamento),before=num(prev?.faturamento);
 const change=revenue!==null&&before!==null&&before>0?(revenue-before)/before*100:null;
 const relevant=calls.filter(r=>r.seller_id===seller.seller_id&&r.data.split('/').reverse().join('-').slice(0,7)===month);
 const reasons:string[]=[];let score=0;
 if(change!==null&&change<=-20){score+=35;reasons.push('Queda de faturamento ≥ 20%');}
 if(latest&&['Laranja','Vermelha'].includes(latest.reputacao)){score+=25;reasons.push('Reputação '+latest.reputacao.toLowerCase());}
 if((num(latest?.taxa_reclamacao_pct)??0)>=3){score+=20;reasons.push('Reclamações ≥ 3%');}
 if(relevant.some(r=>r.resolvido==='Não')){score+=10;reasons.push('Atendimento não resolvido no mês');}
 if(relevant.some(r=>{const n=num(r.nota_satisfacao);return n!==null&&n<=2;})){score+=10;reasons.push('Satisfação ≤ 2 no mês');}
 if(!latest)reasons.push('Sem vendas registradas no mês');
 if(latest?.pendencias_tratamento)reasons.push('Dados de vendas com pendências');
 return {seller,latest,revenue,change,score,reasons,level:score>=50?'Alta':score>=20?'Moderada':latest?'Baixa':'Sem dados'};
}
