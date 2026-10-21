import { parseCSV } from '#lib/data.js';
import { error } from '@sveltejs/kit';
export const load = async ({ fetch }) => {
 const names=['vendedores','vendas_mensais','atendimentos'];
 const tables=await Promise.all(names.map(async name=>{const response=await fetch(`/dados/${name}.csv`);if(!response.ok)error(500,`Não foi possível carregar ${name}.`);return parseCSV(await response.text());}));
 return { sellers:tables[0],sales:tables[1],calls:tables[2] };
};
