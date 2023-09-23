# Web Scraping de site de opções + criação de Google Sheets

Esse projeto foi feito para um cliente com o objetivo de raspar os dados do site https://opcoes.net.br/opcoes/bovespa/vencimentos-longos após entrar em sua conta e criar uma planilha do Google Sheets em CSV com os cálculos solicitados.

Funcionamento do sistema:
- Possui uma interface gráfica intuitiva que permite colocar o usuário e a senha, que serão salvos em um arquivo JSON para serem usados posteriormente, e as opções do site a serem escolhidas.
- Ao iniciar a coleta de dados com login, para se adaptar ao site, abre o site sem o login primeiro para pegar os dados R$ da tabela.
- Abre-se o site com login para pegar a tabela com os dados mostrados em tempo real. O script aguarda a tabela ser povoada com novos dados antes de extraí-los.
- Os dados da tabela são tratados para que seja convertido em um Data Frame do Pandas.
- Usa-se o Pandas para manipular os dados de acordo com as preferências solicitadas.
- Por fim, cria-se um CSV adaptado ao Google Sheets em uma pasta separada com todos os dados organizados.

As bibliotecas utilizadas foram: customtkinter, selenium, beautifulsoup4 e pandas.
