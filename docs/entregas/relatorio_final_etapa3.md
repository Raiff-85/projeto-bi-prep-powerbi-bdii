# Análise do Programa Nacional de PrEP no SUS e sua relação com a epidemia de HIV no Brasil: um painel de business intelligence

**Emanoel Raiff Gomes da Nóbrega Filho**

Universidade Federal da Paraíba (UFPB), Curso de Sistemas de Informação, João Pessoa, PB, Brasil

**Resumo**

Este trabalho apresenta um painel de business intelligence em Power BI para a análise do Programa Nacional de PrEP do SUS. O modelo dimensional segue a metodologia de Kimball, com duas tabelas fatos (dispensações e status anual do usuário) e quatro dimensões, alimentadas pelas bases oficiais do Ministério da Saúde de 2018 a 2025 e pelos casos de HIV detectados por população do Boletim Epidemiológico HIV e Aids 2025. O painel responde a oito perguntas de negócio. O achado central é que os casos novos de HIV se dividem quase meio a meio entre gays e outros homens que fazem sexo com homens (49%) e heterossexuais (48%), mas cerca de dois terços dos usuários de PrEP são do primeiro grupo: os heterossexuais, metade da transmissão detectada, seguem pouco alcançados pela prevenção.

**Abstract**

This work presents a business intelligence dashboard built in Power BI for the analysis of the Brazilian National PrEP program (SUS). The dimensional model follows the Kimball methodology, with two fact tables (dispensations and yearly user status) and four dimensions, fed by official Ministry of Health databases from 2018 to 2025 and by detected HIV cases per population from the 2025 HIV/AIDS Epidemiological Bulletin. The dashboard answers eight business questions. The central finding is that new HIV cases are split almost evenly between gay men and other men who have sex with men (49%) and heterosexuals (48%), but about two thirds of PrEP users belong to the former group: heterosexuals, half of detected transmission, are still barely reached by prevention.

## 1. Introdução

O Brasil incorporou a PrEP (profilaxia pré-exposição ao HIV) no SUS em dezembro de 2017, e o programa cresce de forma acelerada desde então; a série de dados analisada cobre o primeiro ano completo do programa, 2018, até 2025. Monitorar um programa dessa dimensão exige ir além dos relatórios administrativos: é preciso consolidar grandes volumes de dados de usuários e de dispensação em indicadores que apoiem decisões de política pública. Este relatório, produzido para a disciplina Banco de Dados II (UFPB, 2026.2), descreve o painel de business intelligence (BI) desenvolvido com esse objetivo, sobre um modelo dimensional construído segundo a metodologia de Kimball (KIMBALL; ROSS, 2013) e publicado em repositório público.

O objetivo do trabalho é responder, a partir de dados públicos, oito perguntas de negócio sobre o programa: evolução, perfil dos usuários, retenção, distribuição territorial do acesso, tipos de serviço, adesão por população-chave, distribuição dos casos novos de HIV detectados e desempenho comparado dos estados. Para sustentar as três últimas perguntas, o escopo foi ampliado, com mudança registrada em documentação própria, por uma terceira fonte: os casos de HIV detectados por população de exposição publicados no Boletim Epidemiológico HIV e Aids 2025 (BRASIL, 2025). O cruzamento entre quem usa a prevenção e em quem a transmissão recente ocorre produziu o achado central deste trabalho.

O restante do texto está organizado da seguinte forma: a Seção 2 caracteriza as fontes de dados; a Seção 3 apresenta a modelagem dimensional; a Seção 4 descreve o processo de ETL; a Seção 5 detalha as medidas em DAX; a Seção 6 registra as mudanças de escopo; a Seção 7 descreve o dashboard; a Seção 8 responde às perguntas de negócio; a Seção 9 analisa o achado central; a Seção 10 declara as limitações metodológicas; a Seção 11 trata da reprodutibilidade; e a Seção 12 conclui.

