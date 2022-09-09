#coding: utf-8
import json, re, traceback, shutil
from .functions import pdfutils
from .functions.utils import ordinance_type
from ... import publisher
from datetime import datetime, timedelta

#  
#  name: processamento do texto
#  @ param: texto, data da análise e link para documento
#  @ return: pd.Series
#  
class text_processing:

    mask_ordinance = r'PORTARIA [SEMATUR ]*N°. (\d*), DE[\w\s]*DE[\w\s]*(\d{4})'
    # mask_process = r'\d*.\d*.TEC.\w*.\d*'
    # mask_process = r'\d*.\d*.\d*/\s*\w*/\w*[–|_]\s*\d*|\d*[–|_]\d*/\w*/\w*[–|_]\d*'
    mask_process = r'\d*\.\s*\d*\.\d*/\s*\w*/\w*–\s*\d*|\d*–\d*/\w*/\w*–\d*|\d*-\d*/\w*/\w*–\d*'
    # mask_process = r'\d*\s*.\s*\d*[./]TEC[./]\w*.\d*'
    mask_deadline = r'(\d{2}?)[(\w) ]*ano[s]*|v[aá]lida por (\d*)'
    mask_name = r'[a|à] ([\w\s_/.–]*?)[,]* insc'
    # mask_cpf = r'\d*\.\d*\.\d*–\d*|\d*[\.\s]\d*[\.\s]\d*/\d*–\d*'
    mask_cpf = r'\d*\.\d*\.\d*–\d*|\d*[\.\s]\d*[\.\s]\d*/\d*–\s*\d*'
    issuer_name = 'São Desidério'
    issuer = 3449304
    labels = ["ordinance_type", "ordinance_number", "process", "publish_date", "owner_id", "issuer_name", "issuer", "term", "link"]
    
    def ls(text, search_date, dom_link):
        aux = re.findall(text_processing.mask_ordinance, text)
        n_ordinance = f'{aux[0][0]}/{aux[0][1]}'
        
        process = re.findall(text_processing.mask_process, text)[0]
        
        try:
            doc_number = re.findall(text_processing.mask_cpf, text)[1]
        except:
            doc_number = re.findall(text_processing.mask_cpf, text)[0]

        deadline = re.findall(text_processing.mask_deadline, text)
        deadline = deadline[0][0] + deadline[0][1] + ' ano(s)'

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
       
        return reg

    def lu(text, search_date, dom_link):
        aux = re.findall(text_processing.mask_ordinance, text)
        n_ordinance = f'{aux[0][0]}/{aux[0][1]}'
        
        process = re.findall(text_processing.mask_process, text)[0]
        
        try:
            doc_number = re.findall(text_processing.mask_cpf, text)[1]
        except:
            doc_number = re.findall(text_processing.mask_cpf, text)[0]

        deadline = re.findall(text_processing.mask_deadline, text)
        deadline = deadline[0][0] + deadline[0][1] + ' ano(s)'

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.UNIFIED_LICENSE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: dom_link
        }))
       
        return reg

    def license_renewal(text, search_date, dom_link):
        mask_renov_type = r'CONCEDER[:\s]*RENOVA[GC]AO\s*DE\s*LICEN[GCÇ]A\s*DE\s*(.*?) '
        labels = ['ordinance_number', 'process', 'publish_date', 'grant_type', 'renovation_type', 'owner_name', 'doc_number', 'deadline', 'city_name', 'link']
        
        aux = re.findall(text_processing.mask_ordinance, text)
        n_ordinance = f'{aux[0][0]}/{aux[0][1]}'
        
        process = re.findall(text_processing.mask_process, text)[0]
        
        try:
            doc_number = re.findall(text_processing.mask_cpf, text)[1]
        except:
            doc_number = re.findall(text_processing.mask_cpf, text)[0]
        deadline = re.findall(text_processing.mask_deadline, text)
        deadline = deadline[0][0] + deadline[0][1] + ' ano(s)'

        renov_type = re.findall(mask_renov_type, text.upper())[0]
        
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
    
    def condition_review(ordinance_text, search_date, link):
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
            text_processing.labels[8]: link
        }))
       
        reg['details'] = {'origin_ordinance': origin_ordinance}
        
        return reg    


    def asv(text, search_date, link):
        aux = re.findall(text_processing.mask_ordinance, text)
        n_ordinance = f'{aux[0][0]}/{aux[0][1]}'
        
        process = re.findall(text_processing.mask_process, text)[0]
        doc_number = re.findall(text_processing.mask_cpf, text)[1]
        
        deadline = re.findall(text_processing.mask_deadline, text)
        deadline = deadline[0][0] + deadline[0][1] + ' ano(s)'
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.VEGETAL_SUPPRESSION, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: link
        }))
       
        return reg

    def tt(text, search_date, link):
        aux = re.findall(text_processing.mask_ordinance, text)
        n_ordinance = f'{aux[0][0]}/{aux[0][1]}'
        
        process = re.findall(text_processing.mask_process, text)[0]
        doc_number = re.findall(text_processing.mask_cpf, text)
        old_doc = doc_number[0]
        new_doc = doc_number[1]
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.OWNERSHIP_TRANSFER, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: old_doc, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link
        }))
       
        reg['details'] = {'to': new_doc}
        
        return reg
      
    def operation_license(ordinance_text, search_date, link):
        mask_operation = r'operação [\w_/. ]*'
            
        process = re.findall(text_processing.mask_process, ordinance_text)[0].replace(' ', '').replace('_','–')
        n_ordinance = f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}'
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('_','–')
        
        try:
            operation = re.findall(mask_operation, ordinance_text)[0].replace('_','–')
        except:
            operation = None
        
        deadline = re.findall(text_processing.mask_prazo, ordinance_text)[0][9:]
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.SIMPLIFIED_ENVIRONMENTAL_LICENSE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: link
        }))
       
        reg['details'] = {
            'operation': operation
        }
        
        return reg

    def extension_expiry_date(ordinance_text, search_date, link):
        mask_processo_num = r'tendo em vista o que consta do Processo nº (.*?), RESOLVE'
        mask_prorrogacao = r'Conceder PRORROGAÇÃO D[A–Z]{1} PRAZO DE VALIDADE,(.*?). Art'

        n_ordinance = str(f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}')
        process = re.findall(mask_processo_num, ordinance_text)[0]
        portaria_prorrogacao = re.findall(mask_prorrogacao, ordinance_text)[0]

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.SIMPLIFIED_ENVIRONMENTAL_LICENSE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: None, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link
        }))
       
        reg['details'] = {
            'prorrogration': portaria_prorrogacao
        }
    
        return reg
    
    def erratum(text, search_date, link):
        mask_ordinance = r'PORTARIA N°(\d*/\d*)—_'

        n_ordinance = re.findall(mask_ordinance, text)[0]
        old_text = re.findall(r'Onde\s*[LI][ée]-se\s*:\s*(.*)\s*Leia', text)[0]
        new_text = re.findall(r'Leia-se\s*:\s*(.*)\s*Gab', text)[0]

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
    

    def prad(text, search_date, link):
        
        process = re.findall(text_processing.mask_process, text)[0].replace('_', '–')
        doc_number = re.findall(text_processing.mask_cpf, text)[0].replace('_', '–')
        
        reg = json.loads(json.dumps({
            # TODO tipo de portaria no backend ainda não foi desenvolvido 
            text_processing.labels[0]: ordinance_type.PRAD, 
            # TODO não tem valor de portaria
            text_processing.labels[1]: None, 
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
    
    def deadline_extension(ordinance_text, search_date, dom_link):
        process = re.findall(text_processing.mask_process, ordinance_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0]
        deadline = re.findall(text_processing.mask_deadline, ordinance_text)[0][11:] + ' anos'
        n_ordinance = re.findall(text_processing.mask_ordinance, ordinance_text)[0]
        changed_ordinance = re.findall(text_processing.mask_ordinance, ordinance_text)[2]

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.DEADLINE_EXTENSION, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: dom_link
        }))
       
        reg['details'] = {'changed_ordinance': changed_ordinance}
        
        return reg

    def preliminary_license(ordinance_text, search_date, link):
        mask_operation = r'para [\w_/. ]*'
        
        process = re.findall(text_processing.mask_process, ordinance_text)[0].replace(' ', '').replace('_','–')
        n_ordinance = f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}'
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('_','–')
        deadline = re.findall(text_processing.mask_prazo, ordinance_text)[0][9:]

        try:
            operation = re.findall(mask_operation, ordinance_text)[0][5:].replace('_','–')
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

    # licença de implantação
    def implantation_license(text, search_date, dom_link):
        n_ordinance = str(re.findall(text_processing.mask_ordinance, text)[0])
        process = re.findall(text_processing.mask_process, text)[0]
        doc_number = re.findall(text_processing.mask_cpf, text)[0]
        deadline = re.findall(text_processing.mask_deadline, text)[0][11:] + ' anos'
        try:
            area = re.findall(text_processing.mask_area, text)[0]
        except Exception:
            area = None

        try:
            volume_production = re.findall(text_processing.mask_volume_production, text)[0]
        except Exception:
            volume_production = None

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.IMPLANTATION_LICENSE, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: dom_link
        }))
       
        reg['details'] = {'area': area, 'prod_volume': volume_production}
        
        return reg

    # licença de localização
    def location_license(text, search_date, dom_link):
        n_ordinance = str(re.findall(text_processing.mask_ordinance, text)[0])
        process = re.findall(text_processing.mask_process, text)[0]
        doc_number = re.findall(text_processing.mask_cpf, text)[0]
        deadline = re.findall(text_processing.mask_deadline, text)[0][11:] + ' anos'
        try:
            area = re.findall(text_processing.mask_area, text)[0]
        except Exception:
            area = None

        try:
            volume_production = re.findall(text_processing.mask_volume_production, text)[0]
        except Exception:
            volume_production = None

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
        
            reg['details'] = {'area': area, 'prod_volume': volume_production}
            
            return reg

    def dismissal_license(text, search_date, dom_link):
        aux = re.findall(text_processing.mask_ordinance, text)
        n_ordinance = f'{aux[0][0]}/{aux[0][1]}'
        
        process = re.findall(text_processing.mask_process, text)[0]
        doc_number = re.findall(text_processing.mask_cpf, text)[0].replace(' ', '')
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.LICENSE_DISMISSAL, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: dom_link
        }))
       
        return reg



