#coding: utf-8
import json, re, traceback, shutil
from .functions import pdfutils
from .functions.utils import ordinance_type
from datetime import datetime, timedelta
from ... import publisher

#  
#  name: processamento do texto
#  @ param: texto, data da análise e link para documento
#  @ return: pd.Series
#  
class text_processing:
    mask_ordinance = r'\d*/\d*'
    mask_process = r'\d*.\d*.TEC.\w*.\d*'
    mask_deadline = r'válida por \d*'
    mask_name = r'[a|à] [\w\s_/.–]*, [P|p]essoa'
    mask_cpf = r'\d*\.\d*\.\d*[–|_]\d*|^\d+\.\d+\.\d+/\d+[-_]\d+$'
    mask_area = r'\d*,\d*\s*ha'
    mask_volume_production = r'[,\d\.]* ton[eladas/anomês]*'
    mask_from_name = r'em favor de[\w\s_/.,]*[P|p]essoa'
    mask_to_name = r'para[\w\s_/.,–]*[P|p]essoa'
    mask_origin_ordinance = 'Portaria \w* Nº.\s*'+mask_ordinance
    issuer = 3470583
    city_name = 'Barreiras'
    kafka_topic = 'NEW_ORDINANCE'
    labels = ["ordinance_type", "ordinance_number", "process", "publish_date", "owner_id", "issuer_name", "issuer", "term", "link"]
    
    # autorização de supressão de vegetação nativa
    def asv(page_text, search_date, dom_link):
        n_ordinance = str(re.findall(text_processing.mask_ordinance, page_text)[0])
        process = re.findall(text_processing.mask_process, page_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)[0][11:] + ' anos'

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.VEGETAL_SUPPRESSION, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: 'Barreiras', 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: dom_link,
            'details': None
        }))
        
        return reg


    # licença de operação
    def lo(page_text, search_date, dom_link):
        n_ordinance = str(re.findall(text_processing.mask_ordinance, page_text)[0])
        process = re.findall(text_processing.mask_process, page_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)[0][11:] + ' anos'
        try:
            area = re.findall(text_processing.mask_area, page_text)[0]
        except Exception:
            area = None

        try:
            volume_production = re.findall(text_processing.mask_volume_production, page_text)[0]
        except Exception:
            volume_production = None

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.OPERATION_LICENSE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: 'Barreiras', 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: dom_link
        }))
       
        reg['details'] = {'area': area, 'prod_volume': volume_production}
        
        return reg
    
    
    # licença simplificada
    def ls(page_text, search_date, dom_link):
        n_ordinance = str(re.findall(text_processing.mask_ordinance, page_text)[0])
        process = re.findall(text_processing.mask_process, page_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)[0][11:] + ' anos'

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.SIMPLIFIED_ENVIRONMENTAL_LICENSE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: 'Barreiras', 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: dom_link
        }))
                
        return reg

    # licença de implantação
    def implantation_license(page_text, search_date, dom_link):
        n_ordinance = str(re.findall(text_processing.mask_ordinance, page_text)[0])
        process = re.findall(text_processing.mask_process, page_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)[0][11:] + ' anos'
        try:
            area = re.findall(text_processing.mask_area, page_text)[0]
        except Exception:
            area = None

        try:
            volume_production = re.findall(text_processing.mask_volume_production, page_text)[0]
        except Exception:
            volume_production = None

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.IMPLANTATION_LICENSE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: 'Barreiras', 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: dom_link
        }))
       
        reg['details'] = {'area': area, 'prod_volume': volume_production}
        
        return reg


    # licença de localização
    def ll(page_text, search_date, dom_link):
        n_ordinance = str(re.findall(text_processing.mask_ordinance, page_text)[0])
        process = re.findall(text_processing.mask_process, page_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)[0][11:] + ' anos'

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.LOCATION_LICENSE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: 'Barreiras', 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: dom_link
        }))
        
        return reg


    # transferência de titularidade
    def tt(ordinance_text, search_date, dom_link):
        n_ordinance = str(re.findall(text_processing.mask_ordinance, ordinance_text)[0])
        process = re.findall(text_processing.mask_process, ordinance_text)[0]
        from_doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('–','-')
        to_doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('–','-')
        origin_ordinance = re.findall(text_processing.mask_origin_ordinance, ordinance_text)[0]
        deadline = re.findall(text_processing.mask_deadline, ordinance_text)[0][11:] + ' anos'
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.OWNERSHIP_TRANSFER, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: from_doc_number, 
            text_processing.labels[5]: 'Barreiras', 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: dom_link
        }))
       
        reg['details'] = {
            # 'origin_ordinance': origin_ordinance,
            'to_doc_number': to_doc_number
        }
        
        return reg
        

    # retífica de razão social
    def rrs(ordinance_text, search_date, dom_link):
        n_ordinance = str(re.findall(text_processing.mask_ordinance, ordinance_text)[0])
        process = re.findall(text_processing.mask_process, ordinance_text)[0]
        from_doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('–','-')
        to_doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[1].replace('–','-')
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.OWNER_NAME_CHANGE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: from_doc_number, 
            text_processing.labels[5]: 'Barreiras', 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: dom_link
        }))
       
        reg['details'] = {'to_owner_id': to_doc_number}
        
        return reg
        

    # revogar licença
    def revogar(ordinance_text, search_date, dom_link):
        n_ordinance = str(re.findall(text_processing.mask_ordinance,ordinance_text)[0])
        process = re.findall(text_processing.mask_process,ordinance_text)[0]
        doc_number = re.findall(text_processing.mask_cpf,ordinance_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline,ordinance_text)[0][11:] + ' anos'
        try:
            area = re.findall(text_processing.mask_area,ordinance_text)[0]
        except Exception:
            area = None
            print('\"Area not found in ordinance\"')
        
        try:
            volume_production = re.findall(text_processing.mask_volume_production,ordinance_text)[0]
        except Exception:
            volume_production = None
            print('\"Production volume not found in ordinance\"')

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.LICENSE_REVOCATION, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: 'Barreiras', 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: dom_link
        }))
       
        reg['details'] = {'area': area, 'volume_production': volume_production}
        
        return reg


    # prorrogação do prazo de validade
    def deadline_extension(ordinance_text, search_date, dom_link):
        process = re.findall(text_processing.mask_process, ordinance_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, ordinance_text)[0][11:] + ' anos'
        n_ordinance = re.findall(text_processing.mask_ordinance, ordinance_text)[0]
        changed_ordinance = re.findall(text_processing.mask_ordinance, ordinance_text)[2]

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.DEADLINE_EXTENSION, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: 'Barreiras', 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: dom_link
        }))
       
        reg['details'] = {'changed_ordinance': changed_ordinance}
        
        return reg


    # errata
    def erratum(text, search_date, link):
        mask_ordinance = r'portaria sematur nº \d* de \d* de \w* de \d*'
        
        ordinance_number = re.findall(mask_ordinance, text.lower())[0]
        n_ordinance = str(f'{ordinance_number[20:23]}/{ordinance_number[-4:]}')
    
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
    
        return reg


