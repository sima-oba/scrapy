import os, shutil, requests, urllib3
from dms2dec.dms_convert import dms2dec
urllib3.disable_warnings()

class ordinance_type:
    ALTERATION_LICENSE = 'ALTERATION_LICENSE'
    ANIMAL_HANDLING = 'ANIMAL_HANDLING'
    CANCEL_ = 'CANCEL_'
    CONDITION_REVIEW = 'CONDITION_REVIEW'
    ENVIRONMENTAL_AUTHORIZATION = 'ENVIRONMENTAL_AUTHORIZATION'
    ERRATUM = 'ERRATUM'
    EXPLORATION_APPROVAL = 'EXPLORATION_APPROVAL'
    EXTENDED_TERM = 'EXTENDED_TERM'
    FOREST_MANAGEMENT = 'FOREST_MANAGEMENT'
    FOREST_REPLACEMENT_CREDIT = 'FOREST_REPLACEMENT_CREDIT'
    FOREST_VOLUME_CREDIT = 'FOREST_VOLUME_CREDIT'
    FOREST_VOLUME_RECOGNITION = 'FOREST_VOLUME_RECOGNITION'
    FOREST_VOLUME_TRANSFER = 'FOREST_VOLUME_TRANSFER'
    GRANT_WAIVER = 'GRANT_WAIVER'
    INSTALLATION_LICENSE = 'INSTALLATION_LICENSE'
    LICENSE_CANCELLATION = 'LICENSE_CANCELLATION'
    LICENSE_RENEWAL = 'LICENSE_RENEWAL'
    LICENSE_REVOCATION = 'LICENSE_REVOCATION'
    OPERATION_LICENSE = 'OPERATION_LICENSE'
    OWNER_NAME_CHANGE = 'OWNER_NAME_CHANGE'
    OWNERSHIP_TRANSFER = 'OWNERSHIP_TRANSFER'
    PLANTING_ANTICIPATION = 'PLANTING_ANTICIPATION'
    PRELIMINARY_LICENSE = 'PRELIMINARY_LICENSE'
    REGULARIZATION_LICENSE = 'REGULARIZATION_LICENSE'
    RIGHT_USE_WATER_RESOURCES = 'RIGHT_USE_WATER_RESOURCES'
    SPECIAL_PROCEDURE = 'SPECIAL_PROCEDURE'
    UNIFIED_LICENSE = 'UNIFIED_LICENSE'
    VEGETAL_SUPPRESSION = 'VEGETAL_SUPPRESSION'
    LOCATION_LICENSE = 'LOCATION_LICENSE'
    OWNER_CORRECTION = 'OWNER_CORRECTION'
    IMPLANTATION_LICENSE = 'IMPLANTATION_LICENSE'
    INFRACTION_WARNING = 'INFRACTION_WARNING'
    INTERDICTION_INFRACTION = 'INTERDICTION_INFRACTION'
    DEMOLITION_PENALTY = 'DEMOLITION_PENALTY'
    FINE_INFRACTION = 'FINE_INFRACTION'
    SEIZURE_INFRACTION = 'SEIZURE_INFRACTION'
    ACTIVE_DEBIT = 'ACTIVE_DEBIT'
    GRANT_PROCESS = 'GRANT_PROCESS'
    PROCESS_EXTINCTION = 'PROCESS_EXTINCTION'
    ANTECIPATED_ENVIRONMENTAL_LICENSE = 'ANTICIPATED_ENVIRONMENTAL_LICENSE'
    NOTIFICATION_NOTICE = 'NOTIFICATION_NOTICE'
    SIMPLIFIED_ENVIRONMENTAL_LICENSE = 'SIMPLIFIED_ENVIRONMENTAL_LICENSE'
    DEADLINE_EXTENSION = 'DEADLINE_EXTENSION'
    RECTIFICATION = 'RECTIFICATION'
    ORDER_REVOCATION = 'ORDER_REVOCATION'
    SEIZURE = 'SEIZURE'
    DEGRADED_AREA_RECOVERY_PLAN = 'DEGRADED_AREA_RECOVERY_PLAN'
    GRANT_ENVIRONMENTAL_LICENSE = 'GRANT_ENVIRONMENTAL_LICENSE'
    ADMINISTRATIVE_DECISION = 'ADMINISTRATIVE_DECISION'
    CONFORMITY_CERTIFICATE = 'CONFORMITY_CERTIFICATE'
    ICMBIO_INFRACTION_NOTICE = 'ICMBIO_INFRACTION_NOTICE'
    IBAMA_INFRACTION_NOTICE = 'IBAMA_INFRACTION_NOTICE'
    LICENSE_DISMISSAL = 'LICENSE_DISMISSAL'
    LEGAL_RESERVE_LOCATION_APPROVAL = 'LEGAL_RESERVE_LOCATION_APPROVAL'
    TEMPORARY_INTERDICTION_NOTICE = 'TEMPORARY_INTERDICTION_NOTICE'
    PROCESS_ANALYSIS = 'PROCESS_ANALYSIS'
    PLANT_ENRICHMENT_PLAN = 'PLANT_ENRICHMENT_PLAN'
    TEMPORARY_EMBARGO = 'TEMPORARY_SEIZURE'
    PENALTY_WARNING = 'PENALTY_WARNING'
    CEFIR = 'CEFIR'
    SOLID_WASTE_MANAGEMENT_PLAN = 'SOLID_WASTE_MANAGEMENT_PLAN'
    RIGHT_WATER_USE_RESOURCE_RENOVATION = 'RIGHT_USE_WATER_RESOURCES_RENOVATION'
    RIGHT_WATER_USE_RESOURCE_CHANGE = 'RIGHT_USE_WATER_RESOURCES_CHANGE'
    VOLUME_EXPASION = 'VOLUME_EXPASION'
    PREVENTIVE = 'PREVENTIVE'
    TEMPORARY_SUSPEND = 'TEMPORARY_SUSPEND'


