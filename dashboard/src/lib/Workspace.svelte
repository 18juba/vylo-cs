<script lang="ts">
	import Chart from '#lib/Chart.svelte';
	import PriorityMethod from '#lib/PriorityMethod.svelte';
	import Performance from '#lib/Performance.svelte';
	import Insights from '#lib/Insights.svelte';
	import Churn from '#lib/Churn.svelte';
	import { health, money, integer, num, type Row } from '#lib/data.js';
	import {
		Users,
		ShoppingBag,
		Wallet,
		ShieldAlert,
		ArrowUpRight,
		Search,
		SlidersHorizontal,
		ArrowDownRight,
		Database,
		ChevronRight
	} from '@lucide/svelte';
	let {
		data,
		mode = 'dashboard'
	}: {
		data: { sellers: Row[]; sales: Row[]; calls: Row[]; logs?: Row[]; logsAvailable?: boolean };
		mode?: string;
	} = $props();
	let month = $state('');
	let owner = $state('Todos');
	let query = $state('');
	let tab = $state('vendedores');
	let currentPage = $state(1);
	const months = $derived([...new Set(data.sales.map((r) => r.mes))].sort());
	const selected = $derived(
		mode === 'dashboard' ? months.at(-1) || '' : month || months.at(-1) || ''
	);
	const owners = $derived([...new Set(data.sellers.map((r) => r.responsavel_cs))].sort());
	const sellers = $derived(
		data.sellers.filter(
			(s) => mode === 'dashboard' || owner === 'Todos' || s.responsavel_cs === owner
		)
	);
	const ids = $derived(new Set(sellers.map((s) => s.seller_id)));
	const sales = $derived(data.sales.filter((r) => ids.has(r.seller_id)));
	const current = $derived(mode === 'dashboard' ? sales : sales.filter((r) => r.mes === selected));
	const active = $derived(
		sellers.filter((s) => {
			const d = s.data_cancelamento.split('/').reverse().join('-');
			const entry = s.data_entrada.split('/').reverse().join('-');
			return entry.slice(0, 7) <= selected && (!d || d.slice(0, 7) > selected);
		})
	);
	const ranked = $derived(
		active.map((s) => health(s, sales, data.calls, selected)).sort((a, b) => b.score - a.score)
	);
	const revenue = $derived(current.reduce((sum, r) => sum + (num(r.faturamento) ?? 0), 0));
	const orders = $derived(
		current.reduce((sum, r) => sum + ((num(r.pedidos) ?? 0) >= 0 ? (num(r.pedidos) ?? 0) : 0), 0)
	);
	const attention = $derived(ranked.filter((r) => r.score >= 20).length);
	const overview = $derived(
		sellers
			.map((s) => {
				const history = sales
					.filter((r) => r.seller_id === s.seller_id)
					.sort((a, b) => a.mes.localeCompare(b.mes));
				const snapshot = health(s, sales, data.calls, selected);
				const first = num(history[0]?.faturamento),
					last = num(history.at(-1)?.faturamento);
				const valid = history.map((r) => num(r.faturamento)).filter((n): n is number => n !== null);
				const cancelled =
					Boolean(s.data_cancelamento) &&
					s.data_cancelamento.split('/').reverse().join('-').slice(0, 7) <= selected;
				return {
					...snapshot,
					revenue: valid.length ? valid.reduce((a, b) => a + b, 0) : null,
					change:
						history.length >= 2 && first !== null && first > 0 && last !== null
							? ((last - first) / first) * 100
							: null,
					level: cancelled ? 'Cancelado' : snapshot.level
				};
			})
			.sort((a, b) => b.score - a.score)
	);
	const list = $derived(
		(mode === 'dashboard' ? overview : ranked).filter(
			(r) =>
				(mode !== 'risco' || r.score >= 20) &&
				`${r.seller.nome_loja} ${r.seller.seller_id}`.toLowerCase().includes(query.toLowerCase())
		)
	);
	const raw = $derived(
		tab === 'log_tratamento'
			? (data.logs ?? [])
			: tab === 'vendedores'
				? data.sellers
				: tab === 'vendas_mensais'
					? data.sales
					: data.calls
	);
	const logLabels: Record<string, string> = {
		arquivo: 'Arquivo',
		linha_original: 'Linha original',
		campo: 'Campo',
		antes: 'Antes',
		depois: 'Depois',
		motivo: 'Tratamento / motivo'
	};
	const columns = $derived(
		tab === 'log_tratamento' ? Object.keys(logLabels) : Object.keys(raw[0] ?? {})
	);
	const filtered = $derived(
		raw.filter((r) => Object.values(r).some((v) => v.toLowerCase().includes(query.toLowerCase())))
	);
	const totalPages = $derived(Math.max(1, Math.ceil(filtered.length / 15)));
	const safePage = $derived(Math.min(currentPage, totalPages));
	const labelMonth = (m: string) =>
		new Date(m + '-02T12:00:00').toLocaleDateString('pt-BR', { month: 'short', year: '2-digit' });
