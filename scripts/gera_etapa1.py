"""Gera docs/entregas/etapa1_definicao_do_projeto.md a partir das bases 2025."""
import csv
import os

D = os.path.join(os.path.dirname(__file__), "..", "dados", "2025") + os.sep


def primeira_linha(path):
    with open(D + path, encoding="utf-8-sig") as f:
        r = csv.DictReader(f, delimiter=";")
        row = next(r)
    return {k: (v or "").strip() for k, v in row.items()}, r.fieldnames


ex_u, cols_u = primeira_linha("Banco_PrEP_2025.csv")
ex_d, cols_d = primeira_linha("Disp_PrEP_2025.csv")

defstatus = "Status em 31/12/{a}: 'Em PrEP {a}' ou 'Descontinuou em {a}'"

dic_u = {
    "Cod_unificado": ("Código único que identifica cada usuário(a) da PrEP", "Texto", "Pessoa pseudonimizada — não permite identificação"),
    "raca": ("Raça/cor autodeclarada", "Categórica", "Indígena, Preta, Parda, Branca, Amarela, Ignorada/Não informada"),
    "escolaridade": ("Escolaridade em anos de estudo", "Categórica", "Nenhuma/Sem educação formal; 1-3; 4-7; 8-11; 12 ou mais anos; Ignorada"),
    "fetar": ("Faixa etária no momento da última dispensação", "Categórica", "<18, 18-24, 25-29, 30-39, 40-49, 50 e mais"),
    "Pop_genero_pratica": ("População-chave (gênero/prática sexual)", "Categórica", "Gays e outros HSH cis; Mulheres cis; Homens heterossexuais cis; Mulheres trans; Homens trans; Não bináries; Travestis"),
    "codigo_udm": ("Código do serviço de saúde da última dispensação (UDM)", "Texto", "Chave de ligação com a base de dispensas"),
    "nome_udm": ("Nome do serviço de saúde da última dispensação", "Texto", ""),
    "cod_ibge_udm": ("Código IBGE do município do serviço", "Texto", "Permite ligar com tabela de municípios IBGE"),
    "UF_UDM": ("Sigla da Unidade Federada do serviço", "Texto", ""),
    "regiao_UDM": ("Região geográfica do serviço", "Texto", ""),
    "dt_disp_min": ("Data da primeira dispensação de PrEP do usuário", "Data (aaaa-mm-dd)", "Base para calcular 'novos usuários' por ano"),
    "dt_disp_max": ("Data da última dispensação de PrEP do usuário", "Data (aaaa-mm-dd)", ""),
    "st_habitantes_fronteira": ("Se a pessoa era habitante de fronteira no cadastro", "Categórica (Sim/Não)", "Novo na versão 2025"),
    "st_droga_injetavel": ("Uso de droga injetável ou slam nos últimos 3 meses", "Categórica (Sim/Não)", "Novo na versão 2025"),
    "st_substancias_psicoativas": ("Uso de substâncias psicoativas antes/durante sexo (chemsex), últimos 3 meses", "Categórica (Sim/Não)", "Novo na versão 2025"),
    "tp_servico_atendimento": ("Tipo de serviço onde ocorreu o atendimento", "Categórica", "Serviço Especializado; CTA; Atenção Primária; Privado; Extra-muros; Teleatendimento"),
    "tp_profissional": ("Profissional que prescreveu a última dispensação", "Categórica", "Médico(a); Enfermeiro(a); Farmacêutico(a); Dentista"),
    "IST_autorrelato": ("Relato de sinal/sintoma ou diagnóstico de IST na última dispensação", "Categórica", "Nenhuma IST autorrelatada; Alguma IST autorrelatada"),
    "st_populacao_rua": ("Situação de rua no momento do cadastro", "Categórica (Sim/Não)", ""),
    "st_privada_liberdade": ("Pessoa privada de liberdade no momento do cadastro", "Categórica (Sim/Não)", ""),
    "Pop_prof_sexo": ("Trocou sexo por dinheiro/bens/serviços nos últimos 3 meses", "Categórica (Sim/Não)", ""),
    "Pop_plan_rep": ("Uso da PrEP relacionado a planejamento reprodutivo", "Categórica (Sim/Não)", ""),
    "Pop_gestante": ("Uso da PrEP relacionado à gestação", "Categórica", "Sim; Não; Não se aplica"),
    "Pop_amamentacao": ("Uso da PrEP relacionado à amamentação", "Categórica (Sim/Não)", ""),
    "teve_dispensa": ("Se a pessoa teve dispensação (Sim) ou apenas cadastro (Não)", "Categórica (Sim/Não)", ""),
    "Disp_Ultimos_12m": ("Se teve dispensação nos últimos 12 meses (2025)", "Categórica", "Teve/Não teve dispensação nos últimos 12 meses"),
}
for a in range(2018, 2026):
    dic_u["EmPrEP_%d" % a] = (defstatus.format(a=a), "Categórica", "Vazio = usuário ainda não havia iniciado PrEP")

