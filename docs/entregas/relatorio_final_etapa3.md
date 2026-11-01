# Relatório Final — Etapa 3: Resultados e Apresentação

**Disciplina:** Banco de Dados II — Profª. Renata Viegas — UFPB — 2026.2
**Projeto:** Análise do Programa Nacional de PrEP no SUS e sua relação com a epidemia de HIV/aids no Brasil
**Integrante:** Emanoel Raiff Nóbrega Fernandes
**Data:** 01/11/2026 · **Entrega:** 04/11/2026
**Artefatos:** `powerbi/Projeto_BI_PREP.pbix` (dashboard com 7 páginas) · repositório GitHub (github.com/Raiff-85), com bases em `dados/`, ETL em `powerbi/` e documentação em `docs/`

---

## 1. Resumo executivo

O projeto construiu, em Power BI, um painel de business intelligence sobre o **Programa
Nacional de PrEP (Profilaxia Pré-Exposição) do SUS**, usando a base oficial do
Departamento de DST/Aids/HV do Ministério da Saúde (dados 2018–2025, versão de
07/05/2026) e, como ampliação de escopo registrada, os **casos de HIV detectados por
população de exposição** do Boletim Epidemiológico HIV e Aids 2025 (Sinan +
Siscel/Siclom, 2018–2025; 2025 parcial).

O modelo dimensional segue **Kimball**: duas tabelas fatos (dispensações, transacional;
status anual do usuário, *periodic snapshot*) e dimensões de Data, Usuário, Unidade
Dispensadora (com UF/região) e Tipo de Atendimento. O dashboard responde às 8 perguntas
de negócio definidas no projeto — incluindo as três novas (P6–P8) que comparam **adesão
à PrEP × transmissão recente por população**, revelando o principal achado: **os casos
novos de HIV se dividem quase meio a meio entre gays e outros HSH (≈49%) e
heterossexuais (≈48%), mas a PrEP se concentra nos primeiros (~2/3 dos usuários) — os
heterossexuais, metade da transmissão detectada, ainda são alcançados pela prevenção em
bem menor escala**.

---

## 2. O que foi entregue nas etapas anteriores (caráter cumulativo)

### 2.1 Fontes de dados (4, sendo 2 originais + 2 de ampliação)

| # | Fonte | Conteúdo | Período | Volume |
|---|---|---|---|---|
| 1 | MS/Dathi — Banco de usuários de PrEP (`Banco_PrEP_2025.csv`) | 1 linha = 1 usuário (status `EmPrEP_2018…EmPrEP_2025`) | 2018–2025 | 332.976 linhas |
| 2 | MS/Dathi — Dispensações de PrEP (`Disp_PrEP_2025.csv`) | 1 linha = 1 dispensação | 02/01/2018–31/12/2025 | 1.672.709 linhas |
| 3 | MS/Dathi — **Boletim Epidemiológico HIV e Aids 2025** (Tabelas 1, 2 e 8): casos de HIV detectados por UF, taxa de detecção por UF e casos por categoria de exposição (13+ anos) | matriz ano × categoria (e ano × UF) | 2018–2025 (2025 parcial até 30/09) | PDF transcrito para CSV por script (`scripts/gera_dados_hiv.py`) |
| 4 | IBGE (API SIDRA, tabela 6579) — população estimada por UF, 2024 | 1 linha = 1 UF | 2024 | 27×2 |

As fontes 3 e 4 foram incorporadas em 31/10/2026 (mudança registrada e justificada no
documento `docs/entregas/complemento_terceira_fonte_hiv.md`, como exige a especificação).
Em 01/11/2026 a fonte 3 foi **substituída** (TABNET de casos de aids → Boletim com casos
de **HIV** detectados), porque o objetivo da P7 é medir transmissão recente — quem não
está se prevenindo — e não casos de aids (que marcam diagnóstico tardio/acesso a
tratamento). A substituição está registrada como adendo no mesmo documento. A fonte 4
(IBGE) ficou como **material de apoio** fora do .pbix, por decisão do integrante também
registrada.

### 2.2 Modelo dimensional (esquema estrela, metodologia Kimball)

- **FATO_DISPENSACOES** — grão: 1 dispensação. FKs: DataKey, UsuarioKey, UDMKey,
  TipoAtendKey. Medidas: `QtdDispensas`, flag `ServicoPrivado`.
