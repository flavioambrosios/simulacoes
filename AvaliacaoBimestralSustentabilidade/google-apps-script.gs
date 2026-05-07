const SPREADSHEET_ID = '1SgAsDYqCKlz2Kel0_dmbdMEf9pmCz2mDVQHJwV2kIZk';
const HISTORY_SHEET_NAME = 'Historico Avaliacoes';
const DEFAULT_SCORE_HEADER = 'prova';
const SCRIPT_VERSION = '2026-05-05-b';
const MODELO_ABA_NOME = '2o ano A';
const LINHA_CABECALHO = 1;
const LINHA_INICIO_ALUNOS = 2;
const SCHOOL_NAME = 'CEAN - Centro de Ensino Médio Asa Norte';
const TEACHER_NAME = 'Prof. Flávio Ambrósio';
const TERM_BASE_COLUMNS = ['J', 'N', 'R', 'V'];
const TERM_ORDER = ['1o', '2o', '3o', '4o'];
const TERM_START_COLUMNS_PROPERTY = 'TERM_START_COLUMNS_MAP';
const TERM_START_COLUMNS = {
  '1o': 'J',
  '2o': 'N',
  '3o': 'R',
  '4o': 'V'
};

function doGet(e) {
  if (e && e.parameter && e.parameter.action === 'students') {
    return jsonResponse({
      status: 'ok',
      version: SCRIPT_VERSION,
      studentDatabase: buildStudentDatabase(getManagedSpreadsheet())
    });
  }

  return jsonResponse({
    status: 'ok',
    message: 'Apps Script de notas ativo.',
    version: SCRIPT_VERSION,
    hasDoPost: true,
    spreadsheetId: SPREADSHEET_ID,
    historySheet: HISTORY_SHEET_NAME,
    defaultScoreHeader: DEFAULT_SCORE_HEADER
  });
}

function doPost(e) {
  try {
    const payload = parsePayload(e);

    if (payload.action === 'addStudent') {
      validateStudentPayload(payload);
      const spreadsheet = getManagedSpreadsheet();
      const targetSheet = findTargetSheet(spreadsheet, payload);
      const studentRow = findOrCreateStudentRow(targetSheet, payload.estudante);

      appendHistory(spreadsheet, {
        avaliacao: 'Cadastro de estudante',
        atividade: 'Cadastro manual ou remoto de estudante',
        categoria: 'cadastro_aluno',
        serie: payload.serie || '',
        turma: payload.turma || '',
        trilha: payload.trilha || '',
        sheetName: targetSheet.getName(),
        estudante: payload.estudante,
        estudanteDigitado: payload.estudante,
        nota: '',
        payloadOriginal: payload
      });

      return jsonResponse({ status: 'success', action: 'addStudent', sheet: targetSheet.getName(), row: studentRow });
    }

    validatePayload(payload);

    const spreadsheet = getManagedSpreadsheet();
    const targetSheet = findTargetSheet(spreadsheet, payload);
    const scoreColumn = resolveScoreColumn(targetSheet, payload);
    const studentRow = findOrCreateStudentRow(targetSheet, payload.estudante);

    targetSheet.getRange(studentRow, scoreColumn).setValue(payload.nota || 0);

    appendHistory(spreadsheet, {
      avaliacao: payload.avaliacao || 'Avaliação Bimestral - Educação Digital',
      atividade: payload.atividade || payload.simulacao || '',
      categoria: payload.categoria || '',
      serie: payload.serie || '',
      turma: payload.turma || '',
      bimestre: payload.bimestre || '',
      recuperacao: payload.recuperacao ? 'sim' : 'nao',
      trilha: payload.trilha || '',
      sheetName: payload.sheetName || targetSheet.getName(),
      scoreHeader: buildScoreHeader(payload),
      colunaDestino: columnToLetter(scoreColumn),
      estudante: payload.estudante || '',
      estudanteDigitado: payload.estudanteDigitado || '',
      nota: payload.nota || 0,
      notaPercentual: payload.notaPercentual || '',
      paresCorretos: payload.paresCorretos || 0,
      totalPares: payload.totalPares || 0,
      acertosIndividuais: payload.acertosIndividuais || 0,
      totalQuestoes: payload.totalQuestoes || 0,
      questoesPuladas: payload.questoes_puladas || '',
      conclusao: payload.conclusao || '',
      criticas: payload.criticas || '',
      sugestoes: payload.sugestoes || '',
      email: payload.email || '',
      respostas: payload.respostas || [],
      payloadOriginal: payload
    });

    const emailStatus = sendConfirmationEmailIfPossible(payload);

    return jsonResponse({ status: 'success', sheet: targetSheet.getName(), row: studentRow, emailStatus: emailStatus });
  } catch (error) {
    return jsonResponse({ status: 'error', message: formatRuntimeError(error) });
  }
}