month_name = {
    1: 'Janeiro',
    2: 'Fevereiro',
    3: 'Março',
    4: 'Abril',
    5: 'Maio',
    6: 'Junho',
    7: 'Julho',
    8: 'Agosto',
    9: 'Setembro',
    10:'Outubro',
    11:'Novembro',
    12:'Dezembro'
}

#  
#  name: kafka_register
#  @ param: Pandas.Series
#  @ return: send to kafka topic
#  
def kafka_register(reg):
	# instância do kafka
	# producer = Producer({
	# 	'bootstrap.servers': 'localhost:9092',
	# 	'client.id': 'grant_scrapy',
	# 	'message.max.bytes': 10485760
	# })
    try:
        print(reg.to_json(force_ascii=False))
    except:
        print(reg)
    # conexão com kafka	
	# try:
	# 	producer.produce(topic, key='foo', value=reg.to_json(force_ascii=False))
	# 	producer.flush()
	# except Exception as e:
	# 	print(f'falhou')
	# 	traceback.print_exc()
    return 0

#  
#  name: create temp folder
#  @ param: folder name
#  @ return: prepare and clean temp folder
#  
def create_temp_folder(pasta):
    if os.path.exists(pasta) and not os.path.isdir(pasta):
        print('Folder name already used in file. Creating as temp folder')
        os.remove(pasta)
        os.mkdir(pasta)
    elif os.path.exists(pasta) and os.path.isdir(pasta):
        print('Folder already exists. Cleaning temp folder')
        shutil.rmtree(pasta)
        os.mkdir(pasta)
    elif not os.path.exists(pasta):
        print('Creating temp folder')
        os.mkdir(pasta) 


#  
#  name: download to file
#  @ param: url, download file directory 
#  @ return: true if download's ok; false if fails
#  
def download_to_file(url, filename):
    response = requests.get(url, headers={"user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"})
    if response.ok:        
        with open(filename, 'wb') as f:
            f.write(response.content)
            f.close()
        return response

    else:        
        return response



def degree_to_decimal(text: str) -> float:
    return dms2dec(text) if text else None