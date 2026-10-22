# Vylo CS

Análise da saúde dos sellers para apoiar o time de Customer Success na identificação de clientes que precisam de atenção.

## Fluxo dos dados

```text
Dados originais → Análise exploratória → Tratamento → Dados limpos → Dashboard
dados/           analise_exploratoria.py tratar_dados.py dados_tratados/ dashboard/
```

1. **Originais:** os arquivos `vendedores.csv`, `vendas_mensais.csv` e `atendimentos.csv` ficam em `dados/`.
2. **Análise exploratória:** identifica ausências, duplicidades, formatos e categorias inconsistentes, imprimindo o diagnóstico no terminal.
3. **Tratamento:** padroniza datas, textos, marketplaces e números; remove duplicatas conforme as regras definidas e calcula tickets médios ausentes quando possível.
4. **Dados limpos:** os CSVs são gerados em `dados_tratados/`, com pendências sinalizadas e alterações registradas em `log_tratamento.csv`. Os originais são preservados.
5. **Dashboard:** os três CSVs tratados e `log_tratamento.csv` são copiados para `dashboard/static/dados/`, alimentando gráficos, tabelas, insights e priorização de sellers.

## Dashboard

Construído com **SvelteKit, Tailwind CSS, Chart.js e Lucide**.

- **Dashboard:** desempenho histórico por marketplace e plano, além de churn mensal.
- **Dados:** consulta aos três CSVs tratados e ao log de alterações (antes, depois e motivo).
- **Relatórios:** insights e proposta de acompanhamento proativo.
- **Sellers em risco:** prioridade por sinais de vendas e atendimento, com regras explicadas na tela.

O churn é calculado pelas datas de entrada e cancelamento. A prioridade de atendimento é um indicador baseado em regras, não uma probabilidade validada de cancelamento.