## 2. Fontes de dados

O painel utiliza quatro fontes públicas, duas originais, definidas na primeira etapa do projeto, e duas incorporadas por ampliação de escopo. A Tabela 1 resume as quatro.

Tabela 1. Fontes de dados utilizadas no projeto.

| # | Fonte | Conteúdo | Período | Volume |
| --- | --- | --- | --- | --- |
| 1 | MS/Dathi. Banco de usuários de PrEP (Banco_PrEP_2025.csv) | 1 linha por usuário, com status EmPrEP de 2018 a 2025 | 2018 a 2025 | 332.976 linhas |
| 2 | MS/Dathi. Dispensações de PrEP (Disp_PrEP_2025.csv) | 1 linha por dispensação | 02/01/2018 a 31/12/2025 | 1.672.709 linhas |
| 3 | MS/Dathi. Boletim Epidemiológico HIV e Aids 2025 (Tabelas 1, 2 e 8) | casos de HIV detectados por UF, por categoria de exposição (13+ anos) e taxa de detecção por UF | 2018 a 2025 (2025 parcial, até 30/09) | PDF transcrito para CSV por script (scripts/gera_dados_hiv.py) |
| 4 | IBGE. API SIDRA, tabela 6579 | população estimada por UF em 2024 | 2024 | 27 UFs |

As fontes 3 e 4 foram incorporadas em 31/10/2026, com registro e justificativa em documento próprio de mudança de escopo (docs/entregas/complemento_terceira_fonte_hiv.md), como exige a especificação da disciplina. Em 01/11/2026, a terceira fonte foi substituída: o conjunto de casos de aids do TABNET deu lugar aos casos de HIV detectados do Boletim 2025. O motivo é conceitual: a pergunta P7 busca medir transmissão recente, isto é, em quem a infecção está acontecendo agora, enquanto os casos de aids indicam diagnóstico tardio e acesso a tratamento. A substituição está registrada como adendo no mesmo documento. A quarta fonte (IBGE) permanece como material de apoio no repositório, fora do arquivo .pbix, por decisão registrada do integrante.

## 3. Modelagem dimensional

O modelo segue o esquema estrela preconizado por Kimball (KIMBALL; ROSS, 2013), no qual as tabelas fatos registram eventos que geram medidas e as tabelas dimensão descrevem o contexto desses eventos. O critério de decisão foi direto: um conjunto de dados entrou como fato quando representava uma ocorrência datada e mensurável (uma dispensação realizada; o status de um usuário em um fechamento de ano) e como dimensão quando representava uma entidade descritiva que responde a quem, onde, quando ou como o evento ocorreu.

FATO_DISPENSACOES registra o evento transacional de dispensa, com grão de uma linha por dispensação (1.672.709 linhas) e chaves estrangeiras para as dimensões de data, usuário, unidade dispensadora e tipo de atendimento; cada linha carrega a quantidade dispensada e a flag de serviço privado. FATO_STATUS_ANUAL tem grão de um usuário por ano e funciona como foto periódica (periodic snapshot): cada linha guarda o flag EmPrEP da pessoa em 31/12 do respectivo ano, construído no Power Query por unpivot das colunas EmPrEP_2018 a EmPrEP_2025 da base oficial.

As dimensões são: Dim_Data (calendário), Dim_Usuario (faixa etária, população-chave Pop_genero_pratica, raça, escolaridade e flags de vulnerabilidade), Dim_UDM (unidade dispensadora, com UF e região derivadas no ETL) e Dim_TipoAtendimento (serviço, esquema, modalidade, esfera e profissional).

Uma quarta tabela de fatos, FATO_CasosHIVAnual, foi criada para a terceira fonte, com grão de categoria de exposição por ano e, desde 01/11/2026, também por sexo (casos de HIV detectados na população de 13 anos ou mais). Ela não possui relacionamento com o esquema estrela, decisão deliberada que evita uma relação ambígua com a Dim_Data e com uma UF de significado distinto (unidade dispensadora na estrela; residência do caso na base do Boletim). A leitura cruzada entre PrEP e HIV é feita lado a lado, na aba Epidemia do painel.

