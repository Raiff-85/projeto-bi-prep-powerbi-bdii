# Relatório Final — Etapa 3: Resultados e Apresentação

**Disciplina:** Banco de Dados II — Profª. Renata Viegas — UFPB — 2026.2
**Projeto:** Análise do Programa Nacional de PrEP no SUS e sua relação com a epidemia de HIV/aids no Brasil
**Integrante:** Emanoel Raiff Nóbrega Fernandes
**Data:** 31/10/2026 · **Entrega:** 04/11/2026
**Artefatos:** `powerbi/Projeto_BI_PREP.pbix` (dashboard com 7 páginas) · repositório GitHub (github.com/Raiff-85), com bases em `dados/`, ETL em `powerbi/` e documentação em `docs/`

---

## 1. Resumo executivo

O projeto construiu, em Power BI, um painel de business intelligence sobre o **Programa
Nacional de PrEP (Profilaxia Pré-Exposição) do SUS**, usando a base oficial do
Departamento de DST/Aids/HV do Ministério da Saúde (dados 2018–2025, versão de
07/05/2026) e, como ampliação de escopo registrada, a base TABNET de **casos de
aids por categoria de exposição** (SINAN/SIM/SISCEL, 2018–2025).

O modelo dimensional segue **Kimball**: duas tabelas fatos (dispensações, transacional;
status anual do usuário, *periodic snapshot*) e dimensões de Data, Usuário, Unidade
Dispensadora (com UF/região) e Tipo de Atendimento. O dashboard responde às 8 perguntas
de negócio definidas no projeto — incluindo as três novas (P6–P8) que comparam **adesão
à PrEP × carga epidemiológica por população**, revelando o principal achado: **os
heterossexuais são a maioria absoluta dos novos casos de aids, mas têm a menor adesão
relativa à PrEP, enquanto gays e outros HSH — minoria nos casos — são a maioria dos
usuários do programa**.

---

## 2. O que foi entregue nas etapas anteriores (caráter cumulativo)

### 2.1 Fontes de dados (4, sendo 2 originais + 2 de ampliação)

| # | Fonte | Conteúdo | Período | Volume |
|---|---|---|---|---|
| 1 | MS/Dathi — Banco de usuários de PrEP (`Banco_PrEP_2025.csv`) | 1 linha = 1 usuário (status `EmPrEP_2018…EmPrEP_2025`) | 2018–2025 | 332.976 linhas |
| 2 | MS/Dathi — Dispensações de PrEP (`Disp_PrEP_2025.csv`) | 1 linha = 1 dispensação | 02/01/2018–31/12/2025 | 1.672.709 linhas |
| 3 | TABNET/Dathi — Casos de aids por categoria de exposição e por UF | matriz ano × categoria (e ano × UF) | 2018–2025 (2025 parcial até 30/09) | 10×10 e 29×10 |
| 4 | IBGE (API SIDRA, tabela 6579) — população estimada por UF, 2024 | 1 linha = 1 UF | 2024 | 27×2 |

As fontes 3 e 4 foram incorporadas em 31/10/2026 (mudança registrada e justificada no
documento `docs/entregas/complemento_terceira_fonte_hiv.md`, como exige a especificação).
A fonte 4 (IBGE) ficou como **material de apoio** fora do .pbix, por decisão do
integrante também registrada no mesmo documento.

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
- **FATO_CasosAidsAnual** (3ª fonte) — grão: categoria de exposição × ano. **Sem
  relacionamento** com a estrela (decisão deliberada: evita relação ambígua com a
  Dim_Data e com UF de significado distinto); a correlação é feita visualmente na aba
  Epidemia.

### 2.3 ETL principal (Power Query / M)

- Leitura dos CSVs oficiais com `Delimiter=";"` e `Encoding=65001` (UTF-8);
- **Unpivot** das colunas `EmPrEP_2018…EmPrEP_2025` → FATO_STATUS_ANUAL (grão usuário×ano);
- Derivação de `Ano`, `DataKey` (31/12 de cada ano) e flag `EmPrEP` a partir do texto de status;
- **DIM_UDM** derivada das dispensas (dedupe por `codigo_udm`; valores vazios → "Não informado"/"NI");
- Limpeza: `Trim` em categorias com espaços (ex.: `'Sorologia   '`), categorias ausentes → "Não informado";
- FATO_CasosAidsAnual: unpivot dos anos do CSV TABNET, exclusão da linha "Total", tipagem Int64.

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

