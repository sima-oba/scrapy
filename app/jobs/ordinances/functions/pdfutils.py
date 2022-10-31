#coding: utf-8
import pdfplumber, traceback, pytesseract, shutil
import os
import re
import time
import glob as glob
import cv2
import numpy as np
import logging
from . import utils

from datetime import datetime as dt, timedelta as td
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
from pdf2image import convert_from_path 


log = logging.getLogger(__name__)

#  
#  name: Extrai texto de um pdf
#  @ param: file directory
#  @ return: pdf pages as array if strings
#  
def extract_page_text(filename):
    print("Extracting text from PDF")
    text = []
    try:
        with pdfplumber.open(filename) as pdf:
            for n_page in range(len(pdf.pages)):
                text.append(pdf.pages[n_page].extract_text())
                text[n_page] = text[n_page].replace('\n', '')
                
            pdf.close()
    except Exception:
        traceback.print_exc()
        
    return text

#  
#  name: Extrai texto de um pdf utilizando OCR
#  @ param: file directory
#  @ return: pdf pages as array of strings
#  
def ocr_extract_page_text(filename, details = 0):
    try:
        folder = f'extract_ocr_{dt.now()}/'
        utils.create_temp_folder(folder)
        print('Extracting images')
        pages = convert_from_path(filename, 250) 
        print('Saving images to temp_folder')
        image_counter = 1
        for page in pages:
            filename = f'{folder}pre_{image_counter}.jpg'
            page.save(filename, 'JPEG')

            img_bgr = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

            matrix = np.ones(img_rgb.shape, dtype = 'uint8') * details

            img_rgb_brighter = cv2.add(img_rgb, matrix)

            img_rgb_darker = cv2.subtract(img_rgb_brighter, matrix)

            cv2.imwrite(f'{folder}page_{image_counter}.jpg', img_rgb_brighter)
            
            image_counter += 1

        pages = []

        print(f'Extracting text from {image_counter-1} pages...')
        for count in range(1,image_counter):
            # print(f'Page {count}...')
            text = pytesseract.image_to_string(
                Image.open(
                    f'{folder}page_{count}.jpg'
                )
            )
            text = text.replace('\n\n', '').replace('\n', ' ')
            pages.append(text)

    except:
        traceback.print_exc()
        pages = []

    finally:

        shutil.rmtree(folder)
                    
    return pages

#  
#  name: Diário Oficial de Barreiras (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: reponse from download pdf DOM based on date to a pdf file
#  
def barreiras_dom(search_date):  
    search_date = dt.strptime(search_date, '%Y-%m-%d')

    url_base = f'https://barreiras.ba.gov.br/diario-oficial'
    url = ''
    
    if search_date.year == dt.today().year:
        url = f'{url_base}/'
    else :
        url = f'{url_base}-{search_date.year}/'
        
    print(f'Access {url}')
    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    options.add_argument('window-size=1024x768')
    driver = webdriver.Chrome(options=options)

    driver.get(url)

    all_dates = driver.find_elements(By.XPATH, '//a[strong]')
    # len(all_dates)
    pdf_link = ''
    
    print(f'Searching date {search_date.strftime("%d/%m/%Y")}')
    for diary in all_dates:
        if diary.get_attribute('outerHTML').find(search_date.strftime('%d/%m/%Y')) > -1:
            pdf_link = diary.get_attribute('href')
            print(f'Found: {pdf_link}')        

    driver.close()

    filename = ''
    r = ''
    temp_folder = 'portarias-dom-barreiras/'

    if pdf_link != '':
        utils.create_temp_folder(temp_folder)

        print('Downloading pdf document')
        filename = temp_folder+'DOM_Barreiras_'+search_date.strftime('%Y-%m-%d')+'.pdf'
        r = utils.download_to_file(pdf_link, filename)
    
    return filename, temp_folder, pdf_link, r

#  
#  name: Diário Oficial de Luís Eduardo Magalhães (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name
#  TODO: portal modificado
def lem_dom(s_date):
    print('Acessing LEM diary')
    # s_date = '2021-04-30'
    search_date = dt.strptime(s_date, '%Y-%m-%d')
    url = f'http://dom.imap.org.br/sitesMunicipios/imprensaOficial.cfm?varCodigo=469'

    temp_folder = 'portarias-dom-lem/'
    utils.create_temp_folder(temp_folder)
    
    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    # options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    options.add_argument('window-size=1024x768')
    profile = {#"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    select_year_xpath = '//*[@id="cboAno"]'
    search_button_xpath = '/html/body/div/div[1]/div/div/div/div/div/form/div/div[5]/div/input'

    select = Select(driver.find_element(By.XPATH, select_year_xpath))
    select.select_by_visible_text(str(search_date.year))

    driver.find_element(By.XPATH, search_button_xpath).click()

    # busca todas as datas na página
    all_itens = driver.find_elements(By.CLASS_NAME, "todo-task")

    # filtra todas as datas buscando as publicações para o dia escolhido extraindo os links
    s_date = search_date.strftime("%d/%m/%Y")
    links = []
    for item in all_itens:
        if item.get_attribute('outerHTML').find(s_date) > -1:
            link = item.find_element(By.TAG_NAME, 'a').get_attribute("href")
            links.append(link)


    # faz o download dos arquivos
    files = []
    for link in links:
        filename = f'{temp_folder}{search_date} - {links.index(link)}.pdf'
        response = utils.download_to_file(link, filename)
        if response.ok:
            files.append(filename)
    
    return files, temp_folder, links

#  
#  name: Diário Oficial de São Desidério (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name, PDF urls
#
def dom_sao_desiderio(s_date):
    search_date = dt.strptime(s_date, '%Y-%m-%d')

    url = 'http://www.acessoinformacao.com.br/ba/saodesiderio/#diario-oficial'

    temp_folder = "portarias-sao-desiderio/"

    utils.create_temp_folder(temp_folder)        

    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    options.add_argument('window-size=1024x768')
    profile = {#"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
               "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
               "download.extensions_to_open": "applications/pdf",
               "download.prompt_for_download": False, #To auto download the file
               "download.directory_upgrade": True,
               "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
              }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)

    driver.get(url)

    # seleciona o ano
    xpath_select = f'//*[@id="_f_ano"]'

    select = Select(driver.find_element(By.XPATH, xpath_select))
    select.select_by_visible_text(str(search_date.year))

    driver.find_element(By.XPATH, '//*[@id="doem-container"]/div/form/div[2]/div[2]/div/button').click()

    # encontra as datas
    xpath = '//div[@class="panel panel-default"]'
    month_dates = driver.find_elements(By.XPATH, xpath)[-search_date.month].find_elements(By.TAG_NAME, 'tr')

    # separa os possíveis links para a data escolhida
    link = []
    for i in range(len(month_dates)):
        if month_dates[i].get_attribute("outerHTML").find(search_date.strftime('%d/%m/%Y')) > -1:
            aux= re.findall(r'href=\"(.*?)\"', month_dates[i+1].get_attribute('outerHTML'))
            for i2 in range(len(aux)):
                link.append(aux[i2])
                
    # encontra os links das publicações da data escolhida
    download_queue = []
    for i in range(len(link)):
        if (link[i].find('javascript') > -1):
            try:
                download_queue.append(link[i+1])
            except:
                pass

    # baixa os arquivos
    for pdf_link in download_queue:
        driver.get(pdf_link)

    print("Waiting download file(s)")
    # espera que todos os arquivos sejam baixados ou timeout de 60 segundos
    inicio = dt.now()
    timeout = dt.now() - inicio
    downloaded_files = glob.glob(f'{temp_folder}*.pdf')
    while len(download_queue) > len(downloaded_files) and timeout.seconds < 60:
        downloaded_files = glob.glob(f'{temp_folder}*.pdf')
        timeout = dt.now() - inicio
    # driver.close()

    driver.close()
    
    return downloaded_files, temp_folder, download_queue

