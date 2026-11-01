# -*- coding: utf-8 -*-
"""
Gera as bases de apoio de HIV (3a fonte) a partir do Boletim Epidemiologico
HIV e Aids 2025 (Departamento de HIV/Aids/TB/Hepatites Virais e IST - SVSA/MS)
e da populacao estimada do IBGE.

Fontes (consulta feita em 01/11/2026):
- Boletim Epidemiologico HIV e Aids 2025 - Numero Especial (dez/2025), dados
  Sinan + Siscel/Siclom atualizados em 30/09/2025 (preliminares nos ultimos anos):
    https://www.gov.br/aids/pt-br/central-de-conteudo/boletins-epidemiologicos/2025/boletim_hiv_aids_2025.pdf
    * Tabela 1: casos de HIV notificados/registrados por UF de residencia, 1991-2025
    * Tabela 2: taxa de deteccao (por 100 mil hab.) de HIV por UF, 2014-2024
    * Tabela 8: casos de HIV (13+ anos) por categoria de exposicao hierarquizada,
      sexo e ano de diagnostico, 2007-2025
- IBGE SIDRA tabela 6579 (populacao estimada por UF, 2024)  https://apisidra.ibge.gov.br

Por que o Boletim (PDF transcrito) e nao o TABNET: o TABNET do Dathi publica
aberta apenas a serie de CASOS DE AIDS; casos de HIV detectados por populacao
nao existem como TABNET/CSV aberto - a fonte oficial consolidada e o Boletim.
A transcricao e feita por este script, de forma reprodutivel e com validacoes.
"""
import csv
import json
import re
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "dados" / "hiv"
DESTINO.mkdir(parents=True, exist_ok=True)

URL_BOLETIM = ("https://www.gov.br/aids/pt-br/central-de-conteudo/"
               "boletins-epidemiologicos/2025/boletim_hiv_aids_2025.pdf"
               "/@@display-file/file")
PDF = DESTINO / "boletim_hiv_aids_2025.pdf"

COL_TAB1 = ["1991-2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020",
            "2021", "2022", "2023", "2024", "2025", "total"]
COL_TAB2 = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021",
            "2022", "2023", "2024"]

