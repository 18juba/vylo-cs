<script lang="ts">
 import Chart from '#lib/Chart.svelte';
 import { planColors } from '#lib/colors.js';
 import type {Snippet} from 'svelte';
 import type {Row} from '#lib/data.js';
 import {frequencies} from '#lib/frequencies.js';
 let {sellers,calls,sales,children,donuts}:{sellers:Row[];calls:Row[];sales:Row[];children?:Snippet;donuts?:Snippet}=$props();
 const groups=$derived([
  {title:'Sellers por plano',source:'Cadastro de sellers',rows:sellers,field:'plano'},
  {title:'Sellers por responsável CS',source:'Cadastro de sellers',rows:sellers,field:'responsavel_cs'},
  {title:'Sellers por status',source:'Situação atual do cadastro',rows:sellers,field:'status'},
  {title:'Sellers por segmento',source:'Cadastro de sellers',rows:sellers,field:'segmento'},
  {title:'Atendimentos por canal',source:'Todos os registros de atendimento',rows:calls,field:'canal'},
  {title:'Atendimentos por motivo',source:'Todos os registros de atendimento',rows:calls,field:'motivo'},
  {title:'Reputação nas vendas mensais',source:'Registros seller × mês, não sellers únicos',rows:sales,field:'reputacao'},
  {title:'Atendimentos por resolução',source:'Situação registrada nos atendimentos',rows:calls,field:'resolvido'}
 ].map(group=>({...group,counts:frequencies(group.rows,group.field)})));
 const palette=['#8559ee','#25aebd','#a47bea','#65c7ce','#6840b2','#22919f','#ba9be5','#87d4d8'];
</script>
<section class="frequencies" aria-label="Desempenho e distribuições de frequência">
 {#each [true,false] as isDonut}<div class="frequency-grid" class:donut-grid={isDonut} aria-label={isDonut?'Gráficos de donut':'Gráficos de barras'}>
 {#if isDonut}{@render donuts?.()}{:else}{@render children?.()}{/if}
 {#each groups.filter(g=>['plano','status','resolvido'].includes(g.field)===isDonut) as group}<article class="panel"><div class="panel-heading"><div><h3>{group.title}</h3><p>{group.source} · {group.rows.length.toLocaleString('pt-BR')} registros</p></div></div><Chart kind={isDonut?'doughnut':'bar'} title={group.title} labels={group.counts.map(r=>r.label)} values={group.counts.map(r=>r.count)} countTotal={group.rows.length} colors={group.counts.map((r,i)=>group.field==='plano'?(planColors[r.label]??'#8559ee'):group.field==='reputacao'?({Verde:'#258667',Amarela:'#d1a50c',Laranja:'#e7832b',Vermelha:'#cf4755'}[r.label]??palette[i%palette.length]):group.field==='status'||group.field==='resolvido'?(['Ativo','Sim'].includes(r.label)?'#25aebd':['Cancelado','Não'].includes(r.label)?'#b05a82':palette[i%palette.length]):palette[i%palette.length])} height={isDonut?170:240}/></article>{/each}</div>{/each}
</section>
<style>
 .frequencies{margin:12px 0 22px}.frequency-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-bottom:16px}.donut-grid{grid-template-columns:repeat(4,minmax(0,1fr))}.frequency-grid :global(> .panel){height:390px;overflow-y:auto;min-width:0;border-color:#e9e2f0;border-radius:14px;box-shadow:0 3px 16px #35204b04;transition:border-color .18s,box-shadow .18s}.frequency-grid :global(> .panel:hover){border-color:#d7c5ef;box-shadow:0 5px 22px #65408b09}.donut-grid :global(> .panel){height:310px}.donut-grid :global(.panel-heading){height:74px}.frequency-grid :global(.panel-heading){height:84px;padding:16px 18px 4px;align-items:start}.frequency-grid :global(.panel-heading h2),.panel-heading h3{font-size:14px;line-height:1.4;margin:0}.frequency-grid :global(.panel-heading p){font-size:11px;color:#8a7b97;margin-top:5px}@media(max-width:1350px){.donut-grid,.frequency-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:800px){.donut-grid,.frequency-grid{grid-template-columns:1fr}}
</style>
