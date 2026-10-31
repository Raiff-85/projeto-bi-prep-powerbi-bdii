# Complemento — Ampliação do escopo com uma 3ª fonte (HIV/aids) — registrado em 31/10/2026

> A especificação da professora pede que **mudanças de fonte/escopo/modelo sejam
> registradas e justificadas** ao longo das etapas. Este documento registra a
> ampliação do escopo aprovada pelo integrante em 31/10/2026, a menos de 4 dias da
> entrega da Etapa 3 (04/11).

## 1. Justificativa da mudança

As perguntas originais (P1–P5) caracterizam o programa de PrEP por dentro (crescimento,
perfil, retenção, território, esquema de uso). O integrante propôs perguntas mais
relevantes epidemiologicamente:

- **P6.** Comparando homossexuais e heterossexuais, quem mais adere à prevenção (PrEP)?
- **P7.** Os novos casos de HIV/aids no Brasil — em qual população eles ocorrem
  (homossexual × heterossexual), e esse quadro mudou de 2018 a 2024?
- **P8.** Qual estado melhor aderiu à PrEP até agora?

P6 e P7 só são respondíveis **cruzando a PrEP com uma base de casos de HIV/aids por
população** — inexistente nas duas fontes atuais. P8 exige **normalizar por população**
(taxa por 100 mil habitantes), senão SP "vence" só por ser o estado mais populoso.
Por isso incorporamos duas bases oficiais complementares (casos × população).

## 2. Caracterização das novas fontes

**Quantidade:** 2 novas fontes (passando de 2 para 4 no total do projeto).

| Item | Fonte 3 — Casos de aids por categoria/UF | Fonte 4 — População por UF (IBGE) |
|---|---|---|
| Nome | TABNET "Casos de aids identificados no Brasil" (SINAN + SIM + SISCEL/SICLOM) | População estimada — tabela 6579, Censo/estimativas 2024 |
| Origem / responsável | MS/SVSA — Departamento de HIV, Aids, Tuberculose, Hepatites Virais e IST (Dathi), via TABNET | IBGE, via API SIDRA |
| Link | http://www2.aids.gov.br/cgi/tabcgi.exe?tabnet/br.def (exportação CSV `formato=prn`) | https://apisidra.ibge.gov.br/values/t/6579/n3/all/v/9324/p/2024 |
| Formato | CSV exportado do TABNET (`;`), UTF-8 | JSON da API convertido para CSV (`;`) |
| Conteúdo | Casos de aids diagnosticados por ano, por **categoria de exposição hierárquica** (Homossexual, Bissexual, Heterossexual, UDI, Transmissão Vertical, Ignorado…) e por **UF de residência** | Habitantes estimados de cada UF em 2024 |
| Período | Diagnóstico 2018–2025 (consolidado até 30/09/2025; **2025 é preliminar e incompleto**) | Ano 2024 |
| Abrangência | Brasil (todas as UFs) | Brasil (27 UFs) |
| Linhas × colunas | Categoria: 10×10 · UF: 29×10 | 27×2 |
| Significado do registro | 1 linha = categoria de exposição (ou UF); cada célula = nº de casos no ano | 1 linha = 1 UF; valor = população |
| Integração | **Ano** (liga com DIM_Calendário) e **UF** (liga com DIM_UF do PrEP) | **UF** (sigla) |

Arquivos gerados em `dados/hiv/` pelo script `scripts/gera_dados_hiv.py`:

- `hiv_aids_casos_categoria_2018_2025.csv` (10 categorias × 8 anos + Total)
- `hiv_aids_casos_uf_2018_2025.csv` (28 UF/ignorado × 8 anos + Total)
- `pop_uf_ibge_2024.csv` (27 UFs)
- `taxa_prep_uf_100k.csv` (derivada no projeto: usuários de PrEP por UF ÷ população × 100 mil, + casos aids/100 mil)

## 3. Ressalvas metodológicas (honestidade com os dados)

