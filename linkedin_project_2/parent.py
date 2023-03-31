import json
import os
from playwright.sync_api import sync_playwright
from traceback import print_exc
from typing import Union
from requests import Response
from constant import SEARCH_HEADERS
from copy import deepcopy
from requests_cache.session import CachedSession
from requests import Session
import csv
requests_cache.install_cache("cache")



class LinkedIn():
    login_url = 'https://www.linkedin.com/login'
    logged_in = False
    # session = CachedSession()
    session = Session()


    def init_playwright(self) -> None:
        self.play = sync_playwright().start()
        self.page = self.play.firefox.launch(headless=False).new_context().new_page()


    def init_writer(self):
        self.file = open('output.csv','w', newline='', encoding='utf8')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['Name', 'Primary_desc', 'Secondary_desc','Url', 'Source'])


    def request(self, url: str, headers: Union[dict, None] = None, cookies: dict = None) -> Union[Response, None]:
        try:
            response = self.session.get(url, headers=headers, cookies=cookies)
        except Exception:
            print_exc()
            response = None
        finally:
            return response


    def start_requests(self, urls):
        self.init_writer()
        try:
            for url in urls:
                username = url.split('in/')[-1].replace('/','')
                headers = self.build_headers(url)
                modified_url = f"https://www.linkedin.com:443/voyager/api/identity/dash/profiles?q=memberIdentity&memberIdentity={username}&decorationId=com.linkedin.voyager.dash.deco.identity.profile.TopCardSupplementary-120"
                response = self.request(modified_url, headers=headers, cookies=self.cookies)
                self.parse(response)
        except Exception:
            print_exc()
        finally:
            self.file.close()


    def build_headers(self, url):
        headers = deepcopy(HEADERS)
        headers['Referer'] = url
        headers['Csrf-Token'] = self.cookies.get("JSESSIONID").replace('"','')
        return headers


    def parse(self, response):
        if response:
            profile_urn = response.json().get("data").get("*elements")[0].split('profile:')[-1]
            offset = 0
            while True:
                url = f'https://www.linkedin.com:443/voyager/api/graphql?includeWebMetadata=true&variables=(start:{offset},origin:MEMBER_PROFILE_CANNED_SEARCH,query:(flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:connectionOf,value:List({profile_urn})),(key:network,value:List(F)),(key:resultType,value:List(PEOPLE))),includeFiltersInResponse:false))&&queryId=voyagerSearchDashClusters.ee225d5273446315cee711c9f30203fc'
                response = self.request(url, headers=response.request.headers, cookies=self.cookies)
                result = self.parse_mutuals(response)
                if result == False:
                    break
                else:
                    print(" next page")
                    offset += 10
                    continue


    def parse_mutuals(self, response):
        if response:
            if response.json().get("included"):
                for mutual in response.json().get("included"):
                    if mutual.get("template"):
                        name = mutual.get("title", {}).get("text", '')
                        primary_desc = mutual.get("primarySubtitle", {}).get("text", '')
                        secondary_desc = mutual.get('secondarySubtitle',{}).get('text', '')
                        url = mutual.get("navigationUrl", '')
                        item = {
                            "name": name,
                            "primary_desc": primary_desc,
                            "secondary_desc": secondary_desc,
                            "url": url,
                            "source": url
                        }
                        print(item)
                        self.writer.writerow(item.values())
            else:
                return False


    def reshape_cookies(self, cookies: list[dict]) -> Union[dict, None]:
        if cookies:
            request_cookies = {}
            for cookie in cookies:
                name = cookie['name']
                del cookie['name']
                value = cookie['value']
                del cookie['value']
                cookie[name] = value
                request_cookies.update(cookie)
            request_cookies = {k:str(v) for k,v in request_cookies.items()}
            return request_cookies
        else:
            return None


    def load_cookies(self) -> bool:
        if os.path.exists("./cookies.json"):
            with open("cookies.json", 'r') as f:
                self.cookies = self.reshape_cookies(json.load(f))
                self.logged_in = True
                print(" [+] Cookies loaded!")
                return True
        else:
            return False


    def save_cookies(self, cookies: dict) -> None:
        with open("cookies.json", 'w') as f:
            json.dump(cookies, f)
            print(" [+] Cookies saved")


    def login(self) -> None:   
        try:
            self.init_playwright()
            self.page.goto(self.login_url)
            input(" [+] Complete login & press enter: ")
        except Exception:
            print_exc()
        else:
            cookies = self.page.context.cookies()
            self.save_cookies(cookies)
            self.load_cookies()
            self.logged_in = True
            self.play.stop()

    @staticmethod
    def load_urls():
        urls = []
        with open('urls.csv','r') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                urls.append(row[0])
        return urls


    def crawl(self):
        if not self.load_cookies():
            self.login()
        if self.logged_in:
            print('logged in')
            urls = self.load_urls()
            self.start_requests(urls)




