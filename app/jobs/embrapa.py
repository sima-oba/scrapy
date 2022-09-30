from glob import glob
import logging
import shutil
import geopandas
import patoolib
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from . import utils

from .. import publisher

log = logging.getLogger(__name__)

def wait_element(driver, locator: tuple, timeout: int = 60):
    condition = EC.presence_of_element_located(locator)
    WebDriverWait(driver, timeout).until(condition)


def import_matopiba():
    log.debug("Setting the args")
    utils.create_temp_folder('temp')
    url = "http://mapas.cnpm.embrapa.br/matopiba2015/"

    prefs = {'download.default_directory': './temp/'}

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
    actions.context_click(element).perform()
    wait_element(driver, (By.XPATH, '//*[@id="ext-comp-1022"]'))

    log.debug('Export to shp')
    element = driver.find_element(By.XPATH, '//*[@id="ext-comp-1022"]')
    actions.move_to_element(element).perform()
    wait_element(driver, (By.XPATH, '//*[@id="ext-comp-1024"]'))
    
    log.debug('Downloading file')
    driver.find_element(By.XPATH, '//*[@id="ext-comp-1024"]').click()

    driver.quit()

    files = glob('./temp/*.zip')
    patoolib.extract_archive(files[0], outdir='./temp/extract-matopiba/')
    
    matopiba = geopandas.read_file(glob('temp/extract-matopiba/*.shp')[0])
    shutil.rmtree('./temp')

    log.debug("Saving in to kafka")
    for reg in matopiba.iterrows():
        # TODO: topico kafka
        publisher.publish("matopiba", reg[1])

