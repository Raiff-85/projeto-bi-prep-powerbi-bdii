# -*- coding: utf-8 -*-
"""
Gera as bases de apoio de HIV/aids (3a fonte) a partir do TABNET oficial do
Departamento de HIV/Aids/TB/Hepatites/IST (MS) e do IBGE, e calcula as taxas
por 100 mil habitantes usadas nas novas perguntas de negocio.

Fontes (consulta feita em 31/10/2026):
- TABNET aids.gov.br  (Casos de aids identificados no Brasil, SINAN+SIM+SISCEL/SICLOM,
  dados consolidados ate 30/09/2025 - preliminares)   http://www2.aids.gov.br/cgi/tabcgi.exe?tabnet/br.def
- IBGE SIDRA tabela 6579 (populacao estimada por UF, 2024)  https://apisidra.ibge.gov.br
"""
import csv
import html
import io
import json
import re
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "dados" / "hiv"
DESTINO.mkdir(parents=True, exist_ok=True)

TABNET_BASE = "http://www2.aids.gov.br/cgi/tabcgi.exe?tabnet/br.def"
ANOS = list(range(2018, 2026))

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


def post_tabnet(linha: str) -> str:
    arquivos = "&".join(f"Arquivos=aids_{a % 100:02d}.dbf" for a in ANOS)
    dados = (
        f"Linha={urllib.request.quote(linha.encode('latin-1'))}"
        "&Coluna=Ano_Diagn%F3stico"
        "&Incremento=Freq%FC%EAncia"
        "&SAno_Diagn%F3stico=TODAS_AS_CATEGORIAS__"
        "&formato=prn&mostre=Mostra&" + arquivos
    )
    req = urllib.request.Request(
        TABNET_BASE,
        data=dados.encode("ascii"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        bruto = r.read().decode("latin-1")
    m = re.search(r"<PRE>(.*?)</PRE>", bruto, re.S)
    if not m:
        raise RuntimeError("bloco PRE nao encontrado na resposta do TABNET")
    return m.group(1)


def pre_para_csv(pre: str) -> list[list[str]]:
    linhas = []
    primeira = True
    for bruta in pre.strip().splitlines():
        bruta = bruta.strip()
        if bruta in ("", "&"):  # TABNET termina o bloco com um '&'
            continue
        campos = [html.unescape(c) for c in
                  next(csv.reader(io.StringIO(bruta), delimiter=";"))]
        if primeira:  # primeira linha do bloco = cabecalho proprio do TABNET
            primeira = False
            continue
        linhas.append(campos)
    return linhas


def salva_csv(nome: str, linhas: list[list[str]], cabecalho_extra: str):
    caminho = DESTINO / nome
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(cabecalho_extra.split(";"))
        w.writerows(linhas)
    print(f"OK  {caminho}  ({len(linhas)} linhas de dados)")
    return caminho


def baixa_pop_ibge() -> list[list[str]]:
    url = "https://apisidra.ibge.gov.br/values/t/6579/n3/all/v/9324/p/2024?formato=json"
    with urllib.request.urlopen(url, timeout=120) as r:
        j = json.load(r)
    cab = j[0]
    assert "Unidade da Federação" in cab.values(), cab
    linhas = [[r["D1N"], int(r["V"])] for r in j[1:] if r["V"] != "..."]
    return linhas


def main():
    # 1) casos por categoria de exposicao
    cat = pre_para_csv(post_tabnet("Categ_Exp_Hierar"))
    salva_csv("hiv_aids_casos_categoria_2018_2025.csv", cat,
              "categoria_exposicao;2018;2019;2020;2021;2022;2023;2024;2025;total")

    # 2) casos por UF de residencia
    uf = pre_para_csv(post_tabnet("UF_Residência"))
    salva_csv("hiv_aids_casos_uf_2018_2025.csv", uf,
              "uf_residencia;2018;2019;2020;2021;2022;2023;2024;2025;total")

    # 3) populacao IBGE 2024 por UF
    pop = baixa_pop_ibge()
    salva_csv("pop_uf_ibge_2024.csv", pop, "uf;populacao_2024")

    # ---- calculo das taxas por 100 mil habitantes -------------------------
    popuf = {n.upper(): v for n, v in pop}

    def le(nome):
        with open(DESTINO / nome, encoding="utf-8-sig") as f:
            return list(csv.reader(f, delimiter=";"))

    casos_uf = {r[0].upper(): [int(x) for x in r[1:]] for r in le("hiv_aids_casos_uf_2018_2025.csv")[1:]}

    # usuarios unicos de PrEP por UF (UF da ultima dispensacao)
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
    # codigo unico por pessoa pode aparecer em mais de uma UF de servico;
    # contagem por (pessoa, UF) e aproximate para "usuarios por UF de atendimento"

    print("\nUF;Usuarios_Prep;Pop2024;Prep_por_100k;CasosAids_2024;Aids_por_100k")
    linhas_taxa = []
    for uf_sigla, n_prep in sorted(prep_por_uf.items(), key=lambda kv: -kv[1]):
        chave = NOME_POR_SIGLA.get(uf_sigla, uf_sigla).upper()
        p = popuf.get(chave)
        if not p:
            continue
        c24 = casos_uf.get(chave, [0] * 9)[6]  # coluna 2024
        uf_nome = uf_sigla
        p100k = n_prep / p * 100000
        a100k = c24 / p * 100000
        linhas_taxa.append((uf_nome, n_prep, p, round(p100k, 1), c24, round(a100k, 1)))
    with open(DESTINO / "taxa_prep_uf_100k.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["uf", "usuarios_prep", "populacao_2024", "prep_por_100k", "casos_aids_2024", "aids_por_100k"])
        w.writerows(linhas_taxa)
    print(f"OK  {DESTINO / 'taxa_prep_uf_100k.csv'}")

    ordem_prep = sorted(linhas_taxa, key=lambda l: -l[3])
    ordem_aids = sorted(linhas_taxa, key=lambda l: -l[5])
    print("\nTop 8 adesao PrEP (usuarios por 100 mil hab):")
    for l in ordem_prep[:8]:
        print("  %-24s %8.1f" % (l[0], l[3]))
    print("\nTop 8 carga de aids 2024 (casos por 100 mil hab):")
    for l in ordem_aids[:8]:
        print("  %-24s %8.1f" % (l[0], l[5]))
    pb_prep = next((i + 1, l) for i, l in enumerate(ordem_prep) if l[0] == "PB")
    pb_aids = next((i + 1, l) for i, l in enumerate(ordem_aids) if l[0] == "PB")
    print(f"\nParaiba: PrEP {pb_prep[1][3]} por 100k (posicao {pb_prep[0]}/27); "
          f"aids 2024 {pb_aids[1][5]} por 100k (posicao {pb_aids[0]}/27)")


if __name__ == "__main__":
    sys.exit(main())
