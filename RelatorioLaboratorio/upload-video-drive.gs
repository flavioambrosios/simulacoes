const VIDEO_FOLDER_ID = '1S7Q5kuB4vbCK9OKFoGbiiLg6fabDgdZc';
const MAX_VIDEO_BYTES = 30 * 1024 * 1024;

function autorizarUploadDeVideo() {
  const folder = DriveApp.getFolderById(VIDEO_FOLDER_ID);
  const authorizationFile = folder.createFile(
    Utilities.newBlob('', 'text/plain', 'autorizacao-upload-video.txt')
  );
  authorizationFile.setTrashed(true);
}

function doPost(e) {
  try {
    const body = e.parameter && e.parameter.action
      ? e.parameter
      : JSON.parse(e.postData.contents || '{}');
    if (body.action !== 'uploadVideo') {
      return responseForRequest(e, { ok: false, error: 'Acao nao reconhecida.' });
    }

    const dataUrl = String(body.dataUrl || '');
    const fileName = String(body.fileName || 'video-experiencia.mp4').replace(/[\\/:*?"<>|]/g, '_');
    const mimeType = String(body.mimeType || 'video/mp4');
    const match = dataUrl.match(/^data:([^;]+);base64,(.+)$/);
    if (!match) {
      return responseForRequest(e, { ok: false, error: 'Arquivo de video invalido.' });
    }

    const bytes = Utilities.base64Decode(match[2]);
    if (bytes.length > MAX_VIDEO_BYTES) {
      const actualSizeMb = (bytes.length / (1024 * 1024)).toFixed(2);
      return responseForRequest(e, {
        ok: false,
        error: 'O arquivo recebido tem ' + actualSizeMb + ' MB. O limite técnico de envio e 30 MB.'
      });
    }

    const folder = DriveApp.getFolderById(VIDEO_FOLDER_ID);
    const file = folder.createFile(Utilities.newBlob(bytes, mimeType, fileName));
    file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);

    return responseForRequest(e, {
      ok: true,
      fileId: file.getId(),
      fileName: file.getName(),
      url: file.getUrl(),
      size: bytes.length
    });
  } catch (error) {
    return responseForRequest(e, { ok: false, error: error.message || 'Falha ao salvar o video.' });
  }
}

function doGet() {
  return jsonResponse({ ok: true, service: 'upload-video-drive' });
}

function responseForRequest(e, payload) {
  if (e.parameter && e.parameter.action) {
    const message = Object.assign({ type: 'video-upload-result' }, payload);
    return HtmlService
      .createHtmlOutput('<script>window.top.postMessage(' + JSON.stringify(message) + ', "*");</script>')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
  }
  return jsonResponse(payload);
}

function jsonResponse(payload) {
  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}
