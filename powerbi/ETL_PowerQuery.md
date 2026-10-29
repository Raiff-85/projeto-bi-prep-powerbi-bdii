# ETL no Power Query — cole cada consulta abaixo

**Como usar (uma vez só):** abra o **Power BI Desktop** (atalho novo na área de trabalho) →
`Obter dados` → `Consulta Nula` → na janela do Power Query: `Página Inicial` →
`Editor Avançado` → apague o que estiver lá, cole o código da consulta e clique em `Concluído`.
Depois: clique com o botão direito na consulta (à direita) → `Renomear` com o nome indicado.
Repita para as 8 consultas, **na ordem**. Ao final: `Página Inicial` → `Fechar e Aplicar`.

> Cada bloco diz o **nome da consulta** e o **código**. A primeira (pPasta) guarda o
> caminho dos arquivos — se um dia mover a pasta, é só editar ali.

---

## 1) Consulta `pPasta` (parâmetro do caminho)

```
"C:\Users\Administrator\Desktop\Trabalho Banco de Dados II - Power BI\dados\2025\"
```

## 2) Consulta `StgUsuarios` (base bruta de usuários)

```
let
    Fonte = Csv.Document(File.Contents(pPasta & "Banco_PrEP_2025.csv"), [Delimiter=";", Encoding=65001]),
    Cabecalho = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),
    Datas = Table.TransformColumnTypes(Cabecalho, {{"dt_disp_min", type date}, {"dt_disp_max", type date}}, "sv-SE"),
    ColunasTexto = List.Select(Table.ColumnNames(Datas), each not List.Contains({"dt_disp_min", "dt_disp_max"}, _)),
    SemEspacos = Table.TransformColumns(Datas, List.Transform(ColunasTexto, each {_, each Text.Trim(Text.From(_)), type text}))
in
    SemEspacos
```

## 3) Consulta `StgDispensas` (base bruta de dispensações)

```
let
    Fonte = Csv.Document(File.Contents(pPasta & "Disp_PrEP_2025.csv"), [Delimiter=";", Encoding=65001]),
    Cabecalho = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),
    Datas = Table.TransformColumnTypes(Cabecalho, {{"dt_disp", type date}, {"dt_disp_min", type date}, {"dt_disp_max", type date}}, "sv-SE"),
    ColunasTexto = List.Select(Table.ColumnNames(Datas), each not List.Contains({"dt_disp", "dt_disp_min", "dt_disp_max"}, _)),
    SemEspacos = Table.TransformColumns(Datas, List.Transform(ColunasTexto, each {_, each Text.Trim(Text.From(_)), type text}))
in
    SemEspacos
```

## 4) Consulta `Dim_Data` (calendário 2018–2025)

```
let
    Inicio = #date(2018, 1, 1),
    Fim = #date(2025, 12, 31),
    Dias = Duration.Days(Fim - Inicio) + 1,
    Lista = List.Dates(Inicio, Dias, #duration(1, 0, 0, 0)),
    Tab = Table.FromList(Lista, Splitter.SplitByNothing(), {"Data"}),
    Tipos = Table.TransformColumnTypes(Tab, {{"Data", type date}}),
    Adiciona = Table.AddColumn(Tipos, "Ano", each Date.Year([Data]), Int64.Type),
    Adiciona2 = Table.AddColumn(Adiciona, "NumTrimestre", each Date.QuarterOfYear([Data]), Int64.Type),
    Adiciona3 = Table.AddColumn(Adiciona2, "Trimestre", each "T" & Text.From([NumTrimestre]) & "/" & Text.From([Ano]), type text),
    Adiciona4 = Table.AddColumn(Adiciona3, "MesNum", each Date.Month([Data]), Int64.Type),
    Adiciona5 = Table.AddColumn(Adiciona4, "NomeMes", each Date.ToText([Data], "MMMM", "pt-BR"), type text),
    Adiciona6 = Table.AddColumn(Adiciona5, "MesAno", each Text.End("0" & Text.From([MesNum]), 2) & "/" & Text.From([Ano]), type text)
in
    Adiciona6
```

