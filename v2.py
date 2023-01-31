import sys
import time
import traceback
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException,NoSuchElementException
import os
import coloredlogs, logging
from argparse import ArgumentParser
import re
import json
import random
import pyautogui
import pickle



class LoginRequired(Exception):
    pass


class Linkedin_Bot():
    logger = logging.getLogger(__name__)
    coloredlogs.install(level='INFO')


    def __init__(self):
        self.login_url = 'https://www.linkedin.com/login'
        self.logged_In = False
        self.page_no = 1
        self.count = 1


    def init_driver(self):
        self.driver = uc.Chrome()
        self.driver.maximize_window()
        self.driver.get("https://www.linkedin.com/")
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
        pyautogui.moveTo(x, y, duration=random.uniform(0.4, 0.7))
        time.sleep(random.choice(range(delay['min'], delay['max'])))


    def wait_for_element(self, path, timeout=10, retry=False):
        try:
            WebDriverWait(self.driver,timeout=timeout).until(EC.visibility_of_element_located((By.XPATH,path)))
        except (TimeoutException, NoSuchElementException):
            if retry:
                return self.wait_for_element(path, timeout, retry=False)
            else:
                return None
        else:
            return True


    def connect(self, name):
        """ connect to a person """
        try:
            if self.message:
                self.driver.find_element(By.XPATH,"//button[@aria-label='Add a note']").click()
                self.im_not_robot()
                self.driver.find_element(By.XPATH,"//textarea[@id='custom-message']").send_keys(self.message)
                self.im_not_robot()
            self.driver.find_element(By.XPATH,"//button[@aria-label='Send now']").click()
            self.logger.info(f" [+] Request sent to {name}!")
        except TimeoutError:
            traceback.print_exc()
            self.logger.info(f" [+] Skipping {name}!")


    def search(self, query):
        """ perform search and connect() to results """
        self.logger.info(f" [+] Page {self.page_no}")
        url = f'https://www.linkedin.com/search/results/people/?keywords={query}&origin=GLOBAL_SEARCH_HEADER'
        self.driver.get(url)
        if self.cookie_expired():
            raise LoginRequired()
        else:
            self.wait_for_element("//div[@class='entity-result']", timeout=5)
            self.driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
            self.im_not_robot(delay={'min':3, 'max':5})
            for profile in self.driver.find_elements(By.XPATH, "//button[contains(@aria-label,'Invite')]"):
                name = re.match(r"(?:Invite)(.*?)to", profile.get_attribute("aria-label")).group(1).strip()
                self.action.move_to_element(profile).click().perform()
                self.connect(name)
                self.im_not_robot(delay={"min":3, "max":5})
                if self.count == self.connects_limit:
                    return None
                else:
                    self.count +=1
            if self.wait_for_element("//button[@aria-label='Next']"):
                self.page_no +=1
                self.search(url + f"&page={self.page_no}")

    
    def check_captcha(self):
        if self.wait_for_element("//h1[contains(text(),'quick security check')]", timeout=5):
            self.logger.info(" [+] Press enter after solving captcha")
            input("Waiting:")


    def save_cookies(self):
        cookies = self.driver.get_cookies()
        with open("cookies.pkl", 'wb') as f:
            pickle.dump(cookies, f)
            self.logger.info(" [+] Cookies Saved!")


    def cookie_expired(self):
        if self.wait_for_element("//button[@aria-label='Sign in']", timeout=5):
            return True
        else:
            return False


    def load_cookies(self):
        if os.path.exists("./cookies.pkl"):
            with open("cookies.pkl", 'rb') as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                self.logger.info(" [+] Cookies loaded!")
                return True
        else:
            return False


    def login(self, username, password):   
        try:
            self.driver.get(self.login_url)
            self.driver.find_element(By.XPATH,"//input[@id='username']").send_keys(username)
            self.driver.find_element(By.XPATH,"//input[@id='password']").send_keys(password)
            self.im_not_robot()
            self.driver.find_element(By.XPATH,"//button[@aria-label='Sign in']").click()
            self.check_captcha()
            if self.wait_for_element("//div[contains(@class, 'feed-identity-module__actor')]", timeout=30) == None:
                raise Exception()
        except Exception as e:
            traceback.print_exc()
            self.logger.info(" [+] Login Failed")
        else:
            self.logger.info(" [+] Login Successful")
            self.logged_In = True
            self.save_cookies()

    
    def take_args(self):
        parser = ArgumentParser()
        parser.add_argument('-q', '--query', dest='query', required=True, default='')
        parser.add_argument('-c', '--connect', dest='connects_limit', default=10, type=int)
        parser.add_argument('-m', '--message', dest='message', default='', help="e.g -m 'hello there!'")
        values = parser.parse_args()
        args_dict = vars(values)
        query = args_dict.get('query')
        self.connects_limit = args_dict.get('connects_limit')
        self.message = args_dict.get('message')
        if query:
            return query
        else:
            self.logger.info(" [+] Invalid query")
            sys.exit()

    
    def main(self):
        username, password = self.load_creds()
        query = self.take_args()
        self.init_driver()
        if self.load_cookies():
            try:
                self.search(query)
            except LoginRequired:
                self.login(username, password)
                if self.logged_In:
                    self.search(query)
        else:
            self.login(username, password)
            if self.logged_In:
                self.search(query)
        self.driver.close()


bot = Linkedin_Bot()
bot.main()