## 4. Processo de ETL

O ETL foi implementado em Power Query (linguagem M) dentro do Power BI Desktop, em passos reproduzíveis, espelhados na pasta powerbi/etl_m do repositório:

1. leitura dos CSVs oficiais com delimitador ponto e vírgula e codificação UTF-8;
2. unpivot das colunas EmPrEP_2018 a EmPrEP_2025, que transforma uma linha por usuário em uma linha por usuário e ano e origina a FATO_STATUS_ANUAL;
3. derivação de Ano, DataKey (31/12 de cada ano) e do flag EmPrEP a partir do texto de status;
4. derivação da Dim_UDM a partir das dispensações, com deduplicação por codigo_udm e tratamento de valores vazios como Não informado;
5. limpeza de categorias com espaços extras (por exemplo, Sorologia com espaços à direita) e tratamento dos vazios gravados como nan e None na exportação oficial, padronizados como Não informado (308.898 dispensações, 18,5% do total, sem tipo de serviço informado);
6. unpivot dos anos do CSV transcrito do Boletim para a FATO_CasosHIVAnual, com exclusão da linha de total e tipagem inteira.

## 5. Medidas em DAX

Sete medidas sustentam o painel. A Tabela 2 apresenta cada uma com sua expressão resumida e a justificativa da escolha.

Tabela 2. Medidas DAX e justificativas.

| Medida | Expressão (resumo) | Justificativa |
| --- | --- | --- |
| Usuários Únicos | DISTINCTCOUNT(Cod_unificado) | contagem distinta, pois o mesmo usuário aparece em várias dispensações |
| Usuários em PrEP | CALCULATE(DISTINCTCOUNT(...), EmPrEP = 1) | medida semi-aditiva: nunca somar usuários entre anos |
| Usuários Descontinuados | análogo, com EmPrEP = 0 | mesma natureza semi-aditiva da medida anterior |
| Taxa de Retenção % | DIVIDE([Usuários em PrEP], [todos com status no ano]) | DIVIDE evita divisão por zero; o denominador reúne os registros usuário e ano com status |
| Total de Dispensas | COUNTROWS(FATO_DISPENSACOES) | contador de transações, medida aditiva |
| Novos Usuários | primeira dispensação do ano (dt_disp_min) | identifica a entrada no programa |
| % Dispensas Privado | DIVIDE(dispensações com esfera Privado, total) | participação do setor privado |

## 6. Mudanças de escopo registradas

Duas mudanças de escopo foram registradas em documento próprio, em 31/10 e 01/11 de 2026:

1. Ampliação de fontes: de duas para quatro, com a inclusão da base de casos de HIV por população e da população por UF do IBGE, necessárias para tornar respondíveis as perguntas P6, P7 e P8.
2. Substituição da terceira fonte (01/11/2026): os casos de aids do TABNET foram substituídos pelos casos de HIV detectados do Boletim Epidemiológico HIV e Aids 2025, por categoria de exposição e por UF, com a taxa de detecção por UF. O objetivo da P7 é mostrar em quem ocorre a transmissão recente, e os casos de aids medem outra coisa, o diagnóstico tardio e o acesso a tratamento. O CSV original de aids foi removido do repositório e permanece recuperável pelo histórico do git.
3. Escopo final do dashboard: as perguntas de adesão (P6 e P8) são respondidas somente com a base PrEP, em duas novas abas (Adesao Populacao e Estados); a base de HIV entra em uma única aba (Epidemia, P7); a população IBGE permanece fora do .pbix, como apoio no repositório, acompanhada da taxa de PrEP por 100 mil habitantes pré-calculada.
4. Análise de apoio por 100 mil habitantes: sem normalização pela população, a P8 favoreceria São Paulo apenas por ser o estado mais populoso. O indicador de apoio mostra São Paulo (279,8), Distrito Federal (245,6) e Rio de Janeiro (222,9) por 100 mil habitantes liderando a PrEP; quatro das seis maiores taxas de detecção de HIV do país em 2024 são de estados do Norte (Roraima 37,5; Amazonas 32,7; Pará 24,2; Amapá 22,7 por 100 mil, ao lado do Rio de Janeiro com 27,4 e do Distrito Federal com 22,9), sem cobertura proporcional de PrEP; e a Paraíba registra 71,2 usuários de PrEP por 100 mil habitantes (a 20ª entre 27 UFs) contra a menor taxa de detecção do país (12,4 por 100 mil, a 27ª).

