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
    mask_ordinance = r' (\d+/\d+ ?)'
    mask_process = r'\d*.\d*.TEC.\w*.\d*'
    mask_deadline = r'VALIDADE: (\d*)'
    mask_cpf = r'\d*\.\d*\.\d*–\d*|\d*[\.\s]\d*[\.\s]\d*/\d*–\s*\d*'
    mask_operation = r'ATIVIDADE: (.*)PROCESSO'
    issuer_name = 'Riachão das Neves'
    issuer = 3451478
    
    labels = [
        "ordinance_type", 
        "ordinance_number", 
        "process", 
        "publish_date",
        "owner_id", 
        "issuer_name", 
        "issuer", 
        "term", 
        "link"
    ]
    
    # licença simplificada
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

    # licença de operação
    def lo(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-')
        doc_number = re.findall(text_processing.mask_cpf, page_text)[1].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        deadline = deadline[0] + ' ano(s)'
        operation = re.findall(text_processing.mask_operation, page_text)[0]

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.OPERATION_LICENSE, 
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

    # licença unificada
    def lu(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-')
        doc_number = re.findall(text_processing.mask_cpf, page_text)[1].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        deadline = deadline[0] + ' ano(s)'
        operation = re.findall(text_processing.mask_operation, page_text)[0]

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
        
        reg['details'] = {
            'operation': operation
        }
        
        return reg

    # licença prévia
    def lp(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-')
        doc_number = re.findall(text_processing.mask_cpf, page_text)[1].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        deadline = deadline[0] + ' ano(s)'
        operation = re.findall(text_processing.mask_operation, page_text)[0]

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.PRELIMINARY_LICENSE, 
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
    
    # licença de implantação
    def limp(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-')
        doc_number = re.findall(text_processing.mask_cpf, page_text)[1].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        deadline = deadline[0] + ' ano(s)'
        operation = re.findall(text_processing.mask_operation, page_text)[0]

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
        
        reg['details'] = {
            'operation': operation
        }
        
        return reg

    # licença de instalação
    def linst(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-')
        doc_number = re.findall(text_processing.mask_cpf, page_text)[1].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        deadline = deadline[0] + ' ano(s)'
        operation = re.findall(text_processing.mask_operation, page_text)[0]

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.INSTALLATION_LICENSE, 
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

    # Supressão de vegetão nativa
    def asv(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-')
        doc_number = re.findall(text_processing.mask_cpf, page_text)[1].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)
        deadline = deadline[0] + ' ano(s)'

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.VEGETAL_SUPPRESSION, 
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

    def tt(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-')
        doc_number = re.findall(text_processing.mask_cpf, page_text)
        deadline = re.findall(text_processing.mask_deadline, page_text)
        deadline = deadline[0] + ' ano(s)'
        
        regs = []
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.OWNERSHIP_TRANSFER, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: None, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, # prazo
            text_processing.labels[8]: dom_link,
            'details': {
                'from_doc_number':doc_number[1].replace('–','-'),
                'to_doc_number':doc_number[3].replace('–','-')
            }
        }))
        
        regs.append(reg)
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.OWNERSHIP_TRANSFER, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: None, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: deadline, # prazo
            text_processing.labels[8]: dom_link,
            'details': {
                'from_doc_number':doc_number[2].replace('–','-'),
                'to_doc_number':doc_number[4].replace('–','-')
            }
        }))
        
        regs.append(reg)
        
        return regs
           

    def erratum(page_text, search_date, dom_link):
        mask_original = r'ONDE\s*SE\s*L[EÊ]:\s*.*\s*LEIA\s*–\s*SE'
        mask_correction = r'LEIA\s*–\s*SE:\s*.*\s*Riachao das Neves'
        
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        before = re.findall(mask_original, page_text)[0][:-9]
        after = re.findall(mask_correction, page_text)[0][:-17]
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.ERRATUM, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: None, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: None, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, # prazo
            text_processing.labels[8]: dom_link,
            'details': {
                'before':before,
                'after':after
            }
        }))

        return reg

    
def _import_date(search_date):
    type_list = [
        r'TIPO\s*DE\s*LICENCA:\s*LICENCA\s*SIMPLIFICADA',
        r'TIPO\s*DE\s*LICENCA:\s*LICENCA\s*PR[ÉE]VIA',
        r'TIPO\s*DE\s*LICENCA:\s*LICENCA.*OPERA[CG][ÃA]O',
        r'TIPO\s*DE\s*LICENCA:\s*LICENCA\s*UNIFICADA',
        r'TIPO\s*DE\s*LICENCA:\s*LICENCA.*IMPLANTA[CG][ÃA]O',
        r'TIPO\s*DE\s*LICENCA:\s*LICENCA.*LOCALIZA[CG][ÃA]O',
        r'TIPO\s*DE\s*LICENCA:\s*LICENCA.*INSTALA[CG][ÃA]O',
        r'AUTORIZA[CG]AO\s*[PARA|DE]*\s*SUPRESSAO\s*DA\s*VEGETA[CG]AO\s*NATIVA',
        r'ERRATA\s*D[AE]\s*PORTARIA',
        r'TRANSFER[ÉE]NCIA\s*DE\s*TITULARIDADE'
    ]

    type2function = {
        type_list[0]: 'ls',
        type_list[1]: 'lp',
        type_list[2]: 'lo',
        type_list[3]: 'lu',
        type_list[4]: 'limp',
        type_list[5]: 'll',
        type_list[6]: 'linst',
        type_list[7]: 'asv',
        type_list[8]: 'erratum',
        type_list[9]: 'tt'          
    }


    files, folder, links = pdfutils.dom_riachao_neves(search_date)

    regs = []
    for file, link in zip(files, links):
        pages = pdfutils.ocr_extract_page_text(file)
        print("Reading file")

        for page in pages:
            ordinance_text = page
            for ord_type in type_list:
                # verifica se o tipo da portaria é conhecido de acordo com o vetor "type_list"
                if len(re.findall(ord_type, ordinance_text.upper())) > 0:
                    try:
                        # chama a função que irá processar a portaria de acordo com o dicionário "type2function"
                        reg = getattr(text_processing, type2function[ord_type])(ordinance_text.replace('-','–'), search_date, link)

                        if type(reg) == list:
                            for r in reg: 
                                regs.append(r)

                                publisher.publish('NEW_ORDINANCE', r)
                                
                                print('')
                        else:
                            regs.append(reg)

                            publisher.publish('NEW_ORDINANCE', reg)
                            print('')

                        
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
    
