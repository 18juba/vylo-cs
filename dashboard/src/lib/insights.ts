import {num, type Row} from './data';
import {monthlyChurn} from './churn';

const pct=(a:number,b:number)=>b?(a/b*100).toLocaleString('pt-BR',{maximumFractionDigits:1})+'%':'indisponível';
const decimal=(n:number)=>n.toLocaleString('pt-BR',{maximumFractionDigits:1});
const iso=(d:string)=>d.split('/').reverse().join('-');
const label=(m:string)=>new Date(m+'-02T12:00:00').toLocaleDateString('pt-BR',{month:'long',year:'numeric'});

export function buildInsights(sellers:Row[],sales:Row[],calls:Row[]){
 const months=[...new Set(sales.map(r=>r.mes))].sort();
 const end=months.at(-1)??'';
 const cancelled=sellers.filter(s=>s.data_cancelamento&&months.includes(iso(s.data_cancelamento).slice(0,7)));
 const churn=monthlyChurn(sellers,months);
 const first=churn.slice(0,3),last=churn.slice(-3);
 const pooled=(rows:typeof churn)=>({loss:rows.reduce((a,r)=>a+r.cancellations,0),base:rows.reduce((a,r)=>a+r.initial,0)});
 const a=pooled(first),b=pooled(last);
 const peak=churn.filter(r=>r.rate!==null).sort((x,y)=>(y.rate??0)-(x.rate??0))[0];
 const essential=sellers.filter(s=>s.plano==='Essencial');
 const essentialLoss=cancelled.filter(s=>s.plano==='Essencial').length;
 const cancelIds=new Set(cancelled.map(s=>s.seller_id));
 const sellerMap=new Map(sellers.map(s=>[s.seller_id,s]));
 const response=(lost:boolean)=>{
  const eligible=calls.filter(r=>{const s=sellerMap.get(r.seller_id);if(!s)return false;
   if(lost)return cancelIds.has(s.seller_id)&&iso(r.data)<=iso(s.data_cancelamento);
   return !s.data_cancelamento||iso(s.data_cancelamento).slice(0,7)>end;
  });
  const valid=eligible.map(r=>num(r.tempo_resposta_h)).filter((n):n is number=>n!==null&&n>=0);
  return {count:valid.length,total:eligible.length,mean:valid.length?valid.reduce((a,b)=>a+b,0)/valid.length:null};
 };
 const lost=response(true),retained=response(false);
 const series=churn.map(r=>({grupo:label(r.month),base:r.initial,resultado:`${r.cancellations} cancelamentos · ${r.rate===null?'indisponível':decimal(r.rate)+'%'}`}));
 return {period:months.length?`${label(months[0])} a ${label(end)}`:'Sem período disponível',cards:[
  {title:'A perda de clientes se concentrou no fim do período',metric:`${b.loss} cancelamentos nos últimos três meses`,evidence:`Nos primeiros três meses foram ${a.loss} cancelamentos; nos últimos três, ${b.loss}. A taxa mensal agregada passou de ${pct(a.loss,a.base)} para ${pct(b.loss,b.base)}. ${peak?`O pico foi em ${label(peak.month)}: ${peak.cancellations} de ${peak.initial} sellers (${decimal(peak.rate??0)}%).`:''}`,why:'A aceleração das perdas pede uma rotina de retenção antes do encerramento da relação, além do acompanhamento de vendas.',action:'Revisar os motivos dos cancelamentos e realizar uma reunião semanal entre os responsáveis de CS para acompanhar sellers em deterioração e ações de recuperação.',owner:'Gestão de CS · revisão semanal',limit:'Taxa mensal agregada = soma dos cancelamentos ÷ soma das carteiras iniciais dos meses. Não é churn acumulado do trimestre. Cadastro completo e ausência de reativações não registradas são pressupostos.',rows:series},
  {title:'O plano Essencial merece uma revisão da jornada',metric:`${essentialLoss} de ${essential.length} sellers cancelaram`,evidence:`O Essencial representa ${pct(essential.length,sellers.length)} dos cadastros e ${pct(essentialLoss,cancelled.length)} dos cancelamentos no período. A proporção de cadastros cancelados nesse plano é ${pct(essentialLoss,essential.length)}.`,why:'A concentração permite direcionar a investigação e testar melhorias de acompanhamento para o grupo mais numeroso entre as perdas.',action:'Revisar onboarding, expectativas e adoção no Essencial. Testar uma cadência de acompanhamento em um grupo piloto e comparar retenção com sellers de tempo de carteira semelhante.',owner:'CS e onboarding · piloto de acompanhamento',limit:'Proporção de cancelados no cadastro, não churn mensal. Plano atual, tamanhos dos grupos e tempo de exposição podem explicar parte das diferenças; não demonstra efeito causal do plano.',rows:['Essencial','Pro','Premium'].map(plan=>{const group=sellers.filter(s=>s.plano===plan);const loss=cancelled.filter(s=>s.plano===plan).length;return {grupo:plan,base:group.length,resultado:`${loss} cancelados · ${pct(loss,group.length)}`};})},
  {title:'Atendimentos de clientes perdidos tiveram respostas mais lentas',metric:lost.mean!==null&&retained.mean!==null?`${decimal(lost.mean)} h vs. ${decimal(retained.mean)} h`:'Cobertura insuficiente',evidence:`Antes ou no dia do cancelamento, a média de resposta foi ${lost.mean===null?'indisponível':decimal(lost.mean)+' h'} em ${lost.count} atendimentos com tempo informado. Para sellers ativos no fim do histórico, foi ${retained.mean===null?'indisponível':decimal(retained.mean)+' h'} em ${retained.count} atendimentos.`,why:'A diferença justifica investigar filas, complexidade dos casos e tempo até a resolução, especialmente nas contas com outros sinais de dificuldade.',action:'Definir metas de resposta por motivo e gravidade, revisar casos demorados e acompanhar pendências até resolução. Comparar também mediana e percentis antes de estabelecer um SLA.',owner:'Operação de CS · revisão de filas e metas',limit:'Associação descritiva por atendimento, não causalidade. Problemas mais complexos podem levar a respostas lentas e cancelamento. Períodos de exposição diferem e atendimentos frequentes têm maior peso.',rows:[{grupo:'Cancelados: até a data do cancelamento',base:`${lost.count}/${lost.total} com tempo informado`,resultado:lost.mean===null?'Indisponível':decimal(lost.mean)+' h'},{grupo:'Ativos ao final do histórico',base:`${retained.count}/${retained.total} com tempo informado`,resultado:retained.mean===null?'Indisponível':decimal(retained.mean)+' h'}]}
 ]};
}
