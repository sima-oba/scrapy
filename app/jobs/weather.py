import logging
import math
import os
import requests
import pandas
import shutil
from datetime import datetime, timedelta
from math import isnan
from pandas import DataFrame

from .. import publisher
from . import utils

FORECAST_SUMMARY = {
    'Muitas nuvens': 'Nublado',
    'Muitas nuvens com possibilidade de chuva isolada': 'Nublado',
    'Muitas nuvens com pancadas de chuva isoladas': 'Chuvoso',
    'Muitas nuvens com pancadas de chuva e trovoadas isoladas': 'Tempestade',
    'Nublado com pancadas de chuva e trovoadas isoladas': 'Chuvoso',
    'Encoberto com chuvisco': 'Chuvoso',
    'Encoberto': 'Chuvoso',
    'Claro': 'Limpo',
    'Nublado': 'Nublado',
    'Poucas nuvens': 'Poucas nuvens'
}

log = logging.getLogger(__name__)


def _is_valid(data) -> bool:
    if type(data) is not dict:
        return False

    for value in data.values():
        if value is None:
            return False

        if type(value) is float and isnan(value):
            return False

    return True


def _format_forecast(forecast: DataFrame) -> list:
    data = []

    for day, content in forecast.to_dict().items():
        items = [
            content.pop('manha', None),
            content.pop('tarde', None),
            content.pop('noite', None),
            content,
        ]

        for item in items:
            if not _is_valid(item):
                continue

            item['resumo'] = FORECAST_SUMMARY.get(item['resumo'])

            # Remove unwanted fields
            item.pop('icone')
            item.pop('temp_max_tende_icone')
            item.pop('temp_min_tende_icone')

            formatted = {'dia': day, **item}
            data.append(formatted)

    return data


def _float_or_none(value):
    try:
        number = float(value)
        return None if isnan(number) else number
    except (TypeError, ValueError):
        return None


def forecast(base_url: str):
    cities_url = base_url + '/cities'
    log.debug(f'Fetching cities at {cities_url}')
    cities = requests.get(f'{cities_url}').json()

    for city in cities:
        geoid = city['geoid']
        url = f'https://apiprevmet3.inmet.gov.br/previsao/{geoid}'

        log.debug(f'Fetching forecast at {url}')
        response = requests.get(url)

        if not response.ok:
            log.error(f'HTTP error: {response.status_code}: {response.url}')
            continue

        data = response.json()
        frame = DataFrame(data[str(geoid)])
        data = _format_forecast(frame)

        for item in data:
            log.debug(f'Publishing forecast')
            publisher.publish('FORECAST', item)