#  
#  name: Diário Oficial de Correntina (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name
#
def dom_correntina(s_date):
    search_date = dt.strptime(s_date, '%Y-%m-%d')
    
    url = f'https://sai.io.org.br/ba/correntina/site/diariooficial'

    temp_folder = 'portarias-dom-correntina/'
    
    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    options.add_argument('window-size=1024x768')
    profile = {
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1024, 768)

    driver.get(url) 

    # preenche os campos de busca com a data desejada
    el_start_date = driver.find_element(By.ID, 'diarioOficial_dataInicial')
    el_end_date = driver.find_element(By.ID, 'diarioOficial_dataFinal')

    el_start_date.send_keys(search_date.strftime('%d%m%Y'))
    el_end_date.send_keys(search_date.strftime('%d%m%Y'))

    xpath = '//input[@type="submit"]'
    bt = driver.find_element(By.XPATH, xpath)

    try:
        bt.click()
    except:
        bt.click()

    try:
        tabela = driver.find_element(By.XPATH, '//table')
        docs = tabela.find_elements(By.TAG_NAME, 'a')
    except:
        log.debug("No publications founded")
        docs = []    
    
    download_queue = [] 

    for doc in docs:
        download_queue.append(doc.get_attribute('href'))
    
    
    downloaded_files = []
    links = []

    for i in range(len(download_queue)):
        utils.download_to_file(download_queue[i], f'{temp_folder}{search_date} - {i}.pdf')
        downloaded_files.append(f'{temp_folder}{search_date} - {i}.pdf')
        links.append(download_queue[i])
            
    driver.quit()

    return downloaded_files, temp_folder, links

#  
#  name: Diário Oficial de Riachão das Neves (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name
#  
def dom_riachao_neves(s_date):
    try:
        print('Acessing Riachão das Neves diary')
        search_date = dt.strptime(s_date, '%Y-%m-%d')
        url = f'http://www.riachaodasneves.ba.io.org.br/diarioOficial/index/645/{search_date.year}/-/-/-/-/-/-/-/-/-'

        temp_folder = 'portarias-dom-riachao/'
        
        options = webdriver.ChromeOptions()
        options.add_argument('ignore-certificate-errors')
        options.add_argument('headless')
        options.add_argument('disable-dev-shm-usage')
        options.add_argument('disable-gpu')
        options.add_argument('window-size=1024x768')
        profile = {#"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
                "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
                "download.extensions_to_open": "applications/pdf",
                "download.prompt_for_download": False, #To auto download the file
                "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
                }
        options.add_experimental_option("prefs", profile)
        driver = webdriver.Chrome(options=options)
        driver.get(url)

        print("Locating month")
        # encontra botão referente ao mês. Datas só podem ser clicadas se estiverem visíveis
        all_months = driver.find_elements(By.XPATH, '//ul[@class="konsertina"]')
        ActionChains(driver).move_to_element(all_months[-search_date.month]).click().perform()
    #     print(all_months[-search_date.month].get_attribute('outerHTML'))
        

        print(f'Searching publication(s) in {search_date.strftime("%d/%m/%Y")}')
        # encontra todas as datas disponíveis na página
        all_dates = driver.find_elements(By.XPATH, '//li')

        # encontra os links corretos para a data desejada
        i = 0
        download_queue = []
        links = []
        for i in range(len(all_dates)):
            link_date = re.findall(r'href="(.*?)"(.*?)&', all_dates[i].get_attribute('outerHTML'))

            try:
                if link_date[0][1][1:] == search_date.strftime('%d/%m/%Y'):
                    links.append(link_date[1][0].replace('diarioOficiaI', 'diarioOficial'))
                    download_queue.append(i)
            except:
                pass
            
        
        downloaded_files = []
        if len(download_queue) > 0:
            utils.create_temp_folder(temp_folder)
            
            print("Start download file(s)")
            for i in download_queue:
                try:
                    # clica na data
                    ActionChains(driver).move_to_element(all_dates[i]).perform()
                    all_dates[i].click()

                    # clica no documento para iniciar o download
                    link = all_dates[i].find_elements(By.TAG_NAME, 'a')[2]
    #                 ActionChains(driver).move_to_element(link).click().perform()
    #                 link
                    driver.execute_script("arguments[0].click();", link)
                except:
                    traceback.print_exc()
                    pass

            print("Waiting download file(s)")
            # espera que todos os arquivos sejam baixados. Segue o fluxo caso estoure o timeout de 30 segundos
            inicio = dt.now()
            timeout = dt.now() - inicio
            while len(download_queue) > len(downloaded_files) and timeout.seconds < 60:
                downloaded_files = glob.glob(f'{temp_folder}*.pdf')
                timeout = dt.now() - inicio
            print(downloaded_files)
            
        else:
            print(f'No publications found in {search_date.strftime("%d/%m/%Y")}')
    except:
        downloaded_files = []
        traceback.print_exc()

    return downloaded_files, temp_folder, links

