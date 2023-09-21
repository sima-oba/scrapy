import geopandas
import glob
import logging
import pandas
import requests
import os
import shutil
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .. import publisher

log = logging.getLogger(__name__)

CITIES = [
    'Barreiras',
    'Luís Eduardo Magalhães',
    'São Desidério',
    'Correntina',
    'Riachão Das Neves',
    'Formosa Do Rio Preto',
    'Cocos',
    'Jaborandi',
    'Baianópolis',
    'Santa Rita De Cássia',
    'Angical',
    'Cotegipe',
    'Cristópolis',
    'Wanderley',
    'Santana',
    'Santa Maria Da Vitória',
    'Serra Dourada',
    'Tabocas Do Brejo Velho',
    'Brejolândia',
    'Mansidão',
    'Catolândia',
    'Canápolis',
    'Coribe',
    'São Félix Do Coribe',
    'Coração de Maria'
]


def fire_risk(url):
    tmp_file = '/tmp/fire_risk.csv'
    
    log.debug(f'Seeking fire risk at {url}')
    res = requests.get(url, allow_redirects=True, verify=False)

    with open(tmp_file, 'wb') as file:
        file.write(res.content)

    # Load data from all files in a single dataframe and filter by Bahia
    log.debug('Loading data from Bahia')

    df = geopandas.read_file(tmp_file)
    df_ba = df
    df_cities = geopandas.GeoDataFrame()
    os.remove(tmp_file)

    log.debug('Filtering cities in the west of Bahia')

    for reg in df_ba.iterrows():
        for city in CITIES:
            if reg[1]['municipio'] == city.upper():
                df_cities = df_cities.append(reg[1])

    df_cities.reset_index(drop=True, inplace=True)

    log.debug('Publising...')

    if len(df_cities) > 0:
        publisher.publish('FIRE_RISK', df_cities)

    log.debug(f'Records processed: {len(df_cities)}')


def climate_risk():
    download_dir = '/tmp/climate_risk'
    url = (
        'http://indicadores.agricultura.gov.br/QvAJAXZfc/opendoc.htm'
        '?document=PORTALQVW%2FSISSER.qvw&host=QVS%40masrv1005'
        '&anonymous=true&sheet=ZARC'
    )

    prefs = {'download.default_directory': download_dir}
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", prefs)
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    driver = webdriver.Chrome(options=options)

    try:
        log.debug(f'Seeking climate risk at {url}')
        driver.get(url)

        WebDriverWait(driver, 1200).until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'Document_LB2599')
        ))

        time.sleep(60)

        uf_list = driver.find_element(By.CLASS_NAME, 'Document_LB2599')
        uf_list.find_element(By.CSS_SELECTOR, 
            'div:nth-child(2) div:nth-child(1) div:nth-child(1) '
            'div:nth-child(5)'
        ).click()

        time.sleep(60)

        driver.find_element(By.CSS_SELECTOR, 
            '[title="Tabela Detalhada"] [title="Enviar para Excel"]'
        ).click()

        log.debug('Exporting file...')
        seconds = 1800

        while seconds > 0:
            files = glob.glob(f'{download_dir}/*.csv')

            if len(files) > 0:
                break

            time.sleep(1)
            seconds -= 1

        if seconds == 0:
            log.debug('Time is over')
        else:
            log.debug(f'Found file {files[0]}')

            for df in pandas.read_csv(files[0], sep=';', chunksize=50):
                for row in df.iterrows():
                    payload = row[1].to_dict()

                    if payload['Município'] not in CITIES:
                        continue

                    periods = [payload.pop(str(i)) for i in range(1, 37)]
                    payload['periods'] = periods
                    payload['Safra'] = payload['Safra'].replace('\\', '/')

                    publisher.publish('CLIMATE_RISK', payload)
    finally:
        driver.close()
        shutil.rmtree(download_dir, ignore_errors=True)
