<script lang="ts">
 import {onMount} from 'svelte';
 import Chart from 'chart.js/auto';
 let {labels,values,title,kind='line',colors,height,countTotal}:{labels:string[];values:(number|null)[];title:string;kind:'line'|'bar';colors?:string[];height?:number;countTotal?:number}=$props();
 let canvas:HTMLCanvasElement;
 let ready=$state(false);
 onMount(()=>{ready=true;});
 const compact=(v:string|number)=>Number(v)>=1000?new Intl.NumberFormat('pt-BR',{notation:'compact',maximumFractionDigits:1}).format(Number(v)):v;
 $effect(()=>{
  if(!ready||!canvas)return;
  const horizontal=kind==='bar';
  const chart=new Chart(canvas,{
   type:kind,
   data:{labels,datasets:[{label:title,data:values,borderColor:horizontal?(colors??'#35c5d6'):'#8559ee',backgroundColor:horizontal?(colors??'#35c5d6'):'#8559ee18',fill:!horizontal,tension:.35,borderWidth:horizontal?0:3,...(horizontal?{barThickness:9,maxBarThickness:9,borderRadius:4}: {})}]},
   options:{indexAxis:horizontal?'y':'x',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:context=>{const value=values[context.dataIndex];return value===null?'Sem dados':`${value?.toLocaleString('pt-BR')}${countTotal?` (${((value??0)/countTotal*100).toLocaleString('pt-BR',{maximumFractionDigits:1})}%)`:''}`;}}}},scales:horizontal?{x:{beginAtZero:true,grid:{color:'#f0edf5'},ticks:{color:'#675773',callback:compact,...(countTotal!==undefined?{precision:0}:{})}},y:{grid:{display:false},ticks:{autoSkip:false,color:'#4b3c60',font:{size:12}}}}:{x:{grid:{display:false}},y:{grid:{color:'#f0edf5'},ticks:{callback:compact}}}}
  });
  return ()=>chart.destroy();
 });
</script>
<div class="chart" style:height={height?`${height}px`:undefined}><canvas bind:this={canvas} aria-label={title}>{title}</canvas></div>
<details><summary>Ver valores do gráfico</summary><div class="chart-values">{#each labels as label,i}<span>{label}: {values[i]?.toLocaleString('pt-BR')??'Sem dados'}{#if countTotal} ({((values[i]??0)/countTotal*100).toLocaleString('pt-BR',{maximumFractionDigits:1})}%){/if}</span>{/each}</div></details>
