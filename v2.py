import sys
import time
import traceback
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
import os
import coloredlogs, logging
from argparse import ArgumentParser
import re
import json
import random
import pyautogui



class Linkedin_Bot():
    logger = logging.getLogger(__name__)
    coloredlogs.install(level='INFO')


    def __init__(self):
        self.login_url = 'https://www.linkedin.com/login'
        self.logged_In = False
        self.message = 'Hello'
        self.page_no = 1
        self.connects_limit = 20
        self.count = 1


    def init_driver(self):
        self.driver = uc.Chrome()
        self.action = ActionChains(self.driver)


    def load_creds(self):
        if os.path.exists('./creds.json'):
            with open('creds.json', 'r') as f:
                self.creds  = json.load(f)
                return self.creds.values()
        else:
            self.logger.info(f" [+] Credentials missing!")
            sys.exit()

    
    def im_not_robot(self, delay={'min':2, 'max':5}):
        x, y = pyautogui.size()
        x = random.randint(0, x)
        y = random.randint(0, y)
        pyautogui.moveTo(x, y, duration=0.5)
        time.sleep(random.choice(range(delay['min'], delay['max'])))


    def wait_for_element(self, path, timeout=10, retry=False):
        try:
            WebDriverWait(self.driver,timeout=timeout).until(EC.visibility_of_element_located((By.XPATH,path)))
        except TimeoutException:
            if retry:
                return self.wait_for_element(path, timeout, retry=False)
            else:
                return None
        else:
            return True


    def connect(self, name, message=None):
        try:
            if message:
                self.driver.find_element(By.XPATH,"//button[@aria-label='Add a note']").click()
                self.im_not_robot()
                self.driver.find_element(By.XPATH,"//textarea[@id='custom-message']").send_keys(message)
            self.driver.find_element(By.XPATH,"//button[@aria-label='Send now']").click()
            self.logger.info(f" [+] Request sent to {name}!")
        except TimeoutError:
            traceback.print_exc()
            self.logger.info(f" [+] Skipping {name}!")


    def search(self, query):
        self.logger.info(f" [+] Page {self.page_no}")
        url = f'https://www.linkedin.com/search/results/people/?keywords={query}&origin=GLOBAL_SEARCH_HEADER'
        self.logger.info(f" [+] Searching for {query}")
        self.driver.get(url)
        self.wait_for_element("//div[@class='entity-result']")
        self.driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
        self.im_not_robot(delay={'min':3, 'max':5})
        profiles = self.driver.find_elements(By.XPATH, "//button[contains(@aria-label,'Invite')]")
        for profile in profiles:
            raw_name = profile.get_attribute("aria-label")
            name = re.match(r"(?:Invite)(.*?)to",raw_name).group(1).strip()
            print(name)
            self.im_not_robot()
            self.action.move_to_element(profile).click().perform()
            self.connect(name)
            self.im_not_robot(delay={"min":3, "max":5})
            if self.count == self.connects_limit:
                return None
            else:
                self.count +=1
        if self.wait_for_element("//button[@aria-label='Next']"):
            self.im_not_robot()
            self.page_no +=1
            self.search(url + f"&page={self.page_no}")

    
    def is_captcha(self):
        return self.wait_for_element("//h1[contains(text(),'quick security check')]")

    
    def login(self, username, password):   
        try:
            self.driver.get(self.login_url)
            self.driver.find_element(By.XPATH,"//input[@id='username']").send_keys(username)
            self.driver.find_element(By.XPATH,"//input[@id='password']").send_keys(password)
            self.im_not_robot()
            self.driver.find_element(By.XPATH,"//button[@aria-label='Sign in']").click()
            if self.is_captcha():
                self.logger.info(" [+] Press enter after solving captcha")
                input("Waiting:")
            if self.wait_for_element("//div[contains(@class, 'feed-identity-module__actor')]", timeout=30) == None:
                raise Exception()
        except Exception as e:
            traceback.print_exc()
            self.logger.info(" [+] Login Failed")
        else:
            self.logger.info(" [+] Login Successful")
            self.logged_In = True

    
    def take_inputs(self):
        parser = ArgumentParser()
        parser.add_argument('-q', '--query', dest='query', required=True, default='')
        values = parser.parse_args()
        args_dict = vars(values)
        query = args_dict.get('query')
        if query:
            return query
        else:
            self.logger.info(" [+] Invalid query")
            sys.exit()

    
    def main(self):
        username, password = self.load_creds()
        query = self.take_inputs()
        self.init_driver()
        self.login(username, password)
        if self.logged_In:
            self.search(query)
        self.driver.close()


bot = Linkedin_Bot()
bot.main()