// ==================================================================
// PARTE 1 - FUNÇÕES ORIGINAIS (RECEBIMENTO DE DADOS DAS SIMULAÇÕES)
// ==================================================================

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    
    // O envio de confirmação de e-mail foi removido deste script.
    // O script de notas já cuida do envio de e-mail.
    
    // Código existente para salvar na planilha...
    const sheet = SpreadsheetApp.openById('1WjP-ezybLQ2wyk_lZriLlByMPiH9d0I3otdfNjM5UVQ').getActiveSheet();
    
    // Validar os dados para evitar campos undefined
    const rowData = [
      data.timestamp || '',
      data.serie || '',
      data.turma || '',
      data.estudante || '',
      data.simulacao || '',
      data.questoes_puladas || '',
      data.acertos_erros || '',
      data.nota || '',
      data.conclusao || '',
      data.criticas || '',
      data.sugestoes || '',
      data.email || ''
    ];
    
    sheet.appendRow(rowData);
    
    return ContentService.createTextOutput(JSON.stringify({status: 'success'})).setMimetype(ContentService.MimeType.JSON);
    
  } catch (error) {
    // Log do erro para depuração
    console.error('Erro no doPost: ', error);
    return ContentService.createTextOutput(JSON.stringify({status: 'error', message: error.toString()})).setMimetype(ContentService.MimeType.JSON);
  }
}

/// ==================================================================
// PARTE 2 - FUNÇÃO PARA ORGANIZAR ALUNOS POR TURMA (VERSÃO CORRIGIDA)
// ==================================================================