function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Notas CEAN')
    .addItem('Aplicar formatação segura', 'aplicarFormatacaoSegura')
    .addItem('Adicionar estudante', 'adicionarEstudanteManualmente')
    .addItem('Testar envio de email', 'testarEnvioEmailDoSistema')
    .addItem('Verificar configuração do script', 'mostrarDiagnosticoDoScript')
    .addToUi();
}

function criarMenu() {
  onOpen();
  SpreadsheetApp.getUi().alert('Menu criado.');
}

function mostrarDiagnosticoDoScript() {
  SpreadsheetApp.getUi().alert(
    'Apps Script de notas ativo.\n\n' +
    'Versão: ' + SCRIPT_VERSION + '\n' +
    'Planilha: ' + SPREADSHEET_ID + '\n' +
    'Aba de histórico: ' + HISTORY_SHEET_NAME + '\n' +
    'Coluna padrão de nota: ' + DEFAULT_SCORE_HEADER
  );
}

function testarEnvioEmailDoSistema() {
  const ui = SpreadsheetApp.getUi();
  const resposta = ui.prompt(
    'Teste de envio de email',
    'Digite o email que deve receber a mensagem de teste:',
    ui.ButtonSet.OK_CANCEL
  );

  if (resposta.getSelectedButton() !== ui.Button.OK) {
    return;
  }

  const email = String(resposta.getResponseText() || '').trim();
  if (!email) {
    ui.alert('Informe um email valido para o teste.');
    return;
  }

  sendConfirmationEmailIfPossible({
    email: email,
    estudante: 'Teste tecnico do sistema',
    atividade: 'Teste de envio de email',
    serie: '---',
    turma: '---',
    bimestre: '---',
    recuperacao: false,
    nota: '---',
    paresCorretos: 0,
    totalPares: 0,
    acertosIndividuais: 0,
    totalQuestoes: 0
  });

  ui.alert('Solicitacao de envio executada. Se esta foi a primeira vez, o Google pode pedir autorizacao antes de concluir.');
}

function adicionarEstudanteManualmente() {
  const ui = SpreadsheetApp.getUi();

  const nomeResposta = ui.prompt('Adicionar estudante', 'Digite o nome completo do estudante:', ui.ButtonSet.OK_CANCEL);
  if (nomeResposta.getSelectedButton() !== ui.Button.OK) {
    return;
  }

  const estudante = nomeResposta.getResponseText().trim();
  if (!estudante) {
    ui.alert('Informe um nome válido.');
    return;
  }

  const abaResposta = ui.prompt('Adicionar estudante', 'Digite o nome exato da aba de destino, por exemplo: 3o ano E ou PCA - Educação Digital 3o ano G', ui.ButtonSet.OK_CANCEL);
  if (abaResposta.getSelectedButton() !== ui.Button.OK) {
    return;
  }

  const sheetName = abaResposta.getResponseText().trim();
  if (!sheetName) {
    ui.alert('Informe o nome da aba de destino.');
    return;
  }

  const spreadsheet = getManagedSpreadsheet();
  const targetSheet = spreadsheet.getSheetByName(sheetName);
  if (!targetSheet) {
    ui.alert('Aba não encontrada: ' + sheetName);
    return;
  }

  const studentRow = findOrCreateStudentRow(targetSheet, estudante);

  appendHistory(spreadsheet, {
    avaliacao: 'Cadastro de estudante',
    atividade: 'Cadastro manual pelo menu',
    categoria: 'cadastro_aluno',
    sheetName: targetSheet.getName(),
    estudante: estudante,
    estudanteDigitado: estudante,
    payloadOriginal: { action: 'menu_add_student', estudante: estudante, sheetName: targetSheet.getName() }
  });

  ui.alert('Estudante registrado na aba ' + targetSheet.getName() + ', linha ' + studentRow + '.');
}