- **FATO_STATUS_ANUAL** — grão: 1 usuário × ano (foto periódica 31/12 de cada ano,
  construída no Power Query por *unpivot* das colunas `EmPrEP_2018…EmPrEP_2025`).
  Medida-fato: flag `EmPrEP` (1 = "Em PrEP", 0 = descontinuado; nulos = pré-entrada,
  filtrados).
- **Dimensões:** Dim_Data (calendário), Dim_Usuario (faixa etária, população-chave
  `Pop_genero_pratica`, raça, escolaridade, flags de vulnerabilidade), Dim_UDM (unidade
  dispensadora, com `UF_UDM` e `regiao_UDM` derivados no ETL), Dim_TipoAtendimento
  (serviço, esquema, modalidade, esfera, profissional).
- **FATO_CasosHIVAnual** (3ª fonte) — grão: categoria de exposição × ano (casos de HIV
  detectados, 13+ anos). **Sem relacionamento** com a estrela (decisão deliberada: evita
  relação ambígua com a Dim_Data e com UF de significado distinto); a leitura cruzada é
  feita visualmente na aba Epidemia.

### 2.3 ETL principal (Power Query / M)

- Leitura dos CSVs oficiais com `Delimiter=";"` e `Encoding=65001` (UTF-8);
- **Unpivot** das colunas `EmPrEP_2018…EmPrEP_2025` → FATO_STATUS_ANUAL (grão usuário×ano);
- Derivação de `Ano`, `DataKey` (31/12 de cada ano) e flag `EmPrEP` a partir do texto de status;
- **DIM_UDM** derivada das dispensas (dedupe por `codigo_udm`; valores vazios → "Não informado"/"NI");
- Limpeza: `Trim` em categorias com espaços (ex.: `'Sorologia   '`), categorias ausentes → "Não informado";
- FATO_CasosHIVAnual: unpivot dos anos do CSV transcrito do Boletim (Tabela 8),
  exclusão da linha "Total", tipagem Int64.

### 2.4 Medidas DAX (todas com justificativa)

| Medida | Expressão (resumo) | Justificativa |
|---|---|---|
| Usuários Únicos | `DISTINCTCOUNT(Cod_unificado)` | contagem distinta — o mesmo usuário aparece em várias dispensas |
| Usuários em PrEP | `CALCULATE(DISTINCTCOUNT(...), EmPrEP=1)` | medida semi-aditiva: **nunca somar** usuários entre anos |
| Usuários Descontinuados | análogo com `EmPrEP=0` | idem |
| Taxa de Retenção % | `DIVIDE([Usuários em PrEP], [todos com status no ano])` | `DIVIDE` evita divisão por zero; denominador = usuários-ano com status |
| Total de Dispensas | `COUNTROWS(FATO_DISPENSACOES)` | contador de transações (aditivo) |
| Novos Usuários | 1ª dispensa no ano (`dt_disp_min`) | identifica entrada no programa |
| % Dispensas Privado | `DIVIDE(dispensas com esfera=Privado, total)` | participação do setor privado |

---

## 3. Mudanças de escopo registradas (31/10 e 01/11/2026)

1. **Ampliação de fontes** (2 → 4): inclusão de base de casos de HIV por população e
   do IBGE (população por UF) — para tornar respondíveis P6, P7 e P8. Justificativa
   completa e caracterização das fontes em `docs/entregas/complemento_terceira_fonte_hiv.md`.
2. **Substituição da 3ª fonte (01/11/2026):** o TABNET de casos de **aids** deu lugar ao
   **Boletim Epidemiológico HIV e Aids 2025** (casos de **HIV detectados** por categoria
   de exposição e por UF + taxa de detecção por UF). Motivo: o objetivo da P7 é mostrar
   **quem não está se prevenindo** (transmissão recente), e casos de aids medem outra
   coisa — diagnóstico tardio/acesso a tratamento. Registrado como adendo no mesmo
   documento; o CSV original de aids foi removido do repositório (recuperável pelo git).
3. **Decisão final de escopo do dashboard:** as perguntas de **adesão (P6 e P8) são
   respondidas somente com a base PrEP** (novas abas "Adesao Populacao" e "Estados", com
   gráficos de entrada, permanência e saída por população e por UF). A população IBGE não
   entra no .pbix (fica no repositório como apoio, junto com a taxa PrEP/100 mil
   pré-calculada). A base de HIV entra em **uma única aba** ("Epidemia", P7).
