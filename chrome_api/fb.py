import threading
import time

from kafka import KafkaConsumer
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from graph_api import settings


class CrawlerThread(threading.Thread):
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-notifications")
    browser = webdriver.Chrome(executable_path=settings.CHROME_DRIVER_PATH, chrome_options=chrome_options)

    def __init__(self, threadID, threadName):
        super(CrawlerThread, self).__init__()
        print("Let's do it!")
        self.browser.get('https://facebook.com')
        passwd = 'JCCG200330005523'
        self.browser.execute_script('document.getElementById("email").value = "%s";' % (settings.EMAIL))
        time.sleep(2)
        self.browser.execute_script('document.getElementById("pass").value = "%s";' % passwd)
        time.sleep(2)
        self.browser.find_element_by_id('login_form').submit()
        print("Login facebook success!!")


    def run(self):
        consumer = KafkaConsumer(bootstrap_servers='localhost:9092',
                                 auto_offset_reset='earliest', enable_auto_commit='True')
        consumer.subscribe(['test'])
        self.browser.set_page_load_timeout(120)
        for message in consumer:
            print (message)
            target_url = message.value
            if 'facebook' not in target_url:
                continue
            else:
                try:
                    self.browser.get(target_url)
                    consumer.commit()
                    if 'followers' in target_url:
                        self.browser.find_element_by_xpath("//span[contains(text(), 'Followers')]/parent::a").is_displayed()
                        self.browser.find_element_by_xpath("//span[contains(text(), 'Followers')]/parent::a").click()
                    if 'friends' in target_url:
                        self.browser.find_elements_by_class_name()
                except:
                    continue
