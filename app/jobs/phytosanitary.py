
import glob
import imp
import logging
import os
import re
import shutil
import time
import pandas
import patoolib
from . import utils
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .. import publisher

log = logging.getLogger(__name__)


def arcgis(username: str, password: str):
    temp_dir = '/tmp/arcgis'
    url_login = (
        'https://survey123.arcgis.com/surveys'
        '/8796fcf09fee49738676d05813f1c9a6/data?'
        'report=format:docx&extent=-51.8168,-13.0272,-40.0999,-11.0718'
    )

    utils.create_temp_folder(temp_dir)

    prefs = {
        "download.default_directory": f'{temp_dir}',
        "download.prompt_for_download": False, #To auto download the file
        "download.directory_upgrade": True,
    }
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", prefs)
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    driver = webdriver.Chrome(options=options)
    driver.get(url_login)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.CLASS_NAME, "content-wrap")
    ))

    login_textbox = driver.find_element(By.ID, 'user_username')
    pw_textbox = driver.find_element(By.ID, 'user_password')
    ent_button = driver.find_element(By.ID, 'signIn')

    login_textbox.send_keys(username)
    pw_textbox.send_keys(password)

    ent_button.click()

    WebDriverWait(driver, 120).until(EC.presence_of_element_located(
        (By.TAG_NAME, "table")
    ))

    WebDriverWait(driver, 120).until(EC.presence_of_element_located(
        (By.CLASS_NAME, "esri-feature-table-column-header-title")
    ))

    time.sleep(5)

    # Encontra os menus e abre o menu de exportação
    toggle = driver.find_elements(By.XPATH, "//a[@class='dropdown-toggle']")
    toggle[1].click()

    # Sabemos que o menu 'Exportar' é o index 1.
    # A partir disso, carregar os links para arquivos
    exports = driver.find_element(By.CSS_SELECTOR, 
        '.open .dropdown-menu li:nth-child(3) a'
    )
    exports.click()

    # aguarda que o arquivo seja exportado e baixado num
    # timeout máximo de 30 segundos
    arquivos = []
    
    inicio = datetime.now()
    timeout = datetime.now() - inicio

    while len(arquivos) == 0 and timeout.seconds < 90:
        arquivos = glob.glob(f'{temp_dir}/*.zip')
        timeout = datetime.now() - inicio
        time.sleep(1)

    # logout
    logout_toggle = driver.find_elements(By.XPATH, 
        "//a[@class='dropdown-toggle user-dropdown']"
    )
    logout_toggle[0].click()
    logout_bts = driver.find_elements(By.XPATH, "//li[@class='buttons']")
    bts = logout_bts[0].find_elements(By.TAG_NAME, "div")
    bts[1].click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.TAG_NAME, "button")
    ))

    driver.close()

    if len(arquivos) == 0:
        log.debug('No files found')
        return

    # Extrai
    patoolib.extract_archive(arquivos[-1], outdir=temp_dir)

    # Carrega o shapefile
    reader = pandas.read_csv(temp_dir + '/surveyPoint_1.csv', chunksize=10)

    for df in reader:
        df.drop(columns=['ObjectID'], inplace=True)

        # registra em tópico kafka
        sucesso = 0
        i = 0
        for reg in df.iterrows():
            i += 1

            try:
                publisher.publish('PHYTOSANITARY', reg[1])
                sucesso += 1
            except Exception as e:
                log.debug(e)

    # Apaga arquivos utilizados
    shutil.rmtree(temp_dir)


def phytosanitary():  # noqa: max-complexity: 12
    search_date = datetime.utcnow().strftime('%Y-%m-%d')
    date_aux = datetime.strptime(search_date, '%Y-%m-%d').strftime('%d-%m-%Y')
    url = f'https://www.in.gov.br/leiturajornal?data={date_aux}'
    grant_type = 'Programa Nacional de Controle da Ferrugem Asiática da Soja'
    ministerio = 'Ministério da Agricultura, Pecuária e Abastecimento'
    secoes = ['DO1', 'DO2', 'DO3', 'DO1e', 'DO2e', 'DO3e']
    labels = ['date', 'link', 'file']

    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    options.add_argument('window-size=1024x768')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    driver = webdriver.Chrome(options=options)

    inicio = datetime.now()
    link_final = []
    quantEncontrado = 0

    for s in secoes:
        driver.get(f'{url}&secao={s}')

        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.CLASS_NAME, "materia-link")
            ))

            link = ""
            is_found = False

            nav_page = driver.find_elements(
                By.XPATH,
                "//span[@class='pagination-button']"
            )
            has_next = True
            pagina = 1

            while has_next and not is_found:
                log.debug(f'Seção {s} - Página {pagina}')
                pagina += 1
                materias = driver.find_elements(
                    By.XPATH,
                    "//li[@class='materia-link']")
                i = 0

                while i < len(materias) and not is_found:
                    materias = driver.find_elements(
                        By.XPATH,
                        "//li[@class='materia-link']")

                    if len(
                        re.findall(
                            ministerio.lower(),
                            materias[i].get_attribute('innerHTML').lower()
                        )
                    ) > 0:
                        log.debug(
                            f'{i} pertence ao ministerio. '
                            'Verificar se é o documento de interesse'
                        )

                        link = materias[i].find_element(By.TAG_NAME, 
                            'a').get_attribute("href")

                        driver.execute_script("window.open('');")
                        driver.switch_to.window(driver.window_handles[1])
                        driver.get(link)

                        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                            (By.CLASS_NAME, "texto-dou")
                        ))

                        if len(re.findall(grant_type.lower(), driver.find_element(By.XPATH, "//div[@class='texto-dou']").get_attribute("innerHTML").lower())) > 0:  # noqa: E501
                            is_found = False
                            log.debug(f'{i} encontrado {link}')
                            link_final.append(link)

                            link_pdf = driver.find_element(By.ID, 'versao-certificada').get_attribute("href")  # noqa: E501
                            driver.get(link_pdf)

                            baixar = driver.find_elements(By.XPATH,"//frame")[1].get_attribute("src")  # noqa: E501
                            # a = requests.get(baixar)
                            # pdf_para_envio = base64.b64encode(a.content)

                            # to-do: mudar date_aux para search_date quando api mudar o formato da data # noqa: E501
                            reg = pandas.Series([date_aux, link], index=labels)
                            publisher.publish('ANNUAL_ORDINANCE', reg)
                            quantEncontrado += 1

                        else:
                            driver.back()
                            log.debug(f'{i} não é o documento... voltando')
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])

                    i += 1

                nav_page = driver.find_elements(
                    By.XPATH,
                    "//span[@class='pagination-button']")

                try:
                    if 'Próximo »' in nav_page[0].text and not is_found:
                        log.debug('Proxima pagina')
                        has_next = True
                        nav_page[0].click()
                    elif 'Próximo »' in nav_page[1].text and not is_found:
                        log.debug('Proxima pagina')
                        has_next = True
                        nav_page[1].click()
                    else:
                        log.debug(
                            'Última pagina da seção ou arquivo foi encontrado')
                        has_next = False
                except Exception:
                    log.debug(
                        'Última pagina da seção ou arquivo foi encontrado')
                    has_next = False
        except TimeoutException:
            pass

    log.debug(f'Foram encontradas {quantEncontrado} outorga(s)')
    log.debug(f'Tempo de processamento: {str(datetime.now() - inicio)}')

    driver.close()
