#coding: utf-8
import json, re, traceback, shutil
from .functions import pdfutils
from .functions.utils import ordinance_type
from ... import publisher
from datetime import datetime, timedelta

#  
#  name: processamento do texto
#  @ param: texto, data da análise e link para documento
#  @ return: json
#  
class text_processing:
    mask_ordinance = r'(\d+/\d+ ?)'
    mask_process = r'[Processo|processo] SEMMARH\s*[Nn]*.*\s*(.*), RESOLVE'
    mask_deadline = r'(\d{2}?)[(\w) ]*ano[s]*|v[aá]lida por (\d*)'
    mask_cpf = r'\d*\.\d*\.\d*–\d*|\d*[\.\s]\d*[\.\s]\d*/\d*–\s*\d*'
    mask_area = r'\d*,\d*\s*ha'
    
    issuer = 3465373
    issuer_name = 'Correntina'
    labels = ["ordinance_type", "ordinance_number", "process", "publish_date", "owner_id", "issuer_name", "issuer", "term", "link"]
    
    # autorização de supressão de vegetação nativa
    def asv(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        
        try: deadline = deadline[0][0] + deadline[0][1] + ' ano(s)'
        except: deadline = None
        
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

    
    # licença simplificada
    def ls(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        try: deadline = deadline[0][0] + deadline[0][1] + ' ano(s)'
        except: deadline = None

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.SIMPLIFIED_ENVIRONMENTAL_LICENSE, 
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


    # licença unificada
    def lu(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        try: deadline = deadline[0][0] + deadline[0][1] + ' ano(s)'
        except: deadline = None

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.UNIFIED_LICENSE, 
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

    # licença de localização
    def ll(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        try: deadline = deadline[0][0] + deadline[0][1] + ' ano(s)'
        except: deadline = None

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.LOCATION_LICENSE, 
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

    
    # licença de instalação
    def linst(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        try: deadline = deadline[0][0] + deadline[0][1] + ' ano(s)'
        except: deadline = None

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
        process = re.findall(text_processing.mask_process, page_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        try: deadline = deadline[0][0] + deadline[0][1] + ' ano(s)'
        except: deadline = None

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
        process = re.findall(text_processing.mask_process, page_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        try: deadline = deadline[0][0] + deadline[0][1] + ' ano(s)'
        except: deadline = None
        
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
        
        
    # aprovação de localização de reserva legal
    def legal_reserve(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        try: deadline = deadline[0][0] + deadline[0][1] + ' ano(s)'
        except: deadline = None

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.LEGAL_RESERVE_LOCATION_APPROVAL, 
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

    
    # dispensa de licença ambiental
    def dismissal_license(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        try: deadline = deadline[0][0] + deadline[0][1] + ' ano(s)'
        except: deadline = None

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.LICENSE_DISMISSAL, 
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


    # renovação de licenção ambiental
    def license_renewal(page_text, search_date, dom_link):
        mask_renov_type = r'CONCEDER[R]*\s*RENOVA[GC][AÃ]O\s*DE\s*LICEN[GCÇ]A\s*AMBIENTAL\s*[DE ]*(.*?) '
        
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]        
        process = re.findall(text_processing.mask_process, page_text)[0]        
        try:
            doc_number = re.findall(text_processing.mask_cpf, page_text)[1].replace('–','-')
        except:
            doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        try: deadline = deadline[0][0] + deadline[0][1] + ' ano(s)'
        except: deadline = None

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

    
    # transferência de titularidade
    def tt(page_text, search_date, link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]        
        process = re.findall(text_processing.mask_process, page_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, page_text)
        old_doc = doc_number[0].replace('–','-')
        new_doc = doc_number[1].replace('–','-')
        
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


    # licença préiva
    def preliminary_license(page_text, search_date, link):
        mask_operation = r'para [\w_/. ]*'
        
        process = re.findall(text_processing.mask_process, page_text)[0].replace(' ', '').replace('_','–')
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


    # razão social
    def corporate_name_change(ordinance_text, search_date, link):
        process = re.findall(text_processing.mask_process, ordinance_text)[0]
        n_ordinance = str(f'{re.findall(text_processing.mask_ordinance_number, ordinance_text)[0]}/{re.findall(text_processing.mask_year, ordinance_text)[0]}')
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0].replace('_','–')

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

        try:
            volume_production = re.findall(text_processing.mask_volume_production,ordinance_text)[0]
        except Exception:
            volume_production = None
            
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.LICENSE_REVOCATION, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.issuer_name, 
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
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, 
            text_processing.labels[8]: dom_link
        }))
       
        reg['details'] = {'changed_ordinance': changed_ordinance}
        
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
    

    # revisão de condicionantes
    def condition_review(ordinance_text, search_date, link):
        n_ordinance = re.findall(text_processing.mask_ordinance, ordinance_text)[0]
        process = re.findall(text_processing.mask_process, ordinance_text)[0]
        doc_number = re.findall(text_processing.mask_cpf, ordinance_text)[0]
        origin_ordinance = re.findall(text_processing.mask_ordinance, ordinance_text)[1]
                                        
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


def _import_date(search_date):
    type_list = [
        r'CONCEDER[R]*\s*[A ]*LICEN[CG]A[\w\s]*SIMPLIFICADA',
        r'CONCEDER[R]*\s*[A ]*LICEN[CG]A[\w\s]*UNIFICADA',
        r'CONCEDER[R]*\s*[A ]*LICEN[CG]A[\w\s]*LOCALIZA[GC]AO',
        r'CONCEDER[R]*\s*[A ]*LICEN[CG]A[\w\s]*INSTALA[GC]AO',
        r'CONCEDER[R]*\s*[A ]*LICEN[CG]A[\w\s]*IMPLANTA[GC]AO',
        r'CONCEDER[R]*\s*[A ]*LICEN[CG]A[\w\s]*OPERA[GC]AO',
        r'CONCEDER[R]*\s*[A ]*LICEN[CG]A[\w\s]*PR[ÉE]VIA',
        r'CONCEDER[R]*\s*[A ]*APROVA[CG]AO\s*DE\s*LOCALIZA[GC]AO\s*DE\s*RESERVA\s*LEGAL',
        r'CONCEDER[R]*\s*[A ]*AUTORIZA[CG]AO\s*PARA\s*SUPRESSAO\s*DA\s*VEGETA[CG]AO\s*NATIVA',
        r'CONCEDER[R]*\s*[A ]*DISPENSA\s*DE\s*LICENCA\s*AMBIENTAL',
        r'CONCEDER[R]*\s*RENOVA[GC][AÃ]O\s*DE\s*LICEN[GCÇ]A',
        r'TRANSFERIR.*TITULARIDADE',
        r'ALTERAR|RETIFICA\s*.*\s*RAZ[AÃ]O\s*SOCIAL',
        r'REVOGAR[R]*',
        r'CONCEDER[R]*\s*[A ]*PRORROGA[GC]AO\s*D[EO]\s*PRAZO\s*D[AE]\s*VALIDADE',
        r'ERRATA',
        r'REVIS[AÃ]O\s*DO\s*CONDICIONANTE'
    ]

    type2function = {
        type_list[0]: 'ls',
        type_list[1]: 'lu',
        type_list[2]: 'll',
        type_list[3]: 'linst',
        type_list[4]: 'limp',
        type_list[5]: 'lo',
        type_list[6]: 'preliminary_license',
        type_list[7]: 'legal_reserve',
        type_list[8]: 'asv',
        type_list[9]: 'dismissal_license',
        type_list[10]: 'license_renewal',
        type_list[11]: 'tt',
        type_list[12]: 'corporate_name_change',
        type_list[13]: 'revogar',
        type_list[14]: 'deadline_extension',
        type_list[15]: 'erratum',
        type_list[16]: 'condition_review'
    }
    
    files, folder, links = pdfutils.dom_correntina(search_date)

    regs = []

    for file, dom_link in zip(files, links):
        pages = pdfutils.ocr_extract_page_text(file)
        print("Reading file")

        for page in pages:
        # verifica quantas portarias existem nessa página e onde é o início de cada uma (para casos em que haja mais de uma portaria por página)
            ordinance_text_index = [i for i in range(len(page)) if page.upper().startswith('PORTARIA SEMMARH', i)]

            for ord_index in range(len(ordinance_text_index)):
                
                # separa o texto de cada portaria para ser analisada individualmente
                try:
                    ordinance_text = page[ordinance_text_index[ord_index] : ordinance_text_index[ord_index+1]]
                except IndexError:
                    ordinance_text = page[ordinance_text_index[ord_index] :]

                for ord_type in type_list:
                    # verifica se o tipo da portaria é conhecido de acordo com o vetor "type_list"
                    if len(re.findall(ord_type, ordinance_text.upper())) > 0:
                        try:
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
    