function aplicarFormatacaoSegura() {
  try {
    const planilha = getManagedSpreadsheet();
    const abaModelo = planilha.getSheetByName(MODELO_ABA_NOME);

    if (!abaModelo) {
      SpreadsheetApp.getUi().alert('Aba modelo ' + MODELO_ABA_NOME + ' não encontrada.');
      return;
    }

    const ultimaColunaModelo = abaModelo.getLastColumn();
    const todasAbas = planilha.getSheets();
    let abasAtualizadas = 0;
    const abasIgnoradas = [];

    for (let index = 0; index < todasAbas.length; index += 1) {
      const aba = todasAbas[index];
      const nomeAba = aba.getName();

      if (nomeAba === MODELO_ABA_NOME) {
        continue;
      }

      if (shouldSkipSheet(nomeAba)) {
        abasIgnoradas.push(nomeAba);
        continue;
      }

      for (let col = 1; col <= ultimaColunaModelo; col += 1) {
        aba.setColumnWidth(col, abaModelo.getColumnWidth(col));
      }

      aba.setFrozenRows(abaModelo.getFrozenRows());

      abaModelo.getRange(LINHA_CABECALHO, 1, 1, ultimaColunaModelo)
        .copyTo(aba.getRange(LINHA_CABECALHO, 1, 1, ultimaColunaModelo), { contentsOnly: false, formatOnly: false });

      const ultimaLinhaDestino = aba.getLastRow();
      if (ultimaLinhaDestino >= LINHA_INICIO_ALUNOS) {
        const numLinhasAlunos = ultimaLinhaDestino - LINHA_INICIO_ALUNOS + 1;
        const ultimaLinhaModelo = abaModelo.getLastRow();
        const numLinhasModelo = ultimaLinhaModelo - LINHA_INICIO_ALUNOS + 1;
        const linhasParaCopiar = Math.min(numLinhasAlunos, numLinhasModelo);

        if (linhasParaCopiar > 0) {
          abaModelo.getRange(LINHA_INICIO_ALUNOS, 1, linhasParaCopiar, ultimaColunaModelo)
            .copyTo(aba.getRange(LINHA_INICIO_ALUNOS, 1, linhasParaCopiar, ultimaColunaModelo), { formatOnly: true });
        }

        copyModelFormulas(abaModelo, aba, ultimaColunaModelo, ultimaLinhaDestino);
      }

      abasAtualizadas += 1;
    }

    let mensagem = 'Formatação aplicada com segurança.\n\n';
    mensagem += abasAtualizadas + ' turmas formatadas.\n';
    mensagem += 'Cabeçalho copiado com texto e formatação.\n';
    mensagem += 'Dados dos alunos não foram alterados.\n';

    if (abasIgnoradas.length) {
      mensagem += '\nAbas ignoradas:\n' + abasIgnoradas.join('\n');
    }

    SpreadsheetApp.getUi().alert(mensagem);
  } catch (error) {
    SpreadsheetApp.getUi().alert('Erro: ' + error.message);
    console.error(error);
  }
}

function shouldSkipSheet(sheetName) {
  const normalized = normalizeText(sheetName);
  return normalized.includes('sheet') || normalized.includes('config') || normalized.includes('resumo') || normalized === normalizeText(HISTORY_SHEET_NAME);
}

