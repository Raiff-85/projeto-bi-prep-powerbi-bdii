# Etapa 1 — Definição do projeto (BDII 2026.2)

**Título do projeto:** Painel de Business Intelligence do Programa PrEP no Brasil —
quem usa, como acessa e quem permanece (2018–2025)

**Integrante:** Emanoel Raiff Nóbrega Fernandes (matrícula 20221350010)

---

## Tema e contexto

A PrEP (Profilaxia Pré-Exposição) é o uso preventivo de antirretrovirais contra o HIV,
distribuída gratuitamente pelo SUS desde 2018. O Departamento de HIV/Aids, Tuberculose,
Hepatites Virais e IST do Ministério da Saúde publica, no Painel de Monitoramento da PrEP,
os microdados anonimizados de **usuários** e **dispensações** de todo o país. Analisar esse
programa é relevante porque a PrEP é a principal estratégia biomédica de prevenção do HIV
no Brasil: entender quem acessa, por onde e quem permanece no uso apoia decisões de gestão
em saúde pública (onde ampliar serviços, quais populações priorizar em campanhas, como
reduzir a descontinuidade — problema central apontado pelo próprio Ministério da Saúde).

## Objetivo do projeto (perguntas que o BI deve responder)

1. Como evoluiu o programa de 2018 a 2025 (usuários ativos, novas entradas, volume de dispensações)?
2. Qual o perfil sociodemográfico dos usuários (população-chave, faixa etária, raça, escolaridade, vulnerabilidades)?
3. Quais populações retêm mais e quais abandonam mais o método (retenção × descontinuidade por grupo)?
4. Como se distribui o acesso no território (UF, região, público × privado, tipo de serviço)?
5. Como mudaram, ao longo do tempo, o esquema de uso (diário × sob demanda) e o profissional prescritor?

## Caracterização das fontes

**Quantidade:** 2 fontes (2 arquivos CSV do mesmo pacote oficial) + dicionário de dados oficial.

| Item | Fonte 1 | Fonte 2 |
|---|---|---|
| Nome | Banco de usuários de PrEP (`Banco_PrEP_2025.csv`) | Banco de dispensações de PrEP (`Disp_PrEP_2025.csv`) |
| Origem / responsável | Ministério da Saúde — Dept. de HIV/Aids/TB/Hepatites Virais e IST | idem |
| Link | https://mediacenter.aids.gov.br/prep/Dados_PrEP_transparencia.zip (página: gov.br/aids → indicadores → Painel PrEP) | idem (mesmo pacote) |
| Formato | CSV UTF-8, separador `;` | CSV UTF-8, separador `;` |
| Conteúdo | Cadastro e situação de cada usuário | Cada dispensação realizada |
| Período | Dados até 31/12/2025 (status anual 2018–2025) | 02/01/2018 a 31/12/2025 |
| Abrangência | Brasil (todas as UFs) | Brasil (todas as UFs) |
| Linhas × colunas | 332.976 linhas × 34 colunas | 1.672.709 linhas × 14 colunas |
| Significado do registro | 1 linha = 1 usuário(a); dados referentes à última dispensação | 1 linha = 1 dispensação; um usuário pode ter várias |

**Integração entre as fontes:** as duas bases se relacionam pelas chaves
**`Cod_unificado`** (identifica a pessoa — 1 usuário : N dispensações) e
**`codigo_udm` / `cod_ibge_udm`** (identificam o serviço dispensador, permitindo enriquecer
com nomes de municípios via tabela do IBGE). A base de usuários traz o *perfil* (base para
as dimensões) e a de dispensas traz os *eventos datados* (fato transacional); os status
anuais `EmPrEP_2018…2025` da base de usuários formam a segunda tabela de fatos (foto
periódica de 31/12 de cada ano).

## Dicionário de dados

Definições oficiais (fonte: `Dicionário de Dados_painelPrEP.pdf` do próprio pacote);
exemplos retirados do primeiro registro de cada base.

### Banco_PrEP_2025.csv (usuários) (34 colunas · 332.976 linhas)

