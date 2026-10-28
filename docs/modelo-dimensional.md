# Modelo dimensional — PrEP Brasil (estrela)

> **Base a usar:** `dados/2025/` (versão oficial de 07/05/2026, dados 2018–2025).
> **Atenção no ETL:** os CSVs novos usam separador **`;`** (ponto e vírgula) e BOM UTF-8
> (`utf-8-sig`). Nomes: `Banco_PrEP_2025.csv` (usuários, 332.976 linhas) e
> `Disp_PrEP_2025.csv` (dispensas, 1.672.709 linhas, 02/01/2018 a 31/12/2025).
> A versão antiga (vírgula, até 2024) fica em `dados/` como referência/backup.

Metodologia: **Kimball** — as 4 etapas foram aplicadas na ordem.

## As 4 etapas de Kimball

1. **Selecionar o processo de negócio** — dispensação e acompanhamento de usuários de PrEP
   no SUS/serviços conveniados (programa nacional do Dept. de DST/Aids/HV do MS).
2. **Declarar a granularidade**
   - Fato A: **uma linha por dispensação realizada** (evento transacional).
   - Fato B: **uma linha por usuário × ano de fechamento (31/12/2018…31/12/2024)** —
     foto periódica (periodic snapshot) do status "Em PrEP / Descontinuou".
3. **Identificar as dimensões** — Data, Usuário, Unidade Dispensadora (UDM),
   Localidade de residência, Tipo de Atendimento/Dispensação.
4. **Identificar os fatos** — contagem de dispensações; contagem de usuários por status;
   flags (teve testagem, IST autorrelatada, serviço privado etc.). Medidas **não aditivas
   no tempo** no Fato B (contagem distinta de usuários não soma entre anos — usar
   `DISTINCTCOUNT` por filtro, nunca somar fatos B entre períodos).

---

## FATO_DISPENSACOES (fato de transação)

- **Grão:** 1 dispensação · **~1.138.106 linhas** (2018-01-02 a 2024-12-31)
- **Chaves (FK):** `DataKey`(dt_disp) · `UsuarioKey` · `UDMKey` · `TipoAtendKey`
- **Medidas / fatos numéricos:**
  - `QtdDispensas` (contador = 1 por linha)
  - `ServicoPrivado` (flag 0/1 — Publico_privado_disp = Privado)
  - (a versão 2025 **não traz mais** `tp_testagem_hiv` nem `IST_autorrelato` por dispensa;
    IST autorrelatado agora consta na base de usuários)
- **Dimensões degeneradas (texto curtas na própria fato):** nenhuma necessária —
  todas as categorias caem em `Dim_TipoAtendimento`.
- Colunas da fonte (versão 2025): `Cod_unificado, codigo_udm, nome_udm, cod_ibge_udm, dt_disp,
  UF_UDM, regiao_UDM, tp_servico_atendimento, tp_esquema_prep, tp_modalidade,
  Publico_privado_disp, tp_profissional, dt_disp_min, dt_disp_max`
- Notas de qualidade (perfil da versão 2024; reconfirmar na 2025): parte das dispensas sem
  `tp_servico_atendimento`/`tp_esquema_prep` (maioria serviço privado) → categoria
  "Não informado"; valores com espaços extras (ex.: `'Sorologia   '`) → Trim no Power Query.

## FATO_STATUS_ANUAL_USUARIO (foto periódica)

- **Grão:** 1 usuário × ano · construída no Power Query por **unpivot** das colunas
  `EmPrEP_2018 … EmPrEP_2025` do CSV de usuários (8 anos; valor vazio = usuário ainda não
  tinha entrado no programa → filtrar ou marcar "Pré-entrada").
- **Chaves (FK):** `DataKey`(ano) · `UsuarioKey` · `UDMKey`(última UDM)
- **Medidas:** `EmPrEP` (flag), `Descontinuou` (flag), `UsuariosAtivosAno`
  (DISTINCTCOUNT Cod_unificado com EmPrEP=1), `TaxaRetencaoAno`
  (= Ativos / (Ativos + Descontinuados)).

## Dimensões (5)

