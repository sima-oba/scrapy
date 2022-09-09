#coding: utf-8
import json, re, traceback, shutil
from .functions import pdfutils
from .functions.utils import ordinance_type
from ... import publisher
from datetime import datetime, timedelta

class text_processing:

    #mask_ordinance_number = r'\d{2}\.\d{3}'
    mask_ordinance = r'[Portaria|PORTARIA]\s*([nN].\s*)?(\d*/\d*)'
    mask_year = r'\d{4}'
    mask_cpf = r'\d*\.\d*\.\d*–\d*|\d*[\.\s]\d*[\.\s]\d*/\d*–\s*\d*'
    mask_process = r'[Pp]rocesso SEMMA\s*(.*)[,.]\s*RESOLVE'
    mask_deadline = r'(\d{2}?)[(\w) ]*ano[s]*|v[aá]lida\s*por\s*(\d*)'
    mask_area = r'[\d+,]* ha'
    mask_city_name = r'município[s]* de [\w\s]*'
    mask_lat = r'Lat.[\d\s]*[°|º][\d\s]*[’ ]*[\d,\s]*["|”]\w'
    mask_longitude = r'Long.[\d\s]*[°|º][\d\s]*[’ ]*[\d,\s]*["|”]\w'
    mask_name = r'[à|a] [\w_/. ]*,'
    mask_capture = r'captação [\w\s]*'
    mask_flow = r'vazão [\d.]*'
    
    
    issuer = 6320811 
    issuer_name = 'Cocos'
    labels = ["ordinance_type", "ordinance_number", "process", "publish_date", "owner_id", "issuer_name", "issuer", "term", "link"]
    
    #licenca simplificada
    def ls(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-')
        doc_number = re.findall(text_processing.mask_cpf, page_text)[1].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        deadline = deadline[0] + ' ano(s)'
        operation = re.findall(text_processing.mask_operation, page_text)[0]

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.SIMPLIFIED_ENVIRONMENTAL_LICENSE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline,
            text_processing.labels[8]: dom_link
        }))
        
        reg['details'] = {
            'operation': operation
        }
        
        return reg

    def unified_license(ordinance_text, search_date):
        mask_operation = r'para [\w_/. ]*'

        n_ordinance = str(f'{re.findall(text_processing.mask_ordinance, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}')
        process = re.findall(text_processing.mask_process, ordinance_text)[0].replace('_','-')
        deadline = re.findall(text_processing.mask_deadline, ordinance_text)[0][-15:]
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('_','-')

        try:
            operation = re.findall(mask_operation, ordinance_text)[0][5:].replace('_','-')
        except Exception:
            operation = None

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.RIGHT_USE_WATER_RESOURCES, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: None,
            'details': None
        }))
       
        reg['details'] = {
            'operation': operation
        }
        return reg
    
    #renovacao
    def license_renewal(page_text, search_date, dom_link):
        mask_renov_type = r'CONCEDER[:\s]*RENOVA[GC]AO\s*DE/s*LICEN[GCÇ]A\s*DE/s*(.*?) '
        labels = ['ordinance_number', 'process', 'publish_date', 'grant_type', 'renovation_type', 'owner_name', 'doc_number', 'deadline', 'city_name', 'link']
        
        aux = re.findall(text_processing.mask_ordinance, page_text)
        n_ordinance = f'{aux[0][0]}/{aux[0][1]}'
        
        process = re.findall(text_processing.mask_process, page_text)[0]
        
        try:
            doc_number = re.findall(text_processing.mask_cpf, page_text)[1]
        except:
            doc_number = re.findall(text_processing.mask_cpf, page_text)[0]
        deadline = re.findall(text_processing.mask_deadline, page_text)
        deadline = deadline[0][0] + deadline[0][1] + ' ano(s)'

        renov_type = re.findall(mask_renov_type, page_text.upper())[0]
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.LICENSE_RENEWAL, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: dom_link
        }))
       
        reg['details'] = {'license_type': renov_type}
        
        return reg



    # errata
    def erratum(text, search_date, link):
        mask_ordinance = r'[PORTARIA|EDITAL] N° (\d*/\d{4})'

        try:
            n_ordinance = re.findall(text_processing.mask_ordinance, text)[0]
        except:
            try:
                n_ordinance = re.findall(mask_ordinance, text)[0]
            except:
                n_ordinance = None

        old_text = re.findall(r'ONDE|onde*\s*se*\s*[LlIéeE]*[–SE:]*\s*(.*)Leia', text)[0]
        new_text = re.findall(r'LEIA|eia\s*–\*SE|se:(.*)\.\s*Dé', text)[0]

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.ERRATUM, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: None, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: None, 
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
    

    # licença de localização
    def ll(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-')
        doc_number = re.findall(text_processing.mask_cpf, page_text)[1].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        deadline = deadline[0] + ' ano(s)'
        operation = re.findall(text_processing.mask_operation, page_text)[0]

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.LOCATION_LICENSE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline,
            text_processing.labels[8]: dom_link
        }))
        
        reg['details'] = {
            'operation': operation
        }
        
        return reg

    # licença prévia
    def preliminary_license(page_text, search_date, link):
        mask_operation = r'para [\w_/. ]*'
        
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-').replace(' ', '').replace(' ', '').replace('_','–')
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]        
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('_','–')
        deadline = re.findall(text_processing.mask_deadline, page_text)[0]

        try:
            operation = re.findall(mask_operation, page_text)[0][5:].replace('_','–')
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
            text_processing.labels[8]: link
        }))
       
        reg['details'] = {'operation': operation}
        
        return reg

    # licença de instalação
    def linst(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-').replace(' ', '')
        try:
            doc_number = re.findall(text_processing.mask_cpf, page_text)[1].replace('–','-').replace(' ', '')
        except:
            doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-').replace(' ', '').replace(' ', '')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        deadline = deadline[0][0] + deadline[0][1] + ' ano(s)'

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.INSTALLATION_LICENSE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, # prazo
            text_processing.labels[8]: dom_link
        }))
        
        return reg


    # licença de implantação
    def limp(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-').replace(' ', '')
        try:
            doc_number = re.findall(text_processing.mask_cpf, page_text)[1].replace('–','-').replace(' ', '')
        except:
            doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-').replace(' ', '').replace(' ', '')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        deadline = deadline[0][0] + deadline[0][1] + ' ano(s)'

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.IMPLANTATION_LICENSE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, # prazo
            text_processing.labels[8]: dom_link
        }))
        
        return reg
        
        
    # licença de operação
    def lo(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-').replace(' ', '')
        try:
            doc_number = re.findall(text_processing.mask_cpf, page_text)[1].replace('–','-').replace(' ', '')
        except:
            doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-').replace(' ', '').replace(' ', '')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        deadline = deadline[0][0] + deadline[0][1] + ' ano(s)'
        
        try:
            area = re.findall(text_processing.mask_area, page_text)[0]
        except Exception:
            area = None

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.OPERATION_LICENSE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, # prazo
            text_processing.labels[8]: dom_link
        }))

        reg['details'] = {
            'area': area
        }        
        
        return reg

    # autorização de supressão de vegetação nativa
    def asv(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-').replace(' ', '')
        try:
            doc_number = re.findall(text_processing.mask_cpf, page_text)[1].replace('–','-').replace(' ', '')
        except:
            doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-').replace(' ', '').replace(' ', '').replace(' ', '')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        deadline = deadline[0][0] + deadline[0][1] + ' ano(s)'

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.VEGETAL_SUPPRESSION, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, # prazo
            text_processing.labels[8]: dom_link
        }))
        
        return reg


