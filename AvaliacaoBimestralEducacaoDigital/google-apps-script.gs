const SPREADSHEET_ID = '1SgAsDYqCKlz2Kel0_dmbdMEf9pmCz2mDVQHJwV2kIZk';
const HISTORY_SHEET_NAME = 'Historico Avaliacoes';
const DEFAULT_SCORE_HEADER = 'prova';
const SCRIPT_VERSION = '2026-08-03-email-single-path';
const LINHA_CABECALHO = 1;
const LINHA_INICIO_ALUNOS = 2;
const SCHOOL_NAME = 'CEAN - Centro de Ensino Médio Asa Norte';
const TEACHER_NAME = 'Prof. Flávio Ambrósio';
const ACCESS_TOKEN_HASH = 'f267aa257c7116e591f638a9bb704f8c11940f3798b59f7a8f1f6a55d0877be1';
const MAX_ROSTER_NAMES_PER_RESPONSE = 80;
const EMAIL_CONFIRMATION_ENABLED = false;
const TERM_ORDER = ['1o', '2o', '3o', '4o'];
const TERM_START_COLUMNS_PROPERTY = 'TERM_START_COLUMNS_MAP';
const TERM_START_COLUMNS = {
  '1o': 'J',
  '2o': 'N',
  '3o': 'R',
  '4o': 'V'
};

function doGet(e) {
  if (e && e.parameter && e.parameter.action === 'sheets') {
    const accessToken = String(e.parameter.accessToken || '').trim().toLowerCase();
    if (!accessToken || accessToken !== String(ACCESS_TOKEN_HASH).toLowerCase()) {
      return jsonResponse({
        status: 'error',
        message: 'Nao autorizado. Use token valido para consultar as abas.'
      });
    }

    return jsonResponse({
      status: 'ok',
      action: 'getAvailableSheets',
      sheets: getAvailableStudentSheets(getManagedSpreadsheet()),
      version: SCRIPT_VERSION
    });
  }

  if (e && e.parameter && e.parameter.action === 'students') {
    const accessToken = String(e.parameter.accessToken || '').trim().toLowerCase();
    if (!accessToken || accessToken !== String(ACCESS_TOKEN_HASH).toLowerCase()) {
      return jsonResponse({
        status: 'error',
        message: 'Nao autorizado. Use doPost com action=getStudentNames e token valido.'
      });
    }

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
    hasDoGet: true,
    spreadsheetId: SPREADSHEET_ID,
    historySheet: HISTORY_SHEET_NAME,
    defaultScoreHeader: DEFAULT_SCORE_HEADER,
    termStartColumns: getTermStartColumnsMap()
  });
}

