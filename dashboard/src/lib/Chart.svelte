<script lang="ts">
 import { onMount } from 'svelte';
 import Chart from 'chart.js/auto';
 let { labels, values, title, kind='line', colors }: {labels:string[];values:(number|null)[];title:string;kind:'line'|'bar';colors?:string[]}=$props();
 let canvas:HTMLCanvasElement;let chart:Chart|undefined;let ready=$state(false);
 onMount(()=>{ready=true;return()=>chart?.destroy();});
 $effect(()=>{
  if(ready&&canvas){
   chart?.destroy();
   chart=new Chart(canvas,{
    type:kind,
    data:{labels,datasets:[{label:title,data:values,borderColor:kind==='bar'?(colors??'#35c5d6'):'#8559ee',backgroundColor:kind==='line'?'#8559ee18':(colors??'#35c5d6'),fill:true,tension:0.35,borderWidth:kind==='bar'?0:3}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{grid:{display:false}},y:{grid:{color:'#f0edf5'},ticks:{callback:(v)=>Number(v)>=1000?`${Math.round(Number(v)/1000)} mil`:v}}}}
   });
  }
 });
</script>
<div class="chart"><canvas bind:this={canvas} aria-label={title}>{title}</canvas></div>
<details><summary>Ver valores do gráfico</summary><div class="chart-values">{#each labels as label,i}<span>{label}: {values[i]?.toLocaleString('pt-BR')??'Sem dados'}</span>{/each}</div></details>