4. **Motivação das perguntas novas:** P6 e P7 só existem cruzando PrEP × casos por
   população (inexistente nas fontes originais); P8 sem normalização favoreceria SP
   apenas por ser o estado mais populoso — por isso a análise de apoio por 100 mil
   habitantes acompanha o relatório (SP 279,8 e DF 245,6 por 100 mil lideram a PrEP;
   o Norte tem as maiores taxas de detecção de HIV do país — RR 37,5; AM 32,7; PA 24,2;
   AP 22,7 por 100 mil em 2024 — sem cobertura proporcional de PrEP; PB: PrEP 71,2 —
   20º/27 — contra detecção de HIV 12,4 — 27º/27).

---

## 4. O dashboard (7 páginas no .pbix)

| Página | Conteúdo | Pergunta |
|---|---|---|
| Visao Geral | Total de Dispensas por UF; evolução anual de Usuários em PrEP | P1, P4 |
| Perfil | Usuários únicos por ano, gênero/prática, faixa etária e raça (barras empilhadas, página inteira) | P2 |
| Retencao | Taxa de Retenção % por ano; Usuários em PrEP × Descontinuados por população | P3 |
| Servicos | Total de Dispensas por tipo de serviço de atendimento | P5 |
| **Adesao Populacao** | Usuários em PrEP por ano × população-chave; Taxa de Retenção % e Usuários Descontinuados por população | **P6** |
| **Estados** | Usuários Únicos por UF; crescimento anual por UF (com segmentação de UF); Taxa de Retenção % por UF | **P8** |
| **Epidemia** | Casos de HIV detectados por ano × categoria de exposição (3ª fonte; segmentação por categoria; sem relação com a estrela) | **P7** |

---

## 5. Respostas às perguntas de negócio (P1–P8)

**P1 — Como evoluiu o programa?** Crescimento contínuo e acelerado: de ≈12 mil usuários
com status "Em PrEP" em 2018 para ≈190 mil em 2025 (foto de 31/12 de cada ano). As
dispensações crescem na mesma proporção, passando de ~50 mil/ano no início para centenas
de milhares/ano no fim do período. (Painéis *Visao Geral* e *Adesao Populacao*.)

**P2 — Qual o perfil dos usuários?** Gays e outros HSH cis são a maioria absoluta
(~2/3 dos usuários únicos); seguidos por mulheres cis, homens heterossexuais cis e
pessoas trans/travestis. A faixa etária concentra-se em 20–39 anos. (Painel *Perfil*.)

**P3 — Quem retém e quem abandona?** A Taxa de Retenção anual (usuários que seguem
"Em PrEP" no fechamento do ano seguinte à entrada) cresce de ≈3% (2018) para ≈44% (2025)
— reflexo tanto da maturação do programa quanto do aumento da base. Entre populações,
a retenção varia de ≈42% (mulheres cis) a ≈55% (Outros), com gays/HSH ≈52% e pessoas
trans ≈50%. Em volume absoluto de descontinuações, gays/HSH lideram (são também a
maioria da base); em termos relativos, as descontinuações acompanham a participação de
cada população. (Painéis *Retencao* e *Adesao Populacao*.)

**P4 — Como se distribui o acesso?** SP concentra o maior volume de dispensas (≈700 mil,
seguida de RJ e MG) e também o maior número de usuários únicos (≈140 mil). O indicador
de apoio por 100 mil habitantes (fora do .pbix) mostra SP (279,8), DF (245,6) e RJ
(222,9) liderando a cobertura relativa — e o Norte com as maiores taxas de detecção de
HIV do país e baixa cobertura de PrEP. (Painéis *Visao Geral* e *Estados* + apoio
IBGE/Boletim.)

**P5 — Serviços e esquema?** O atendimento é predominantemente público e concentrado no
Serviço de Atenção Especializada em IST/aids (serviço especializado), seguido pelo
atendimento na atenção primária; a dispensação privada é marginal (percentual medido
pela DAX `% Dispensas Privado`). (Painel *Servicos*.)

**P6 — Quem mais adere à prevenção (PrEP)?** Entre usuários do programa, gays e outros
HSH cis são a maioria absoluta das entradas em todos os anos e lideram a retenção relativa.
Homens heterossexuais cis e mulheres cis aderem em volumes muito menores e com retenção
inferior (≈42–47%). **Adesão é desproporcional à participação na epidemia** (ver P7).