## 7. O dashboard

O arquivo Projeto_BI_PREP.pbix contém um dashboard de sete páginas. A Tabela 3 relaciona cada página às perguntas que ela responde.

Tabela 3. Páginas do dashboard e perguntas respondidas.

| Página | Conteúdo | Pergunta |
| --- | --- | --- |
| Visao Geral | Total de Dispensas por UF e evolução anual de Usuários em PrEP | P1, P4 |
| Perfil | Usuários únicos por ano, gênero/prática, faixa etária e raça (barras empilhadas em página inteira) | P2 |
| Retencao | Taxa de Retenção % por ano e Usuários em PrEP comparados aos Descontinuados por população | P3 |
| Servicos | Total de Dispensas por tipo de serviço de atendimento | P5 |
| Adesao Populacao | Usuários em PrEP por ano e população-chave; Taxa de Retenção % e Usuários Descontinuados por população | P6 |
| Estados | Usuários Únicos por UF, crescimento anual por UF (com segmentação de UF) e Taxa de Retenção % por UF | P8 |
| Epidemia | Casos de HIV detectados por ano e categoria de exposição, com segmentações por categoria e por sexo e matriz de categoria por sexo | P7 |

## 8. Respostas às perguntas de negócio

**P1. Como evoluiu o programa?** Crescimento contínuo e acelerado: de aproximadamente 6,7 mil usuários com status Em PrEP em 2018 para cerca de 142 mil em 2025, na foto de 31/12 de cada ano. As dispensações crescem na mesma proporção, de cerca de 22 mil em 2018 para mais de 530 mil em 2025 (páginas Visao Geral e Adesao Populacao).

**P2. Qual o perfil dos usuários?** Gays e outros HSH cis são a maioria absoluta dos usuários únicos, cerca de dois terços, seguidos por mulheres cis, homens heterossexuais cis e pessoas trans e travestis. A faixa etária se concentra entre 20 e 39 anos (página Perfil).

**P3. Quem retém e quem abandona?** A proporção da base que segue Em PrEP no fechamento de cada ano cresce de cerca de 2% em 2018 para aproximadamente 43% em 2025, reflexo tanto da maturação do programa quanto do aumento da base. Entre populações, essa proporção em 2025 varia de aproximadamente 23% (mulheres cis) a 48% (gays e outros HSH cis), com homens heterossexuais cis em 32% e pessoas trans entre 33% e 37%. Em volume absoluto de registros fora da PrEP, gays e HSH lideram, pois também são a maioria da base (páginas Retencao e Adesao Populacao).

**P4. Como se distribui o acesso?** São Paulo concentra o maior volume de dispensações (cerca de 700 mil, seguida por Rio de Janeiro e Minas Gerais) e o maior número de usuários únicos (aproximadamente 140 mil). O indicador de apoio por 100 mil habitantes, calculado fora do .pbix, mostra São Paulo (279,8), Distrito Federal (245,6) e Rio de Janeiro (222,9) liderando a cobertura relativa, enquanto o Norte tem as maiores taxas de detecção de HIV do país e baixa cobertura de PrEP (páginas Visao Geral e Estados, com apoio do IBGE e do Boletim).

