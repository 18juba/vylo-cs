import type { Row } from '#lib/data.js';

// Datas tratadas: DD/MM/AAAA. Comparações ISO não dependem do fuso horário.
export function monthlyChurn(sellers: Row[], months: string[]) {
 const dates = sellers.map(s => ({
  entry: s.data_entrada.split('/').reverse().join('-'),
  cancellation: s.data_cancelamento.split('/').reverse().join('-')
 }));
 return months.map(month => {
  const start = `${month}-01`;
  const initial = dates.filter(s => s.entry && s.entry < start && (!s.cancellation || s.cancellation >= start));
  const cancellations = initial.filter(s => s.cancellation.startsWith(month)).length;
  return { month, initial: initial.length, cancellations, rate: initial.length ? cancellations / initial.length * 100 : null };
 });
}