**P7 — Em quais populações ocorrem os novos casos de HIV detectados?** A detecção se
mantém estável em ≈36–40 mil casos/ano (40.259 em 2018; 39.216 em 2024), com queda em
2020 (32.949) compatível com subnotificação da pandemia; 2025 é parcial (até 30/09).
Entre casos de 13+ anos com categoria conhecida em 2024 (28.176), **gays e outros HSH
somam ≈49%** (homossexuais 40,8% + bissexuais 8,5%) e **heterossexuais ≈48%** (13.424
casos, somando homens e mulheres) — praticamente metade da transmissão detectada em cada
um dos dois públicos. (Painel *Epidemia*; Boletim Epidemiológico HIV e Aids 2025,
Tabela 8, dados em `dados/hiv/`.)

**P8 — Qual estado melhor aderiu?** Em volume absoluto, SP (≈140 mil usuários únicos),
RJ e MG. Normalizando pela população (apoio IBGE), **SP (279,8/100 mil), DF (245,6) e
RJ (222,9) lideram**; SC também se destaca (200,5). A Paraíba registra 71,2 usuários de
PrEP por 100 mil (20º entre 27 UFs). O contraste mais importante: **as maiores taxas de
detecção de HIV do país estão no Norte (RR 37,5; AM 32,7; PA 24,2 e AP 22,7 por 100 mil
em 2024 — 4 das 6 primeiras colocações) e esses estados não figuram no topo da adesão à
PrEP** — lacuna territorial clara de focalização da política pública.

---

## 6. O achado central: adesão × transmissão (P6 + P7 lidos juntos)

- **Gays e outros HSH: ≈49% dos casos novos de HIV (2024) × ~2/3 dos usuários de PrEP**
  — super-representados na prevenção em relação ao peso na transmissão detectada:
  focalização correta.
- **Heterossexuais: ≈48% dos casos novos de HIV (13.424 em 2024) × participação muito
  menor na PrEP (~1/3 dos usuários, somando homens heterossexuais cis e mulheres cis)**
  — sub-alcançados pela prevenção.
- Leitura: a PrEP chega mais ao grupo de maior risco relativo (HSH), mas heterossexuais
  — hoje metade da transmissão detectada — ainda não são alcançados na mesma proporção,
  seja por menor indicação/oferta, seja por menor demanda/procura. Como a base conta
  **casos de HIV detectados (transmissão recente)** — e não casos de aids (que marcariam
  diagnóstico tardio) —, o dado aponta diretamente o público em que a prevenção ainda
  não chegou.
- Corolário territorial (P8): a mesma desigualdade aparece no mapa — o Norte concentra
  as maiores taxas de detecção de HIV do país (RR 37,5; AM 32,7; PA 24,2; AP 22,7 por
  100 mil) sem cobertura proporcional de PrEP.

---

## 7. Limitações metodológicas (declaradas)

1. **Casos detectados ≠ incidência estimada.** A base conta casos de HIV
   **detectados/diagnosticados** (Sinan + Siscel/Siclom) — o melhor proxy aberto de
   transmissão recente; estimativas de incidência só existem no Boletim (PDF). O Boletim
   nota ainda que os dados dos **últimos cinco anos são preliminares** (consolidação
   futura tende a aumentá-los).
2. **Categoria de exposição (Boletim/Sinan) ≠ Pop_genero_pratica (base PrEP).** Os
   taxonomias não são idênticos (HSH ≈ homossexual+bissexual; cis hetero ≈ heterossexual).
   A comparação P6×P7 é por aproximação.
3. **O recorte por categoria cobre pessoas de 13+ anos** (Tabela 8 do Boletim); os totais
   por UF incluem todas as idades. **2025 é parcial** (até 30/09). A categoria
   "Ignorado" (~27% dos casos 13+ em 2024) é mostrada, não distribuída.
4. **Contagens de usuários são semi-aditivas** (um usuário não soma entre anos); as
   medidas usam `DISTINCTCOUNT` por ano. Usuários Descontinuados por população soma
   registros usuário-ano em descontinuação ao longo da série (não pessoas únicas).
5. **UF no painel = UF da unidade dispensadora** (a base 2025 não traz município/UF de
   residência do usuário). Quem se deslocou conta em mais de uma UF. Na base de HIV, a UF
   é a de residência (leva a um leve viés de comparação, declarado).
6. **FATO_CasosHIVAnual não tem relacionamento** com o modelo estrela: a leitura
   PrEP×HIV é lado a lado (mesmos eixos de ano/população), não um join — decisão
   documentada para evitar relação ambígua.

---

## 8. Considerações finais

