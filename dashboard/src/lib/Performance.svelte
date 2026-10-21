<script lang="ts">
 import Chart from '#lib/Chart.svelte';
 import {money,integer,num,type Row} from '#lib/data.js';
 let {sellers,sales}:{sellers:Row[];sales:Row[]}=$props();
 let metric=$state('revenue');
 const plans=['Essencial','Pro','Premium'];
 const colors:Record<string,string>={'Amazon':'#FF9900','Magalu':'#0086FF','Mercado Livre':'#FFE600','Shopee':'#EE4D2D'};
 const markets=$derived([...new Set(sellers.map(s=>s.marketplace))].sort());
 const metrics:Record<string,string>={revenue:'Faturamento acumulado (R$)',orders:'Pedidos válidos',perSeller:'Faturamento por seller (R$)',ticket:'Ticket médio ponderado (R$)'};
 function summarize(group:Row[]){
  const ids=new Set(group.map(s=>s.seller_id));
  const rows=sales.filter(r=>ids.has(r.seller_id));
  const revenueRows=rows.filter(r=>num(r.faturamento)!==null);
  const revenue=revenueRows.reduce((sum,r)=>sum+Number(r.faturamento),0);
  const orderRows=rows.filter(r=>{const n=num(r.pedidos);return n!==null&&n>=0&&Number.isInteger(n);});
  const orders=orderRows.reduce((sum,r)=>sum+Number(r.pedidos),0);
  const paired=orderRows.filter(r=>{const n=num(r.faturamento);return n!==null&&n>=0;});
  const denominator=paired.reduce((sum,r)=>sum+Number(r.pedidos),0);
  const observed=new Set(revenueRows.map(r=>r.seller_id)).size;
  return {count:group.length,observed,revenue:revenueRows.length?revenue:null,orders:orderRows.length?orders:null,perSeller:observed?revenue/observed:null,ticket:denominator>0?paired.reduce((sum,r)=>sum+Number(r.faturamento),0)/denominator:null};
 }
 const byMarket=$derived(markets.map(label=>({label,...summarize(sellers.filter(s=>s.marketplace===label))})));
 const byPlan=$derived(plans.map(label=>({label,...summarize(sellers.filter(s=>s.plano===label))})));
 const crossed=$derived(markets.flatMap(market=>plans.map(plan=>({market,plan,...summarize(sellers.filter(s=>s.marketplace===market&&s.plano===plan))}))));
 function metricValue(row:ReturnType<typeof summarize>){return row[metric as 'revenue'|'orders'|'perSeller'|'ticket'];}
 const displayMoney=(n:number|null)=>n===null?'Sem dados':money(n);
</script>
<section class="performance-section" aria-label="Desempenho por marketplace e plano">
 <div class="performance-heading"><div><span class="eyebrow">COMPARAÇÃO DE DESEMPENHO</span><h2>Marketplace e plano, lado a lado.</h2><p>Todo o histórico · todos os responsáveis · incluindo sellers cancelados</p></div><label>Indicador dos gráficos <select bind:value={metric}>{#each Object.entries(metrics) as [value,label]}<option {value}>{label}</option>{/each}</select></label></div>
 <div class="charts-grid"><article class="panel"><div class="panel-heading"><div><h2>Desempenho por marketplace</h2><p>{metrics[metric]}</p></div></div><Chart kind="bar" title={metrics[metric]+' por marketplace'} labels={byMarket.map(r=>r.label)} values={byMarket.map(metricValue)} colors={byMarket.map(r=>colors[r.label]??'#8559ee')}/></article><article class="panel"><div class="panel-heading"><div><h2>Desempenho por plano</h2><p>{metrics[metric]}</p></div></div><Chart kind="bar" title={metrics[metric]+' por plano'} labels={byPlan.map(r=>r.label)} values={byPlan.map(metricValue)} colors={['#35c5d6','#8559ee','#be77dc']}/></article></div>
 <article class="panel"><div class="panel-heading"><div><span class="eyebrow">VISÃO CRUZADA</span><h2>Resultados por marketplace × plano</h2><p>Compare volume e desempenho médio para considerar carteiras de tamanhos diferentes.</p></div></div><div class="table-scroll"><table><thead><tr><th>MARKETPLACE</th><th>PLANO</th><th>SELLERS</th><th>COM FATURAMENTO</th><th>FATURAMENTO</th><th>PEDIDOS VÁLIDOS</th><th>FATURAMENTO / SELLER¹</th><th>TICKET MÉDIO²</th></tr></thead><tbody>{#each crossed as row}<tr><td><span class="market-marker" style:background={colors[row.market]??'#8559ee'}></span>{row.market}</td><td>{row.plan}</td><td>{integer(row.count)}</td><td>{integer(row.observed)}</td><td class="tabular">{displayMoney(row.revenue)}</td><td>{row.orders===null?'Sem dados':integer(row.orders)}</td><td class="tabular">{displayMoney(row.perSeller)}</td><td class="tabular">{displayMoney(row.ticket)}</td></tr>{/each}</tbody></table></div><div class="performance-notes"><p>¹ Faturamento acumulado dividido pelos sellers com faturamento informado. Diferenças no tempo de carteira também afetam essa comparação.</p><p>² Soma do faturamento ÷ soma dos pedidos, usando apenas registros com ambos válidos e pedidos não negativos. Sem denominador positivo, o resultado fica indisponível. Valores negativos de pedidos são excluídos.</p><p>Marketplace e plano refletem o cadastro disponível; não há histórico de mudanças de plano. Valores com pendências preservados na base continuam incluídos.</p></div></article>
</section>
<style>
 .performance-section{margin-bottom:26px}.performance-heading{display:flex;justify-content:space-between;align-items:center;gap:20px;margin:30px 0 20px}.performance-heading h2{font-size:22px}.performance-heading label{display:flex;flex-direction:column;gap:7px;color:#8c859b;font-size:10px}.market-marker{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:8px}.performance-notes{padding:14px 24px}.performance-notes p{font-size:12px;color:#675773;max-width:950px}@media(max-width:700px){.performance-heading{align-items:start;flex-direction:column}.performance-heading label,.performance-heading select{width:100%}}
</style>
