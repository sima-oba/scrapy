import logging
import pandas
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .. import publisher

LABELS = [
    'name',
    'city_name',
    'state',
    'hidric_body',
    'hydrographic_region',
    'main_use',
    'interference_type',
    'resolution',
    'publish_date',
    'due_date',
    'annual_volume'
]

log = logging.getLogger(__name__)


def _import():
    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    options.add_argument('window-size=1024x768')
    driver = webdriver.Chrome(options=options)
    url = (
        'https://portal1.snirh.gov.br/ana/apps/webappviewer/index.html?'
        'id=0d9d29ec24cc49df89965f05fc5b96b9'
    )

    try:
        driver.get(url)

        xpath_search_button = "/html/body/div[2]/div[2]/div/div[9]/div/div[3]/div/div[4]/div[1]"

        log.debug('Aguardando splash screen')
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable(
            (By.XPATH, xpath_search_button)
        ))

        log.debug('Abre aba de consulta')
        driver.find_element(By.XPATH, xpath_search_button).click()
        xpath_basin_search = '//*[@id="widgets_Query_Widget_21"]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/table/tbody/tr[6]'
        WebDriverWait(driver, 60).until(EC.presence_of_element_located(
            (By.XPATH, xpath_basin_search)
        ))

        log.debug('Acessa menu de consulta por bacia hidrográfica')

        driver.find_elements(
            By.XPATH, "//tr[@role='button']"
        )[5].click()

        WebDriverWait(driver, 60).until(EC.presence_of_element_located(
            (By.CLASS_NAME, "checkedNameDiv")
        ))

        time.sleep(10)

        log.debug('Seleciona Bacia do Sao Francisco')
        driver.find_element_by_css_selector(
            'div.checkBtn > '
            'div.jimu-icon.jimu-icon-down-arrow-8.checkBtnDownIcon'
        ).click()

        driver.find_element_by_css_selector(
            '.jimu-multiple-items-list > div:nth-child(11)'
        ).click()

        driver.find_element_by_class_name("btn-execute").click()

        WebDriverWait(driver, 600).until(EC.presence_of_element_located(
            (By.CLASS_NAME, "query-result-item-table")
        ))

        driver.find_element(     
            By.XPATH, 
            "//div[@data-dojo-attach-point='btnFeatureAction']"
        ).click()

        log.debug('Visualizar na tabela de atributos')
        driver.find_elements(     
            By.XPATH, 
            "//div[@data-dojo-attach-point='labelNode']"
        )[-2].click()

        WebDriverWait(driver, 300).until(EC.presence_of_element_located(
            (By.CLASS_NAME, "dijitArrowButtonInner")
        ))

        log.debug('Carregando tabela de atributos')
        tables = driver.find_elements(By.XPATH, "//table[@class='attrTable']")

        for row in tables:
            df = pandas.read_html(
                row.get_attribute('outerHTML')
            )[0].transpose()

            if df.loc[1, 2] != 'BA':
                continue

            log.debug(f'Produtor encontrado: {df.loc[1,0]} {df.loc[1,2]}')
            df.columns = LABELS

            yield df.loc[1]
    except Exception as e:
        log.error(e)
    finally:
        driver.close()


def ana():
    success = 0
    total = 0
    series = _import()

    for reg in series:
        try:
            total += 1

            data = reg.to_dict()
            due = str(data['due_date'])
            publish = str(data['publish_date'])
            resolution = str(data['resolution'])
            data['due_date'] = due if due != 'nan' else None
            data['publish_date'] = publish if publish != 'nan' else None
            data['resolution'] = resolution if resolution != 'nan' else None

            publisher.publish('ANA', data)
            success += 1
        except Exception as e:
            log.debug(e)

    log.debug(f'{success}/{total} stored')
