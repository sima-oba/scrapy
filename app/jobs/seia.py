import logging
from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep


from .. import publisher


log = logging.getLogger(__name__)


def _logoff(driver):
    try:
        driver.find_element(
            By.XPATH,
            '//*[@id="j_idt33"]/table/tbody/tr/td[7]/a'
        ).click()
        
    except Exception as e:
        pass

    driver.close()

def _logon(driver, user_name, password):
    url = 'http://sistema.seia.ba.gov.br/'
    log.debug(f'Acessing {url}')

    driver.get(url)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located(
        (By.CLASS_NAME, "ui-panel")
    ))

    actions = ActionChains(driver)
    element = driver.find_elements(
        By.XPATH,
        "//*[@id='_dialogAlertaIndex']/div[1]/a"
    )[0]
    actions.move_to_element(element)
    actions.click()
    actions.perform()

    log.debug('Logging')
    login_textbox = driver.find_element(
        By.ID,       
        'j_username'
    )
    
    pw_textbox = driver.find_element(
        By.ID,
        'j_password'
    )
    
    ent_button = driver.find_element(
        By.ID,
        'btnEntrar'
    )

    login_textbox.send_keys(user_name)
    pw_textbox.send_keys(password)
    ent_button.click()

def get_producers(api_url, username, password):
    credentials = {
        "username": username,
        "password": password
    }
    
    access_token = requests.post(
        'http://34.83.97.43/api/v1/auth/session/login', 
        json=credentials        
    ).json()
    
    token = access_token["access_token"]

    producers = requests.get(
        api_url,
        headers={
            "Content-Type":"text",
            "Authorization": f"Bearer {token}"
        }
    ).json()
    
    return producers

