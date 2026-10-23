import type { Plugin } from 'chart.js';

export function frequencyAccents(total?: number): Plugin {
 return {
  id:'frequencyAccents',
  afterDatasetsDraw(chart){
   if(total===undefined || !('type' in chart.config))return;
   const {ctx}=chart;
   ctx.save();
   if(chart.config.type==='doughnut'){
    const arc=chart.getDatasetMeta(0).data[0];
    if(arc){
     const active=chart.getActiveElements()[0];
     const value=active?Number(chart.data.datasets[0].data[active.index]):total;
     ctx.textAlign='center';ctx.textBaseline='middle';
     ctx.fillStyle='#49335f';ctx.font='600 22px system-ui';
     ctx.fillText(new Intl.NumberFormat('pt-BR',{notation:'compact',maximumFractionDigits:1}).format(value),arc.x,arc.y-5);
     ctx.fillStyle='#82718f';ctx.font='11px system-ui';
     ctx.fillText(active&&total?`${(value/total*100).toLocaleString('pt-BR',{maximumFractionDigits:1})}% do total`:'registros',arc.x,arc.y+17);
    }
   }else if(chart.config.type==='bar'){
    ctx.font='500 11px system-ui';ctx.fillStyle='#675773';ctx.textBaseline='middle';ctx.textAlign='left';
    chart.getDatasetMeta(0).data.forEach((bar,index)=>{
     const value=chart.data.datasets[0].data[index];
     if(typeof value==='number')ctx.fillText(value.toLocaleString('pt-BR'),bar.x+9,bar.y);
    });
   }
   ctx.restore();
  }
 };
}
