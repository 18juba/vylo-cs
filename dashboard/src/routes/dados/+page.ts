import { error } from '@sveltejs/kit';
import { parseCSV } from '#lib/data.js';

export const load = async ({ fetch }) => {
 const response = await fetch('/dados/log_tratamento.csv');
 if (response.status === 404) return { logs: [], logsAvailable: false };
 if (!response.ok) error(500, 'Não foi possível carregar o log de tratamento.');
 const logs = parseCSV(await response.text());
 const expected = ['arquivo', 'linha_original', 'campo', 'antes', 'depois', 'motivo'];
 if (logs.length && expected.some(column => !(column in logs[0]))) {
  error(500, 'O log de tratamento não contém as colunas esperadas.');
 }
 return { logs, logsAvailable: true };
};