**P5. Como é a oferta de serviços?** O atendimento é predominantemente público e concentrado no Serviço de Atenção Especializada em IST/aids, seguido pelo atendimento na atenção primária; a dispensação privada é marginal, e sua participação é medida pela medida % Dispensas Privado (página Servicos).

**P6. Quem mais adere à prevenção?** Entre os usuários do programa, gays e outros HSH cis são a maioria absoluta das entradas em todos os anos e lideram a retenção relativa. Homens heterossexuais cis e mulheres cis aderem em volumes bem menores e com retenção inferior (32% e 23%, respectivamente, em 2025, contra 48% de gays e outros HSH cis). A adesão é desproporcional à participação na epidemia, como se vê na P7.

**P7. Em quais populações ocorrem os casos novos de HIV detectados?** A detecção se mantém estável, entre 36 mil e 40 mil casos por ano (40.259 em 2018 e 39.216 em 2024), com queda em 2020 (32.949) compatível com a subnotificação da pandemia; 2025 é parcial (até 30/09). Entre os casos de 13 anos ou mais com categoria conhecida em 2024 (28.176 casos), gays e outros HSH somam aproximadamente 49% (homossexuais 40,8% e bissexuais 8,5%) e heterossexuais aproximadamente 48% (13.424 casos, somando homens e mulheres), praticamente metade da transmissão detectada para cada um dos dois públicos (página Epidemia; Boletim 2025, Tabela 8, dados em dados/hiv).

**P8. Qual estado melhor aderiu?** Em volume absoluto, São Paulo (aproximadamente 140 mil usuários únicos), Rio de Janeiro e Minas Gerais. Normalizando pela população (apoio IBGE), São Paulo (279,8 por 100 mil), Distrito Federal (245,6) e Rio de Janeiro (222,9) lideram, com Santa Catarina também em destaque (200,5). A Paraíba registra 71,2 usuários de PrEP por 100 mil habitantes, a 20ª posição entre 27 UFs. O contraste territorial usa a taxa de detecção de HIV do Boletim, isto é, quantos diagnósticos novos foram notificados por 100 mil habitantes em 2024. Roraima (37,5), Amazonas (32,7), Rio de Janeiro (27,4), Pará (24,2), Distrito Federal (22,9) e Amapá (22,7) têm as seis maiores taxas do país, quatro delas de estados do Norte, e nenhum estado do Norte figura entre os líderes de PrEP. A Paraíba tem a menor taxa de detecção do país (12,4 por 100 mil, a 27ª): proporcionalmente, foi a UF que menos notificou diagnósticos novos de HIV em 2024.

## 9. O achado central: adesão e transmissão lidas juntas

A leitura conjunta das perguntas P6 e P7 é o principal resultado do trabalho.

- Gays e outros HSH respondem por aproximadamente 49% dos casos novos de HIV de 2024 e por cerca de dois terços dos usuários de PrEP: estão super-representados na prevenção em relação ao peso na transmissão detectada, o que indica focalização correta.
- Heterossexuais respondem por aproximadamente 48% dos casos novos de HIV (13.424 em 2024) e por participação muito menor na PrEP, cerca de um terço dos usuários somando homens heterossexuais cis e mulheres cis: estão sub-alcançados pela prevenção.
- Leitura por sexo (2024, casos de 13 anos ou mais com categoria conhecida, 28.176 no total): gays e outros HSH, população exclusivamente masculina, somam 13.895 casos (49,3%), mais que o dobro dos 6.325 homens heterossexuais (22,4%); completam o quadro 7.099 mulheres heterossexuais (25,2%) e as demais categorias (857 casos, 3,0%). A comparação é sempre por categoria de exposição, como o Boletim publica: homens e mulheres heterossexuais são populações distintas, e os percentuais são distribuição de casos, não risco individual, pois não há denominador de população por categoria.
- Não há contradição em quem mais usa PrEP também liderar as detecções: a PrEP é indicada justamente para pessoas com exposição elevada e cobre minoria da população HSH, de modo que o grupo de maior risco segue concentrando a transmissão detectada enquanto a prevenção evita infecções entre os usuários alcançados.
- A PrEP está bem focalizada no grupo de maior risco relativo, mas os heterossexuais, hoje metade da transmissão detectada, ainda não são alcançados na mesma proporção, seja por menor indicação e oferta, seja por menor procura. Como a base conta casos de HIV detectados (transmissão recente) e não casos de aids (que marcariam diagnóstico tardio), o dado aponta diretamente o público em que a prevenção ainda não chegou.
- Corolário territorial (P8): a mesma desigualdade aparece no mapa, já que quatro das seis maiores taxas de detecção de HIV do país em 2024 são de estados do Norte (Roraima 37,5; Amazonas 32,7; Pará 24,2; Amapá 22,7 por 100 mil), sem cobertura proporcional de PrEP.

