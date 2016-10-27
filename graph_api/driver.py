import logging
import settings
from spider_posts import spider_posts
from spider_events import spider_events
from cursor import cursor

class driver():
    FORMAT = '[%(asctime)s -- %(levelname)s -- %(threadName)s -- %(funcName)s]:%(message)s'
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger("fb_wrapper")

    def __init__(self, page_name):
        self.page_name = page_name
        self.spider_basic_pageinfo()
        self.cursor = cursor(settings.ELASTIC_SEARCH_SERVER, settings.ELASTIC_SEARCH_INDEX, self.page_id)

    # format page to facebook_id and store it into redis
    def spider_basic_pageinfo(self):
        self.s = spider_posts(settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET, self.page_name,
                              settings.ELASTIC_SEARCH_SERVER,
                              settings.ELASTIC_SEARCH_INDEX)
        self.page_id = self.s.get_base_info()
        if self.page_id == False:
            exit()

    #Get newest posts or get one year posts relative to one page
    def spider_posts_driver(self):
        self.s = spider_posts(settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET, self.page_name,
                              settings.ELASTIC_SEARCH_SERVER,
                              settings.ELASTIC_SEARCH_INDEX)
        end_time = self.cursor.get_newest_posts()
        self.s.get_fb_post(end_time)

    def spider_comments_driver(self):
        self.s = spider_posts(settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET, self.page_name,
                              settings.ELASTIC_SEARCH_SERVER,
                              settings.ELASTIC_SEARCH_INDEX)
        query_index = 0
        while(True):
            result = self.cursor.get_newest_comments(query_index)
            for iteam in result:
                print iteam
                spider_res = self.s.get_fb_comments_of_post(iteam['post_id'], iteam['end_time'])
                print spider_res
            if len(result) < 30:
                return True
            else:
                query_index = query_index + 30

                # Get newest posts or get one year posts relative to one page

    def spider_events_driver(self):
        self.s = spider_events(settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET, self.page_name,
                              settings.ELASTIC_SEARCH_SERVER,
                              settings.ELASTIC_SEARCH_INDEX)
        end_time = self.cursor.get_newest_event()
        print end_time
        self.s.get_fb_events(end_time)

if __name__ == '__main__':
    driver = driver("lululemon")
    driver.spider_events_driver()