function buildStudentDatabase(spreadsheet) {
  const database = {
    bySheet: {},
    bySerieTurma: {},
    byTrilha: {}
  };

  const sheets = spreadsheet.getSheets();
  for (let index = 0; index < sheets.length; index += 1) {
    const sheet = sheets[index];
    const sheetName = sheet.getName();

    if (shouldSkipSheet(sheetName)) {
      continue;
    }

    const studentNames = readStudentNamesFromSheet(sheet);
    if (!studentNames.length) {
      continue;
    }

    database.bySheet[sheetName] = studentNames;

    const serieTurma = extractSerieTurmaFromSheetName(sheetName);
    if (serieTurma) {
      const serieTurmaKey = `${serieTurma.serie}|${serieTurma.turma}`;
      database.bySerieTurma[serieTurmaKey] = mergeStudentLists(database.bySerieTurma[serieTurmaKey], studentNames);
    }

    if (!looksLikeSerieTurmaSheet(sheetName)) {
      database.byTrilha[sheetName] = studentNames;
    }
  }

  return database;
}

function readStudentNamesFromSheet(sheet) {
  const lastRow = sheet.getLastRow();
  if (lastRow < LINHA_INICIO_ALUNOS) {
    return [];
  }

  const names = sheet.getRange(LINHA_INICIO_ALUNOS, 2, lastRow - LINHA_INICIO_ALUNOS + 1, 1)
    .getDisplayValues()
    .flat()
    .map(function(name) { return String(name || '').trim(); })
    .filter(function(name) { return name !== ''; });

  return Array.from(new Set(names)).sort(function(first, second) {
    return first.localeCompare(second, 'pt-BR');
  });
}

function extractSerieTurmaFromSheetName(sheetName) {
  const match = String(sheetName || '').match(/([123]o ano)\s+([A-Z])/i);
  if (!match) {
    return null;
  }

  return {
    serie: match[1].replace(/\s+/g, ' ').trim(),
    turma: match[2].trim().toUpperCase()
  };
}

function looksLikeSerieTurmaSheet(sheetName) {
  return /^\s*[123]o ano\s+[A-Z]\s*$/i.test(String(sheetName || ''));
}

function mergeStudentLists(currentList, nextList) {
  const merged = new Set([].concat(currentList || [], nextList || []));
  return Array.from(merged).sort(function(first, second) {
    return first.localeCompare(second, 'pt-BR');
  });
}

function copyModelFormulas(abaModelo, abaDestino, ultimaColunaModelo, ultimaLinhaDestino) {
  const formulasModelo = abaModelo.getRange(LINHA_INICIO_ALUNOS, 1, 1, ultimaColunaModelo).getFormulas()[0];

  for (let linha = LINHA_INICIO_ALUNOS; linha <= ultimaLinhaDestino; linha += 1) {
    for (let col = 0; col < formulasModelo.length; col += 1) {
      const formula = formulasModelo[col];
      if (!formula) {
        continue;
      }

      const formulaAdaptada = formula.replace(/\d+/g, function(match) {
        return String(parseInt(match, 10) - LINHA_INICIO_ALUNOS + linha);
      });

      abaDestino.getRange(linha, col + 1).setFormula(formulaAdaptada);
    }
  }
}

function parsePayload(e) {
  if (!e || !e.postData || !e.postData.contents) {
    throw new Error('Nenhum dado foi enviado para o Apps Script.');
  }

  return JSON.parse(e.postData.contents);
}

function validateStudentPayload(payload) {
  if (!payload || !payload.estudante) {
    throw new Error('Nome do estudante não informado.');
  }
}

function validatePayload(payload) {
  validateStudentPayload(payload);
}

function getManagedSpreadsheet() {
  return SpreadsheetApp.openById(SPREADSHEET_ID);
}

