# PROPOSTA DE PROJETO PEDAGÓGICO

## CLUBE DE ROBÓTICA: Projeto Humanoide (Ciclo de 3 Anos)

**Destinado a:** Direção Escolar e Coordenação Pedagógica  
**Responsável pelo Projeto:** [Seu Nome / Disciplina]  
**Público-alvo:** Alunos do Ensino Médio  
**Carga de dedicação:** 2 a 4 horas semanais por aluno  
**Calendário:** 4 bimestres por ano, com 6 semanas efetivas por bimestre  

---

### 1. JUSTIFICATIVA PEDAGÓGICA

O avanço tecnológico exige que a escola atue além da teoria. O **Clube de Robótica** propõe a metodologia **STEAM** (*Science, Technology, Engineering, Arts, and Mathematics*) por meio de um desafio de engenharia de longo prazo: o desenvolvimento de um **robô humanoide de aproximadamente 35 cm**.

Ao contrário de kits educacionais prontos, o projeto desafiará os alunos a desenhar peças no computador, fabricá-las em impressora 3D, montar a eletrônica e programar o robô. O trabalho sequencial pode aumentar o engajamento, desenvolver colaboração, pensamento crítico, resolução de problemas e preparação para desafios técnicos e acadêmicos.

Cada ano terá aproximadamente 24 semanas efetivas, ou 48 a 96 horas de dedicação por aluno. As equipes trabalharão com divisão de funções, documentação e revezamento, permitindo que estudantes com diferentes interesses contribuam em mecânica, eletrônica, programação, comunicação e testes.

---

### 2. ESCOPO TÉCNICO E PREMISSAS

Após análise inicial de viabilidade, optou-se pela escala de **30 a 45 cm**, utilizando servomotores seriais:

* **Custo-benefício:** Robôs maiores exigiriam motores e estruturas mais caros. A escala de 35 cm permite o uso de servos de torque elevado e componentes educacionais.
* **Segurança e logística:** O protótipo deverá ser leve, com massa estimada de até 2 kg, e seus testes ocorrerão em área delimitada, com supervisão.
* **Fabricação:** As peças estruturais serão produzidas em uma impressora 3D FDM, inicialmente com PLA e, quando necessário, PETG.
* **Desenvolvimento incremental:** Antes do robô completo, serão feitos protótipos de articulações, módulos de perna e testes de bancada.
* **Meta de visão computacional:** A primeira aplicação será a identificação de cores, marcadores ou objetos definidos pela equipe. Reconhecimento facial não fará parte da meta padrão, devido a questões de privacidade e proteção de dados de estudantes.

---

### 3. METODOLOGIA E ORGANIZAÇÃO DAS EQUIPES

As equipes terão entre 3 e 5 alunos, conforme o número de participantes, com funções que poderão ser alternadas:

* **Mecânica e CAD:** modelagem, tolerâncias, montagem e fabricação das peças;
* **Eletrônica e energia:** alimentação, conexões, servos, sensores e testes elétricos;
* **Programação e controle:** firmware, controle de movimento, leitura de sensores e visão computacional;
* **Documentação e comunicação:** diário de bordo, versionamento, relatórios, apresentação e registro dos testes.

Cada equipe manterá um diário de bordo e um repositório com arquivos CAD, código, esquemas, lista de materiais, resultados de testes e decisões técnicas. Ao final de cada bimestre haverá uma demonstração ou entrega verificável.

---

### 4. CRONOGRAMA DE EXECUÇÃO

#### Ano 1: Fundamentos de engenharia e estrutura inferior

| Bimestre | Conteúdos e atividades | Entrega verificável |
| :---: | :--- | :--- |
| 1º | Segurança, organização do laboratório, introdução ao CAD, eletricidade básica e programação com ESP32. | Projeto CAD simples, ficha de segurança e circuito de teste. |
| 2º | Impressão 3D, tolerâncias, montagem mecânica, servos e controle de uma articulação. | Peça funcional impressa e bancada de teste documentada. |
| 3º | Projeto das pernas, distribuição de massa, alimentação e controle coordenado de servos. | Protótipo de perna e sequência de movimentos reproduzível. |
| 4º | Montagem da estrutura inferior, testes de estabilidade e correção de falhas. | Cintura para baixo capaz de permanecer em pé com apoio e executar passos guiados. |

#### Ano 2: Integração mecatrônica e estabilização

| Bimestre | Conteúdos e atividades | Entrega verificável |
| :---: | :--- | :--- |
| 1º | Projeto e fabricação do tronco, braços e cabeça; revisão das peças do Ano 1. | Estrutura superior montada e lista de peças revisada. |
| 2º | Integração dos servos, organização dos cabos, bateria, proteção e testes de consumo. | Robô montado com checklist elétrico e de segurança. |
| 3º | IMU, orientação, calibração e controle de equilíbrio em ambiente controlado. | Dados de sensores registrados e rotina básica de correção. |
| 4º | Integração e testes de caminhada em percurso delimitado. | Robô caminhando pequena distância com supervisão e documentação dos limites. |

#### Ano 3: Autonomia e visão computacional

| Bimestre | Conteúdos e atividades | Entrega verificável |
| :---: | :--- | :--- |
| 1º | Raspberry Pi, Python, comunicação com o microcontrolador e gerenciamento de energia. | Comunicação estável entre computador e controlador. |
| 2º | Câmera, processamento de imagens e identificação de cores, marcadores ou objetos simples. | Demonstração de identificação em condições controladas. |
| 3º | Desvio de obstáculos, integração de sensores e planejamento de testes. | Percurso autônomo curto, com critérios de sucesso definidos. |
| 4º | Validação, melhorias, relatório final e preparação para feira de ciências. | Protótipo demonstrável, código documentado e apresentação final. |

