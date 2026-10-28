# Projeto de BI — Programa PrEP no Brasil (BDII 2026.2)

Data Warehouse + dashboard Power BI sobre o **Painel de Monitoramento da PrEP**
(Ministério da Saúde — Departamento de DST, Aids e Hepatites Virais), dados até 31/12/2024.

- **Usuários:** 236.053 registros · 234.967 usuários únicos
- **Dispensações:** 1.138.106 eventos (02/01/2018 a 31/12/2024)
- Fonte: <https://mediacenter.aids.gov.br/prep/Dados_PrEP_transparencia.zip>

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `dados/` | CSVs brutos + `Dicionário de Dados.pdf` (**não** versionados — 306 MB) |
| `docs/` | [ROTEIRO.md](docs/ROTEIRO.md) · [modelo-dimensional.md](docs/modelo-dimensional.md) · resumo da especificação |
| `powerbi/` | Projeto `.pbix` |
| `scripts/` | Utilitários de checagem dos dados |

## Modelo (resumo)

**2 fatos** — `FATO_DISPENSACOES` (transacional, grão: dispensa) e
`FATO_STATUS_ANUAL_USUARIO` (foto periódica, grão: usuário × ano, via *unpivot* de
`EmPrEP_2018…2024`) — ligadas a **5 dimensões**: Data, Usuário, Unidade Dispensadora,
Localidade de residência e Tipo de Atendimento. Detalhe completo em
[docs/modelo-dimensional.md](docs/modelo-dimensional.md).

## Aproveitamento do trabalho de Análise de Dados (2025.2)

O notebook da disciplina anterior (PrEP na Paraíba) embasa o domínio, as regras de limpeza
e as perguntas de negócio; o DW amplia o escopo para o Brasil inteiro e reorganiza os dados
em modelo estrela. Ver [docs/ROTEIRO.md](docs/ROTEIRO.md#2-o-que-estamos-aproveitando-do-trabalho-de-análise-de-dados-20252).

## Status

- [x] Estrutura do repositório
- [ ] Confirmação do tema com a professora (ver Passo 0 do roteiro)
- [ ] Modelo dimensional validado
- [ ] ETL (Power Query)
- [ ] Modelo estrela + DAX
- [ ] Dashboard (4 páginas)
- [ ] Documentação e apresentação (07–11/12)
