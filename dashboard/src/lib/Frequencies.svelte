<script lang="ts">
 import Chart from '#lib/Chart.svelte';
 import type {Row} from '#lib/data.js';
 import {frequencies} from '#lib/frequencies.js';
 let {sellers,calls}:{sellers:Row[];calls:Row[]}=$props();
 const groups=$derived([
  {title:'Sellers por plano',source:'Cadastro de sellers',rows:sellers,field:'plano'},
  {title:'Sellers por responsável CS',source:'Cadastro de sellers',rows:sellers,field:'responsavel_cs'},
  {title:'Sellers por status',source:'Situação atual do cadastro',rows:sellers,field:'status'},
  {title:'Sellers por segmento',source:'Cadastro de sellers',rows:sellers,field:'segmento'},
  {title:'Atendimentos por canal',source:'Todos os registros de atendimento',rows:calls,field:'canal'},
  {title:'Atendimentos por motivo',source:'Todos os registros de atendimento',rows:calls,field:'motivo'}
 ].map(group=>({...group,counts:frequencies(group.rows,group.field)})));
 const palette=['#8559ee','#25aebd','#a47bea','#65c7ce','#6840b2','#22919f','#ba9be5','#87d4d8'];
</script>
<section class="frequencies" aria-label="Distribuições de frequência"><div class="frequency-heading"><h2>Perfil da carteira e dos atendimentos</h2><p>Contagens e participação no total · todos os responsáveis · histórico completo dos atendimentos</p></div><div class="frequency-grid">{#each groups as group}<article class="panel"><div class="panel-heading"><div><h3>{group.title}</h3><p>{group.source} · {group.rows.length.toLocaleString('pt-BR')} registros</p></div></div><Chart kind="bar" title={group.title} labels={group.counts.map(r=>r.label)} values={group.counts.map(r=>r.count)} countTotal={group.rows.length} colors={group.counts.map((r,i)=>group.field==='status'?(r.label==='Ativo'?'#25aebd':r.label==='Cancelado'?'#b05a82':palette[i%palette.length]):palette[i%palette.length])} height={Math.max(125,group.counts.length*27+40)}/></article>{/each}</div></section>
<style>.frequencies{margin:24px 0}.frequency-heading{margin-bottom:14px}.frequency-heading h2{font-size:19px;margin:0 0 5px}.frequency-heading p{font-size:12px;color:#675773}.frequency-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;align-items:start}.panel-heading{padding:16px 18px 4px}.panel-heading h3{font-size:14px;margin:0}.panel-heading p{font-size:11px;color:#675773;margin-top:5px}@media(max-width:1250px){.frequency-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:800px){.frequency-grid{grid-template-columns:1fr}}</style>