## 5) Consulta `Dim_Usuario` (perfil — 1 linha por usuário)

```
let
    Origem = StgUsuarios,
    Ordenado = Table.Sort(Origem, {{"dt_disp_max", Order.Descending}}),
    Unico = Table.Distinct(Ordenado, {"Cod_unificado"}),
    Colunas = Table.SelectColumns(Unico, {"Cod_unificado", "fetar", "Pop_genero_pratica", "raca", "escolaridade",
        "st_populacao_rua", "st_privada_liberdade", "st_habitantes_fronteira", "st_droga_injetavel",
        "st_substancias_psicoativas", "Pop_prof_sexo", "Pop_plan_rep", "Pop_gestante", "Pop_amamentacao",
        "dt_disp_min", "dt_disp_max", "codigo_udm", "UF_UDM", "regiao_UDM"}),
    Categorias = List.RemoveItems(Table.ColumnNames(Colunas), {"Cod_unificado", "dt_disp_min", "dt_disp_max", "codigo_udm"}),
    SemVazios = Table.TransformColumns(Colunas, List.Transform(Categorias, each {_, each if _ = null or _ = "" then "Não informado" else _, type text}))
in
    SemVazios
```

## 6) Consulta `Dim_UDM` (unidades dispensadoras)

```
let
    Origem = StgDispensas,
    Colunas = Table.SelectColumns(Origem, {"codigo_udm", "nome_udm", "cod_ibge_udm", "UF_UDM", "regiao_UDM"}),
    SemVazios = Table.TransformColumns(Colunas, {{"nome_udm", each if _ = null or _ = "" then "Não informado" else _, type text},
        {"cod_ibge_udm", each if _ = null or _ = "" then "Não informado" else _, type text},
        {"UF_UDM", each if _ = null or _ = "" then "NI" else _, type text},
        {"regiao_UDM", each if _ = null or _ = "" then "Não informado" else _, type text}}),
    Agrupado = Table.Group(SemVazios, {"codigo_udm"},
        {{"nome_udm", each List.Max([nome_udm]), type text},
         {"cod_ibge_udm", each List.Max([cod_ibge_udm]), type text},
         {"UF_UDM", each List.Max([UF_UDM]), type text},
         {"regiao_UDM", each List.Max([regiao_UDM]), type text}})
in
    Agrupado
```

## 7) Consulta `Dim_TipoAtendimento` (combinação de categorias da dispensa)

```
let
    Origem = StgDispensas,
    Colunas = Table.SelectColumns(Origem, {"tp_servico_atendimento", "tp_esquema_prep", "tp_modalidade", "Publico_privado_disp", "tp_profissional"}),
    SemVazios = Table.TransformColumns(Colunas, List.Transform(Table.ColumnNames(Colunas),
        each {_, each if _ = null or _ = "" then "Não informado" else _, type text})),
    Distinto = Table.Distinct(SemVazios),
    ComChave = Table.AddColumn(Distinto, "TipoKey",
        each Text.Combine({[tp_servico_atendimento], [tp_esquema_prep], [tp_modalidade], [Publico_privado_disp], [tp_profissional]}, " | "), type text)
in
    ComChave
```

## 8) Consulta `FATO_Dispensacoes` (grão: 1 dispensa)

```
let
    Origem = StgDispensas,
    SemVazios = Table.TransformColumns(Origem, List.Transform({"tp_servico_atendimento", "tp_esquema_prep", "tp_modalidade", "Publico_privado_disp", "tp_profissional"},
        each {_, each if _ = null or _ = "" then "Não informado" else _, type text})),
    ComChave = Table.AddColumn(SemVazios, "TipoKey",
        each Text.Combine({[tp_servico_atendimento], [tp_esquema_prep], [tp_modalidade], [Publico_privado_disp], [tp_profissional]}, " | "), type text),
    Fato = Table.SelectColumns(ComChave, {"dt_disp", "Cod_unificado", "codigo_udm", "TipoKey"}),
    Renomear = Table.RenameColumns(Fato, {{"dt_disp", "DataKey"}}),
    Contador = Table.AddColumn(Renomear, "QtdDispensas", each 1, Int64.Type)
in
    Contador
```

