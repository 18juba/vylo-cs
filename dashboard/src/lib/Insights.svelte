<script lang="ts">
	import type { Row } from '#lib/data.js';
	import { buildInsights } from '#lib/insights.js';
	import Improvement from '#lib/Improvement.svelte';
	let { data }: { data: { sellers: Row[]; sales: Row[]; calls: Row[] } } = $props();
	const report = $derived(buildInsights(data.sellers, data.sales, data.calls));
	const summaries = [
		{
			title: 'Cancelamentos em aceleração',
			why: 'A perda recente de clientes exige antecipar as ações de retenção.',
			action:
				'Revisar motivos de saída e acompanhar semanalmente as ações para contas em deterioração.'
		},
		{
			title: 'Atenção ao plano Essencial',
			why: 'O plano concentra mais da metade dos cancelamentos da carteira.',
			action:
				'Revisar onboarding e adoção. Testar uma cadência de CS com sellers de tempo de carteira semelhante.'
		},
		{
			title: 'Respostas mais lentas antes da saída',
			why: 'A diferença de tempo de resposta pede uma revisão das filas e dos casos complexos.',
			action:
				'Definir metas por gravidade, revisar atendimentos demorados e acompanhar pendências até a resolução.'
		}
	];
</script>

<section class="insights-intro">
	<h1>Insights e ações recomendadas</h1>
	<p>{report.period} · {data.sellers.length} sellers analisados</p>
</section>
<div class="insights-list">
	{#each report.cards as card, index}<article class="panel insight-card">
			<header>
				<span class="insight-number">0{index + 1}</span>
				<h2>{summaries[index].title}</h2>
			</header>
			<strong class="insight-metric">{card.metric}</strong>
			<p class="insight-evidence">{card.evidence}</p>
			<section class="insight-why">
				<h3>Por que importa</h3>
				<p>{summaries[index].why}</p>
			</section>
			<section class="insight-action">
				<h3>Ação recomendada</h3>
				<p>{summaries[index].action}</p>
			</section>
			<details>
				<summary>Evidências e limites</summary>
				<div class="table-scroll">
					<table>
						<caption>Detalhamento do insight {index + 1}</caption><thead
							><tr
								><th scope="col">GRUPO / PERÍODO</th><th scope="col">BASE</th><th scope="col"
									>RESULTADO</th
								></tr
							></thead
						><tbody
							>{#each card.rows as row}<tr
									><th scope="row">{row.grupo}</th><td>{row.base}</td><td>{row.resultado}</td></tr
								>{/each}</tbody
						>
					</table>
				</div>
				<p class="insight-limit">{card.limit}</p>
			</details>
		</article>{/each}
</div>
<Improvement />

<style>
	.insights-intro {
		margin-bottom: 20px;
	}
	.insights-intro h1 {
		font-size: 25px;
		margin: 0 0 6px;
	}
	.insights-intro p {
		font-size: 13px;
		color: #675773;
	}
	.insights-list {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 16px;
		align-items: stretch;
	}
	.insight-card {
		padding: 20px;
		min-width: 0;
		display: flex;
		flex-direction: column;
	}
	.insight-card header {
		display: flex;
		gap: 10px;
		align-items: center;
		margin-bottom: 16px;
	}
	.insight-number {
		border-radius: 7px;
		padding: 7px;
		background: #eee6fc;
		color: #7546b8;
		font-size: 13px;
	}
	.insight-card h2 {
		font-size: 16px;
		line-height: 1.4;
		margin: 0;
	}
	.insight-metric {
		display: block;
		font-size: 22px;
		line-height: 1.35;
		color: #7546b8;
		font-weight: 650;
	}
	.insight-evidence {
		font-size: 13px;
		line-height: 1.7;
		color: #4b405b;
		margin: 12px 0 16px;
	}
	.insight-card h3 {
		font-size: 12px;
		font-weight: 650;
		color: #40304f;
		margin: 0 0 5px;
	}
	.insight-card section p {
		font-size: 13px;
		line-height: 1.65;
		color: #594c67;
		margin: 0;
	}
	.insight-why {
		margin-bottom: 14px;
	}
	.insight-action {
		margin-top: auto;
		padding: 13px;
		background: #edfaf9;
		border-radius: 8px;
	}
	.insight-action small {
		display: block;
		font-size: 11px;
		color: #276c67;
		margin-top: 9px;
	}
	.insight-card details {
		padding: 14px 0 0;
		font-size: 12px;
		color: #67468f;
	}
	.insight-card summary {
		font-weight: 600;
	}
	.insight-card caption {
		text-align: left;
		padding: 12px 0;
		font-size: 12px;
		color: #675773;
	}
	.insight-card tbody th {
		background: white;
		font-size: 13px;
		letter-spacing: 0;
		color: #40364e;
		white-space: normal;
	}
	.insight-card td,
	.insight-card th {
		padding: 10px;
		font-size: 12px;
		min-width: 100px;
		white-space: normal;
	}
	.insight-limit {
		font-size: 12px;
		color: #675773;
		padding-top: 10px;
		line-height: 1.7;
	}
	@media (max-width: 1100px) {
		.insights-list {
			grid-template-columns: 1fr;
		}
		.insight-card {
			padding: 18px;
		}
		.insight-metric {
			font-size: 21px;
		}
	}
</style>