| Nome da coluna | Descrição | Tipo de dado | Exemplo | Observações |
|---|---|---|---|---|
| `Cod_unificado` | Código único que identifica cada usuário(a) da PrEP | Texto | `102120980.0` | Pessoa pseudonimizada — não permite identificação |
| `raca` | Raça/cor autodeclarada | Categórica | `Parda` | Indígena, Preta, Parda, Branca, Amarela, Ignorada/Não informada |
| `escolaridade` | Escolaridade em anos de estudo | Categórica | `De 12 e mais anos` | Nenhuma/Sem educação formal; 1-3; 4-7; 8-11; 12 ou mais anos; Ignorada |
| `fetar` | Faixa etária no momento da última dispensação | Categórica | `40 a 49` | <18, 18-24, 25-29, 30-39, 40-49, 50 e mais |
| `Pop_genero_pratica` | População-chave (gênero/prática sexual) | Categórica | `Gays e outros HSH cis` | Gays e outros HSH cis; Mulheres cis; Homens heterossexuais cis; Mulheres trans; Homens trans; Não bináries; Travestis |
| `codigo_udm` | Código do serviço de saúde da última dispensação (UDM) | Texto | `005` | Chave de ligação com a base de dispensas |
| `nome_udm` | Nome do serviço de saúde da última dispensação | Texto | `CENTRO DE REFERÊNCIA E TREINAMENTO DST/A` | — |
| `cod_ibge_udm` | Código IBGE do município do serviço | Texto | `3550308` | Permite ligar com tabela de municípios IBGE |
| `UF_UDM` | Sigla da Unidade Federada do serviço | Texto | `SP` | — |
| `regiao_UDM` | Região geográfica do serviço | Texto | `Sudeste` | — |
| `dt_disp_min` | Data da primeira dispensação de PrEP do usuário | Data (aaaa-mm-dd) | `2019-02-08` | Base para calcular 'novos usuários' por ano |
| `dt_disp_max` | Data da última dispensação de PrEP do usuário | Data (aaaa-mm-dd) | `2026-01-23` | — |
| `st_habitantes_fronteira` | Se a pessoa era habitante de fronteira no cadastro | Categórica (Sim/Não) | `Não` | Novo na versão 2025 |
| `st_droga_injetavel` | Uso de droga injetável ou slam nos últimos 3 meses | Categórica (Sim/Não) | `Não` | Novo na versão 2025 |
| `st_substancias_psicoativas` | Uso de substâncias psicoativas antes/durante sexo (chemsex), últimos 3 meses | Categórica (Sim/Não) | `Não` | Novo na versão 2025 |
| `tp_servico_atendimento` | Tipo de serviço onde ocorreu o atendimento | Categórica | `Serviço Especializado` | Serviço Especializado; CTA; Atenção Primária; Privado; Extra-muros; Teleatendimento |
| `tp_profissional` | Profissional que prescreveu a última dispensação | Categórica | `Médico(a)` | Médico(a); Enfermeiro(a); Farmacêutico(a); Dentista |
| `IST_autorrelato` | Relato de sinal/sintoma ou diagnóstico de IST na última dispensação | Categórica | `Nenhuma IST autorrelatada` | Nenhuma IST autorrelatada; Alguma IST autorrelatada |
| `st_populacao_rua` | Situação de rua no momento do cadastro | Categórica (Sim/Não) | `Não` | — |
| `st_privada_liberdade` | Pessoa privada de liberdade no momento do cadastro | Categórica (Sim/Não) | `Não` | — |
| `Pop_prof_sexo` | Trocou sexo por dinheiro/bens/serviços nos últimos 3 meses | Categórica (Sim/Não) | `Não` | — |
| `Pop_plan_rep` | Uso da PrEP relacionado a planejamento reprodutivo | Categórica (Sim/Não) | `Não Informado` | — |
| `Pop_gestante` | Uso da PrEP relacionado à gestação | Categórica | `Não se aplica` | Sim; Não; Não se aplica |
| `Pop_amamentacao` | Uso da PrEP relacionado à amamentação | Categórica (Sim/Não) | `Não` | — |
| `teve_dispensa` | Se a pessoa teve dispensação (Sim) ou apenas cadastro (Não) | Categórica (Sim/Não) | `Sim` | — |
| `Disp_Ultimos_12m` | Se teve dispensação nos últimos 12 meses (2025) | Categórica | `Teve dispensação nos últimos 12 meses` | Teve/Não teve dispensação nos últimos 12 meses |
| `EmPrEP_2018` | Status em 31/12/2018: 'Em PrEP 2018' ou 'Descontinuou em 2018' | Categórica | `nan` | Vazio = usuário ainda não havia iniciado PrEP |
| `EmPrEP_2019` | Status em 31/12/2019: 'Em PrEP 2019' ou 'Descontinuou em 2019' | Categórica | `Em PrEP 2019` | Vazio = usuário ainda não havia iniciado PrEP |
| `EmPrEP_2020` | Status em 31/12/2020: 'Em PrEP 2020' ou 'Descontinuou em 2020' | Categórica | `Em PrEP 2020` | Vazio = usuário ainda não havia iniciado PrEP |
| `EmPrEP_2021` | Status em 31/12/2021: 'Em PrEP 2021' ou 'Descontinuou em 2021' | Categórica | `Em PrEP 2021` | Vazio = usuário ainda não havia iniciado PrEP |
| `EmPrEP_2022` | Status em 31/12/2022: 'Em PrEP 2022' ou 'Descontinuou em 2022' | Categórica | `nan` | Vazio = usuário ainda não havia iniciado PrEP |
| `EmPrEP_2023` | Status em 31/12/2023: 'Em PrEP 2023' ou 'Descontinuou em 2023' | Categórica | `Em PrEP 2023` | Vazio = usuário ainda não havia iniciado PrEP |
| `EmPrEP_2024` | Status em 31/12/2024: 'Em PrEP 2024' ou 'Descontinuou em 2024' | Categórica | `nan` | Vazio = usuário ainda não havia iniciado PrEP |
| `EmPrEP_2025` | Status em 31/12/2025: 'Em PrEP 2025' ou 'Descontinuou em 2025' | Categórica | `Em PrEP 2025` | Vazio = usuário ainda não havia iniciado PrEP |