#  
#  name: Diário Oficial de Formosa do Rio Preto (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name, download links
#  
def dom_formosa_rio_preto(s_date):
    print('Acessing Formosa do Rio Preto diary')
    url = f'http://doem.org.br/ba/formosadoriopreto?dt={s_date}'

    temp_folder = 'portarias-dom-formosa/'
    utils.create_temp_folder(temp_folder)

    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    options.add_argument('window-size=1024x768')
    profile = {#"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    driver.find_element(By.XPATH, '//*[@class="btn btn-primary btn-lg btn-accept-all-privacy-and-terms"]').click()

    download_links = []

    len_queue = 0

    try:
        # para caso de uma publicação no dia (mostrada diretamente na página)
        # entra no iframe para conseguir localizar o link (caso data tenha uma única publicação)
        xpath = '//*[@id="pdf-iframe"]'
        iframe = driver.find_element(By.XPATH, xpath)
        driver.switch_to.frame(iframe)

        # localiza link dentro da janela de visualização
        xpath = '//*[@id="pdfjs-object"]'
        link = driver.find_element(By.XPATH, xpath).get_attribute('data')
        download_links.append(link)
        driver.get(link)
        
        # marca quantas publicações foram encontradas
        len_queue = 1
        print(f'{len_queue} publication found')

        # acessa pdf e faz o download através do botão
        xpath = '//*[@id="download"]'
        download_button = driver.find_element(By.XPATH, xpath)
        ActionChains(driver).move_to_element(download_button).click().perform()
        
    except:
        # localiza os botões que levam ao PDF's
        xpath = '//*[@class="btn btn-xs btn-default pull-right"]'
        view_buttons = driver.find_elements(By.XPATH, xpath)
            
        # marca quantas publicações foram encontradas
        len_queue = len(view_buttons)
        print(f'{len_queue} publications found')

        for view_bt in view_buttons:
            # acessa pdf publicado através do botão
            ActionChains(driver).move_to_element(view_bt).click().perform()
            driver.switch_to.window(driver.window_handles[1])

            # localiza link dentro da janela de visualização
            xpath = '//*[@id="pdfjs-object"]'
            link = driver.find_element(By.XPATH, xpath).get_attribute('data')
            download_links.append(link)
        
            # acessa pdf e faz o download através do botão
            driver.get(link)
            xpath = '//*[@id="download"]'
            download_button = driver.find_element(By.XPATH, xpath)
            ActionChains(driver).move_to_element(download_button).click().perform()

            # fecha a janela 
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
    
    if len_queue > 0:    
        print("Waiting download file(s)")

    # espera que todos os arquivos sejam baixados. Segue o fluxo caso estoure o timeout de 30 segundos
    inicio = dt.now()
    timeout = dt.now() - inicio
    downloaded_files = glob.glob(f'{temp_folder}*.pdf')
        
    while len_queue > len(downloaded_files) and timeout.seconds < 30:
        # recupera os nomes de arquivos baixados em pela ordem em que foram baixados
        downloaded_files = sorted(glob.glob(f'{temp_folder}*.pdf'), key = os.path.getmtime)
        timeout = dt.now() - inicio
    # print(downloaded_files)

    driver.quit()

    return downloaded_files, temp_folder, download_links

#  
#  name: Diário Oficial de Cocos (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name, download links
#  
def dom_cocos(search_date):
    url = 'http://www.cocos.ba.gov.br/diario_oficial'
    
    search_date = dt.strptime(search_date, '%Y-%m-%d')

    temp_folder = 'cocos-download/'

    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    driver = webdriver.Chrome(options=options)
    profile = {#"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    
    # carrega o calendário do mês
    print('Loading month')
    xpath = '//*[@id="diarios_publicados"]'
    text = f'{utils.month_name[search_date.month]} - {search_date.year}'

    select = Select(driver.find_element(By.XPATH, xpath))
    select.select_by_visible_text(text)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "td")))

    # encontra o pdf no calendário do mês
    print('Searching date')
    for el in driver.find_elements(By.TAG_NAME, 'td'):
        html = el.get_attribute('outerHTML')
    #     print(html)
    #     print(re.findall(r'>(\d*)</', html))
        if re.findall(r'>(\d*)</', html)[0] == str(search_date.day):
            try:
                print('Downloading file')
                link = re.findall(r'href="(.*)" ', html)
                el.click()
            except:
                print('No publication for selected date')
                return [], temp_folder, []
    #     print()

    downloaded_files = glob.glob(f'{temp_folder}*.pdf')
    inicio = dt.now()
    timeout = dt.now()- inicio

    while timeout.seconds < 30 and len(downloaded_files) == 0:
        downloaded_files = glob.glob(f'{temp_folder}*.pdf')
        timeout = dt.now()- inicio

    return downloaded_files, temp_folder, link

#  
#  name: Diário Oficial de Jaborandi (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name, download links
#  
def dom_jaborandi(search_date):
    url = 'http://ba.portaldatransparencia.com.br/prefeitura/jaborandi/index.cfm'

    temp_folder = 'jaborandi-download/'
    utils.create_temp_folder(temp_folder)
    search_date = dt.strptime(search_date, '%Y-%m-%d')

    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    profile = {#"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)

    print("Acessing Jaborandi DOM")
    driver.get(url)

    print('Searching date')
    input_date = driver.find_element(By.XPATH, '//*[@id="data_publicacao"]')
    input_date.send_keys(search_date.strftime('%d%m%Y'))

    bt_search = driver.find_element(By.XPATH, '//*[@id="buscaExt"]/button[1]')
    bt_search.click()

    bt_download = driver.find_elements(By.XPATH, '//a[@class="btn btn_visualizar hidden-desktop"]')
    links = []
    for bt in bt_download: 
        url_pdf = bt.get_attribute("href")
        links.append(url_pdf)
        driver.get(url_pdf)

    print(f'Waiting download {len(links)} file(s)')
    downloaded_files = glob.glob(f'{temp_folder}*.pdf')
    inicio = dt.now()
    timeout = dt.now()- inicio

    while timeout.seconds < 30 and len(downloaded_files) < len(bt_download):
        downloaded_files = glob.glob(f'{temp_folder}*.pdf')
        timeout = dt.now()- inicio

        for f in downloaded_files:
            if f.find('crdownload') > -1:
                downloaded_files = []

    driver.quit()

    return downloaded_files, links, temp_folder

#  
#  name: Diário Oficial de Baianópolis (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name, download links
#  
def dom_baianopolis(search_date):
    search_date = dt.strptime(search_date, '%Y-%m-%d')

    url = f'https://sai.io.org.br/ba/baianopolis/Site/DiarioOficial'

    temp_folder = 'portarias-dom-baianopolis/'

    utils.create_temp_folder(temp_folder)

    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    options.add_argument('window-size=1024x768')
    profile = {
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1024, 768)

    driver.get(url) 

    # preenche os campos de busca com a data desejada
    el_start_date = driver.find_element(By.ID, 'diarioOficial_dataInicial')
    el_end_date = driver.find_element(By.ID, 'diarioOficial_dataFinal')

    el_start_date.send_keys(search_date.strftime('%d%m%Y'))
    el_end_date.send_keys(search_date.strftime('%d%m%Y'))

    xpath = '//input[@type="submit"]'
    bt = driver.find_element(By.XPATH, xpath)

    try:
        bt.click()
    except:
        bt.click()

    try:
        tabela = driver.find_element(By.XPATH, '//table')
        docs = tabela.find_elements(By.TAG_NAME, 'a')
    except:
        log.debug("No publications founded")
        docs = []
    
    download_queue = [] 

    for doc in docs:
        download_queue.append(doc.get_attribute('href'))
    
    
    downloaded_files = []
    links = []

    for i in range(len(download_queue)):
        utils.download_to_file(download_queue[i], f'{temp_folder}{search_date} - {i}.pdf')
        downloaded_files.append(f'{temp_folder}{search_date} - {i}.pdf')
        links.append(download_queue[i])
            
    driver.quit()

    return downloaded_files, links, temp_folder
    
#  
#  name: ibama embargos e autos de infração
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name
#  
def ibama(start_date):
    url = 'https://servicos.ibama.gov.br/ctf/publico/areasembargadas/ConsultaPublicaAreasEmbargadas.php'
    temp_folder = 'ibama-download/'
    utils.create_temp_folder(temp_folder)

    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    # driver = webdriver.Chrome(options=options)
    profile = {
        "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
        "download.extensions_to_open": "applications/pdf",
        "download.prompt_for_download": False, #To auto download the file
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
    }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)

    try:
        print(f'Access: {url}')
        driver.get(url)

        xpath = '//*[@id="sit_isencao_lic_transporte_A"]'
        driver.find_element(By.XPATH, xpath).click()

        xpath = '//*[@id="dat_inicial"]'
        data_inicio = driver.find_element(By.XPATH, xpath)

        xpath = '//*[@id="dat_final"]'
        data_final = driver.find_element(By.XPATH, xpath)

        data_inicio.send_keys(dt.strptime(start_date, '%Y-%m-%d').strftime('%d%m%Y'))
        data_final.send_keys(dt.today().strftime('%d%m%Y'))

        xpath = '//*[@id="btn_gerarPdfAuto"]'
        driver.find_element(By.XPATH, xpath).click()

        url_pdf = driver.find_element(By.XPATH, '//iframe').get_attribute('src')

        driver.get(url_pdf)

        downloaded_files = glob.glob(f'{temp_folder}*.pdf')
        inicio = dt.now()
        timeout = dt.now()- inicio

        while timeout.seconds < 30 and len(downloaded_files) == 0:
            downloaded_files = glob.glob(f'{temp_folder}*.pdf')
            
            for f in downloaded_files:
                if f.find('crdownload') > -1:
                    downloaded_files = []
                    
            timeout = dt.now()- inicio
        
    except:
        downloaded_files = []   

    finally:
        driver.close()

    print(downloaded_files)
    
    return downloaded_files, temp_folder

