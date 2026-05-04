# Backend de Notas com IA

Este módulo em Python faz quatro tarefas:

1. Lê um CSV com as colunas estudante, turma, simulacao, nota, conclusao.
2. Usa heurísticas locais e uma API de IA para avaliar a conclusão.
3. Salva tudo em banco SQLite e, se você quiser, também em um CSV de saída.
4. Calcula média geral do aluno integrando nota da simulação e nota da conclusão.

Agora ele também inclui um módulo consolidado de notas bimestrais para avaliações, simulações, experiências e outras notas.

## Estrutura esperada do CSV

Exemplo de cabeçalho:

```csv
estudante,turma,simulacao,nota,conclusao
Ana Silva,3o ano E,Espectrômetro de Massa,8.5,"Percebi que o aumento do campo magnético altera a trajetória..."
```

## Onde colocar a chave da API

1. Copie o arquivo .env.example para .env.
2. Edite o arquivo .env.
3. Preencha AI_API_KEY com a sua chave.

Exemplo:

```env
AI_PROVIDER=openai
AI_API_KEY=SUA_CHAVE_AQUI
AI_MODEL=gpt-4o-mini
```

Se preferir Gemini:

```env
AI_PROVIDER=gemini
AI_API_KEY=SUA_CHAVE_AQUI
AI_MODEL=gemini-2.0-flash
```

## Como instalar

No terminal, dentro desta pasta:

```powershell
pip install -r requirements.txt
```

## Como avaliar um CSV

```powershell
python main.py evaluate .\seu_arquivo.csv --output-csv .\resultados_conclusoes.csv
```

Resultado:

- Banco SQLite: notas.db
- CSV de saída: resultados_conclusoes.csv

## Como calcular a média geral do aluno

```powershell
python main.py student-average "ANA BEATRIZ DE OLIVEIRA DA SILVA" --turma "3o ano E"
```

## Como exportar lista de alunos para usar nas simulações

```powershell
python main.py list-students --output-csv .\alunos_cadastrados.csv
```

Ou por turma:

```powershell
python main.py list-students --turma "3o ano E" --output-csv .\alunos_3o_ano_E.csv
```

## Como a nota da conclusão é calculada

- Número de palavras: 10%
- Coerência: 30%
- Originalidade: 30%
- Significância: 30%

Fórmula:

```text
nota_final = 0.10*palavras + 0.30*coerencia + 0.30*originalidade + 0.30*significancia
```

## Como a média geral do aluno é calculada

Para cada registro de simulação:

- se existir nota da conclusão, a nota integrada da atividade é a média entre nota da simulação e nota da conclusão;
- se ainda não existir conclusão avaliada, vale apenas a nota da simulação.

Depois, a média geral do aluno é a média dessas notas integradas.

## Observação prática

Esse banco SQLite já pode servir de base para suas futuras simulações. Cada simulação em HTML ou Python pode consultar a tabela students para montar a lista de nomes por turma e depois gravar as notas em simulation_records.

## Módulo consolidado do bimestre

O banco agora possui duas tabelas novas:

- gradebook_items: define cada componente do bimestre, como avaliação, experiência, simulação ou outra nota.
- gradebook_scores: guarda a nota de cada aluno em cada componente.

### CSV de componentes

Use um CSV com pelo menos:

```csv
categoria,atividade,bimestre,recuperacao,peso,nota_maxima,turma,origem
avaliacao,Avaliação Bimestral - Educação Digital,1o bimestre,nao,2,10,3o ano E,manual
experiencia,Experiência 1,1o bimestre,nao,1,10,3o ano E,manual
outra,Gincana,1o bimestre,nao,1,10,3o ano E,manual
```

Importação:

```powershell
python main.py gradebook-import-items .\componentes_bimestre.csv
```

### CSV de notas

Use um CSV com pelo menos:

```csv
estudante,turma,categoria,atividade,nota,bimestre,recuperacao,peso,nota_maxima,observacoes,origem
ANA BEATRIZ DE OLIVEIRA DA SILVA,3o ano E,avaliacao,Avaliação Bimestral - Educação Digital,8.5,1o bimestre,nao,2,10,prova objetiva,manual
```

Importação:

```powershell
python main.py gradebook-import-scores .\notas_bimestre.csv
```

### Sincronizar simulações já avaliadas

As simulações registradas em simulation_records podem ser levadas para o módulo consolidado com nota integrada.

```powershell
python main.py gradebook-sync-simulations --bimestre "1o bimestre"
```

### Relatório consolidado do bimestre

```powershell
python main.py gradebook-report --bimestre "1o bimestre" --output-csv .\relatorio_bimestral.csv
```

Por turma:

```powershell
python main.py gradebook-report --bimestre "1o bimestre" --turma "3o ano E" --output-csv .\relatorio_3o_ano_E.csv
```

### Resumo consolidado de um estudante

```powershell
python main.py gradebook-student-summary "ANA BEATRIZ DE OLIVEIRA DA SILVA" --bimestre "1o bimestre" --turma "3o ano E"
```

Esse resumo devolve:

- média geral bimestral normalizada em escala 0-10;
- médias por categoria, como avaliacao, simulacao, experiencia e outra;
- quantidade de lançamentos usados no cálculo.