def observed(base_url: str):
    # Fetch the observed data from the date specified by the backend
    # Date must be in YYYY-MM-DD format
    res = requests.get(f'{base_url}/observed_weather/checkpoint').json()
    start_date = res['checkpoint'][:10]

    # setting end date (yesterday)
    end_date = (datetime.today() - timedelta(1)).strftime('%Y-%m-%d')

    # TODO: adds stations in database
    log.debug(f'Updating from {start_date} to {str(end_date)}')
    log.debug('Loading station id')

    ms = requests.get('https://apitempo.inmet.gov.br/estacoes/M').json()
    ts = requests.get('https://apitempo.inmet.gov.br/estacoes/T').json()
    ms = pandas.DataFrame(ms)
    ts = pandas.DataFrame(ts)
    datas = pandas.concat([ts, ms])

    log.debug('Filtering station id of interests...')
    stations = ['BARREIRAS', 'CORRENTINA', 'POSSE', 'TAGUATINGA']
    codes = []

    for s in stations:
        codes.append(datas[datas['DC_NOME'] == s].CD_ESTACAO.values[0])

    cols = [
        'PRE_INS',
        'TEM_SEN',
        'PRE_MAX',
        'RAD_GLO',
        'PTO_INS',
        'TEM_MIN',
        'UMD_MIN',
        'PTO_MAX',
        'VEN_DIR',
        'CHUVA',
        'PRE_MIN',
        'UMD_MAX',
        'VEN_VEL',
        'PTO_MIN',
        'TEM_MAX',
        'VEN_RAJ',
        'TEM_INS',
        'UMD_INS',
        'UMID_MED',
        'UMID_HORA',
        'TEMP_HORA',
        'INSO_HORA',
        'NEBU_HORA',
        'TEMP_MED',
        'VENT_VEL',
        'TEMP_MIN',
        'TEMP_MAX',
        'PRESS_EST',
        'VENT_DIR',
    ]

    response = DataFrame()

    for st in codes:
        res = requests.get(
            f'https://apitempo.inmet.gov.br/estacao/{start_date}/{end_date}'
            f'/{st}'
        )

        data = DataFrame(res.json())
        st_name = data.loc[0]['DC_NOME']
        i = 1
        total = len(data)

        for st in data.iterrows():
            log.debug(
                f'Removing empty records from station:{st_name} {i}/{total}'
            )
            # search how much data is missing that day
            nans = 0

            for col in cols:
                try:
                    # there are two values ​​that can be considered null:
                    # NoneFormat and math.Nan
                    val = st[1][col]

                    if val is None or math.isnan(float(val)):
                        nans += 1

                except KeyError:
                    # if there is a column name error, it means that this data
                    # is also missing
                    nans += 1

            # the vector of columns considered has 29 items, so if less than 29
            # data are missing, the record has some useful data and should be
            # saved
            if nans < 29:
                response = response.append(st[1])

    response.reset_index(drop=True, inplace=True)

    i = 0
    success = 0
    total = len(response)

    for r in response.iterrows():
        i += 1
        log.debug(f'Publishing {i}/{total}')

        try:
            raw_data = r[1].to_dict()
            payload = {
                'station_code': raw_data['CD_ESTACAO'],
                'name': raw_data['DC_NOME'],
                'latitude': float(raw_data['VL_LATITUDE']),
                'longitude': float(raw_data['VL_LONGITUDE']),
                'msr_date': raw_data['DT_MEDICAO'],
                'msr_hour': raw_data['HR_MEDICAO'],
                'temp': _float_or_none(raw_data['TEMP_HORA']),
                'min_temp': _float_or_none(raw_data['TEMP_MIN']),
                'max_temp': _float_or_none(raw_data['TEMP_MAX']),
                'avg_temp': _float_or_none(raw_data['TEMP_MED']),
                'insolation': _float_or_none(raw_data['INSO_HORA']),
                'cloudiness': _float_or_none(raw_data['NEBU_HORA']),
                'humidity': _float_or_none(raw_data['UMID_HORA']),
                'avg_humidity': _float_or_none(raw_data['UMID_MED']),
                'rain': _float_or_none(raw_data['CHUVA']),
                'wind_speed': _float_or_none(raw_data['VENT_VEL']),
                'wind_direction': _float_or_none(raw_data['VENT_DIR']),
                'gust': _float_or_none(raw_data['VEN_RAJ']),
                'pressure': _float_or_none(raw_data['PRESS_EST'])
            }

            publisher.publish('OBSERVED_WEATHER', payload)
            success += 1
        except Exception:
            log.error(f'{r[1].to_json()} failed')

    log.debug(f'Have been registered: {success}/{total}')


