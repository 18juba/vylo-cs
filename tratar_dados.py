"""Python 3.10+, sem dependências. Uso: python tratar_dados.py

Entrada: dados/; saída: dados_tratados/, ao lado deste script.
Opcional: --entrada PASTA --saida PASTA --corrigir-sinais-pedidos
Datas completas: DD/MM/AAAA. Mês de referência: AAAA-MM.
Decimais de saída: ponto, sem símbolo de moeda ou separador de milhar.
"""
import argparse
import csv
import io
import re
import unicodedata
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path


def normalizar(texto):
    texto = unicodedata.normalize('NFKD', texto.strip().casefold())
    return ' '.join(''.join(c for c in texto if not unicodedata.combining(c)).split())


def numero(texto):
    texto = texto.replace('R$', '').replace('\u00a0', '').replace(' ', '').strip()
    if not texto:
        return None
    if ',' in texto:
        if not re.fullmatch(r'[+-]?(?:\d+|\d{1,3}(?:\.\d{3})+),\d+', texto):
            raise ValueError(f'Número inválido: {texto}')
        texto = texto.replace('.', '').replace(',', '.')
    try:
        valor = Decimal(texto)
        if not valor.is_finite():
            raise InvalidOperation
        return valor
    except InvalidOperation as erro:
        raise ValueError(f'Número inválido: {texto}') from erro


def data(texto):
    if not texto:
        return ''
    # Meses em inglês são explícitos para não depender do idioma do computador.
    meses = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05',
             'Jun': '06', 'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10',
             'Nov': '11', 'Dec': '12'}
    for mes, digitos in meses.items():
        texto = re.sub(mes, digitos, texto, flags=re.IGNORECASE)
    # Anos de dois dígitos são interpretados explicitamente como 2000–2099.
    if re.fullmatch(r'\d{2}[/\-]\d{2}[/\-]\d{2}', texto):
        texto = texto[:-2] + '20' + texto[-2:]
    for formato in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y']:
        try:
            return datetime.strptime(texto, formato).strftime('%d/%m/%Y')
        except ValueError:
            pass
    raise ValueError(f'Data não reconhecida: {texto}')


def ler(caminho):
    bruto = caminho.read_bytes()
    try:
        texto = bruto.decode('utf-8-sig')
    except UnicodeDecodeError:
        texto = bruto.decode('cp1252')
    try:
        formato = csv.Sniffer().sniff(texto[:65536], delimiters=',;\t')
    except csv.Error:
        formato = csv.excel
    leitor = csv.DictReader(io.StringIO(texto, newline=''), dialect=formato, strict=True)
    campos = leitor.fieldnames
    if not campos or len(campos) != len(set(campos)):
        raise ValueError(f'{caminho.name}: cabeçalho ausente ou duplicado.')
    linhas = []
    for registro in leitor:
        if None in registro or None in registro.values():
            raise ValueError(f'{caminho.name}: estrutura inválida na linha {leitor.line_num}.')
        linhas.append((leitor.line_num, registro))
    return campos, linhas


def salvar(caminho, campos, linhas):
    with caminho.open('w', encoding='utf-8-sig', newline='') as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(linhas)