def _import_date(search_date):
    type_list = [
        r'CONCEDE[R]*\s*LICEN[GCÇ]A\s*AMBIENTAL\s*SIMPLIFICADA',
        r'CONCEDE[R]*\s*LICEN[GCÇ]A\s*AMBIENTAL\s*UNIFICADA',
        r'CONCEDE[R]*\s*A\s*RENOVA[GCÇ][AÃ]O\s*D[EA]\s*LICEN[GCÇ]A', #caso especial
        r'CONCEDE[R]*\s*LICEN[GCÇ]A\s*AMBIENTAL\s*DE/s*IMPLANTA[GCÇ][AÃ]O',
        r'ERRATA:\s*PORTARIA', #achado apenas errata de DECRETO no portal, essa regex é de LEM
        r'CONCEDE[R]*\s*A\s*LICEN[GCÇ]A\s*AMBIENTAL\s*DE/s*LOCALIZAGAO',
        r'CONCEDER[R]*\s*[A _]*LICEN[CG]A[\w\s]*PR[ÉE]VIA',
        r'CONCEDER[R]*\s*[A _]*LICEN[CG]A[\w\s]*OPERA[GC]AO',
        r'CONCEDER[R]*\s*[A _]*LICEN[CG]A[\w\s]*INSTALA[GC]AO',
        r'CONCEDER[R]*\s*.*AUTORIZA[CGÇADO]*\s*PARA\s*SUPRESSAO\s*DA\s*VEGETA[CGÇ]*AO[\sNATIVA]*'       
    ]

    type2function = {
        type_list[0]: 'ls',
        type_list[1]: 'unified_license',
        type_list[2]: 'license_renewal',
        type_list[3]: 'limp',
        type_list[4]: 'erratum',
        type_list[5]: 'll',
        type_list[6]: 'preliminary_license',
        type_list[7]: 'lo',
        type_list[8]: 'linst',
        type_list[9]: 'asv'
    }

    files, folder, links = pdfutils.dom_cocos(search_date)
    
    regs = []
        
    # verifica se o documento foi encontrado
    for filename, link in zip(files, links):
        pages = pdfutils.ocr_extract_page_text(filename)
        print("Reading file")

        for page in pages:
            ordinance_text = page.replace('-','–')
            for ord_type in type_list:
                # print(ordinance_text)

                # verifica se o tipo da portaria é conhecido de acordo com o vetor "type_list"
                if len(re.findall(ord_type, ordinance_text.upper())) > 0:

                    try:
                        # chama a função que irá processar a portaria de acordo com o dicionário "type2function"
                        reg = getattr(text_processing, type2function[ord_type])(ordinance_text, search_date, link)
                        
                        regs.append(reg)
                        
                        publisher.publish('NEW_ORDINANCE', reg)
                    except:
                        print(ordinance_text)
                        traceback.print_exc()

                    print('')

    try:
        shutil.rmtree(folder)
    except FileNotFoundError:
        pass

    print(f'{ len(regs) } ordinance(s) imported')
    
    return regs
    
def import_news():
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    _import_date(yesterday)
    