## 3. Mudanças de escopo registradas (31/10/2026)

1. **Ampliação de fontes** (2 → 4): inclusão do TABNET/aids (casos por categoria e UF) e
   do IBGE (população por UF) — para tornar respondíveis P6, P7 e P8. Justificativa completa
   e caracterização das fontes em `docs/entregas/complemento_terceira_fonte_hiv.md`.
2. **Decisão final de escopo do dashboard:** as perguntas de **adesão (P6 e P8) são
   respondidas somente com a base PrEP** (novas abas "Adesao Populacao" e "Estados", com
   gráficos de entrada, permanência e saída por população e por UF). A população IBGE não
   entra no .pbix (fica no repositório como apoio, junto com a taxa PrEP/100 mil
   pré-calculada). A base de aids entra em **uma única aba** ("Epidemia", P7).
3. **Motivação das perguntas novas:** P6 e P7 só existem cruzando PrEP × casos por
   população (inexistente nas fontes originais); P8 sem normalização favoreceria SP
   apenas por ser o estado mais populoso — por isso a análise de apoio por 100 mil
   habitantes acompanha o relatório (SP 279,8 e DF 245,6 por 100 mil lideram a PrEP;
   o Norte tem a maior carga de aids por 100 mil — RR 41,3; AM 35,2 — sem cobertura
   proporcional de PrEP; PB: PrEP 71,2 — 20º/27 — contra carga de aids 13,9 — 23º/27).

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
| **Epidemia** | Casos de aids por ano × categoria de exposição (3ª fonte; segmentação por categoria; sem relação com a estrela) | **P7** |

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
— reflexo tanto da maturação do programa quanto do increase da base. Entre populações,
a retenção varia de ≈42% (mulheres cis) a ≈55% (Outros), com gays/HSH ≈52% e pessoas
trans ≈50%. Em volume absoluto de descontinuações, gays/HSH lideram (são também a
maioria da base); em termos relativos, as descontinuações acompanham a participação de
cada população. (Painéis *Retencao* e *Adesao Populacao*.)

**P4 — Como se distribui o acesso?** SP concentra o maior volume de dispensas (≈700 mil,
seguida de RJ e MG) e também o maior número de usuários únicos (≈140 mil). O indicador
de apoio por 100 mil habitantes (fora do .pbix) mostra SP (279,8), DF (245,6) e RJ
(222,9) liderando a cobertura relativa — e o Norte com alta carga de aids e baixa
cobertura de PrEP. (Painéis *Visao Geral* e *Estados* + apoio IBGE.)

**P5 — Serviços e esquema?** O atendimento é predominantemente público e concentrado no
Serviço de Atenção Especializada em IST/aids (serviço especializado), seguido pelo
atendimento na atenção primária; a dispensação privada é marginal (percentual medido
pela DAX `% Dispensas Privado`). (Painel *Servicos*.)

**P6 — Quem mais adere à prevenção (PrEP)?** Entre usuários do programa, gays e outros
HSH cis são a maioria absoluta das entradas em todos os anos e lideram a retenção relativa.
Homens heterossexuais cis e mulheres cis aderem em volumes muito menores e com retenção
inferior (≈42–47%). **Adesão é desproporcional à participação na epidemia** (ver P7).

**P7 — Onde ocorrem os novos casos de aids?** Entre casos com categoria de exposição
conhecida, **heterossexuais são a maioria absoluta em todos os anos** (16.262 em 2024,
≈44% dos 36.955 casos do ano), contra 8.170 homossexuais (≈22%) e 1.937 bissexuais
(≈5%) — HSH somados ≈27%. A série é estável em ≈35–37 mil casos/ano (2018–2024), com
queda em 2020 (29.980) compatível com subnotificação da pandemia; 2025 é parcial (até
30/09). (Painel *Epidemia*; números exatos da base TABNET em `dados/hiv/`.)

