from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup
from time import time
from time import sleep


class DataExtractor():
    def __init__(self, settings) -> None:
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        self.driver = webdriver.Chrome(options=options)

        # A variável system_wait define o tempo de espera em segundos que o script
        # aguardará para localizar os elementos. Caso esteja em algum local com
        # conexão muito fraca, aumente esse valor conforme achar necessário.
        # Senão mantenha o valor médio de 15.
        system_wait = 15
        self.driver.implicitly_wait(system_wait)

        self.settings = settings
        self.login_url = 'https://opcoes.net.br/login'
        self.target_url = 'https://opcoes.net.br/opcoes/bovespa/vencimentos-longos'
        self.start_login_bool = False
        # Não adiciona [Modelo (M.), Vol Impl Bid, Vol Impl Ask, VI, VE]
        self.columns_to_delete = [5, 8, 11, 12, 13]

        # Dados com Login feito
        self.table_data = []
        # Atributo que servirá para sobrescrever os dados
        self.table_data_temporary = []

    def initiate_scraping(self):
        print('Coleta de dados iniciada...')
        start = time()

        # Se tiver um usuário, fazer o login normalmente
        # Senão, prosseguirá sem login
        if self.settings['usuario']:
            self.enter_settings()
            self.set_table_data_temporary()
            self.start_login_bool = True
            self.driver.get(self.login_url)
            print('Página de cadastro encontrada.')
            self.enter_login()

        self.enter_settings()

        self.driver.minimize_window()

        # Recebe o valor Boolean que indicará se deve ou não verificar Bid e Ask.
        self.verify_data_is_ready(self.start_login_bool)

        login_time = time() - start

        # Inicia a função que pega os dados da tabela
        print('Processando dados...')
        process_time = time()
        self.set_table_data()

        process_time = time() - process_time
        print('Processamento finalizado!')
        print(f'\nTempo de login: {login_time:.2f} segundos')
        print(
            f'Tempo de processamento de dados: {process_time:.2f} segundos')
        print(f'Tempo total: {login_time + process_time:.2f} segundos')

    def set_table_data_temporary(self):
        table_data_list = self.get_table_data_list()
        table_data_dict = self.convert_lists_to_dict(table_data_list)

        new_dict = {'R$': []}

        for obj in table_data_dict:
            new_dict['R$'].append(obj['R$'])

        self.table_data_temporary = new_dict

    # Verifica se a a tabela está pronta para extrair os dados
    # Se a coluna Bid estiver completamente vazia, repete o loop de verificação
    # Se a coluna Bid tiver pelo menos um item, o loop será parado
    def verify_data_is_ready(self, start_login_bool):
        print('Verificando se a tabela está pronta para extração...')
        while start_login_bool:
            sleep(1)
            tbody_html = self.get_tbody_html()
            table_html = BeautifulSoup(tbody_html, 'html.parser')
            rows = table_html.find_all('tr')

            tds_bid = []
            tds_ask = []
            for row in rows:
                columns = row.find_all('td')
                column_bid = columns[9].get_text()
                column_ask = columns[10].get_text()
                if column_bid != '':
                    tds_bid.append(column_bid)

                if column_ask != '':
                    tds_ask.append(column_ask)

            if len(tds_bid) != 0 and len(tds_ask) != 0:
                break

    # Pega o CPF e a senha, e coloca-os nos campos
    def enter_login(self):
        user = self.settings['usuario']

        # Formata o CPF, caso não seja vazio
        if user:
            user = f'{user[:3]}.{user[3:6]}.{user[6:9]}-{user[9:11]}'
        field_cpf = self.driver.find_element(By.XPATH, '//*[@id="CPF"]')
        field_cpf.send_keys(user)

        field_password = self.driver.find_element(
            By.XPATH, '//*[@id="Password"]')
        field_password.send_keys(self.settings['senha'])

        btn_login = self.driver.find_element(
            By.XPATH, '//*[@id="divmiddle"]/div/div/div[1]/section/form/div[4]/button')
        btn_login.click()

        if self.driver.current_url != self.login_url:
            print(
                '\n\033[32m----------------------------------------------\033[0m')
            print('\033[32mLogin realizado com sucesso.\033[0m')
            print(
                '\033[32m----------------------------------------------\033[0m\n')
        else:
            print(
                '\n\033[31m----------------------------------------------\033[0m')
            print('\033[31mLOGIN INVÁLIDO, VERIFIQUE!\033[0m')
            print(
                '\033[31m----------------------------------------------\033[0m\n')

    def enter_settings(self):
        self.driver.get(self.target_url)

        call_filters = self.driver.find_element(
            By.XPATH, '//*[@id="callPutFilter"]')
        options_call_filter = Select(call_filters)
        options_call_filter.select_by_value(
            self.settings['call filter'])

        min_expirations = self.driver.find_element(
            By.XPATH, '//*[@id="minExpiration"]')
        options_min_expirations = Select(min_expirations)
        options_min_expirations.select_by_value(
            self.settings['min expiration'])
        print('Opções definidas.')

    # Define o atributo table_data da classe
    def set_table_data(self):
        table_data_list = self.get_table_data_list()
        table_data_dict = self.convert_lists_to_dict(table_data_list)
        self.table_data = table_data_dict

    # Transforma o HTML do tbody em uma lista com os dados de cada linha
    # E trata os dados conforme os requisitos solicitados
    def get_table_data_list(self):
        tbody_html = self.get_tbody_html()
        table_html = BeautifulSoup(tbody_html, 'html.parser')
        rows = table_html.find_all('tr')
        table_data_list = []

        for row in rows:
            row_elements = row.find_all('td')
            row_data = [element.get_text() for element in row_elements]
            table_data_list.append(row_data)

        # table_data_list = self.verify_days(table_data_list)
        table_data_list = self.delete_columns(table_data_list)

        return table_data_list

    # Retorna o HTML do tbody
    def get_tbody_html(self):
        tbody_element = self.driver.find_element(
            By.XPATH, '//*[@id="tbl-opcoes-body"]/tbody')
        tbody_html = tbody_element.get_attribute('outerHTML')
        return tbody_html

    # Verifica o dia corrido da última negociação (posição 16)
    # Excluir se for maior que 20
    def verify_days(self, table_data_list):
        new_list = []
        for row in table_data_list:
            if int(row[16]) <= 20:
                new_list.append(row)
        return new_list

    # Deleta as colunas a serem deletadas
    # Modelo (M.), Vol Impl Bid, Vol Impl Ask, VI, VE
    def delete_columns(self, table_data_list):
        actualized_table_data_list = []
        for row in table_data_list:
            new_row = []
            for index, column in enumerate(row):
                if index not in self.columns_to_delete:
                    new_row.append(column)
            actualized_table_data_list.append(new_row)
        return actualized_table_data_list

    # Converte as listas de linhas para uma lista de dicionários e retorna a nova lista
    def convert_lists_to_dict(self, table_data_list):
        dict_model = {
            'Opção': None,
            'Tipo': None,
            'Data': None,
            'Dias úteis': None,
            'Dias corr. Venc.': None,
            'Strike': None,
            'Dist.(%) do Strike': None,
            'Bid': None,
            'Ask': None,
            'R$': None,
            'Data / hora': None,
            'Dias corr. Ult. Neg.': None,
            'Num. Neg.': None,
            'Vol. Financeiro': None
        }
        decimals = ['Strike',
                    'Dist.(%) do Strike',
                    'Bid',
                    'Ask',
                    'R$',
                    'Vol. Financeiro']
        integers = ['Dias úteis',
                    'Dias corr. Venc.',
                    'Dias corr. Ult. Neg.',
                    'Num. Neg.']

        new_list = []

        for row in table_data_list:
            new_row = {}
            for index, key in enumerate(dict_model.keys()):
                if row[index] == '':
                    value = None
                elif key in decimals:
                    value = self.convert_str_to_float(row[index])
                elif key in integers:
                    value = int(row[index].replace('.', ''))
                else:
                    value = row[index]
                new_row[key] = value
            new_list.append(new_row)
        return new_list

    def convert_str_to_float(self, value: str):
        value = value.replace('.', '').replace(',', '.')
        return float(value)
