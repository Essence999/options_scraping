import json
import sys
from interface import MyGUI
from data_extractor import DataExtractor
from csv_generator import CSVGenerator

# Inicia a interface
app = MyGUI()
app.mainloop()

# Se fechar a interface, o sistema não prosseguirá
if not app.web_scraper_bool:
    sys.exit(0)

with open('settings.json', 'r', encoding='utf=8') as archive:
    settings = json.load(archive)

# Inicia o extrator de dados
scrap = DataExtractor(settings)
scrap.initiate_scraping()

# Cria a planilha em csv
csv_gen = CSVGenerator(scrap.table_data, scrap.table_data_temporary)
csv_gen.initiate_sheet_generation()