| Dimensão | Grão | Atributos (origem) |
|---|---|---|
| **Dim_Data** | dia (2018–2024) | Data, Ano, Trimestre, Mês, MêsAno, Semestre — padrão da `DimCalendario.csv` usada em aula; criar por DAX (`CALENDAR`) ou Power Query |
| **Dim_Usuario** | usuário (base 2025: ~333 mil; deduplicar por `Cod_unificado` se houver repetição) | Cod_unificado (SK), FaixaEtária(fetar), PopulacaoChave(Pop_genero_pratica), Raca(raca), Escolaridade(escolaridade), flags vulnerabilidade: st_populacao_rua, st_privada_liberdade, st_habitantes_fronteira, st_droga_injetavel, st_substancias_psicoativas, Pop_prof_sexo, Pop_plan_rep, Pop_gestante, Pop_amamentacao |
| **Dim_UnidadeDispensadora** | UDM (codigo_udm) | CodigoUDM, NomeUDM(nome_udm), MunicipioIBGE(cod_ibge_udm) → junta com município/UF/região; construir a partir do CSV de dispensas (tem mais UDMs que o de usuários) |
| **Dim_Localidade** | município IBGE da **unidade dispensadora** (na versão 2025 a base não traz mais o município de residência do usuário) | MunicipioIBGE, UF, Regiao — **enriquecimento**: complementar com tabela de municípios do IBGE (nome do município) — opcional |
| **Dim_TipoAtendimento** | combinação de categorias da dispensa | TipoServico(tp_servico_atendimento), Esquema(tp_esquema_prep), Modalidade(tp_modalidade), Esfera(Publico_privado_disp), Prescritor(tp_profissional) |

## Relacionamentos (1:N, filtro dimensão → fato)

```
Dim_Data[DataKey]        → FATO_DISPENSACOES[DataKey]
Dim_Usuario[UsuarioKey]  → FATO_DISPENSACOES[UsuarioKey]
Dim_UDM[UDMKey]          → FATO_DISPENSACOES[UDMKey]
Dim_TipoAtend[TipoKey]   → FATO_DISPENSACOES[TipoAtendKey]
Dim_Data[DataKey]        → FATO_STATUS_ANUAL[AnoKey]   (ou Dim separada AnoCalendario)
Dim_Usuario[UsuarioKey]  → FATO_STATUS_ANUAL[UsuarioKey]
Dim_UDM[UDMKey]          → FATO_STATUS_ANUAL[UDMKey]
```
Hierarquias: Data → Ano › Trimestre › Mês; Localidade → Região › UF › Município.

## Medidas DAX iniciais

```dax
Total Dispensas = COUNTROWS(FATO_DISPENSACOES)
Usuarios Unicos = DISTINCTCOUNT(FATO_DISPENSACOES[UsuarioKey])
Usuarios em PrEP (ano) = CALCULATE(DISTINCTCOUNT(FATO_STATUS_ANUAL[UsuarioKey]), FATO_STATUS_ANUAL[EmPrEP] = 1)
Taxa Retencao % = DIVIDE([Usuarios em PrEP (ano)], CALCULATE(COUNTROWS(FATO_STATUS_ANUAL), FATO_STATUS_ANUAL[EmPrEP] IN {0,1}))
Novos Usuarios = -- usuarios cujo ano da 1ª dispensa (dt_disp_min) = ano do filtro
Dispensas por Usuario = DIVIDE([Total Dispensas], [Usuarios Unicos])
% Servico Privado = DIVIDE(CALCULATE([Total Dispensas], Dim_TipoAtendimento[Esfera]="Privado"), [Total Dispensas])
```

## Perguntas de negócio que o dashboard responde (herdadas do trabalho de Análise de Dados)

1. Como evoluiu o programa de PrEP no Brasil (usuários ativos e novas entradas, 2018–2025)?
2. Qual o perfil sociodemográfico dos usuários (população-chave × idade × raça × escolaridade) e das novas variáveis de vulnerabilidade (fronteira, droga injetável, substâncias psicoativas)?
3. Qual população retém mais e qual abandona mais (retenção × descontinuidade)?
4. Como se distribui o acesso (UF/região, público×privado, tipo de serviço)?
5. Como mudaram esquema (diário × sob demanda) e prescritor (médico × enfermeiro) ao longo do tempo?