SIGLA_POR_NOME = {
    "Rondônia": "RO", "Acre": "AC", "Amazonas": "AM", "Roraima": "RR",
    "Pará": "PA", "Amapá": "AP", "Tocantins": "TO", "Maranhão": "MA",
    "Piauí": "PI", "Ceará": "CE", "Rio Grande do Norte": "RN",
    "Paraíba": "PB", "Pernambuco": "PE", "Alagoas": "AL", "Sergipe": "SE",
    "Bahia": "BA", "Minas Gerais": "MG", "Espírito Santo": "ES",
    "Rio de Janeiro": "RJ", "São Paulo": "SP", "Paraná": "PR",
    "Santa Catarina": "SC", "Rio Grande do Sul": "RS",
    "Mato Grosso do Sul": "MS", "Mato Grosso": "MT", "Goiás": "GO",
    "Distrito Federal": "DF",
}
NOME_POR_SIGLA = {s: n for n, s in SIGLA_POR_NOME.items()}
REGIOES = ["Brasil", "Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]


def baixa_boletim():
    if PDF.exists() and PDF.stat().st_size > 1_000_000:
        return
    req = urllib.request.Request(URL_BOLETIM, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=300) as r:
        PDF.write_bytes(r.read())
    print(f"OK  {PDF} ({PDF.stat().st_size} bytes)")


def texto_da_tabela(marcador: str) -> str:
    from pypdf import PdfReader
    r = PdfReader(str(PDF))
    for p in r.pages:
        t = p.extract_text() or ""
        if marcador in t:
            return t
    raise RuntimeError(f"marcador nao encontrado: {marcador}")


def tokens_da_linha(linha: str, rotulo: str) -> list[str]:
    """Numeros (N e %) da linha apos remover o rotulo da categoria."""
    corpo = linha[len(rotulo):] if rotulo and linha.startswith(rotulo) else linha
    corpo = re.sub(r"^[^0-9]+", "", corpo)   # rotulo pode vir colado ao 1o numero
    return re.findall(r"\d+(?:,\d+)?", corpo)


def numeros_de_secao(texto: str, rotulo: str) -> list[int]:
    """Valores N das 14 colunas da Tabela 8 (rotulo pode quebrar de linha)."""
    nums: list[str] = []
    coletando = False
    for ln in texto.splitlines():
        ln = ln.strip()
        if not coletando:
            if ln.startswith(rotulo):
                coletando = True
                nums = tokens_da_linha(ln, rotulo)
        elif len(nums) < 28:
            nums += tokens_da_linha(ln, "")
        if len(nums) >= 28:                    # 14 colunas x (N + %)
            break
    if len(nums) < 28:
        raise RuntimeError(f"{rotulo}: so {len(nums)} tokens")
    return [int(float(v.replace(".", "").replace(",", "."))) for v in nums[:28:2]]


def parse_tabela8() -> list[list]:
    t = texto_da_tabela("TABELA 8")
    tm = re.search(r"Masculino(.*?)Feminino", t, re.S).group(1)
    tf = t.split("Feminino", 1)[1].replace("SexualHeterossexual", "Heterossexual")

    m = {rot: numeros_de_secao(tm, rot) for rot in
         ["Homossexual", "Bissexual", "Heterossexual", "Uso de drogas injetáveis",
          "Hemofílico", "Transfusão", "Acidente de trabalho",
          "Transmissão vertical", "Subtotal", "Ignorado", "Total"]}
    f = {rot: numeros_de_secao(tf, rot) for rot in
         ["Heterossexual", "Uso de drogas injetáveis", "Hemofílico",
          "Transfusão", "Acidente de trabalho", "Transmissão vertical",
          "Subtotal", "Ignorado", "Total"]}

    # validacoes conferidas no PDF (pag. 47, totais por sexo)
    assert m["Total"][5] == 29196 and m["Total"][11] == 28689, m["Total"]
    assert f["Total"][5] == 10606 and f["Total"][11] == 10198, f["Total"]
    assert m["Heterossexual"][11] == 6325 and f["Heterossexual"][11] == 7099

    i0 = COL_TAB1.index("2018")
    linhas = []
    for rot in ["Homossexual", "Bissexual"]:          # categorias so de homens
        linhas.append([rot] + m[rot][i0:i0 + 8] + [m[rot][13]])
    for rot in ["Heterossexual", "Uso de drogas injetáveis",
                "Transmissão vertical", "Ignorado"]:  # M + F
        soma = [a + b for a, b in zip(m[rot], f[rot])]
        linhas.append([rot] + soma[i0:i0 + 8] + [soma[13]])
    sang = ["Hemofílico", "Transfusão", "Acidente de trabalho"]
    soma = [a + b for a, b in
            zip([sum(x) for x in zip(*(m[r] for r in sang))],
                [sum(x) for x in zip(*(f[r] for r in sang))])]
    linhas.append(["Outras (hemofil./transfusão/acidente)"]
                  + soma[i0:i0 + 8] + [soma[13]])
    tot = [a + b for a, b in zip(m["Total"], f["Total"])]
    linhas.append(["Total (13+ anos)"] + tot[i0:i0 + 8] + [tot[13]])
    return linhas


def parse_tabela_uf(marcador: str, colunas: list[str]) -> list[list]:
    t = texto_da_tabela(marcador)
    rotulos = sorted(list(SIGLA_POR_NOME) + REGIOES, key=len, reverse=True)
    saida = {}
    for ln in t.splitlines():
        ln = ln.strip()
        for rot in rotulos:
            if ln.startswith(rot) and rot not in saida:
                nums = re.findall(r"\d+(?:,\d+)?", ln[len(rot):])
                if len(nums) >= len(colunas):
                    saida[rot] = nums[:len(colunas)]
                break
    if len(saida) < len(SIGLA_POR_NOME) + len(REGIOES):
        raise RuntimeError(f"{marcador}: apenas {len(saida)} linhas parseadas")
    ordem = REGIOES + list(SIGLA_POR_NOME)
    return [[rot] + saida[rot] for rot in ordem]


def le(nome):
    with open(DESTINO / nome, encoding="utf-8-sig") as f:
        return list(csv.reader(f, delimiter=";"))


def baixa_pop_ibge() -> list[list[str]]:
    existente = DESTINO / "pop_uf_ibge_2024.csv"
    if existente.exists():                      # ja baixada em 31/10/2026
        return [[r[0], int(r[1])] for r in le("pop_uf_ibge_2024.csv")[1:]]
    url = "https://apisidra.ibge.gov.br/values/t/6579/n3/all/v/9324/p/2024?formato=json"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=120) as r:
        j = json.load(r)
    cab = j[0]
    assert "Unidade da Federação" in cab.values(), cab
    return [[r["D1N"], int(r["V"])] for r in j[1:] if r["V"] != "..."]


def salva_csv(nome: str, linhas: list[list], cabecalho: str):
    caminho = DESTINO / nome
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(cabecalho.split(";"))
        w.writerows(linhas)
    print(f"OK  {caminho}  ({len(linhas)} linhas de dados)")


