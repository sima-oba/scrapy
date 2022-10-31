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

    #mask_ordinance_number = r'\d{2}\.\d{3}'
    mask_ordinance = r'[Portaria|PORTARIA]\s*[nN].\s*(\d*/\d*)'
    mask_year = r'\d{4}'
    mask_cpf = r'\d*\.\d*\.\d*–\d*|\d*[\.\s]\d*[\.\s]\d*/\d*–\s*\d*'
    mask_process = r'[Pp]rocesso [Nn][.*][°*]\s*(.*)[,.]\s*RESOLVE'
    mask_deadline = r'(\d{2}?)[(\w) ]*ano[s]*|v[aá]lida\s*por\s*(\d*)'
    mask_lat = r'Lat.[\d\s]*[°|º][\d\s]*[’ ]*[\d,\s]*["|”]\w'
    mask_longitude = r'Long.[\d\s]*[°|º][\d\s]*[’ ]*[\d,\s]*["|”]\w'
    mask_operation = r'para [\w_/. ]*'

    issuer = 6324151
    issuer_name = 'Luís Eduardo Magalhães'
    labels = ["ordinance_type", "ordinance_number", "process", "publish_date", "owner_id", "issuer_name", "issuer", "term", "link"]
    
    
    def license_renewal(page_text, search_date, dom_link):
        mask_renov_type = r'CONCEDE[R]*[:\s]*RENOVA[GC]AO\s*DE\s*LICEN[GCÇ]A\s*[DE\s](.*?),'
        
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-').replace(' ','')
        
        try:
            doc_number = re.findall(text_processing.mask_cpf, page_text)[1].replace('–','-')
        except:
            doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')

        deadline = re.findall(text_processing.mask_deadline, page_text)[0][0] + ' anos'

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


    def asv(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-').replace(' ','')
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)[0][0] + ' anos'

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
    
    # recuperação de área degradada
    def prad(text, search_date, link):
        n_ordinance = re.findall(text_processing.mask_ordinance, text)[0]
        process = re.findall(text_processing.mask_process, text)[0].replace('–','-')
        doc_number = re.findall(text_processing.mask_cpf, text)[0].replace('–','-')
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.DEGRADED_AREA_RECOVERY_PLAN, 
            # TODO não tem valor de portaria
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

    # licença de operação
    def lo(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-').replace(' ','')
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)[0][0] + ' anos'
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
    def unified_license(text, search_date, link):
        n_ordinance = re.findall(text_processing.mask_ordinance, text)[0]
        process = re.findall(text_processing.mask_process, text)[0].replace('–','-').replace(' ','')
        deadline = re.findall(text_processing.mask_deadline, text)[0][0] + ' anos'
        doc_number = re.findall(text_processing.mask_cpf, text)[0].replace('–','-')

        try:
            operation = re.findall(text_processing.mask_operation, text)[0][5:].replace('–','-')
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
            text_processing.labels[8]: link,
            'details': None
        }))
       
        reg['details'] = {
            'operation': operation
        }
        return reg
    
    # licença de implantação
    def limp(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-').replace(' ','')
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)[0][0] + ' anos'
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

    # licença prévia
    def lp(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-').replace(' ','')
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)[0][0] + ' anos'
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

    # errata
    def erratum(text, search_date, link):
        mask_ordinance = r'PORTARIA .* (\d*) DE \d* DE[\w\s]*DE\s*(\d{4}),'
        mask_original = r'ONDE\s*SE\s*L[EÊ]:\s*.*\s*LEIA\s*–\s*SE'
        mask_correction = r'LEIA\s*–\s*SE:\s*.*\s*Luis'
        
        aux = re.findall(mask_ordinance, text.upper())
        n_ordinance = f'{aux[0][0]}/{aux[0][1]}'
        before = re.findall(mask_original, text)[0][11:-9]
        after = re.findall(mask_correction, text)[0][8:-4]
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.ERRATUM, 
            text_processing.labels[1]: n_ordinance, 
            text_processing.labels[2]: None, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: None, 
            text_processing.labels[5]: text_processing.issuer_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, # prazo
            text_processing.labels[8]: link,
            'details': {
                'before':before,
                'after':after
            }
        }))

        return reg

    # revogar licença
    def revogar(text, search_date, dom_link):
        n_ordinance = str(re.findall(text_processing.mask_ordinance,text)[0])
        process = re.findall(text_processing.mask_process,text)[0]
        doc_number = re.findall(text_processing.mask_cpf,text)[0].replace('–','-').replace(' ','')
        deadline = re.findall(text_processing.mask_deadline, text)[0][0] + ' anos'
            
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
       
        
        return reg

    # transferência de titularidade
    def tt(page_text, search_date, link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-')
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

    # prorrogação de prazo de validade
    def deadline_extension(text, search_date, dom_link):
        process = re.findall(text_processing.mask_process, text)[0]
        doc_number = re.findall(text_processing.mask_cpf, text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, text)[0][0] + ' anos'
        n_ordinance = re.findall(text_processing.mask_ordinance, text)[0]
        changed_ordinance = re.findall(text_processing.mask_ordinance, text)[1]

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

    # revisão de condicionante
    def condition_review(text, search_date, dom_link):
        process = re.findall(text_processing.mask_process, text)[0]
        doc_number = re.findall(text_processing.mask_cpf, text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, text)[0][0] + ' anos'
        n_ordinance = re.findall(text_processing.mask_ordinance, text)[0]
        changed_ordinance = re.findall(text_processing.mask_ordinance, text)[1]

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
       
        reg['details'] = {'origin_ordinance': changed_ordinance}
        
        return reg

    # licença de instalação
    def linst(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-').replace(' ','')
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        deadline = re.findall(text_processing.mask_deadline, page_text)[0][0] + ' anos'
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

    # Dispensa de licença
    def dismissal_license(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-')
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        
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
        
    # reserva legal
    def legal_reserve(page_text, search_date, dom_link):
        mask_process = r'\d*.\d*.TEC.\w*.\d*'
    
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(mask_process, page_text)[0].replace('–','-')
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.LEGAL_RESERVE_LOCATION_APPROVAL, 
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

    # Retífica de razão social
    def corporate_name_change(page_text, search_date, dom_link):
        n_ordinance = re.findall(text_processing.mask_ordinance, page_text)[0]
        process = re.findall(text_processing.mask_process, page_text)[0].replace('–','-')
        doc_number = re.findall(text_processing.mask_cpf, page_text)[0].replace('–','-')
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.OWNER_NAME_CHANGE, 
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
        r'CONCEDE[R]*\s*LICEN[GÇC]*A\s*AMBIENTAL*\s*UNIFICADA',
        r'CONCEDE[R]*\s*RENOVA[GÇC]*[AÃ]O\s*DE\s*LICEN[CÇG]*A',
        r'CONCEDE[R]*\s*AUTORIZA[GÇC]*[AÃ]O\s*PARA\s*SUPRESS[AÃ]O\s*D[EA]\s*VEGETA[CÇG]*[AÃ]O\s*NATIVA',
        r'CONCEDE[R]*\s*LICEN[CÇG]A\s*AMBIENTAL*\s*DE\s*OPERA[CÇG]*AO',
        r'CONCEDE[R]*\s*LICEN[CÇG]A\s*AMBIENTAL*\s*DE\s*IMPLANTA[CÇG][AÃ]O',
        r'APROVAR\s*O\s*PLANO\s*DE\s*RECUPERA[CÇG]*AO\s*DE\s*[ÁA]REA[S]*\s*DEGRADADA[S]*',
        r'CONCEDE[R]*\s*LICEN[CÇG]*A\s*AMBIENTAL*\s*PR[ÉE]VIA',
        r'ERRATA:\s*PORTARIA',
        r'REVOGA[R]*' ,
        r'CONCEDE[R]*\s*LICEN[GÇC]*A\s*AMBIENTAL*\s*SIMPLIFICADA',
        r'TRANSFERIR.*TITULARIDADE',
        r'CONCEDER[R]*\s*[A ]*PRORROGA[GC]AO\s*D[EO]\s*PRAZO\s*D[AE]\s*VALIDADE',
        r'CONCEDE[R]\s*REVIS[ÃA]O\s*D[OE]\s*CONDICIONANTE[S]',    
        r'CONCEDE[R]*\s*LICEN[CÇG]A\s*AMBIENTAL*\s*DE\s*INSTALA[CÇG]*AO',
        r'CONCEDE[R]*\s*LICEN[CÇG]A\s*AMBIENTAL*\s*DE\s*LOCALIZA[CÇG][AÃ]O',
        r'APROVA[CÇG][AÃ]O\s*DE\s*LOCALIZA[CÇG][AÃ]O\s*OU\s*RELOCA[CÇG][AÃ]O\s*DE\s*RESERVA',
        r'ALTERAR|RETIFICA\s*.*\s*RAZ[AÃ]O\s*SOCIAL',
        r'CONCEDER[R]*\s*[A ]*DISPENSA\s*DE\s*LICEN[GC]A\s*AMBIENTAL'        
    ]

    type2function = {
        type_list[0]: 'unified_license',
        type_list[1]: 'license_renewal',
        type_list[2]: 'asv',
        type_list[3]: 'lo',
        type_list[4]: 'limp',
        type_list[5]: 'prad',
        type_list[6]: 'lp',
        type_list[7]: 'erratum',
        type_list[8]: 'revogar',
        type_list[9]: 'ls',
        type_list[10]:'tt',
        type_list[11]:'deadline_extension',
        type_list[12]:'condition_review' ,
        type_list[13]:'linst',
        type_list[14]:'ll',
        type_list[15]:'legal_reserve',
        type_list[16]:'corporate_name_change',
        type_list[17]:'dismissal_license'   
    }

    files, folder, links = pdfutils.lem_dom(search_date)
    
    # files = ['documentos-luis/aprovacao_localizacao_reserva.pdf']
    # links = ['']

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
    