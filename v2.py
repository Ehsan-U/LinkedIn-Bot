import sys
import time
import traceback
from seleniumwire import undetected_chromedriver as wire_uc
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
from parsel import Selector
import pickle
from sqlalchemy import create_engine, Column, Integer, String, select, inspect, MetaData, Table
from sqlalchemy.orm import sessionmaker,declarative_base
from hashlib import sha256
Base = declarative_base()


###### DB section ######
class Person(Base):
    __tablename__ = 'connections'
    person_id = Column(String, primary_key=True)
    url = Column(String)
    name = Column(String)
    location = Column(String)
    profile_headline = Column(String)

    def __init__(self, person_id, url, name, location, profile_headline):
        self.person_id = person_id
        self.url = url
        self.name = name
        self.location = location
        self.profile_headline = profile_headline



class LoginRequired(Exception):
    pass



class Linkedin_Bot():
    logger = logging.getLogger(__name__)
    coloredlogs.install(level='INFO')


    def __init__(self):
        self.login_url = 'https://www.linkedin.com/login'
        self.logged_In = False
        self.page_no = 1
        self.connect_count = 1


    def init_driver(self):
        if self.use_proxy:
            self.logger.info(" [+] Using proxies")
            if self.proxy_user:
                options = {
                    "proxy": {
                        "http": f"http://{self.proxy_user}:{self.proxy_pass}@{self.proxy_server}:{self.proxy_port}",
                        "https": f"http://{self.proxy_user}:{self.proxy_pass}@{self.proxy_server}:{self.proxy_port}"
                    },
                }
            else:
                options = {
                    "proxy": {
                        "http": f"http://{self.proxy_server}:{self.proxy_port}",
                        "https": f"http://{self.proxy_server}:{self.proxy_port}"
                    },
                }
            self.driver = wire_uc.Chrome(seleniumwire_options=options)
        else:
            self.driver = uc.Chrome()
        self.driver.maximize_window()
        self.driver.get("https://www.linkedin.com/")
        self.action = ActionChains(self.driver)


    def init_db(self):
        try:
            engine = create_engine(self.server_uri)
            table_exist = True if 'connections' in inspect(engine).get_table_names() else False
            self.conn = engine.connect()
            self.metadata = MetaData()
            if not table_exist:
                print('run it')
                Base.metadata.create_all(engine)
            Session = sessionmaker(bind=engine)
            self.session = Session()
        except Exception:
            # traceback.print_exc()
            self.logger.warning(" [+] DB connection failed")
            return False
        else:
            return True


    def dump_person(self, item):
        person = Person(
            person_id = item['person_id'],
            url= item['url'], 
            name= item['name'], 
            location= item['location'], 
            profile_headline= item['profile_headline']
        )
        self.session.add(person)
        self.session.commit()
        # else:
            # self.logger.info(f" [+] {item['name']} already exist in the db!")

    
    def load_config(self):
        if os.path.exists('./config.json'):
            with open('config.json', 'r') as f:
                config  = json.load(f)
                self.username, self.password = config['credentials'].values()
                self.server_uri = config['db_config']['uri']
                self.proxy_user = config['proxies']['username']
                self.proxy_pass = config['proxies']['password']
                self.proxy_server = config['proxies']['server']
                self.proxy_port = config['proxies']['port']
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

        
    def connect(self, person):
        """ connect to a person """
        try:
            if self.message:
                self.driver.find_element(By.XPATH,"//button[@aria-label='Add a note']").click()
                self.im_not_robot()
                self.driver.find_element(By.XPATH,"//textarea[@id='custom-message']").send_keys(self.message)
                self.im_not_robot()
            self.driver.find_element(By.XPATH,"//button[@aria-label='Send now']").click()
            self.logger.info(f" [+] Request sent to {person['name']}!")
            self.dump_person(person)
        except TimeoutError:
            traceback.print_exc()
            self.logger.info(f" [+] Skipping {person['name']}!")


    def search(self, url):
        """ perform search and connect() to results """
        self.logger.info(f" [+] Page {self.page_no}")
        self.driver.get(url)
        if self.cookie_expired():
            raise LoginRequired()
        else:
            self.wait_for_element("//div[@class='entity-result']", timeout=5)
            self.driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
            self.im_not_robot(delay={'min':3, 'max':5})
            sel = Selector(text=self.driver.page_source)
            for profile, parser in zip(self.driver.find_elements(By.XPATH, "//button[contains(@aria-label,'Invite')]"), sel.xpath("//button[contains(@aria-label,'Invite')]/ancestor::div[@class='entity-result']")):
                person = self.parse(parser)
                # interactions
                self.action.move_to_element(profile).click().perform()
                self.connect(person)
                self.im_not_robot(delay={"min":3, "max":5})
                if self.connect_count == self.connects_limit:
                    return None
                else:
                    self.connect_count +=1
                # next page
                if self.wait_for_element("//button[@aria-label='Next']"):
                    self.page_no +=1
                    self.search(url + f"&page={self.page_no}")
    

    def parse(self, response):
        source_url = response.xpath(".//a[contains(@class,'scale')]/@href").get()
        name = re.match(r"(?:Invite)(.*?)to", response.xpath(".//button[contains(@aria-label,'Invite')]/@aria-label").get()).group(1).strip()
        profile_headline = response.xpath(".//div[contains(@class, 'entity-result__primary-subtitle')]/text()[2]").get()
        location = response.xpath(".//div[contains(@class, 'entity-result__secondary-subtitle')]/text()[2]").get()
        item = {
            'person_id': sha256(source_url.encode()).hexdigest()[:16],
            'url':source_url,
            'name':name,
            'profile_headline':profile_headline,
            'location':location
        }
        return item

    
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


    def login(self):   
        try:
            self.driver.get(self.login_url)
            self.driver.find_element(By.XPATH,"//input[@id='username']").send_keys(self.username)
            self.driver.find_element(By.XPATH,"//input[@id='password']").send_keys(self.password)
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
        parser.add_argument('-p', '--proxy', dest='proxy', default=False, type=bool)
        values = parser.parse_args()
        args_dict = vars(values)
        query = args_dict.get('query')
        self.connects_limit = args_dict.get('connects_limit')
        self.message = args_dict.get('message')
        self.use_proxy = args_dict.get("proxy")
        if query:
            return query
        else:
            self.logger.info(" [+] Invalid query")
            sys.exit()

    
    def main(self):
        query = self.take_args()
        self.load_config()
        if self.init_db():
            self.init_driver()
            if self.load_cookies():
                try:
                    self.search(query)
                except LoginRequired:
                    self.login()
                    if self.logged_In:
                        self.search(query)
            else:
                self.login()
                if self.logged_In:
                    self.search(query)
            self.driver.close()


bot = Linkedin_Bot()
bot.main()