## 10. Limitações metodológicas

1. Casos detectados não equivalem à incidência estimada. A base conta casos de HIV detectados e diagnosticados (Sinan, Siscel e Siclom), o melhor proxy aberto de transmissão recente; estimativas de incidência existem apenas no Boletim em PDF, que avisa que os dados dos últimos cinco anos são preliminares. Taxa de detecção baixa também não prova, sozinha, menos transmissão: pode refletir menos testagem e busca ativa ou atraso de notificação, de modo que a leitura territorial é sempre qualificada. O mesmo viés vale por população: homens heterossexuais testam menos e tendem a chegar tarde ao diagnóstico, de modo que o peso desse grupo nas detecções é um piso, e a transmissão real nele pode ser maior que a contada. O dado, porém, não permite inverter o ranking: mesmo com essa subestimação, gays e outros HSH seguem como o grupo líder em casos detectados.
2. A categoria de exposição do Boletim e a população-chave da base PrEP não formam taxonomias idênticas (HSH equivale aproximadamente à soma de homossexuais e bissexuais; heterossexuais cis equivale aproximadamente aos heterossexuais), de modo que a comparação entre P6 e P7 é por aproximação.
3. O recorte por categoria cobre pessoas de 13 anos ou mais (Tabela 8 do Boletim), enquanto os totais por UF incluem todas as idades. 2025 é parcial (até 30/09). A categoria Ignorado (cerca de 27% dos casos de 13 anos ou mais em 2024) é mostrada, não distribuída.
4. As contagens de usuários são semi-aditivas: um usuário não soma entre anos, e as medidas usam DISTINCTCOUNT por ano. A base oficial registra apenas dois valores por ano (Em PrEP ou vazio), sem a categoria descontinuado; o zero significa que a pessoa não estava Em PrEP naquele fechamento, o que inclui tanto quem ainda não tinha entrado quanto quem já tinha saído. Por isso a medida Usuários Descontinuados por população soma registros usuário e ano fora da PrEP ao longo da série, não pessoas únicas.
5. A UF do painel é a da unidade dispensadora, pois a base 2025 não traz município ou UF de residência do usuário; quem se deslocou conta em mais de uma UF. Na base de HIV, a UF é a de residência, o que gera um leve viés de comparação, declarado.
6. FATO_CasosHIVAnual não tem relacionamento com o modelo estrela: a leitura conjunta de PrEP e HIV é lado a lado, com os mesmos eixos de ano e população, e não uma junção (join), decisão documentada para evitar relação ambígua.
7. A base de HIV registra sexo registral (Masculino e Feminino), não identidade de gênero. A edição 2025 do Boletim não traz discriminação de pessoas trans em nenhum capítulo ou tabela, de modo que pessoas trans aparecem diluídas nos sexos registrais. O recorte por identidade de gênero existe apenas na base PrEP (Pop_genero_pratica), usada nas páginas Perfil e Adesao Populacao: gays e outros HSH cis (235.850), mulheres cis (40.678), homens heterossexuais cis (36.827), mulheres trans (11.240), homens trans (5.534), não binários (1.920) e travestis (926), usuários de PrEP de 2018 a 2025.