**P8 — Qual estado melhor aderiu?** Em volume absoluto, SP (≈140 mil usuários únicos),
RJ e MG. Normalizando pela população (apoio IBGE), **SP (279,8/100 mil), DF (245,6) e
RJ (222,9) lideram**; SC também se destaca (200,5). A Paraíba registra 71,2 usuários de
PrEP por 100 mil (20º entre 27 UFs). O contraste mais importante: **os estados do Norte
têm a maior carga de aids do país (RR 41,3; AM 35,2; AP 28,4 e PA 27,4 por 100 mil) e
não figuram no topo da adesão à PrEP** — lacuna territorial clara de focalização da
política pública.

---

## 6. O achado central: adesão × epidemia (P6 + P7 lidos juntos)

- **Heterossexuais: ≈44% dos casos de aids (2024) × participação pequena na PrEP.**
- **Gays e outros HSH: ≈27% dos casos × maioria absoluta dos usuários de PrEP (~2/3).**
- Leitura: a PrEP está bem **focalizada** no grupo de maior risco relativo (HSH), mas
  **heterossexuais — que hoje lideram o volume absoluto de casos avançados — ainda não
  são alcançados na mesma proporção**, seja por menor indicação/oferta, seja por menor
  demanda/procura. Como os casos aqui contabilizados são de **aids** (doença avançada,
  marcador de diagnóstico tardio), o dado sugere que a epidemia entre heterossexuais está
  sendo diagnosticada tardiamente e sem prevenção biomedical associada.
- Corolário territorial (P8): a mesma desigualdade aparece no mapa — Norte com maior
  carga de aids e menor cobertura de PrEP.

---

## 7. Limitações metodológicas (declaradas)

1. **Casos de aids ≠ infecções por HIV.** A base aberta por categoria de exposição é a
   de aids (doença manifesta — proxy oficial da epidemia usada no Boletim Epidemiológico);
   estimativas de incidência de HIV só existem em PDF. O painel usa aids como proxy e o
   diz explicitamente.
2. **Categoria de exposição (SINAN) ≠ Pop_genero_pratica (base PrEP).** Os taxonomias
   não são idênticas (HSH ≈ homossexual+bissexual; cis hetero ≈ heterossexual). A
   comparação P6×P7 é por aproximação.
3. **2025 da base de aids é parcial** (consolidado até 30/09/2025); tendências usam
   2018–2024. O "Ignorado" de categoria (~75 mil casos na série) é mostrado, não distribuído.
4. **Contagens de usuários são semi-aditivas** (um usuário não soma entre anos); as
   medidas usam `DISTINCTCOUNT` por ano. Usuários Descontinuados por população soma
   registros usuário-ano em descontinuação ao longo da série (não pessoas únicas).
5. **UF no painel = UF da unidade dispensadora** (a base 2025 não traz município/UF de
   residência do usuário). Quem se deslocou conta em mais de uma UF.
6. **FATO_CasosAidsAnual não tem relacionamento** com o modelo estrela: a leitura
   PrEP×aids é lado a lado (mesmos eixos de ano/população), não um join — decisão
   documentada para evitar relação ambígua.

---

## 8. Conclusões

O projeto entregou um modelo dimensional Kimball completo (2 fatos, 4 dimensões +
calendário), ETL reproduzível em Power Query, camada DAX com medidas justificadas e um
dashboard de 7 páginas que responde às 8 perguntas de negócio — incluindo a análise
epidemiológica que conecta adesão à PrEP e carga de aids por população. O achado central
é acionável: **a focalização da PrEP em HSH está funcionando, mas há dois vales claros de
cobertura — heterossexuais (maioria dos casos novos) e a região Norte — que indicam para
onde a política pública deve avançar.**

---

## 9. Estrutura do repositório (reprodutibilidade)

- `dados/2025/` — bases oficiais PrEP (usuários e dispensas); `dados/hiv/` — TABNET aids
  (categoria e UF), população IBGE e taxa PrEP/100 mil (apoio); script `scripts/gera_dados_hiv.py`.
- `powerbi/Projeto_BI_PREP.pbix` — modelo, ETL (Power Query M em `.zcode-gui/m/q*.txt`
  espelhado no repositório), medidas DAX e dashboard (7 páginas).
- `docs/` — especificação resumida, modelo dimensional, dicionário de dados (Etapa 1),
  relatório de ETL (Etapa 2) e registros de mudança de escopo (Etapa 3).
