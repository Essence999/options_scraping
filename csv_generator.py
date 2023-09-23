import pandas as pd
import os
from datetime import datetime


class CSVGenerator:
    def __init__(self, table_data, table_data_temporary) -> None:
        self.df_temp = pd.DataFrame(table_data_temporary)
        self.df = pd.DataFrame(table_data)
        if len(self.df_temp) > 0:
            self.df['R$'] = self.df['R$'].combine_first(self.df_temp['R$'])
        self.df = self.df.query("`Dias corr. Ult. Neg.` <= 20")
        self.df = self.df.fillna('')
        self.rows_number = len(self.df) + 2

    # Cria a planilha com todas as informações requisitadas
    def initiate_sheet_generation(self):
        # Coluna Preço
        self.create_price_column()
        # Coluna 20%
        self.create_20_column()
        # Coluna W/E
        # if col.Bid, (1/col.Strike)*col.Bid, (1/col.Strike)*col.R$
        self.create_we_column()
        # Coluna S/E
        # (1/col.Strike)*col.Preço
        self.create_se_column()

        # Converte todas as colunas com número decimal para número com vírgula.
        # Permite que o Google Sheets use suas fórmulas nos números.
        self.convert_float_to_comma()

        self.create_sheet()

    def convert_float_to_comma(self):
        decimal_columns = [
            'Strike',
            'Dist.(%) do Strike',
            'Bid',
            'Ask',
            'R$',
            'Vol. Financeiro',
            'W/E',
            'S/E']

        for column in decimal_columns:
            self.df[column] = self.df[column].apply(
                lambda x: str(x).replace('.', ','))

    def create_price_column(self):
        string_price_rows = []
        for i in range(2, self.rows_number):
            string_price = f'=IF(LEFT(A{i};4)="KLBN";GOOGLEFINANCE("KLBN11");IFNA(IFNA(GOOGLEFINANCE(CONCAT(LEFT(A{i};4);3));GOOGLEFINANCE(CONCAT(LEFT(A{i};4);4)));GOOGLEFINANCE(CONCAT(LEFT(A{i};4);11))))'
            string_price_rows.append(string_price)
        self.df['Preço'] = string_price_rows

    def create_20_column(self):
        string_20_rows = []
        for i in range(2, self.rows_number):
            string_20 = f'=if((G{i}*1,2)<B{i};1;if((G{i}*0,8)>B{i};1;0))'
            string_20_rows.append(string_20)
        self.df['20%'] = string_20_rows

    def create_we_column(self):
        self.df['W/E'] = self.df.apply(
            lambda row:
                (1/row['Strike'])*row['Bid']
                if row['Bid']
                else (1/row['Strike'])*row['R$'], axis=1)

    def create_se_column(self):
        string_se_rows = []
        for i in range(2, self.rows_number):
            string_se = f'=(1/F{i})*O{i}'
            string_se_rows.append(string_se)
        self.df['S/E'] = string_se_rows

    def create_sheet(self):
        # Verifica se a pasta das planilhas já existe, senão cria a pasta.
        if os.path.exists('planilhas geradas'):
            pass
        else:
            os.mkdir('planilhas geradas')

        time = datetime.now()
        time = time.strftime('%d-%m-%Y_%H-%M-%S')
        sheet_name = 'dados'

        self.df.to_csv(
            f'planilhas geradas/{sheet_name}_{time}.csv', index=False)

        print("\nArquivo CSV criado com sucesso.")