## 11. Reprodutibilidade

Todo o processo está versionado em repositório público no GitHub (github.com/Raiff-85). A pasta dados reúne as bases oficiais de PrEP (dados/2025), o PDF do Boletim 2025 e os CSVs transcritos por script (dados/hiv, gerados por scripts/gera_dados_hiv.py), além da população IBGE e da taxa de PrEP por 100 mil habitantes de apoio. O arquivo powerbi/Projeto_BI_PREP.pbix contém o modelo, o ETL (com as consultas M espelhadas em powerbi/etl_m), as medidas DAX e o dashboard de sete páginas. A pasta docs guarda a especificação resumida, o modelo dimensional, o dicionário de dados da Etapa 1, o relatório de ETL da Etapa 2 e os registros de mudança de escopo da Etapa 3.

## 12. Considerações finais

O projeto entregou um modelo dimensional Kimball completo (duas tabelas fatos e quatro dimensões, além do calendário), ETL reproduzível em Power Query, camada de medidas DAX justificadas e um dashboard de sete páginas que responde às oito perguntas de negócio, incluindo a análise epidemiológica que conecta adesão à PrEP e transmissão recente por população. O achado central é acionável: a focalização da PrEP em gays e outros HSH está funcionando, mas há dois vales claros de cobertura, os heterossexuais (aproximadamente 48% dos casos novos de HIV) e a região Norte (com quatro das seis maiores taxas de detecção do país), que apontam as frentes prioritárias da política pública.

Como aprendizados de modelagem, a decisão de grão (uma dispensação; um usuário por ano) determinou toda a camada de medidas: contagens de usuários são semi-aditivas e exigem DISTINCTCOUNT por ano, jamais soma entre períodos, e a foto anual construída por unpivot no Power Query se mostrou mais simples e auditável do que derivações equivalentes em DAX. A ampliação de escopo com a terceira fonte foi o que permitiu sair da descrição interna do programa e contrapor dois públicos distintos, quem está em prevenção e em quem ocorre a transmissão recente, revelando que os heterossexuais, metade dos casos novos de HIV, são justamente a população que a PrEP ainda não alcançou.

## Referências

KIMBALL, R.; ROSS, M. The data warehouse toolkit: the definitive guide to dimensional modeling. 3. ed. Indianapolis: John Wiley & Sons, 2013.

BRASIL. Ministério da Saúde. Departamento de DST, Aids e Hepatites Virais (Dathi). Banco de usuários e dispensações de PrEP do SUS: bases oficiais, versão 2025. Disponível em: http://www2.aids.gov.br/. Acesso em: out. 2026.

BRASIL. Ministério da Saúde. Departamento de HIV, Aids, Tuberculose, Hepatites Virais e Infecções Sexualmente Transmissíveis (Dathi). Boletim Epidemiológico: HIV e Aids 2025. Número Especial, dez. 2025. Disponível em: https://www.gov.br/aids/pt-br/central-de-conteudo/boletins-epidemiologicos/2025/boletim_hiv_aids_2025.pdf. Acesso em: 1º nov. 2026.

IBGE. Sistema SIDRA: tabela 6579, população estimada por Unidade da Federação, 2024. Disponível em: https://apisidra.ibge.gov.br/values/t/6579/n3/all/v/9324/p/2024. Acesso em: 31 out. 2026.

MICROSOFT. Documentação do Power BI Desktop: modelagem, linguagem M (Power Query) e DAX. Disponível em: https://learn.microsoft.com/power-bi/. Acesso em: out. 2026.

UFPB. Banco de Dados II (2026.2): especificação do projeto de BI. Material da disciplina, Profª. Renata Viegas.
