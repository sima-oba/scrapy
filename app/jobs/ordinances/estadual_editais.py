#coding: utf-8
#coding: utf-8
import json, re, traceback, requests
from bs4 import BeautifulSoup
from uuid import uuid4
from .functions.utils import ordinance_type
from ... import publisher
from datetime import datetime, timedelta
from .estadual import busca_id

URL = "https://dool.egba.ba.gov.br"

class text_processing:
    mask_cpf = r'\d{3}\.\d{3}\.\d{3}[-|_]\d{2}|\d{2}\.\d*\.\d*/\d*[-|_]\d*'
    mask_process = r'\d*\.\s*\d*\.\d*/\s*\w*/\w*[-|_]\s*\d*|\d*[-|_]\d*/\w*/\w*[-|_]\d*'
    mask_obs = r'\“(.*?)\”'

    issuer = 3471168
    city_name = 'Bahia'
    kafka_topic = 'NEW_ORDINANCE'
    labels = ["ordinance_type", "ordinance_number", "process", "publish_date", "owner_id", "issuer_name", "issuer", "term", "link"]
    
        
    # Auto de infração de multa
    def fine_infraction_notice(text, search_date, link):
        process = re.findall(text_processing.mask_process, text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, text)[0].replace('_', '-')
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.FINE_INFRACTION, 
            text_processing.labels[1]: str(uuid4()), 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.city_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))
        
        return reg

    # Auto de infração de apreensão
    def arrest_infraction_notice(text, search_date, link):
        process = re.findall(text_processing.mask_process, text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, text)[0].replace('_', '-')
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.INTERDICTION_INFRACTION, 
            text_processing.labels[1]: str(uuid4()), 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.city_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))
        
        return reg

    # Auto de infração de advertência
    def warning_infraction_notice(text, search_date, link):
        mask_observation = r'\“[^\.]*'
        
        process = re.findall(text_processing.mask_process, text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, text)[0].replace('_', '-')
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.INFRACTION_WARNING, 
            text_processing.labels[1]: str(uuid4()), 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.city_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))

        try:
            observation = re.findall(mask_observation, text)[0].replace('_', '-')
            reg['details'] = {'observation': observation}
        except:
            reg['details'] = None
        
        return reg

    # Auto de infração de interdição temporária
    def temporary_interdiction(text, search_date, link):
        process = re.findall(text_processing.mask_process, text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, text)[0].replace('_', '-')
            
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.TEMPORARY_INTERDICTION_NOTICE, 
            text_processing.labels[1]: str(uuid4()), 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.city_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))
        
        try:
            observation = re.findall(text_processing.mask_obs, text)[0].replace('_', '-')
            reg['details'] = {'observation': observation}
        except:
            reg['details'] = None
        
        return reg
    
    # Penalidade de demolição
    def demolition(text, search_date, link):
        process = re.findall(text_processing.mask_process, text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, text)[0].replace('_', '-')
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.DEMOLITION_PENALTY, 
            text_processing.labels[1]: str(uuid4()), 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.city_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))
        
        return reg
    
    # Dívida ativa
    def active_debt(text, search_date, link):
        process = re.findall(text_processing.mask_process, text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, text)[0].replace('_', '-')
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.ACTIVE_DEBIT, 
            text_processing.labels[1]: str(uuid4()), 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.city_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))
        
        return reg

    # análise do processo
    def process_analysis(text, search_date, link):
        mask_dados = r'[RequerenteEQUERENTE]:\s*(.*?)[,;]\s*[CGPFNJ/]*:\s*(.*?)[,;]\s*'
        mask_process_type = r'[cC]uja\s*análise\s*d[eo]\s*processo\s*de\s*(.*?)\s*encontra_se'
        mask_obs = r'devido (.*?),'
        
        regs = []
        
        dados = re.findall(mask_dados, text)
        all_process = re.findall(text_processing.mask_process, text)
        process_type = re.findall(mask_process_type, text)[0]
        observation = re.findall(mask_obs, text)[0]
            
        for data in zip(dados, all_process):
            doc_number = data[0][1].replace('_', '-').replace('.-', '-')
            process = data[1].replace('_', '-')
            
            reg = json.loads(json.dumps({
                text_processing.labels[0]: ordinance_type.PROCESS_ANALYSIS, 
                text_processing.labels[1]: str(uuid4()), 
                text_processing.labels[2]: process, 
                text_processing.labels[3]: search_date, 
                text_processing.labels[4]: doc_number, 
                text_processing.labels[5]: text_processing.city_name, 
                text_processing.labels[6]: text_processing.issuer, 
                text_processing.labels[7]: None, 
                text_processing.labels[8]: link,
                'details': None
            }))
            
            reg['details'] = {'process_type': process_type,'observation': observation}
            
            regs.append(reg)
        
        return regs
    

    # Plano de recuperação de áreas degradadas
    def prad(text, search_date, link):
        process = re.findall(text_processing.mask_process, text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, text)[0].replace('_', '-')
                
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.DEGRADED_AREA_RECOVERY_PLAN, 
            text_processing.labels[1]: str(uuid4()), 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.city_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))
        
        return reg

    # Plano de Enriquecimento Vegetal
    def prev(text, search_date, link):
        process = re.findall(text_processing.mask_process, text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, text)[0].replace('_', '-')
        
        reg = json.loads(json.dumps({
            # TODO código do tipo
            text_processing.labels[0]: ordinance_type.PLANT_ENRICHMENT_PLAN, 
            text_processing.labels[1]: str(uuid4()), 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.city_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))
        
        return reg

    # penalidade de advertência
    def warning(text, search_date, link):
        process = re.findall(text_processing.mask_process, text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, text)[0].replace('_', '-')
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.PENALTY_WARNING, 
            text_processing.labels[1]: str(uuid4()), 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.city_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))
        
        try:
            observation = re.findall(text_processing.mask_obs, text)[0].replace('_', '-')
            reg['details'] = {'observation': observation}
        except:
            reg['details'] = None
                
        return reg

    # Plano de Gerenciamento de Resíduos Sólidos
    def pgrs(text, search_date, link):
        process = re.findall(text_processing.mask_process, text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, text)[0].replace('_', '-')
        
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.SOLID_WASTE_MANAGEMENT_PLAN, 
            text_processing.labels[1]: str(uuid4()), 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.city_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))
        
        try:
            observation = re.findall(text_processing.mask_obs, text)[0].replace('_', '-')
            reg['details'] = {'observation': observation}
        except:
            reg['details'] = None
        
        return reg

    # Embargo temporário
    def temporary_embargo(text, search_date, link):
        process = re.findall(text_processing.mask_process, text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, text)[0].replace('_', '-')
            
        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.TEMPORARY_EMBARGO, 
            text_processing.labels[1]: str(uuid4()), 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.city_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))
        
        try:
            observation = re.findall(text_processing.mask_obs, text)[0].replace('_', '-')
            reg['details'] = {'observation': observation}
        except:
            reg['details'] = None
        return reg

    # Documentos relacionados ao CEFIR
    def cefir(text, search_date, link):
        process = re.findall(text_processing.mask_process, text)[0].replace('_', '-')
        doc_number = re.findall(text_processing.mask_cpf, text)[0].replace('_', '-')

        reg = json.loads(json.dumps({
            text_processing.labels[0]: ordinance_type.CEFIR, 
            text_processing.labels[1]: str(uuid4()), 
            text_processing.labels[2]: process, 
            text_processing.labels[3]: search_date, 
            text_processing.labels[4]: doc_number, 
            text_processing.labels[5]: text_processing.city_name, 
            text_processing.labels[6]: text_processing.issuer, 
            text_processing.labels[7]: None, 
            text_processing.labels[8]: link,
            'details': None
        }))

        return reg

