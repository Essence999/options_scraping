import customtkinter as ctk
import json


class MyGUI(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Sistema de Coleta de Dados")
        self.geometry("350x350")
        self.eval('tk::PlaceWindow . center')
        # Verifica se a janela foi fechada (permanece False) ou
        # se a coleta será iniciada (True)
        self.web_scraper_bool = False
        # Opções escolhidas, começa com as opções padrões
        self.chosen_options = {
            'call filter': 'C',
            'min expiration': 'opcoes/vencimentos-longos/minimo-18-meses'}

        # Título de Login
        font_login = ctk.CTkFont(size=16)
        login_title = ctk.CTkLabel(
            self, text="Insira as informações de login", font=font_login)
        login_title.pack(padx=10, pady=10)

        # Abre as settings e pega o usuário já cadastrado se necessário
        settings_list = self.get_settings()
        current_user = settings_list[0]
        current_password = settings_list[1]

        # Campo do CPF
        user_entry = ctk.CTkEntry(
            self, placeholder_text='CPF (apenas números)',
            textvariable=current_user, width=200, height=40)
        user_entry.pack(padx=10, pady=3)

        # Campo da Senha
        user_password_entry = ctk.CTkEntry(
            self, placeholder_text='Senha',
            textvariable=current_password, width=200, height=40)
        user_password_entry.pack(padx=10, pady=5)

        # Valores do Tipo (Call Filter)
        self.call_filter_values = ['CALLs', 'PUTs', 'TODAS']

        combobox_call_filter_var = ctk.StringVar(
            value=self.call_filter_values[0])

        combobox_call_filter = ctk.CTkComboBox(
            self, values=self.call_filter_values,
            command=self.combobox_call,
            variable=combobox_call_filter_var)
        combobox_call_filter.pack(padx=10, pady=10)
        combobox_call_filter_var.set('CALLs')

        # Valores do vencimento (Min Expiration)
        self.min_expiration_values = [
            'entre 3 e 6 meses',
            'mínimo em 6 meses',
            'mínimo em 12 meses',
            'mínimo em 18 meses'
        ]

        combobox_min_expiration_var = ctk.StringVar(
            value=self.min_expiration_values[3])

        combobox_min_expiration = ctk.CTkComboBox(
            self, width=175,
            values=self.min_expiration_values,
            command=self.combobox_call,
            variable=combobox_min_expiration_var)
        combobox_min_expiration.pack(padx=10, pady=10)
        combobox_min_expiration_var.set('mínimo em 18 meses')

        font_btn_activate_web_scraper = ctk.CTkFont(size=16)
        btn_activate_web_scraper = ctk.CTkButton(
            self, text="Iniciar coleta de dados",
            font=font_btn_activate_web_scraper,
            command=lambda: self.activate_web_scraper(
                user_entry.get(), user_password_entry.get()),
            width=200, corner_radius=8)
        btn_activate_web_scraper.pack(padx=10, pady=10)

    # Pega as configurações
    def get_settings(self):
        # Verifica se as configurações já existem
        settings_model = {
            "usuario": "",
            "senha": "",
            "call filter": "",
            "min expiration": ""
        }
        try:
            open('settings.json', 'r', encoding='utf=8')
        except FileNotFoundError:
            with open('settings.json', "w", encoding='utf-8') as archive:
                json.dump(settings_model, archive, indent=4)

        with open('settings.json', 'r', encoding='utf=8') as archive:
            settings = json.load(archive)
        current_user = ''
        current_password = ''
        if settings['usuario'] and settings['senha']:
            current_user = ctk.StringVar(self, value=settings['usuario'])
            current_password = ctk.StringVar(self, value=settings['senha'])
        return [current_user, current_password]

    # Analisa as opções selecionadas
    def combobox_call(self, choice):
        if choice in self.min_expiration_values:
            print('Selecionado: ' + choice)
            if choice == self.min_expiration_values[0]:
                choice = "opcoes/vencimentos-longos/entre-3-e-6-meses"
            elif choice == self.min_expiration_values[1]:
                choice = "opcoes/vencimentos-longos/minimo-6-meses"
            elif choice == self.min_expiration_values[2]:
                choice = "opcoes/vencimentos-longos/minimo-12-meses"
            else:
                choice = "opcoes/vencimentos-longos/minimo-18-meses"
            self.chosen_options['min expiration'] = choice
        else:
            print('Selecionado: ' + choice)
            if choice == self.call_filter_values[0]:
                choice = "C"
            elif choice == self.call_filter_values[1]:
                choice = "P"
            else:
                choice = ""
            self.chosen_options['call filter'] = choice

    # Permite o início a coleta de dados. e fecha a janela.
    def activate_web_scraper(self, user, password):
        self.web_scraper_bool = True
        self.actualize_login(user, password)

        with open('settings.json', 'r', encoding='utf=8') as archive:
            settings = json.load(archive)

        settings['call filter'] = self.chosen_options['call filter']
        settings['min expiration'] = self.chosen_options['min expiration']

        with open('settings.json', 'w', encoding='utf=8') as archive:
            json.dump(settings, archive, indent=4)

        self.destroy()

    def actualize_login(self, user, password):
        with open('settings.json', 'r', encoding='utf=8') as archive:
            settings = json.load(archive)

        settings['usuario'] = user
        settings['senha'] = password

        with open('settings.json', 'w', encoding='utf=8') as archive:
            json.dump(settings, archive, indent=4)
        print('Login recebido.')