O projeto entregou um modelo dimensional Kimball completo (2 fatos, 4 dimensões +
calendário), ETL reproduzível em Power Query, camada DAX com medidas justificadas e um
dashboard de 7 páginas que responde às 8 perguntas de negócio — incluindo a análise
epidemiológica que conecta adesão à PrEP e transmissão recente por população. O achado
central é acionável: **a focalização da PrEP em HSH está funcionando, mas há dois vales
claros de cobertura — heterossexuais (≈48% dos casos novos de HIV) e a região Norte
(maiores taxas de detecção do país) — que apontam as frentes prioritárias da política
pública.**

Como aprendizados de modelagem, a decisão de grão (1 dispensação; 1 usuário × ano)
determinou toda a camada de medidas: contagens de usuários são **semi-aditivas** e exigem
`DISTINCTCOUNT` por ano, jamais soma entre períodos; e a foto anual construída por
*unpivot* no Power Query mostrou-se mais simples e auditável do que derivações
equivalentes em DAX. A ampliação de escopo com a 3ª fonte (casos de HIV detectados por
população) foi o que permitiu sair da descrição interna do programa e contrapor dois
públicos distintos: quem está em prevenção e em quem ocorre a transmissão recente — os
heterossexuais, metade dos casos novos de HIV, são justamente a população que a PrEP
ainda não alcançou.

Como trabalhos futuros: (i) incorporar a população IBGE ao modelo para normalizar a
adesão por 100 mil habitantes dentro do próprio dashboard (hoje o indicador existe apenas
como material de apoio); (ii) enriquecer a Dim_UDM com a hierarquia região → UF →
município para *drill-down* territorial; (iii) investigar a categoria "Ignorado" da base
de HIV (~27% dos casos de 13+ em 2024), cuja redistribuição pode reforçar ou atenuar as
leituras por população.

---

## 9. Estrutura do repositório (reprodutibilidade)

- `dados/2025/` — bases oficiais PrEP (usuários e dispensas); `dados/hiv/` — Boletim
  Epidemiológico HIV e Aids 2025 (PDF) e CSVs transcritos (casos por categoria 13+, casos
  por UF, taxa de detecção por UF), população IBGE e taxa PrEP/100 mil (apoio); script
  `scripts/gera_dados_hiv.py`.
- `powerbi/Projeto_BI_PREP.pbix` — modelo, ETL (Power Query M em `.zcode-gui/m/q*.txt`
  espelhado no repositório), medidas DAX e dashboard (7 páginas).
- `docs/` — especificação resumida, modelo dimensional, dicionário de dados (Etapa 1),
  relatório de ETL (Etapa 2) e registros de mudança de escopo (Etapa 3).

---

## 10. Referências

- KIMBALL, Ralph; ROSS, Margy. *The Data Warehouse Toolkit: The Definitive Guide to
  Dimensional Modeling*. 3. ed. Indianapolis: John Wiley & Sons, 2013.
- BRASIL. Ministério da Saúde. Departamento de DST, Aids e Hepatites Virais (Dathi).
  **Banco de usuários e dispensações de PrEP do SUS** (bases oficiais, versão 2025).
  Disponível em: http://www2.aids.gov.br/. Acesso em: out. 2026.
- BRASIL. Ministério da Saúde. Departamento de HIV, Aids, Tuberculose, Hepatites Virais
  e Infecções Sexualmente Transmissíveis (Dathi). **Boletim Epidemiológico — HIV e Aids
  2025** (Número Especial, dez. 2025): Tabela 1 (casos de HIV por UF), Tabela 2 (taxa de
  detecção por UF) e Tabela 8 (casos por categoria de exposição, 13+ anos). Disponível
  em: https://www.gov.br/aids/pt-br/central-de-conteudo/boletins-epidemiologicos/2025/
  boletim_hiv_aids_2025.pdf. Acesso em: 1º nov. 2026.
- IBGE. **Sistema SIDRA — Tabela 6579**: População estimada por Unidade da Federação,
  2024. Disponível em:
  https://apisidra.ibge.gov.br/values/t/6579/n3/all/v/9324/p/2024. Acesso em: 31 out. 2026.
- BRASIL. Ministério da Saúde. Departamento de HIV, Aids, Tuberculose, Hepatites Virais
  e Infecções Sexualmente Transmissíveis (Dathi). **Boletins Epidemiológicos HIV/aids** —
  referência metodológica para uso de casos detectados como indicador por população de
  exposição.
- MICROSOFT. **Documentação do Power BI Desktop** — modelagem, linguagem M (Power Query)
  e DAX. Disponível em: https://learn.microsoft.com/power-bi/. Acesso em: out. 2026.
- UFPB. **Banco de Dados II (2026.2) — Especificação do projeto de BI** (Profª. Renata
  Viegas). Material da disciplina.
