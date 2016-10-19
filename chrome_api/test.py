import logging
import traceback

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import settings

logger = logging.getLogger('testThread')

class testThread():
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-notifications")
    browser = webdriver.Chrome(executable_path=settings.CHROME_DRIVER_PATH, chrome_options=chrome_options)

    def __init__(self, threadID, threadName):
        self.browser.get('https://facebook.com')
        passwd = 'JCCG200330005523'
        self.browser.execute_script('document.getElementById("email").value = "%s";' % (settings.EMAIL))
        self.browser.implicitly_wait(3)
        self.browser.execute_script('document.getElementById("pass").value = "%s";' % passwd)
        self.browser.implicitly_wait(3)
        self.browser.find_element_by_id('login_form').submit()
        print("Login facebook success!!")

    def get_fb_friends(self):
        try:
            #self.browser.get("https://www.facebook.com/Fatowzanwar/friends")
            self.browser.get("https://www.facebook.com/muhan.liu.1/friends")
            self.browser.implicitly_wait(30)
            elements = self.browser.find_elements_by_class_name("uiProfileBlockContent")
            base = len(elements)
            print base
            while True:
                self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.browser.implicitly_wait(10)
                now_number = len(self.browser.find_elements_by_class_name("uiProfileBlockContent"))
                if now_number > base:
                    base = now_number
                    print base
                    continue
                else:
                    break
        except Exception, error:
            traceback.print_exc()
            print error
        self.extraFriends()


    def extraFriends(self):
        print self.browser.title
        friends_divs = self.browser.find_elements_by_class_name("uiProfileBlockContent")
        for div in friends_divs:
            try:
                innerHTML = div.get_attribute("innerHTML")
                soup = BeautifulSoup(innerHTML, 'lxml')
                for user_link in soup.find_all('a'):
                    href = user_link['href'].split('?')[0]
                    print user_link.text + " : " + href + '\n'
            except Exception, error:
                traceback.print_exc()
                continue

    def get_fb_edu(self):
        self.browser.get("https://www.facebook.com/muhan.liu.1/about?section=education")
        self.browser.implicitly_wait(20)
        divs = self.browser.find_elements_by_class_name("fbEditProfileViewExperience")
        for div in divs:
            try:
                innerHTML = div.get_attribute("innerHTML")
                soup = BeautifulSoup(innerHTML, 'lxml')
                for school_link in soup.find_all("a"):
                    print school_link.text + " : " + school_link['href'] + '\n'
            except Exception, error:
                traceback.print_exc()
                continue


    def get_fb_lived(self):
        self.browser.get("https://www.facebook.com/muhan.liu.1/about?section=living")
        self.browser.implicitly_wait(20)
        divs = self.browser.find_elements_by_id("pagelet_hometown")
        for div in divs:
            try:
                innerHTML = div.get_attribute("innerHTML")
                soup = BeautifulSoup(innerHTML, 'lxml')
                if len(soup.find_all("uiProfileBlockContent")) > 0:
                    continue
                for school_link in soup.find_all("a"):
                    href = school_link['href']
                    print school_link.text + " : " + href + '\n'
            except Exception, error:
                traceback.print_exc()
                continue

    def close(self):
        self.browser.quit()

if __name__ == "__main__":
    test = testThread(1, "Test1")
    test.get_fb_edu()
    print "=========education above=======\n"
    test.get_fb_lived()
    print "=========lived above==========\n"
    test.get_fb_friends()
    print "=======friends abouve========="
    test.close()