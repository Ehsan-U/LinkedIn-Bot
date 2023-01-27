from playwright.sync_api import sync_playwright
import random
import time
from playwright._impl._api_types import TimeoutError
import coloredlogs, logging
import re
from traceback import print_exc



class Linkedin_Bot():
    logger = logging.getLogger(__name__)
    coloredlogs.install(level='DEBUG')



    def __init__(self):
        self.login_url = 'https://www.linkedin.com/login'



    def init_playwright(self):
        self.play = sync_playwright().start()
        self.page = self.play.firefox.launch(headless=False).new_context().new_page()
        self.page.route("**media.licdn.com/*", lambda route: route.abort() if route.request.resource_type == "image"  else route.continue_())



    # behave like human
    def being_human(self):
        self.page.mouse.move(random.randint(-50, 50),random.randint(-50, 50)) 
        time.sleep(random.uniform(1.0, 3.0))



    def wait_for_element(self, path, timeout=10000, retry=False):
        try:
            self.page.wait_for_selector(path, timeout=timeout)
        except TimeoutError:
            if retry:
                return self.wait_for_element(path, timeout, retry=False)
            else:
                return None
        else:
            return True



    def get_person_name(self):
        raw_name = self.page.locator("//div[@class='pvs-profile-actions ']/div/button[contains(@aria-label, 'connect')]").get_attribute('aria-label')
        if raw_name:
            return re.match(r"(?:Invite)(.*?)to",raw_name).group(1).strip()



    def connect(self, url, message=None):
        self.page.goto(url)
        if self.wait_for_element("//div[@class='pvs-profile-actions ']/div/button[contains(@aria-label, 'connect')]"):
            personName = self.get_person_name()
            self.page.locator("//div[@class='pvs-profile-actions ']/div/button[contains(@aria-label, 'connect')]").click()
            self.being_human()
            if self.wait_for_element("//button[@aria-label='Send now']"):
                if message:
                    self.page.locator("//button[@aria-label='Add a note']").click()
                    self.being_human()
                    self.page.locator("//textarea[@id='custom-message']").fill(message)
                self.page.locator("//button[@aria-label='Send now']").click()
                self.being_human()
                self.logger.info(f" [+] Connected to {personName}!")
        else:
            self.logger.info(" [+] Connection already pending!")      



    def login(self, username, password):   
        try:
            self.page.goto(self.login_url)
            self.being_human()
            self.page.locator("//input[@id='username']").fill(username)
            self.page.locator("//input[@id='password']").fill(password)
            self.being_human()
            self.page.locator("//button[@aria-label='Sign in']").click()
            if self.wait_for_element("//div[contains(@class, 'feed-identity-module__actor')]", timeout=30000) == None:
                raise Exception()
        except Exception as e:
            print_exc()
            self.logger.info(" [+] Login Failed")
            return None
        else:
            self.logger.info(" [+] Login Successful")
            return True



    def main(self):
        username = 'dorin79289@chotunai.com'
        password = 'l*kc841tIvd0C5LqG8^9qm'
        self.init_playwright()
        if self.login(username, password):
            person = 'https://www.linkedin.com/in/abdullahskzai/'
            self.connect(person, message="Hello")
        self.play.stop()



bot = Linkedin_Bot()
bot.main()