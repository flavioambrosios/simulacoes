# Inventário inicial de questões ENEM (2016-2025)

Este inventário registra candidatos encontrados nos PDFs disponíveis em `_shared/ENEM`. A questão só deve ser publicada no banco depois da conferência do enunciado, alternativas, gabarito e dependência de figura.

## Questões localizadas

| Ano | Questão | Página PDF | Tema | Simulação sugerida | Figura necessária | Situação |
|---|---:|---:|---|---|---|---|
| 2017 | 130 | 14 | Circuitos, resistência interna e Lei de Ohm | `resistencia` | Não para a ideia, mas o enunciado original apresenta a situação textual | Cadastrada e publicada |
| 2018 | 128 | 13 | Prisma óptico, dispersão e reflexão | `optica-geometrica` | Sim, o esquema do prisma e do espelho é necessário | Cadastrada e publicada com `2018_128_figura_1.png` |
| 2019 | 91 | 2 | Circuitos em paralelo e queda de tensão | `resistencia` | Sim, o esquema do circuito é necessário | Catalogada no banco; página salva como `2019_91.png`; aguardando recorte |
| 2019 | 109 | 8 | Íon em campo magnético e espectrometria de massa | `espectrometro-de-massa` | Sim, a trajetória helicoidal aparece na figura | Catalogada no banco com gabarito; recorte `2019_109_recorte.png` pronto |
| 2020 | 106 | 6 | Corrente elétrica e amperímetro | `resistencia` | Sim, os esquemas de ligação são as alternativas | Página salva como `2020_106.png`; aguardando recorte |
| 2020 | 96 | 3 | Divisor de tensão com resistores | `circuitos-eletricos-dc` | Sim, o esquema do divisor é necessário | Catalogada no banco; página salva como `2020_96.png`; aguardando recorte |
| 2020 | 125 | 12 | Eletrização por atrito | `lei-de-coulomb` | Sim, a pergunta se refere a uma tirinha | Página salva como `2020_125.png`; aguardando recorte |
| 2020 | 130 | 13 | Gerador elétrico e Lei de Faraday | `lei-de-faraday-v2` | Não | Cadastrada e publicada |
| 2020 | 133 | 15 | Refrigeração, condensador e fluxo de calor | `fluxo-de-calor` | Não | Cadastrada e publicada |
| 2022 | 133 | 16 | Pilhas em série e resistência interna | `resistencia` | Não | Cadastrada e publicada |
| 2023 | 101 | 5 | Indução eletromagnética | `lei-de-faraday-v2` | Não para o conceito cobrado | Cadastrada e publicada |
| 2023 | 91 | 2 | Propagação do som em barbante | `ondas-1d` | Sim, a tirinha é necessária | Cadastrada e publicada com `2023_91_figura_1.png` |
| 2023 | 119 | 10 | Transformação isovolumétrica de gás ideal | `comportamento-dos-gases` | Sim, alternativas gráficas preparadas | Cadastrada e publicada com figuras separadas |
| 2024 | 100 | 4 | Linhas de campo elétrico e blindagem eletrostática | `lei-de-coulomb` | Sim, os esquemas A-E são indispensáveis | Recorte `2024_100_recorte.png` pronto; aguardando decisão de publicar ou redesenhar |
| 2024 | 109 | 8 | LEDs em circuito de corrente contínua | `led-e-oled` | Sim, os circuitos A-E são indispensáveis | Catalogada no banco com gabarito; recorte `2024_109_recorte.png` pronto |
| 2024 | 101 | 5 | Geração de eletricidade com chuva e grafeno | `efeito-fotoeletrico` ou nova categoria | Não confirmado para a simulação atual | Candidata, classificação pendente |
| 2025 | 104 | 6 | Movimento de elétrons em campo elétrico | `lei-de-coulomb` | Sim, as Figuras 1 e 2 são indispensáveis | Cadastrada e publicada com `2025_104_figura_1.png` e `2025_104_figura_2.png` |
| 2025 | 101 | 4 | LED azul, fotoluminescência e frequência | `led-e-oled` | Sim, gráfico e alternativas já preparados | Cadastrada e publicada com figuras separadas |

## Registros já publicados

- **ENEM 2017, questão 130**: cerca eletrificada. Foi associada à simulação `resistencia`.
- **ENEM 2023, questão 101**: fogão por indução. Foi associada à simulação `lei-de-faraday-v2`.

## Registros catalogados, mas ocultos

Os registros abaixo estão no banco com `publicado: false` porque a questão depende de uma figura que ainda não foi recuperada:

- ENEM 2020, questão 106.
- ENEM 2020, questão 125.
- ENEM 2024, questão 100.

## Observação sobre a Lei de Coulomb

Nos PDFs analisados, não apareceu até o momento uma questão textual sem figura que cobre exclusivamente a fórmula de Coulomb entre duas cargas puntiformes. Os candidatos mais próximos são a questão 100 de 2024, sobre linhas de campo, e a questão 125 de 2020, sobre eletrização por atrito. A etapa seguinte deve recuperar essas figuras ou refazer os desenhos antes de publicá-las.

## Próxima triagem

1. Conferir os gabaritos oficiais das questões candidatas.
2. Transcrever integralmente as alternativas que dependem de esquemas.
3. Separar as questões por `simulationKey`.
4. Criar variações autorais com valores diferentes, sempre marcadas como `origem: 'modelo'`.
5. Recuperar ou redesenhar somente as figuras realmente necessárias.
