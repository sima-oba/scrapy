from apscheduler.triggers.cron import CronTrigger
from flask import current_app

from .. import scheduler
from . import (
    risk,
    weather,
    hydrography,
    phytosanitary,
    ana,
    ibama,
    icmbio,
    incra,
    seia,
    embrapa
)

from .ordinances import (
    angical,
    baianopolis,
    barreiras,
    bjlapa,
    buritirama,
    canapolis,
    catolandia,
    cocos,
    coribe,
    correntina,
    cotegipe,
    cristopolis,
    estadual,
    estadual_editais,
    formosa_rio_preto as frp,
    jaborandi,
    lem,
    mansidao,
    riachao_neves,
    santa_maria_vitoria as smv,
    santa_rita_cassia as src,
    santana,
    sao_desiderio,
    serra_dourada,
    sfcoribe,
    tabocas,
    wanderley
)

def set_up_jobs():
    config = current_app.config
    scheduler.remove_all_jobs()

    scheduler.add_job(
        id='DOM_ANGICAL',
        name='Diário oficial de Angical',
        func=angical.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_BAIANOPOLIS',
        name='Diário oficial de Baianopolis',
        func=baianopolis.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_BARREIRAS',
        name='Diário oficial de Barreiras',
        func=barreiras.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_BJLAPA',
        name='Diário oficial de Bom Jesus da Lapa',
        func=bjlapa.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_BURITIRAMA',
        name='Diário oficial de Buritirama',
        func=buritirama.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_CANAPOLIS',
        name='Diário oficial de Canapolis',
        func=canapolis.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_CATOLANDIA',
        name='Diário oficial de Catolandia',
        func=catolandia.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_COCOS',
        name='Diário oficial de Cocos',
        func=cocos.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_CORIBE',
        name='Diário oficial de Coribe',
        func=coribe.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_CORRENTINA',
        name='Diário oficial de Correntina',
        func=correntina.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_COTEGIPE',
        name='Diário oficial de Cotegipe',
        func=cotegipe.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_CRISTOPOLIS',
        name='Diário oficial de Cristopolis',
        func=cristopolis.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOE',
        name='Diário oficial do Estado',
        func=estadual.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOE_WARNING',
        name='Edital de notificações do DOE',
        func=estadual_editais.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_FORMOSA',
        name='Diário oficial de Formosa do Rio Preto',
        func=frp.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_JABORANDI',
        name='Diário oficial de Jaborandi',
        func=jaborandi.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_LEM',
        name='Diário oficial de Luís Eduardo Magalhães',
        func=lem.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_MANSIDAO',
        name='Diário oficial de Mansidão',
        func=mansidao.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_RIACHAO_NEVES',
        name='Diário oficial de Riachão das Neves',
        func=riachao_neves.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_SMV',
        name='Diário oficial de Santa Maria da Vitória',
        func=smv.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_SRC',
        name='Diário oficial de Santa Rita de Cássia',
        func=src.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_SANTANA',
        name='Diário oficial de Santana',
        func=santana.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_SAO_DESIDERIO',
        name='Diário oficial de São Desidério',
        func=sao_desiderio.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_SERRA_DOURADA',
        name='Diário oficial de Serra Dourada',
        func=serra_dourada.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_SFCORIBE',
        name='Diário oficial de São Felix do Coribe',
        func=sfcoribe.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_TABOCAS',
        name='Diário oficial de Tabocas do Brejo Velho',
        func=tabocas.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='DOM_WANDERLEY',
        name='Diário oficial de Wanderley',
        func=wanderley.import_news,
        trigger=CronTrigger(hour='5')
    )

    scheduler.add_job(
        id='FIRE_RISK',
        name='Risco de Fogo',
        func=risk.fire_risk,
        args=[config['RISK_FIRE']],
        trigger=CronTrigger(hour='5,10,15'),
        misfire_grace_time=config['MAX_MISFIRE']
    )

    scheduler.add_job(
        id='CLIMATE_RISK',
        name='Risco Climático',
        func=risk.climate_risk,
        trigger=CronTrigger(hour='6', minute='10')
    )

    scheduler.add_job(
        id='OBSERVED_WEATHER',
        name='Dados de Clima Observados',
        func=weather.observed,
        args=[config['WEATHER_API']],
        trigger=CronTrigger(day_of_week='6', hour='0')
    )

    scheduler.add_job(
        id='RAINFALL',
        name='Estações Meteorológicas',
        func=weather.rainfall,
        trigger=CronTrigger(day='1', hour='23')
    )

    scheduler.add_job(
        id='FORECAST',
        name='Previsão do Tempo',
        func=weather.forecast,
        args=[config['WEATHER_API']],
        trigger=CronTrigger(hour=','.join([str(i) for i in range(0, 24)]))
    )

    scheduler.add_job(
        id='HYDROGRAPHY_ANA',
        name='Vetores de Hidrografia',
        func=hydrography.hydrography_vectors,
        args=[config['HYDROGRAPHY_VECTORS']],
        trigger=CronTrigger(month='1'),
        misfire_grace_time=config['MAX_MISFIRE']
    )

    scheduler.add_job(
        id='LIMIT_LVL_1',
        name='Limites Nível 1',
        func=hydrography.limit_n1,
        args=[config['HYDROGRAPHY_LIMIT_N1']],
        trigger=CronTrigger(month='1', day='1', hour='0')
    )

    scheduler.add_job(
        id='LIMIT_LVL_2',
        name='Limites Nível 2',
        func=hydrography.limit_n2,
        args=[config['HYDROGRAPHY_LIMIT_N2']],
        trigger=CronTrigger(month='1', day='1', hour='1')
    )

    scheduler.add_job(
        id='BASIN_RIO_GRANDE',
        name='Limites Nível 4',
        func=hydrography.limit_n4,
        args=[config['HYDROGRAPHY_LIMIT_N4']],
        trigger=CronTrigger(month='1', day='1', hour='2')
    )

    scheduler.add_job(
        id='CONTRIB',
        name='Limites Nível 5',
        func=hydrography.limit_n5,
        args=[config['HYDROGRAPHY_LIMIT_N5']],
        trigger=CronTrigger(month='1', day='1', hour='3')
    )

    scheduler.add_job(
        id='FLOW_RATE_QMLD',
        name='Vazão Específica QMLD',
        func=hydrography.qmld_flow,
        args=[config['HYDROGRAPHY_QMLD']],
        trigger=CronTrigger(month='1', day='1', hour='4')
    )

    scheduler.add_job(
        id='FLOW_RATE_Q90',
        name='Vazão Específica Q90',
        func=hydrography.q90_flow,
        args=[config['HYDROGRAPHY_Q90']],
        trigger=CronTrigger(month='1', day='1', hour='5')
    )

    scheduler.add_job(
        id='WATER_AVAILABILITY',
        name='Disponibilidade Hídrica',
        func=hydrography.water_availability,
        args=[config['HYDROGRAPHY_WATER_AVAILABILITY']],
        trigger=CronTrigger(month='1', day='1', hour='6')
    )

    scheduler.add_job(
        id='WATER_SECURITY',
        name='Índice de Segurança Hídrica',
        func=hydrography.water_safety_index,
        args=[config['HYDROGRAPHY_WATER_SAFETY_INDEX']],
        trigger=CronTrigger(month='1', day='1', hour='7')
    )

    scheduler.add_job(
        id='WATERBODY',
        name='Corpos Hídricos',
        func=hydrography.water_bodies,
        args=[config['HYDROGRAPHY_WATER_BODIES']],
        trigger=CronTrigger(month='1', day='1', hour='8')
    )

    scheduler.add_job(
        id='BASIN_1',
        name='Micro Bacias do São Francisco',
        func=hydrography.sao_francisco_micro_basins,
        args=[config['HYDROGRAPHY_SAO_FRANCISCO_MICRO_BASINS']],
        trigger=CronTrigger(month='1', day='1', hour='9')
    )

    scheduler.add_job(
        id='BASIN_2',
        name='Bacia do São Francisco',
        func=hydrography.sao_francisco_basin,
        args=[config['HYDROGRAPHY_SAO_FRANCISCO_BASINS']],
        trigger=CronTrigger(month='1', day='1', hour='10')
    )

    scheduler.add_job(
        id='AQUIFER',
        name='Aquíferos',
        func=hydrography.aquifer,
        args=[config['HYDROGRAPHY_AQUIFER']],
        trigger=CronTrigger(month='1', day='1', hour='11')
    )

    scheduler.add_job(
        id='IRRIGATED_AREA',
        name='Áreas Irrigadas',
        func=hydrography.irrigated_areas,
        args=[config['HYDROGRAPHY_IRRIGATED_AREAS']],
        trigger=CronTrigger(month='1', day='1', hour='12')
    )

    scheduler.add_job(
        id='PIVOT',
        name='Pivôs Centrais',
        func=hydrography.center_pivots,
        args=[config['HYDROGRAPHY_CENTER_PIVOTS']],
        trigger=CronTrigger(day='1', hour='0')
    )

    scheduler.add_job(
        id='PHYTOSANITARY',
        name='ArcGis',
        func=phytosanitary.arcgis,
        args=[config['ARCGIS_USER'], config['ARCGIS_PASSWORD']],
        trigger=CronTrigger(day_of_week='6', hour='1'),
        misfire_grace_time=config['MAX_MISFIRE']
    )

    scheduler.add_job(
        id='ANNUAL_ORDINANCE',
        name='Portaria Anual do Fitossanitário',
        func=phytosanitary.phytosanitary,
        trigger=CronTrigger(hour='12')
    )

    scheduler.add_job(
        id='ANA',
        name='ANA',
        func=ana.ana,
        trigger=CronTrigger(hour='8', minute='30')
    )

    scheduler.add_job(
        id='IBAMA',
        name='Embargo Ibama',
        func=ibama.ibama,
        trigger=CronTrigger(hour='9')
    )

    scheduler.add_job(
        id='ICMBIO',
        name='ICMBIO',
        func=icmbio.icmbio,
        trigger=CronTrigger(hour='9', minute='30')
    )

    scheduler.add_job(
        id='INCRA',
        name='INCRA',
        func=incra.incra,
        trigger=CronTrigger(day='2', hour='0')
    )

    scheduler.add_job(
        id='SEIA',
        name='SEIA',
        func=seia.seia,
        args=[
            config['SEIA_USER'], 
            config['SEIA_PASSWORD'],
            config['SIMA_USER'],
            config['SIMA_PASSWORD']
        ],
        trigger=CronTrigger(day_of_week='6', hour='2')
    )
    
    # TODO: ajustar agendamentos
    scheduler.add_job(
        id='CORRENTE_BASIN',
        name='Bacia do Rio Corrente',
        func=hydrography.corrente_basin,
        args=[config['HYDROGRAPHY_CORRENTE_BASIN']],
        trigger=CronTrigger(month='1', day='1', hour='11')
    )

    scheduler.add_job(
        id='CARINHANHA_BASIN',
        name='Bacia do Rio Carinhanha',
        func=hydrography.carinhanha_basin,
        args=[config['HYDROGRAPHY_CARINHANHA_BASIN']],
        trigger=CronTrigger(month='1', day='1', hour='11')
    )

    scheduler.add_job(
        id='MATOPIBA',
        name='Delimitação do MATOPIBA',
        func=embrapa.import_matopiba,
        trigger=CronTrigger(month='1', day='1', hour='12')
    )


    