function doPost(e) {
  try {
    const payload = parsePayload(e);

    if (payload.action === 'getAvailableSheets') {
      validateAccessToken(payload.accessToken);

      return jsonResponse({
        status: 'ok',
        action: 'getAvailableSheets',
        sheets: getAvailableStudentSheets(getManagedSpreadsheet()),
        version: SCRIPT_VERSION
      });
    }

    if (payload.action === 'getStudentNames') {
      validateAccessToken(payload.accessToken);

      const spreadsheet = getManagedSpreadsheet();
      const studentDatabase = buildStudentDatabase(spreadsheet);
      const names = getFilteredStudentNames(studentDatabase, payload);

      return jsonResponse({
        status: 'ok',
        action: 'getStudentNames',
        names: names,
        version: SCRIPT_VERSION
      });
    }

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
  const emailTestMenuLabel = EMAIL_CONFIRMATION_ENABLED
    ? 'Testar envio de email'
    : 'Testar envio de email (desativado)';

  ui.createMenu('Notas CEAN')
    .addItem('Adicionar estudante', 'adicionarEstudanteManualmente')
    .addItem(emailTestMenuLabel, 'testarEnvioEmailDoSistema')
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

  if (!EMAIL_CONFIRMATION_ENABLED) {
    ui.alert('Envio de email desativado neste script. Os dados continuam sendo gravados normalmente na planilha.');
    return;
  }

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

function getAvailableStudentSheets(spreadsheet) {
  return spreadsheet.getSheets()
    .map(function(sheet) {
      return {
        sheet: sheet,
        name: sheet.getName()
      };
    })
    .filter(function(entry) {
      return !shouldSkipSheet(entry.name) && readStudentNamesFromSheet(entry.sheet).length > 0;
    })
    .map(function(entry) {
      return entry.name;
    })
    .sort(function(first, second) {
      return first.localeCompare(second, 'pt-BR');
    });
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
  const requestedColumn = getRequestedColumnFromPayload(sheet, payload);
  const scoreHeader = buildScoreHeader(payload);

  if (!requestedColumn) {
    return findOrCreateColumn(sheet, scoreHeader);
  }

  if (!shouldUseColumnBlock(payload)) {
    return ensureFixedColumn(sheet, requestedColumn, scoreHeader);
  }

  return findOrCreateColumnInRequestedBlock(sheet, requestedColumn, scoreHeader, payload.bimestre || '');
}

function getRequestedColumnFromPayload(sheet, payload) {
  const normalizedTerm = normalizeTermKey(payload.bimestre);
  if (normalizedTerm) {
    const headerColumns = getTermStartColumnsFromSheet(sheet);
    if (headerColumns[normalizedTerm]) {
      return String(headerColumns[normalizedTerm]).trim().toUpperCase();
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
  if (normalized.startsWith('primeir')) return '1o';
  if (normalized.startsWith('segund')) return '2o';
  if (normalized.startsWith('terceir')) return '3o';
  if (normalized.startsWith('quart')) return '4o';

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
  const normalizedSchoolTerm = normalizeTermKey(schoolTerm);
  const headerColumns = getTermStartColumnsFromSheet(sheet);

  if (normalizedSchoolTerm && !headerColumns[normalizedSchoolTerm]) {
    throw new Error(
      'Nao encontrei o marcador do ' + normalizedSchoolTerm + ' bimestre na linha 1 da aba ' + sheet.getName() +
      '. Use um cabecalho como "1o bimestre", "2o bimestre", "3o bimestre" ou "4o bimestre".'
    );
  }

  const resolvedColumnLetter = headerColumns[normalizedSchoolTerm] || requestedColumnLetter;
  const targetColumn = columnLetterToNumber(resolvedColumnLetter);
  if (!targetColumn) {
    throw new Error('Coluna de destino inválida: ' + resolvedColumnLetter);
  }

  ensureColumnExists(sheet, targetColumn);

  const nextProtectedColumn = getNextProtectedColumn(targetColumn, sheet, normalizedSchoolTerm);
  const blockEnd = nextProtectedColumn ? nextProtectedColumn - 1 : Math.max(sheet.getLastColumn(), targetColumn);
  ensureColumnExists(sheet, blockEnd);

  const lastColumn = Math.max(sheet.getLastColumn(), blockEnd);
  const headers = sheet.getRange(LINHA_CABECALHO, 1, 1, lastColumn).getDisplayValues()[0];
  const normalizedHeader = normalizeText(headerName);
  let rightmostUsedInBlock = 0;

  for (let column = targetColumn; column <= blockEnd; column += 1) {
    const headerValue = String(headers[column - 1] || '').trim();
    if (normalizeText(headerValue) === normalizedHeader) {
      return column;
    }
    if (headerValue) {
      rightmostUsedInBlock = column;
    }
  }

  if (!rightmostUsedInBlock) {
    sheet.getRange(LINHA_CABECALHO, targetColumn).setValue(headerName);
    return targetColumn;
  }

  const nextColumnInBlock = rightmostUsedInBlock + 1;

  if (!nextProtectedColumn || nextColumnInBlock < nextProtectedColumn) {
    ensureColumnExists(sheet, nextColumnInBlock);
    sheet.getRange(LINHA_CABECALHO, nextColumnInBlock).setValue(headerName);
    if (nextColumnInBlock !== targetColumn) {
      copyColumnFormatting(sheet, rightmostUsedInBlock, nextColumnInBlock);
    }
    return nextColumnInBlock;
  }

  if (!schoolTerm) {
    throw new Error('Não foi possível expandir o bloco iniciado em ' + resolvedColumnLetter + ' sem informar o bimestre.');
  }

  const insertedColumn = insertSimulationColumnAcrossManagedSheets(nextProtectedColumn, normalizedSchoolTerm, headerName);
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

function getNextProtectedColumn(currentColumn, sheet, currentTerm) {
  if (sheet && currentTerm) {
    const headerColumns = getTermStartColumnsFromSheet(sheet);
    const currentIndex = TERM_ORDER.indexOf(currentTerm);

    if (currentIndex !== -1) {
      for (let index = currentIndex + 1; index < TERM_ORDER.length; index += 1) {
        const termKey = TERM_ORDER[index];
        if (headerColumns[termKey]) {
          return columnLetterToNumber(headerColumns[termKey]);
        }
      }
    }

    return null;
  }

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

function insertSimulationColumnAcrossManagedSheets(insertionColumn, schoolTerm, headerName) {
  const spreadsheet = getManagedSpreadsheet();
  const sheets = spreadsheet.getSheets();

  if (!insertionColumn || insertionColumn <= 0) {
    throw new Error('Não foi possível calcular a coluna de inserção para a nova simulação.');
  }

  for (let index = 0; index < sheets.length; index += 1) {
    const sheet = sheets[index];
    if (shouldSkipSheet(sheet.getName())) {
      continue;
    }

    const lastExistingColumn = Math.max(sheet.getMaxColumns(), 1);
    const sourceColumn = Math.max(Math.min(insertionColumn - 1, lastExistingColumn), 1);

    if (insertionColumn > lastExistingColumn) {
      sheet.insertColumnAfter(lastExistingColumn);
    } else {
      sheet.insertColumnBefore(insertionColumn);
    }

    copyColumnFormatting(sheet, sourceColumn, insertionColumn);
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
  if (!EMAIL_CONFIRMATION_ENABLED) {
    return { status: 'skipped', reason: 'envio_email_desativado_temporariamente' };
  }

  if (payload && (payload.categoria === 'simulacao' || String(payload.simulacao || '').trim())) {
    return { status: 'skipped', reason: 'email_confirmacao_desativado_para_simulacao' };
  }

  if (payload && payload.suppressStudentEmail) {
    return { status: 'skipped', reason: 'email_terceirizado' };
  }

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

function validateAccessToken(accessToken) {
  const normalized = String(accessToken || '').trim().toLowerCase();
  if (!normalized || normalized !== String(ACCESS_TOKEN_HASH).toLowerCase()) {
    throw new Error('Nao autorizado. Token de acesso invalido.');
  }
}

function getFilteredStudentNames(studentDatabase, payload) {
  const requestedSheetName = String(payload.sheetName || '').trim();
  const serie = String(payload.serie || '').replace('º', 'o').trim();
  const turma = String(payload.turma || '').trim().toUpperCase();
  const trilha = String(payload.trilha || '').trim();

  const names = new Set();
  const preferredSheet = requestedSheetName || resolvePreferredSheetName(serie, turma, trilha);
  const serieTurmaKey = serie && turma ? `${serie}|${turma}` : '';

  if (preferredSheet && studentDatabase.bySheet[preferredSheet]) {
    studentDatabase.bySheet[preferredSheet].forEach(function(name) { names.add(name); });
  }

  if (serieTurmaKey && studentDatabase.bySerieTurma[serieTurmaKey]) {
    studentDatabase.bySerieTurma[serieTurmaKey].forEach(function(name) { names.add(name); });
  }

  if (trilha && studentDatabase.byTrilha[trilha]) {
    studentDatabase.byTrilha[trilha].forEach(function(name) { names.add(name); });
  }

  return Array.from(names)
    .filter(function(name) { return !!String(name || '').trim(); })
    .sort(function(first, second) { return first.localeCompare(second, 'pt-BR'); })
    .slice(0, MAX_ROSTER_NAMES_PER_RESPONSE);
}

function resolvePreferredSheetName(serie, turma, trilha) {
  if (trilha && trilha !== 'Outra' && trilha !== 'Nenhuma (Turma de Fisica)' && trilha !== 'Visitante') {
    return trilha;
  }

  if (!serie || !turma || serie === 'Visitante' || turma === 'Visitante') {
    return '';
  }

  return `${serie} ${turma}`;
}
function debugSpreadsheet() {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  Logger.log('ID: ' + ss.getId());
  Logger.log('Nome: ' + ss.getName());
  Logger.log('URL: ' + ss.getUrl());
}

function getTermStartColumnsFromSheet(sheet) {
  const result = {};
  const lastColumn = Math.max(sheet.getLastColumn(), 1);
  const headers = sheet.getRange(LINHA_CABECALHO, 1, 1, lastColumn).getDisplayValues()[0];

  for (let column = 1; column <= headers.length; column += 1) {
    const termKey = detectTermHeaderKey(headers[column - 1]);
    if (!termKey || TERM_ORDER.indexOf(termKey) === -1 || result[termKey]) {
      continue;
    }

    result[termKey] = columnToLetter(column);
  }

  return result;
}

function detectTermHeaderKey(headerValue) {
  const compact = normalizeText(headerValue)
    .replace(/[º°]/g, 'o')
    .replace(/\s+/g, '');

  if (!compact) {
    return '';
  }

  if (compact === '1obimestre' || compact === '1bimestre' || compact === '1o' || compact === 'primeirobimestre' || compact === 'primeiro') {
    return '1o';
  }

  if (compact === '2obimestre' || compact === '2bimestre' || compact === '2o' || compact === 'segundobimestre' || compact === 'segundo') {
    return '2o';
  }

  if (compact === '3obimestre' || compact === '3bimestre' || compact === '3o' || compact === 'terceirobimestre' || compact === 'terceiro') {
    return '3o';
  }

  if (compact === '4obimestre' || compact === '4bimestre' || compact === '4o' || compact === 'quartobimestre' || compact === 'quarto') {
    return '4o';
  }

  return '';
}