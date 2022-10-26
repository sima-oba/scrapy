#coding: utf-8
import json, re, requests, traceback, unidecode
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .functions.utils import ordinance_type
from ... import publisher
from .functions import utils
from datetime import datetime, timedelta

URL = "https://dool.egba.ba.gov.br"

#  
#  name: busca_id
#  @ param: String 'aaaa-mm-dd'
#  @ return: array with all materia_id 
#  
def busca_id(search_date):
    URL_BUSCA = f"{URL}/apifront/portal/edicoes/edicoes_from_data/{search_date}.json"
    response = requests.get(URL_BUSCA, verify=False)

    if(response.status_code == 200):
        response_id = []
        response_json = response.json()
        if(response_json['erro'] == False):
            for item in response_json['itens']:
                response_id.append(item['id'])
            
            print(f'Buscando documentos para a data: {search_date}')
        else:
            print("Erro ao buscar data")
            
    else:
        print("Erro ao encontrar página")

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('ignore-certificate-errors')
    driver = webdriver.Chrome(chrome_options=options)

    doc_id_link = []

    for _id in response_id:
        url_doi = f"{URL}/ver-html/{_id}/#e:{_id}"
        print(url_doi)

        driver.get(url_doi)

        WebDriverWait(driver, 30).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="modal-acessolivre"]/div/div/div[2]/div[2]/button[1]')   
        )).click()

        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "linkMateria")))
        links = driver.find_elements(By.CLASS_NAME, 'linkMateria')
        
        for i in range(len(links)):
            doc_id_link.append(links[i].get_attribute('data-materia-id'))

    driver.close()

    return doc_id_link