function organizarAlunosPorTurma() {
  // CONFIGURAÇÕES
  const ID_PLANILHA_FONTE = '1WjP-ezybLQ2wyk_lZriLlByMPiH9d0I3otdfNjM5UVQ';
  const NOME_ABA_FONTE = null;
  const PRIMEIRA_LINHA_EH_CABECALHO = true;
  
  const COLUNA_SERIE = 1;       // coluna B
  const COLUNA_TURMA_LETRA = 2; // coluna C
  
  const NOME_PLANILHA_DESTINO = "📚 Alunos por Turma";
  
  try {
    // Acessar a planilha fonte
    const planilhaFonte = SpreadsheetApp.openById(ID_PLANILHA_FONTE);
    let abaFonte = NOME_ABA_FONTE ? planilhaFonte.getSheetByName(NOME_ABA_FONTE) : planilhaFonte.getActiveSheet();
    if (!abaFonte) throw new Error("Aba não encontrada.");
    
    let dados = abaFonte.getDataRange().getValues();
    if (dados.length === 0) {
      SpreadsheetApp.getUi().alert("Nenhum dado encontrado.");
      return;
    }
    
    const cabecalho = PRIMEIRA_LINHA_EH_CABECALHO ? dados[0] : null;
    const linhas = PRIMEIRA_LINHA_EH_CABECALHO ? dados.slice(1) : dados;
    
    // Agrupar por turma
    const turmasMap = new Map();
    
    for (let i = 0; i < linhas.length; i++) {
      const linha = linhas[i];
      let serieRaw = linha[COLUNA_SERIE]?.toString().trim() || "";
      let letraRaw = linha[COLUNA_TURMA_LETRA]?.toString().trim() || "";
      
      serieRaw = serieRaw.replace(/º/g, "o").replace(/\./g, "");
      letraRaw = letraRaw.toUpperCase().trim();
      
      if (serieRaw === "" || letraRaw === "") continue;
      
      const turma = `${serieRaw} ${letraRaw}`;
      if (!turmasMap.has(turma)) turmasMap.set(turma, []);
      turmasMap.get(turma).push(linha);
    }
    
    if (turmasMap.size === 0) {
      SpreadsheetApp.getUi().alert("Nenhuma turma identificada.");
      return;
    }
    
    // Criar ou obter planilha destino
    let planilhaDestino;
    let isNovaPlanilha = false;
    
    const arquivos = DriveApp.getFilesByName(NOME_PLANILHA_DESTINO);
    if (arquivos.hasNext()) {
      planilhaDestino = SpreadsheetApp.openById(arquivos.next().getId());
      isNovaPlanilha = false;
    } else {
      planilhaDestino = SpreadsheetApp.create(NOME_PLANILHA_DESTINO);
      isNovaPlanilha = true;
    }
    
    // Obter abas existentes
    const abasExistentes = planilhaDestino.getSheets();
    const nomesAbasExistentes = abasExistentes.map(aba => aba.getName());
    const nomesTurmas = Array.from(turmasMap.keys());
    
    // 1. Criar as abas necessárias
    for (let turma of nomesTurmas) {
      if (!nomesAbasExistentes.includes(turma)) {
        planilhaDestino.insertSheet(turma);
      }
    }
    
    // 2. Remover abas que não são turmas (protegendo a última aba)
    for (let aba of abasExistentes) {
      const nomeAba = aba.getName();
      if (!nomesTurmas.includes(nomeAba) && nomeAba !== "Sheet1") {
        if (planilhaDestino.getSheets().length > 1) {
          planilhaDestino.deleteSheet(aba);
        }
      }
    }
    
    // 3. Preencher cada aba da turma com os dados
    for (let [turma, linhasTurma] of turmasMap.entries()) {
      let aba = planilhaDestino.getSheetByName(turma);
      if (!aba) continue;
      
      // Limpar a aba completamente
      aba.clear();
      
      // Escrever cabeçalho (se houver)
      let linhaAtual = 1;
      if (cabecalho) {
        aba.getRange(linhaAtual, 1, 1, cabecalho.length).setValues([cabecalho]);
        linhaAtual++;
      }
      
      // Escrever os dados
      if (linhasTurma.length > 0) {
        aba.getRange(linhaAtual, 1, linhasTurma.length, linhasTurma[0].length).setValues(linhasTurma);
      }
      
      // APLICAR FORMATO DE DATA/HORA NA COLUNA A (TIMESTAMP)
      if (linhasTurma.length > 0) {
        const ultimaLinhaDados = linhaAtual + linhasTurma.length - 1;
        // Verifica se a coluna A existe e tem dados
        if (ultimaLinhaDados >= linhaAtual) {
          const rangeData = aba.getRange(linhaAtual, 1, linhasTurma.length, 1);
          rangeData.setNumberFormat("dd/mm/yyyy hh:mm:ss");
        }
      }
      
      // Ajustar largura das colunas
      const numColunas = cabecalho ? cabecalho.length : (linhasTurma[0]?.length || 1);
      aba.autoResizeColumns(1, numColunas);
    }
    
    // 4. Tentar remover a aba "Sheet1" se existir e se houver outras abas
    const abaPadrao = planilhaDestino.getSheetByName("Sheet1");
    if (abaPadrao && planilhaDestino.getSheets().length > 1) {
      try {
        planilhaDestino.deleteSheet(abaPadrao);
      } catch (e) {
        // Ignora - não é crítico
      }
    }
    
    // Mensagem de sucesso
    const url = planilhaDestino.getUrl();
    const mensagem = isNovaPlanilha ? "✅ Planilha CRIADA" : "✅ Planilha ATUALIZADA";
    SpreadsheetApp.getUi().alert(mensagem + " com sucesso!\n\n" + 
      turmasMap.size + " turmas organizadas.\n" +
      "Link: " + url);
    
  } catch (error) {
    SpreadsheetApp.getUi().alert("❌ Erro: " + error.message);
    console.error("Erro: ", error);
  }
}

// ==================================================================
// PARTE 3 - MENU PERSONALIZADO NA PLANILHA
// ==================================================================

function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('📂 Organizar turmas')
    .addItem('Atualizar planilha com turmas separadas', 'organizarAlunosPorTurma')
    .addToUi();
}