import glob
import logging
import shutil
import pandas
import patoolib
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from .. import publisher
from . import utils

LABELS = [
    'tad_number',
    'tad_series',
    'area',
    'ai_number',
    'owner_name',
    'owner_doc',
    'location',
    'uf',
    'seizure_city',
    'city',
    'neighborhood',
    'address',
    'status',
    'infringement',
    'insert_date'
]

log = logging.getLogger(__name__)


def _import():
    tmp_dir = '/tmp/ibama-download/'
    prefs = {"download.default_directory": f"{tmp_dir}"}
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", prefs)
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-gpu')
    options.add_argument('disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    url = (
        'https://servicos.ibama.gov.br/ctf/publico/areasembargadas'
        '/ConsultaPublicaAreasEmbargadas.php'
    )

    try:
        utils.create_temp_folder(tmp_dir)

        log.debug(f'Access: {url}')
        driver.get(url)

        log.debug('Downloading...')
        element = driver.find_element_by_xpath('//*[@id="download"]/a')
        ActionChains(driver).move_to_element(element).click().perform()

        arquivos = glob.glob(f'{tmp_dir}areas*.zip')
        inicio = datetime.now()
        timeout = datetime.now() - inicio

        while timeout.seconds < 30 and len(arquivos) == 0:
            arquivos = glob.glob(f'{tmp_dir}areas*.zip')
            timeout = datetime.now() - inicio

        patoolib.extract_archive(f'{arquivos[0]}', outdir=tmp_dir)

        log.debug(f'Loading file {glob.glob(f"{tmp_dir}*.xls")[0]}')
        df = pandas.read_html(glob.glob(f'{tmp_dir}*.xls')[0])[0]
        df.drop([0, 1, 2, 3, 4, 5, 6], inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.columns = LABELS
        df[df[LABELS[7]] == 'BA']

        lista_cidades = [
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
            'São Félix Do Coribe'
        ]

        return df[df[LABELS[8]].isin(lista_cidades)]
    except Exception as e:
        log.error(e)
    finally:
        driver.close()
        shutil.rmtree(tmp_dir, ignore_errors=True)


def ibama():
    embargo_area = _import()
    embargo_area.columns = LABELS

    success = 0
    punctuation = re.compile('[-.]')
    date = re.compile(r'(\d{2})/(\d{2})/(\d{4})')

    for reg in embargo_area.iterrows():
        try:
            data = reg[1].to_dict()
            data.pop('ai_number')
            data.pop('tad_series')
            data.pop('owner_name')
            data.pop('location')
            data.pop('infringement')
            data['owner_doc'] = punctuation.sub('', data['owner_doc'])
            data['area'] = utils.to_float(data['area'])
            data['insert_date'] = date.sub(r'\3-\2-\1', data['insert_date'])

            publisher.publish('IBAMA', data)
            success += 1
        except Exception as e:
            log.error(e)

    log.debug(f'{success}/{len(embargo_area)} stored')