def _import_date(search_date):
    type_list = [
        r'CONCEDER[:\s]*LICEN[GCÇ]A\s*SIMPLIFICADA',
        r'CONCEDER[:\s]*LICEN[GCÇ]A\s*UNIFICADA',
        r'CONCEDER[:\s]*RENOVA[GC][AÃ]O\s*DE\s*LICEN[GCÇ]A',
        r'CONCEDER[:\s]*AUTORIZA[GC][AÃ]O\s*DE\s*SUPRESS[AÃ]O\s*DE\s*VEGETA[GCÇ][AÃ]O\s*NATIVA',
        r'TRANSFERIR.*TITULARIDADE',
        r'CONCEDER[:\s]*LICEN[GCÇ]A\s*DE\s*OPERAÇ[AÃ]O,',
        r'CONCEDER\s*PRORROGA[CGÇ][AÃ]O\s*DO\s*PRAZO\s*DE\s*VALIDADE',
        r'ERRATA\s*[ÀA]\s*PORTARIA',
        r'ALTERAR\s*.*\s*RAZ[AÃ]O\s*SOCIAL',
        r'PLANO\s*DE\s*RECUPERAÇÃO\s*DE\s*[ÁREAS]*\s*DEGRADADA[S]+',
        r'CONCEDE[r]*\s*PRORROGA[GÇC][AÃ]O\s*D[EO]\s*PRAZO\s*D[AE]\s*VALIDADE',
        r'CONCEDER[:\s]*LICEN[CGÇ]A PR[EÉ]VIA,',
        r'CONCEDER REVISÃO DO CONDICIONANTE',
        r'CONCEDER[:\s]*LICEN[GCÇ]A\[\w\s]*IMPLANTA[GÇC][AÃ]O',
        r'CONCEDER[:\s]*LICEN[GCÇ]A[\w\s]*LOCALIZA[GÇC][AÃ]O',
        r'CONCEDER\s*DISPENSA\s*DE\s*LICEN[GC]A'
    ]

    type2function = {
        type_list[0]: 'ls',
        type_list[1]: 'lu',
        type_list[2]: 'license_renewal',
        type_list[3]: 'asv',
        type_list[4]: 'tt',
        type_list[5]: 'operation_license',
        type_list[6]: 'extension_expiry_date',
        type_list[7]: 'erratum',
        type_list[8]: 'corporate_name_change',
        type_list[9]: 'prad',
        type_list[10]: 'deadline_extension',
        type_list[11]: 'preliminary_license',
        type_list[12]: 'condition_review',
        type_list[13]: 'implantation_license',
        type_list[14]: 'location_license',
        type_list[15]: 'dismissal_license'     
    }

    files, folder, links = pdfutils.dom_sao_desiderio(search_date)
    regs = []
    for file, link in zip(files, links):
        pages = pdfutils.ocr_extract_text(file)
        print("Reading file")

        for page in pages:
            ordinance_text = page.replace('-','–')
            for ord_type in type_list:
                # verifica se o tipo da portaria é conhecido de acordo com o vetor "type_list"
                if len(re.findall(ord_type, ordinance_text.upper())) > 0:
                    # print(ordinance_text)
                
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
    