#  
#  name: Diário Oficial de Santa Rita de Cássia (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name, download links
#  
def dom_srcassia(search_date):
    url = 'http://www.portaldatransparencia.com.br/prefeitura/santaritadecassia/'

    temp_folder = 'srcassia-download/'
    utils.create_temp_folder(temp_folder)
    search_date = dt.strptime(search_date, '%Y-%m-%d')

    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    profile = {#"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)

    print("Acessing Santa Rita de Cássia DOM")
    driver.get(url)

    print('Searching date')
    input_date = driver.find_element(By.XPATH, '//*[@id="data_publicacao"]')
    input_date.send_keys(search_date.strftime('%d%m%Y'))

    bt_search = driver.find_element(By.XPATH, '//*[@id="buscaExt"]/button[1]')
    bt_search.click()

    bt_download = driver.find_elements(By.XPATH, '//a[@class="btn btn_visualizar hidden-desktop"]')
    links = []
    for bt in bt_download: 
        url_pdf = bt.get_attribute("href")
        links.append(url_pdf)
        driver.get(url_pdf)

    print(f'Waiting download {len(links)} file(s)')
    downloaded_files = glob.glob(f'{temp_folder}*.pdf')
    inicio = dt.now()
    timeout = dt.now()- inicio

    while timeout.seconds < 30 and len(downloaded_files) < len(bt_download):
        downloaded_files = sorted(glob.glob(f'{temp_folder}*.pdf'), key = os.path.getmtime)
        timeout = dt.now() - inicio
        
        for f in downloaded_files:
            if f.find('crdownload') > -1:
                print(downloaded_files)
                downloaded_files = []

    driver.quit()

    return downloaded_files, links, temp_folder

#  
#  name: Diário Oficial de Wanderley (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name, download links
#  
def dom_wanderley(search_date):
    url = 'http://www.portaldatransparencia.com.br/prefeitura/wanderley/'

    temp_folder = 'wanderley-download/'
    utils.create_temp_folder(temp_folder)
    search_date = dt.strptime(search_date, '%Y-%m-%d')

    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    profile = {#"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)

    print("Acessing Wanderley DOM")
    driver.get(url)

    print('Searching date')
    input_date = driver.find_element(By.XPATH, '//*[@id="data_publicacao"]')
    input_date.send_keys(search_date.strftime('%d%m%Y'))

    bt_search = driver.find_element(By.XPATH, '//*[@id="buscaExt"]/button[1]')
    bt_search.click()

    bt_download = driver.find_elements(By.XPATH, '//a[@class="btn btn_visualizar hidden-desktop"]')
    links = []
    for bt in bt_download: 
        url_pdf = bt.get_attribute("href")
        links.append(url_pdf)
        driver.get(url_pdf)

    print(f'Waiting download {len(links)} file(s)')
    downloaded_files = glob.glob(f'{temp_folder}*.pdf')
    inicio = dt.now()
    timeout = dt.now()- inicio

    while timeout.seconds < 30 and len(downloaded_files) < len(bt_download):
        downloaded_files = sorted(glob.glob(f'{temp_folder}*.pdf'), key = os.path.getmtime)
        timeout = dt.now() - inicio
        
        for f in downloaded_files:
            if f.find('crdownload') > -1:
                print(downloaded_files)
                downloaded_files = []

    driver.quit()

    return downloaded_files, links, temp_folder

#  
#  name: Diário Oficial de Santa Maria da Vitória (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name, download links
#  
def dom_smvitoria(search_date):
    url = 'http://ba.portaldatransparencia.com.br/prefeitura/santamariadavitoria/'

    temp_folder = 'smvitoria-download/'
    utils.create_temp_folder(temp_folder)
    search_date = dt.strptime(search_date, '%Y-%m-%d')
    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    profile = {#"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)

    print("Acessing Santa Maria da Vitória DOM")
    
    driver.get(url)
    print('Searching date')
    input_date = driver.find_element(By.XPATH, '//*[@id="data_publicacao"]')
    input_date.send_keys(search_date.strftime('%d%m%Y'))

    bt_search = driver.find_element(By.XPATH, '//*[@id="buscaExt"]/button[1]')
    bt_search.click()
    bt_download = driver.find_elements(By.XPATH, '//a[@class="btn btn_visualizar hidden-desktop"]')
    links = []
    for bt in bt_download: 
        url_pdf = bt.get_attribute("href")
        links.append(url_pdf)
        driver.get(url_pdf)
        
    print(f'Waiting download {len(links)} file(s)')
    downloaded_files = glob.glob(f'{temp_folder}*.pdf')
    inicio = dt.now()
    timeout = dt.now()- inicio

    while timeout.seconds < 30 and len(downloaded_files) < len(bt_download):
        downloaded_files = sorted(glob.glob(f'{temp_folder}*.pdf'), key = os.path.getmtime)
        timeout = dt.now() - inicio
        
        for f in downloaded_files:
            if f.find('crdownload') > -1:
                print(downloaded_files)
                downloaded_files = []

    driver.quit()

    return downloaded_files, links, temp_folder

#  
#  name: Diário Oficial de Mansidão (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name, download links
#  
def dom_mansidao(search_date):
    search_date = dt.strptime(search_date, '%Y-%m-%d')
    
    url = f'https://www.mansidao.ba.gov.br/site/diariooficial'

    temp_folder = 'portarias-dom-mansidao/'
    
    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    options.add_argument('window-size=1024x768')
    profile = {
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1024, 768)

    driver.get(url) 

    # preenche os campos de busca com a data desejada
    el_start_date = driver.find_element(By.ID, 'diarioOficial_dataInicial')
    el_end_date = driver.find_element(By.ID, 'diarioOficial_dataFinal')

    el_start_date.send_keys(search_date.strftime('%d%m%Y'))
    el_end_date.send_keys(search_date.strftime('%d%m%Y'))

    xpath = '//input[@type="submit"]'
    bt = driver.find_element(By.XPATH, xpath)

    try:
        bt.click()
    except:
        bt.click()

    try:
        tabela = driver.find_element(By.XPATH, '//table')
        docs = tabela.find_elements(By.TAG_NAME, 'a')
    except:
        log.debug("No publications founded")
        docs = []    
    
    download_queue = [] 

    for doc in docs:
        download_queue.append(doc.get_attribute('href'))
    
    
    downloaded_files = []
    links = []

    for i in range(len(download_queue)):
        utils.download_to_file(download_queue[i], f'{temp_folder}{search_date} - {i}.pdf')
        downloaded_files.append(f'{temp_folder}{search_date} - {i}.pdf')
        links.append(download_queue[i])
            
    driver.quit()


    return downloaded_files, links, temp_folder

#  
#  name: Diário Oficial de Angical (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name, download links
#  
def dom_angical(search_date):
    url_old = 'http://www.portaldatransparencia.com.br/prefeitura/angical/'
    url_new = f'http://doem.org.br/ba/angical?dt={search_date}'


    temp_folder = 'angical-download/'
    utils.create_temp_folder(temp_folder)
    search_date = dt.strptime(search_date, '%Y-%m-%d')
    
    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    profile = {#"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)

    print("Acessing Angical DOM")
    if search_date.year <= 2020:
        # portal com publicações até 2020
        driver.get(url_old)

        print('Searching date')
        input_date = driver.find_element(By.XPATH, '//*[@id="data_publicacao"]')
        input_date.send_keys(search_date.strftime('%d%m%Y'))

        bt_search = driver.find_element(By.XPATH, '//*[@id="buscaExt"]/button[1]')
        bt_search.click()
        bt_download = driver.find_elements(By.XPATH, '//a[@class="btn btn_visualizar hidden-desktop"]')
        download_links = []
        for bt in bt_download: 
            url_pdf = bt.get_attribute("href")
            download_links.append(url_pdf)
            driver.get(url_pdf)
        
        # marca quantas publicações foram encontradas
        len_queue = len(download_links)
        print(f'{len_queue} publications found')


    else:
        # portal com publicações a partir de 2021
        driver.get(url_new)

        driver.find_element(By.XPATH, '//*[@class="btn btn-primary btn-lg btn-accept-all-privacy-and-terms"]').click()

        download_links = []

        len_queue = 0

        try:
            # para caso de uma publicação no dia (mostrada diretamente na página)
            # entra no iframe para conseguir localizar o link (caso data tenha uma única publicação)
            xpath = '//*[@id="pdf-iframe"]'
            iframe = driver.find_element(By.XPATH, xpath)
            driver.switch_to.frame(iframe)

            # localiza link dentro da janela de visualização
            xpath = '//*[@id="pdfjs-object"]'
            link = driver.find_element(By.XPATH, xpath).get_attribute('data')
            download_links.append(link)
            driver.get(link)
            
            # marca quantas publicações foram encontradas
            len_queue = 1
            print(f'{len_queue} publication found')

            # acessa pdf e faz o download através do botão
            xpath = '//*[@id="download"]'
            download_button = driver.find_element(By.XPATH, xpath)
            ActionChains(driver).move_to_element(download_button).click().perform()
            
        except:
            # localiza os botões que levam ao PDF's
            xpath = '//*[@class="btn btn-xs btn-default pull-right"]'
            view_buttons = driver.find_elements(By.XPATH, xpath)
                
            # marca quantas publicações foram encontradas
            len_queue = len(view_buttons)
            print(f'{len_queue} publications found')

            for view_bt in view_buttons:
                # acessa pdf publicado através do botão
                ActionChains(driver).move_to_element(view_bt).click().perform()
                driver.switch_to.window(driver.window_handles[1])

                # localiza link dentro da janela de visualização
                xpath = '//*[@id="pdfjs-object"]'
                link = driver.find_element(By.XPATH, xpath).get_attribute('data')
                download_links.append(link)
            
                # acessa pdf e faz o download através do botão
                driver.get(link)
                xpath = '//*[@id="download"]'
                download_button = driver.find_element(By.XPATH, xpath)
                ActionChains(driver).move_to_element(download_button).click().perform()

                # fecha a janela 
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

        if len_queue > 0:    
            print("Waiting download file(s)")

    # espera que todos os arquivos sejam baixados. Segue o fluxo caso estoure o timeout de 30 segundos
    print(f'Waiting download {len(download_links)} file(s)')
    downloaded_files = glob.glob(f'{temp_folder}*.pdf')
    inicio = dt.now()
    timeout = dt.now()- inicio

    while timeout.seconds < 30 and len(downloaded_files) < len_queue:
        downloaded_files = sorted(glob.glob(f'{temp_folder}*.pdf'), key = os.path.getmtime)
        timeout = dt.now() - inicio
        
        for f in downloaded_files:
            if f.find('crdownload') > -1:
                print(downloaded_files)
                downloaded_files = []

   
    return downloaded_files, download_links, temp_folder

#  
#  name: Diário Oficial de Coribe (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name, download links
#  
def dom_coribe(search_date):
    search_date = dt.strptime(search_date, '%Y-%m-%d')

    url = f'https://www.coribe.ba.gov.br/Site/DiarioOficial'

    temp_folder = 'portarias-dom-coribe/'

    utils.create_temp_folder(temp_folder)

    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    options.add_argument('window-size=1024x768')
    profile = {
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1024, 768)

    driver.get(url) 

    # preenche os campos de busca com a data desejada
    el_start_date = driver.find_element(By.ID, 'diarioOficial_dataInicial')
    el_end_date = driver.find_element(By.ID, 'diarioOficial_dataFinal')

    el_start_date.send_keys(search_date.strftime('%d%m%Y'))
    el_end_date.send_keys(search_date.strftime('%d%m%Y'))

    xpath = '//input[@type="submit"]'
    bt = driver.find_element(By.XPATH, xpath)

    try:
        bt.click()
    except:
        bt.click()

    try:
        tabela = driver.find_element(By.XPATH, '//table')
        docs = tabela.find_elements(By.TAG_NAME, 'a')
    except:
        log.debug("No publications founded")
        docs = []

    download_queue = [] 

    for doc in docs:
        download_queue.append(doc.get_attribute('href'))
    
    
    downloaded_files = []
    links = []

    for i in range(len(download_queue)):
        utils.download_to_file(download_queue[i], f'{temp_folder}{search_date} - {i}.pdf')
        downloaded_files.append(f'{temp_folder}{search_date} - {i}.pdf')
        links.append(download_queue[i])

    driver.quit()

    return downloaded_files, links, temp_folder

#  
#  name: Diário Oficial de Cotegipe (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name, download links
#  
def dom_cotegipe(search_date):
    search_date = dt.strptime(search_date, '%Y-%m-%d')

    url = f'https://www.cotegipe.ba.gov.br/site/diariooficial'

    temp_folder = 'portarias-dom-cotegipe/'

    utils.create_temp_folder(temp_folder)

    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    options.add_argument('window-size=1024x768')
    profile = {
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1024, 768)

    driver.get(url) 

    # preenche os campos de busca com a data desejada
    el_start_date = driver.find_element(By.ID, 'diarioOficial_dataInicial')
    el_end_date = driver.find_element(By.ID, 'diarioOficial_dataFinal')

    el_start_date.send_keys(search_date.strftime('%d%m%Y'))
    el_end_date.send_keys(search_date.strftime('%d%m%Y'))

    xpath = '//input[@type="submit"]'
    bt = driver.find_element(By.XPATH, xpath)

    try:
        bt.click()
    except:
        bt.click()

    try:
        tabela = driver.find_element(By.XPATH, '//table')
        docs = tabela.find_elements(By.TAG_NAME, 'a')
    except:
        log.debug("No publications founded")
        docs = []

    download_queue = [] 

    for doc in docs:
        download_queue.append(doc.get_attribute('href'))
    
    
    downloaded_files = []
    links = []

    for i in range(len(download_queue)):
        utils.download_to_file(download_queue[i], f'{temp_folder}{search_date} - {i}.pdf')
        downloaded_files.append(f'{temp_folder}{search_date} - {i}.pdf')
        links.append(download_queue[i])

    driver.quit()

    return downloaded_files, links, temp_folder

#  
#  name: Diário Oficial de Santana (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name, download links
#  
def dom_santana(search_date):
    search_date = dt.strptime(search_date, '%Y-%m-%d')
    
    url = f'https://www.santana.ba.gov.br/site/diariooficial'

    temp_folder = 'portarias-dom-santana/'
    
    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    options.add_argument('window-size=1024x768')
    profile = {
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1024, 768)

    driver.get(url) 

    # preenche os campos de busca com a data desejada
    el_start_date = driver.find_element(By.ID, 'diarioOficial_dataInicial')
    el_end_date = driver.find_element(By.ID, 'diarioOficial_dataFinal')

    el_start_date.send_keys(search_date.strftime('%d%m%Y'))
    el_end_date.send_keys(search_date.strftime('%d%m%Y'))

    xpath = '//input[@type="submit"]'
    bt = driver.find_element(By.XPATH, xpath)

    try:
        bt.click()
    except:
        bt.click()

    try:
        tabela = driver.find_element(By.XPATH, '//table')
        docs = tabela.find_elements(By.TAG_NAME, 'a')
    except:
        log.debug("No publications founded")
        docs = []    
    
    download_queue = [] 

    for doc in docs:
        download_queue.append(doc.get_attribute('href'))
    
    
    downloaded_files = []
    links = []

    for i in range(len(download_queue)):
        utils.download_to_file(download_queue[i], f'{temp_folder}{search_date} - {i}.pdf')
        downloaded_files.append(f'{temp_folder}{search_date} - {i}.pdf')
        links.append(download_queue[i])
            
    driver.quit()

    return downloaded_files, links, temp_folder

#  
#  name: Diário Oficial de Serra Dourada (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name, download links
#  
def dom_serra_dourada(search_date):
    search_date = dt.strptime(search_date, '%Y-%m-%d')
    
    url = f'https://www.serradourada.ba.gov.br/site/diariooficial'

    temp_folder = 'portarias-dom-serra-dourada/'
    
    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    options.add_argument('window-size=1024x768')
    profile = {
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1024, 768)

    driver.get(url) 

    # preenche os campos de busca com a data desejada
    el_start_date = driver.find_element(By.ID, 'diarioOficial_dataInicial')
    el_end_date = driver.find_element(By.ID, 'diarioOficial_dataFinal')

    el_start_date.send_keys(search_date.strftime('%d%m%Y'))
    el_end_date.send_keys(search_date.strftime('%d%m%Y'))

    xpath = '//input[@type="submit"]'
    bt = driver.find_element(By.XPATH, xpath)

    try:
        bt.click()
    except:
        bt.click()

    try:
        tabela = driver.find_element(By.XPATH, '//table')
        docs = tabela.find_elements(By.TAG_NAME, 'a')
    except:
        log.debug("No publications founded")
        docs = []    
    
    download_queue = [] 

    for doc in docs:
        download_queue.append(doc.get_attribute('href'))
    
    
    downloaded_files = []
    links = []

    for i in range(len(download_queue)):
        utils.download_to_file(download_queue[i], f'{temp_folder}{search_date} - {i}.pdf')
        downloaded_files.append(f'{temp_folder}{search_date} - {i}.pdf')
        links.append(download_queue[i])
            
    driver.quit()

    return downloaded_files, links, temp_folder

#  
#  name: Diário Oficial de Canápolis (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name, download links
#  
def dom_canapolis(search_date):
    # search_date = '2022-04-23'
    url = 'http://diariooficial.canapolis.ba.gov.br/'

    temp_folder = 'canapolis-download/'
    utils.create_temp_folder(temp_folder)
    search_date = dt.strptime(search_date, '%Y-%m-%d')
    
    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    profile = {#"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)

    print("Acessing Canápolis DOM")
    driver.get(url)
    
    iframe = driver.find_element(By.XPATH, '/html/body/iframe')
    driver.switch_to.frame(iframe)
    
    print('Searching date')
    input_date = driver.find_element(By.XPATH, '//*[@id="dataEdicaoPortal"]')
    input_date.clear()
    input_date.send_keys(search_date.strftime('%d/%m/%Y'))
    
    bt_search = driver.find_element(By.XPATH, '//*[@id="sbmt1"]')
    bt_search.click()
    
    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present(),
                                    'Timed out waiting for PA creation ' +
                                    'confirmation popup to appear.')

        alert = driver.switch_to.alert
        alert.accept()
        print(f'No publications found for {search_date.strftime("%d/%m/%Y")}. Try another date.')
        valid_date = False
    except:
        valid_date = True


    if valid_date:
        bt_download = driver.find_elements(By.XPATH, '//*[@id="downloadPdf"]')
        links = []
        for bt in bt_download: 
            url_pdf = bt.get_attribute("href")
            links.append(url_pdf)
            driver.get(url_pdf)
    
        bt_download = driver.find_element(By.XPATH, '//*[@id="baixar-diario-completo"]')
        bt_download.click()
    
        print(f'Waiting download {len(links)} file(s)')
        downloaded_files = glob.glob(f'{temp_folder}*.pdf')
        inicio = dt.now()
        timeout = dt.now()- inicio

        while timeout.seconds < 30 and len(downloaded_files) < 1:
            downloaded_files = glob.glob(f'{temp_folder}*.pdf')
            timeout = dt.now()- inicio

            for f in downloaded_files:
                if f.find('crdownload') > -1:
                    print(downloaded_files)
                    downloaded_files = []

    else:
        downloaded_files = []
        links = []


    driver.quit()

    return downloaded_files, links, temp_folder

#  
#  name: Diário Oficial de Cristópolis (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name, download links
#  
def dom_cristopolis(search_date):
    # search_date = '2022-04-20'
    search_date = dt.strptime(search_date, '%Y-%m-%d')
    url = 'https://www.cristopolis.ba.gov.br/#diario-oficial'

    temp_folder = 'cristopolis-download/'
    utils.create_temp_folder(temp_folder)
    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    profile = {#"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)

    print("Acessing Cristópolis DOM")
    driver.get(url)
    # Ocultar janela de mensagem
    try:
        driver.find_element(By.XPATH, '//*[@id="sgpb-popup-dialog-main-div-wrapper"]/div/img').click()
    except: pass
    # seleciona o ano
    xpath_select = f'//*[@id="_f_ano"]'

    select = Select(driver.find_element(By.XPATH, xpath_select))
    select.select_by_visible_text(str(search_date.year))

    driver.find_element(By.XPATH, '//*[@id="doem-container"]/div/form/div[2]/div[2]/div/button').click()

    # encontra as datas
    xpath = '//div[@class="panel panel-default"]'
    month_dates = driver.find_elements(By.XPATH, xpath)[-search_date.month].find_elements(By.TAG_NAME, 'tr')
    # month_dates
    # separa os possíveis links para a data escolhida
    link = []
    for i in range(len(month_dates)):
        if month_dates[i].get_attribute("outerHTML").find(search_date.strftime('%d/%m/%Y')) > -1:
            aux= re.findall(r'href=\"(.*?)\"', month_dates[i+1].get_attribute('outerHTML'))
            for i2 in range(len(aux)):
                link.append(aux[i2])
            
    # encontra os links das publicações da data escolhida
    download_queue = []
    for i in range(len(link)):
        if (link[i].find('javascript') > -1):
            try:
                download_queue.append(link[i+1])
            except:
                pass
    
    # baixa os downloaded_files
    for pdf_link in download_queue:
        driver.get(pdf_link)
        time.sleep(2)

    print(f'Waiting download {len(download_queue)} file(s)')
    downloaded_files = glob.glob(f'{temp_folder}*.pdf')
    inicio = dt.now()
    timeout = dt.now()- inicio

    while timeout.seconds < 30 and len(downloaded_files) < len(download_queue):
        downloaded_files = glob.glob(f'{temp_folder}*.pdf')
        timeout = dt.now()- inicio

        for f in downloaded_files:
            if f.find('crdownload') > -1:
                print(downloaded_files)
                downloaded_files = []



    driver.quit()

    return downloaded_files, download_queue, temp_folder

#  
#  name: Diário Oficial de Tabocas do Brejo Velho (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name, download links
#  
def dom_tabocas(s_date):
    print('Acessing Tabocas do Brejo Velho diary')
    url = f'http://doem.org.br/ba/tabocasdobrejovelho?dt={s_date}'

    temp_folder = 'portarias-dom-tabocas/'
    utils.create_temp_folder(temp_folder)

    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    options.add_argument('window-size=1024x768')
    profile = {#"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    driver.find_element(By.XPATH, '//*[@class="btn btn-primary btn-lg btn-accept-all-privacy-and-terms"]').click()

    download_links = []

    len_queue = 0

    try:
        # para caso de uma publicação no dia (mostrada diretamente na página)
        # entra no iframe para conseguir localizar o link (caso data tenha uma única publicação)
        xpath = '//*[@id="pdf-iframe"]'
        iframe = driver.find_element(By.XPATH, xpath)
        driver.switch_to.frame(iframe)

        # localiza link dentro da janela de visualização
        xpath = '//*[@id="pdfjs-object"]'
        link = driver.find_element(By.XPATH, xpath).get_attribute('data')
        download_links.append(link)
        driver.get(link)
        
        # marca quantas publicações foram encontradas
        len_queue = 1
        print(f'{len_queue} publication found')

        # acessa pdf e faz o download através do botão
        xpath = '//*[@id="download"]'
        download_button = driver.find_element(By.XPATH, xpath)
        ActionChains(driver).move_to_element(download_button).click().perform()
        
    except:
        # localiza os botões que levam ao PDF's
        xpath = '//*[@class="btn btn-xs btn-default pull-right"]'
        view_buttons = driver.find_elements(By.XPATH, xpath)
            
        # marca quantas publicações foram encontradas
        len_queue = len(view_buttons)
        print(f'{len_queue} publications found')

        for view_bt in view_buttons:
            # acessa pdf publicado através do botão
            ActionChains(driver).move_to_element(view_bt).click().perform()
            driver.switch_to.window(driver.window_handles[1])

            # localiza link dentro da janela de visualização
            xpath = '//*[@id="pdfjs-object"]'
            link = driver.find_element(By.XPATH, xpath).get_attribute('data')
            download_links.append(link)
        
            # acessa pdf e faz o download através do botão
            driver.get(link)
            xpath = '//*[@id="download"]'
            download_button = driver.find_element(By.XPATH, xpath)
            ActionChains(driver).move_to_element(download_button).click().perform()

            # fecha a janela 
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
    
    if len_queue > 0:    
        print("Waiting download file(s)")

    # espera que todos os arquivos sejam baixados. Segue o fluxo caso estoure o timeout de 30 segundos
    print(f'Waiting download {len_queue} file(s)')
    downloaded_files = glob.glob(f'{temp_folder}*.pdf')
    inicio = dt.now()
    timeout = dt.now()- inicio

    while timeout.seconds < 30 and len(downloaded_files) < len_queue:
        downloaded_files = sorted(glob.glob(f'{temp_folder}*.pdf'), key = os.path.getmtime)
        timeout = dt.now()- inicio

        for f in downloaded_files:
            if f.find('crdownload') > -1:
                print(downloaded_files)
                downloaded_files = []
                
    driver.quit()

    return downloaded_files, download_links, temp_folder

#  
#  name: Diário Oficial de Catolândia (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name, download links
#  
def dom_catolandia(s_date):
    print('Acessing Catolândia diary')
    url = f'http://doem.org.br/ba/catolandia?dt={s_date}'

    temp_folder = 'portarias-dom-catolandia/'
    utils.create_temp_folder(temp_folder)

    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    options.add_argument('window-size=1024x768')
    profile = {#"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    driver.find_element(By.XPATH, '//*[@class="btn btn-primary btn-lg btn-accept-all-privacy-and-terms"]').click()

    download_links = []

    len_queue = 0

    try:
        # para caso de uma publicação no dia (mostrada diretamente na página)
        # entra no iframe para conseguir localizar o link (caso data tenha uma única publicação)
        xpath = '//*[@id="pdf-iframe"]'
        iframe = driver.find_element(By.XPATH, xpath)
        driver.switch_to.frame(iframe)

        # localiza link dentro da janela de visualização
        xpath = '//*[@id="pdfjs-object"]'
        link = driver.find_element(By.XPATH, xpath).get_attribute('data')
        download_links.append(link)
        driver.get(link)
        
        # marca quantas publicações foram encontradas
        len_queue = 1
        print(f'{len_queue} publication found')

        # acessa pdf e faz o download através do botão
        xpath = '//*[@id="download"]'
        download_button = driver.find_element(By.XPATH, xpath)
        ActionChains(driver).move_to_element(download_button).click().perform()
        
    except:
        # localiza os botões que levam ao PDF's
        xpath = '//*[@class="btn btn-xs btn-default pull-right"]'
        view_buttons = driver.find_elements(By.XPATH, xpath)
            
        # marca quantas publicações foram encontradas
        len_queue = len(view_buttons)
        print(f'{len_queue} publications found')

        for view_bt in view_buttons:
            # acessa pdf publicado através do botão
            ActionChains(driver).move_to_element(view_bt).click().perform()
            driver.switch_to.window(driver.window_handles[1])

            # localiza link dentro da janela de visualização
            xpath = '//*[@id="pdfjs-object"]'
            link = driver.find_element(By.XPATH, xpath).get_attribute('data')
            download_links.append(link)
        
            # acessa pdf e faz o download através do botão
            driver.get(link)
            xpath = '//*[@id="download"]'
            download_button = driver.find_element(By.XPATH, xpath)
            ActionChains(driver).move_to_element(download_button).click().perform()

            # fecha a janela 
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
    
    if len_queue > 0:    
        print("Waiting download file(s)")

    # espera que todos os arquivos sejam baixados. Segue o fluxo caso estoure o timeout de 30 segundos
    print(f'Waiting download {len_queue} file(s)')
    downloaded_files = glob.glob(f'{temp_folder}*.pdf')
    inicio = dt.now()
    timeout = dt.now()- inicio

    while timeout.seconds < 30 and len(downloaded_files) < len_queue:
        downloaded_files = sorted(glob.glob(f'{temp_folder}*.pdf'), key = os.path.getmtime)
        timeout = dt.now()- inicio

        for f in downloaded_files:
            if f.find('crdownload') > -1:
                print(downloaded_files)
                downloaded_files = []
                
    driver.quit()

    return downloaded_files, download_links, temp_folder

#  
#  name: Diário Oficial de São Felix do Coribe (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name, download links
#  
def dom_sfcoribe(search_date):
    url = 'http://saofelixdocoribe.ba.gov.br/diario_oficial'

    temp_folder = 'sfcoribe-download/'
    utils.create_temp_folder(temp_folder)

    search_date = dt.strptime(search_date, '%Y-%m-%d')

    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    profile = {#"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)

    print("Acessing São Felix do Coribe DOM")
    driver.get(url)

    print('Searching date')
    select = Select(driver.find_element(By.XPATH, '//*[@id="diarios_publicados"]'))
    select.select_by_visible_text(f'{utils.month_name[search_date.month]} - {search_date.year}')

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//td[@class="bg-info"]')))
    bt_download = driver.find_elements(By.XPATH, '//td[@class="bg-info"]')
    
    links = []
    for bt in bt_download: 
        html_element = bt.get_attribute("outerHTML")
        valid_dates = re.findall(r'\d*', html_element)
        
        for valid_date_bt in valid_dates:
            if valid_date_bt == str(search_date.day):
                url_pdf = re.findall(r'href="(.*?)"', html_element)[0]
                links.append(url_pdf)
                driver.get(url_pdf)
        
    # espera que todos os arquivos sejam baixados. Segue o fluxo caso estoure o timeout de 30 segundos
    len_queue = len(links)
    print(f'Waiting download {len_queue} file(s)')
    downloaded_files = glob.glob(f'{temp_folder}*.pdf')
    inicio = dt.now()
    timeout = dt.now()- inicio

    while timeout.seconds < 30 and len(downloaded_files) < len_queue:
        downloaded_files = sorted(glob.glob(f'{temp_folder}*.pdf'), key = os.path.getmtime)
        timeout = dt.now()- inicio

        for f in downloaded_files:
            if f.find('crdownload') > -1:
                print(downloaded_files)
                downloaded_files = []
                
    driver.quit()

    return downloaded_files, links, temp_folder

#  
#  name: Diário Oficial de Bom Jesus da Lapa (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name, download links
#  
def dom_bjlapa(search_date):
    url = 'http://www.bomjesusdalapa.ba.gov.br/diario_oficial'

    temp_folder = 'bjlapa-download/'
    utils.create_temp_folder(temp_folder)

    search_date = dt.strptime(search_date, '%Y-%m-%d')

    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    profile = {#"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)

    print("Acessing Bom Jesus da Lapa DOM")
    driver.get(url)

    print('Searching date')
    select = Select(driver.find_element(By.XPATH, '//*[@id="diarios_publicados"]'))
    select.select_by_visible_text(f'{utils.month_name[search_date.month]} - {search_date.year}')

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//td[@class="bg-info"]')))
    bt_download = driver.find_elements(By.XPATH, '//td[@class="bg-info"]')
    
    links = []
    for bt in bt_download: 
        html_element = bt.get_attribute("outerHTML")
        valid_dates = re.findall(r'\d*', html_element)
        
        for valid_date_bt in valid_dates:
            if valid_date_bt == str(search_date.day):
                url_pdf = re.findall(r'href="(.*?)"', html_element)[0]
                links.append(url_pdf)
                driver.get(url_pdf)
        
    # espera que todos os arquivos sejam baixados. Segue o fluxo caso estoure o timeout de 30 segundos
    len_queue = len(links)
    print(f'Waiting download {len_queue} file(s)')
    downloaded_files = glob.glob(f'{temp_folder}*.pdf')
    inicio = dt.now()
    timeout = dt.now()- inicio

    while timeout.seconds < 30 and len(downloaded_files) < len_queue:
        downloaded_files = sorted(glob.glob(f'{temp_folder}*.pdf'), key = os.path.getmtime)
        timeout = dt.now()- inicio

        for f in downloaded_files:
            if f.find('crdownload') > -1:
                print(downloaded_files)
                downloaded_files = []
                
    driver.quit()

    return downloaded_files, links, temp_folder

#  
#  name: Diário Oficial de Buritirama (DOM)
#  @ param: search date yyyy-mm-dd
#  @ return: PDF filenames, download temp folder name, download links
#  
def dom_buritima(search_date):
    url = 'http://www.buritirama.ba.gov.br/diario_oficial'

    temp_folder = 'buritima-download/'
    utils.create_temp_folder(temp_folder)

    search_date = dt.strptime(search_date, '%Y-%m-%d')

    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    profile = {#"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
            "download.default_directory" : f"{os.getcwd()}/{temp_folder}" , 
            "download.extensions_to_open": "applications/pdf",
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options)

    print("Acessing Buritima DOM")
    driver.get(url)

    print('Searching date')
    select = Select(driver.find_element(By.XPATH, '//*[@id="diarios_publicados"]'))
    select.select_by_visible_text(f'{utils.month_name[search_date.month]} - {search_date.year}')

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//td[@class="bg-info"]')))
    bt_download = driver.find_elements(By.XPATH, '//td[@class="bg-info"]')
    
    links = []
    for bt in bt_download: 
        html_element = bt.get_attribute("outerHTML")
        valid_dates = re.findall(r'\d*', html_element)
        
        for valid_date_bt in valid_dates:
            if valid_date_bt == str(search_date.day):
                url_pdf = re.findall(r'href="(.*?)"', html_element)[0]
                links.append(url_pdf)
                driver.get(url_pdf)
        
    # espera que todos os arquivos sejam baixados. Segue o fluxo caso estoure o timeout de 30 segundos
    len_queue = len(links)
    print(f'Waiting download {len_queue} file(s)')
    downloaded_files = glob.glob(f'{temp_folder}*.pdf')
    inicio = dt.now()
    timeout = dt.now()- inicio

    while timeout.seconds < 30 and len(downloaded_files) < len_queue:
        downloaded_files = sorted(glob.glob(f'{temp_folder}*.pdf'), key = os.path.getmtime)
        timeout = dt.now()- inicio

        for f in downloaded_files:
            if f.find('crdownload') > -1:
                print(downloaded_files)
                downloaded_files = []
                
    driver.quit()

    return downloaded_files, links, temp_folder
  

  
