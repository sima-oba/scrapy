import logging
import os
import shutil
import geopandas
import pandas
import patoolib
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from .. import publisher
from . import utils

LABESL_SNCI = [
    "num_proces",
    "sr",
    "num_certif",
    "data_certi",
    "qtd_area_p",
    "cod_profis",
    "cod_imovel",
    "nome_imove",
    "uf_municip",
    "geometry"
]

LABELS_SIGEF = [
    "parcela_co",
    "rt",
    "art",
    "situacao_i",
    "codigo_imo",
    "data_submi",
    "data_aprov",
    "status",
    "nome_area",
    "registro_m",
    "registro_d",
    "municipio_",
    "uf_id",
    "geometry"
]

log = logging.getLogger(__name__)


def _import():
    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-gpu')
    options.add_argument('disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    url = 'https://certificacao.incra.gov.br/csv_shp/export_shp.py'

    try:
        log.debug(f'Accessing {url}')
        driver.get(url)

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "form_1"))
        )

        tmp_dir = '/tmp/incra/'
        docs = [
            'Imóvel certificado SIGEF Total',
            'Imóvel certificado SNCI Total'
        ]

        if os.path.exists(tmp_dir) and os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir)

        os.mkdir(tmp_dir)

        for doc in docs:
            try:
                log.debug(f'Searching "{doc}"')
                select = Select(driver.find_element(By.ID, 'selectshp'))
                select.select_by_visible_text(doc)

                select = Select(driver.find_element(By.ID, 'selectuf'))
                select.select_by_visible_text('Bahia')

                driver.find_element(By.XPATH, "//button[@id='enviar']").click()
                link = driver.find_elements(
                    By.XPATH,
                    "//a"
                )[0].get_attribute('href')

                log.debug(f'Downloading \'{doc}\'')
                zfile = open(f'/tmp/{doc}.zip', 'wb')
                zfile.write(requests.get(link, verify=False).content)
                zfile.close()

                patoolib.extract_archive(f'/tmp/{doc}.zip', outdir=tmp_dir)
                os.remove(f'/tmp/{doc}.zip')
            except IndexError:
                log.debug(
                    'Error in website. '
                    'Please check if you can download manually'
                )
            except Exception as e:
                log.error(e)

        driver.close()

        # Por algum motivo, o Geopandas não consegue criar o json por causa
        # da coluna geometry. A solução foi transformar o Geodataframe em csv,
        # carregá-lo via Pandas e só então exportar para json
        log.debug('Opening Imóvel certificado SNCI Brasil_BA')
        snci_frame = geopandas.read_file(
            f'{tmp_dir}Imóvel certificado SNCI Brasil_BA.shp', parse_dates=True
        )
        snci_frame.to_csv(
            f'{tmp_dir}Imóvel certificado SNCI Brasil_BA.csv', index=False
        )
        snci = pandas.read_csv(
            f'{tmp_dir}Imóvel certificado SNCI Brasil_BA.csv')

        log.debug('Opening Sigef Brasil_BA')
        sigef_frame = geopandas.read_file(
            f'{tmp_dir}Sigef Brasil_BA.shp', parse_dates=True
        )
        sigef_frame.to_csv(f'{tmp_dir}Sigef Brasil_BA.csv', index=False)
        sigef = pandas.read_csv(f'{tmp_dir}Sigef Brasil_BA.csv')

        log.debug('Cleaning temp files')
        shutil.rmtree(tmp_dir)

    except Exception as e:
        log.error(e)

    return snci, sigef


def incra():
    snci, sigef = _import()
    snci.columns = LABESL_SNCI
    sigef.columns = LABELS_SIGEF

    log.debug('Sending Imóvel certificado SNCI Brasil_BA to Kafka')

    for reg in snci.iterrows():
        row = reg[1].to_dict()
        data = {
            'farm_code':            row['cod_imovel'],
            'farm_name':            row['nome_imove'],
            'process_number':       row['num_proces'],
            'certificate_number':   row['num_certif'],
            'certificate_date':     row['data_certi'],
            'sr':                   row['sr'],
            'preserved area':       row['qtd_area_p'],
            'uf':                   row['uf_municip'],
            'geometry':             row['geometry']
        }
        publisher.publish('SNCI_INCRA', data)

    log.debug('Sending Sigef Brasil_BA to Kafka')

    for reg in sigef.iterrows():
        row = reg[1].to_dict()
        data = {
            'imported_id':      row['parcela_co'],
            'rt':               row['rt'],
            'art':              row['art'],
            'farm_code':        str(utils.to_int(row['codigo_imo'])),
            'farm_name':        row['nome_area'],
            'situation':        row['situacao_i'],
            'status':           row['status'],
            'submission_date':  row['data_submi'],
            'approval_date':    row['data_aprov'],
            'city_geoid':       str(row['municipio_'])
        }
        publisher.publish('SIGEF_INCRA', data)

    log.debug(f'Foram encontrados {len(sigef) + len(snci)} registros')