1. **Casos de aids ≠ infecções por HIV.** A tabela aberta nacional por categoria de
   exposição é a de **aids** (doença manifesta — indicador de diagnóstico tardio, usado
   no Boletim Epidemiológico). Estimativas de *novas infecções por HIV* por população são
   publicadas só em PDF (Boletim), sem base aberta. Para P7 usamos casos de aids como
   proxy oficial da epidemia por população, e o relatório diz isso explicitamente.
2. **Categoria de exposição ≠ Pop_genero_pratica.** O SINAN classifica como
   Homossexual/Bissexual/Heterossexual; a base PrEP usa Gays e outros HSH cis / Mulheres
   cis / Homens heterossexuais cis / trans e não bináries. A comparação é por
   **aproximação** (HSH ≈ homossexual+bissexual; cis hetero ≈ heterossexual), declarada no relatório.
3. **2025 (aids) está incompleto** (até 30/09) — comparações de tendência usam 2018–2024.
4. Na contagem de usuários por UF, quem mudou de serviço em UFs diferentes conta em cada
   uma (1 pessoa = até 27 marcações); efeito pequeno e declarado.

## 4. O que os números já mostram (prévia, 31/10/2026)

- **P6:** entre os usuários de PrEP, "Gays e outros HSH cis" são a maioria absoluta
  (ver painel Perfil); nos casos de aids com categoria conhecida, **heterossexuais são a
  maioria absoluta** (16–17 mil/ano × ~8 mil homossexual + ~1,9 mil bissexual).
  Adesão à PrEP dos HSH é **desproporcional à sua participação nos casos** — indício de
  boa focalização; heterossexuais têm adesão baixa relativa à sua carga de casos.
- **P7:** casos de aids estão estáveis (~37 mil/ano, 2018–2024, com queda em 2020 por
  subnotificação da pandemia); heterossexual lidera em absoluto; HSH crescem em
  participação relativa. 2025 parcial até setembro.
- **P8 (taxa por 100 mil hab):** lideram **SP (279,8), DF (245,6), RJ (222,9), SC (200,5)**;
  o **Norte tem a maior carga de aids (RR 41,3; AM 35,2; AP 28,4; PA 27,4 por 100 mil) e
  NÃO está no topo da PrEP** — lacuna de cobertura territorial. **PB: 71,2/100 mil (20º
  de 27)** com carga de aids de 13,9/100 mil (23º).

## 5. Impacto no modelo e no dashboard (decisão FINAL de 31/10, pelo integrante)

O integrante decidiu: **as perguntas de adesão (P6 e P8) são respondidas só com a base
da PrEP**, sem população do IBGE no dashboard — por meio de novas abas com os gráficos
adequados (quem entra mais por população/UF, quem permanece mais, quem desiste mais).
A base de população IBGE fica no repositório apenas como **material de apoio opcional**
(`dados/hiv/pop_uf_ibge_2024.csv` e `taxa_prep_uf_100k.csv`), fora do .pbix.

Adesão, operacionalmente, na base PrEP = **entrada** (novos usuários no ano, status
`Em PrEP <ano>`), **permanência** (Taxa de Retenção % por grupo) e **saída**
(Usuários Descontinuados por grupo).

- **P6 (população):** aba nova "Adesao Populacao" — colunas empilhadas Usuários em PrEP
  por Ano com legenda Pop_genero_pratica (quem cresce mais); barras Taxa de Retenção % e
  Usuários Descontinuados por Pop_genero_pratica (quem permanece/abandona mais).
- **P8 (estado):** aba nova "Estados" — barras Usuários Únicos por UF_UDM (onde a PrEP
  chegou mais); barras Taxa de Retenção % por UF_UDM; segmentação de UF ligada ao
  Usuários em PrEP por Ano (crescimento estado a estado).
- **P7 (novos casos por população):** única aba que usa a 3ª fonte — aba "Epidemia"
  com os casos de aids por categoria de exposição (homossexual × heterossexual ×
  bissexual, 2018–2024; 2025 parcial). Consulta nova `FATO_CasosAidsAnual` (unpivot dos
  anos), **sem relacionamento com o modelo estrela** (usa o próprio Ano no eixo —
  evita relação ambígua com DIM_Calendário) e com a ressalva aids≠HIV declarada.