def main():
    baixa_boletim()

    # 1) casos de HIV por categoria (13+ anos, M+F) - Tabela 8
    cat = parse_tabela8()
    salva_csv("hiv_casos_categoria_2018_2025.csv", cat,
              "categoria_exposicao;2018;2019;2020;2021;2022;2023;2024;"
              "2025_preliminar;total")

    # 2) casos de HIV por UF de residencia - Tabela 1
    uf1 = parse_tabela_uf("TABELA 1", COL_TAB1)
    i0 = COL_TAB1.index("2018")
    linhas_uf = [[r[0]] + r[1 + i0:1 + i0 + 8] + [r[1 + 13]] for r in uf1]
    salva_csv("hiv_casos_uf_2018_2025.csv", linhas_uf,
              "uf_residencia;2018;2019;2020;2021;2022;2023;2024;"
              "2025_preliminar;total")

    # 3) taxa de deteccao de HIV por UF - Tabela 2
    uf2 = parse_tabela_uf("TABELA 2", COL_TAB2)
    salva_csv("hiv_taxa_deteccao_uf_2014_2024.csv", uf2,
              "uf_residencia;" + ";".join(COL_TAB2))

    # 4) populacao IBGE 2024 por UF
    pop = baixa_pop_ibge()
    salva_csv("pop_uf_ibge_2024.csv", pop, "uf;populacao_2024")

    # ---- taxas de apoio (PrEP por 100 mil x deteccao de HIV) --------------
    popuf = {n.upper(): v for n, v in pop}
    casos_uf = {r[0].upper(): [int(x) for x in r[1:]]
                for r in le("hiv_casos_uf_2018_2025.csv")[1:]}
    taxa_uf = {r[0].upper(): r[-1].replace(",", ".")
               for r in le("hiv_taxa_deteccao_uf_2014_2024.csv")[1:]}

    prep_por_uf = {}
    base = RAIZ / "dados" / "2025" / "Banco_PrEP_2025.csv"
    with open(base, encoding="utf-8-sig") as f:
        rd = csv.reader(f, delimiter=";")
        cab = next(rd)
        i_uf, i_cod = cab.index("UF_UDM"), cab.index("Cod_unificado")
        vistos = set()
        for r in rd:
            chave = (r[i_cod], r[i_uf])
            if chave not in vistos:
                vistos.add(chave)
                prep_por_uf[r[i_uf]] = prep_por_uf.get(r[i_uf], 0) + 1
    # 1 pessoa pode ter dispensacao em mais de uma UF; conta pares unicos (pessoa,UF)

    print("\nUF;Usuarios_Prep;Pop2024;Prep_por_100k;CasosHIV_2024;TaxaDetecaoHIV_2024")
    linhas_taxa = []
    for uf_sigla, n_prep in sorted(prep_por_uf.items(), key=lambda kv: -kv[1]):
        chave = NOME_POR_SIGLA.get(uf_sigla, uf_sigla).upper()
        pp = popuf.get(chave)
        if not pp:
            continue
        c24 = casos_uf.get(chave, [0] * 9)[6]      # coluna 2024
        tx = taxa_uf.get(chave, "")
        p100k = n_prep / pp * 100000
        linhas_taxa.append((uf_sigla, n_prep, pp, round(p100k, 1), c24, tx))
    with open(DESTINO / "taxa_prep_uf_100k.csv", "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["uf", "usuarios_prep", "populacao_2024", "prep_por_100k",
                    "casos_hiv_2024", "taxa_deteccao_hiv_2024"])
        w.writerows(linhas_taxa)
    print(f"OK  {DESTINO / 'taxa_prep_uf_100k.csv'}")

    ordem_prep = sorted(linhas_taxa, key=lambda l: -float(l[3]))
    ordem_hiv = sorted(linhas_taxa, key=lambda l: -float(l[5] or 0))
    print("\nTop 8 PrEP (usuarios por 100 mil hab):")
    for l in ordem_prep[:8]:
        print("  %-24s %8.1f" % (l[0], float(l[3])))
    print("\nTop 8 deteccao de HIV 2024 (por 100 mil hab):")
    for l in ordem_hiv[:8]:
        print("  %-24s %8s" % (l[0], l[5]))
    pb_prep = next((i + 1, l) for i, l in enumerate(ordem_prep) if l[0] == "PB")
    pb_hiv = next((i + 1, l) for i, l in enumerate(ordem_hiv) if l[0] == "PB")
    print(f"\nParaiba: PrEP {pb_prep[1][3]} por 100k (posicao {pb_prep[0]}/27); "
          f"deteccao HIV 2024 {pb_hiv[1][5]} por 100k (posicao {pb_hiv[0]}/27)")

    # participacao por categoria entre casos com categoria conhecida (13+)
    cat_dict = {r[0]: r[1:] for r in cat}
    i24 = 6
    conhecidos = ["Homossexual", "Bissexual", "Heterossexual",
                  "Uso de drogas injetáveis", "Transmissão vertical",
                  "Outras (hemofil./transfusão/acidente)"]
    tot24 = sum(int(cat_dict[r][i24]) for r in conhecidos)
    print(f"\n2024, entre casos de HIV 13+ com categoria conhecida ({tot24}):")
    for r in conhecidos:
        v = int(cat_dict[r][i24])
        print(f"  {r:<40} {v:>7}  {v / tot24 * 100:4.1f}%")


if __name__ == "__main__":
    sys.exit(main())