function findTargetSheet(spreadsheet, payload) {
  const candidates = [
    payload.sheetName,
    payload.trilha,
    buildSerieTurmaSheetName(payload.serie, payload.turma)
  ].filter(Boolean);

  for (let index = 0; index < candidates.length; index += 1) {
    const candidate = spreadsheet.getSheetByName(candidates[index]);
    if (candidate) {
      return candidate;
    }
  }

  throw new Error('Não foi possível localizar a aba correspondente ao estudante.');
}

function buildSerieTurmaSheetName(serie, turma) {
  if (!serie || !turma) {
    return '';
  }

  return String(serie).replace('º', 'o').trim() + ' ' + String(turma).trim();
}

function findOrCreateColumn(sheet, headerName) {
  const lastColumn = Math.max(sheet.getLastColumn(), 1);
  const headers = sheet.getRange(1, 1, 1, lastColumn).getDisplayValues()[0];
  const normalizedHeader = normalizeText(headerName);

  for (let column = 0; column < headers.length; column += 1) {
    if (normalizeText(headers[column]) === normalizedHeader) {
      return column + 1;
    }
  }

  const newColumn = headers.length + 1;
  sheet.getRange(1, newColumn).setValue(headerName);
  return newColumn;
}

function resolveScoreColumn(sheet, payload) {
  const requestedColumn = getRequestedColumnFromPayload(payload);
  const scoreHeader = buildScoreHeader(payload);

  if (!requestedColumn) {
    return findOrCreateColumn(sheet, scoreHeader);
  }

  if (!shouldUseColumnBlock(payload)) {
    return ensureFixedColumn(sheet, requestedColumn, scoreHeader);
  }

  return findOrCreateColumnInRequestedBlock(sheet, requestedColumn, scoreHeader, payload.bimestre || '');
}

function getRequestedColumnFromPayload(payload) {
  const normalizedTerm = normalizeTermKey(payload.bimestre);
  if (normalizedTerm) {
    const dynamicColumns = getTermStartColumnsMap();
    if (dynamicColumns[normalizedTerm]) {
      return String(dynamicColumns[normalizedTerm]).trim().toUpperCase();
    }
  }

  const explicitColumn = String(payload.coluna || payload.colunaBimestre || '').trim().toUpperCase();
  if (explicitColumn) {
    return explicitColumn;
  }

  return String(TERM_START_COLUMNS[normalizedTerm] || '').trim().toUpperCase();
}

function shouldUseColumnBlock(payload) {
  return payload.categoria === 'nota-bimestral'
    || payload.acao === 'acumular_nota_bimestral'
    || !!String(payload.simulacao || '').trim();
}

function normalizeTermKey(value) {
  const normalized = normalizeText(value)
    .replace(/bimestre/g, '')
    .replace(/\s+/g, ' ')
    .trim();

  if (!normalized) {
    return '';
  }

  if (normalized.startsWith('1')) return '1o';
  if (normalized.startsWith('2')) return '2o';
  if (normalized.startsWith('3')) return '3o';
  if (normalized.startsWith('4')) return '4o';

  return normalized;
}

function buildScoreHeader(payload) {
  const explicitHeader = String(payload.scoreHeader || '').trim();
  const normalizedExplicitHeader = normalizeText(explicitHeader);

  if (payload.simulacao) {
    return String(payload.simulacao).trim();
  }

  if (payload.atividade && payload.categoria === 'nota-bimestral') {
    return String(payload.atividade).trim();
  }

  if (explicitHeader && normalizedExplicitHeader !== normalizeText(DEFAULT_SCORE_HEADER)) {
    return explicitHeader;
  }

  return explicitHeader || DEFAULT_SCORE_HEADER;
}