</script>

{#if mode === 'risco'}
	<div class="filters">
		<div class="filter-intro"><SlidersHorizontal size={16} /> Filtrar carteira</div>
		<label
			>Período <select bind:value={month}
				><option value="">{labelMonth(months.at(-1) || '2026-09')}</option
				>{#each months.slice(0, -1) as m}<option value={m}>{labelMonth(m)}</option>{/each}</select
			></label
		><label
			>Responsável CS <select bind:value={owner}
				><option>Todos</option>{#each owners as o}<option>{o}</option>{/each}</select
			></label
		><span class="filter-note">Referência: {labelMonth(selected)}</span>
	</div>
{/if}
{#if mode === 'dashboard'}
	<div class="charts-grid">
		<article class="panel">
			<div class="panel-heading">
				<div>
					<h2>Evolução do faturamento</h2>
				</div>
				<span class="legend-dot">Faturamento</span>
			</div>
			<Chart
				kind="line"
				title="Faturamento mensal em reais"
				labels={months.filter((m) => m <= selected).map(labelMonth)}
				values={months
					.filter((m) => m <= selected)
					.map((m) =>
						sales.filter((r) => r.mes === m).reduce((s, r) => s + (num(r.faturamento) ?? 0), 0)
					)}
			/>
		</article>
		<Churn {sellers} {months} />
	</div>
{/if}
{#if mode === 'dashboard'}<Performance {sellers} {sales} />{/if}
{#if mode === 'risco'}
	{#if mode === 'risco'}
		<PriorityMethod />{/if}
	<article class="panel table-panel">
		<div class="panel-heading">
			<h2>{mode === 'risco' ? 'Sellers prioritários' : 'Saúde dos sellers'}</h2>
			<label class="search"
				><Search size={17} /><input
					aria-label="Buscar seller"
					placeholder="Buscar seller ou ID..."
					bind:value={query}
				/></label
			>
		</div>
		<div class="table-scroll">
			<table>
				<thead
					><tr
						><th>SELLER</th><th>MARKETPLACE</th><th>FATURAMENTO</th><th>VARIAÇÃO¹</th><th
							>PRIORIDADE</th
						><th>{mode === 'risco' ? 'MOTIVOS' : 'RESPONSÁVEL CS'}</th></tr
					></thead
				><tbody
					>{#each list as item}<tr
							><td
								><div class="seller-cell">
									<div>
										<strong>{item.seller.nome_loja}</strong><small>{item.seller.seller_id}</small>
									</div>
								</div></td
							><td>{item.seller.marketplace}</td><td class="tabular"
								>{item.revenue === null ? 'Sem dados' : money(item.revenue)}</td
							><td
								><span
									class:negative={(item.change ?? 0) < 0}
									class:positive={(item.change ?? 0) >= 0 && item.change !== null}
									>{#if item.change !== null}{#if item.change < 0}<ArrowDownRight
												size={14}
											/>{:else}<ArrowUpRight size={14} />{/if}{Math.abs(item.change).toFixed(
											1
										)}%{:else}—{/if}</span
								></td
							><td
								><span
									class="badge"
									class:high={item.level === 'Alta'}
									class:moderate={item.level === 'Moderada'}
									class:low={item.level === 'Baixa'}>{item.level}</span
								></td
							><td>{mode === 'risco' ? item.reasons.join(' · ') : item.seller.responsavel_cs}</td
							></tr
						>{:else}<tr
							><td colspan="6" class="empty">Nenhum seller encontrado para esta seleção.</td></tr
						>{/each}</tbody
				>
			</table>
		</div>
		<div class="table-footer">
			<span
				>¹ Comparação com o último mês anterior disponível. {list.length} sellers encontrados.</span
			>
		</div>
	</article>
{:else if mode === 'dados'}
	<article class="panel">
		<div class="data-tabs">
			{#each ['vendedores', 'vendas_mensais', 'atendimentos', 'log_tratamento'] as name}<button
					class:chosen={tab === name}
					onclick={() => {
						tab = name;
						currentPage = 1;
						query = '';
					}}>{name === 'log_tratamento' ? 'Log de tratamento' : name.replace('_', ' ')}</button
				>{/each}
		</div>
		<div class="panel-heading">
			<div>
				<h2>{tab === 'log_tratamento' ? 'Log de tratamento' : tab + '.csv'}</h2>
				{#if tab === 'log_tratamento'}<p>
						Rastreie o arquivo, a linha original, o valor antes e depois e o motivo da alteração
					</p>{/if}
				<p>{filtered.length} registros encontrados de {raw.length}</p>
			</div>
			<label class="search"
				><Search size={17} /><input
					aria-label="Buscar nos registros"
					placeholder="Buscar em todas as colunas..."
					bind:value={query}
					oninput={() => (currentPage = 1)}
				/></label
			><a
				class="button secondary"
				aria-disabled={tab === 'log_tratamento' && !data.logsAvailable}
				href={'/dados/' + tab + '.csv'}
				download>Baixar CSV <ArrowUpRight size={15} /></a
			>
		</div>
		<div class="table-scroll">
			<table class:log-table={tab === 'log_tratamento'}>
				<thead
					><tr
						>{#each columns as key}<th scope="col"
								>{tab === 'log_tratamento' ? logLabels[key] : key}</th
							>{/each}</tr
					></thead
				><tbody
					>{#each filtered.slice((safePage - 1) * 15, safePage * 15) as row}<tr
							>{#each columns as key}<td>{row[key] || '—'}</td>{/each}</tr
						>{:else}<tr
							><td colspan={columns.length || 1} class="empty"
								>{tab === 'log_tratamento' && !data.logsAvailable
									? 'Log indisponível. Adicione log_tratamento.csv em static/dados.'
									: 'Nenhum registro encontrado.'}</td
							></tr
						>{/each}</tbody
				>
			</table>
		</div>
		<div class="pagination">
			<button disabled={safePage === 1} onclick={() => (currentPage = safePage - 1)}
				>Anterior</button
			><span>Página {safePage} de {totalPages}</span><button
				disabled={safePage === totalPages}
				onclick={() => (currentPage = safePage + 1)}>Próxima</button
			>
		</div>
	</article>
{:else if mode === 'relatorios'}
	<Insights {data} />
{/if}

<style>
	.log-table td {
		white-space: pre-wrap;
		overflow-wrap: anywhere;
		min-width: 120px;
		max-width: 340px;
		vertical-align: top;
	}
	.log-table th {
		white-space: nowrap;
	}
	.data-tabs {
		flex-wrap: wrap;
	}
	.button[aria-disabled='true'] {
		pointer-events: none;
		opacity: 0.5;
	}
</style>