def _import_date(search_date):
    filename, folder, dom_link, _ = pdfutils.barreiras_dom(search_date)
    
    pages =[]
    # verifica se o documento foi encontrado
    if dom_link != '':
        pages = pdfutils.extract_page_text(filename)
        print("Reading file")

    type_list = [
        r'Onde se lê',
        r'Concede[r]*\s*Autorização de Supressão de Vegetação Nativa',
        r'Concede[r]* Licença[\w\s]*Operação',
        r'Concede[r]* Licença[\w\s]*Simplificada',
        r'Concede[r]* Licença[\w\s]*Implantação',
        r'Concede[r]* Licença[\w\s]*Localização',
        r'Concede[\w\s]* Transferência de Titularidade',
        r'Retifica a razão social',
        r'Revoga[r]*',
        r'Concede[r]* prorrogação d[eo] prazo d[ae] validade',
        r'SUSPENDER TEMPORARIAMENTE'
    ]

    type2function = {
        type_list[0]: 'erratum',
        type_list[1]: 'asv',
        type_list[2]: 'lo',
        type_list[3]: 'ls',
        type_list[4]: 'implantation_license',
        type_list[5]: 'll',
        type_list[6]: 'tt',
        type_list[7]: 'rrs',
        type_list[8]: 'revogar',
        type_list[9]: 'deadline_extension',
        type_list[10]: 'temporary_suspend'
    }

    regs = []

    for page in pages:    
        # verifica quantas portarias existem nessa página e onde é o início de cada uma (para casos em que haja mais de uma portaria por página)
        ordinance_text_index = [i for i in range(len(page)) if page.lower().startswith('PORTARIA SEMATUR'.lower(), i)]
        
        for ord_index in range(len(ordinance_text_index)):
            # separa o texto de cada portaria para ser analisada individualmente
            
            try:
                ordinance_text = page[ordinance_text_index[ord_index] : ordinance_text_index[ord_index+1]]
            except IndexError:
                ordinance_text = page[ordinance_text_index[ord_index] :]
        
            for ord_type in type_list:
                # print(ordinance_text)

                # verifica se o tipo da portaria é conhecido de acordo com o vetor "type_list"
                if len(re.findall(ord_type, ordinance_text)) > 0:

                    try:
                        # chama a função que irá processar a portaria de acordo com o dicionário "type2function"
                        reg = getattr(text_processing, type2function[ord_type])(ordinance_text.replace('-','–'), search_date, dom_link)
                        
                        regs.append(reg)
                        
                        publisher.publish('NEW_ORDINANCE', reg)

                        # is_found = 2
                    except IndexError:
                        try:
                            ordinance_text = page[ordinance_text_index[ord_index] : ordinance_text_index[ord_index+2]]
                            
                            reg = getattr(text_processing, type2function[ord_type])(ordinance_text.replace('-','–'), search_date, dom_link)
                        
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
    
