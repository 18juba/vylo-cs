<script lang="ts">
	import { onMount } from 'svelte';
	import Chart from 'chart.js/auto';
 import {tooltipStyle,hoverGuide,lineGradient} from '#lib/chartStyle.js';
	import type { Row } from '#lib/data.js';
	import { monthlyChurn } from '#lib/churn.js';
	let { sellers, months }: { sellers: Row[]; months: string[] } = $props();
	const rows = $derived(monthlyChurn(sellers, months));
	const monthLabel = (month: string) =>
		new Date(`${month}-02T12:00:00`).toLocaleDateString('pt-BR', {
			month: 'short',
			year: '2-digit'
		});
	const percentage = (value: number | null) =>
		value === null
			? 'Indisponível'
			: value.toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%';
	let canvas: HTMLCanvasElement;
	let ready = $state(false);
	onMount(() => {
		ready = true;
	});
	$effect(() => {
		if (!ready || !canvas) return;
		const points = rows;
		const chart = new Chart(canvas, {
			type: 'line',
 plugins: [hoverGuide],
			data: {
				labels: points.map((r) => monthLabel(r.month)),
				datasets: [
					{
						label: 'Churn mensal',
						data: points.map((r) => r.rate),
						borderColor: '#8559ee',
						backgroundColor: (context: {chart: Chart}) => lineGradient(context.chart),
						fill: true,
						tension: .35, cubicInterpolationMode: 'monotone', borderCapStyle: 'round', borderJoinStyle: 'round', pointHitRadius: 16, pointBackgroundColor: '#ffffff', pointBorderColor: '#8559ee', pointBorderWidth: 2, pointHoverBackgroundColor: '#8559ee', pointHoverBorderColor: '#ffffff', pointHoverBorderWidth: 3,
						pointRadius: 2,
						pointHoverRadius: 6,
						borderWidth: 3,
						spanGaps: false
					}
				]
			},
			options: {
				responsive: true, animation: {duration: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 350},
				maintainAspectRatio: false,
				interaction: { mode: 'index', intersect: false },
				plugins: {
					legend: { display: false },
					tooltip: { ...tooltipStyle,
						callbacks: {
							label: (context) => `Churn: ${percentage(points[context.dataIndex].rate)}`,
							afterLabel: (context) => {
								const r = points[context.dataIndex];
								const prev = points[context.dataIndex - 1];
 const lines = [`Cancelamentos: ${r.cancellations}`, `Carteira inicial: ${r.initial}`];
 if(r.rate !== null && prev?.rate !== null && prev?.rate !== undefined) lines.push(`Variação mensal: ${(r.rate-prev.rate).toLocaleString('pt-BR',{maximumFractionDigits:1,signDisplay:'exceptZero'})} p.p.`);
 return lines;
							}
						}
					}
				},
				scales: {
					x: { border:{display:false}, grid: { display: false, drawTicks:false }, ticks: { color: '#8d8499',font:{size:11},padding:10 } },
					y: {
						beginAtZero: true, border:{display:false},
						suggestedMax: 1,
						title: { display: false, text: 'Churn (%)' },
						ticks: {
							color: '#8d8499', font:{size:10}, maxTicksLimit:5, padding:8,
							callback: (value) => Number(value).toLocaleString('pt-BR') + '%'
						},
						grid: { color: '#6650800b', drawTicks:false }
					}
				}
			}
		});
		return () => chart.destroy();
	});
</script>

<article class="panel churn-panel">
	<div class="panel-heading">
		<div>
			<h2>Cancelamentos e churn mensal</h2>
		</div>
	</div>
	<div class="churn-chart">
		<canvas
			bind:this={canvas}
			aria-label="Evolução mensal do churn em porcentagem. Os valores completos estão na tabela em Ver detalhes."
			aria-describedby="churn-method"
			>Consulte a tabela em Ver detalhes para acessar os valores mensais.</canvas
		>
	</div>
	<details class="churn-details">
		<summary>Ver detalhes — tabela mensal de churn</summary>
		<!-- svelte-ignore a11y_no_noninteractive_tabindex (Região rolável precisa de foco para navegação horizontal pelo teclado.) -->
		<div class="table-scroll" role="region" aria-label="Tabela de churn mensal" tabindex="0">
			<table>
				<caption>Carteira inicial, cancelamentos e taxa de churn por mês</caption>
				<thead
					><tr
						><th scope="col">MÊS</th><th scope="col">CARTEIRA INICIAL</th><th scope="col"
							>CANCELAMENTOS</th
						><th scope="col">CHURN</th></tr
					></thead
				>
				<tbody
					>{#each rows as row}<tr
							><th scope="row">{monthLabel(row.month)}</th><td>{row.initial}</td><td
								>{row.cancellations}</td
							><td class="tabular">{percentage(row.rate)}</td></tr
						>{:else}<tr><td colspan="4">Sem meses disponíveis para análise.</td></tr>{/each}</tbody
				>
			</table>
		</div>
	</details>
</article>

<style>
	.churn-chart {
		height: 190px;
		padding: 8px 22px 10px;
	}
	.churn-details {
		padding: 10px 0 0 !important;
		font-size: 12px !important;
		color: #513b6c !important;
	}
	.churn-details summary {
		margin: 0 22px 14px;
		font-weight: 600;
		cursor: pointer;
	}
	.churn-details summary:focus-visible {
		outline: 2px solid #8559ee;
		outline-offset: 5px;
	}
	.churn-notes {
		padding: 12px 22px 18px;
		font-size: 12px;
		color: #675773;
		line-height: 1.7;
	}
	.churn-panel th,
	.churn-panel td {
		padding: 12px 14px;
	}
	.churn-panel th {
		white-space: normal;
		line-height: 1.5;
	}
	.churn-panel tbody th {
		background: white;
		font-size: 14px;
		letter-spacing: 0;
		font-weight: 500;
		color: #40364e;
	}
	.churn-panel td:last-child {
		min-width: 0;
	}
	caption {
		text-align: left;
		padding: 12px 14px;
		font-size: 12px;
		color: #675773;
	}
	@media (max-width: 700px) {
		.churn-chart {
			padding-inline: 12px;
		}
	}
</style>