function findOrCreateColumnInRequestedBlock(sheet, requestedColumnLetter, headerName, schoolTerm) {
  const targetColumn = columnLetterToNumber(requestedColumnLetter);
  if (!targetColumn) {
    throw new Error('Coluna de destino inválida: ' + requestedColumnLetter);
  }

  ensureColumnExists(sheet, targetColumn);

  const nextProtectedColumn = getNextProtectedColumn(targetColumn);
  const blockEnd = nextProtectedColumn ? nextProtectedColumn - 1 : Math.max(sheet.getLastColumn(), targetColumn + 3);
  ensureColumnExists(sheet, blockEnd);

  const lastColumn = Math.max(sheet.getLastColumn(), blockEnd);
  const headers = sheet.getRange(LINHA_CABECALHO, 1, 1, lastColumn).getDisplayValues()[0];
  const normalizedHeader = normalizeText(headerName);

  for (let column = targetColumn; column <= blockEnd; column += 1) {
    if (normalizeText(headers[column - 1]) === normalizedHeader) {
      return column;
    }
  }

  const currentHeader = String(headers[targetColumn - 1] || '').trim();
  if (!currentHeader || normalizeText(currentHeader) === normalizedHeader) {
    sheet.getRange(LINHA_CABECALHO, targetColumn).setValue(headerName);
    return targetColumn;
  }

  for (let column = targetColumn + 1; column <= blockEnd; column += 1) {
    const headerValue = String(headers[column - 1] || '').trim();
    if (!headerValue) {
      sheet.getRange(LINHA_CABECALHO, column).setValue(headerName);
      copyColumnFormatting(sheet, targetColumn, column);
      return column;
    }
  }

  if (!schoolTerm) {
    throw new Error('Não há coluna livre no bloco iniciado em ' + requestedColumnLetter + ' para registrar a simulação ' + headerName + '.');
  }

  const insertedColumn = insertSimulationColumnAcrossManagedSheets(targetColumn, normalizeTermKey(schoolTerm), headerName);
  return insertedColumn;
}

function ensureFixedColumn(sheet, requestedColumnLetter, headerName) {
  const targetColumn = columnLetterToNumber(requestedColumnLetter);
  if (!targetColumn) {
    throw new Error('Coluna de destino inválida: ' + requestedColumnLetter);
  }

  ensureColumnExists(sheet, targetColumn);

  if (!String(sheet.getRange(LINHA_CABECALHO, targetColumn).getDisplayValue() || '').trim() && headerName) {
    sheet.getRange(LINHA_CABECALHO, targetColumn).setValue(headerName);
  }

  return targetColumn;
}

function getNextProtectedColumn(currentColumn) {
  const dynamicColumns = getTermStartColumnsMap();
  const protectedLetters = TERM_ORDER.map(function(termKey) {
    return dynamicColumns[termKey] || TERM_START_COLUMNS[termKey] || '';
  }).filter(Boolean);

  for (let index = 0; index < protectedLetters.length; index += 1) {
    const protectedColumn = columnLetterToNumber(protectedLetters[index]);
    if (protectedColumn > currentColumn) {
      return protectedColumn;
    }
  }

  return null;
}

function ensureColumnExists(sheet, columnNumber) {
  const maxColumns = sheet.getMaxColumns();
  if (columnNumber <= maxColumns) {
    return;
  }

  sheet.insertColumnsAfter(maxColumns, columnNumber - maxColumns);
}

function copyColumnFormatting(sheet, sourceColumn, targetColumn) {
  const totalRows = Math.max(sheet.getMaxRows(), LINHA_INICIO_ALUNOS);
  sheet.getRange(1, sourceColumn, totalRows, 1)
    .copyTo(sheet.getRange(1, targetColumn, totalRows, 1), { formatOnly: true });
  sheet.setColumnWidth(targetColumn, sheet.getColumnWidth(sourceColumn));
}

function getTermStartColumnsMap() {
  const storedValue = PropertiesService.getScriptProperties().getProperty(TERM_START_COLUMNS_PROPERTY);
  if (!storedValue) {
    return Object.assign({}, TERM_START_COLUMNS);
  }

  try {
    const parsed = JSON.parse(storedValue);
    return Object.assign({}, TERM_START_COLUMNS, parsed || {});
  } catch (error) {
    return Object.assign({}, TERM_START_COLUMNS);
  }
}

