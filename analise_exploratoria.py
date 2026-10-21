import csv
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

PASTA_DADOS = Path(__file__).resolve().parent / 'dados'
AUSENTES = {'', 'null', 'none', 'nan', 'n/a', 'na', '-', 'nao informado'}
CATEGORIAS = {'marketplace', 'segmento', 'plano', 'status', 'responsavel_cs',
              'canal', 'motivo', 'resolvido', 'reputacao'}
NUMEROS = {'faturamento', 'pedidos', 'ticket_medio', 'anuncios_ativos',
           'taxa_reclamacao_pct', 'tempo_resposta_h', 'nota_satisfacao'}
CHAVES = {'vendedores': ['seller_id'], 'vendas_mensais': ['seller_id', 'mes'],
          'atendimentos': ['atendimento_id']}


def normalizar(valor):
    texto = unicodedata.normalize('NFKD', valor.strip().casefold())
    return ' '.join(''.join(c for c in texto if not unicodedata.combining(c)).split())


def ausente(valor):
    return normalizar(valor) in AUSENTES


def analisar(caminho):
    print(f'\n{"=" * 65}\nARQUIVO: {caminho.name}\n{"=" * 65}')
    conteudo = caminho.read_bytes()
    try:
        texto = conteudo.decode('utf-8-sig')
    except UnicodeDecodeError:
        texto = conteudo.decode('cp1252')
        print('Codificação: cp1252 (não UTF-8).')
    import io
    try:
        formato = csv.Sniffer().sniff(texto[:65536], delimiters=',;\t|')
    except csv.Error:
        formato = csv.excel
    leitor = csv.reader(io.StringIO(texto, newline=''), formato, strict=True)
    colunas = next(leitor)
    if len(colunas) != len(set(colunas)):
        raise ValueError('Cabeçalhos duplicados; revise o arquivo antes de analisar.')
    linhas = []
    for valores in leitor:
        if len(valores) != len(colunas):
            print(f'  Estrutura inválida no registro terminado na linha {leitor.line_num}: '
                  f'{len(valores)} campos, esperados {len(colunas)}. Ignorado no perfil.')
            continue
        linhas.append(dict(zip(colunas, valores)))
    print(f'Registros analisados: {len(linhas)} | Colunas: {len(colunas)}')
    print('Colunas:', ', '.join(colunas))
    duplicatas = len(linhas) - len({tuple(r.values()) for r in linhas})
    print(f'Linhas duplicadas exatas (além da primeira): {duplicatas}')
    chaves = CHAVES.get(caminho.stem, [])
    if chaves and all(c in colunas for c in chaves):
        valores = [tuple(normalizar(r[c]) for c in chaves) for r in linhas
                   if all(not ausente(r[c]) for c in chaves)]
        print(f'Chaves repetidas {chaves} (além da primeira): {len(valores)-len(set(valores))}')
    for coluna in colunas:
        valores = [r[coluna] for r in linhas]
        preenchidos = [v for v in valores if not ausente(v)]
        print(f'\n  {coluna}: {len(valores)-len(preenchidos)} ausentes; '
              f'{len(set(preenchidos))} valores distintos preenchidos')
        espacos = sum(v != v.strip() or '  ' in v for v in preenchidos)
        if espacos:
            print(f'    Espaços extras: {espacos}')
        if coluna in CATEGORIAS:
            print('    Valores e frequências:', dict(Counter(valores)))
            grupos = defaultdict(Counter)
            for valor in preenchidos:
                chave = normalizar(valor)
                if coluna == 'marketplace' and chave == 'ml':
                    chave = 'mercado livre'
                grupos[chave][valor] += 1
            for chave, variantes in grupos.items():
                if len(variantes) > 1:
                    print(f'    Possível padronização [{chave}]: {dict(variantes)}')
        if coluna in NUMEROS:
            numeros, invalidos = [], Counter()
            for valor in preenchidos:
                try:
                    # Vírgula = decimal brasileiro; ponto isolado = decimal.
                    texto_num = valor.strip()
                    if ',' in texto_num:
                        texto_num = texto_num.replace('.', '').replace(',', '.')
                    numero = float(texto_num)
                    import math
                    if not math.isfinite(numero):
                        raise ValueError
                    numeros.append(numero)
                except ValueError:
                    invalidos[valor] += 1
            if numeros:
                print(f'    Mínimo: {min(numeros):.2f} | Média: {sum(numeros)/len(numeros):.2f} '
                      f'| Máximo: {max(numeros):.2f} | Negativos: {sum(n < 0 for n in numeros)}')
            if invalidos:
                print('    Números inválidos:', dict(invalidos))
        if coluna == 'mes' or coluna.startswith('data'):
            formatos, invalidos = Counter(), Counter()
            for valor in preenchidos:
                for formato_data in (['%Y-%m'] if coluna == 'mes' else ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']):
                    try:
                        datetime.strptime(valor.strip(), formato_data)
                        formatos[formato_data] += 1
                        break
                    except ValueError:
                        pass
                else:
                    invalidos[valor] += 1
            print('    Formatos de data:', dict(formatos))
            if len(formatos) > 1:
                print('    ATENÇÃO: formatos de data misturados.')
            if invalidos:
                print('    Datas inválidas:', dict(invalidos))
    return linhas


def main():
    pasta = Path(sys.argv[1]) if len(sys.argv) > 1 else PASTA_DADOS
    arquivos = sorted(pasta.glob('*.csv'))
    if not arquivos:
        print(f'Nenhum CSV encontrado em: {pasta}')
        return 1
    tabelas = {}
    falhas = 0
    for arquivo in arquivos:
        try:
            tabelas[arquivo.stem] = analisar(arquivo)
        except (OSError, UnicodeError, ValueError, csv.Error, StopIteration) as erro:
            print(f'Falha ao analisar {arquivo.name}: {erro}')
            falhas += 1
    if 'vendedores' in tabelas:
        cadastro = {normalizar(r['seller_id']) for r in tabelas['vendedores']
                    if 'seller_id' in r and not ausente(r['seller_id'])}
        print('\nVÍNCULOS ENTRE AS BASES')
        for nome in ['vendas_mensais', 'atendimentos']:
            if nome in tabelas:
                orfaos = Counter(r['seller_id'] for r in tabelas[nome]
                                 if 'seller_id' in r and not ausente(r['seller_id'])
                                 and normalizar(r['seller_id']) not in cadastro)
                print(f'  {nome}: sellers sem cadastro: {dict(orfaos)}')
    print('\nDiagnóstico concluído. Nenhum arquivo foi alterado.')
    return 1 if falhas else 0


if __name__ == '__main__':
    raise SystemExit(main())