def _import_date(search_date):
    type_list = [
        r'AUTO\s*DE\s*INFRAÇÃO\s*DE\s*MULTA',
        r'PENALIDADE\s*DE\s*DEMOLIÇÃO',
        r'INSCRITO\s*EM\s*DÍVIDA\s*ATIVA',
        r'AUTO\s*DE\s*INFRAÇÃO\s*DE\s*APREENSÃO',
        r'CUJA\s*AN[ÁA]LISE\s*D[EO]\s*PROCESSO',
        r'PLANO\s*DE\s*RECUPERAÇÃO\s*DE\s*[ÁREAS]*\s*DEGRADADA[S]+',
        r'PLANO\s*[DE]*\s*ENRIQUECIMENTO\s*VEGETAL',
        r'PENALIDADE\s*DE\s*ADVERT[ÊE]NCIA',
        r'PGRS',
        r'AUTO\s*DE\s*INFRA[ÇC][AÃ]O\s*DE\s*ADVERT[ÊE]NCIA',
        r'INTERDI[ÇC][AÃ]O TEMPOR[AÁ]RIA',
        r'EMBARGO\s*TEMPOR[ÁA]RIO',
        r'CEFIR'
    ]

    type2function = {
        type_list[0]: 'fine_infraction_notice',
        type_list[1]: 'demolition',
        type_list[2]: 'active_debt',
        type_list[3]: 'arrest_infraction_notice',
        type_list[4]: 'process_analysis',
        type_list[5]: 'prad',
        type_list[6]: 'prev',
        type_list[7]: 'warning',
        type_list[8]: 'pgrs',
        type_list[9]: 'warning_infraction_notice',
        type_list[10]:'temporary_interdiction',
        type_list[11]:'temporary_embargo',
        type_list[12]:'cefir'
    }

    ids = busca_id(search_date)
    
    success = 0
    i = 0
    is_found = False

    print(f"Lendo o diário")

    while i < len(ids) and is_found == False:
        URL_DOC = f'{URL}/apifront/portal/edicoes/publicacoes_ver_conteudo/{ids[i]}'
        print(f'{i}/{len(ids)}')
        try:
            response = requests.get(URL_DOC, verify=False)
            soup = BeautifulSoup(response.text, "html.parser")
            soup_text = soup.getText().replace('\r\n',' ').replace('\n', '').replace('\'','’').replace('"', '”')
            
            # procura pelo termo "EDITAL DE NOTIFICAÇÃO" ou "EDITAL DE INTERESSE" e somente lê páginas que o contenham
            if len(re.findall(r'EDITAL[DE ]*NOTIFI[CAÇÃ]*O', soup_text)) > 0 or len(re.findall(r'EDITAL[DE ]*INTERESSE', soup_text)) > 0:
                paragrafos = soup.find_all('p')

                for paragrafo in paragrafos:
                    paragrafo = paragrafo.getText().replace('\r\n',' ').replace('\n', '').replace('\'','’').replace('"', '”')
                    autos = []
                    
                    # entende se o parágrafo se trata de uma lista de autos e os separa
                    if len(re.findall('ao[s]* Autuado[s]*:', paragrafo)) > 0:
                        autos = re.findall(r' (.*?);', paragrafo)
                    # caso não sejam autos, passa o texto inteiro pois se trata de outro tipo de documento
                    elif not autos:
                        autos.append(paragrafo)
                    
                    for text in autos:
                        for ord_type in type_list:
                            # verifica se o tipo é conhecido de acordo com o vetor "type_list"
                            if len(re.findall(ord_type, text.upper())) > 0:
                                # print(text)
                                
                                is_found = True
                                # separa corretamente o texto para o primeiro parágrafo dos autos
                                if len(re.findall('Autuado[s]*', text)) > 0:
                                    text = text[text.find(':')+2:]

                                try:
                                    # chama a função que irá processar o texto de acordo com o dicionário "type2function"
                                    reg = getattr(text_processing, type2function[ord_type])(text.replace('-', '_'), search_date, URL_DOC)


                                    if type(reg) == dict:
                                        publisher.publish('NEW_ORDINANCE', reg)
                                        success += 1

                                    elif type(reg) == list:
                                        for mult_reg in reg:
                                            publisher.publish('NEW_ORDINANCE', mult_reg)
                                            success += 1

                                    print()
                                except:
                                    print(text)
                                    # print()
                                    traceback.print_exc()
        except:
            traceback.print_exc()
        i += 1

    print(f'{ success } ordinance(s) imported')

    return success

def import_news():
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    _import_date(yesterday)
    