As metas são progressivas: caso uma etapa exija mais tempo, a equipe priorizará segurança, estabilidade e documentação antes de avançar para novas funcionalidades.

---

### 5. FERRAMENTAS, EQUIPAMENTOS E INSUMOS

Além dos componentes do robô, são imprescindíveis:

* **Impressora 3D FDM**, com mesa aquecida, bico de reposição e materiais PLA/PETG;
* computador para CAD, fatiamento, programação e documentação;
* paquímetro, régua, esquadros, jogo de chaves Allen, chaves de precisão e alicates;
* estação de solda com suporte, estanho, sugador ou malha dessoldadora, fluxo e exaustão adequada;
* multímetro, fonte de bancada com limitação de corrente, protoboards, cabos, conectores, termorretráteis, abraçadeiras e organizadores;
* alicate desencapador, alicate de crimpar e kit de terminais;
* óculos de proteção, tapetes antiestáticos, luvas adequadas para manuseio, armário para componentes e sinalização da área de testes;
* peças sobressalentes, fusíveis, parafusos, porcas, rolamentos, filamentos e componentes eletrônicos de reposição.

A impressora 3D e a estação de eletrônica serão utilizadas somente com treinamento e supervisão. A escola deverá verificar ventilação, instalação elétrica, manutenção e regras do fabricante antes do uso.

---

### 6. SEGURANÇA, PRIVACIDADE E GESTÃO DE RISCOS

Antes das atividades práticas, os alunos receberão orientação sobre ferramentas, partes móveis, eletricidade, soldagem, impressão 3D e armazenamento de baterias. Os testes do robô ocorrerão em área livre, delimitada e sob supervisão de um responsável.

Baterias LiPo deverão ser carregadas apenas com carregador compatível, em recipiente apropriado e nunca sem supervisão. Também serão adotados procedimentos para inspeção, armazenamento, transporte e descarte. Haverá desligamento de emergência e checklist antes de cada teste.

O uso de câmera deverá respeitar a autorização da escola e as regras de proteção de dados. A preferência será por reconhecimento de cores, marcadores e objetos, sem armazenamento de imagens de estudantes. Qualquer atividade que envolva pessoas identificáveis dependerá de avaliação institucional e autorizações específicas.

---

### 7. ORÇAMENTO ESTIMADO E INVESTIMENTO DILUÍDO

O investimento será fracionado por ano letivo e inclui uma reserva aproximada de 15% para reposição, manutenção e variação de preços. Os valores são estimativas e devem ser atualizados por meio de pelo menos três cotações antes da compra. O orçamento abaixo considera um protótipo principal e não inclui reformas estruturais do laboratório.

| Ano letivo | Foco da aquisição | Itens principais | Custo estimado |
| :---: | :--- | :--- | :--- |
| **Ano 1** | Laboratório, fabricação e pernas | Impressora 3D FDM, filamentos, ferramentas mecânicas, estação de solda, multímetro, fonte de bancada, 10 servos seriais, controladora, ESP32, parafusos e peças de reposição. | **R$ 5.000,00 a R$ 7.000,00** |
| **Ano 2** | Tronco, braços e energia | 8 servos adicionais, sensor IMU, bateria LiPo, carregador compatível, conectores, proteção elétrica, materiais estruturais e reposições. | **R$ 1.800,00 a R$ 2.500,00** |
| **Ano 3** | Cérebro e autonomia | Raspberry Pi, cartão SD de alta velocidade, câmera, sensores de distância, iluminação ou marcadores para testes e peças de reposição. | **R$ 1.000,00 a R$ 1.500,00** |
| **TOTAL** | **Projeto completo (3 anos)** | **Equipamentos, ferramentas, hardware, insumos, segurança e reserva de manutenção.** | **R$ 7.800,00 a R$ 11.000,00** |

*Nota: os valores dependem do modelo da impressora, da marca dos servomotores, da disponibilidade nacional e de eventuais taxas de importação. Equipamentos adquiridos no Ano 1 permanecerão disponíveis para as turmas seguintes.*

---

### 8. AVALIAÇÃO E INDICADORES DE SUCESSO

O acompanhamento será formativo e baseado em evidências. Serão considerados:

1. participação, colaboração e alternância de funções;
2. qualidade do diário de bordo, dos relatórios e da documentação técnica;
3. quantidade e qualidade dos protótipos testados, sem considerar apenas o sucesso final;
4. estabilidade do robô, distância percorrida sem intervenção e repetibilidade dos movimentos;
5. taxa de acerto na identificação de cores, marcadores ou objetos;
6. cumprimento dos procedimentos de segurança;
7. capacidade de explicar decisões, erros, melhorias e limitações do projeto.

---

### 9. CONTINUIDADE E RESULTADOS ESPERADOS

Para garantir a continuidade entre turmas, cada ano terminará com inventário, revisão do código, cópia dos arquivos, relatório técnico e uma sessão de transmissão de conhecimento para os próximos participantes. Alunos veteranos poderão atuar como monitores, sempre sob supervisão do responsável.

Espera-se que o projeto:

1. gere um protótipo demonstrável para feiras de ciências locais e mostras de robótica, como a MNR ou a OBR;
2. produza documentação e materiais de divulgação institucional, respeitando autorizações de imagem;
3. amplie o contato dos estudantes com possibilidades acadêmicas e profissionais em ciência, tecnologia e engenharia;
4. desenvolva competências de planejamento, comunicação, trabalho em equipe, programação, fabricação e resolução de problemas.