### Disp_PrEP_2025.csv (dispensações) (14 colunas · 1.672.709 linhas)

| Nome da coluna | Descrição | Tipo de dado | Exemplo | Observações |
|---|---|---|---|---|
| `Cod_unificado` | Código único que identifica cada usuário(a) da PrEP | Texto | `101519956.0` | Pessoa pseudonimizada — não permite identificação |
| `codigo_udm` | Código do serviço de saúde da dispensação | Texto | `359` | Chave de ligação com a base de usuários |
| `nome_udm` | Nome do serviço de saúde da dispensação | Texto | `SAE MARIA JOSÉ ESTEVANATO - BARUERI` | — |
| `cod_ibge_udm` | Código IBGE do município do serviço | Texto | `3505708` | — |
| `dt_disp` | Data da dispensação de PrEP | Data (aaaa-mm-dd) | `2022-05-19` | Grão temporal dia a dia (2018-2025) |
| `UF_UDM` | Sigla da UF do serviço dispensador | Texto | `SP` | — |
| `regiao_UDM` | Região geográfica do serviço | Texto | `Sudeste` | — |
| `tp_servico_atendimento` | Tipo de serviço onde ocorreu o atendimento | Categórica | `Serviço Especializado` | Serviço Especializado; CTA; Atenção Primária; Privado; Extra-muros; Teleatendimento |
| `tp_esquema_prep` | Como o usuário tomou a PrEP desde a última dispensa, em média | Categórica | `None` | Diário; Sob demanda; Ambos; Eu não tomei |
| `tp_modalidade` | Modalidade de prescrição | Categórica | `None` | PrEP diária; PrEP sob demanda |
| `Publico_privado_disp` | Esfera do serviço do atendimento | Categórica | `Público` | Público; Privado (saúde suplementar) |
| `tp_profissional` | Profissional que prescreveu a última dispensação | Categórica | `Médico(a)` | Médico(a); Enfermeiro(a); Farmacêutico(a); Dentista |
| `dt_disp_min` | Data da primeira dispensação do usuário | Data (aaaa-mm-dd) | `2022-05-19` | Repete em todas as linhas do mesmo usuário |
| `dt_disp_max` | Data da última dispensação do usuário | Data (aaaa-mm-dd) | `2026-04-09` | Repete em todas as linhas do mesmo usuário |

---

*Documento gerado programaticamente a partir das bases originais (`scripts/gera_etapa1.py`).*
