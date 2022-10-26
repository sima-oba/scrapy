from glob import glob
import time
import logging
import shutil
import geopandas
import patoolib
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from shapely.geometry import mapping
from . import utils

from .. import publisher

log = logging.getLogger(__name__)

def wait_element(driver, locator: tuple, timeout: int = 60):
    condition = EC.presence_of_element_located(locator)
    WebDriverWait(driver, timeout).until(condition)


def import_matopiba():
    log.debug("Setting the args")
    utils.create_temp_folder('/tmp/matopiba')
    url = "http://mapas.cnpm.embrapa.br/matopiba2015/"
    prefs = {'download.default_directory': '/tmp/matopiba'}

    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", prefs)
    options.add_argument('ignore-certificate-errors')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('no-sandbox')
    options.add_argument('headless')

    driver = webdriver.Chrome(options=options)
    actions = ActionChains(driver)
    
    log.debug("Acessing EMBRAPA site")
    driver.get(url)
    wait_element(driver, (By.XPATH, '//*[@id="extdd-37"]'))
    
    log.debug('Opening menu \"Estados\"')
    element = driver.find_element(By.XPATH, '//*[@id="extdd-37"]')
    actions.context_click(element).pause(5).perform()
    wait_element(driver, (By.XPATH, '//*[@id="ext-comp-1022"]'))

    log.debug('Export to shp')
    element = driver.find_element(By.XPATH, '//*[@id="ext-comp-1022"]')
    actions.move_to_element(element).pause(5).perform()
    wait_element(driver, (By.XPATH, '//*[@id="ext-comp-1024"]'))
    
    log.debug('Downloading file')
    driver.find_element(By.XPATH, '//*[@id="ext-comp-1024"]').click()

    timeout = 120
    while timeout > 0:
        files = glob('/tmp/matopiba/*.zip')

        if len(files) > 0:
            break

    if timeout == 0:
        raise Exception('Unable to download files')

    driver.quit()
    patoolib.extract_archive(files[0], outdir='/tmp/matopiba/extract-matopiba/')
    matopiba = geopandas.read_file(glob('/tmp/matopiba/extract-matopiba/*.shp')[0])
    shutil.rmtree('/tmp/matopiba')

    log.debug("Saving in to kafka")

    for reg in matopiba.iterrows():
        payload = reg[1].to_dict()
        payload['geometry'] = mapping(payload['geometry'])
        publisher.publish("MATOPIBA", payload)