dic_d = {
    "Cod_unificado": dic_u["Cod_unificado"],
    "codigo_udm": ("Código do serviço de saúde da dispensação", "Texto", "Chave de ligação com a base de usuários"),
    "nome_udm": ("Nome do serviço de saúde da dispensação", "Texto", ""),
    "cod_ibge_udm": ("Código IBGE do município do serviço", "Texto", ""),
    "dt_disp": ("Data da dispensação de PrEP", "Data (aaaa-mm-dd)", "Grão temporal dia a dia (2018-2025)"),
    "UF_UDM": ("Sigla da UF do serviço dispensador", "Texto", ""),
    "regiao_UDM": ("Região geográfica do serviço", "Texto", ""),
    "tp_servico_atendimento": dic_u["tp_servico_atendimento"],
    "tp_esquema_prep": ("Como o usuário tomou a PrEP desde a última dispensa, em média", "Categórica", "Diário; Sob demanda; Ambos; Eu não tomei"),
    "tp_modalidade": ("Modalidade de prescrição", "Categórica", "PrEP diária; PrEP sob demanda"),
    "Publico_privado_disp": ("Esfera do serviço do atendimento", "Categórica", "Público; Privado (saúde suplementar)"),
    "tp_profissional": dic_u["tp_profissional"],
    "dt_disp_min": ("Data da primeira dispensação do usuário", "Data (aaaa-mm-dd)", "Repete em todas as linhas do mesmo usuário"),
    "dt_disp_max": ("Data da última dispensação do usuário", "Data (aaaa-mm-dd)", "Repete em todas as linhas do mesmo usuário"),
}


def tabela(nome_arquivo, cols, dic, exemplos, linhas):
    out = [
        "\n### %s (%d colunas · %s linhas)\n" % (nome_arquivo, len(cols), format(linhas, ",").replace(",", ".")),
        "| Nome da coluna | Descrição | Tipo de dado | Exemplo | Observações |",
        "|---|---|---|---|---|",
    ]
    for c in cols:
        desc, tipo, obs = dic[c]
        ex = (exemplos.get(c) or "—")[:40].replace("|", "/")
        ex = "`%s`" % ex if ex != "—" else "—"
        obs = obs or "—"
        out.append("| `%s` | %s | %s | %s | %s |" % (c, desc, tipo, ex, obs))
    return "\n".join(out)


doc = """# Etapa 1 — Definição do projeto (BDII 2026.2)

**Título do projeto:** Painel de Business Intelligence do Programa PrEP no Brasil —
quem usa, como acessa e quem permanece (2018–2025)

**Integrante:** Emanoel Raiff Gomes da Nóbrega Filho (matrícula 20221350010)

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
| Linhas × colunas | {linhas_u} linhas × {cols_u_n} colunas | {linhas_d} linhas × {cols_d_n} colunas |
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
{tab_u}
{tab_d}

---

*Documento gerado programaticamente a partir das bases originais (`scripts/gera_etapa1.py`).*
""".format(
    linhas_u="332.976",
    cols_u_n=len(cols_u),
    linhas_d="1.672.709",
    cols_d_n=len(cols_d),
    tab_u=tabela("Banco_PrEP_2025.csv (usuários)", cols_u, dic_u, ex_u, 332976),
    tab_d=tabela("Disp_PrEP_2025.csv (dispensações)", cols_d, dic_d, ex_d, 1672709),
)

saida = os.path.join(os.path.dirname(__file__), "..", "docs", "entregas", "etapa1_definicao_do_projeto.md")
with open(saida, "w", encoding="utf-8") as f:
    f.write(doc)
print("OK — etapa1 gerado:", os.path.abspath(saida))
print("colunas usuarios:", len(cols_u), "| colunas dispensas:", len(cols_d))
