import subprocess
import sys
import time
import traceback
import scrapy as scrapy
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
import csv
import os
import re
import random

def start():
    
    url = 'https://www.linkedin.com/search/results/people/?keywords=Data%20Science'
    system_name = os.getlogin()
    connected = open('Connects.csv','w',newline='')
    writer = csv.writer(connected)
    writer.writerow(['Name'])
    username = input(" [+] Enter Your Name: ")
    # url = input(" [+] Enter URL: ")
    limit = int(input(' [+] Connects: '))
    print(' [+] Started')
    opt = ChromeOptions()
    p = rf'C:\Users\{system_name}\AppData\Local\Google\Chrome\User%20Data\Default'
    my_profile = rf'user-data-dir={p}'
    opt.add_argument(my_profile)
    driver = uc.Chrome(options=opt,use_subprocess=True)
    driver.maximize_window()
    driver.get(url)
    action = ActionChains(driver)
    i = 1
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        sel = scrapy.Selector(text=driver.page_source)
        for profile,name in zip(driver.find_elements(by=By.XPATH,value="//button[contains(@aria-label,'Invite')]"),sel.xpath("//button[contains(@aria-label,'Invite')]/@aria-label").getall()):
            try:
                name = re.match(r"(?:Invite)(.*?)to",name).group(1)
                action.move_to_element(profile).click().perform()
                time.sleep(random.choice([j for j in range(3,10)]))
                try:
                    driver.find_element(by=By.XPATH,value="//button[@aria-label='Add a note']").click()
                except:
                    driver.find_element(by=By.XPATH,value="//button[@aria-label='Dismiss'][1]").click()
                    continue
                else:
                    time.sleep(random.choice([j for j in range(3,10)]))
                    driver.find_element(by=By.XPATH,value="//textarea[@id='custom-message']").send_keys(f"""Hi {name}\n\nCongratulations on your success. I look forward to connecting.\nIf I can assist you with anything, reach out anytime\n\n{username}""")
                    time.sleep(random.choice([j for j in range(3,10)]))
                    enable = driver.find_element(by=By.XPATH, value="//button[@aria-label='Send now']").is_enabled()
                    if enable:
                        driver.find_element(by=By.XPATH, value="//button[@aria-label='Send now']").click()
                        time.sleep(random.choice([j for j in range(3,10)]))
                        i += 1
                        writer.writerow([name])
                    else:
                        driver.find_element(by=By.XPATH,value="//button[@aria-label='Dismiss'][1]").click()
                        time.sleep(random.choice([j for j in range(3,10)]))
            except Exception as e:
                traceback.print_exc()
                print("exception in main")
            else:
                print(f"\r [+] Done {i}",end='')
                if i == limit:
                    break
                else:
                    continue
        if i == limit:
            break
        # next page
        else:
            try:
                current = driver.current_url
                next = driver.find_element(by=By.XPATH,value="//button[@aria-label='Next']")
                action.move_to_element(next).click().perform()
                # driver.find_element(by=By.XPATH,value="//button[@aria-label='Next']").click()
            except Exception as e:
                # print(e)
                pass
            else:
                time.sleep(random.choice([j for j in range(10,15)]))
                sel = scrapy.Selector(text=driver.page_source)
                if sel.xpath("//div[@class='search-results-container']"):
                    continue
                else:
                    driver.get(current)
                    continue
    connected.close()
    driver.close()
    print(' [+] Finished')

# https://www.linkedin.com/search/results/people/?keywords=Selenium&origin=GLOBAL_SEARCH_HEADER&sid=aTC
if __name__=="__main__":
    try:
        subprocess.call("TASKKILL /f /IM CHROME.EXE",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    except Exception as e:
        print(e)
    else:
        pass
    finally:
        start()
