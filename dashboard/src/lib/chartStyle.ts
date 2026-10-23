import type { Chart, ChartType, Plugin, TooltipOptions } from 'chart.js';

export const tooltipStyle: Partial<TooltipOptions<ChartType>> = {
 backgroundColor: '#2c1b40', titleColor: '#f5eeff', bodyColor: '#e8ddf6',
 titleFont: { size: 12, weight: 600 }, bodyFont: { size: 12 },
 padding: 14, cornerRadius: 10, borderColor: '#9874c355', borderWidth: 1,
 titleMarginBottom: 9, bodySpacing: 7, displayColors: false,
 caretSize: 5, caretPadding: 9
};
export const hoverGuide: Plugin = {
 id: 'hoverGuide',
 afterDatasetsDraw(chart) {
  if (!('type' in chart.config) || chart.config.type !== 'line') return;
  const active = chart.getActiveElements();
  if (!active.length) return;
  const {ctx, chartArea} = chart;
  const x = active[0].element.x;
  ctx.save(); ctx.beginPath(); ctx.setLineDash([3, 5]);
  ctx.strokeStyle = '#9573c350'; ctx.lineWidth = 1;
  ctx.moveTo(x, chartArea.top); ctx.lineTo(x, chartArea.bottom); ctx.stroke(); ctx.restore();
 }
};
export function lineGradient(chart: Chart) {
 const area = chart.chartArea;
 if (!area) return '#8559ee12';
 const gradient = chart.ctx.createLinearGradient(0, area.top, 0, area.bottom);
 gradient.addColorStop(0, '#8559ee26'); gradient.addColorStop(1, '#8559ee00');
 return gradient;
}