function saveTermStartColumnsMap(termStartColumns) {
  PropertiesService.getScriptProperties().setProperty(
    TERM_START_COLUMNS_PROPERTY,
    JSON.stringify(termStartColumns)
  );
}

function insertSimulationColumnAcrossManagedSheets(targetColumn, schoolTerm, headerName) {
  const spreadsheet = getManagedSpreadsheet();
  const nextProtectedColumn = getNextProtectedColumn(targetColumn);
  const sheets = spreadsheet.getSheets();
  let insertionColumn = nextProtectedColumn || 0;

  if (!insertionColumn) {
    insertionColumn = 1;
    for (let index = 0; index < sheets.length; index += 1) {
      const sheet = sheets[index];
      if (shouldSkipSheet(sheet.getName())) {
        continue;
      }
      insertionColumn = Math.max(insertionColumn, sheet.getLastColumn() + 1);
    }
  }

  for (let index = 0; index < sheets.length; index += 1) {
    const sheet = sheets[index];
    if (shouldSkipSheet(sheet.getName())) {
      continue;
    }

    ensureColumnExists(sheet, Math.max(insertionColumn - 1, 1));
    sheet.insertColumnBefore(insertionColumn);
    copyColumnFormatting(sheet, Math.max(insertionColumn - 1, 1), insertionColumn);
    sheet.getRange(LINHA_CABECALHO, insertionColumn).setValue(headerName);
  }

  const dynamicColumns = getTermStartColumnsMap();
  const currentIndex = TERM_ORDER.indexOf(String(schoolTerm || '').trim());

  if (currentIndex !== -1) {
    for (let index = currentIndex + 1; index < TERM_ORDER.length; index += 1) {
      const termKey = TERM_ORDER[index];
      const currentLetter = dynamicColumns[termKey] || TERM_START_COLUMNS[termKey];
      dynamicColumns[termKey] = columnToLetter(columnLetterToNumber(currentLetter) + 1);
    }
    saveTermStartColumnsMap(dynamicColumns);
  }

  return insertionColumn;
}

function columnLetterToNumber(columnLetter) {
  const normalized = String(columnLetter || '').trim().toUpperCase();
  if (!/^[A-Z]+$/.test(normalized)) {
    return 0;
  }

  let result = 0;
  for (let index = 0; index < normalized.length; index += 1) {
    result = result * 26 + (normalized.charCodeAt(index) - 64);
  }

  return result;
}

function columnToLetter(columnNumber) {
  let number = Number(columnNumber) || 0;
  if (number <= 0) {
    return '';
  }

  let result = '';
  while (number > 0) {
    const remainder = (number - 1) % 26;
    result = String.fromCharCode(65 + remainder) + result;
    number = Math.floor((number - 1) / 26);
  }

  return result;
}

function findOrCreateStudentRow(sheet, studentName) {
  const lastRow = Math.max(sheet.getLastRow(), 2);
  const names = sheet.getRange(2, 2, Math.max(lastRow - 1, 1), 1).getDisplayValues().flat();
  const normalizedStudent = normalizeText(studentName);

  for (let index = 0; index < names.length; index += 1) {
    if (normalizeText(names[index]) === normalizedStudent) {
      return index + 2;
    }
  }

  const newRow = lastRow + 1;
  const lastNumber = Number(sheet.getRange(lastRow, 1).getValue()) || lastRow - 1;
  sheet.getRange(newRow, 1).setValue(lastNumber + 1);
  sheet.getRange(newRow, 2).setValue(studentName);
  copyRowFormat(sheet, Math.max(newRow - 1, LINHA_INICIO_ALUNOS), newRow);
  return newRow;
}

function copyRowFormat(sheet, sourceRow, targetRow) {
  const totalColumns = Math.max(sheet.getLastColumn(), 1);
  sheet.getRange(sourceRow, 1, 1, totalColumns)
    .copyTo(sheet.getRange(targetRow, 1, 1, totalColumns), { formatOnly: true });
}

