# from selenium import webdriver
import sys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys 
from pprint import pprint
import json
from selenium_stealth import stealth
from seleniumwire import webdriver
import time
import re
LOGIN_USER = 'REDACTED'
LOGIN_PASSW = 'REDACTED'
# caption_to_scrape = sys.argv[1]
usernames = ["j.e.bracelets"]
output = {}
def prepare_browser():
    chrome_options = webdriver.ChromeOptions()
    proxy = "server:port"
    chrome_options.add_argument(f'--proxy-server={proxy}')
    chrome_options.add_argument("start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging']) 
    chrome_options.add_experimental_option('useAutomationExtension', False) #disables the use of other extensions while on chrome
    driver = webdriver.Chrome(options=chrome_options, service=Service((ChromeDriverManager().install())))
    driver1 = webdriver.Chrome(options= chrome_options)
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
    return driver
def parse_data(username, user_data):
    captions = []
    posts = []
    if len(user_data['edge_owner_to_timeline_media']['edges']) > 0:
        for node in user_data['edge_owner_to_timeline_media']['edges']:
            if len(node['node']['edge_media_to_caption']['edges']) > 0:
                if (node['node']['edge_media_to_caption']['edges'][0]['node']['text']):
                    exp = re.compile("brown", re.I)
                    for result in exp.finditer(node['node']['edge_media_to_caption']['edges'][0]['node']['text']):
                        
                        captions.append(
                            node['node']['edge_media_to_caption']['edges'][0]['node']['text']
                        )
                        posts.append(
                            node['node']['display_url']
                        )
                
    output[username] = {
        'name': user_data['full_name'],
        'category': user_data['category_name'],
        'followers': user_data['edge_followed_by']['count'],
        'posts': posts,
    }
def scrape(username):
    
    url = f'https://instagram.com/{username}/?__a=1&__d=dis'
    chrome = prepare_browser()
    url1 = 'https://www.instagram.com/'
    chrome.get(url1)
    username_field = WebDriverWait(chrome, 10).until(EC.visibility_of_element_located((By.NAME, "username")))
    password_field = WebDriverWait(chrome, 10).until(EC.visibility_of_element_located((By.NAME, "password")))
    time.sleep(3)
    username_field.send_keys(LOGIN_USER)
    time.sleep(3)
    password_field.send_keys(LOGIN_PASSW)
    submit_el = chrome.find_element(By.CSS_SELECTOR,"button[type='submit']")
    time.sleep(1)
    submit_el.click()
    time.sleep(5)
    tab_field = WebDriverWait(chrome, 5).until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
    tab_field.send_keys(Keys.CONTROL + "t")
    chrome.get(url)
    print (f"Attempting: {chrome.current_url}")
    if "login" in chrome.current_url:
        print ("Failed/ redir to login")
        chrome.quit()
    else:
        print ("Success")
        resp_body = chrome.find_element(By.TAG_NAME, "body").text
        print(resp_body)
        data_json = json.loads(resp_body)
        user_data = data_json['graphql']['user']
        parse_data(username, user_data)
        chrome.quit()
def main():
    for username in usernames:
        scrape(username)
if __name__ == '__main__':
    main()
    pprint(output)