class text_processing:
    mask_ordinance_number = r'\d{2}\.\d{3}'
    mask_year = r'\d{4}'
    mask_cpf = r'\d{3}\.\d{3}\.\d{3}[-|_]\d{2}|\d{2}\.\d*\.\d*/\d*[-|_]\d*'
    mask_process = r'\d*\.\s*\d*\.\d*/\s*\w*/\w*[-|_]\s*\d*|\d*[-|_]\d*/\w*/\w*[-|_]\d*'
    # mask_process = r'\d*\.\d*\.\d*/\w*/\w*[-|_]\d*'
    # mask_process = r'\d*\.\d*\.\d*/\w*/\w*[–|_]\d*'    
    # mask_process = r'\d{4}\.\d{3}\.\d{6}/INEMA/LIC-\d{5}'
    mask_prazo = r'prazo [de ]*\d{1,2}[ (\w) anos]*|válida [por ]*\d{1,2}[ (\w) anos]*|prazo[ de vigência]* da Portaria[ INEMA]* n[°|º]* \d*\.\d*'
    mask_area = r'[\d+,]* ha'
    mask_issuer_name = r'município[s]* de [\w\s]*'
    mask_lat = r'Lat.[\d\s]*[°|º][\d\s]*[’ ]*[\d,\s]*["|”]\w'
    mask_longitude = r'Long.[\d\s]*[°|º][\d\s]*[’ ]*[\d,\s]*["|”]\w'
    mask_name = r'[à|a] [\w_/. ]*,'
    mask_capture = r'captação [\w\s]*'
    mask_flow = r'vazão [\d.]*'
    issuer = 3471168
    issuer_name = 'Bahia'
    labels = ["ordinance_type", "ordinance_number", "process", "publish_date", "owner_id", "issuer_name", "issuer", "term", "link"]
    
    def water_resource_right_authorization(ordinance_text, search_date, link):
        try:
            area = re.findall(text_processing.mask_area, ordinance_text)[0]
        except Exception as e:
            area = None

        capture = re.findall(text_processing.mask_capture, ordinance_text)[0][9:]
        
        try:
            lat = re.findall(text_processing.mask_lat, ordinance_text)[0][4:]
            longitude = re.findall(text_processing.mask_longitude, ordinance_text)[0][5:]
        except:
            lat = None
            longitude = None
        n_ordinance = str(f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}')
        deadline = re.findall(text_processing.mask_prazo, ordinance_text)[0][-15:]
        process = re.findall(text_processing.mask_process, ordinance_text)[0].replace('_','-')
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0]
        flow= re.findall(text_processing.mask_flow, ordinance_text)[0][6:]
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.RIGHT_USE_WATER_RESOURCES, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: link,
            'details': None
        }))
       
        reg['details'] = {
            'flow': flow,
            'capture': capture,
            'area': area,
            'latitude':  utils.degree_to_decimal(lat),
            'longitude': utils.degree_to_decimal(longitude)
        }
        
        return reg
        
    def water_resource_right_renovation(ordinance_text, search_date, link):
        try:
            area = re.findall(text_processing.mask_area, ordinance_text)[0]
        except Exception as e:
            area = None
        capture = re.findall(text_processing.mask_capture, ordinance_text)[0][9:]
        
        lat = re.findall(text_processing.mask_lat, ordinance_text)[0]
        longitude = re.findall(text_processing.mask_longitude, ordinance_text)[0]
        n_ordinance = str(f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}')
        deadline = re.findall(text_processing.mask_prazo, ordinance_text)[0][-15:]
        process = re.findall(text_processing.mask_process, ordinance_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0]
        flow= re.findall(text_processing.mask_flow, ordinance_text)
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.RIGHT_WATER_USE_RESOURCE_RENOVATION, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: link,
            'details': None
        }))

        isinstance()
       
        reg['details'] = {
            'flow': flow[0] if isinstance(flow, list) else flow,
            'capture': capture,
            'area': area,
            'latitude':  utils.degree_to_decimal(lat),
            'longitude': utils.degree_to_decimal(longitude)
        }

        return reg

    def water_resource_right_change(ordinance_text, search_date, link):
        try:
            area = re.findall(text_processing.mask_area, ordinance_text)[0]
        except Exception as e:
            area = None
        capture = re.findall(text_processing.mask_capture, ordinance_text)[0][9:]
        
        lat = re.findall(text_processing.mask_lat, ordinance_text)[0]
        longitude = re.findall(text_processing.mask_longitude, ordinance_text)[0]
        n_ordinance = str(f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}')
        deadline = re.findall(text_processing.mask_prazo, ordinance_text)[0]
        process = re.findall(text_processing.mask_process, ordinance_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0]
        flow= re.findall(text_processing.mask_flow, ordinance_text)[0]
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.RIGHT_WATER_USE_RESOURCE_CHANGE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: link,
            'details': None
        }))
       
        reg['details'] = {
            'flow': flow,
            'capture': capture,
            'area': area,
            'latitude':  utils.degree_to_decimal(lat),
            'longitude': utils.degree_to_decimal(longitude)
        }
        
        return reg

    # TODO review erratum scrapy structure
    def erratum(text, search_date, link):
        n_ordinance = re.findall(text_processing.mask_ordinance_number, text)[0]

        try:
            doc_number = re.findall(text_processing.mask_cpf, text)[0].replace('_','-')
        except:
            doc_number = None

        
        old_text = re.findall(r'ONDE SE L[EÊ]:(.*)LEIA', text.upper())[0][1:-1]
        new_text = re.findall(r'LEIA_SE:(.*”);', text.upper())[0][1:-1]

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.ERRATUM, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: None, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))
       
        reg['details'] = {
            'old': old_text,
            'new': new_text
        }
        return reg
    
    def license_renewal(ordinance_text, search_date, link):        
        mask_operation = r'para [\w_/. ]*'
        mask_renovation_type = r'RENOVAÇÃO [\w\s]*'

        process = re.findall(text_processing.mask_process, ordinance_text)[0].replace(' ', '').replace('_','-')
        n_ordinance = f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}'
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('_','-')
        operation = re.findall(mask_operation, ordinance_text)[0].replace('_','-')
        deadline = re.findall(text_processing.mask_prazo, ordinance_text)[0][-15:]
        renovation_type = re.findall(mask_renovation_type, ordinance_text)[0]
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.LICENSE_RENEWAL, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: link,
            'details': None
        }))
       
        reg['details'] = {
            'renovation_type': renovation_type,
            'operation': operation
        }
        
        return reg

    def operation_license(ordinance_text, search_date, link):
        mask_operation = r'operação [\w_/. ]*'
            
        process = re.findall(text_processing.mask_process, ordinance_text)[0].replace(' ', '').replace('_','-')
        n_ordinance = f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}'
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('_','-')
        try:
            operation = re.findall(mask_operation, ordinance_text)[0].replace('_','-')
        except:
            operation = None
        
        deadline = re.findall(text_processing.mask_prazo, ordinance_text)[0][9:]
        

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.OPERATION_LICENSE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: link,
            'details': None
        }))
       
        reg['details'] = {
            'operation': operation
        }
        
        return reg

    def alteration_license(ordinance_text, search_date, link):
        # mask_licenca = r'Conceder LICENÇA DE ALTERAÇÃO, válida até (.*?), (.*?), inscrita no CNPJ sob o n° (.*?), com sede (.*?), para (.*?). Art'
        mask_licenca = r'Conceder LICENÇA DE ALTERAÇÃO, válida até (.*?), (.*?),'
        labels = ['TipoPortaria', 'PortariaPub', 'PubData', 'ProcessoNum', 'LicencaValidade', 
          'LicencaEmpresa', 'LicencaCNPJ', 'URL']

        n_ordinance = str(f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}') # re.findall(mask_portaria, ordinance_text)[0].split("Nº ")[1]
        process = re.findall(text_processing.mask_process, ordinance_text)[0]
        portaria_licenca = re.findall(mask_licenca, ordinance_text)[0]

        deadline = portaria_licenca[0]
        portaria_licenca_empresa = portaria_licenca[1]
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('_','-')
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.ALTERATION_LICENSE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: link,
            'details': None
        }))
        
        return reg

    def preliminary_license(ordinance_text, search_date, link):
        mask_operation = r'para [\w_/. ]*'
        
        process = re.findall(text_processing.mask_process, ordinance_text)[0].replace(' ', '').replace('_','-')
        n_ordinance = f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}'
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('_','-')
        deadline = re.findall(text_processing.mask_prazo, ordinance_text)[0][9:]

        try:
            operation = re.findall(mask_operation, ordinance_text)[0][5:].replace('_','-')
        except Exception:
            operation = None

            
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.PRELIMINARY_LICENSE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: link,
            'details': None
        }))
       
        reg['details'] = {
            'operation': operation
        }
        
        return reg

    def regularization_license(ordinance_text, search_date, link):
        mask_operation = r'operação [\w_/. ]*'
        
        n_ordinance = str(f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}')
        process = re.findall(text_processing.mask_process, ordinance_text)[0].replace('_','-')
        deadline = re.findall(text_processing.mask_prazo, ordinance_text)[0][-15:]
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('_','-')
        
        try:
            operation = re.findall(mask_operation, ordinance_text)[0].replace('_','-')
        except Exception:
            operation = None

        try:
            latitude = re.findall(text_processing.mask_lat, ordinance_text)[-1]
        except Exception:
            latitude = None

        try:
            longitude = re.findall(text_processing.mask_longitude, ordinance_text)[-1]
        except Exception:
            longitude = None
            
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.REGULARIZATION_LICENSE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: link,
            'details': None
        }))
       
        reg['details'] = {
            'operation': operation,
            'latitude':  utils.degree_to_decimal(latitude),
            'longitude': utils.degree_to_decimal(longitude)
        }
        
        return reg

    def unified_license(ordinance_text, search_date, link):
        mask_operation = r'para [\w_/. ]*'
        mask_cpf = r'\d{3}\.\d{3}\.\d{3}-\d{2}|\d{2}\.\d{3}\.\d{3}/\d{4}[-|_]\d{2}'

        n_ordinance = str(f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}')
        process = re.findall(text_processing.mask_process, ordinance_text)[0].replace('_','-')
        deadline = re.findall(text_processing.mask_prazo, ordinance_text)[0][-15:]
        doc_number = re.findall(mask_cpf, ordinance_text)[0].replace('_','-')
        
        try:
            operation = re.findall(mask_operation, ordinance_text)[0][5:].replace('_','-')
        except Exception:
            operation = None
            
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.UNIFIED_LICENSE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: link,
            'details': None
        }))
       
        reg['details'] = {
            'operation': operation
        }
        
        return reg

    def installation_license(ordinance_text, search_date, link):
        mask_portaria = r'PORTARIA Nº [\d]+\.+[\d]* '
        mask_licenca = r'LICENÇA DE INSTALAÇÃO, válida pelo prazo de (.*?), para (.*?), localizado (.*?). [Art|§]'
        
        labels = ['TipoPortaria', 'PortariaPub', 'PubData', 'ProcessoNum', 'LicencaValidade', 
            'LicencaObjetivo', 'LicencaLocalizacao', 'URL']
        
        portaria_licenca = re.findall(mask_licenca, ordinance_text)[0]
        portaria_licenca_objetivo = portaria_licenca[1]
        portaria_licenca_localizado = portaria_licenca[2]

        n_ordinance = str(f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}')
        process = re.findall(text_processing.mask_process, ordinance_text)[0].replace('_','-')
        deadline = re.findall(text_processing.mask_prazo, ordinance_text)[0][-15:]
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('_','-')
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.INSTALLATION_LICENSE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: link,
            'details': None
        }))
       
        reg['details'] = {
            'objective': portaria_licenca_objetivo,
            'location': portaria_licenca_localizado
        }
        
        return reg

    # TODO review corporate name change scrapy strucuture
    def corporate_name_change(ordinance_text, search_date, link):
        process = re.findall(text_processing.mask_process, ordinance_text)[0]
        n_ordinance = str(f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}')
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0]
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.OWNER_CORRECTION, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))
        
        return reg

    def vegetal_suppression(ordinance_text, search_date, link):
        n_ordinance = str(f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}')
        process = re.findall(text_processing.mask_process, ordinance_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('_','-')
        deadline = re.findall(text_processing.mask_prazo, ordinance_text)[0][9:]
        

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.VEGETAL_SUPPRESSION, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: link,
            'details': None
        }))
       
        return reg

    def deadline_extension(ordinance_text, search_date, link):
        mask_processo_num = r'tendo em vista o que consta do Processo nº (.*?), RESOLVE'
        mask_prorrogacao = r'Conceder PRORROGAÇÃO D[A-Z]{1} PRAZO DE VALIDADE,(.*?). Art'
    
        n_ordinance = str(f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}')
        process = re.findall(mask_processo_num, ordinance_text)[0]
        portaria_prorrogacao = re.findall(mask_prorrogacao, ordinance_text)[0]

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.DEADLINE_EXTENSION, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            # TODO checar se há número de documento nesse tipo de portaria
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))

        reg['details'] = {
            'prorrogation': portaria_prorrogacao
        }
       
        return reg

    def exploration_approval(ordinance_text, search_date, link):
        n_ordinance = f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}'
        process = re.findall(text_processing.mask_process, ordinance_text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('_', '-')
        deadline = re.findall(text_processing.mask_prazo, ordinance_text)[0].replace('_', '-')
        area = re.findall(text_processing.mask_area, ordinance_text)[0]

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.EXPLORATION_APPROVAL, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: link,
            'details': None
        }))

        reg['details'] = {
            'area': area
        }
       
        return reg

    def ownership_transfer(ordinance_text, search_date, link):
        mask_grant_type = r'a titularidade .* concedida'
        
        
        n_ordinance = f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}'
        process = re.findall(text_processing.mask_process, ordinance_text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)
        
        try:
            grant_typeTransf = re.findall(mask_grant_type, ordinance_text)[0][15:-10]
        except:
            grant_typeTransf = None

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.OWNERSHIP_TRANSFER, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number[0], 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))

        reg['details'] = {
            'transfer_type': f'transferência de titularidade {grant_typeTransf}',
            'to_doc_number': doc_number[1]
        }
        
        return reg

    def forest_replacement_credit(ordinance_text, search_date, link):
        n_ordinance = f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}'
        process = re.findall(text_processing.mask_process, ordinance_text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('_', '-')
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.FOREST_REPLACEMENT_CREDIT, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))

        return reg

    def forest_volume_credit(ordinance_text, search_date, link):
        n_ordinance = f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}'
        process = re.findall(text_processing.mask_process, ordinance_text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('_', '-')
        deadline = re.findall(text_processing.mask_prazo, ordinance_text)[0].replace('_', '-')

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.FOREST_VOLUME_CREDIT, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: link,
            'details': None
        }))

        return reg

    def forest_volume_recognition(ordinance_text, search_date, link):
        n_ordinance = f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}'
        process = re.findall(text_processing.mask_process, ordinance_text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('_', '-')
        deadline = re.findall(text_processing.mask_prazo, ordinance_text)[0].replace('_', '-')

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.FOREST_VOLUME_RECOGNITION, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: link,
            'details': None
        }))

        return reg

    def forest_volume_transfer(ordinance_text, search_date, link):
        n_ordinance = f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}'
        process = re.findall(text_processing.mask_process, ordinance_text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('_', '-')
        to_cpf = re.findall(text_processing.mask_cpf, ordinance_text)[1].replace('_', '-')
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.FOREST_VOLUME_TRANSFER, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))

        reg['details'] = {
            'to_doc_number': to_cpf
        }
        
        return reg
        
    def forest_management(ordinance_text, search_date, link):
        mask_coord = r'\d{2}[°|º]\d{2}’[\d{2},.]*”\s*\w'
        
        n_ordinance = f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}'
        process = re.findall(text_processing.mask_process, ordinance_text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('_', '-')
        deadline = re.findall(text_processing.mask_prazo, ordinance_text)[0].replace('_', '-')
                    
        try:
            area = re.findall(text_processing.mask_area, ordinance_text)[0]
        except Exception as e:
            area = ""

        try:
            lati = re.findall(mask_coord, ordinance_text)[0]
        except Exception as e:
            lati = ""

        try:
            long = re.findall(mask_coord, ordinance_text)[1]
        except Exception as e:
            long = ""
                           
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.FOREST_MANAGEMENT, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: link,
            'details': None
        }))

        reg['details'] = {
            'area': area,
            'latitude':  utils.degree_to_decimal(lati),
            'longitude': utils.degree_to_decimal(long)
        }
        
        return reg
        
    def environmental_authorization(ordinance_text, search_date, link):
        mask_prazo = r'\d+ \(\w*\) ano[s]*'
        mask_operation = r'para [\w_/. ]*,'

        n_ordinance = f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}'
        process = re.findall(text_processing.mask_process, ordinance_text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('_', '-')
        deadline = re.findall(mask_prazo, ordinance_text)[0].replace('_', '-')
        obs = re.findall(mask_operation, ordinance_text)[0][5:-1].replace('_', '-')

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.ENVIRONMENTAL_AUTHORIZATION, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: link,
            'details': None
        }))

        reg['details'] = {
            'observation': obs
        }
        
        return reg

    # TODO não tem documento
    def cancel_grant(ordinance_text, search_date, link):
        mask_canceled_year = r'D.O.E. em \d*/\d*/\d*'
        mask_canceled_portaria = r'Portaria INEMA nº '+text_processing.mask_ordinance_number
        	
        try:
            process = re.findall(text_processing.mask_process, ordinance_text)[0].replace('_', '-')
        except Exception as e:
            process = None
        n_ordinance = f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}'
        portaria_cancelada = f'{re.findall(mask_canceled_portaria, ordinance_text)[0][-6:]}/{re.findall(mask_canceled_year, ordinance_text)[0][-4:]}'
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.CANCEL_, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: None, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))

        reg['details'] = {
            'canceled_ordinance': portaria_cancelada
        }
        
        return reg

    def license_cancellation(ordinance_text, search_date, link):
        mask_processo_num = r'tendo em vista o que consta do Processo nº (.*?), RESOLVE'
        mask_cancelamento = r'CANCELAR a Licença (.*?). Art'

        n_ordinance = f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}'
        process = re.findall(mask_processo_num, ordinance_text)[0]
        portaria_cancelamento = re.findall(mask_cancelamento, ordinance_text)[0]

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.LICENSE_CANCELLATION, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: None, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))

        reg['details'] = {
            'canceled_license': portaria_cancelamento
        }
        
        return reg

    def license_revocation(ordinance_text, search_date, link):
        mask_long = r'X= _\d*,\d*'
        mask_lat = r'Y= _\d*,\d*'
        mask_revocation_type = r'LICENÇA DE[\w\s]*conc'
        
        n_ordinance = f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}'
        process = re.findall(text_processing.mask_process, ordinance_text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('_', '-')
        
        origin_ordinance = f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[1]}/{re.findall(text_processing.mask_year, ordinance_text)[2]}'
        revocation_type = re.findall(mask_revocation_type, ordinance_text)[0][:-5]

        try:
            lat = re.findall(mask_lat, ordinance_text)[0][3:].replace('_','-')
        except Exception as e:
            lat = None

        try:
            long = re.findall(mask_long, ordinance_text)[0][3:].replace('_','-')
        except Exception as e:
            long = None

        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.LICENSE_REVOCATION, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))

        reg['details'] = {
            'latitude':  utils.degree_to_decimal(lat),
            'longitude': utils.degree_to_decimal(long),
            'origin_ordinance': origin_ordinance,
            'revocation_type': revocation_type
        }
        
        return reg

    def grant_waiver(ordinance_text, search_date, link):
        grant_type = r'DISPENSAD[AO] DE OUTORGA[DA]*'
        grants = []

        n_ordinance = f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}'
        process = re.findall(text_processing.mask_process, ordinance_text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('_', '-')
        try:
            lat = re.findall(text_processing.mask_lat, ordinance_text)
            longitude = re.findall(text_processing.mask_longitude, ordinance_text)
        except:
            lat = None
            longitude = None

        for i2 in range(len(re.findall(grant_type, ordinance_text.upper()))):
            try:
                try:
                    dismissal_process = re.findall(text_processing.mask_process, ordinance_text)[i2+1].replace('_', '-')
                except Exception as e:
                    dismissal_process = "not found"
                reg = json.loads(json.dumps({
                    text_processing.labels[0]: ordinance_type.GRANT_WAIVER, 
                    text_processing.labels[1]: n_ordinance, 
                    text_processing.labels[2]: process, 
                    text_processing.labels[3]: search_date, 
                    text_processing.labels[4]: doc_number, 
                    text_processing.labels[5]: text_processing.issuer_name, 
                    text_processing.labels[6]: text_processing.issuer, 
                    text_processing.labels[7]: None, 
                    text_processing.labels[8]: link,
                    'details': None
                }))
                try:
                    reg['details'] = {
                        'latitude':  utils.degree_to_decimal(lat[i2][4:]),
                        'longitude': utils.degree_to_decimal(longitude[i2][5:]),
                        'dismissal_process': dismissal_process
                    }
                except:
                    reg['details'] = {
                        'latitude':  None,
                        'longitude': None,
                        'dismissal_process': dismissal_process
                    }
                
                grants.append(reg)
                        
            except Exception as e:
                traceback.print_exc()


        return grants

    def volume_expansion(ordinance_text, search_date, link):
        mask_farm = r'Fazenda [\w ]*'
        
        n_ordinance = str(f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}')
        deadline = re.findall(text_processing.mask_prazo, ordinance_text)[0][-15:]
        process = re.findall(text_processing.mask_process, ordinance_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0]
        
        try:
            area = re.findall(text_processing.mask_area, ordinance_text)[0]
        except Exception as e:
            area = None
            
        try:
            lat = re.findall(text_processing.mask_lat, ordinance_text)[0]
        except Exception as e:
            lat = None

        try:
            longitude = re.findall(text_processing.mask_longitude, ordinance_text)[0]
        except Exception as e:
            longitude = None

        try:
            flow= re.findall(text_processing.mask_flow, ordinance_text)
        except Exception as e:
            flow = None

        try:
            capture = re.findall(text_processing.mask_capture, ordinance_text)[0][9:]
        except Exception as e:
            capture = None
            
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.VOLUME_EXPASION, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: link,
            'details': None
        }))

        reg['details'] = {
            'latitude':  utils.degree_to_decimal(lat),
            'longitude': utils.degree_to_decimal(longitude),
            'capture': capture, 
            'area': area, 
            'flow': flow
        }
        
        return reg

    def special_procedure_authorization(ordinance_text, search_date, link):
        mask_authorization_number = r'\d+.\d+.\d+/APE'
        
        n_ordinance = str(f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}')
        process = re.findall(text_processing.mask_process, ordinance_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0]
        
        authorization_number = re.findall(mask_authorization_number, ordinance_text)[0].replace('_', '-').replace(',', '')
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.SPECIAL_PROCEDURE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))

        reg['details'] = {
            'authorization_number': authorization_number
        }
            
        return reg

    def preventive(ordinance_text, search_date, link):
        mask_farm = r'Fazenda [\w ]*'
        
        n_ordinance = str(f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}')
        deadline = re.findall(text_processing.mask_prazo, ordinance_text)[0][-15:]
        process = re.findall(text_processing.mask_process, ordinance_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0]
        
        try:
            area = re.findall(text_processing.mask_area, ordinance_text)[0]
        except Exception as e:
            area = None
        try:
            lat = re.findall(text_processing.mask_lat, ordinance_text)[0]
        except Exception as e:
            lat = None

        try:
            longitude = re.findall(text_processing.mask_longitude, ordinance_text)[0]
        except Exception as e:
            longitude = None

        try:
            farm = re.findall(mask_farm, ordinance_text)[0][8:]					
        except Exception as e:
            farm = None

        try:
            flow = re.findall(text_processing.mask_flow, ordinance_text)
        except Exception as e:
            flow = None

        try:
            capture = re.findall(text_processing.mask_capture, ordinance_text)[0][9:]
        except Exception as e:
            capture = None
            
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.PREVENTIVE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: link,
            'details': None
        }))

        reg['details'] = {
            'latitude':  utils.degree_to_decimal(lat),
            'longitude': utils.degree_to_decimal(longitude),
            'farm': farm, 
            'capture': capture, 
            'area': area, 
            'flow': flow
        }
            
        return reg

    def condition_review(ordinance_text, search_date, link):
        labels = ['ordinance', 'process', 'publish_date', 'grant_type_porta', 'name', 'cnpj', 'origin_ordinance', 'obs', 'link']
        
        n_ordinance = str(f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}')
        process = re.findall(text_processing.mask_process, ordinance_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0]
        origin_ordinance = re.findall(text_processing.mask_ordinance_number, ordinance_text)[6]
                                        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.CONDITION_REVIEW, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))

        reg['details'] = {
            'origin_ordinance': origin_ordinance
        }

        return reg

    def temporary_suspend(text, search_date, link):
        mask_origin_ordinance = r'Portaria n° (.*?)[,]* publicada no D.O.E de \d*/\d*/(.*?) '
    
        n_ordinance = str(f'{re.findall(text_processing.mask_ordinance_number, text)[0]}/{re.findall(text_processing.mask_year, text)[0]}')
        process = re.findall(text_processing.mask_process, text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, text)[0].replace('_', '-')
        
        try:
            origin_ordinance = f'{re.findall(mask_origin_ordinance, text)[0][0]}/{re.findall(mask_origin_ordinance, text)[0][1]}'
        except:
            origin_ordinance = None
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.TEMPORARY_SUSPEND, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))

        reg['details'] = {
            'origin_ordinance': origin_ordinance
        }