function appendHistory(spreadsheet, data) {
  const historySheet = findOrCreateHistorySheet(spreadsheet);
  historySheet.appendRow([
    new Date(),
    data.avaliacao || '',
    data.atividade || '',
    data.categoria || '',
    data.serie || '',
    data.turma || '',
    data.bimestre || '',
    data.recuperacao || 'nao',
    data.trilha || '',
    data.sheetName || '',
    data.colunaDestino || data.scoreHeader || '',
    data.estudante || '',
    data.estudanteDigitado || '',
    data.nota || '',
    data.notaPercentual || '',
    data.paresCorretos || '',
    data.totalPares || '',
    data.acertosIndividuais || '',
    data.totalQuestoes || '',
    data.questoesPuladas || '',
    data.conclusao || '',
    data.criticas || '',
    data.sugestoes || '',
    data.email || '',
    JSON.stringify(data.respostas || []),
    JSON.stringify(data.payloadOriginal || {})
  ]);
}

function sendConfirmationEmailIfPossible(payload) {
  const email = String(payload.email || '').trim();
  if (!email) {
    return { status: 'skipped', reason: 'email_nao_informado' };
  }

  const lines = [
    SCHOOL_NAME,
    TEACHER_NAME,
    '',
    'Confirmamos o recebimento do resultado da avaliação.',
    '',
    'Estudante: ' + (payload.estudante || ''),
    'Atividade: ' + (payload.atividade || payload.avaliacao || 'Avaliação Bimestral - Educação Digital'),
    'Série/Turma: ' + [payload.serie || '', payload.turma || ''].join(' ').trim(),
    'Bimestre: ' + (payload.bimestre || ''),
    'Tipo: ' + (payload.recuperacao ? 'Recuperação' : 'Prova regular'),
    'Nota: ' + (payload.nota != null ? String(payload.nota).replace('.', ',') : ''),
    'Pares corretos: ' + (payload.paresCorretos || 0) + '/' + (payload.totalPares || 0),
    'Acertos individuais: ' + (payload.acertosIndividuais || 0) + '/' + (payload.totalQuestoes || 0),
    '',
    'Mensagem automática do sistema de avaliação.'
  ];

  MailApp.sendEmail({
    to: email,
    subject: 'Confirmação de resultado - Avaliação Bimestral de Educação Digital',
    body: lines.join('\n'),
    name: SCHOOL_NAME
  });

  return { status: 'sent', to: email };
}

function formatRuntimeError(error) {
  const message = error && error.message ? String(error.message) : String(error || 'Erro desconhecido.');

  if (/permission|authorization|mail\.google\.com|gmail\.send|script\.send_mail/i.test(message)) {
    return 'A nota foi gravada, mas o Apps Script ainda nao tem permissao para enviar email. Abra o editor do Apps Script, execute a funcao testarEnvioEmailDoSistema e aceite a autorizacao do Google.';
  }

  return message;
}

function findOrCreateHistorySheet(spreadsheet) {
  let historySheet = spreadsheet.getSheetByName(HISTORY_SHEET_NAME);

  if (!historySheet) {
    historySheet = spreadsheet.insertSheet(HISTORY_SHEET_NAME);
    historySheet.appendRow([
      'timestamp',
      'avaliacao',
      'atividade',
      'categoria',
      'serie',
      'turma',
      'bimestre',
      'recuperacao',
      'trilha',
      'aba_destino',
      'coluna_destino',
      'estudante',
      'estudante_digitado',
      'nota',
      'nota_percentual',
      'pares_corretos',
      'pares_totais',
      'acertos_individuais',
      'questoes_totais',
      'questoes_puladas',
      'conclusao',
      'criticas',
      'sugestoes',
      'email',
      'respostas_json',
      'payload_json'
    ]);
  }

  return historySheet;
}

function normalizeText(value) {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase();
}

function jsonResponse(data) {
  return ContentService
    .createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}