## 9) Consulta `FATO_StatusAnual` (grão: usuário × ano — foto de 31/12)

```
let
    Origem = StgUsuarios,
    Colunas = Table.SelectColumns(Origem, {"Cod_unificado", "codigo_udm", "EmPrEP_2018", "EmPrEP_2019", "EmPrEP_2020", "EmPrEP_2021", "EmPrEP_2022", "EmPrEP_2023", "EmPrEP_2024", "EmPrEP_2025"}),
    Despivotado = Table.UnpivotOtherColumns(Colunas, {"Cod_unificado", "codigo_udm"}, "AnoColuna", "Status"),
    Ano = Table.AddColumn(Despivotado, "Ano", each Number.FromText(Text.End([AnoColuna], 4)), Int64.Type),
    Foto = Table.AddColumn(Ano, "DataKey", each #date([Ano], 12, 31), type date),
    Flag = Table.AddColumn(Foto, "EmPrEP", each if [Status] = null or [Status] = "" then null else if Text.Contains([Status], "Em PrEP") then 1 else 0, Int64.Type),
    SoValidos = Table.SelectColumns(Table.FilterRows(Flag, each [EmPrEP] <> null), {"Cod_unificado", "codigo_udm", "DataKey", "Ano", "EmPrEP"})
in
    SoValidos
```

---

# Depois do "Fechar e Aplicar": criar os relacionamentos

Na exibição de **Modelo** (ícone de tabelas à esquerda), arraste para criar (ou confirme
que o Power BI sugeriu — confira se ficou **1 para muitos (1:*)** na direção certa):

| Da tabela (muitos) | Para a tabela (um) | Coluna |
|---|---|---|
| FATO_Dispensacoes | Dim_Data | DataKey → Data |
| FATO_Dispensacoes | Dim_Usuario | Cod_unificado |
| FATO_Dispensacoes | Dim_UDM | codigo_udm |
| FATO_Dispensacoes | Dim_TipoAtendimento | TipoKey |
| FATO_StatusAnual | Dim_Data | DataKey → Data |
| FATO_StatusAnual | Dim_Usuario | Cod_unificado |
| FATO_StatusAnual | Dim_UDM | codigo_udm |

Dica: clique com o botão direito em `Dim_Data` → **Marcar como tabela de datas**.

# Medidas DAX (criar em `Nova medida`)

```
Total de Dispensas = COUNTROWS(FATO_Dispensacoes)
```
```
Usuários Únicos = DISTINCTCOUNT(FATO_Dispensacoes[Cod_unificado])
```
```
Usuários em PrEP = CALCULATE(DISTINCTCOUNT(FATO_StatusAnual[Cod_unificado]), FATO_StatusAnual[EmPrEP] = 1)
```
```
Usuários Descontinuados = CALCULATE(DISTINCTCOUNT(FATO_StatusAnual[Cod_unificado]), FATO_StatusAnual[EmPrEP] = 0)
```
```
Taxa de Retenção % = DIVIDE([Usuários em PrEP], [Usuários em PrEP] + [Usuários Descontinuados])
```
```
Novos Usuários no Ano =
CALCULATE(
    DISTINCTCOUNT(Dim_Usuario[Cod_unificado]),
    FILTER(Dim_Usuario, YEAR(Dim_Usuario[dt_disp_min]) IN VALUES(Dim_Data[Ano]))
)
```
```
% Dispensas Privadas =
DIVIDE(
    CALCULATE([Total de Dispensas], Dim_TipoAtendimento[Publico_privado_disp] = "Privado"),
    [Total de Dispensas]
)
```
