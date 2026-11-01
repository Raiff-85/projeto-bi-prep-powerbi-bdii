# Projeto de BI — Programa Nacional de PrEP no Brasil (BDII 2026.2)

Data Warehouse + dashboard Power BI sobre o **Programa Nacional de PrEP do SUS**
(Ministério da Saúde — Departamento de DST, Aids e Hepatites Virais), com dados de
**02/01/2018 a 31/12/2025** (base versão 2025), ampliado com os **casos de HIV
detectados por população de exposição** (Boletim Epidemiológico HIV e Aids 2025) e a
**população estimada por UF** (IBGE) como apoio.

- **Usuários:** 332.976 linhas (base 2025)
- **Dispensações:** 1.672.709 eventos (02/01/2018 a 31/12/2025)
- **Casos de HIV detectados:** série 2018–2025 por categoria de exposição, sexo e UF
  (transcrita do Boletim com validações automáticas)
- Fontes: <https://mediacenter.aids.gov.br/prep/Dados_PrEP_transparencia.zip> ·
  <https://www.gov.br/aids/pt-br/central-de-conteudo/boletins-epidemiologicos/2025/boletim_hiv_aids_2025.pdf>

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `dados/2025/` | Bases oficiais PrEP — usuários e dispensações (**fora do git** por tamanho; ZIP oficial acima) |
| `dados/hiv/` | Casos de HIV detectados, taxa de detecção e população IBGE (CSVs gerados por script, versionados) |
| `docs/` | [ROTEIRO.md](docs/ROTEIRO.md) · [modelo-dimensional.md](docs/modelo-dimensional.md) · especificação resumida · entregas das etapas |
| `powerbi/` | Projeto `.pbix` + M do ETL espelhado em [`powerbi/etl_m/`](powerbi/etl_m/) |
| `scripts/` | `gera_dados_hiv.py` — transcreve o Boletim para CSV com asserts de validação |

## Modelo (resumo)

**2 fatos** — `FATO_DISPENSACOES` (transacional, grão: dispensa) e `FATO_STATUS_ANUAL`
(foto periódica, grão: usuário × ano, via *unpivot* de `EmPrEP_2018…2025`) — e a fato
`FATO_CasosHIVAnual` (categoria de exposição × sexo × ano, sem relacionamento, por
decisão documentada), ligadas a dimensões de **Data, Usuário, Unidade Dispensadora e
Tipo de Atendimento**. Detalhe completo em
[docs/modelo-dimensional.md](docs/modelo-dimensional.md).

O dashboard tem **7 páginas** e responde a **8 perguntas de negócio**: evolução do
programa, perfil dos usuários, retenção × descontinuidade, distribuição do acesso,
esquema e prescritor, adesão por população, casos de HIV detectados por população e
adesão por estado — com o cruzamento adesão × transmissão recente (aba Epidemia) e a
taxa de detecção por UF (RR 37,5 … PB 12,4 por 100 mil) como contraste territorial.

## Aproveitamento do trabalho de Análise de Dados (2025)

O trabalho da disciplina anterior (PrEP na Paraíba, 2018–2024) embasou o domínio, as
regras de limpeza e as perguntas; este projeto amplia o escopo para o Brasil inteiro e
reorganiza os dados em modelo estrela. Ver
[docs/ROTEIRO.md](docs/ROTEIRO.md#2-o-que-estamos-aproveitando-do-trabalho-de-análise-de-dados-20252).

## Status

- [x] Bases oficiais tratadas (PrEP 2018–2025 + Boletim HIV/aids 2025)
- [x] Modelo dimensional (2 fatos + dimensões; fato de HIV sem relacionamento, deliberado)
- [x] ETL em Power Query (M espelhado em `powerbi/etl_m/`)
- [x] Medidas DAX (contagens semi-aditivas com `DISTINCTCOUNT`, `DIVIDE`)
- [x] Dashboard de 7 páginas respondendo às 8 perguntas
- [x] Relatório final, roteiro de apresentação e documentação das etapas
- [ ] Apresentação dos resultados (07–11/12)