def rainfall(year: int = None):
    year = datetime.now().year
    tmp_folder = '/tmp/rainfall'

    city_names = [
        'Barreiras',
        'Luiz Eduardo Magalhaes',  # O nome da cidade está errado no zip
        'Luis Eduardo Magalhaes',
        'Sao Desiderio',
        'Correntina',
        'Riachao das Neves',
        'Formosa do Rio Preto',
        'Cocos',
        'Jaborandi',
        'Baianapolis',
        'Santa Rita de Cassia',
        'Angical',
        'Cotegipe',
        'Cristopolis',
        'Wanderley',
        'Santana',
        'Santa Maria da Vitoria',
        'Serra Dourada',
        'Tabocas do Brejo Velho',
        'Brejolandia',
        'Mansidao',
        'Catolandia',
        'Canapolis',
        'Coribe',
        'Sao Felix do Coribe'
    ]

    rotulos = [
        'data',
        'hora_utc',
        'total_rainfall',
        'atmospheric_pressure_at_station_level',
        'atmospheric_pressure_maximum',
        'atmospheric_pressure_minimum',
        'global_radiation',
        'temp_dry_bulb',
        'temp_dew_point',
        'temp_maximum',
        'temp_minimum',
        'temp_dew_maximum',
        'temp_dew_minimum',
        'humidity_maximum',
        'humidity_minimum',
        'humidity_air',
        'wind_clockwise_direction',
        'wind_gust_maximum',
        'wind_speed',
        'a'
    ]

    utils.create_temp_folder(tmp_folder)

    log.debug(f'Searching for year {year}')
    log.debug('Download files')
    url = f'https://portal.inmet.gov.br/uploads/dadoshistoricos/{year}.zip'
    utils.download_to_file(url, f'{tmp_folder}/{year}.zip')

    utils.create_temp_folder(f'{tmp_folder}/filtered')
    shutil.unpack_archive(f'{tmp_folder}/{year}.zip', tmp_folder)

    log.debug('Filtering stations')

    for filename in os.listdir(tmp_folder):
        for city in city_names:
            if (f'_{city}_').upper() in filename:
                os.replace(
                    f'{tmp_folder}/{filename}',
                    f'{tmp_folder}/filtered/{filename}'
                )
                log.debug(filename)

    for file in os.listdir(f'{tmp_folder}/filtered'):
        log.debug(f'Reading {file}')

        dataframe = pandas.read_csv(
            f'{tmp_folder}/filtered/{file}',
            sep=';',
            header=9,
            encoding='Windows-1252'
        )
        first_row = DataFrame(dataframe.columns)

        # preenche valores inválidos com NaN
        for i in range(len(first_row)):
            if first_row.loc[i].values[0].find('Unna') > -1:
                first_row.loc[i] = float('NaN')

        first_row = first_row.transpose()
        first_row.columns = rotulos
        dataframe.columns = rotulos
        dataframe = pandas.concat([first_row, dataframe])
        dataframe = dataframe.drop('a', axis=1)
        dataframe.reset_index(drop=True, inplace=True)

        # completa dados gerais da estação
        separator = file.split('_')
        state = separator[2]
        station_code = separator[3]
        city = separator[4]

        dataframe['state'] = state
        dataframe['code'] = station_code
        dataframe['city'] = city

        # buscando dados de latitude e longitude
        ms = requests.get('https://apitempo.inmet.gov.br/estacoes/T')
        ms = DataFrame(ms.json())
        new_ms = ms[ms['CD_ESTACAO'] == station_code]

        latitude = new_ms['VL_LATITUDE']
        longitude = new_ms['VL_LONGITUDE']
        altitude = new_ms['VL_ALTITUDE']

        dataframe['latitude'] = float(latitude)
        dataframe['longitude'] = float(longitude)
        dataframe['altitude'] = float(altitude)

        i = 0

        for row in dataframe.iterrows():
            data = row[1].data
            hora = row[1].hora_utc
            hora = hora.split(' ')
            hora = hora[0]

            date = datetime.strptime(data + ' ' + hora, '%Y/%m/%d %H00')

            rowIndex = dataframe.index[i]
            dataframe.loc[rowIndex, 'date_time'] = date.isoformat() + '.000'
            i += 1

        dataframe = dataframe.drop('data', axis=1)
        dataframe = dataframe.drop('hora_utc', axis=1)

        fields_str_to_float = [
            'total_rainfall',
            'atmospheric_pressure_at_station_level',
            'atmospheric_pressure_maximum',
            'atmospheric_pressure_minimum',
            'global_radiation',
            'temp_dry_bulb',
            'temp_dew_point',
            'temp_maximum',
            'temp_minimum',
            'temp_dew_maximum',
            'temp_dew_minimum',
            'wind_gust_maximum',
            'wind_speed'
        ]

        fields_nan_to_float = [
            'humidity_maximum',
            'humidity_minimum',
            'humidity_air',
            'wind_clockwise_direction'
        ]

        for reg in dataframe.iterrows():
            payload = reg[1].to_dict()

            for field in fields_str_to_float:
                value = payload[field]

                try:
                    payload[field] = float(
                        value.replace('.', '').replace(',', '.')
                    )
                except Exception as e:
                    log.debug(e)
                    payload[field] = 0

            for field in fields_nan_to_float:
                value = float(payload[field])

                if math.isnan(value) or math.isfinite(value):
                    payload[field] = 0

            publisher.publish('RAINFALL', payload)

    shutil.rmtree(tmp_folder)