def tratar(entrada, saida, corrigir_sinais=False):
    if entrada.resolve() == saida.resolve():
        raise ValueError('Entrada e saída precisam ser pastas diferentes.')
    nomes = ['vendedores', 'vendas_mensais', 'atendimentos']
    bases = {nome: ler(entrada / f'{nome}.csv') for nome in nomes}
    resultados, log = {}, []

    def registrar(nome, linha, campo, antes, depois, motivo):
        log.append(dict(arquivo=nome, linha_original=linha, campo=campo,
                        antes=antes, depois=depois, motivo=motivo))

    for nome, (campos, linhas) in bases.items():
        saidas, vistos = [], set()
        for linha, original in linhas:
            if nome == 'vendas_mensais':
                assinatura = tuple(original.values())
                if assinatura in vistos:
                    registrar(nome, linha, '*', str(original), '', 'duplicata_exata_removida')
                    continue
                vistos.add(assinatura)
            r = {c: ' '.join(v.split()) for c, v in original.items()}
            for c in campos:
                if r[c] != original[c]:
                    registrar(nome, linha, c, original[c], r[c], 'espacos_removidos')
            if nome == 'vendedores' and r['seller_id'] in {'S024', 'S008'} and r['nome_loja'].isupper():
                alternativas = [outro for _, outro in linhas if outro['seller_id'].strip() == r['seller_id'] and not outro['nome_loja'].strip().isupper()]
                if len(alternativas) != 1:
                    raise ValueError(f'Não foi possível escolher cadastro único para {r["seller_id"]}.')
                registrar(nome, linha, '*', str(original), '', 'cadastro_maiusculo_removido_por_regra_do_usuario')
                continue
            pendencias = []
            for c in campos:
                if c in {'data', 'data_entrada', 'data_cancelamento'}:
                    try:
                        r[c] = data(r[c])
                    except ValueError:
                        pendencias.append(f'data_invalida:{c}')
                if c in {'faturamento', 'pedidos', 'ticket_medio', 'anuncios_ativos',
                         'taxa_reclamacao_pct', 'tempo_resposta_h', 'nota_satisfacao'}:
                    try:
                        n = numero(r[c])
                        r[c] = format(n, 'f') if n is not None else ''
                        if n is not None and (n < 0 or (c in {'pedidos', 'anuncios_ativos', 'nota_satisfacao'} and n != n.to_integral_value())):
                            pendencias.append(f'valor_invalido:{c}')
                    except ValueError:
                        pendencias.append(f'numero_invalido:{c}')
            if nome == 'vendedores':
                mapa = {'ml': 'Mercado Livre', 'mercado livre': 'Mercado Livre',
                        'amazon': 'Amazon', 'shopee': 'Shopee', 'magalu': 'Magalu', 'magazine luiza': 'Magalu'}
                r['marketplace'] = mapa.get(normalizar(r['marketplace']), r['marketplace'])
            if nome == 'atendimentos':
                mapa = {'sim': 'Sim', 's': 'Sim', 'nao': 'Não', 'n': 'Não'}
                r['resolvido'] = mapa.get(normalizar(r['resolvido']), r['resolvido'])
                if r['resolvido'] not in {'Sim', 'Não'}:
                    pendencias.append('resolvido_desconhecido')
            if nome == 'vendas_mensais':
                try:
                    f, p, t = (numero(r[c]) for c in ['faturamento', 'pedidos', 'ticket_medio'])
                    # Correção específica validada pelo usuário; não generalizar a outliers.
                    if r['seller_id'] == 'S041' and r['mes'] == '2026-07' and f == Decimal('23520674'):
                        antes = r['faturamento']
                        f = Decimal('235206.74')
                        r['faturamento'] = format(f, 'f')
                        registrar(nome, linha, 'faturamento', antes, r['faturamento'],
                                  'separador_decimal_corrigido_s041_julho_2026_validado_pelo_usuario')
                    if p is not None and p < 0 and p == p.to_integral_value():
                        compativel = f is not None and f >= 0 and t is not None and t > 0 and abs(f / abs(p) - t) <= Decimal('0.005')
                        if corrigir_sinais and compativel:
                            antes = r['pedidos']
                            p = abs(p)
                            r['pedidos'] = format(p, 'f')
                            pendencias.remove('valor_invalido:pedidos')
                            registrar(nome, linha, 'pedidos', antes, r['pedidos'], 'sinal_corrigido_por_opcao_e_compatibilidade_ticket')
                        else:
                            pendencias.append('pedidos_negativos_compativeis_com_erro_de_sinal' if compativel else 'pedidos_negativos_investigar')
                    if f is not None and f >= 0 and p is not None and p > 0 and p == p.to_integral_value() and t is not None:
                        if abs(f / p - t) > Decimal('0.005'):
                            pendencias.append('faturamento_ticket_pedidos_incompativeis')
                        if t > 0 and abs((f / 100) / p - t) <= Decimal('0.005') and abs(f / p - t) > Decimal('0.005'):
                            pendencias.append('possivel_faturamento_100_vezes_maior')
                    if not r['ticket_medio'] and f is not None and f >= 0 and p is not None and p > 0 and p == p.to_integral_value() and not pendencias:
                        r['ticket_medio'] = format((f / p).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), 'f')
                        registrar(nome, linha, 'ticket_medio', '', r['ticket_medio'], 'calculado_faturamento_dividido_por_pedidos')
                except ValueError:
                    pass  # Erros de conversão já sinalizados acima.
            for c in campos:
                if r[c] != original[c] and not any(x['arquivo'] == nome and x['linha_original'] == linha and x['campo'] == c for x in log):
                    registrar(nome, linha, c, original[c], r[c], 'padronizacao')
            r['pendencias_tratamento'] = ';'.join(pendencias)
            for pendencia in pendencias:
                registrar(nome, linha, '*', str(original), '', 'PENDENTE:' + pendencia)
            saidas.append(r)
        resultados[nome] = saidas

    ids = [r['seller_id'] for r in resultados['vendedores']]
    if len(ids) != len(set(ids)):
        raise ValueError('Ainda existem sellers repetidos após as regras de deduplicação.')
    cadastro = set(ids)
    for r in resultados['atendimentos']:
        r['cadastro_nao_encontrado'] = 'Sim' if r['seller_id'] not in cadastro else 'Não'
    saida.mkdir(parents=True, exist_ok=True)
    for nome in nomes:
        campos = bases[nome][0] + ['pendencias_tratamento']
        if nome == 'atendimentos':
            campos.append('cadastro_nao_encontrado')
        salvar(saida / f'{nome}.csv', campos, resultados[nome])
        print(f'{nome}: {len(bases[nome][1])} registros -> {len(resultados[nome])}; '
              f'{sum(bool(r["pendencias_tratamento"]) for r in resultados[nome])} com pendências')
    salvar(saida / 'log_tratamento.csv', ['arquivo', 'linha_original', 'campo', 'antes', 'depois', 'motivo'], log)
    print('Atendimentos sem cadastro:', sum(r['cadastro_nao_encontrado'] == 'Sim' for r in resultados['atendimentos']))
    print('Ações:', dict(Counter(r['motivo'] for r in log)))
    print(f'Saída: {saida.resolve()}\nOriginais preservados. Pendências são mantidas e sinalizadas, não corrigidas por suposição.')


if __name__ == '__main__':
    raiz = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entrada', type=Path, default=raiz / 'dados')
    parser.add_argument('--saida', type=Path, default=raiz / 'dados_tratados')
    parser.add_argument('--corrigir-sinais-pedidos', action='store_true', help='Converte negativos em positivos apenas quando faturamento/ticket confirma o valor absoluto, com tolerância de 0,005 no ticket.')
    args = parser.parse_args()
    try:
        tratar(args.entrada, args.saida, args.corrigir_sinais_pedidos)
    except (OSError, ValueError, KeyError, csv.Error) as erro:
        parser.exit(1, f'Falha: {erro}\n')