def _import_date(search_date):
    type_list = [
        r'RESOLVE: ART. 1.º - PUBLICAR A ERRATA DA PORTARIA Nº',
        r'AUTORIZAR O DIREITO DE USO DOS RECURSOS HÍDRICOS',
        r'AUTORIZAR A RENOVAÇÃO DO DIREITO DE USO DOS RECURSOS HÍDRICOS',
        r'ALTERAÇÃO[ DA OUTORGA]* DO DIREITO DE USO DOS RECURSOS HÍDRICOS',
        r'CONCEDER[A ]*RENOVAÇÃO DA LICENÇA',
        r'CONCEDER[: § 1º -]*LICENÇA DE OPERAÇÃO,',
        r'CONCEDER[: § 1º -]*LICENÇA DE ALTERAÇÃO',
        r'CONCEDER[: § 1º -]*LICENÇA PRÉVIA,',
        r'CONCEDER[: § 1º -]*LICENÇA DE INSTALAÇÃO',
        r'CONCEDER[: § 1º -]*LICENÇA DE REGULARIZAÇÃO,',
        r'CONCEDER[: § 1º -]*LICENÇA UNIFICADA,',
        r'REVOGAR A LICENÇA',
        r'CANCELAR A LICENÇA',
        r'ALTERAR NOS REGISTROS DO INSTITUTO DO MEIO AMBIENTE E RECURSOS HÍDRICOS - INEMA, A RAZÃO SOCIAL',
        r'TRANSFERIR, NOS REGISTROS DO INSTITUTO DO MEIO AMBIENTE E RECURSOS HÍDRICOS - INEMA, A TITULARIDADE',
        r'CONCEDER[: § 1º -]*AUTORIZAÇÃO\s*DE\s*SUPRESSÃO\s*DA\s*VEGETAÇÃO\s*NATIVA',
        r'CONCEDER PRORROGAÇÃO DO PRAZO DE VALIDADE',
        r'CONCEDER APROVAÇÃO DA EXPLORAÇÃO OU CORTE DE FLORESTAS PLANTADAS',
        r'EMITIR CRÉDITO DE REPOSIÇÃO FLORESTAL',
        r'EMITIR CRÉDITO DE VOLUME FLORESTAL',
        r'CONCEDER RECONHECIMENTO DE VOLUME FLORESTAL',
        r'TRANSFERIR CRÉDITO DE VOLUME FLORESTAL',
        r'CONCEDER AUTORIZAÇÃO AMBIENTAL',
        r'CANCELAR A PORTARIA INEMA',
        r'DISPENSAD[AO] DE OUTORGA[DA]*',
        r'ampliação da outorga do direito de uso dos recursos hídricos'.upper(),
        r'Autorização por procedimento especial'.upper() ,
        r'CONCEDER APROVAÇÃO DA EXECUÇÃO DAS ETAPAS DO PLANO DE MANEJO FLORESTAL SUSTENTÁVEL',
        r'OUTORGA PREVENTIVA',
        r'CONCEDER REVISÃO DO CONDICIONANTE',
        r'SUSPENDER TEMPORARIAMENTE'
    ]

    type2function = {
        type_list[0]: 'erratum',
        type_list[1]: 'water_resource_right_authorization',
        type_list[2]: 'water_resource_right_renovation',
        type_list[3]: 'water_resource_right_change',
        type_list[4]: 'license_renewal',
        type_list[5]: 'operation_license',
        type_list[6]: 'alteration_license',
        type_list[7]: 'preliminary_license',
        type_list[8]: 'installation_license',
        type_list[9]: 'regularization_license',
        type_list[10]: 'unified_license',
        type_list[11]: 'license_revocation',
        type_list[12]: 'license_cancellation',
        type_list[13]: 'corporate_name_change',
        type_list[14]: 'ownership_transfer',
        type_list[15]: 'vegetal_suppression',
        type_list[16]: 'deadline_extension',
        type_list[17]: 'exploration_approval',
        type_list[18]: 'forest_replacement_credit',
        type_list[19]: 'forest_volume_credit',
        type_list[20]: 'forest_volume_recognition',
        type_list[21]: 'forest_volume_transfer',
        type_list[22]: 'environmental_authorization',
        type_list[23]: 'grant_waiver',
        type_list[24]: 'volume_expansion',
        type_list[25]: 'special_procedure_authorization',
        type_list[26]: 'forest_management',
        type_list[27]: 'preventive',
        type_list[28]: 'condition_review',
        type_list[29]: 'temporary_suspend'
    }

    ids = busca_id(search_date)
    
    success = 0
    i = 0
    is_found = False
    
    # busca pelo documento que contém as portarias
    while i < len(ids) and is_found == False:
        URL_DOC = f'{URL}/apifront/portal/edicoes/publicacoes_ver_conteudo/{ids[i]}'
        print(f'{i}/{len(ids)}')
        try:
            response = requests.get(URL_DOC, verify=False)
            soup = BeautifulSoup(response.text, "html.parser")
            pub = soup.find_all('p')
            for ordinance_text in pub:
                ordinance_text = ordinance_text.getText().replace('\r\n',' ').replace('\n', '').replace('\'','’').replace('"', '”') # .replace('–','-')
    
                for ord_type in type_list:
                    # print(ordinance_text)

                    # verifica se o tipo da portaria é conhecido de acordo com o vetor "type_list"
                    if len(re.findall(ord_type, ordinance_text.upper())) > 0:

                        is_found = True

                        try:
                            # chama a função que irá processar a portaria de acordo com o dicionário "type2function"
                            reg = getattr(text_processing, type2function[ord_type])(ordinance_text.replace('-', '_'), search_date, URL_DOC)
                            
                            
                            if type(reg) == dict:
                                # print(reg))
                                publisher.publish('NEW_ORDINANCE', reg)

                            elif type(reg) == list:
                                for mult_reg in reg:
                                    # print(mult_reg[1].to_json(force_ascii=False))
                                    publisher.publish('NEW_ORDINANCE', mult_reg)

                            print()
                            print()
                            success += 1
                        except:
                            print(ordinance_text)
                            print()
                            print()
                            traceback.print_exc()
        except:
            traceback.print_exc()
        i += 1
        
    print(f'{ success } ordinance(s) imported')

def import_news():
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    _import_date(yesterday)
    