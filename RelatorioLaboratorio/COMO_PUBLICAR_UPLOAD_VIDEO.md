# Publicar upload direto de video

1. Abra https://script.google.com/ e crie um novo projeto.
2. Apague o codigo inicial e cole o conteudo de `upload-video-drive.gs`.
3. Salve o projeto.
4. Clique em **Implantar** > **Nova implantacao**.
5. Tipo: **Aplicativo da web**.
6. Executar como: **Eu**.
7. Quem tem acesso: **Qualquer pessoa**.
8. Clique em **Implantar** e autorize o acesso ao Google Drive.
9. Copie a URL terminada em `/exec`.
10. No arquivo `RelatorioLaboratorio_3.html`, substitua o valor de `VIDEO_UPLOAD_URL` pela URL copiada.

A pasta usada pelo serviço é a pasta informada pelo professor no Google Drive. O limite atual é de 25 MB por vídeo. O arquivo é salvo na pasta e recebe permissão de visualização por link.

Não compartilhe o código do projeto nem tokens de autorização. A URL `/exec` ficará no HTML para que os alunos possam enviar os arquivos; por isso, acompanhe o uso da pasta e suspenda a implantação se houver abuso.
