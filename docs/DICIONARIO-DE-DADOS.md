# Dicionário de Dados

## Objetivo
Este documento descreve, de forma padronizada, os campos que podem ser utilizados na coleta e organização de dados do Portal das Simulações, com foco em uso pedagógico e pesquisa aplicada.

## Princípios
- Coletar o mínimo necessário.
- Evitar identificadores pessoais sempre que possível.
- Priorizar análise agregada por turma, série, atividade e período.

## Tabela de campos sugeridos

| Campo | Tipo | Exemplo | Obrigatório | Finalidade | Observação de privacidade |
|------|------|---------|-------------|------------|---------------------------|
| periodo_letivo | Texto | 2026/1 | Sim | Organizar análises temporais | Sem risco direto |
| data_atividade | Data | 2026-06-29 | Sim | Localizar aplicação | Sem risco direto |
| turma | Texto | 2A | Sim | Agregação por grupo | Usar apenas em ambiente interno |
| serie | Texto | 2º ano | Sim | Agregação por nível escolar | Sem risco direto |
| simulacao | Texto | Calorimetria | Sim | Identificar atividade | Sem risco direto |
| topico_fisica | Texto | Termologia | Sim | Classificação pedagógica | Sem risco direto |
| total_participantes | Inteiro | 32 | Sim | Medir adesão | Dado agregado |
| total_concluintes | Inteiro | 27 | Sim | Medir conclusão | Dado agregado |
| taxa_conclusao | Decimal | 84.4 | Sim | Indicador de processo | Derivado de dados agregados |
| media_acertos_objetivas | Decimal | 7.3 | Sim | Indicador de desempenho | Dado agregado |
| desvio_padrao_objetivas | Decimal | 1.2 | Não | Variabilidade do grupo | Dado agregado |
| media_rubrica_discursiva | Decimal | 6.8 | Não | Indicador qualitativo agregado | Dado agregado |
| observacoes_docente | Texto | Dificuldade com interpretação de gráfico | Não | Registro pedagógico | Evitar nomes de estudantes |
| versao_simulacao | Texto | v2026.06 | Não | Rastrear mudanças | Sem risco direto |
| tempo_medio_interacao | Decimal | 18.5 | Não | Analisar engajamento | Preferir sempre em nível agregado |

## Campos a evitar em base principal de análise

- Nome completo do estudante.
- E-mail pessoal.
- Telefone.
- Matrícula.
- CPF ou qualquer identificador civil.
- Texto livre que mencione explicitamente nomes de colegas ou professores.

## Regras de uso

1. A base principal de análise deve operar preferencialmente com dados agregados.
2. Caso um campo identificável seja necessário em etapa operacional, ele deve ser removido antes de análises externas.
3. Publicações, relatórios e apresentações devem usar apenas dados anonimizados ou agregados.
4. Turmas muito pequenas devem ser tratadas com cautela para evitar reidentificação indireta.

## Versionamento

- Versão inicial: 1.0
- Data: 29/06/2026
