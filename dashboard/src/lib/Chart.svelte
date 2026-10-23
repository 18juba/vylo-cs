<script lang="ts">
 import {onMount} from 'svelte';
 import Chart from 'chart.js/auto';
 import {frequencyAccents} from '#lib/frequencyStyle.js';
 import {tooltipStyle,hoverGuide,lineGradient} from '#lib/chartStyle.js';
 let {labels,values,title,kind='line',colors,height,countTotal}:{labels:string[];values:(number|null)[];title:string;kind:'line'|'bar'|'doughnut';colors?:string[];height?:number;countTotal?:number}=$props();
 let canvas:HTMLCanvasElement;
 let ready=$state(false);
 onMount(()=>{ready=true;});
 const compact=(v:string|number)=>Number(v)>=1000?new Intl.NumberFormat('pt-BR',{notation:'compact',maximumFractionDigits:1}).format(Number(v)):v;
 $effect(()=>{
  if(!ready||!canvas)return;
  const horizontal=kind==='bar';
  const donut=kind==='doughnut';
  const chart=new Chart(canvas,{
   type:kind,plugins:[hoverGuide,frequencyAccents(countTotal)],
   data:{labels,datasets:[{label:title,data:values,borderColor:donut?'#ffffff':horizontal?(colors??'#35c5d6'):'#8559ee',backgroundColor:horizontal||donut?(colors??'#35c5d6'):(context: {chart: Chart})=>lineGradient(context.chart),fill:kind==='line',tension:.35,cubicInterpolationMode:'monotone',borderCapStyle:'round',borderJoinStyle:'round',pointRadius:2,pointHoverRadius:6,pointHitRadius:16,pointBackgroundColor:'#ffffff',pointBorderColor:'#8559ee',pointBorderWidth:2,pointHoverBackgroundColor:'#8559ee',pointHoverBorderColor:'#ffffff',pointHoverBorderWidth:3,borderWidth:horizontal?0:donut?2:3,...(donut?{spacing:3,borderRadius:5,hoverOffset:5}:{}),...(horizontal?{barThickness:8,maxBarThickness:8,borderRadius:10,borderSkipped:false,hoverBackgroundColor:colors??'#8559ee'}: {})}]},
   options:{...(donut?{cutout:'74%'}:{}),layout:{padding:{right:horizontal&&countTotal!==undefined?36:5,left:0,top:5,bottom:0}},indexAxis:horizontal?'y':'x',responsive:true,maintainAspectRatio:false,animation:{duration:window.matchMedia('(prefers-reduced-motion: reduce)').matches?0:350},interaction:{mode:donut?'nearest':'index',intersect:donut},plugins:{legend:{display:donut,position:'bottom',labels:{color:'#594c67',usePointStyle:true,pointStyle:'circle',boxWidth:7,boxHeight:7,padding:14,font:{size:11}}},tooltip:{...tooltipStyle,callbacks:{label:context=>{const value=values[context.dataIndex];return value===null?'Sem dados':`${/R\$|reais/.test(title)?new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL',maximumFractionDigits:2}).format(value??0):value?.toLocaleString('pt-BR')}${countTotal?` (${((value??0)/countTotal*100).toLocaleString('pt-BR',{maximumFractionDigits:1})}%)`:''}`;},afterLabel:context=>{if(kind!=='line')return '';const current=values[context.dataIndex],previous=values[context.dataIndex-1];return current!==null&&current!==undefined&&previous!==null&&previous!==undefined&&previous>0?`Variação mensal: ${((current/previous-1)*100).toLocaleString('pt-BR',{maximumFractionDigits:1,signDisplay:'exceptZero'})}%`:'';}}}},scales:donut?{}:horizontal?{x:{beginAtZero:true,border:{display:false},grid:{display:countTotal===undefined,color:'#6650800b',drawTicks:false},ticks:{color:'#a196aa',padding:8,maxTicksLimit:4,font:{size:10},callback:compact,...(countTotal!==undefined?{precision:0}:{})}},y:{border:{display:false},grid:{display:false,drawTicks:false},ticks:{autoSkip:false,color:'#4b3c60',font:{size:12}}}}:{x:{border:{display:false},grid:{display:false,drawTicks:false},ticks:{color:'#8d8499',font:{size:11},padding:10}},y:{border:{display:false},grid:{color:'#6650800b',drawTicks:false},ticks:{color:'#8d8499',padding:8,maxTicksLimit:5,font:{size:10},callback:compact}}}}
  });
  return ()=>chart.destroy();
 });
</script>
<div class="chart" style:height={height?`${height}px`:undefined}><canvas bind:this={canvas} aria-label={title}>{title}</canvas></div>
<details><summary>Ver valores do gráfico</summary><div class="chart-values">{#each labels as label,i}<span>{label}: {values[i]?.toLocaleString('pt-BR')??'Sem dados'}{#if countTotal} ({((values[i]??0)/countTotal*100).toLocaleString('pt-BR',{maximumFractionDigits:1})}%){/if}</span>{/each}</div></details>

<style>
.chart-values{gap:8px}.chart-values span{display:block;background:#f7f4fb;border:1px solid #eee7f5;border-radius:6px;padding:6px 8px;color:#675773;line-height:1.5}details{border-top:1px solid #f2edf7;margin:5px 18px 0;padding:10px 0!important;color:#79628e!important;font-size:11px!important}summary{width:fit-content}summary:hover{color:#7546b8}summary:focus-visible{outline:2px solid #8559ee;outline-offset:4px}
</style>