def _import(seia_username, seia_password, sima_username, sima_password):
    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('window-size=1024x768')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    driver = webdriver.Chrome(options=options)

    _logon(driver, seia_username, seia_password)

    log.debug('Opening public access page')
    try:
        driver.find_element(
            By.XPATH,
            "//*[@id='frmMenu']/div[16]"
        ).click()
    except:
        driver.close()
        raise Exception("Could not login. Check credentials or if the user is being used.")

    log.debug("Loading database users data")
    
    users = get_producers("http://34.83.97.43/api/v1/producer/owners", sima_username, sima_password)
    
    labels = [
        'proccess_number',
        'requirement_number',
        'opening_date',
        'formation_date',
        'ordinance_type',
        'status',
        'owner',
        'owner_doc_number',
        'interprise_name',
        'city'
    ]

    user_proccess = []

    for user in users:
        log.debug(f'Searching for {user["doc"]} {users.index(user) + 1}/{len(users)}')
        # Fills user CPF form
        cpf_textbox = driver.find_element(
            By.XPATH,
            "//*[@id='conteudo:numDocumento']"
        )
        cpf_textbox.send_keys(user["doc"])

        # Start searching
        driver.find_element(
            By.XPATH,
            '//*[@id="conteudo:j_idt7693"]'
        ).click()

        is_mult_page = True
        current_page = 0

        while is_mult_page:
            start = datetime.now()
            timeout = datetime.now() - start

            # Wait query result
            # 30 seconds timeout
            while (
                    timeout.seconds < 120 and
                    driver.find_element(
                        By.XPATH, '//*[@id="statusDialog"]'
                    ).get_attribute('outerHTML').find('display: block') > 0
            ):
                sleep(3)
                timeout = datetime.now() - start

            if len(driver.find_elements(By.CLASS_NAME, 'ui-growl-item')) > 0:
                # no data user
                log.debug(f'Cannot found any data to { user["name"] }')

            elif timeout.seconds < 120:
                for i in range(
                    1,
                    len(driver.find_elements(By.TAG_NAME, "tr")) - 105
                ):
                    log.debug(f'Open proccess details page')
                    
                    try:
                        element = driver.find_element(
                            By.XPATH,
                            f'//*[@id="conteudo:dataTableProcesso:{i+current_page*10}:j_idt7714"]'
                        )
                        ActionChains(driver).move_to_element(element).click().perform()

                        start = datetime.now()
                        timeout = datetime.now() - start
                        while driver.find_element(
                            By.ID,
                            "_dialogdetalharProcesso"
                        ).get_attribute('outerHTML').find('display: block') < 0 and timeout.seconds < 30:
                            timeout = datetime.now() - start

                        try:
                            proccess_number = driver.find_element(
                                By.XPATH,
                                f'//*[@id="formDetalharProcesso:tabviewprocesso:j_idt6841"]/table[3]/tbody/tr[2]/td[1]'
                            ).get_attribute('innerHTML')
                            
                            requirement_number = driver.find_element(
                                By.XPATH,
                                f'//*[@id="formDetalharProcesso:tabviewprocesso:j_idt6841"]/table[6]/tbody/tr[2]/td[1]/a'
                            ).get_attribute('innerHTML')
                            
                            opening_date = datetime.strptime(
                                driver.find_element(
                                    By.XPATH,
                                    f'//*[@id="formDetalharProcesso:tabviewprocesso:j_idt6841"]/table[6]/tbody/tr[2]/td[3]'
                                ).get_attribute('innerHTML'),        
                                '%d/%m/%Y'
                            ).strftime('%Y-%m-%d')
                            
                            formation_date = datetime.strptime(
                                driver.find_element(
                                    By.XPATH,
                                    f'//*[@id="formDetalharProcesso:tabviewprocesso:j_idt6841"]/table[3]/tbody/tr[2]/td[3]'
                                ).get_attribute('innerHTML'),        
                                '%d/%m/%Y'
                            ).strftime('%Y-%m-%d')
                            
                            ordinance_type = driver.find_element(
                                By.XPATH,
                                f'//*[@id="formDetalharProcesso:tabviewprocesso:tabelaAtos_r_0"]/td[1]/div'
                            ).get_attribute('innerHTML')
                            
                            status = driver.find_element(
                                By.XPATH,
                                f'//*[@id="formDetalharProcesso:tabviewprocesso:j_idt6841"]/table[3]/tbody/tr[2]/td[7]'
                            ).get_attribute('innerHTML')
                            
                            owner = driver.find_element(
                                By.XPATH,
                                f'//*[@id="formDetalharProcesso:tabviewprocesso:j_idt6841"]/table[4]/tbody/tr[2]/td[1]'
                            ).get_attribute('innerHTML')
                            
                            owner_doc_number = driver.find_element(
                                By.XPATH,
                                f'//*[@id="formDetalharProcesso:tabviewprocesso:j_idt6841"]/table[4]/tbody/tr[2]/td[3]'
                            ).get_attribute('innerHTML')
                            
                            enterprise_name = driver.find_element(
                                By.XPATH,
                                f'//*[@id="formDetalharProcesso:tabviewprocesso:j_idt6841"]/table[4]/tbody/tr[4]/td[1]'
                            ).get_attribute('innerHTML')
                            
                            city = driver.find_element(
                                By.XPATH,
                                f'//*[@id="formDetalharProcesso:tabviewprocesso:j_idt6841"]/table[4]/tbody/tr[4]/td[3]'
                            ).get_attribute('innerHTML')
                        except Exception as e:
                            log.error(e)

                        reg = {
                            labels[0]: proccess_number,
                            labels[1]: requirement_number,
                            labels[2]: opening_date,
                            labels[3]: formation_date,
                            labels[4]: ordinance_type,
                            labels[5]: status,
                            labels[6]: owner,
                            labels[7]: owner_doc_number,
                            labels[8]: enterprise_name,
                            labels[9]: city
                        }
                        user_proccess.append(reg)

                        while ( driver.find_element(
                                    By.XPATH, '//*[@id="statusDialog"]'
                                ).get_attribute('outerHTML').find('display: block') > 0):
                            sleep(3)

                        log.debug('Close proccess modal')
                        driver.find_element(
                            By.XPATH,
                            '//*[@id="_dialogdetalharProcesso"]/div[1]/a'
                        ).click()
                    except: pass

            else:
                # timeout exception
                raise TimeoutException("SEIA not responding to public query")

            try:
                xpath_next_page = '//a[@class="ui-paginator-next ui-state-default ui-corner-all"]'
                bt_next_page = driver.find_element(By.XPATH, xpath_next_page)
                ActionChains(driver).move_to_element(bt_next_page).click().perform()
                current_page += 1
                log.debug('Next page')
            except:
                is_mult_page = False

        log.debug('Clean last query')
        driver.find_element(
            By.XPATH,
            '//*[@id="conteudo:j_idt7694"]'
        ).click()

        start = datetime.now()
        timeout = datetime.now() - start

        while len(driver.find_elements(By.CLASS_NAME, f'ui-growl-item')) > 0 and timeout.seconds < 30 or len(driver.find_elements(By.TAG_NAME, "th")) > 8:
            timeout = datetime.now() - start
        # log.debug()

        _logoff(driver)

    return user_proccess


def seia(username: str, password: str, sima_username: str, sima_password: str):
    users_proccess = _import(username, password, sima_username, sima_password)
        
    success = 0

    for reg in users_proccess:
        try:
            publisher.publish(reg, 'SEIA')
            success = + 1
        except Exception as e:
            log.error(e)

    log.debug(f'{success}/{len(users_proccess)} stored')
