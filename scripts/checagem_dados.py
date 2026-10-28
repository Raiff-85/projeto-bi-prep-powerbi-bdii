"""Checagens rápidas das bases PrEP (executar com python puro, sem dependências).

Uso:  python scripts/checagem_dados.py
"""
import csv
import os
import sys
from collections import Counter

DADOS = os.path.join(os.path.dirname(__file__), "..", "dados")


def resumo(path, colunas, chave):
    caminho = os.path.join(DADOS, path)
    if not os.path.exists(caminho):
        sys.exit(f"Arquivo não encontrado: {caminho} (ver dados/LEIA-ME.txt)")
    with open(caminho, newline="", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        contadores = {c: Counter() for c in colunas}
        chaves = Counter()
        n = 0
        for linha in leitor:
            n += 1
            chaves[linha[chave]] += 1
            for c in colunas:
                contadores[c][(linha.get(c) or "").strip() or "(vazio)"] += 1
    print(f"\n=== {path}: {n} linhas | {len(chaves)} {chave} únicos ===")
    for c in colunas:
        print(f"{c}: {dict(contadores[c].most_common(6))}")


if __name__ == "__main__":
    resumo(
        "Banco_PrEP_usuarios.csv",
        ["fetar", "Pop_genero_pratica", "raca4_cat", "escol4", "EmPrEP_2024"],
        "Cod_unificado",
    )
    resumo(
        "Banco_PrEP_dispensas.csv",
        ["tp_servico_atendimento", "tp_esquema_prep", "Publico_privado_disp", "tp_profissional"],
        "Cod_unificado",
    )
